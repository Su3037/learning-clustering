# Completion report · {{course / module}}

Date {{…}}. Scope: {{…}}. Published: {{yes, URL / no, local only}}.

## 1. Deliverables
| Item | Location | Count |
| --- | --- | --- |
| Engines | `site/engines/*.js` | |
| Module pages (zh + en) | `site/modules/<id>/`, `site/en/modules/<id>/` | |
| Films | `site/media/<id>/` | {{modules × 4 × 2 languages}} + home intro |
| Slides | `site/slides/<id>/` (PDF, PPTX, previews) | {{decks, pages}} |
| Challenges | `site/modules/<id>/challenges.js` | |
| Code labs | `python/<id>/`, `site/data/<id>/codelab.json` | |

## 2. Commands and results
| Command | Result |
| --- | --- |
| `./scripts/build.sh` | |
| `node --test tests/*.test.mjs` | {{n / n}} |
| `python3 tests/crosscheck.py` | {{PASS, n comparisons}} |
| `python3 python/<id>/check.py python/<id>/reference.py` | |

## 3. Errors fixed in the source material
- {{module}}: {{error}} → {{fix}}; regression test {{name}}.

## 4. Browser checks (where, which browser, which widths)
- …

## 5. Media
| Module | Film | Length | Scenes | Captions | Size | Reading violations |
| --- | --- | --- | --- | --- | --- | --- |

## 6. Limitations and checks not done
- {{e.g. no full real-time viewing of every film; contact sheets + sampled frames only}}
- {{e.g. no real-device matrix; 375 px viewport in Chromium only}}

## 7. Waiting on the author / instructor
- …
