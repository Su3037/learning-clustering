# Film beat sheet · {{Module NN}} · {{story | concise | advanced}}

Film title (zh / en): {{…}} / {{…}}
Music: {{track:wenever | score:calm | score:curious | score:steady}}
Why watch this (zh / en, one paragraph each, goes into `film.json → why`): {{…}}

Reading time per beat ≥ max(zh chars / 4.5, en chars / 15) + 0.8 s.

| # | Scene id | Pin to music (s) | Chapter | Caption zh | Caption en | On screen (what moves) | Data (trace path / assert) | Hold (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | p-hook | 0–10.75 | 序 · {{…}} | {{…}} | {{…}} | {{lands on the intro hits}} | — illustration | 4.6 |
| 2 | p-hook2 | 10.75–17.41 | | {{punchline}} | {{…}} | {{plays in silence}} | | 4.8 |
| 3 | p-rule | 17.41– | | {{the turn}} | {{…}} | {{the course example appears}} | `traces.run.events[0]` | 4.4 |
| 4 | p-title | 32.03–37.0 | | — | — | title assembles on the roll, locks 34.17 | | 4.5 |
| … | | | | | | | | |
| n | p-end | 170.6–189.82 | 尾声 | {{invitation to the lab}} | {{…}} | credits incl. music | | |

## Asserts (top of the film script)

```python
assert SEED == {...} and P1["startCut"] == ...
assert [(s["a"], s["b"], s["gain"]) for s in P1["swaps"]] == [...]
```

## Review notes

- Contact sheet zh: {{date, issues found}}
- Contact sheet en: {{…}}
- Sample cut shown to author: {{date, reaction}}
- Reading violations: {{0}}
