# 01 · Course anatomy

What exists in a finished course, where each piece lives, and what feeds what. Paths are those of the
reference repository; a new course can rename the course but should keep the shape.

## 1. Pages

| Page | Purpose | Notes |
| --- | --- | --- |
| Home `index.html` | Course title, intro film, module grid, comparison table, how to study | The intro film covers the field's common background once. The comparison table names each method ("Affinity metrics · M02"), never bare codes. |
| Module `modules/<id>/index.html` | One per algorithm; the core of the course | Static page per module, so deep links survive refresh. |
| Foundations `foundations/` | Shared basics (graphs, cut, notation) | Modules link here instead of repeating it; each module keeps a one-paragraph review card. |
| Glossary `glossary/` | Every term, zh + en, with a "do not confuse with" column | |
| Guide `guide/` | How the challenges work and why they exist | Linked from every challenge section. |
| Progress `progress/` | Learner's record; export / import JSON | localStorage with a schema version; works when storage throws. |
| Credits `credits/` | Original authors, pinned commits, licences, music credit | |
| 404 | Helps a lost visitor back to the course | |
| English | Same tree under `en/` | Chinese stays at the root URLs. The switch remembers the reader's choice. |

## 2. A module page, section by section

Section headings are numbered like `01 / 目标与问题` with a monospace eyebrow such as `MODULE 07 / KERNIGHAN–LIN`.

1. **Goals and problem (`#goals`)**
   - Hook line (one question, e.g. "一次交换让结果变差了，为什么还要继续换下去？").
   - Prerequisites (links to earlier modules) and a short review card.
   - 6 objectives `o1…o6`, each listing where it is practised (`m07-gain`, `challenge-c2`, `python`).
   - Problem statement, six fields: **input, output, objective, constraints, assumptions, stop**.
2. **Films (`#film`)** — four cards: 科普 / 精讲 / 进阶 / 实验演示. Each card: title, length, one-paragraph
   "why watch this", chapters you can jump to, transcript, captions (WebVTT, off by default because captions
   are burned in), language follows the page.
3. **Lesson (`#lesson`)** — sections with stable anchors `mNN-topic`. Built from `lesson.md` with these blocks:
   - ```` ```terms ```` term cards: `中文名 | english | one-line definition`, placed before first use.
   - Tables of computed values (D values, gains, rounds), all reproducible by the engine.
   - ```` ```callout warn <title> ```` for the one idea a beginner will get wrong.
   - ```` ```pseudo <engine> ```` pseudocode with a comment per line (`code || explanation`).
   - Background (who, when, with a citation), applications (real use, with limits), limitations.
4. **Slides (`#slides`)** — web viewer: slide on top, its transcript directly below, thumbnails, search,
   arrow keys, `#slide-<id>` deep links. Downloads: PDF (fonts embedded), PPTX (editable, notes = transcript).
5. **Lab (`#lab`)** — the algorithm engine in the browser on the course's shared graph. Step / back / to end,
   keyboard arrows, the current pseudocode line highlighted, state panels (candidates, totals, cut),
   controls to change seeds, weights, order, tie rules. Export the run as JSON.
6. **Challenges (`#challenges`)** — see `prompts/06-challenges.md`.
7. **Code lab (`#python`)** — editor + Run checks + "run your own functions" visualiser; downloads the same
   files as a zip for offline work.
8. **Common mistakes (`#mistakes`)** — wrong / why / counterexample / fix.
9. **Sources (`#sources`)** — original author, site, repository, pinned commit, what was kept, what was
   changed and why, references, licence note (including third-party music).

## 3. Source files per module

```
content/modules/<id>/
  module.md            outline, written FIRST (problem, goals, order, acceptance numbers, films, slides, dedup)
  module.json          page data: objectives, problem, film/lab notes, mistakes, limits, credits, code-lab text
  module.en.json       English of the same
  lesson.md            lesson body with terms / callout / pseudo blocks
  lesson.en.md
  slides.json          slides: id, title, figure, film scene, objectives, bullets, transcript
  slides.en.json
  challenges.json      generated index (id, type, difficulty, title, objective, validator)
  challenges.en.json
  crosswalk.json       objective → lesson section → film scene → slide → challenge → code
site/engines/<algo>.js     engine: validate() / run() → events + result + status
site/modules/<id>/lab.js   lab UI for this module
site/modules/<id>/challenges.js  challenge definitions and validators (call the engine)
python/<id>/               starter.py, reference.py, check.py, fixtures/, README.md, en/
video/<id>/films.py        the three drawn films (story, concise, advanced) as scenes + beats
video/<id>/walkthrough.mjs the lab walkthrough recording script
video/<id>/figures.py      figures shared by slides
```

Shared: `content/course.json` (module order, registry), `content/glossary.json`, `content/foundations.md`,
`content/synthesis.md` (home comparison), `content/credits.md`.

## 4. Generated outputs

| Output | From | Script |
| --- | --- | --- |
| `site/data/<id>/traces.json` | engines run on fixed inputs | `scripts/build-traces.mjs` |
| `site/modules/<id>/index.html` (+ `site/en/…`) | `module*.json` + `lesson*.md` | `scripts/build-site.mjs` |
| `site/data/<id>/codelab.json` | `python/<id>/` (check names from running the real checker) | `scripts/build-codelab.mjs` |
| `site/media/<id>/<film>.<lang>.mp4/.vtt/.jpg`, `film.json` | `video/<id>/films.py` | `scripts/film/cinema.py` |
| `site/media/<id>/lab.<lang>.*` | Playwright recording of the real page | `video/<id>/walkthrough.mjs` → `scripts/film/walkthrough.py` |
| `site/slides/<id>/*` | `slides*.json` + figures | `scripts/slides/build_slides.py` |
| `site/downloads/<id>-python*.zip`, `<id>-outline.md` | `python/<id>/`, `module.md` | `scripts/package-downloads.mjs` |
| `site/assets/fonts/*.woff2` | bundled OFL fonts, subset to the characters used | `scripts/build-fonts.py` |

`film.json` (schema 2): one entry per film with `id`, `kind`, `title`, `why`, `music`, `scenes`, and a
version per language holding `src`, `vtt`, `poster`, `duration`, `chapters`, `transcript`,
`readingViolations` (must be 0).

## 5. Data contracts worth copying

- **Engine:** `validate(input)` returns errors; `run(input, options)` returns `{events, result, status}`.
  Events are what the lab steps through, what films animate and what challenges check. Different algorithms
  keep their own data structures; do not force one schema on all.
- **Tie-breaking is explicit** and documented per algorithm (e.g. `(−gain, a, b)` lexicographic).
- **Progress:** one localStorage key `<course>:v1` → `{schemaVersion, savedAt, modules:{id:{challenges:{cid:
  {status, attempts, hintsUsed, updatedAt}}}}}`. Statuses: not started / trying / solved alone / solved after
  viewing the answer. Viewing the answer is never punished. Import validates size, version, known ids.
- **Crosswalk:** every objective maps to lesson anchors, film scene ids, slide numbers, challenges and code-lab
  functions. Build it from data so it never drifts.
