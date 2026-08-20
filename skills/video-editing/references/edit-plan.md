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
      "zoom": 1.0,
      "position_x": 0.5,
      "position_y": 0.4,
      "zoom_anchor_x": 0.5,
      "zoom_anchor_y": 0.35,
      "zoom_events": [
        {
          "start": 1.2,
          "scale": 1.12,
          "ease_in": 1.4,
          "hold": 0.6,
          "ease_out": 1.8,
          "reason": "The sentence states the central conclusion"
        }
      ]
    }
  ],
  "output": {
    "path": "output/preview.mp4",
    "width": 720,
    "height": 1280,
    "fps": 25,
    "video_codec": "h264_videotoolbox",
    "video_bitrate": "3M",
    "audio_bitrate": "192k",
    "color_range": "tv",
    "colorspace": "bt709",
    "color_trc": "bt709",
    "color_primaries": "bt709"
  },
  "audio": {
    "loudnorm": false,
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
- `zoom` — optional constant baseline crop, default `1.0`. Do not use it as a substitute for an animated emphasis zoom.
- `position_x` / `position_y` — optional crop focal position from `0.0` to `1.0`, default center.
- `zoom_anchor_x` / `zoom_anchor_y` — optional anchor for animated zooms within the cropped frame. For a portrait talking head, `0.5` and about `0.35` usually keep the face stable.
- `zoom_events` — optional list of animated emphasis zooms relative to the start of this clip. Events may not overlap or cross the end of the clip.
- `fade_in` / `fade_out` — optional fade-to/from-black duration in seconds. Keep shorter than half the clip.
- `audio_gain_db` — optional per-clip audio gain in dB.

Each zoom event accepts `start`, `scale`, `ease_in`, `hold`, `ease_out`, and an optional human-readable `reason`. Defaults are `1.12`, `1.4`, `0.6`, and `1.8` seconds. The renderer uses cosine easing, works at twice the output resolution, and downsamples for smooth motion.

Every clip must contain a video stream. Missing audio is replaced with silence so concatenation remains stable. The renderer applies 6 ms audio fades around joins to prevent clicks.

## Output fields

- `path` — required and must not equal any source.
- `width` / `height` — required positive even integers.
- `fps` — optional, default `30`; normally preserve the source frame rate unless the destination requires another rate.
- `video_codec` — optional, default `h264_videotoolbox`; `libx264` is accepted.
- `video_bitrate` — optional, default `8M`.
- `audio_bitrate` — optional, default `192k`.
- `color_range`, `colorspace`, `color_trc`, `color_primaries` — optional output color tags. Social SDR defaults to limited-range BT.709.

Use `720x1280` and a lower bitrate for previews. Use `1080x1920` or `1920x1080` for typical final delivery.

## Audio fields

- `loudnorm` — apply FFmpeg loudness normalization, default `false`. Preserve source dynamics unless measurement and listening show that normalization is needed.
- `target_i`, `target_tp`, `target_lra` — optional EBU R128 targets.

When enabled, the renderer performs single-pass normalization. Prefer deliberate gain or measured two-pass loudnorm for a final master.

## Caption fields

- `path` — SRT or ASS path.
- `font_name`, `font_size`, `margin_v`, `outline`, `shadow`, `alignment` — optional libass styling overrides.

When using ASS, prefer styles inside the ASS file. Styling overrides are mainly intended for SRT.

## Planning discipline

The JSON is the executable decision list. Use `reason` on a semantic zoom so reviewers can judge the editorial choice, not only its timing. Keep uncertain alternatives outside the plan.
