---
name: video-editing
description: Edit existing recorded video footage on the Apple Silicon worker `otis` through SSH. Use when Codex must inspect, transcribe, trim, reorder, combine, reframe, caption, lightly zoom or fade, normalize audio, preview, QA, render, or deliver real source videos without generating replacement footage. Supports talking-head videos, multiple takes, reels/shorts, and longer 16:9 edits using Faster-Whisper and FFmpeg Full.
---

# Video Editing

Edit originals non-destructively on `otis`. Use Faster-Whisper for speech recognition and FFmpeg Full for deterministic rendering. Never substitute generated video for supplied footage unless the user separately requests it.

## Fixed environment

- Host: `otis`
- Job root: `/Users/otis/.video-editing/jobs/<job-id>`
- FFmpeg: `/opt/homebrew/bin/ffmpeg`
- FFprobe: `/opt/homebrew/bin/ffprobe`
- Python with Faster-Whisper: `/Users/otis/.hermes/hermes-agent/venv/bin/python`
- Remote skill: `/Users/otis/.agents/skills/video-editing`
- Default transcription model: `small`; use `base` for fast drafts and `large-v3` only when final accuracy justifies the extra time and storage.

## Workflow

1. Read the `ssh` skill before operating `otis`.
2. Check the local and remote source paths, available disk, tool versions, and existing job directory. Do not overwrite or delete originals.
3. Create a unique job with `source`, `work`, and `output` directories. Use a short slug plus UTC timestamp.
4. Transfer local sources with `rsync`; never use `--delete`. If sources already exist on `otis`, copy them into the job's `source` directory only when the user wants an isolated job copy.
5. Run `scripts/inspect_media.py` to create `media-manifest.json`, low-resolution proxies, and contact sheets. Inspect the manifest and review images before making editorial decisions.
6. Run `scripts/transcribe.py` with Faster-Whisper. Keep the raw JSON, TXT, and SRT. Correct language, names, punctuation, and caption line breaks without altering timestamps blindly.
7. Build an explicit edit plan using [references/edit-plan.md](references/edit-plan.md). Select takes by content and visual quality; do not equate every pause with a mistake.
8. Render a low-resolution preview first with `scripts/render_plan.py`. Inspect video, audio, cuts, framing, captions, and lip sync.
9. Revise the plan, then render the final output from the original sources. Keep captions and the plan alongside the master.
10. Verify the final file with FFprobe and sample frames. Download deliverables with `rsync` when needed. Clean job files only after delivery is confirmed and the user authorizes deletion.

## Preflight

Run:

```bash
ssh otis '/opt/homebrew/bin/ffmpeg -version | head -n 1
/opt/homebrew/bin/ffprobe -version | head -n 1
/Users/otis/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper; print(faster_whisper.__version__)"
df -h / | tail -n 1'
```

Confirm FFmpeg exposes `subtitles` and `ass` before burning captions:

```bash
ssh otis '/opt/homebrew/bin/ffmpeg -hide_banner -filters 2>/dev/null | awk '\''$2 == "ass" || $2 == "subtitles" {print}'\'''
```

## Job setup and ingest

Use an explicit validated job ID:

```bash
ssh otis 'mkdir -p /Users/otis/.video-editing/jobs/<job-id>/{source,work,output}'
rsync -av --progress "/absolute/local/input.mp4" "otis:/Users/otis/.video-editing/jobs/<job-id>/source/"
```

Do not place API tokens, customer names, or confidential content in the job ID.

## Inspect and transcribe

After this skill has been synchronized to `otis`:

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/inspect_media.py \
  /Users/otis/.video-editing/jobs/<job-id>/source/*.mp4 \
  --output /Users/otis/.video-editing/jobs/<job-id>/work/media-manifest.json \
  --review-dir /Users/otis/.video-editing/jobs/<job-id>/work/review'
```

Transcribe each speaking source separately so timestamps stay tied to the original file:

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/transcribe.py \
  /Users/otis/.video-editing/jobs/<job-id>/source/input.mp4 \
  --output-dir /Users/otis/.video-editing/jobs/<job-id>/work/input-transcript \
  --model small --language auto --word-timestamps'
```

## Render and QA

Write the plan locally with exact source-relative in/out points, then transfer it to `work/edit-plan.json`. Render preview and final to different paths.

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/render_plan.py \
  /Users/otis/.video-editing/jobs/<job-id>/work/edit-plan.json \
  --root /Users/otis/.video-editing/jobs/<job-id> --overwrite'
```

Validate at minimum:

- Output duration and audio/video streams.
- No clipped first/last syllables at cuts.
- No frozen or black frames around joins.
- Captions match speech and stay inside safe margins.
- Framing keeps the speaker visible in the target aspect ratio.
- Loudness is consistent and speech is not distorted.
- Final resolution, frame rate, codec, and file size fit the destination.

Use `nice`/the render script's default lowered priority and process one render at a time so Hermes stays responsive.

## Editorial rules

- Preserve originals and store every decision in the edit plan.
- Prefer hard cuts for talking heads. Use fades intentionally, not between every sentence.
- Keep punch-in zooms subtle, normally `1.02` to `1.06`.
- Treat silence detection as a suggestion. Preserve rhetorical pauses and breaths that make speech natural.
- Avoid removing filler words when the resulting cut clips consonants or creates visible jump artifacts.
- Generate captions from the final cut or retime them after editing; never assume source timestamps survive a reordered montage.
- Use ASS/SRT burn-in only for the requested deliverable; also retain a separate caption file when useful.
- Never publish or upload externally without explicit user authorization.
