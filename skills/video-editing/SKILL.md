---
name: video-editing
description: Use when editing supplied video footage on Otis, including transcription, editorial cuts, social reframing, captions, color, audio cleanup, previews, QA, or final rendering. Do not use it to generate replacement footage.
---

# Video editing

Edit supplied footage non-destructively on `otis`. Use Faster-Whisper for transcription and FFmpeg Full for deterministic rendering. Keep originals unchanged and create new outputs.

## Fixed environment

- Host: `otis`
- Job root: `/Users/otis/video-work/<job-id>`
- Shared Drive root: `/Users/otis/Google Drive/My Drive/videos`
- FFmpeg Full: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- FFprobe: `/opt/homebrew/opt/ffmpeg-full/bin/ffprobe`
- Python with Faster-Whisper: `/Users/otis/.local/share/fulldev/video-venv/bin/python`
- Remote skill: `/Users/otis/.agents/skills/video-editing`
- Transcription model: `small` for normal work, `base` for rough drafts, and `large-v3` when final accuracy warrants the time and storage.

Use lowered process priority and one render at a time so the agent services stay responsive.

Read [references/commands.md](references/commands.md) when creating a job or running the inspection, transcription, render, or QA scripts manually.

## Storage

- Use `~/video-work/<job-id>` on either Mac for temporary editing work. Otis remains the default editing host.
- Keep lasting source files in Drive `videos/originals`, work-in-progress and review files in `videos/drafts`, and approved deliverables in `videos/finals` so they can be linked from Notion.
- Copy a Drive source into the local job before processing. Never render directly into the streamed Drive folder.
- Copy verified outputs to Drive only when authorized, then verify size and checksum. Keep originals unchanged and delete local jobs only with explicit approval.

## Choose the needed workflow

Resolve the source, destination, requested change, and output format. Check disk space, media metadata, and existing job state. Keep originals unchanged and work in a unique local job. For editorial social deliverables, use the brief or channel's format; default to `1080x1920` only when neither specifies it.

For a technical operation such as trimming known timestamps, compression, remuxing, or resizing, use FFmpeg directly. Preserve source dimensions, framing, timing, and streams except where the requested operation requires changing them. Inspect the relevant source and result. No transcript, contact sheets, style review, or JSON edit plan is needed unless the operation depends on speech, composition, or another editorial choice. Check exact cut boundaries and sync for trims, and composition throughout affected shots for crops.

For editorial work, use the steps that affect the requested result:

1. Use `scripts/inspect_media.py` when choosing content or framing. Inspect the manifest, review sheets, and proxy for burned text, bars, logos, faces, gestures, and important props. A near-silent warning blocks automatic captions until the audio is understood.
2. Transcribe with `scripts/transcribe.py` when selecting by spoken content or writing captions. Keep JSON, TXT, and SRT. Verify names, wording, and timing against audio. Retry once with a larger model if confidence is poor; do not caption gibberish.
3. Follow the supplied examples or brief. Use [references/talking-head-style.md](references/talking-head-style.md) for social talking heads, not for unrelated conversions.
4. Use [references/edit-plan.md](references/edit-plan.md) for a multi-segment edit or the plan-based renderer. Choose cuts by meaning and delivery; silence detection only proposes candidates. Add `qa_points` for risks the plan cannot derive.
5. Check crop, grade, and caption placement with stills before costly renders. Test motion or audio with short windows. Ask about style only when the brief, examples, and prior approval leave a consequential choice unresolved.
6. Render a complete low-resolution preview when needed to judge the edit, then finals from the original sources. Inspect the affected cuts, framing, captions, motion, color, and audio.

## Verify and deliver

For technical conversions, probe the output, fully decode it, and inspect or listen to the affected result. For plan-based edits, use `scripts/qa_media.py` with the plan and relevant caption options; inspect its generated review sheets. Apply the checks below only to features present in the output. Transfer only when authorized, verify the destination checksum, and remove job files only after confirmed delivery and explicit deletion approval.

## Final QA

- Duration, stream presence, resolution, frame rate, codec, color tags, and file size match the target.
- Full decode finishes without errors. No black, frozen, duplicated, or corrupted frames appear around joins.
- First and last syllables survive every cut. Audio has no clicks, pumping, obvious bandwidth loss, or distortion.
- When captions are required, their presence is a hard gate. Open `captions-review.jpg` and confirm visible burned text in every sampled spoken interval. A valid ASS or SRT file alone does not pass.
- Captions match the speech, remain readable over dark and bright frames, and stay inside safe margins. The source does not already contain a competing caption layer.
- Face centering and headroom hold throughout each portrait segment.
- Every animated zoom starts smoothly, holds its intended framing, and resets at the chosen hard cut or uses the explicitly chosen eased return. Check the rendered transition against that choice.
- Color matches the approved reference on representative skin, clothing, and background frames.
- Delivery checksum matches the verified local or Otis render.

Never publish, replace an existing delivery, or upload externally without authorization.
