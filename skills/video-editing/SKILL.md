---
name: video-editing
description: Use when editing supplied video footage on Otis, including transcription, editorial cuts, social reframing, captions, color, audio cleanup, previews, QA, or final rendering. Do not use it to generate replacement footage.
---

# Video editing

Edit supplied footage on `otis` without changing the originals. Use Faster-Whisper for transcription and FFmpeg Full for repeatable rendering.

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

- Use `~/video-work/<job-id>` for temporary editing work. Otis remains the default editing host.
- Keep lasting source files in Drive `videos/originals`, work-in-progress and review files in `videos/drafts`, and approved deliverables in `videos/finals` so they can be linked from Notion.
- Copy a Drive source into the local job before processing. Never render directly into the streamed Drive folder.
- Copy verified outputs to Drive only when authorized. Confirm their size and checksum. Delete local jobs only after confirmed delivery and explicit approval.

## Choose the needed workflow

Resolve the source, destination, change, and output format. Check disk space, media metadata, and existing job state. Work in a unique local job. For social edits, follow the brief or channel format. Use `1080x1920` only when neither specifies one.

For trimming known timestamps, compression, remuxing, or resizing, use FFmpeg directly. Preserve dimensions, framing, timing, and streams unless the request changes them. Inspect the relevant source and result. Use transcripts, contact sheets, style review, and a JSON plan only when speech, composition, or another editorial choice requires them. Check cut boundaries and sync for trims, and composition throughout cropped shots.

For editorial work, use the steps that affect the requested result:

1. Use `scripts/inspect_media.py` when choosing content or framing. Check the manifest, review sheets, and proxy for burned text, bars, logos, faces, gestures, and important props. If it reports near-silent audio, understand the audio before generating captions.
2. Transcribe with `scripts/transcribe.py` when selecting spoken content or writing captions. Keep JSON, TXT, and SRT. Check names, wording, and timing against the audio. If confidence is poor, retry once with a larger model. Do not caption text that remains unintelligible.
3. Follow the supplied examples or brief. Use [references/talking-head-style.md](references/talking-head-style.md) for social talking heads, not for unrelated conversions.
4. Use [references/edit-plan.md](references/edit-plan.md) for a multi-segment edit or the plan-based renderer. Choose cuts by meaning and delivery. Treat silence detection as a source of candidates. Add `qa_points` only for risks the plan cannot derive.
5. Check crop, grade, and caption placement with stills before a costly render. Test motion and audio with short clips. Ask about style only when the brief, examples, and prior approval leave a choice that could change the result.
6. Render a complete low-resolution preview when needed to judge the edit. Render finals from the original sources. Inspect the cuts, framing, captions, motion, color, and audio affected by the request.

## Verify and deliver

For technical conversions, probe and fully decode the output, then inspect or listen to it. For plan-based edits, run `scripts/qa_media.py` with the plan and caption options, then inspect its review sheets. Apply only relevant checks below. Transfer only when authorized and confirm the destination checksum.

## Final QA

- Duration, stream presence, resolution, frame rate, codec, color tags, and file size match the target.
- Full decode finishes without errors. No black, frozen, duplicated, or corrupted frames appear around joins.
- First and last syllables survive every cut. Audio has no clicks, pumping, obvious bandwidth loss, or distortion.
- When captions are required, open `captions-review.jpg` and confirm visible burned text in every sampled spoken interval. An ASS or SRT file alone does not pass.
- Captions match the speech, remain readable over dark and bright frames, and stay inside safe margins. The source does not already contain a competing caption layer.
- Face centering and headroom hold throughout each portrait segment.
- Every animated zoom starts smoothly, holds the intended framing, and either resets at the chosen hard cut or uses the chosen eased return. Check the rendered transition.
- Color matches the approved reference on representative skin, clothing, and background frames.
- The delivered file's checksum matches the verified render on Otis or the local machine.

Never publish, replace an existing delivery, or upload externally without authorization.
