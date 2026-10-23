# Module 07 Kernighan–Lin Refinement · Python exercise pack

Implement the largest-gain pair and the best prefix. From the Learning Clustering course (Module 07). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `five_node.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Tasks** (`starter.py`):

1. `best_swap(adj, side, locked)`: among the unlocked left/right pairs, find the one with the largest gain (the gain may be negative).
2. `best_prefix(gains)`: return (k, cumulative gain); k = 0 is valid.

**Hint 1**: first compute each node’s D = external − internal, then D(a) + D(b) − 2w(a,b) for each pair.

**Hint 2**: a prefix must be consecutive from step 1; update k only when the cumulative gain becomes strictly larger. The checker tests 120 random graphs: the side sizes never change, each node swaps at most once per pass, and gain = cut before − cut after.

## Output of the reference (actually run for this pack)

```
pass 1: A↔D g=9 cut→3, E↔C g=-8 cut→11; best prefix 1, accepted cut 3
pass 2: E↔C g=-8 cut→11, D↔B g=2 cut→9; best prefix 0, accepted cut 3
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: FanqinZeng (Clustering Module - Lesson 7). This pack was written for the unified course; code under MIT.
