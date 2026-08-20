#!/usr/bin/env python3
# WhatsApp collection for work-triage.
import argparse
import contextlib
import fcntl
import os
import platform
import re
import subprocess
import time
from pathlib import Path

from common import MAX_ITEMS_PER_LANE, add_common_args, base_result, compact_text, emit, error_obj, iso_utc, json_cmd, window_from_args

LAUNCH_AGENT_LABEL = "com.fulldev.wacli-sync"
DOWNLOAD_TIMEOUT_SECONDS = 45
DIRECT_LOCK_WAIT = "2s"
RECOVERY_LOCK_WAIT = "15s"
SERVICE_WAIT_SECONDS = 20
RECOVERY_SERIALIZATION_TIMEOUT_SECONDS = 60
RECOVERY_LOCK_NAME = ".work-triage-media-recovery.lock"


class MediaRecoveryError(RuntimeError):
    pass


class CommandError(RuntimeError):
    def __init__(self, cmd, returncode, stdout="", stderr=""):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout or ""
        self.stderr = stderr or ""
        super().__init__(self.safe_message())

    def safe_message(self):
        detail = (self.stderr or self.stdout).strip()
        return f"command failed ({self.returncode}): {' '.join(self.cmd)}" + (f": {detail}" if detail else "")


def store_dir():
    return Path(os.environ.get("WACLI_STORE_DIR", Path.home() / ".wacli")).expanduser()


def media_dir(chat_id, msg_id):
    return store_dir() / "media" / (chat_id or "").replace("@", "_") / (msg_id or "")


def durable_media_paths(chat_id, msg_id):
    directory = media_dir(chat_id, msg_id)
    return [str(p) for p in sorted(directory.rglob("*")) if p.is_file()] if directory.exists() else []


def media(chat_id, msg_id):
    directory = media_dir(chat_id, msg_id)
    paths = durable_media_paths(chat_id, msg_id)
    return {"saved_dir": str(directory), "saved_paths": paths, **({} if paths else {"error": "media_not_downloaded_yet"})}


def run_command(cmd, timeout=None):
    process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if process.returncode:
        raise CommandError(cmd, process.returncode, process.stdout, process.stderr)
    return process


def command_text(exc):
    text = (getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or str(exc)).strip()
    text = re.sub(r"(?i)(token|secret|password|pass|api[_-]?key)(=|:)\S+", r"\1\2[redacted]", text)
    return compact_text(text, 1000)


def is_lock_error(exc):
    text = f"{getattr(exc, 'stdout', '')}\n{getattr(exc, 'stderr', '')}\n{exc}".lower()
    return "lock" in text and (
        "timeout" in text
        or "held" in text
        or "busy" in text
        or "database is locked" in text
        or "could not acquire" in text
    )


def download_media_item(item, runner=run_command, lock_wait=DIRECT_LOCK_WAIT):
    runner(
        [
            "wacli",
            "--json",
            "--timeout",
            f"{DOWNLOAD_TIMEOUT_SECONDS}s",
            "--lock-wait",
            lock_wait,
            "media",
            "download",
            "--chat",
            item["chat_id"],
            "--id",
            item["message_id"],
        ],
        timeout=DOWNLOAD_TIMEOUT_SECONDS + 5,
    )


@contextlib.contextmanager
def recovery_lock(lock_path=None):
    path = Path(lock_path or (store_dir() / RECOVERY_LOCK_NAME)).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        deadline = time.monotonic() + RECOVERY_SERIALIZATION_TIMEOUT_SECONDS
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise MediaRecoveryError("timed out waiting for WhatsApp media recovery lock")
                time.sleep(0.2)
        yield


def launch_agent_plist():
    return Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"


def launch_domain():
    return f"gui/{os.getuid()}"


def launch_service():
    return f"{launch_domain()}/{LAUNCH_AGENT_LABEL}"


def launch_agent_available(runner=run_command):
    if platform.system() != "Darwin":
        return False, "macos_required"
    plist = launch_agent_plist()
    if not plist.exists():
        return False, "launch_agent_plist_missing"
    try:
        result = runner(["launchctl", "print", launch_service()], timeout=5)
    except Exception as exc:
        return False, f"launch_agent_unavailable: {command_text(exc)}"
    if f"path = {plist}" not in (result.stdout or ""):
        return False, "launch_agent_path_mismatch"
    return True, None


def unload_launch_agent(runner=run_command):
    runner(["launchctl", "bootout", launch_service()], timeout=10)


def start_launch_agent(runner=run_command):
    runner(["launchctl", "bootstrap", launch_domain(), str(launch_agent_plist())], timeout=10)


def service_is_running(runner=run_command):
    try:
        result = runner(["launchctl", "print", launch_service()], timeout=5)
    except Exception:
        return False
    return "state = running" in (result.stdout or "")


def wait_until(predicate, timeout_seconds=SERVICE_WAIT_SECONDS, sleep=time.sleep):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        sleep(0.2)
    return predicate()


def wait_for_launch_agent_stopped(runner=run_command, sleep=time.sleep):
    return wait_until(lambda: not service_is_running(runner), SERVICE_WAIT_SECONDS, sleep)


def restore_launch_agent(runner=run_command, sleep=time.sleep):
    if service_is_running(runner):
        return
    try:
        start_launch_agent(runner)
    except Exception:
        if not wait_until(lambda: service_is_running(runner), SERVICE_WAIT_SECONDS, sleep):
            raise
    if not wait_until(lambda: service_is_running(runner), SERVICE_WAIT_SECONDS, sleep):
        raise MediaRecoveryError(f"{LAUNCH_AGENT_LABEL} did not report running after restart")


