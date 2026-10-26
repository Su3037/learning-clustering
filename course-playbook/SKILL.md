---
name: course-playbook
description: Build a bilingual (中文/English) algorithm course in the style of Learning Clustering — one static site, one page per module, a real in-browser lab, an in-browser Python code lab, four films per module (popular science, concise, advanced, lab walkthrough), slides with transcripts, graded challenges and tests. Use when asked to make a new course, a new module, or any of its films/pages in this house style.
---

# Course playbook (Learning Clustering house style)

This folder is the distilled production experience of **Learning Clustering · 连接与分组**
(site: https://su3037.github.io/learning-clustering/, source: https://github.com/Su3037/learning-clustering).
It is written for any capable coding agent: Claude, Codex, Cursor, DeepSeek, Gemini, or a human team.
Nothing here depends on one vendor's tools. Where a step needs a capability (rendering video, driving a
browser), the requirement is stated, and the reference implementation in this repository shows one way to do it.

You are the course designer, algorithm engineer, film director and integration lead at once. The job is to
**ship a working course**, not to describe one. A storyboard is not a film; a screenshot is not a lab.

## 1. What a finished course looks like

One course = a home page + N modules (this course: 8) + shared pages (foundations, glossary, guide,
progress, credits, 404). Every page exists in Chinese and English with a 中文 / EN switch.

Every module page has these sections, in this order (see `reference/01-course-anatomy.md`):

1. **Goals and problem** — 6 learning objectives, and a problem statement with six fields:
   input, output, objective, constraints, assumptions, stop condition.
2. **Four films** — popular science (科普), concise (精讲), advanced (进阶), lab walkthrough (实验演示).
3. **Lesson** — from a hand-checkable example to pseudocode: 6–8 sections, term cards before first use,
   tables of real computed values, callouts, line-by-line pseudocode.
4. **Slides** — 11–14 numbered 16:9 slides; the transcript sits below the slide; PDF + PPTX + web viewer.
5. **Lab** — the real algorithm engine running in the browser, step by step, with pseudocode highlighting.
6. **Challenges** — 6–7 per module, `[category] title`, difficulty Intro → Practice → Stretch, two hints each,
   "why this challenge exists", answers checked against the engine.
7. **Code lab** — Python in the browser (Pyodide): starter with TODOs, checker, reference, fixtures, and a
   visualiser that runs the learner's own functions.
8. **Common mistakes** — 4–5 entries: wrong idea / why it is wrong / counterexample with real numbers / fix.
9. **Sources and credits** — original authors, pinned commits, references, licence notes.

The home page has an **introduction film** for the shared background of the whole course, a module grid,
and a comparison table that names every method (never bare codes like "M02–M09").

## 2. The non-negotiables

These came from real feedback during production. Breaking any of them caused rework.

1. **Engine first, pictures second.** Every number in a film, caption, slide, challenge or mistake comes from
   the course's own algorithm engine (or an independent reference implementation that is cross-checked
   against it). Film scripts `assert` the facts their captions state. No decorative fake activity.
2. **Each chapter's popular film opens with a hook about *its own* algorithm**, drawn from everyday life
   (raindrops merging for greedy merge, a two-seat chairlift for capacity, a chess sacrifice for
   Kernighan–Lin…). The general "what is this field" story is told **once**, in the home intro film.
3. **Depth over breadth, one chapter at a time.** Build a pilot chapter to full quality, get sign-off, then
   go chapter by chapter. Never make all chapters shallow at once because the whole is big.
4. **Elegant, restrained design.** Warm paper reading areas, light serif display type, monospace eyebrows,
   hairline rules, generous space, one deep-teal accent; dark "cinema bands" for films and labs.
   Heavy bold sans headings and boxy pill UIs were rejected.
5. **Dark technical films** in the style of the author's Label Propagation film: near-black blue-green
   background, ivory text, gold and teal accents, outlined nodes, thin glowing wires, captions on a soft shade.
   Bright cream backgrounds, cartoon people, photorealistic images and repeated pans of one diagram were rejected.
6. **Bilingual from the start.** Chinese and English share one film timeline; every caption is long enough
   for both (Chinese 4.5 characters/s, English 15 characters/s, plus 0.8 s). Zero reading-time violations.
7. **Learners can practise in the browser.** No install. Code labs run Python in a worker; labs run the JS engine.
8. **Static site, relative paths, no CDN.** It must work under a GitHub Pages project subpath and on a phone
   (375 px, no horizontal scroll), with keyboard operation and reduced motion.
