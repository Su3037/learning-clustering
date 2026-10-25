| Method (module) | What it does on G01 | Result | What this step shows |
| --- | --- | --- | --- |
| [Affinity metrics](modules/m02-affinity-metrics/index.html) · M02 | Scores 10 pairs by shared neighbours | Highest A–B, D–E = 6; B–D scores 2 with no direct edge | A score is a ranking, not a grouping |
| [Greedy pair merge](modules/m03-greedy-pair-merge/index.html) · M03 | K=2, merging up from single nodes | ABC \| DE, cut 18→13→8→3 | Each merge lowers the cut by exactly that merge’s affinity |
| [Size-constrained agglomerative](modules/m04-size-constrained-agglomerative/index.html) · M04 | K=2, capacity 2 | AB \| C \| DE, cut 8, K not reached | The lower bound ⌈5/2⌉ = 3 already proves K=2 impossible |
| [Label propagation](modules/m05-label-propagation/index.html) · M05 | A→E asynchronous, ties to the smaller label | B/B/B/E/E, 2 rounds, cut 3 | Change the order or go synchronous, and the rounds and even stopping change |
| [Spectral bisection](modules/m06-spectral-bisection/index.html) · M06 | Fiedler order E,D,C,B,A, then sweep | k=2: DE \| ABC, cut 3 | The middle cut (k=3) is 5 |
| [Kernighan–Lin refinement](modules/m07-kernighan-lin/index.html) · M07 | Pair swaps from AE \| BCD | Trial gains 9, −8; keep 1 step; cut 12→3 | Trials may get worse; acceptance looks at the best prefix |
| [Fiduccia–Mattheyses refinement](modules/m08-fiduccia-mattheyses/index.html) · M08 | Single moves from AE \| BCD, side sizes differ by ≤1 | D(+3), A(+6), keep 2 steps, cut 3 | A has the largest gain but is illegal, so D moves first |
| [Rajaraman–Wong delay-oriented clustering](modules/m09-rajaraman-wong/index.html) · M09 | Not G01: a 12-node directed circuit | 8 clusters, 20 instances, longest delay 8 | The goal becomes delay, and replication is allowed |

Several methods reach cut 3 on this small graph; that is a property of this graph only. KL (M07) and FM (M08) reaching 3 does not mean they generally find the global optimum, and RW’s (M09) “optimal” holds only under the paper’s delay model with replication allowed.
