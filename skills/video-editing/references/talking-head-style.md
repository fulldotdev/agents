# Social talking-head style

## Cuts and pacing

- Prefer hard cuts. Use fades only for an intentional opening, ending, or change of scene.
- Shorten dead air and weak repetition when it improves pace. Preserve rhetorical pauses, breaths, and reactions that make the speaker sound human.
- Do not clip consonants or first and last syllables. Use very short audio fades around joins when needed to prevent clicks.
- A visible jump cut is acceptable when the meaning and rhythm improve. Do not hide every edit with motion.

## Portrait framing

- Reframe per shot or segment. A single center crop is not enough when the speaker moves.
- Sample at least the start, middle, and end of each segment. Base the crop on the combined envelope of face, shoulders, hands, and important props, not one flattering frame.
- Keep the face near the vertical centerline with natural headroom. Include enough shoulders and hands to preserve body language.
- Check the entire segment, not one representative frame. Prevent the face, captions, and important gestures from entering unsafe social-app regions.
- When a crop or zoom moves, anchor it on the face and upper body. Do not let the face drift during the move.

## Captions

- Include burned-in captions in social previews and finals unless the user opts out. Also retain SRT or ASS when useful.
- Generate captions from the final cut or retime them after editing. Source timestamps do not survive a reordered montage.
- Prefer one or two short lines. Break on a breath, sentence, or clause. Useful defaults are a new cue after a pause around `500 ms`, after a strong comma with about `250 ms` of space, or before a cue exceeds roughly `7` words or `2.5` seconds. Treat these as editorial defaults, not rigid language rules.
- Keep each cue visible for at least about `0.5` seconds when speech spacing allows it. Avoid a dangling one-word second line. Drop filler, exact stutters, and abandoned self-corrections when meaning stays truthful.
- Use ASS for controlled styling and safe margins. Judge caption size and position on the actual portrait output.
- Before rendering, check the background behind captions at representative dark, mid-tone, and bright moments. Use a glyph-local outline, shadow, or scrim when needed; do not grade or reserve a dead band merely to make captions readable.

## Semantic zooms

- A zoom is an emphasis mark, not background motion. Approved examples may use almost none.
- Prefer a slow push-in when a new subject or distinct argument begins. A thesis, reframing, reveal, or payoff can also justify one. Skip examples, lists, filler, and weak passages.
- Skip the zoom when a posture change or large gesture already supplies emphasis.
- As a default, allow at most one zoom below 90 seconds, normally one below 150 seconds, and two or three below 220 seconds. Keep roughly 35 seconds between them. Break this only when the content clearly has separate chapters.
- Ease from `1.0` to about `1.12` over roughly `3` to `4` seconds. Then keep the tighter framing for the rest of that thought.
- Reset to the baseline crop on the next meaningful hard cut. The cut hides the reset and makes the two scales read as deliberate camera framings. Do not automatically zoom out a few seconds after zooming in.
- Choose a moment whose next cut arrives naturally. Avoid holding the tighter crop for a long, unrelated passage. Use a slow eased return only when no suitable cut exists and the content clearly calls for one.
- Use cosine or equivalent easing. Calculate moving zooms at twice the delivery resolution and downscale so motion does not step.
- Review baseline, movement, held framing, and the reset after the cut. A compact montage of only zoom windows is the fastest approval artifact.

## Color

- Match approved references before adding a look. Compare neutral frames and skin tones side by side.
- Start with correct camera-to-Rec.709 conversion. Make the smallest grade that fixes an observed problem.
- Protect skin tone. Avoid green casts, over-warm skin, crushed clothing detail, and oversaturated backgrounds.
- Tag social masters as BT.709 with limited range when that matches the encode. Check the rendered file in a normal player because metadata mistakes can change apparent contrast and saturation.
- Check a few representative graded stills or short windows against the brief or approved reference before rendering a batch.

## Audio

- Preserve the source audio unless an audible problem needs correction. More processing is not automatically better.
- Diagnose against the clean source or pauses from the same recording. Generic voice curves are not evidence for a filter. If the source and its pauses do not reveal the problem, state the uncertainty instead of inventing a processing chain.
- Work from the camera audio or a lossless intermediate. Avoid transcoding a previous delivery.
- Do not apply a low-pass filter, compressor, denoiser, or loudness normalization by default. Use a light high-pass only for real low-frequency rumble and transparent peak limiting only when peaks require it.
- Measure loudness and true peak. If level correction is needed, prefer deliberate gain or measured two-pass normalization over blind single-pass processing.
- Final social audio should normally be `48 kHz` AAC at about `320 kbps`; previews may use a lower bitrate. Listen to the output, not only the meters.
