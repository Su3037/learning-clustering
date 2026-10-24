## {#m03-local} Connections and local choices

Module 02 answered “who is closest to whom”. The most natural next step: **put the closest two together first, then look at the next pair**. A method that “only makes the best choice in sight at each step” is called **greedy**, and clustering that merges upward from single nodes is called **agglomerative clustering**.

Its strength is a simple rule that you can work by hand at every step; its weakness is just as clear: a merge is never split again, and early choices shape every later one. This chapter makes the rule precise first; the next (Module 04) is devoted to where it goes wrong.

## {#m03-setup} Singletons, the target K and the affinity between clusters

```terms
cluster | 簇 | A group of nodes placed together. At the start, every node is a “singleton” cluster of its own.
contraction | 收缩 | Merging two clusters into one “supernode”: the wires between them become inside wires, and parallel wires to outside nodes add up.
target K | 目标簇数 | The number of clusters you want; stop once the count reaches K.
inter-cluster affinity | 簇间亲和度 | The total weight of every wire between two clusters. This module uses only this affinity.
```

**Why is the affinity between clusters a “total weight”?** Because when two clusters merge, every wire between them becomes an inside wire and no longer counts in the cut. So:

> Every merge lowers the cut by exactly that merge’s affinity.

This property lets you read the effect of each step directly, and it is one of the properties this course’s tests check (it holds at every step on 200 random graphs).

## {#m03-tie} Value first, then the tie rule

At each step we must pick, from all candidates, the pair that “most deserves” to merge. This course fixes the selection key:

> **(−affinity, members of cluster A, members of cluster B)**, compared field by field; take the smallest.

The first field is negated so that higher affinity comes first; the other two fields break ties by the members’ names in alphabetical order. For example, AB–C and D–E both score 5; compare the member lists [A, B] and [D]: A < D, so AB–C merges first.

```callout mistake The comparator bug on the original page (fixed in this course)
The original page’s JavaScript reads `if (!best || cand < best)`, where `cand` is an array. When JavaScript compares two arrays it first **turns them into strings**: `[-1, "A", "C"]` becomes `"-1,A,C"` and `[-5, "A", "B"]` becomes `"-5,A,B"`. The character `1` is less than `5`, so A–C, with affinity 1, is treated as the “better” pair.

The result: on the same graph, the original page merges A–C first and ends at ACDE | B, cut 9; the correct result is ABC | DE, cut 3. Across four settings (K=2, K=3, capacity 2, capacity 3) the original page gives 9/16/12/16, and the correct values are 3/8/8/3. The original Python reference implementation is correct: the problem is only in the page’s JS.

This course’s engine uses `compareKeys()`, which compares field by field, and adds regression tests for 10 versus 2 and 2.5 versus 2 so that it cannot be “right by luck” on this five-node graph alone.
```

## {#m03-walk} Step by step: AB → ABC → DE

On G01, take K = 2 with no capacity. At the start there are 5 singletons, and cut = all the weight = 18.

| Step | Clusters | Candidates (affinity) | Chosen | cut |
| --- | --- | --- | --- | --- |
| 0 | A, B, C, D, E | — | — | 18 |
| 1 | A, B, C, D, E | A–B 5, D–E 5, B–C 4, C–D 2, A–C 1, C–E 1 | **A–B** (tie, A < D) | 18 − 5 = 13 |
| 2 | AB, C, D, E | **AB–C 1+4=5**, D–E 5, C–D 2, C–E 1 | **AB–C** (tie, [A,B] < [D]) | 13 − 5 = 8 |
| 3 | ABC, D, E | D–E 5, ABC–D 2, ABC–E 1 | **D–E** | 8 − 5 = 3 |

Step 2 is the key: once A and B contract into one supernode, A–C (1) and B–C (4) are two parallel wires to C, and together AB–C = 5. The original author drew this step specially, and this course’s films and lab keep it.

The count reaches 2: stop. The result is **ABC | DE**, and the remaining cut is C–D (2) and C–E (1), 3 in all.

## {#m03-capacity} A preview of capacity, and the stopping state

Suppose each cluster can hold at most C units of size (here every node has size 1):

- **Capacity 3**: AB+C has size 3 ≤ 3, legal, and the path is the same as above, giving ABC | DE.
- **Capacity 2**: step 2’s AB+C has size 3 > 2 and is **blocked**; the next legal candidate is D–E, which merges. That leaves AB, C and DE: AB+C is 3 and so is C+DE, both over capacity, so no legal pair with positive affinity remains. Stop.

With capacity 2 the result is **AB | C | DE, 3 clusters, cut 8, K = 2 not reached**. This is not a program error but what the rule demands: with no legal merge, stop and say so honestly. In Module 04 this becomes the main topic: telling “simply impossible” apart from “greedy walked into a dead end”.

```callout note Report three states separately
**Legal (capacity compliant)**: no cluster is over capacity. The capacity-2 result is legal.
**Target reached**: the number of clusters is ≤ K. The capacity-2 result does not reach it.
**Stop reason**: `target-reached`, `capacity-blocked` (positive pairs remain but all are over capacity) or `no-positive-affinity` (the graph is disconnected and no wire joins the remaining clusters).
```

## {#m03-pseudocode} The pseudocode, line by line

```pseudo merge
clusters ← one singleton per node                    || At the start the cut equals all the weight (18 on G01).
while |clusters| > K:                               || The first stopping condition: the count reaches K.
    cands ← every cluster pair (P, Q) with affinity > 0  || Affinity = the total weight between P and Q; parallel wires after a contraction add up here.
    legal ← those in cands with size(P) + size(Q) ≤ C    || With a capacity, filter first; filtered candidates show as “blocked” in the lab.
    if legal is empty: stop (say K is not reached)     || The second stopping condition: never force a merge to reach K.
    (P, Q) ← the legal pair with the smallest key (−affinity, P, Q) || Field by field: value first, member names on a tie. Never compare as strings.
    replace P and Q with P ∪ Q                         || Contraction: inside wires leave the cut, which drops by exactly this affinity.
return clusters, cut, whether K is reached, stop reason || Report all four separately.
```

**How it maps to the Python**: the selection key on line 6 → `selection_key(c)`; lines 2–8 → the main loop of `greedy_pair_merge(...)`.

## {#m03-limits} Greedy’s limits, and what they mean in practice

- **No backtracking**: once merged, never split. On G01 greedy happens to reach the smallest cut, 3, but that is a property of this graph. Module 04 has a counterexample where greedy reaches cut 18 while the best legal grouping has only 11.
- **It depends on the score**: this module uses “the total weight between clusters”. With Module 02’s shared neighbours or another score, the merge order and the result can change.
- **Complexity**: a naive implementation checks every cluster pair at every step. Real tools usually keep a priority queue and update only the few pairs a merge affects.
- **In practice**: in chip design, this kind of bottom-up merging often coarsens a huge number of cells into fewer clusters before handing them to partitioning or placement tools; merging usually also limits a cluster’s area, which is the next module’s capacity constraint.
