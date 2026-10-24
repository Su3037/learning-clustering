# Module 04 Size-Constrained Agglomerative Clustering · Python exercise pack

Complete the stop report and the diagnosis. From the Learning Clustering course (Module 04). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `five_node.json`, `greedy_trap.json`, `suboptimal.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Tasks** (`starter.py`):

1. `report(parts, k, capacity, size, stop)`: return the four items count, capacity_compliant, target_reached and stop_reason.
2. `classify(graph, k, capacity)`: combine `solve()` with the provided `oracle()` and return one of the five endings.

**Hint 1**: the four items are independent; at capacity 2, AB | C | DE is legal but does not reach K.

**Hint 2**: first check whether K is reached; if not, check whether the lower bound already exceeds K, then whether exhaustive search finds a legal partition into exactly K clusters. The checker also tests an over-capacity node and a graph with no edges.

## Output of the reference (actually run for this pack)

```
five_node.json K=2 C=2: ['AB', 'C', 'DE'] cut=8 legal=True K reached=False stop=capacity-blocked → infeasible-by-bound
five_node.json K=2 C=3: ['ABC', 'DE'] cut=3 legal=True K reached=True stop=target-reached → reached-and-optimal-here
five_node.json K=3 C=2: ['AB', 'C', 'DE'] cut=8 legal=True K reached=True stop=target-reached → reached-and-optimal-here
greedy_trap.json K=2 C=3: ['A', 'B', 'CD'] cut=8 legal=True K reached=False stop=capacity-blocked → greedy-stuck
suboptimal.json K=2 C=2: ['AB', 'CD'] cut=18 legal=True K reached=True stop=target-reached → feasible-suboptimal
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: GateUltra (Clustering Module - Lesson 4). This pack was written for the unified course; code under MIT.
