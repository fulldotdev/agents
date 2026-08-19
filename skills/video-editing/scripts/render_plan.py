#!/usr/bin/env python3
"""Render an explicit JSON edit plan with FFmpeg Full."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def probe(path: Path) -> dict:
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def escape_filter_path(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "\\\\")
    for character in (":", "'", ",", "[", "]"):
        value = value.replace(character, f"\\{character}")
    return value


def even(value: object, name: str) -> int:
    number = int(value)
    if number <= 0 or number % 2:
        raise ValueError(f"{name} must be a positive even integer")
    return number


def bounded(value: object, name: str, lower: float, upper: float) -> float:
    number = float(value)
    if not lower <= number <= upper:
        raise ValueError(f"{name} must be between {lower} and {upper}")
    return number


def build(plan: dict, root: Path, output_override: Path | None) -> tuple[list[str], Path]:
    clips = plan.get("clips")
    if not isinstance(clips, list) or not clips:
        raise ValueError("Plan must contain at least one clip")

    output_cfg = plan.get("output") or {}
    width = even(output_cfg.get("width"), "output.width")
    height = even(output_cfg.get("height"), "output.height")
    fps = float(output_cfg.get("fps", 30))
    if not 1 <= fps <= 120:
        raise ValueError("output.fps must be between 1 and 120")
    output = output_override or resolve(root, output_cfg.get("path", ""))
    if not str(output_cfg.get("path", "")) and output_override is None:
        raise ValueError("output.path is required")

    command = [FFMPEG, "-hide_banner", "-loglevel", "warning"]
    filters: list[str] = []
    labels: list[str] = []
    source_paths: list[Path] = []

    for index, clip in enumerate(clips):
        source = resolve(root, str(clip.get("source", ""))).resolve()
        if not source.is_file():
            raise ValueError(f"Missing source for clip {index}: {source}")
        start = float(clip.get("in", 0))
        end = float(clip.get("out", 0))
        duration = end - start
        if start < 0 or duration <= 0:
            raise ValueError(f"Invalid in/out for clip {index}")

        metadata = probe(source)
        streams = metadata.get("streams", [])
        has_video = any(stream.get("codec_type") == "video" for stream in streams)
        has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
        if not has_video:
            raise ValueError(f"Clip {index} has no video stream: {source}")

        source_paths.append(source)
        command.extend(["-ss", f"{start:.6f}", "-t", f"{duration:.6f}", "-i", str(source)])

        zoom = bounded(clip.get("zoom", 1.0), f"clips[{index}].zoom", 1.0, 1.25)
        pos_x = bounded(clip.get("position_x", 0.5), f"clips[{index}].position_x", 0.0, 1.0)
        pos_y = bounded(clip.get("position_y", 0.5), f"clips[{index}].position_y", 0.0, 1.0)
        scaled_w = round(width * zoom / 2) * 2
        scaled_h = round(height * zoom / 2) * 2
        video_filters = [
            f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}:x=(iw-ow)*{pos_x:.6f}:y=(ih-oh)*{pos_y:.6f}",
            "setsar=1",
            f"fps={fps:g}",
            "format=yuv420p",
            "setpts=PTS-STARTPTS",
        ]
        fade_in = float(clip.get("fade_in", 0))
        fade_out = float(clip.get("fade_out", 0))
        if fade_in < 0 or fade_out < 0 or fade_in + fade_out >= duration:
            raise ValueError(f"Invalid fades for clip {index}")
        if fade_in:
            video_filters.append(f"fade=t=in:st=0:d={fade_in:.6f}")
        if fade_out:
            video_filters.append(f"fade=t=out:st={duration - fade_out:.6f}:d={fade_out:.6f}")
        filters.append(f"[{index}:v:0]{','.join(video_filters)}[v{index}]")

        audio_filters = [
            "aresample=48000",
            "aformat=sample_fmts=fltp:channel_layouts=stereo",
            "asetpts=PTS-STARTPTS",
        ]
        gain = float(clip.get("audio_gain_db", 0))
        if gain:
            audio_filters.append(f"volume={gain:.6f}dB")
        if fade_in:
            audio_filters.append(f"afade=t=in:st=0:d={fade_in:.6f}")
        if fade_out:
            audio_filters.append(f"afade=t=out:st={duration - fade_out:.6f}:d={fade_out:.6f}")
        if has_audio:
            filters.append(f"[{index}:a:0]{','.join(audio_filters)}[a{index}]")
        else:
            filters.append(
                f"anullsrc=r=48000:cl=stereo:d={duration:.6f},{','.join(audio_filters)}[a{index}]"
            )
        labels.extend([f"[v{index}]", f"[a{index}]"])

    filters.append(f"{''.join(labels)}concat=n={len(clips)}:v=1:a=1[vcat][acat]")

    audio_cfg = plan.get("audio") or {}
    audio_label = "acat"
    if audio_cfg.get("loudnorm", True):
        target_i = float(audio_cfg.get("target_i", -16))
        target_tp = float(audio_cfg.get("target_tp", -1.5))
        target_lra = float(audio_cfg.get("target_lra", 11))
        filters.append(
            f"[acat]loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}[aout]"
        )
        audio_label = "aout"

    video_label = "vcat"
    captions = plan.get("captions")
    if captions:
        caption_path = resolve(root, str(captions.get("path", "")))
        if not caption_path.is_file():
            raise ValueError(f"Caption file does not exist: {caption_path}")
        style_parts = {
            "FontName": captions.get("font_name", "Arial"),
            "FontSize": int(captions.get("font_size", 42)),
            "MarginV": int(captions.get("margin_v", 90)),
            "Outline": int(captions.get("outline", 3)),
            "Shadow": int(captions.get("shadow", 0)),
            "Alignment": int(captions.get("alignment", 2)),
        }
        style = ",".join(f"{key}={value}" for key, value in style_parts.items())
        filters.append(
            f"[vcat]subtitles=filename='{escape_filter_path(caption_path)}':"
            f"force_style='{style}'[vout]"
        )
        video_label = "vout"

    if output.resolve() in source_paths:
        raise ValueError("Output path must not overwrite a source")

    codec = output_cfg.get("video_codec", "h264_videotoolbox")
    if codec not in {"h264_videotoolbox", "libx264"}:
        raise ValueError("output.video_codec must be h264_videotoolbox or libx264")
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{video_label}]",
            "-map",
            f"[{audio_label}]",
            "-c:v",
            codec,
        ]
    )
    if codec == "libx264":
        command.extend(["-preset", "medium", "-crf", str(output_cfg.get("crf", 18))])
    else:
        command.extend(["-b:v", str(output_cfg.get("video_bitrate", "8M")), "-allow_sw", "1"])
    command.extend(
        [
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-b:a",
            str(output_cfg.get("audio_bitrate", "192k")),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return command, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-nice", action="store_true")
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    root = args.root.resolve()
    command, output = build(plan, root, args.output)
    output = output.resolve()
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output exists; pass --overwrite to replace it: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    command.insert(4, "-y" if args.overwrite else "-n")

    if args.dry_run:
        print(shlex.join(command))
        return 0

    lock_path = Path("/Users/otis/.video-editing/render.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit("Another video render is already running on Otis") from exc
        if not args.no_nice:
            os.nice(10)
        print(shlex.join(command))
        subprocess.run(command, check=True)

    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"Invalid edit plan: {exc}\n")
        raise SystemExit(2)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
