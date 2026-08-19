#!/usr/bin/env python3
"""Transcribe existing audio/video with Faster-Whisper to TXT, SRT, and JSON."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path


def srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--caption-width", type=int, default=42)
    parser.add_argument("--word-timestamps", action="store_true")
    parser.add_argument("--no-vad", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input does not exist or is not a file: {args.input}")
    if args.caption_width < 16:
        raise SystemExit("--caption-width must be at least 16")

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            "faster-whisper is unavailable; run this script with "
            "/Users/otis/.hermes/hermes-agent/venv/bin/python"
        ) from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)
    language = None if args.language.lower() == "auto" else args.language
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(
        str(args.input),
        language=language,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
        word_timestamps=args.word_timestamps,
        condition_on_previous_text=True,
    )

    segments = []
    transcript_parts = []
    for segment in segments_iter:
        text = segment.text.strip()
        transcript_parts.append(text)
        words = []
        for word in segment.words or []:
            words.append(
                {
                    "start": word.start,
                    "end": word.end,
                    "word": word.word,
                    "probability": word.probability,
                }
            )
        segments.append(
            {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": text,
                "words": words,
            }
        )

    transcript = " ".join(part for part in transcript_parts if part).strip()
    (args.output_dir / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
    payload = {
        "source": str(args.input.resolve()),
        "model": args.model,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
        "segments": segments,
    }
    (args.output_dir / "transcript.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    srt_lines = []
    for index, segment in enumerate(segments, start=1):
        wrapped = "\n".join(
            textwrap.wrap(
                segment["text"],
                width=args.caption_width,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        srt_lines.extend(
            [
                str(index),
                f"{srt_timestamp(segment['start'])} --> {srt_timestamp(segment['end'])}",
                wrapped,
                "",
            ]
        )
    (args.output_dir / "captions.srt").write_text("\n".join(srt_lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "language": info.language,
                "segments": len(segments),
                "duration": info.duration,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
