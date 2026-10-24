# Module 06 Spectral Bisection · Python exercise pack

Build L, sweep the cuts, self-check the numerics. From the Learning Clustering course (Module 06). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `disconnected.json`, `five_node.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Tasks** (`starter.py`):

1. `laplacian(nodes, edges)`: build L = D − A.
2. `sweep(order, edges, lo, hi)`: cut at every position along the order and mark whether it is legal.
3. `count_bipartitions(n)`: the number of bisections with both groups non-empty and sides not distinguished.

A pure-Python Jacobi solver is provided; with NumPy installed, the checker also compares against `numpy.linalg.eigvalsh` (without NumPy it reports SKIP, which does not count as a pass).

**Hint 1**: each edge contributes to four entries of L: +w on the two diagonals, −w on the two off-diagonals.

**Hint 2**: which two of the 2ⁿ left/right labellings go, and what do you divide by?

## Output of the reference (actually run for this pack)

```
λ = [-0.0, 1.7733143437, 8.4551152172, 11.6052655098, 14.1663049292]
order ['E', 'D', 'C', 'B', 'A'] sweep [6, 3, 5, 6] chosen (['E', 'D'], ['C', 'B', 'A']) cut 3
residual 3.8543291529169345e-15 non-empty bipartitions 15
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: xingguangyaoyu (Clustering Module - Lesson 6). This pack was written for the unified course; code under MIT.
