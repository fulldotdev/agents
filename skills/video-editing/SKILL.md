---
name: video-editing
description: Use when editing supplied video footage on Otis, including transcription, editorial cuts, social reframing, captions, color, audio cleanup, previews, QA, or final rendering. Do not use it to generate replacement footage.
---

# Video editing

Edit supplied footage non-destructively on `otis`. Use Faster-Whisper for transcription and FFmpeg Full for deterministic rendering. Keep originals unchanged and create new outputs.

## Fixed environment

- Host: `otis`
- Job root: `/Users/otis/.video-editing/jobs/<job-id>`
- FFmpeg Full: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- FFprobe: `/opt/homebrew/opt/ffmpeg-full/bin/ffprobe`
- Python with Faster-Whisper: `/Users/otis/.hermes/hermes-agent/venv/bin/python`
- Remote skill: `/Users/otis/.agents/skills/video-editing`
- Transcription model: `small` for normal work, `base` for rough drafts, and `large-v3` when final accuracy warrants the time and storage.

Read the `ssh` skill before operating Otis. Use lowered process priority and one render at a time so Hermes stays responsive.

## Workflow

1. Resolve every source and destination path. Check disk, media metadata, tool versions, and any existing job state. Never overwrite or delete an original.
2. Create a unique job with `source`, `work`, and `output` directories. Transfer sources with `rsync` without `--delete`.
3. Run `scripts/inspect_media.py`. Inspect its manifest, overview sheet, denser text-scan sheet, and proxy before choosing content or framing. Map existing burned text, letterbox or pillarbox bars, logos, the face and shoulder envelope, hand gestures, and important props. Treat a near-silent audio warning as a stop signal for automatic captions.
4. Transcribe each speaking source separately with `scripts/transcribe.py`. Keep JSON, TXT, and SRT. Read transcript warnings and sanity-check that the text is real language before authoring. Correct names, punctuation, wording, and caption breaks against the audio. Retry once with a larger model when confidence or language detection is poor; never caption confident-looking gibberish.
5. Study the user's approved or published examples when available. Compare cut density, framing, captions, skin tone, background color, motion, and audio. Treat them as the style target, not generic social-video conventions.
6. Build an explicit edit plan using [references/edit-plan.md](references/edit-plan.md). Choose cuts by meaning and delivery. Silence detection may propose cuts but never decides them. Add `qa_points` for risks that cannot be derived from cuts, captions, or zoom events.
7. Calibrate style cheaply. Start with stills and contact sheets for crop, grade, and caption placement. Render motion only for cuts, zooms, lip sync, and audio. For a repeated effect, make one compact review containing only the proposed moments. Do not render a whole batch to discover a static layout problem.
8. After style approval, render one complete low-resolution preview from the original sources. Inspect video, audio, cuts, framing, captions, color, motion, and lip sync.
9. Render finals from the originals. For Sil's social deliverables, always include a `1080x1920` portrait version. Keep or add landscape when the requested use needs it.
10. Run `scripts/qa_media.py` on every final. Fully decode it, probe it, and inspect the generated cut, zoom, manual, contact, and caption sheets. Transfer or upload only when authorized. Verify size and checksum after transfer. Remove job files only after confirmed delivery and explicit deletion approval.

## Editorial standard for social talking heads

### Cuts and pacing

- Prefer hard cuts. Use fades only for an intentional opening, ending, or change of scene.
- Shorten dead air and weak repetition when it improves pace. Preserve rhetorical pauses, breaths, and reactions that make the speaker sound human.
- Do not clip consonants or first and last syllables. Use very short audio fades around joins when needed to prevent clicks.
- A visible jump cut is acceptable when the meaning and rhythm improve. Do not hide every edit with motion.

### Portrait framing

- Reframe per shot or segment. A single center crop is not enough when the speaker moves.
- Sample at least the start, middle, and end of each segment. Base the crop on the combined envelope of face, shoulders, hands, and important props, not one flattering frame.
- Keep the face near the vertical centerline with natural headroom. Include enough shoulders and hands to preserve body language.
- Check the entire segment, not one representative frame. Prevent the face, captions, and important gestures from entering unsafe social-app regions.
- When a crop or zoom moves, anchor it on the face and upper body. Do not let the face drift during the move.

### Captions

- Include burned-in captions in social previews and finals unless the user opts out. Also retain SRT or ASS when useful.
- Generate captions from the final cut or retime them after editing. Source timestamps do not survive a reordered montage.
- Prefer one or two short lines. Break on a breath, sentence, or clause. Useful defaults are a new cue after a pause around `500 ms`, after a strong comma with about `250 ms` of space, or before a cue exceeds roughly `7` words or `2.5` seconds. Treat these as editorial defaults, not rigid language rules.
- Keep each cue visible for at least about `0.5` seconds when speech spacing allows it. Avoid a dangling one-word second line. Drop filler, exact stutters, and abandoned self-corrections when meaning stays truthful.
- Use ASS for controlled styling and safe margins. Judge caption size and position on the actual portrait output.
- Before rendering, check the background behind captions at representative dark, mid-tone, and bright moments. Use a glyph-local outline, shadow, or scrim when needed; do not grade or reserve a dead band merely to make captions readable.

### Semantic zooms

