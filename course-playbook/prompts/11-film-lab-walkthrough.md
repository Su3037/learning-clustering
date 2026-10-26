# Prompt 11 · Lab walkthrough film (实验演示)

---

Record the lab walkthrough for **{{Module NN · topic}}** from the real page, in both languages
(2:20–3:00, original score). Model: `video/m07-kernighan-lin/walkthrough.mjs`,
`scripts/film/recorder.mjs`, `scripts/film/walkthrough.py`.

Needs a scriptable browser (Playwright or similar) and the local site served under its project subpath.

1. Write `video/{{id}}/walkthrough.mjs`: open the module page (`en/` for English), then a series of shots.
   Each shot = caption pair + optional chapter + optional zoom target + actions (scroll, move the cursor to
   a control, choose, click, type, wait). Use accessible names / visible labels to find controls in each
   language.
2. Chapters: **the lab** (what each control does, step through one full run, point at the state panels and
   the highlighted pseudocode line) → **change a parameter** (a seed / weight / order change and why the
   result differs) → **code lab** (type one function, run checks, show PASS / INCOMPLETE) → **your code,
   visualised** → **challenges** (where to go next).
3. If typing everything is long, type one function on screen, fast-forward the rest, and say so.
4. Compose: page in a window on the dark backdrop, drawn cursor with click pulses, eased zoom on the part
   being explained, captions as in every film.
5. Check captions against what the page really shows (numbers come from the live engine, so they must match
   the lesson).

Output: `site/media/{{id}}/lab.{zh,en}.*` merged into `film.json`. Re-record when the page UI changes.
