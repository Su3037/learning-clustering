# Module 03 Greedy Pair Merge · Python exercise pack

Fix the comparator, then write the main loop. From the Learning Clustering course (Module 03). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

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

1. `selection_key(c)`: return a candidate’s selection key so that `min(...)` picks the pair to merge.
2. `greedy_pair_merge(nodes, edges, k, capacity)`: write the main loop and the stop reason.

**Hint 1**: Python tuples compare field by field, and numbers compare as numbers: exactly what the original page’s JS lacked.

**Hint 2**: at each step, list every candidate with positive affinity first, then drop the ones over capacity; with no legal candidate, stop, and tell `capacity-blocked` from `no-positive-affinity`. The checker also tests multi-digit weights, 10 > 9 > 2.

## Output of the reference (actually run for this pack)

```
K=2 cap=None: ABC|DE cut=3 path=[18, 13, 8, 3] K reached=True stop=target-reached
K=3 cap=None: ABC|D|E cut=8 path=[18, 13, 8] K reached=True stop=target-reached
K=2 cap=2: AB|C|DE cut=8 path=[18, 13, 8] K reached=False stop=capacity-blocked
K=2 cap=3: ABC|DE cut=3 path=[18, 13, 8, 3] K reached=True stop=target-reached
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: thy031 (Clustering Module - Lesson 3). This pack was written for the unified course; code under MIT.
