## {#m08-diff} How it differs from KL: one node at a time

KL swaps one for one, so the side sizes never change. FM (Fiduccia and Mattheyses, 1982) instead **moves one node at a time**. That is more flexible, but the sizes change, so a **balance constraint** is added:

> After a move, both sides are nonempty and **|n₀ − n₁| ≤ maxDiff**.

This chapter’s seed is the same as Module 07’s: AE | BCD, cut 12. Five nodes with maxDiff = 1 means the sides can only be 2 : 3 or 3 : 2.

```terms
single move | 单点移动 | Moving one node from its side (F) to the other side (T).
balance window | 平衡窗口 | In this chapter, by node count: |n₀ − n₁| ≤ maxDiff, with both sides nonempty. Not area.
legal candidate | 合法候选 | A node that is unlocked and still satisfies the balance after moving.
```

## {#m08-legal} Legality and gain: the largest may not be allowed to move

The gain of a single move = the cut before the move − the cut after it. Written per net (signal net), it splits into two parts:

> **FS (from-side)**: v is a net’s only pin on side F → after the move the net is no longer cut, **+w**.
> **TE (to-side)**: a net has no pin at all on side T → after the move it becomes cut, **−w**.

For ordinary 2-pin edges this is just “external weight − internal weight”.

The initial gains on seed AE | BCD:

| Node | Side | Gain | Sides after | Legal |
| --- | --- | --- | --- | --- |
| A | left (2 nodes) | +6 | 1 : 4 | **no** |
| B | right | +1 | 3 : 2 | yes |
| C | right | −4 | 3 : 2 | yes |
| D | right | **+3** | 3 : 2 | yes |
| E | left (2 nodes) | +6 | 1 : 4 | **no** |

A and E have the largest gain but may not move: moving either leaves 1 node on the left. **“Largest” is compared among legal candidates only**: choose D (+3).

D’s breakdown: on DE (5), D is the only pin on side F → FS **+5**; CD (2) has no pin on side T (the left) → TE **−2**; gain = 3.

## {#m08-walk} One full pass: D, then A, then the roll-back

| Step | Move | Gain | Cut after | Cumulative |
| --- | --- | --- | --- | --- |
| 1 | D (right → left) | +3 | 9 | 3 |
| 2 | A (left → right) | +6 | **3** | **9** |
| 3 | C | −2 | 5 | 7 |
| 4 | E | −6 | 11 | 1 |
| 5 | B | −1 | 12 | 0 |

Once D has moved, the left has 3 nodes, and only then does A become a legal candidate, with gain +6. Every gain after that is negative, but the moves are still tried one by one, until no legal unlocked node is left.

The largest cumulative gain is the first **2** steps (+9): from the start apply only “move D, move A”, and accept **ABC | DE, cut 3**. The final cut 12 is only where the trials ended, not the result. Pass 2 starts from ABC | DE; its best prefix is empty, and the algorithm stops.

## {#m08-escape} What negative gains are for: a verified example

The original attachment has a case named hillclimb, whose text says: “initial cut 9, every legal move has gain ≤ 0; plain greedy gets stuck, while FM first takes −1, then gains +6, down to 4.” Computed from the attachment’s **own data**:

- the initial cut is **18**, not 9;
- E’s move is legal, with gain **+10**: not every legal gain is ≤ 0;
- pass 1’s best cut is **8**, and exhaustive search over every balanced bisection gives an optimum of 8 too, not 4.

```callout mistake The text does not match the data
This case cannot be used to show that “negative gains help escape a local optimum”. This course keeps its data only as a regression test and as material on “how to audit an example”, not as correct teaching material.
```

This course’s **replacement example** was found by a seeded search and checked by independent computation:

- 6 nodes, edges A–C 4, A–E 5, B–C 2, B–E 1, C–F 3, D–E 1, E–F 1; seed ADE | BCF, maxDiff = 2; initial cut 6.
- At the start **every legal move has gain ≤ 0** (A, B, C, D are −1, F is −2, E is −4): hill climbing that accepts only positive gains stops at cut 6.
- FM first moves A to the right (−1) and B to the left (−1), and the cut rises to 8; now E’s strongest tie, A–E (5), is already across, E’s gain becomes **+4**, and after the move the cut is 4.
- The best prefix is k* = 3, accepting cut **4**; exhaustive search over every balanced bisection gives exactly 4.

The two steps that first make things worse change E’s surroundings, and only then does E have a positive gain. That is what “trying negative gains” is for.

## {#m08-bucket} Buckets, complexity and multi-pin nets

One of the FM paper’s contributions is **linear time**: nodes go into “buckets” by gain (an array of linked lists), a pointer tracks the largest gain, and each move updates only the affected nodes, so a pass costs time in proportion to the total pin count P.

```callout warn Showing is not implementing
Both the original attachment and this course’s lab **show** nodes grouped by gain into buckets. This course’s engine recomputes after each move only the gains of nodes on affected nets (FM’s incremental update rule, checked one by one against a from-scratch recomputation in the tests), but choosing the largest gain still scans every legal candidate. So **this implementation does not reach O(P)**, and the page does not claim it.
```

**Multi-pin nets (extension)**: in a real hypergraph one net can join 3 or more cells. FS/TE must be decided by **counting pins** on each side: for net {A,B,C,D} (weight 3) with A, B, C on the left and D on the right, A’s gain is 0 (the net stays cut after A moves); split the net into a clique (3/(4−1) = 1 per pair) and count edges, and you get 1 − 2 = −1. This course’s engine implements multi-pin nets by counting pins; the attachment’s third case, named hypergraph, actually has only 2-pin edges, and this chapter treats it as an ordinary 7-node graph (initial cut 22, best prefix of 3 steps, down to cut 1).

## {#m08-pseudocode} The pseudocode, line by line

```pseudo fm
repeat:                                               || One pass; unlock everything at the start and remember the start.
    count each net's pins per side; compute every gain by FS/TE || For 2-pin edges: gain = external − internal.
    while a legal unlocked node exists:               || Legal: after moving, both sides nonempty and |n₀ − n₁| ≤ maxDiff.
        v ← the legal candidate with the largest gain (ties by name) || “Largest” among legal candidates only; gains may be negative.
        move v (a trial), lock v                      || Record the gain, FS/TE and the cut after the move.
        update only the gains of other unlocked nodes on v's nets || Incremental update; this implementation's selection is still a scan.
    k* ← prefix with the largest cumulative gain (0 allowed) || As in KL; on a tie, the shorter one.
    current bisection ← start with only the first k* steps applied || Roll back: the end of the trials is discarded.
until k* = 0                                          || The empty prefix means stop.
```

**How it maps to Python**: lines 2 and 6 → `gain()`; lines 3–4 → `legal_moves()`; line 7 → `best_prefix()`; a whole pass → `fm_pass()` and `fm_refine()`.

## {#m08-limits} Where it applies

- FM and its multilevel variants are the core refinement step of EDA partitioning tools; real tools handle multi-pin nets and area balance.
- This chapter’s base track balances by node count only; an area window is not implemented and is marked as an extension.
- The result depends on the seed and the tie rule. The attachment’s tie rule (on equal gain prefer moving from the larger side, names in reverse) differs from this course’s, so the move order differs in some cases; every value listed in this chapter is computed independently by this course’s engine and its Python reference, and the two are checked against each other.
