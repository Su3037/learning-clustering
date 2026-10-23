## {#m07-problem} Improving a split with fixed sizes

The earlier methods all build a grouping from nothing. KL asks a different question: **there is already a bisection; how do we make it better?**

Picture two machine rooms: 2 cells on the left, 3 on the right, and the head count may not change. The more wires cross between the rooms, the higher the cost. The only move allowed is a **one-for-one swap**: one cell from the left trades places with one from the right. To compare fairly, this chapter always starts from a deliberately poor seed:

> **AE | BCD**: the edges across are A–B 5, A–C 1, C–E 1, D–E 5, cut = 12.

```terms
initial bisection | 二分种子 | The bisection the improvement starts from. KL’s result depends on it.
swap | 交换 | One node from the left and one from the right trade groups. The side sizes stay the same.
```

KL was proposed by Kernighan and Lin in 1970 and is one of the classic heuristics for improving a bisection. The original author, FanqinZeng, introduced the fixed head count through a made-up story of five classmates being grouped; this chapter keeps that constraint and explains the rules on the course graph.

## {#m07-gain} D values and the pair gain: why subtract 2w

```terms
external | 外部边权 | The total weight of v’s edges to nodes on the other side.
internal | 内部边权 | The total weight of v’s edges to nodes on its own side.
D(v) = external − internal | D 值 | How much the cut drops if v alone moves across.
gain | 收益 | The cut before a swap minus the cut after it.
```

On the seed AE | BCD:

| Node | Side | External | Internal | D |
| --- | --- | --- | --- | --- |
| A | left | 5 + 1 = 6 | 0 | +6 |
| B | right | 5 | 4 | +1 |
| C | right | 1 + 1 = 2 | 4 + 2 = 6 | −4 |
| D | right | 5 | 2 | +3 |
| E | left | 1 + 5 = 6 | 0 | +6 |

The gain of swapping a (left) with b (right):

> **g(a, b) = D(a) + D(b) − 2·w(a, b)**

Why subtract 2w? Look at E and D: D(E) + D(D) = 9, but both D values count edge DE (5) as “external”. After the swap E is on the right and D on the left: they are still on opposite sides, and DE is **still cut**. The edge was counted twice too many, so take back 2 × 5: g(E, D) = 9 − 10 = −1.

The gains of the six candidate pairs: A↔D **+9**, E↔B +7, A↔C 0, E↔C 0, E↔D −1, A↔B −3. The largest is A↔D (there is no edge between A and D, so nothing comes off).

## {#m07-pass} One pass: trial, lock, update

Within one pass, repeat:

1. Among the **unlocked** left/right pairs, pick the one with the largest gain, **even if the gain is negative**;
2. swap them (this is only a **trial**);
3. lock both nodes: they don’t move again this pass;
4. recompute D for the new grouping.

Pass 1 on G01:

| Step | Trial swap | Gain | Cut after | Cumulative gain |
| --- | --- | --- | --- | --- |
| 1 | A↔D | +9 | 3 | +9 |
| 2 | E↔C | −8 | **11** | +1 |

At step 2 only E (left) and B, C (right) are unlocked: E↔C −8, E↔B −13, all negative. KL does not stop here; it takes the largest, E↔C, and the cut rises to 11 for now. No unlocked node is left on the left, so the pass’s trials end.

```callout warn Why take negative gains
On this small graph step 2 can only make things worse; but on a bigger graph, a step that first makes things worse can “open up” a larger positive gain later. Only by finishing the whole pass can you see every prefix, and then decide how many steps to keep.
```

## {#m07-prefix} The best prefix, roll-back and stopping

```terms
prefix | 前缀 | The first k consecutive steps of a pass’s trial sequence, starting at step 1.
best prefix k* | 最佳前缀 | The prefix with the largest cumulative gain; k = 0 (do nothing) is a candidate too.
trial / accepted | 试探 / 接受 | The trial state is the temporary grouping mid-pass; the accepted state applies only the first k* steps to the pass’s start.
```

Pass 1’s cumulative gains: k = 0 → 0, k = 1 → **+9**, k = 2 → +1. The largest is k* = 1: **from the pass start, apply only A↔D**, accepting ABC | DE, cut 3. Step 2 is undone: it was only there to see whether anything better came later.

**Pass 2** starts from ABC | DE with every node unlocked: trials E↔C −8, D↔B +2, cumulative −8, −6. Neither beats doing nothing: **the empty prefix k* = 0 wins**, the cut stays 3, and the algorithm stops.

## {#m07-pseudocode} The pseudocode, line by line

```pseudo kl
repeat:                                              || One pass; every node is unlocked at the start of a pass.
    start ← current bisection; trial ← start         || Remember the pass start: the roll-back returns here.
    while both sides have unlocked nodes:            || At most min(left, right) swaps per pass.
        compute D = external − internal for unlocked nodes || D is computed from trial (the trial state), not start.
        (a, b) ← unlocked cross pair with the largest g = D(a)+D(b)−2w(a,b) || Gains may be negative; ties by (−g, a, b).
        swap a, b in trial; lock a, b                || This is a trial, not an acceptance.
    k* ← prefix with the largest cumulative gain (k* = 0 allowed) || On a tie, the shorter prefix.
    current bisection ← start with only the first k* steps applied || Roll back: the trial state is discarded.
until k* = 0                                         || The empty prefix: no improvement at all, so stop.
```

**How it maps to Python**: lines 4–5 → `best_swap()`; line 7 → `best_prefix()`; lines 1–9 → `kernighan_lin()`.

## {#m07-limits} Limits and uses

- **A heuristic**: reaching cut 3 on G01 does not mean KL finds the global optimum in general; it can stop at a local optimum.
- **Depends on the seed**: different initial bisections can give different results; compare methods from the same seed. This module’s seed is the same as Module 08’s.
- **Keeps only the count**: a one-for-one swap keeps the node count per side, not the area.
- **Cost**: a naive implementation scans every unlocked cross pair at each step.
- **In engineering**: KL and the next module’s FM are both used for local improvement after a spectral method or another initial partition. Changing one edge weight means recomputing every D value: for example, with A–B changed from 5 to 1 the initial cut becomes 8 and the gain of A↔D becomes 5.