9. **Honest provenance.** Distinguish verified facts, author claims, design decisions and reconstructions.
   Credit original authors with pinned commits. Third-party music never enters the repo and is excluded
   from the course licence.
10. **Report faithfully.** Say what was checked and how; mark skipped checks as skipped, never as passed.

## 3. Workflow (phases)

Follow `reference/05-workflow.md` for detail and `prompts/` for paste-ready prompts per step.

| Phase | Output | Prompt |
| --- | --- | --- |
| 0. Kick-off | scope, sources, module list, four working documents | `prompts/00-kickoff.md` |
| 1. Audit sources | per-module audit: what to keep, what is wrong, fixtures | `prompts/01-audit-sources.md` |
| 2. Outline | `module.md` outline per module (before any page or film) | `prompts/02-module-outline.md` |
| 3. Engine + traces | JS engine, Python reference, cross-check, regression tests | `prompts/03-engine-and-traces.md` |
| 4. Course shell | design system, i18n, shared components, home page | `prompts/04-site-shell.md` |
| 5. Module page | `module.json`, `lesson.md`, mistakes, sources | `prompts/05-module-page.md` |
| 6. Challenges | 6–7 engine-checked challenges | `prompts/06-challenges.md` |
| 7. Code lab | starter / reference / check / fixtures + visualiser | `prompts/07-code-lab.md` |
| 8. Films | popular, concise, advanced, lab walkthrough; home intro | `prompts/08`–`12` |
| 9. Slides | `slides.json` → PDF, PPTX (notes), web viewer | `prompts/13-slides.md` |
| 10. English | `*.en.json`, `*.en.md`, English films and slides | `prompts/14-translation.md` |
| 11. QA + release | tests, browser checks, report, deploy | `prompts/15-qa-and-release.md` |

**Pilot rule:** do phases 2–10 for one module first (pick the one with the strongest existing material),
show it to the author with stills and a short review cut, then repeat per module. Keep a checklist of
modules visible and finish each before starting the next.

## 4. Volume and depth targets

Use `reference/02-volume-and-depth.md` as the yardstick. In short, per module:

| Item | Target (measured on this course) |
| --- | --- |
| Lesson (zh) | 6,000–9,000 Chinese characters; English 1,200–1,700 words |
| Lesson sections | 6–8, each with a stable anchor id `mNN-topic` |
| Objectives | 6, each linked to lesson sections, challenges, slides, code lab |
| Term cards | 5–9 per module, defined before first use |
| Mistakes | 4–5 with real counterexamples |
| Challenges | 6–7, ≥ 3 categories, 2 hints each |
| Slides | 11–14, every slide has a transcript |
| Popular film | ≈ 3:10 (one music track), 15–17 scenes, ≈ 30 captions |
| Concise film | 1:50–2:35, 7–11 scenes |
| Advanced film | 2:10–2:50 (up to ~5 min when the topic needs it), 7–14 scenes |
| Lab walkthrough | 2:20–3:00, recorded from the real page |
| Code lab | 2 functions to write, 5–8 named checks |

Lengths follow the learning goal, not a quota. If a film has nothing more to say, cut it shorter.

## 5. Where to look next

- `reference/01-course-anatomy.md` — every page section, file and data format.
- `reference/02-volume-and-depth.md` — measured content volume and the depth bar per artefact.
- `reference/03-film-style.md` — the four film types, the home intro, hooks, music, captions, art direction.
- `reference/04-site-design.md` — design tokens, typography, layout, i18n, labs, code lab, progress.
- `reference/05-workflow.md` — phases, checkpoints, working documents, how to work with the author.
- `reference/06-quality-and-tests.md` — correctness rules, tests, acceptance checks, release.
- `reference/07-lessons-learned.md` — what was rejected and why; mistakes not to repeat.
- `prompts/` — paste-ready prompts, one per step. Each names its inputs, outputs and done-criteria.
- `templates/` — skeletons for the outline, film beat sheet, challenge, working documents, report.
- `checklists/` — module acceptance, film review, release.
- `adapters/` — how to load this playbook in Claude Code, Codex, Cursor, DeepSeek and others.

The reference implementation is this repository. When a prompt says "see `scripts/film/cine.py`", read
that file: it is the working version of the rule.
