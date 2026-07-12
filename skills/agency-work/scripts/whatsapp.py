#!/usr/bin/env python3
import argparse, os
from pathlib import Path
from common import MAX_ITEMS_PER_LANE, add_common_args, base_result, compact_text, emit, error_obj, iso_utc, json_cmd, window_from_args

def media(chat_id,msg_id):
    d = Path(os.environ.get("WACLI_STORE_DIR", Path.home()/".wacli")).expanduser() / "media" / (chat_id or "").replace("@","_") / (msg_id or "")
    paths = [str(p) for p in sorted(d.rglob("*")) if p.is_file()] if d.exists() else []
    return {"saved_dir": str(d), "saved_paths": paths, **({} if paths else {"error": "media_not_downloaded_yet"})}

def collect(a,b):
    chats = {c.get("JID"): c for c in (json_cmd(["wacli","--json","chats","list"]).get("data") or [])}
    data = json_cmd(["wacli","--json","messages","list","--after",iso_utc(a),"--before",iso_utc(b),"--limit",str(MAX_ITEMS_PER_LANE)])
    grouped = {}
    for m in (data.get("data") or {}).get("messages") or []:
        cid, mid, mt = m.get("ChatJID"), m.get("MsgID"), m.get("MediaType")
        grouped.setdefault(cid, []).append({"id": mid, "sender": m.get("SenderJID"), "timestamp": m.get("Timestamp"), "kind": "media" if mt else "message", "text": compact_text(m.get("Text") or m.get("DisplayText") or m.get("Snippet") or "", 12000), "media": {"type": mt, "display_text": m.get("DisplayText"), **media(cid, mid)} if mt else None})
    return [{"chat_id": cid, "chat": (chats.get(cid) or {}).get("Name") or cid, "messages": sorted(msgs, key=lambda x: x.get("timestamp") or "")} for cid,msgs in grouped.items()]

def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args(); a,b=window_from_args(args.after,args.before,require=True); r=base_result("whatsapp","window",a,b)
    try: r["items"]=collect(a,b)
    except Exception as exc: err=error_obj("whatsapp",exc); r["ok"]=False; r["errors"].append(err)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
