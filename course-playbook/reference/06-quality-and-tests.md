# 06 · Correctness, tests and acceptance

## 1. Correctness rules

1. **One engine, four consumers.** The same engine module drives the lab, the challenge validators, the film
   traces and the Node tests. A film never animates a hard-coded result while a different algorithm runs.
2. **Independent reference.** A second implementation (Python) written from the algorithm description, not
   translated line by line. A cross-check compares the two step by step on the course examples and on random
   inputs (this course: 1,324 comparisons).
3. **Property tests on random inputs** (e.g. 300 random graphs): invariants of the algorithm (gain equals the
   cut difference; each node moves at most once per pass; side sizes stay fixed; the first step equals an
   exhaustive search's best).
4. **Exhaustive oracles** for small cases to prove or refute claims ("the unconstrained optimum is always a
   singleton" was refuted this way; "the 5-node graph has 15 non-empty bipartitions" was confirmed).
5. **Explicit tie rules and stop reasons**, as data: stable, repeated-state cycle, iteration limit, empty
   prefix, infeasible target, greedy stuck, feasible-but-suboptimal. Different outcomes are never merged into one.
6. **Fix documented errors in the source material** and keep a regression test for each. Examples found in
   this course: comparing arrays as strings in JavaScript; a "hill climb" presented as FM; a gain formula
   missing −2w; stored three-decimal eigenvectors presented as live solving; a claimed "9 → 4" improvement
   that the real algorithm does not produce.
7. **Assert in film scripts.** Every number a caption states is read from the trace and asserted at the top
   of `films.py`.
8. **Fair comparisons.** Methods are compared from the same seed on the same graph, and the text says the
   result is local to that example.
9. **Model honesty.** Say what the method does not guarantee (global optimum, balance, a fixed number of
   groups); distinguish node counts from areas; logical grouping from physical placement.

## 2. Automated tests (reference: `tests/`)

| Test | Checks |
| --- | --- |
| `engines.test.mjs` | regression values on course graphs, properties on random graphs, repaired errors |
| `challenges.test.mjs` | every challenge's correct answer passes, typical wrong answers fail with the right message |
| `site.test.mjs` | scope (exact module set), terminology ("Module", not "Lab"), every page has the required sections and the six-field problem statement, media and slides exist, crosswalk complete, every relative link and asset resolves, no CDN, no absolute root paths, CSS `url()` case-exact, font subset covers every page's characters, `.nojekyll`, every module reachable from home, challenges ordered easy → hard with `[category]` titles, analogies only where allowed, home intro film in both languages, comparison table names each method, films have 0 reading violations |
| `crosscheck.py` | JS engine ↔ Python reference, step by step |
| `python/<id>/check.py reference.py` | each reference passes its checker; the starter reports INCOMPLETE, never FAIL or PASS |

CI runs all of these before deploy. A red test blocks the release.

## 3. Manual checks (and how to report them)

| Check | How |
| --- | --- |
| Pages | local server under the project subpath; every page in both languages; no console errors |
| Phone | 375 px viewport: no horizontal scroll, lab and code lab usable |
| Lab | step forward/back with arrows; pseudocode highlight follows events; export works |
| Storage failure | make localStorage throw: page renders, labs and challenges work, notice shown |
| Progress import | non-JSON and wrong version are rejected with a reason |
| Deep links | `#lab`, `#slides`, `#slide-<id>` after refresh |
| Films | contact sheets per scene; sampled frames at entry / middle / exit; full decode; seeking |
| Slides | PPTX page count = PDF page count = slides.json; every slide has notes; PDF embeds only the intended fonts |
| Live site | after deploy: fonts load (200), films play and seek, code lab loads Pyodide |

Report exactly what was done: "checked on a 375 px viewport in Chromium" is not "tested on phones";
"contact sheets and 10 frames" is not "watched every film". List unverified items under limitations.

## 4. Completion report

Every delivery ends with a report (`templates/completion-report.md`): what was delivered (counts and paths),
commands and results, errors fixed in the sources, browser checks, the media table (title, length, scenes,
captions, size), limitations and unchecked items, and what still needs the author.

## 5. Licences and credits

- New code: MIT. New text, figures, films, slides, captions and original music: CC BY 4.0 (author's choice).
- Fonts: SIL OFL 1.1, licence files shipped with the site.
- Student originals: not copied unless their licence allows; credited with name, site, repository and pinned
  commit, plus what was kept and what was changed.
- Third-party music: only inside the finished films that use it; never committed; excluded from the course
  licence on every page; credited by title and artist.
- Runtimes (Pyodide MPL-2.0, CodeMirror MIT): listed in `THIRD_PARTY_NOTICES.md`.
