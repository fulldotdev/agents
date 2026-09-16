# Edit plan schema

The plan is UTF-8 JSON. Relative paths resolve against the job root passed with `--root`.

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
          "ease_in": 3.5,
          "reset": "cut",
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
  },
  "qa_points": [
    {
      "time": 18.4,
      "reason": "Bright background behind the caption"
    }
  ]
}
```

## Clip fields

- `source`: required source path, relative to the job root or absolute.
- `in`: required start in seconds, at least `0`.
- `out`: required end in seconds and greater than `in`.
- `zoom`: optional constant baseline crop, default `1.0`. Not a replacement for an animated emphasis zoom.
- `position_x` / `position_y`: optional crop focal position from `0.0` to `1.0`, default center.
- `zoom_anchor_x` / `zoom_anchor_y`: optional anchor for animated zooms within the cropped frame. For a portrait talking head, `0.5` and about `0.35` usually keep the face stable.
- `zoom_events`: optional list of animated emphasis zooms relative to the start of this clip. Events may not overlap or extend beyond the clip.
- `fade_in` / `fade_out`: optional fade to or from black in seconds. Keep it shorter than half the clip.
- `audio_gain_db`: optional audio gain per clip in dB.

A zoom event has `start`, `scale`, `ease_in`, `reset`, and an optional plain-language `reason`. Defaults are `1.12`, `3.5` seconds, and `reset: "cut"`. A cut-reset event holds its scale to the end of the clip, so use at most one per clip. The next clip starts at the baseline crop.

Set `reset` to `"ease_out"` only when no suitable cut exists. That event also takes `hold` and `ease_out`, default `0.6` and `1.8` seconds. The renderer uses cosine easing at twice the output resolution and downsamples for smooth motion.

Every clip needs a video stream. Missing audio becomes silence so concatenation stays stable. The renderer adds 6 ms audio fades around joins against clicks.

## Output fields

- `path`: required and must not equal any source.
- `width` / `height`: required positive even integers.
- `fps`: optional, default `30`. Preserve the source frame rate unless the destination requires another rate.
- `video_codec`: optional, default `h264_videotoolbox`; `libx264` is accepted.
- `video_bitrate`: optional, default `8M`.
- `audio_bitrate`: optional, default `192k`.
- `color_range`, `colorspace`, `color_trc`, `color_primaries`: optional output color tags. Social SDR defaults to limited-range BT.709.

Use `720x1280` and a lower bitrate for previews. Use `1080x1920` or `1920x1080` for typical final delivery.

## Audio fields

- `loudnorm`: FFmpeg loudness normalization, default `false`. Keep the source dynamics unless measuring and listening show normalization is needed.
- `target_i`, `target_tp`, `target_lra`: optional EBU R128 targets.

When on, the renderer does single-pass normalization. For a final master, prefer deliberate gain or a measured two-pass loudnorm.

## Caption fields

- `path`: SRT or ASS path.
- `font_name`, `font_size`, `margin_v`, `outline`, `shadow`, `alignment`: optional libass styling overrides.

With ASS, put styles in the file. The overrides are meant for SRT.

## QA points

`qa_points` is an optional list of output timestamps with a short `reason`. Use it only for risks `qa_media.py` cannot find itself, such as an unusual color change, a prop entering the crop, or a very bright caption background. The QA helper already makes review frames for every cut, every zoom phase, spread caption cues, and a contact sheet, so do not repeat those.

## Planning

The JSON is the list of decisions the renderer executes. Give each semantic zoom a `reason` so a reviewer can judge the choice, not just the timing. Keep alternatives you are unsure about out of the plan.