- A zoom is an emphasis mark, not background motion. Approved examples may use almost none.
- Prefer a slow push-in when a new subject or distinct argument begins. A thesis, reframing, reveal, or payoff can also justify one. Skip examples, lists, filler, and weak passages.
- Skip the zoom when a posture change or large gesture already supplies emphasis.
- As a default, allow at most one zoom below 90 seconds, normally one below 150 seconds, and two or three below 220 seconds. Keep roughly 35 seconds between them. Break this only when the content clearly has separate chapters.
- Ease from `1.0` to about `1.12` over roughly `3` to `4` seconds. Then keep the tighter framing for the rest of that thought.
- Reset to the baseline crop on the next meaningful hard cut. The cut hides the reset and makes the two scales read as deliberate camera framings. Do not automatically zoom out a few seconds after zooming in.
- Choose a moment whose next cut arrives naturally. Avoid holding the tighter crop for a long, unrelated passage. Use a slow eased return only when no suitable cut exists and the content clearly calls for one.
- Use cosine or equivalent easing. Calculate moving zooms at twice the delivery resolution and downscale so motion does not step.
- Review baseline, movement, held framing, and the reset after the cut. A compact montage of only zoom windows is the fastest approval artifact.

### Color

- Match approved references before adding a look. Compare neutral frames and skin tones side by side.
- Start with correct camera-to-Rec.709 conversion. Make the smallest grade that fixes an observed problem.
- Protect skin tone. Avoid green casts, over-warm skin, crushed clothing detail, and oversaturated backgrounds.
- Tag social masters as BT.709 with limited range when that matches the encode. Check the rendered file in a normal player because metadata mistakes can change apparent contrast and saturation.
- Approve a few representative graded stills or short windows before rendering a batch.

### Audio

- Preserve the source audio unless an audible problem needs correction. More processing is not automatically better.
- Diagnose against the clean source or pauses from the same recording. Generic voice curves are not evidence for a filter. If the source and its pauses do not reveal the problem, state the uncertainty instead of inventing a processing chain.
- Work from the camera audio or a lossless intermediate. Avoid transcoding a previous delivery.
- Do not apply a low-pass filter, compressor, denoiser, or loudness normalization by default. Use a light high-pass only for real low-frequency rumble and transparent peak limiting only when peaks require it.
- Measure loudness and true peak. If level correction is needed, prefer deliberate gain or measured two-pass normalization over blind single-pass processing.
- Final social audio should normally be `48 kHz` AAC at about `320 kbps`; previews may use a lower bitrate. Listen to the output, not only the meters.

## Commands

Preflight:

```bash
ssh otis '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -version | head -n 1
/opt/homebrew/opt/ffmpeg-full/bin/ffprobe -version | head -n 1
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -hide_banner -filters 2>/dev/null | awk '\''$2 == "ass" || $2 == "subtitles" {print}'\''
/Users/otis/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper; print(faster_whisper.__version__)"
df -h / | tail -n 1'
```

Create a job and ingest a source:

```bash
ssh otis 'mkdir -p /Users/otis/.video-editing/jobs/<job-id>/{source,work,output}'
rsync -av --progress "/absolute/local/input.mp4" "otis:/Users/otis/.video-editing/jobs/<job-id>/source/"
```

Inspect and transcribe:

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/inspect_media.py \
  /Users/otis/.video-editing/jobs/<job-id>/source/*.mp4 \
  --output /Users/otis/.video-editing/jobs/<job-id>/work/media-manifest.json \
  --review-dir /Users/otis/.video-editing/jobs/<job-id>/work/review \
  --analyze-audio'

ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/transcribe.py \
  /Users/otis/.video-editing/jobs/<job-id>/source/input.mp4 \
  --output-dir /Users/otis/.video-editing/jobs/<job-id>/work/input-transcript \
  --model small --language auto --word-timestamps'
```

Render an edit plan:

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/render_plan.py \
  /Users/otis/.video-editing/jobs/<job-id>/work/edit-plan.json \
  --root /Users/otis/.video-editing/jobs/<job-id>'
```

QA a final against its plan:

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/qa_media.py \
  /Users/otis/.video-editing/jobs/<job-id>/output/final.mp4 \
  --plan /Users/otis/.video-editing/jobs/<job-id>/work/edit-plan.json \
  --root /Users/otis/.video-editing/jobs/<job-id> \
  --output-dir /Users/otis/.video-editing/jobs/<job-id>/work/final-qa \
  --require-captions'
```

## Final QA

- Duration, stream presence, resolution, frame rate, codec, color tags, and file size match the target.
- Full decode finishes without errors. No black, frozen, duplicated, or corrupted frames appear around joins.
- First and last syllables survive every cut. Audio has no clicks, pumping, obvious bandwidth loss, or distortion.
- Caption presence is a hard gate. Open `captions-review.jpg` and confirm visible burned text in every sampled spoken interval. A valid ASS or SRT file alone does not pass.
- Captions match the speech, remain readable over dark and bright frames, and stay inside safe margins. The source does not already contain a competing caption layer.
- Face centering and headroom hold throughout each portrait segment.
- Every animated zoom has a smooth baseline, peak, and full return.
- Color matches the approved reference on representative skin, clothing, and background frames.
- Delivery checksum matches the verified local or Otis render.

Never publish, replace an existing delivery, or upload externally without authorization.
