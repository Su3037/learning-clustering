## {#m05-why} Why connections form groups

Picture an address book: a few hundred names to sort into circles. You don't need to know who anyone is. You only need to see who keeps in touch with whom: ties are dense inside a circle and sparse between circles. Network science calls this **community detection**.

In 2007, Raghavan, Albert and Kumara proposed a minimal method: **everyone looks at which circle their friends belong to right now and joins the one they are most connected to; repeat, and the circles emerge on their own.** On the fictional address book from Su3037's original film (28 people, 61 ties) it stops after 3 rounds with three circles of 8 + 10 + 10, cutting a total weight of only 4.

A chip has the same problem: wires inside a block are short, wires between blocks have to be long. Carry the local rule "look at your neighbours, follow the strongest" over to the chip and you have **label propagation**.

```callout analogy The analogy only explains structure
The address book only builds intuition: nodes, edges and weights have the same structure. It says nothing about which circle real people "should" belong to and infers no causes. Edge weights between chip cells in this course are invented teaching values.
```

## {#m05-label} Names, labels and membership

```terms
node name | 节点名 | The node's identity; it never changes. The nodes of G01 are always A, B, C, D, E.
label | 标签 | The group marker a node currently carries; it gets updated. At the start every node's label is its own name.
grouping | 分组 | Nodes with the same label form a group. Compare two results by their groups, not by what the labels are called.
```

> A name is identity; a label is membership. "C's label becomes B" does not mean "C is renamed B".

Unlike the previous three modules, there is **no merging at all** here, and **no K is given**: how many groups there are at the end is up to the labels.

## {#m05-vote} One update: a weighted vote by label

When node v takes its turn, group its neighbours by their **current label**, add up the edge weights within each label, and take the label with the largest total:

> **new label(v) = argmax_L Σ w(u, v)**, summed over the neighbours u of v whose label is L.

**C by hand (round 1)**: updating asynchronously in the order A→E, by the time C is visited A has already switched to label B, and B is still B. C's neighbours and votes:

| Label | From | Votes |
| --- | --- | --- |
| B | A (1) + B (4) | **5** |
| D | D (2) | 2 |
| E | E (1) | 1 |

C's new label is B, and its name is still C. What counts is **weight**: if two neighbours B and C carry label B with edge weight 1 each, and one neighbour D carries label D with weight 4, then B = 2 and D = 4, and D wins. More neighbours do not necessarily win.

Ties need a fixed rule. This course implements three: `min` takes the alphabetically smallest candidate (the default), `max` takes the largest, and `keep` keeps the current label if it is among the tied ones. An isolated node with no neighbours keeps its own label.

## {#m05-round} A full round, visiting order, and when to stop

**Round 1** (asynchronous: each update is written back at once, so later nodes see it immediately):

| Visit | Votes seen | New label | Changed |
| --- | --- | --- | --- |
| A | B 5, C 1 | B | yes |
| B | B 5, C 4 | B | no |
| C | B 1+4=5, D 2, E 1 | B | yes |
| D | B 2, E 5 | E | yes |
| E | B 1, E 5 | E | no |

End of round 1: B B B E E, with 3 nodes changed.

**Round 2**: check all 5 nodes again; none changes, and only now is the result confirmed stable. So the number of rounds is **2**, and the cut is C–D 2 + C–E 1 = **3**.

```callout warn Why one more round
In round 1, B and E did not change, but nodes after them were still changing; as long as any node changes, the earlier nodes may see different neighbours next time. Only a full round with **zero changes** confirms that no node still wants to change. The round count includes this confirmation round.
```

**A different visiting order**: updating in the order E→A ends with A/A/A/D/D. The label names differ, the grouping is still ABC | DE, but it takes **3 rounds**. Visiting order affects the number of rounds, and on other graphs it can affect the grouping too.

## {#m05-sync} Synchronous updates, cycles, ties and edge weights

```terms
asynchronous update | 异步更新 | Each node's result is written back as soon as it is computed; the course default.
synchronous update | 同步更新 | Every node in a round reads the same "old snapshot"; all results are committed together at the end of the round.
cycle | 振荡 | The label state returns to one seen before and repeats from then on.
```

**Two nodes, synchronous**: one edge between A and B. Synchronously, A reads B's old label B and B reads A's old label A, and both are committed at the end of the round, so they swap; next round they swap back. The state repeats, and the run reports **cycle**. Asynchronously on the same graph: A switches to B first, B then already sees B, and one round settles it.

G01 does this too: under synchronous updates it is B/A/B/E/D after round 1 and back to A/B/A/D/E after round 2… round 3 brings back the state of round 1. The period is 2 and the cut stays at 17.

The three stopping states must be kept apart:

| State | Test | Can it be called "converged"? |
| --- | --- | --- |
| stable | a full round with zero changes | yes |
| cycle | the label state repeats | no |
| limit | the maximum number of rounds is reached | no |

**What edge weights do**: change the weight of C–D from 2 to 10 and run again (starting over from the initial labels). D pulls C across, the result becomes AB | CDE, and the cut becomes A–C 1 + B–C 4 = **5**.

## {#m05-pseudocode} Reading the pseudocode line by line

```pseudo lp
labels[v] ← v  for every node                        || Start: every node's label is its own name.
repeat for round = 1, 2, …, maxRounds:              || Outer loop, one round after another; the cap guarantees the program ends (limit).
    snapshot ← labels (synchronous mode only)        || In synchronous mode the whole round reads this old snapshot; asynchronous mode reads the latest labels.
    for v in order:                                  || The visiting order is part of the input and affects the result and the round count.
        votes ← sum edge weights by neighbour label   || What counts is the sum of weights, not the number of neighbours. An isolated node gets no votes and keeps its label.
        new ← label with most votes (ties: min/max/keep) || The tie rule must be fixed, or results cannot be reproduced.
        async: write back now; sync: note it down     || This line decides what later nodes get to see.
    sync: commit everything at the end of the round   || This is where the two-node synchronous cycle happens.
    if no change this round: stable, stop             || The round count includes this confirmation round.
    if this state was seen before: cycle, stop        || Repeats are detected with a "signature" of the full label state.
```

**How it maps to Python**: line 5 → `count_votes()`; line 6 → `choose()`; lines 9–10 → the stopping test in the exercise.

## {#m05-cut} Is the grouping good? Cut and limits

Once label propagation stops, judge it by the cut: ABC | DE on G01 cuts only C–D and C–E, a cut of 3.

The 24-cell fictional circuit from the author's original film makes it clearer: total edge weight is 202; cutting it into three columns by position with a "ruler" cuts **88**; after 5 rounds of label propagation only **2** is cut. Trying every split of 24 cells is not realistic either: there are 1,577,585,295 ways to split them into three equal groups.

The limits need saying too:

- No K is given and balance is not guaranteed: it may put almost every node into one group.
- The result depends on the visiting order, the update mode and the tie rule.
- Synchronous updates can cycle; this course does not claim that asynchronous updates stop on every graph.
- In EDA it works well as a fast first grouping, handed on to constrained partitioning or improvement methods (Modules 06–08).
