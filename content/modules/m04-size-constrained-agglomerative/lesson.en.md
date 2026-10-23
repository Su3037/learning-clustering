## {#m04-review} The same rule, one more question: does it fit?

The merge rule is exactly Module 03’s: start from singletons, each time merge the pair with the largest total weight between them, compare selection keys field by field, never undo. Only one thing changes:

> **Filter for legality first, then take the largest.** A candidate whose merged cluster would exceed the capacity C cannot be chosen, however high its affinity.

In a real circuit a cluster often stands for a region of the chip, and that region holds only so much cell area. The constraint looks simple, yet it gives greedy merging three different endings. This chapter’s job is to tell them apart.

## {#m04-size} Size, capacity and the four report items

```terms
size s(v) | 单元大小 | The area or resources one node takes. In this chapter every node of G01 has size 1; in greedy_trap, A and B have size 2.
capacity C | 容量 | The upper limit on a cluster’s size: the sizes of all nodes in a cluster add up to at most C.
capacity compliant | 合法 | Every cluster respects the capacity.
target reached | 达到目标 | The actual number of clusters is ≤ K.
```

The four are independent and must be reported separately:

| Report item | Meaning | With capacity 2, K = 2 |
| --- | --- | --- |
| count | The actual number of clusters | 3 |
| capacityCompliant | Every cluster’s size ≤ C | yes |
| targetReached | count ≤ K | no |
| stopReason | Why it stopped | capacity-blocked |

```callout warn K never overrides the capacity
Making one over-capacity merge to reach K makes the result illegal. Better to stop with more clusters and say so honestly. When a single node already exceeds the capacity, no legal grouping exists at all; this course reports that as an input error instead of forcing merges.
```

## {#m04-fork} One graph, two capacities

On G01 with K = 2, compare capacity 3 with capacity 2:

| Step | Capacity 3 | Capacity 2 |
| --- | --- | --- |
| 1 | A–B (5), size 2, legal | A–B (5), size 2, legal |
| 2 | AB–C (1+4=5), size 3 ≤ 3, legal | AB–C has size 3 > 2, **blocked**; D–E (5) instead |
| 3 | D–E (5) | What remains, AB+C = 3 and C+DE = 3, is **all blocked** |
| Result | ABC \| DE, cut 3, K reached | AB \| C \| DE, cut 8, K not reached |

With capacity 2, the blocked candidate is not a “small” one but exactly the highest-affinity AB–C. The legality filter happens **before** affinities are compared.

## {#m04-infeasible} Impossible, or a dead end?

At capacity 2, G01 stops at 3 clusters. Is that greedy’s fault? First compute a **lower bound**:

> The total size is 5 and each cluster holds at most 2, so at least ⌈5 / 2⌉ = **3** clusters are needed.

No algorithm can split G01 into 2 clusters at capacity 2. Greedy made no mistake here: **the target itself is infeasible**.

A lower bound can only prove “impossible”, never “possible”. The **greedy_trap** graph by the original author, GateUltra, shows a different situation:

- Nodes A and B have size 2, C and D size 1; edges C–D = 10, A–C = 4, B–D = 4; capacity 3, K = 2.
- Lower bound: total size 6, ⌈6/3⌉ = 2 ≤ K, so the bound **allows** 2 clusters.
- Greedy: it first merges C–D (10), the highest affinity, giving CD of size 2; then CD+A and CD+B both have size 4 > 3, and there is no edge between A and B. **It stops at 3 clusters.**
- Exhaustive search: **AC | BD**, two clusters of size 3 each, legal, cut = C–D = 10.

So greedy_trap is “**feasible overall, but greedy is stuck**”: the first step took the biggest 10, and after that no legal pair of clusters can be assembled. Greedy never backtracks, so it has no way to find that way out.

```callout note A counter-intuitive detail
When greedy stops, its cut is 8 (A–C 4 + B–D 4), smaller than the feasible 2-cluster plan (cut 10), because it has one more cluster. A small cut does not mean the target is reached; keep the two apart.
```

## {#m04-suboptimal} Legal, but not optimal

The third ending comes from the original author’s **suboptimal** graph: edges A–B = 10, A–C = 9, B–D = 9, C–D = 1, every node of size 1, capacity 2, K = 2.

- Greedy: it first merges A–B (10); AB is then full, so only C–D (1) can merge. The result is AB | CD, **cut = 9 + 9 = 18**.
- Exhaustive search: AC | BD cuts only A–B (10) and C–D (1), **cut = 11**.

Both results are legal and both reach K, but greedy is 7 worse than the optimum. The reason is the same as in greedy_trap: the first step took the biggest 10 in sight and left both 9s in the cut.

```callout analogy Node sizes change the ending too
Set A’s size in G01 to 2, with capacity 3 and K = 2: after A–B merges its size is already 3, AB+C becomes 4 and is blocked, so greedy merges D–E instead and then puts C into DE. The result is AB | CDE, cut 5, not the original ABC | DE, cut 3. Counting nodes and counting area can give different answers.
```

## {#m04-pseudocode} The pseudocode: merge, report, diagnose

```pseudo capacity
clusters ← singletons; if some s(v) > C: report invalid input   || A single node does not fit, so no grouping is legal: never force a merge.
while |clusters| > K:                                   || The target count is a wish, not a must.
    cands ← cluster pairs with affinity > 0             || As in Module 03: the total weight between clusters.
    legal ← {(P, Q) ∈ cands : s(P) + s(Q) ≤ C}           || Filter for legality first: this line comes before affinities are compared.
    if legal is empty: stop ← capacity-blocked or no-positive-affinity   || Positive pairs all over capacity, and a disconnected graph, are two different stop reasons.
    merge the legal pair with the smallest selection key  || Selection key (−affinity, P, Q), compared field by field.
report: count, capacityCompliant, targetReached, stop  || Four separate items; none stands in for another.
diagnose: lower bound ⌈Σs / C⌉ and small-graph exhaustive search || Tells apart: impossible / greedy stuck / legal but not optimal / optimal on this graph.
```

**How it maps to the Python**: lines 1–6 → `solve()`; line 7 → `report()`; line 8 → `oracle()` and `classify()`.

## {#m04-application} Practice and limits

In chip design, the capacity constraint means “how much area fits in each region”. Capacity-constrained clustering often serves as a coarsening step: it combines a large number of cells into clusters of controlled size before handing them to partitioning or placement.

- A lower bound can only prove impossibility; “possible” needs an actual legal grouping, which is as hard as bin packing.
- This chapter’s exhaustive search only suits 10 nodes or fewer; at real scale you need heuristics or mathematical programming, usually with no guarantee of optimality.
- Greedy never backtracks. In a dead end, all it can do is report honestly; improving on it needs methods that allow moving back or swapping, which is the subject of Modules 07 and 08.
