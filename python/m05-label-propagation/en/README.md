# Module 05 Label Propagation · Python exercise pack

Implement vote counting and the stopping test. From the Learning Clustering course (Module 05). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `circuit.json`, `contacts.json`, `five_node.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Task** (`starter.py`):

1. `count_votes(adj, labels, vertex)`: add up neighbour edge weights by label.
2. The stopping test in the main loop: stable / cycle (limit is handled by the loop bound).

**Hint 1**: for neighbours with the same label, add their edge weights; C’s votes should be B = 5, D = 2, E = 1.

**Hint 2**: a full round with zero changes → stable; if the complete label state at the end of the round has appeared before → cycle. The checker also runs the author’s original 24-cell circuit and 28-person contact graph.

## Output of the reference (actually run for this pack)

```
{'A': 'B', 'B': 'B', 'C': 'B', 'D': 'E', 'E': 'E'} 2 stable cut 3
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: Su3037 (Clustering Module - Lesson 5). This pack was written for the unified course; code under MIT.
