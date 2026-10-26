# Film review checklist

## Story
- [ ] A beginner understands the opening without knowing any term
- [ ] Popular film: the hook is about this algorithm (not the field in general), concrete, true to the mechanism, paid off later
- [ ] Each scene has a reason to follow the previous one; the ending answers the opening
- [ ] No forced analogy, no empty motivational line, no claim of optimality / balance the method does not give

## Picture
- [ ] Dark palette; ivory text, gold focus, teal / blue sides; no bright full-frame backgrounds, cartoons or photoreal images
- [ ] Every important verb is a visible action (not only a colour change)
- [ ] Scene changes when the concept changes; several visual carriers; no long pan of a still image
- [ ] All text legible on a laptop and a classroom projector; no collisions (checked at entry, middle, exit of each scene)

## Data
- [ ] Every number on screen is read from traces and asserted in the script
- [ ] Illustrations (non-course data) are labelled or obviously illustrative; reconstructions labelled

## Captions
- [ ] zh: Chinese + small English line; en: English only; on-screen labels switch language
- [ ] Reading violations = 0 in both languages; VTT cue count = transcript lines
- [ ] Natural phrasing, one idea per caption, each caption matches what is on screen

## Music and export
- [ ] Popular / intro film: the exact chosen recording, original speed; events land on real musical structure
- [ ] Other films: course score, low level (≈ −24 dBFS RMS)
- [ ] No clipping, truncation or drift; clean ending
- [ ] 1920×1080, 30 fps, H.264 yuv420p + AAC, faststart; decodes fully; seeking works
- [ ] `film.json` updated: duration, chapters (actual times), transcript, `readingViolations`, `why`
- [ ] Music credit in the film and on the page; third-party audio not committed

## Honesty
- [ ] Report says what was reviewed (contact sheets, sampled frames, full playback) and what was not
