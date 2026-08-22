# Commands

Use these commands when running the Otis video pipeline manually. Replace every placeholder with a resolved path or ID before execution.

## Preflight

```bash
ssh otis '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -version | head -n 1
/opt/homebrew/opt/ffmpeg-full/bin/ffprobe -version | head -n 1
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -hide_banner -filters 2>/dev/null | awk '\''$2 == "ass" || $2 == "subtitles" {print}'\''
/Users/otis/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper; print(faster_whisper.__version__)"
df -h / | tail -n 1'
```

## Create and ingest

```bash
ssh otis 'mkdir -p /Users/otis/video-work/<job-id>/{source,work,output}'
rsync -av --progress "/absolute/local/input.mp4" "otis:/Users/otis/video-work/<job-id>/source/"
```

## Inspect and transcribe

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/inspect_media.py \
  /Users/otis/video-work/<job-id>/source/*.mp4 \
  --output /Users/otis/video-work/<job-id>/work/media-manifest.json \
  --review-dir /Users/otis/video-work/<job-id>/work/review \
  --analyze-audio'

ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/transcribe.py \
  /Users/otis/video-work/<job-id>/source/input.mp4 \
  --output-dir /Users/otis/video-work/<job-id>/work/input-transcript \
  --model small --language auto --word-timestamps'
```

## Render

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/render_plan.py \
  /Users/otis/video-work/<job-id>/work/edit-plan.json \
  --root /Users/otis/video-work/<job-id>'
```

## QA

```bash
ssh otis '/Users/otis/.hermes/hermes-agent/venv/bin/python \
  /Users/otis/.agents/skills/video-editing/scripts/qa_media.py \
  /Users/otis/video-work/<job-id>/output/final.mp4 \
  --plan /Users/otis/video-work/<job-id>/work/edit-plan.json \
  --root /Users/otis/video-work/<job-id> \
  --output-dir /Users/otis/video-work/<job-id>/work/final-qa \
  --require-captions'
```
