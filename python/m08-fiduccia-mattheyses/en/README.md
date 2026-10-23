# Module 08 Fiduccia–Mattheyses Refinement · Python exercise pack

Implement gain and the legal candidates. From the Learning Clustering course (Module 08). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| `starter.py` | Starter code with TODOs (`NotImplementedError`) |
| `check.py` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| `reference.py` | Reference solution, for when you are stuck |
| `fixtures/` | `five_node.json`, `legacy_hillclimb.json`, `neg_escape.json` |

## Running

```
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
```

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set `COURSE_LANG=en` to drop the `--lang en`.

**Tasks** (`starter.py`):

1. `gain(nets, side, v)`: return (gain, FS list, TE list), counting each net’s pins per side; this works for multi-pin nets too.
2. `legal_moves(side, locked, max_diff)`: the unlocked nodes that are still balanced after moving.

**Hint 1**: for each net that contains v, count its pins on v’s side (F) and on the other side (T): only v on F → +w; none on T → −w.

**Hint 2**: use `balance_ok({**side, v: 1 - side[v]}, max_diff)` to decide whether a move is legal. The checker audits the attachment’s hillclimb data, and checks gain = cut before − cut after on 150 random graphs (multi-pin nets included).

## Output of the reference (actually run for this pack)

```
pass 1: D(+3)→9, A(+6)→3, C(-2)→5, E(-6)→11, B(-1)→12; k*=2, accepted cut 3
pass 2: C(-2)→5, E(-6)→11, B(-1)→12, D(+3)→9, A(+6)→3; k*=0, accepted cut 3
```

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: stephQ-lab (Clustering Module - Lesson 8). This pack was written for the unified course; code under MIT.
