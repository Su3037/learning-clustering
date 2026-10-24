| Module | What it does on G01 | Result | What this step shows |
| --- | --- | --- | --- |
| [M02](modules/m02-affinity-metrics/index.html) | Scores 10 pairs by shared neighbours | Highest A–B, D–E = 6; B–D scores 2 with no direct edge | A score is a ranking, not a grouping |
| [M03](modules/m03-greedy-pair-merge/index.html) | K=2, merging up from single nodes | ABC \| DE, cut 18→13→8→3 | Each merge lowers the cut by exactly that merge’s affinity |
| [M04](modules/m04-size-constrained-agglomerative/index.html) | K=2, capacity 2 | AB \| C \| DE, cut 8, K not reached | The lower bound ⌈5/2⌉ = 3 already proves K=2 impossible |
| [M05](modules/m05-label-propagation/index.html) | A→E asynchronous, ties to the smaller label | B/B/B/E/E, 2 rounds, cut 3 | Change the order or go synchronous, and the rounds and even stopping change |
| [M06](modules/m06-spectral-bisection/index.html) | Fiedler order E,D,C,B,A, then sweep | k=2: DE \| ABC, cut 3 | The middle cut (k=3) is 5 |
| [M07](modules/m07-kernighan-lin/index.html) | Pair swaps from AE \| BCD | Trial gains 9, −8; keep 1 step; cut 12→3 | Trials may get worse; acceptance looks at the best prefix |
| [M08](modules/m08-fiduccia-mattheyses/index.html) | Single moves from AE \| BCD, side sizes differ by ≤1 | D(+3), A(+6), keep 2 steps, cut 3 | A has the largest gain but is illegal, so D moves first |
| [M09](modules/m09-rajaraman-wong/index.html) | Not G01: a 12-node directed circuit | 8 clusters, 20 instances, longest delay 8 | The goal becomes delay, and replication is allowed |

Several methods reach cut 3 on this small graph; that is a property of this graph only. M07/M08 reaching 3 does not mean they generally find the global optimum, and M09’s “optimal” holds only under the paper’s delay model with replication allowed.
