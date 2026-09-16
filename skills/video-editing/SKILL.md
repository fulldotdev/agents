---
name: video-editing
description: Use when editing supplied video footage on Otis, including transcription, editorial cuts, social reframing, captions, color, audio cleanup, previews, QA, or final rendering.
---

# Video editing

Edit supplied footage on Otis without touching the originals. Faster-Whisper transcribes, FFmpeg Full renders. Do not generate replacement footage.

## Environment

- Host: `otis`
- Job root: `/Users/otis/video-work/<job-id>`
- Drive root: `/Users/otis/Google Drive/My Drive/videos`
- FFmpeg Full: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- FFprobe: `/opt/homebrew/opt/ffmpeg-full/bin/ffprobe`
- Python with Faster-Whisper: `/Users/otis/.local/share/fulldev/video-venv/bin/python`
- Remote skill: `/Users/otis/.agents/skills/video-editing`
- Transcription model: `small` for normal work, `base` for rough drafts, `large-v3` when final accuracy is worth the time.

Run renders one at a time at lowered priority so the agent services stay responsive. Read [references/commands.md](references/commands.md) when creating a job or running the inspect, transcribe, render, or QA scripts by hand.

## Storage

- `~/video-work/<job-id>` is the temporary workspace. Copy a Drive source into it before processing. Never render into the streamed Drive folder.
- On Drive, sources go in `videos/originals`, work-in-progress and review files in `videos/drafts`, approved deliverables in `videos/finals`, so Notion can link them.
- Copy outputs to Drive only when approved, and check size and checksum at the destination. Delete a local job only after confirmed delivery and approval.

## Pick the workflow

Resolve the source, destination, change, and output format. Check disk space, media metadata, and existing job state. Work in a fresh local job. For social edits, follow the brief or channel format, and use `1080x1920` only when neither gives one.

For trims at known timestamps, compression, remuxing, or resizing, use FFmpeg directly. Keep dimensions, framing, timing, and streams unless the request changes them. Inspect the source and the result. Use transcripts, contact sheets, style review, and a JSON plan only when speech, composition, or another editorial choice needs them. Check cut boundaries and sync on trims, and composition throughout cropped shots.

For editorial work, use the steps the result needs:

1. Run `scripts/inspect_media.py` when choosing content or framing. Check the manifest, review sheets, and proxy for burned text, bars, logos, faces, gestures, and important props. If it reports near-silent audio, understand the audio before making captions.
2. Run `scripts/transcribe.py` when selecting spoken content or writing captions. Keep JSON, TXT, and SRT. Check names, wording, and timing against the audio. On poor confidence, retry once with a larger model. Do not caption speech that stays unintelligible.
3. Follow the supplied examples or brief. Use [references/talking-head-style.md](references/talking-head-style.md) for social talking heads only.
4. Use [references/edit-plan.md](references/edit-plan.md) for a multi-segment edit or the plan renderer. Cut by meaning and delivery. Silence detection gives candidates, not decisions. Add `qa_points` only for risks the plan cannot derive.
5. Check crop, grade, and caption placement on stills before a costly render. Test motion and audio with short clips. Ask about style only when the brief, examples, and earlier approvals leave a choice that changes the result.
6. Render a full low-resolution preview when you need it to judge the edit. Render finals from the original sources. Inspect the cuts, framing, captions, motion, color, and audio the request touched.

## QA and delivery

For a technical conversion, probe and fully decode the output, then watch or listen to it. For a plan-based edit, run `scripts/qa_media.py` with the plan and caption options and look at its review sheets. Apply the checks that apply:

- Duration, streams, resolution, frame rate, codec, color tags, and file size match the target.
- A full decode finishes without errors. No black, frozen, duplicated, or corrupted frames around joins.
- First and last syllables survive every cut. No clicks, pumping, bandwidth loss, or distortion in the audio.
- When captions are required, open `captions-review.jpg` and confirm burned text in every sampled spoken interval. An ASS or SRT file alone does not count.
- Captions match the speech, stay readable over dark and bright frames, and stay inside safe margins. The source has no competing caption layer.
- Face centering and headroom hold through each portrait segment.
- Every animated zoom starts smoothly, holds its framing, and resets at the chosen cut or with the chosen eased return. Check the rendered transition.
- Color matches the approved reference on skin, clothing, and background frames.
- The delivered file's checksum matches the verified render.

Never publish, replace an existing delivery, or upload externally without approval.
