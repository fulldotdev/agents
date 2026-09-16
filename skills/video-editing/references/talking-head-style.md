# Social talking-head style

## Cuts and pacing

- Prefer hard cuts. Use fades only for an intentional opening, ending, or change of scene.
- Cut dead air and weak repetition when it helps the pace. Keep the pauses, breaths, and reactions that make the speaker sound human.
- Do not clip consonants or first and last syllables. Use very short audio fades around joins against clicks.
- A visible jump cut is fine when meaning and rhythm improve. Do not hide every edit with motion.

## Portrait framing

- Reframe per shot or segment. One center crop is not enough when the speaker moves.
- Sample at least the start, middle, and end of each segment. Base the crop on the full movement of face, shoulders, hands, and important props, not one flattering frame.
- Keep the face near the vertical centerline with natural headroom. Include enough shoulders and hands to preserve body language.
- Check the whole segment. Keep the face, captions, and important gestures out of the areas social apps cover with their interface.
- When a crop or zoom moves, anchor it on the face and upper body so the face does not drift.

## Captions

- Burn captions into social previews and finals unless the user opts out. Keep the SRT or ASS too when useful.
- Make captions from the final cut, or retime them after editing. Source timestamps do not survive a reordered montage.
- One or two short lines per cue. Break on a breath, sentence, or clause. Good defaults: a new cue after a pause of about `500 ms`, after a strong comma with about `250 ms` of space, or before a cue passes roughly `7` words or `2.5` seconds. These are defaults, not rules.
- Show each cue for at least about `0.5` seconds when the speech allows. Avoid a one-word second line. Drop filler, stutters, and abandoned self-corrections only when the meaning stays true.
- Use ASS for controlled styling and safe margins. Judge size and position on the real portrait output.
- Before rendering, check the background behind the captions at dark, mid-tone, and bright moments. Use an outline, shadow, or scrim around the glyphs when needed. Do not grade the image or reserve a dead band just for caption readability.

## Semantic zooms

- Zoom for emphasis, not as constant background motion. Approved examples use almost none.
- Prefer a slow push-in when a new subject or argument starts. A thesis, reframing, reveal, or payoff can also justify one. Skip examples, lists, filler, and weak passages.
- Skip the zoom when a posture change or big gesture already gives emphasis.
- Default to at most one zoom under 90 seconds, normally one under 150 seconds, and two or three under 220 seconds, about 35 seconds apart. Break this only when the content has clear separate chapters.
- Ease from `1.0` to about `1.12` over roughly `3` to `4` seconds, then hold the tighter framing for the rest of that thought.
- Reset to the baseline crop on the next meaningful hard cut. The cut hides the reset, so the two scales read as deliberate framings. Do not zoom back out a few seconds after zooming in.
- Pick a moment whose next cut comes naturally. Do not hold the tighter crop through a long unrelated passage. Use a slow eased return only when no suitable cut exists.
- Use cosine or similar easing. Compute moving zooms at twice the delivery resolution and downscale so the motion does not step.
- Review the baseline, the move, the held framing, and the reset after the cut. A short montage of only the zoom windows is the fastest way to get approval.

## Color

- Match the approved references before adding a look. Compare neutral frames and skin tones side by side.
- Start with a correct camera-to-Rec.709 conversion. Make the smallest grade that fixes a problem you can see.
- Protect skin tone. Avoid green casts, over-warm skin, crushed clothing detail, and oversaturated backgrounds.
- Tag social masters as BT.709 limited range when that matches the encode. Check the file in a normal player, because wrong metadata changes apparent contrast and saturation.
- Check a few graded stills or short windows against the brief or reference before rendering a batch.

## Audio

- Keep the source audio unless you can hear a problem. More processing is not better.
- Compare with the clean source and the pauses in the same recording. A generic voice curve does not justify a filter. If you cannot find the problem there, say so instead of inventing a processing chain.
- Work from the camera audio or a lossless intermediate, not a previous delivery.
- No low-pass filter, compressor, denoiser, or loudness normalization by default. Use a light high-pass only for real rumble and transparent peak limiting only when peaks need it.
- Measure loudness and true peak. If the level needs correcting, prefer deliberate gain or measured two-pass normalization over blind single-pass processing.
- Final social audio is normally `48 kHz` AAC at about `320 kbps`. Previews can use less. Listen to the output, not only the meters.