def recovery_result(status, method=None, recovered_paths=None, error=None):
    result = {"status": status}
    if method:
        result["method"] = method
    if recovered_paths is not None:
        result["recovered_paths"] = recovered_paths
    if error:
        result["error"] = error
    return result


def recover_missing_media(missing, runner=run_command, lock_context=recovery_lock, sleep=time.sleep):
    if not missing:
        return {}
    results = {}
    remaining = []
    with lock_context():
        for item in missing:
            key = (item["chat_id"], item["message_id"])
            try:
                download_media_item(item, runner, DIRECT_LOCK_WAIT)
                results[key] = recovery_result("recovered", method="direct_download", recovered_paths=durable_media_paths(*key))
            except Exception as exc:
                if is_lock_error(exc):
                    remaining.append(item)
                    break
                results[key] = recovery_result("failed", method="direct_download", error=command_text(exc))

        seen = {(item["chat_id"], item["message_id"]) for item in remaining} | set(results)
        remaining.extend(item for item in missing if (item["chat_id"], item["message_id"]) not in seen)
        if not remaining:
            return results

        available, reason = launch_agent_available(runner)
        if not available:
            for item in remaining:
                key = (item["chat_id"], item["message_id"])
                results[key] = recovery_result("failed", method="launch_agent_recovery", error=reason)
            return results

        restore_error = None
        unloaded = False
        try:
            unload_launch_agent(runner)
            unloaded = True
            if not wait_for_launch_agent_stopped(runner, sleep):
                for item in remaining:
                    key = (item["chat_id"], item["message_id"])
                    results[key] = recovery_result("failed", method="launch_agent_recovery", error="launch_agent_stop_timeout")
            else:
                for item in remaining:
                    key = (item["chat_id"], item["message_id"])
                    try:
                        download_media_item(item, runner, RECOVERY_LOCK_WAIT)
                        results[key] = recovery_result("recovered", method="launch_agent_recovery", recovered_paths=durable_media_paths(*key))
                    except Exception as exc:
                        results[key] = recovery_result("failed", method="launch_agent_recovery", error=command_text(exc))
        except Exception as exc:
            for item in remaining:
                key = (item["chat_id"], item["message_id"])
                results[key] = recovery_result("failed", method="launch_agent_recovery", error=command_text(exc))
        finally:
            if unloaded or not service_is_running(runner):
                try:
                    restore_launch_agent(runner, sleep)
                except Exception as exc:
                    restore_error = command_text(exc)
        if restore_error:
            raise MediaRecoveryError(f"failed to restart {LAUNCH_AGENT_LABEL}: {restore_error}")
    return results


def media_with_recovery(chat_id, msg_id, recovery=None):
    info = media(chat_id, msg_id)
    if recovery:
        info["recovery"] = recovery
        if info.get("saved_paths"):
            info.pop("error", None)
        elif recovery.get("error"):
            info["error"] = recovery["error"]
    return info


def recovery_key_for_message(recovery, chat_id, msg_id):
    key = (chat_id, msg_id)
    return key if key in recovery else None


def collect(a, b):
    chat_rows = (json_cmd(["wacli", "--json", "--read-only", "chats", "list", "--limit", str(MAX_ITEMS_PER_LANE)]).get("data") or [])
    chats = {(c.get("jid") or c.get("JID")): c for c in chat_rows}
    data = json_cmd(["wacli", "--json", "--read-only", "messages", "list", "--after", iso_utc(a), "--before", iso_utc(b), "--limit", str(MAX_ITEMS_PER_LANE)])
    grouped, chat_names, missing = {}, {}, []
    for m in (data.get("data") or {}).get("messages") or []:
        cid, mid, mt = m.get("ChatJID"), m.get("MsgID"), m.get("MediaType")
        chat_row = chats.get(cid) or {}
        chat_names[cid] = m.get("ChatName") or chat_names.get(cid) or chat_row.get("name") or chat_row.get("Name") or cid
        media_info = None
        if mt:
            media_info = {"type": mt, "display_text": m.get("DisplayText"), **media(cid, mid)}
            if not media_info.get("saved_paths"):
                missing.append({"chat_id": cid, "message_id": mid})
        grouped.setdefault(cid, []).append(
            {
                "id": mid,
                "sender": m.get("SenderJID"),
                "sender_name": m.get("SenderName") or None,
                "timestamp": m.get("Timestamp"),
                "kind": "media" if mt else "message",
                "text": compact_text(m.get("Text") or m.get("DisplayText") or m.get("Snippet") or "", 12000),
                "media": media_info,
            }
        )

    recovery = recover_missing_media(missing)
    if recovery:
        for cid, messages in grouped.items():
            for msg in messages:
                if not msg.get("media"):
                    continue
                key = recovery_key_for_message(recovery, cid, msg.get("id"))
                if key:
                    msg["media"] = {
                        "type": msg["media"].get("type"),
                        "display_text": msg["media"].get("display_text"),
                        **media_with_recovery(cid, msg.get("id"), recovery[key]),
                    }
    return [{"chat_id": cid, "chat": chat_names.get(cid) or cid, "messages": sorted(msgs, key=lambda x: x.get("timestamp") or "")} for cid, msgs in grouped.items()]


def main():
    p = argparse.ArgumentParser()
    add_common_args(p)
    args = p.parse_args()
    a, b = window_from_args(args.after, args.before, require=True)
    r = base_result("whatsapp", "window", a, b)
    try:
        r["items"] = collect(a, b)
    except Exception as exc:
        err = error_obj("whatsapp", exc)
        r["ok"] = False
        r["errors"].append(err)
    emit(r, args.pretty, args.format)


if __name__ == "__main__":
    main()
