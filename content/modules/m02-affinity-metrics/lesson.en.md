## {#m02-why} Why score a pair of cells first

The first question of clustering is not "how do we split?" but "which cells belong together more?". Give every pair of cells a score, and the merging algorithm that follows (Module 03) has something to go on: merge the highest-scoring pair first.

```terms
affinity | 亲和度 | A score, under **one stated model**, of how much a pair of nodes (or a pair of clusters) "should be together". The higher the score, the more they belong together.
scoring and ranking | 评分与排名 | This module's output: every pair of nodes, listed from the highest score to the lowest. It is **not** a grouping.
net | 信号网 | All the pins one signal connects. An ordinary edge has two ends; a net can have three, five or many more.
```

The same cells can be described by different models of connection:

- **Graph**: each edge connects two cells, and its weight says how strong the connection is. The course's shared graph G01 is one.
- **Netlist**: each net is a set of pins. One clock or reset net can reach thousands of cells.

```callout warn A score is not a grouping
A–B ranking first does not mean A and B "are already in one cluster". This module only answers "if we merge, whom do we merge first". The actual merging, the stopping rule and the number of clusters start in Module 03. Nor does every clustering algorithm rely on "the top pair": label propagation, spectral bisection and KL/FM use entirely different mechanisms.
```

## {#m02-edge} Score one: direct weight

The most direct idea: the weight of the edge between two cells is their score.

> **edge(u, v) = w(u, v)**; a pair with no direct edge has no score.

On G01, the 6 edges are 6 pairs:

| Rank | Pair | Score |
| --- | --- | --- |
| 1 | A–B | 5 |
| 2 | D–E | 5 |
| 3 | B–C | 4 |
| 4 | C–D | 2 |
| 5 | A–C | 1 |
| 6 | C–E | 1 |

A–B and D–E are both 5, so which comes first? Sort by score alone and the order of a tie depends on the input order: feed the edges in reverse and the result changes. So this course fixes a **stable ranking** rule:

> Score descending first; for equal scores, by u alphabetically, then by v (every pair is written with u < v).

So A–B comes before D–E, and A–C before C–E, whatever order the edges arrive in.

## {#m02-shared} Score two: shared neighbours

Direct weight only asks "is there a wire between us?". But if u and v are both tightly connected to the same cell x, putting them together is usually better too, because x can only be in one group.

```terms
shared neighbour | 共同邻居 | A node x directly connected to both u and v.
```

> **shared(u, v) = w(u, v) + Σ₍ₓ₎ min(w(u, x), w(v, x))**, with x running over the shared neighbours of u and v.

Why **min**? An "indirect link" through x can only be as strong as the weaker of its two edges: A and C are both connected to B, but B–C is only 4, so the path through B contributes at most 4.

**A–C by hand**: direct edge 1; the only shared neighbour is B, min(w(A,B), w(C,B)) = min(5, 4) = 4. Total **5**.

**B–D by hand**: there is **no direct edge between B and D**, so the direct part is 0; the shared neighbour C contributes min(w(B,C), w(D,C)) = min(4, 2) = 2. Total **2**.

```callout mistake The most common omission
Compute shared-neighbour scores only on "the edges that exist" and you miss B–D, A–D, A–E and B–E, pairs with no direct wire. The shared-neighbour score must check **every** unordered pair: G01 has 5×4/2 = 10 pairs, and all 10 score above zero. No wire has been invented: the graph's edges have not changed, only the score we give the pair.
```

The full ranking (shared neighbours):

| Pair | Direct | Through shared neighbours | Score |
| --- | --- | --- | --- |
| A–B | 5 | via C: min(1, 4) = 1 | 6 |
| D–E | 5 | via C: min(2, 1) = 1 | 6 |
| A–C | 1 | via B: min(5, 4) = 4 | 5 |
| B–C | 4 | via A: min(5, 1) = 1 | 5 |
| C–D | 2 | via E: min(1, 5) = 1 | 3 |
| C–E | 1 | via D: min(2, 5) = 2 | 3 |
| B–D | 0 | via C: min(4, 2) = 2 | 2 |
| A–D | 0 | via C: min(1, 2) = 1 | 1 |
| A–E | 0 | via C: min(1, 1) = 1 | 1 |
| B–E | 0 | via C: min(4, 1) = 1 | 1 |

## {#m02-priority} Change the score and the first pair changes

