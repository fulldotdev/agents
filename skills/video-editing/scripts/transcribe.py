#!/usr/bin/env python3
"""Transcribe existing audio/video with Faster-Whisper to TXT, SRT, and JSON."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path


def srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def caption_text(words: list[dict]) -> str:
    value = " ".join(str(word["word"]).strip() for word in words).strip()
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def word_caption_cues(
    segments: list[dict],
    duration: float,
    max_words: int,
    max_duration: float,
) -> list[dict]:
    words = [
        word
        for segment in segments
        for word in segment["words"]
        if word.get("start") is not None
        and word.get("end") is not None
        and str(word.get("word", "")).strip()
    ]
    if not words:
        return []

    groups: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        if current:
            previous = current[-1]
            gap = max(0.0, float(word["start"]) - float(previous["end"]))
            previous_text = str(previous["word"]).strip()
            group_duration = float(word["end"]) - float(current[0]["start"])
            should_break = (
                gap >= 0.5
                or bool(re.search(r"[.!?]$", previous_text))
                or (previous_text.endswith(",") and gap >= 0.25)
                or len(current) >= max_words
                or group_duration > max_duration
            )
            if should_break:
                groups.append(current)
                current = []
        current.append(word)
    if current:
        groups.append(current)

    cues = []
    for index, group in enumerate(groups):
        start = max(0.0, float(group[0]["start"]) - 0.08)
        last_word_end = min(duration, float(group[-1]["end"]))
        natural_end = min(duration, last_word_end + 0.45)
        if index + 1 < len(groups):
            next_start = max(0.0, float(groups[index + 1][0]["start"]) - 0.05)
            end = min(natural_end, next_start)
        else:
            end = natural_end
        end = max(last_word_end, end)
        if end - start < 0.5:
            available_end = duration
            if index + 1 < len(groups):
                available_end = max(end, float(groups[index + 1][0]["start"]) - 0.05)
            end = min(available_end, start + 0.5)
        cues.append({"start": start, "end": end, "text": caption_text(group)})
    return cues


def segment_caption_cues(segments: list[dict]) -> list[dict]:
    return [
        {"start": float(segment["start"]), "end": float(segment["end"]), "text": segment["text"]}
        for segment in segments
        if segment["text"]
    ]


def wrap_caption(value: str, width: int) -> str:
    words = value.split()
    if len(value) <= width or len(words) < 4:
        return "\n".join(
            textwrap.wrap(
                value,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )

    candidates = []
    for split_at in range(2, len(words) - 1):
        first = " ".join(words[:split_at])
        second = " ".join(words[split_at:])
        candidates.append((max(len(first), len(second)), abs(len(first) - len(second)), first, second))
    _, _, first, second = min(candidates)
    return f"{first}\n{second}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--caption-width", type=int, default=42)
    parser.add_argument("--caption-max-words", type=int, default=7)
    parser.add_argument("--caption-max-duration", type=float, default=2.5)
    parser.add_argument("--word-timestamps", action="store_true")
    parser.add_argument("--no-vad", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input does not exist or is not a file: {args.input}")
    if args.caption_width < 16:
        raise SystemExit("--caption-width must be at least 16")
    if args.caption_max_words < 2:
        raise SystemExit("--caption-max-words must be at least 2")
    if args.caption_max_duration < 0.5:
        raise SystemExit("--caption-max-duration must be at least 0.5")

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
    caption_cues = (
        word_caption_cues(
            segments,
            duration=float(info.duration),
            max_words=args.caption_max_words,
            max_duration=args.caption_max_duration,
        )
        if args.word_timestamps
        else []
    )
    if not caption_cues:
        caption_cues = segment_caption_cues(segments)

    probabilities = [
        float(word["probability"])
        for segment in segments
        for word in segment["words"]
        if word.get("probability") is not None
    ]
    warnings = []
    if not transcript:
        warnings.append("No speech detected; do not author captions without listening to the source.")
    if probabilities and sum(probabilities) / len(probabilities) < 0.45:
        warnings.append("Low average word confidence; sanity-check the transcript or retry with a larger model.")
    if float(info.language_probability) < 0.5:
        warnings.append("Low language confidence; verify the selected language before captioning.")

    (args.output_dir / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
    payload = {
        "source": str(args.input.resolve()),
        "model": args.model,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
        "segments": segments,
        "caption_cues": caption_cues,
        "warnings": warnings,
    }
    (args.output_dir / "transcript.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    srt_lines = []
    for index, cue in enumerate(caption_cues, start=1):
        wrapped = wrap_caption(cue["text"], args.caption_width)
        srt_lines.extend(
            [
                str(index),
                f"{srt_timestamp(cue['start'])} --> {srt_timestamp(cue['end'])}",
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
                "captions": len(caption_cues),
                "duration": info.duration,
                "warnings": warnings,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
