# Edit plan schema

Use UTF-8 JSON. Resolve relative paths against the job root passed with `--root`.

## Minimal example

```json
{
  "clips": [
    {
      "source": "source/take-1.mp4",
      "in": 2.4,
      "out": 9.8,
      "zoom": 1.0,
      "position_x": 0.5,
      "position_y": 0.5
    },
    {
      "source": "source/take-2.mp4",
      "in": 14.1,
      "out": 22.6,
      "zoom": 1.04,
      "position_x": 0.5,
      "position_y": 0.4
    }
  ],
  "output": {
    "path": "output/preview.mp4",
    "width": 720,
    "height": 1280,
    "fps": 30,
    "video_codec": "h264_videotoolbox",
    "video_bitrate": "3M",
    "audio_bitrate": "160k"
  },
  "audio": {
    "loudnorm": true,
    "target_i": -16,
    "target_tp": -1.5,
    "target_lra": 11
  },
  "captions": {
    "path": "work/final-captions.srt",
    "font_name": "Arial",
    "font_size": 42,
    "margin_v": 90,
    "outline": 3,
    "shadow": 0,
    "alignment": 2
  }
}
```

## Clip fields

- `source` — required source path, relative to the job root or absolute.
- `in` — required start in seconds, at least `0`.
- `out` — required end in seconds and greater than `in`.
- `zoom` — optional constant scale, default `1.0`; normally keep within `1.0–1.08`.
- `position_x` / `position_y` — optional crop focal position from `0.0` to `1.0`, default center.
- `fade_in` / `fade_out` — optional fade-to/from-black duration in seconds. Keep shorter than half the clip.
- `audio_gain_db` — optional per-clip audio gain in dB.

Every clip must contain a video stream. Missing audio is replaced with silence so concatenation remains stable.

## Output fields

- `path` — required and must not equal any source.
- `width` / `height` — required positive even integers.
- `fps` — optional, default `30`.
- `video_codec` — optional, default `h264_videotoolbox`; `libx264` is accepted.
- `video_bitrate` — optional, default `8M`.
- `audio_bitrate` — optional, default `192k`.

Use `720x1280` and a lower bitrate for previews. Use `1080x1920` or `1920x1080` for typical final delivery.

## Audio fields

- `loudnorm` — apply FFmpeg loudness normalization, default `true`.
- `target_i`, `target_tp`, `target_lra` — optional EBU R128 targets.

The renderer performs single-pass normalization. For a critical broadcast master, run a measured two-pass loudnorm workflow separately.

## Caption fields

- `path` — SRT or ASS path.
- `font_name`, `font_size`, `margin_v`, `outline`, `shadow`, `alignment` — optional libass styling overrides.

When using ASS, prefer styles inside the ASS file. Styling overrides are mainly intended for SRT.

## Planning discipline

Record why each take was chosen outside the JSON when editorial review matters. The JSON is the executable decision list; it should contain exact timing, not prose or uncertain alternatives.
