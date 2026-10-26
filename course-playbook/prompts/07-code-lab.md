# Prompt 07 · In-browser code lab

---

Build the Python exercise for **{{Module NN · topic}}** so it runs in the browser (Pyodide) and offline (zip).
Model: `python/m07-kernighan-lin/`, `scripts/build-codelab.mjs`, `site/assets/codelab.js`.

Files in `python/{{id}}/` (and English versions in `python/{{id}}/en/`):
- `starter.py` — helpers already written; **two functions** that carry the algorithm's core idea left as
  `raise NotImplementedError`, each with a docstring stating the rule, the return shape, the tie rule and a
  short "why" (e.g. why −2w). Standard library only.
- `reference.py` — the full solution (the same independent reference used by the cross-check).
- `fixtures/*.json` — the course example and its expected values.
- `check.py` — named checks, 5–8 of them: the course example, edge cases, invariants on ~120 random inputs,
  comparison with an independent enumeration where possible. Each reports PASS / FAIL / INCOMPLETE;
  `NotImplementedError` → INCOMPLETE, never PASS. Supports `--json` and `--lang`.
- `README.md` — task, two hints, sample output.

In the page: editor (CodeMirror), **Run checks** (Ctrl/⌘+Enter), per-check results, Stop (terminates the
worker), code saved per module and language, and a **visualiser** that runs the learner's own functions on the
example and compares each step with the course engine. Mark the module `"codelab": true` in `module.json`.

Done when: `check.py reference.py` passes everything in both languages, `check.py starter.py` reports only
INCOMPLETE, and the page runs both in a real browser.
