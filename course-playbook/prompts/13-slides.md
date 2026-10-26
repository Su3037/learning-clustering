# Prompt 13 · Slides

---

Make the slide deck for **{{Module NN · topic}}** from `content/modules/{{id}}/slides.json` (and
`slides.en.json`). Model: `content/modules/m07-kernighan-lin/slides.json`, `scripts/slides/build_slides.py`.

`slides.json`: `display`, `title`, `contentVersion`, `slides[]` with `id`, `title`, `figure` (a figure drawn
from engine data, shared with films where possible), `scene` (the matching film scene id), `objectives`,
`bullets` (3–5, short), `transcript` (what a teacher would say: 2–5 sentences, real numbers).

Typical 11–14 slides: title · problem definition · background · key quantity · core rule · why the rule
(counterexample) · step 1 · the subtle step · selection / rollback · next round and stop · pseudocode line by
line · common mistakes · scope and limits · summary.

Outputs (16:9):
- PDF with real (selectable) text and embedded font subsets.
- PPTX with native text boxes, shapes and tables (editable), transcript in the speaker notes.
- PNG/JPG previews for the web viewer.
- Footer on every slide: `Module 0X · title · p/total`; where a slide matches a film scene, show the film
  timestamp (read from `film.json`, so build slides after films).

Check: PPTX page count = PDF page count = slides.json length; every slide has notes; text does not overflow;
the web viewer shows the transcript directly under the slide.
