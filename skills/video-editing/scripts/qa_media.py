#!/usr/bin/env python3
"""Decode a final video and create plan-driven visual QA sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"


def run(command: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict:
    result = run(
        [FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture=True,
    )
    return json.loads(result.stdout)


def rational(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return float(numerator) / float(denominator) if float(denominator) else None
    return float(value)


def digest(path: Path) -> str:
    value = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def parse_timestamp(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    parts = normalized.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid caption timestamp: {value}")
    hours, minutes, seconds = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def caption_cues(path: Path) -> list[tuple[float, float]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() == ".ass":
        cues = []
        for line in text.splitlines():
            if not line.startswith("Dialogue:"):
                continue
            fields = line.split(",", 9)
            if len(fields) >= 3:
                cues.append((parse_timestamp(fields[1]), parse_timestamp(fields[2])))
        return cues

    pattern = re.compile(
        r"(?m)^(\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+"
        r"(\d{2}:\d{2}:\d{2}[,.]\d{3})"
    )
    return [(parse_timestamp(start), parse_timestamp(end)) for start, end in pattern.findall(text)]


def evenly_spaced(values: list[float], count: int) -> list[float]:
    if len(values) <= count:
        return values
    indices = {round(index * (len(values) - 1) / (count - 1)) for index in range(count)}
    return [values[index] for index in sorted(indices)]


def plan_checkpoints(plan: dict, fps: float) -> dict[str, list[dict]]:
    clips = plan.get("clips") or []
    cursor = 0.0
    cuts: list[dict] = []
    zooms: list[dict] = []
    frame = 1 / fps

    for clip_index, clip in enumerate(clips):
        duration = float(clip["out"]) - float(clip["in"])
        clip_end = cursor + duration
        if clip_index + 1 < len(clips):
            for offset in (-2 * frame, -frame, frame, 2 * frame):
                cuts.append(
                    {
                        "time": max(0.0, clip_end + offset),
                        "reason": f"cut {clip_index + 1} {offset / frame:+.0f} frame",
                    }
                )

        for event_index, event in enumerate(clip.get("zoom_events") or []):
            start = cursor + float(event.get("start", 0))
            ease_in = float(event.get("ease_in", 3.5))
            peak = start + ease_in
            event_points = [
                {"time": max(cursor, start - 0.6), "reason": "zoom baseline"},
                {"time": start + ease_in / 2, "reason": "zoom movement"},
                {"time": min(clip_end - frame, peak + 0.4), "reason": "zoom hold"},
            ]
            if str(event.get("reset", "cut")) == "cut" and clip_index + 1 < len(clips):
                event_points.append({"time": clip_end + 2 * frame, "reason": "zoom reset after cut"})
            elif str(event.get("reset", "cut")) == "ease_out":
                end = peak + float(event.get("hold", 0.6)) + float(event.get("ease_out", 1.8))
                event_points.append({"time": min(clip_end - frame, end + 0.2), "reason": "zoom reset"})
            for item in event_points:
                item["zoom_event"] = f"{clip_index + 1}.{event_index + 1}"
            zooms.extend(event_points)
        cursor = clip_end

    manual = []
    for index, item in enumerate(plan.get("qa_points") or []):
        if not isinstance(item, dict) or "time" not in item:
            raise ValueError(f"qa_points[{index}] must contain time and may contain reason")
        manual.append(
            {
                "time": float(item["time"]),
                "reason": str(item.get("reason", f"manual QA point {index + 1}")),
            }
        )
    return {"cuts": cuts, "zooms": zooms, "manual": manual}


def make_sheet(path: Path, times: list[float], fps: float, duration: float, output: Path) -> None:
    valid = sorted({max(0, min(round(time * fps), round(duration * fps) - 1)) for time in times})
    if not valid:
        return
    expression = "+".join(f"eq(n\\,{frame})" for frame in valid)
    columns = min(4, len(valid))
    rows = math.ceil(len(valid) / columns)
    run(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(path),
            "-vf",
            f"select={expression},scale=240:-2,tile={columns}x{rows}:padding=3:margin=3:color=black",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )


def contact_sheet(path: Path, duration: float, output: Path) -> None:
    frames = max(1, min(24, math.ceil(duration / 2)))
    interval = max(2.0, duration / frames)
    columns = 4
    rows = math.ceil(frames / columns)
    run(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(path),
            "-vf",
            f"fps=1/{interval:.6f},scale=240:-2,"
            f"tile={columns}x{rows}:nb_frames={frames}:padding=3:margin=3:color=black",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )


def validate_plan_output(raw: dict, plan: dict) -> dict[str, bool]:
    output = plan.get("output") or {}
    video = next((stream for stream in raw.get("streams", []) if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in raw.get("streams", []) if stream.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise ValueError("Final must contain video and audio streams")
    expected_duration = sum(float(clip["out"]) - float(clip["in"]) for clip in plan["clips"])
    duration = float(raw.get("format", {}).get("duration") or 0)
    expected_fps = float(output.get("fps", 30))
    expected_range = str(output.get("color_range", "tv"))
    expected_space = str(output.get("colorspace", "bt709"))
    checks = {
        "duration": abs(duration - expected_duration) <= max(0.1, 2 / expected_fps),
        "resolution": (video.get("width"), video.get("height"))
        == (int(output["width"]), int(output["height"])),
        "fps": abs((rational(video.get("avg_frame_rate")) or 0) - expected_fps) < 0.001,
        "video_codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "color_range": video.get("color_range") == expected_range,
        "color_space": video.get("color_space") == expected_space,
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Final failed plan checks: {', '.join(failed)}")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("final", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--captions", type=Path)
    parser.add_argument("--require-captions", action="store_true")
    parser.add_argument("--caption-samples", type=int, default=6)
    args = parser.parse_args()

    if not args.final.is_file():
        raise SystemExit(f"Final does not exist: {args.final}")
    if args.caption_samples < 3:
        raise SystemExit("--caption-samples must be at least 3")

    plan = None
    root = (args.root or Path.cwd()).resolve()
    if args.plan:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw = probe(args.final)
    duration = float(raw.get("format", {}).get("duration") or 0)
    video = next(stream for stream in raw["streams"] if stream.get("codec_type") == "video")
    fps = rational(video.get("avg_frame_rate")) or rational(video.get("r_frame_rate")) or 30
    checks = validate_plan_output(raw, plan) if plan else {}
    (args.output_dir / "probe.json").write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    run([FFMPEG, "-v", "error", "-i", str(args.final), "-f", "null", "-"])
    loudness = run(
        [
            FFMPEG,
            "-hide_banner",
            "-nostats",
            "-i",
            str(args.final),
            "-map",
            "0:a:0",
            "-af",
            "ebur128=peak=true",
            "-f",
            "null",
            "-",
        ],
        capture=True,
    )
    (args.output_dir / "loudness.log").write_text(loudness.stderr, encoding="utf-8")
    contact_sheet(args.final, duration, args.output_dir / "contact-sheet.jpg")

    checkpoints = {"cuts": [], "zooms": [], "manual": [], "captions": []}
    if plan:
        checkpoints.update(plan_checkpoints(plan, fps))
        for name in ("cuts", "zooms", "manual"):
            times = [float(item["time"]) for item in checkpoints[name]]
            make_sheet(args.final, times, fps, duration, args.output_dir / f"{name}-review.jpg")

    caption_path = args.captions
    if caption_path is None and plan and plan.get("captions"):
        caption_path = resolve(root, str(plan["captions"].get("path", "")))
    if caption_path:
        if not caption_path.is_file():
            raise ValueError(f"Caption file does not exist: {caption_path}")
        cues = caption_cues(caption_path)
        if not cues:
            raise ValueError(f"Caption file contains no readable cues: {caption_path}")
        midpoints = evenly_spaced([(start + end) / 2 for start, end in cues], args.caption_samples)
        checkpoints["captions"] = [
            {"time": time, "reason": "caption must be visibly burned in"} for time in midpoints
        ]
        make_sheet(args.final, midpoints, fps, duration, args.output_dir / "captions-review.jpg")
    elif args.require_captions:
        raise ValueError("Captions are required but no caption file was supplied or declared in the plan")

    (args.output_dir / "checkpoints.json").write_text(
        json.dumps(checkpoints, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "path": str(args.final.resolve()),
        "size_bytes": args.final.stat().st_size,
        "md5": digest(args.final),
        "duration": duration,
        "checks": checks,
        "caption_review_required": bool(checkpoints["captions"]),
        "artifacts": {
            "contact_sheet": str(args.output_dir / "contact-sheet.jpg"),
            "caption_sheet": str(args.output_dir / "captions-review.jpg")
            if checkpoints["captions"]
            else None,
            "checkpoints": str(args.output_dir / "checkpoints.json"),
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output_dir / "summary.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Final QA failed: {exc}") from exc
