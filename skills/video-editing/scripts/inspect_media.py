#!/usr/bin/env python3
"""Inspect existing media and optionally create lightweight review assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def rational(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return float(numerator) / float(denominator) if float(denominator) else None
    return float(value)


def inspect(path: Path) -> dict:
    result = run(
        [
            FFPROBE,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ]
    )
    raw = json.loads(result.stdout)
    video = next((s for s in raw.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in raw.get("streams", []) if s.get("codec_type") == "audio"), None)
    duration = float(raw.get("format", {}).get("duration") or 0)
    return {
        "path": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "duration_seconds": duration,
        "format": raw.get("format", {}).get("format_name"),
        "video": None
        if video is None
        else {
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "fps": rational(video.get("avg_frame_rate") or video.get("r_frame_rate")),
            "pixel_format": video.get("pix_fmt"),
            "rotation": (video.get("tags") or {}).get("rotate"),
        },
        "audio": None
        if audio is None
        else {
            "codec": audio.get("codec_name"),
            "sample_rate": int(audio.get("sample_rate") or 0),
            "channels": audio.get("channels"),
            "channel_layout": audio.get("channel_layout"),
        },
    }


def safe_stem(path: Path) -> str:
    digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in path.stem).strip("-")
    return f"{cleaned or 'media'}-{digest}"


def create_review_assets(path: Path, info: dict, review_dir: Path) -> dict:
    review_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(path)
    proxy = review_dir / f"{stem}-proxy.mp4"
    sheet = review_dir / f"{stem}-contact.jpg"

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
            "scale=1280:-2:force_original_aspect_ratio=decrease",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "2M",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(proxy),
        ]
    )

    duration = max(float(info.get("duration_seconds") or 0), 1.0)
    frames = max(1, min(24, math.ceil(duration / 2)))
    interval = max(2.0, duration / frames)
    columns = 4
    rows = math.ceil(frames / columns)
    vf = (
        f"fps=1/{interval:.6f},scale=320:-2,"
        f"tile={columns}x{rows}:nb_frames={frames}:padding=4:margin=4:color=black"
    )
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
            vf,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(sheet),
        ]
    )
    return {"proxy": str(proxy), "contact_sheet": str(sheet)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review-dir", type=Path)
    args = parser.parse_args()

    records = []
    for path in args.inputs:
        if not path.is_file():
            raise SystemExit(f"Input does not exist or is not a file: {path}")
        info = inspect(path)
        if args.review_dir and info["video"]:
            info["review"] = create_review_assets(path, info, args.review_dir)
        records.append(info)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"media": records}, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or str(exc))
        raise SystemExit(exc.returncode)
