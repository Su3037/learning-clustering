## {#m09-goal} The goal has changed: from cut to delay

The previous seven modules all reduced the **cut**: the fewer wires between groups, the better. On a chip, though, what often matters more is **speed**: as a signal travels from input to output, the slowest path decides how fast the circuit can run.

Put the circuit into separate clusters (for example different chip regions or devices), and **wires between clusters are much slower than wires inside one**. So the question becomes: how should we cluster so that **the delay of the longest path** is as small as possible?

Start with the simplest chain: P → X → Y → O, each node with delay 1, each crossing between clusters adding D = 3, and at most 2 nodes per cluster.

| Split | Crossings on the path | Delay |
| --- | --- | --- |
| {P, X} \| {Y, O} | 1 (X→Y) | 4 + 3 = **7** |
| {P} \| {X, Y} \| {O} | 2 (P→X, Y→O) | 4 + 3 + 3 = **10** |

Both splits respect the capacity, yet the delays differ by 3. **Delay depends only on how many boundaries the longest path crosses**, not on how many wires are cut in total. On a branching circuit, two splits can cut the same number of wires while the critical path crosses a different number of boundaries.

## {#m09-model} The model: DAG, delay, capacity

```terms
directed acyclic graph | DAG | A combinational circuit: signals flow along directed edges, with no cycles. This chapter does not use the earlier undirected five-node graph.
primary input / output | PI / PO | Source nodes with no inputs / the circuit’s outputs.
node delay | node delay δ(v) | The time a signal needs to pass through node v. In this chapter’s example, δ = 1.
inter-cluster delay | inter-cluster delay D | The fixed extra delay of a wire whose two ends are in different clusters; 0 inside a cluster. It has nothing to do with the degree matrix D of Module 06.
cluster capacity | capacity M | The upper limit on a cluster’s size. In this chapter’s example each node has size 1 and M = 4.
```

A path’s delay = the sum of δ over the nodes on it + D × the number of crossings. The circuit’s delay = the largest over all PI→PO paths.

Background: Lawler, Levitt and Turner (1969) studied module clustering under unit delay; Rajaraman and Wong proposed an algorithm for general node delays at DAC 1993, published in IEEE TCAD in 1995, and proved that **when nodes may be replicated** it finds a clustering whose largest delay is minimal.

## {#m09-replication} Replication: one logic node, several instances

```terms
logic node | logicalId | A gate or cell of the circuit (for example b).
physical instance | instanceId | A copy of a logic node placed in some cluster, written “node@root” in this course (for example b@d).
replication | replication | Placing an instance of the same logic node in several clusters. Every instance needs complete inputs.
```

Why replicate? If one node feeds two delay-critical clusters, putting it in one of them makes the other fetch the signal across a boundary, paying D. With a copy, both clusters get it from inside.

```callout warn Replication is not free, and a “node → cluster” map cannot express it
Every copy takes area. The 12 logic nodes of the candidate example end up as 20 instances. As a data structure, a “node → cluster” map gives each node a single cluster; after replication, logic nodes and instances must be recorded separately, and every instance’s inputs checked for completeness. The course engine’s `instances[{instanceId, logicalId, clusterId}]` and instance wires exist for exactly this.
```

## {#m09-init} Initialisation: the longest node delay Δ

The candidate example (reconstructed from a figure in the original author muranfei’s film, **candidate** status) has 12 nodes a–l: PIs a, b, c, POs k, l, and 15 directed edges.

> **Δ(x, v)**: over all paths from x to v, the largest sum of node delays, counting v but not x. Undefined when there is no path.

For example, b → e → g → i → k passes through e, g, i and k: Δ(b, k) = 4. The original film shows the full Δ table at 438 s; this course recomputes it from the reconstructed edge list, and the two agree entry by entry.

A PI’s label is its own delay: l(a) = l(b) = l(c) = 1.

## {#m09-label} Labelling: l(v) = max(l1, l2)

Process each non-PI node v in **topological order**:

