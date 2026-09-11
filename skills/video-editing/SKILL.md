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

Read the `ssh` skill before operating Otis. Use lowered process priority and one render at a time so the agent services stay responsive.

Read [references/commands.md](references/commands.md) when creating a job or running the inspection, transcription, render, or QA scripts manually.

## Storage

- Use `~/video-work/<job-id>` on either Mac for temporary editing work. Otis remains the default editing host.
- Keep lasting source files in Drive `videos/originals`, work-in-progress and review files in `videos/drafts`, and approved deliverables in `videos/finals` so they can be linked from Notion.
- Copy a Drive source into the local job before processing. Never render directly into the streamed Drive folder.
- Copy verified outputs to Drive only when authorized, then verify size and checksum. Keep originals unchanged and delete local jobs only with explicit approval.

## Workflow

1. Resolve every source and destination path. Check disk, media metadata, tool versions, and any existing job state. Never overwrite or delete an original.
2. Create a unique job with `source`, `work`, and `output` directories. Transfer sources with `rsync` without `--delete`.
3. Run `scripts/inspect_media.py`. Inspect its manifest, overview sheet, denser text-scan sheet, and proxy before choosing content or framing. Map existing burned text, letterbox or pillarbox bars, logos, the face and shoulder envelope, hand gestures, and important props. Treat a near-silent audio warning as a stop signal for automatic captions.
4. Transcribe each speaking source separately with `scripts/transcribe.py`. Keep JSON, TXT, and SRT. Read transcript warnings and sanity-check that the text is real language before authoring. Correct names, punctuation, wording, and caption breaks against the audio. Retry once with a larger model when confidence or language detection is poor; never caption confident-looking gibberish.
5. Study the user's approved or published examples when available. Compare cut density, framing, captions, skin tone, background color, motion, and audio. Treat them as the style target, not generic social-video conventions.
6. Build an explicit edit plan using [references/edit-plan.md](references/edit-plan.md). Choose cuts by meaning and delivery. Silence detection may propose cuts but never decides them. Add `qa_points` for risks that cannot be derived from cuts, captions, or zoom events.
7. Calibrate style cheaply. Start with stills and contact sheets for crop, grade, and caption placement. Render motion only for cuts, zooms, lip sync, and audio. For a repeated effect, make one compact review containing only the proposed moments. Do not render a whole batch to discover a static layout problem.
8. Use the brief, supplied examples, or earlier approval to settle style. Ask only when a missing style choice materially affects the result; otherwise render one complete low-resolution preview from the original sources. Inspect video, audio, cuts, framing, captions, color, motion, and lip sync.
9. Render finals from the originals in the format required by the brief or channel. Default to `1080x1920` portrait for social deliverables only when no format is specified.
10. Run `scripts/qa_media.py` on every final. Fully decode it, probe it, and inspect the generated cut, zoom, manual, contact, and caption sheets. Transfer or upload only when authorized. Verify size and checksum after transfer. Remove job files only after confirmed delivery and explicit deletion approval.

Read [references/talking-head-style.md](references/talking-head-style.md) when editing social talking heads. It covers pacing, portrait framing, captions, zooms, color, and audio.

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
