# Module 02 Affinity Metrics · Python exercise pack

Implement the three scores. From the Learning Clustering course (Module 02). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `five_node.json`, `priority_graph.json`, `tiny_netlist.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Task** (three `TODO`s in `starter.py`):

1. `affinity_edge_weight(edges)`: direct weight.
2. `affinity_shared_neighbors(nodes, edges)`: check every unordered pair and list only positive scores.
3. `affinity_pin_count(nodes, nets)`: the clique model; a repeated pin counts once.

All three return `[(u, v, score), ...]` with u < v, sorted by (score descending, u, v).

**Hint 1**: write the double loop over “every unordered pair” first, then decide what each pair adds.

**Hint 2**: a shared neighbour is an x that appears in both u’s and v’s adjacency; it contributes `min(w(u,x), w(v,x))`. The checker also tries a new graph, so memorising the five-node answers will not pass.

## Output of the reference (actually run for this pack)

```
edge   : [('A', 'B', 5), ('D', 'E', 5), ('B', 'C', 4), ('C', 'D', 2), ('A', 'C', 1), ('C', 'E', 1)]
shared : [('A', 'B', 6), ('D', 'E', 6), ('A', 'C', 5), ('B', 'C', 5), ('C', 'D', 3), ('C', 'E', 3), ('B', 'D', 2), ('A', 'D', 1), ('A', 'E', 1), ('B', 'E', 1)]
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: Capeur (Clustering Module - Lesson 2). This pack was written for the unified course; code under MIT.