The original author, Capeur, designed a very persuasive little graph (the priority graph): a tight triangle P, Q, R with every edge 4, and a separate pair X–Y with edge weight 5.

**Predict first**: if the next step merges "the closest pair", which pair do you choose?

- By **direct weight**: X–Y = 5 is the largest, so the first pair is **X–Y@5**.
- By **shared neighbours**: P–Q = 4 + min(4, 4) (via R) = **8**; P–R and Q–R are also 8; X–Y has no shared neighbour and stays at 5. Three pairs tie at 8, and the stable ranking picks **P–Q@8**.

The two models answer different questions: direct weight looks only at the wire between these two cells; shared neighbours also ask whether they belong to the same tight "little group". The three cells of the triangle are all connected to each other, so putting P and Q together first and adding R afterwards is natural; X–Y has a thicker single wire, but nothing to do with any other cell.

```callout note This is a choice of model, not right versus wrong
Both results are "computed correctly under their own rule". What this module asks is: **say which score you use**, and be able to explain why the result changed when the score changed. You may not quietly switch models in the middle of a run.
```

## {#m02-pincount} How wide nets dilute: pin-count

Back to netlists. The original author's tiny netlist has 6 cells: two wide five-pin nets (enable, reset) both connect A–E, and a private two-pin net connects only E and F.

Count only "how many nets connect this pair" and A–B, in both enable and reset, gets 2 points, while E–F, only in n1, gets 1. Yet enable connects 10 pairs of cells at once, so it says almost nothing about "A and B belonging together in particular", while n1 is E and F's own wire.

The **clique model** treats a net with |e| pins as an "illustrative connection" between every two of its pins, and shares its weight out over |e| − 1:

> **pin-count(u, v) = Σ₍ₑ ∋ u, v₎ w(e) / (|e| − 1)**

- A–B: enable contributes 1/(5−1) = 1/4, reset another 1/4, total **0.5**.
- E–F: n1 has only two pins, contributing 1/(2−1) = **1**.

So E–F comes first, and A–B drops to 0.5. The pairwise lines drawn for a five-pin net are only **illustrative contributions**, not new wires on the chip.

Two implementation details must be spelled out (this course's conventions):

- A pin written more than once in the same net counts once (`pins: [A, A, B]` counts as 2 pins).
- A net with fewer than two distinct pins produces no pair and is ignored.

## {#m02-pseudocode} The pseudocode, line by line

Below is the pseudocode of the shared-neighbour score. Click any line for its explanation; when you step through the lab, the line being executed is highlighted automatically.

```pseudo shared
for each unordered pair (u, v) with u < v:        || Visit **every** unordered pair, including pairs with no direct wire; n nodes have n(n−1)/2 pairs.
    score ← w(u, v)   (0 if no edge)               || Start from the direct weight; with no edge, start from 0 instead of skipping the pair.
    for each x adjacent to both u and v:            || Only shared neighbours x: x must appear in both u's and v's adjacency.
        score ← score + min(w(u, x), w(v, x))       || An indirect link through x counts at its weaker edge: a chain is only as strong as its weakest link.
    if score > 0: append (u, v, score)              || This course lists positive scores only (a zero pair has no connection at all; a stated policy).
sort list by (−score, u, v)                         || Stable ranking: score descending, ties by name; independent of input order.
return list                                         || The output is a ranking, not a grouping. Module 03 does the merging.
```

Direct weight needs only lines 2 and 6; pin-count replaces lines 1–4 with "for each net, add w/(|e|−1) to every pair of its pins".

**How it maps to the Python functions**: lines 1–5 → the double loop in `affinity_shared_neighbors(nodes, edges)`; line 6 → the provided `_rank()`; pin-count → `affinity_pin_count(nodes, nets)`.

## {#m02-application} Back to the chip: what the choice of score means in practice

In EDA, the score decides "what gets glued together first". Merging heavily connected cells first can shorten the long wires that cross regions. But a score is only a model:

- **Say where edge weights come from**: the number of wires between two cells, the importance of a signal, or a conversion from multi-pin nets. The small graphs in this course are all **invented teaching values**, not measurements of a real chip.
- **Wide nets need dilution**: clock and reset nets reach almost every cell. Without sharing them out, they make every cell look "equally close" and hide the real local structure.
- **Shared neighbours** find tight little groups, but cost more to compute and can overrate cells that merely "share one big hub".

Next, Module 03 picks "the summed edge weight between clusters" as the affinity and starts merging for real.
