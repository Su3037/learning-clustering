# Module 09 Rajaraman–Wong Delay-Oriented Clustering · Python exercise pack

In layers: evaluate delay first, then labelling and recovery. From the Learning Clustering course (Module 09). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `candidate_dag.json`, `chain.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Base tasks** (these three can be done on their own first):

1. `topological_order(nodes, edges)`: raise an error on a cycle.
2. `longest_node_delays(...)`: Δ[x][v].
3. `evaluate_instance_delay(...)`: instance arrival times; the chain’s 7 and 10.

**Advanced tasks**:

4. `rw_label(dag)`: label in topological order.
5. `rw_reconstruct(dag, cluster)`: work back from the POs to clusters and instances.

**Hint 1**: Δ counts v’s delay on the path but not the start x; with no path, it is None.

**Hint 2**: write instance ids as “node@root”; an input u from outside the cluster comes from “u@u”, at cost D. The checker confirms 8 clusters, 20 instances and output 8 on the candidate graph, and checks that every instance has complete inputs.

## Output of the reference (actually run for this pack)

```
labels {'a': 1, 'b': 1, 'c': 1, 'd': 2, 'e': 2, 'f': 2, 'g': 3, 'h': 2, 'i': 7, 'j': 7, 'k': 8, 'l': 8}
clusters 8 instances 20 output delay {'k': 8, 'l': 8}
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: muranfei (Clustering Module - Lesson 9). This pack was written for the unified course; code under MIT.