1. For each ancestor x of v, compute **l(x) + Δ(x, v)**: “if everything before x is as fast as possible, how long does the signal take to get from x to v”.
2. Sort by this value, largest first (on a tie, this course assumes the later node in topological order comes first: a **candidate assumption**).
3. Put v and the leading ancestors into the candidate cluster, in order, up to capacity M.
4. **l1** = the largest value among the PIs inside the cluster; **l2** = the largest value among the ancestors outside + D. **l(v) = max(l1, l2)**.

Take i (capacity 4):

| Ancestor x | l(x) + Δ(x, i) | Inside? |
| --- | --- | --- |
| g | 3 + 1 = 4 | yes |
| e | 2 + 2 = 4 | yes |
| c | 1 + 3 = 4 | yes (PI) |
| b | 1 + 3 = 4 | no |
| f, d, a | 3 | no |

l1 = 4 (the PI c inside), l2 = 4 + 3 = 7 (b is the largest outside). **l(i) = 7**. Finally l(k) = l(l) = 8.

```callout note Two kinds of “label”
RW’s l(v) is a **time**; Module 05’s label is a **group tag**. The name is the same; the meaning is entirely different.
```

## {#m09-reconstruct} Recovery: working back from the outputs

Labelling only gives each node a candidate cluster. The clusters actually used are found by working back from the POs:

1. Start from k and l and take their candidate clusters: k’s {g, i, j, k}, l’s {e, g, j, l}.
2. The inputs from outside (k’s cluster needs d, e, f, h; l’s cluster needs b, c, h) each become a new root, and their candidate clusters are taken.
3. Repeat until no new cluster is needed.

The candidate example gives **8 clusters and 20 instances**; g, j, e and a have 2 instances each, b and c 3 each. Every instance has complete inputs (the course tests check this). Both outputs arrive at time **8**, equal to their labels.

**Compared with no replication**: with the same capacity 4 and D = 3, if each node may sit in only one cluster, this course’s exhaustive search over every legal grouping gives a best largest delay of **10**. Replication spends 8 extra instances to buy 2 units of delay.

## {#m09-pseudocode} Pseudocode

```pseudo rw
check the input is a DAG; topological order; compute Δ(x, v)  || A cycle is an error. Δ counts v, not x.
for each PI p: l(p) ← δ(p)                         || PIs have no inputs.
for each non-PI node v (topological order):       || v’s ancestors are all labelled already.
    score(x) ← l(x) + Δ(x, v), for each ancestor x of v || The earliest time from x to v.
    candidate cluster ← v + ancestors by score, descending, up to M || Ties: the later in topological order (candidate assumption).
    l1 ← largest score of a PI inside; l2 ← largest score outside + D || A path from outside must cross one boundary.
    l(v) ← max(l1, l2)                              || The label is a time, not a group.
from the POs back: take candidate clusters; outside inputs become new roots || Recover the clusters actually needed.
make an instance per (root, member); connect the instance wires || A logic node may have several instances; check inputs are complete.
```

**How it maps to Python**: line 1 → `topological_order()`, `longest_node_delays()`; lines 2–7 → `rw_label()`; lines 8–9 → `rw_reconstruct()`; arrival times → `evaluate_instance_delay()`.

## {#m09-scope} Limits and open questions

- **Optimality only within the model**: a DAG, node delays, 0 inside a cluster, a fixed D between clusters, capacity, and **replication allowed**. If replication is forbidden, or area, pins or power must also be optimal, the result does not carry over. This course’s tests check the implementation’s consistency; they do not prove optimality.
- **Candidate data**: the 12-node example is reconstructed from frames of the original film; “on a tie, reverse topological order first” is an assumption. It reproduces 8 clusters, 20 instances and output 8, but the original edge list and tie rule await the original author’s confirmation.
- **Course mapping**: this submission is numbered Lesson 9, while Lab 09 in the teacher’s catalogue is Multilevel. This module keeps RW as submitted, does not replace Multilevel, and the correspondence awaits the teacher’s confirmation.
- **In engineering**: delay-driven clustering is used when a circuit is split across chips or FPGA regions, to reduce the delay between regions; replication buys speed and costs area.
