## {#m06-goal} Bisection: why “non-empty” and “balanced” must be declared

A **bisection** splits the nodes into two groups. If all we ask for is the smallest cut, there is a useless answer: put every node in one group, and the cut is 0. So the problem has to be stated first:

1. **Both groups are non-empty**;
2. **Left and right are not distinguished**: ABC | DE and DE | ABC are the same split;
3. **A balance window**: each group’s size must lie in some range, for example 40%–60% of all nodes.

Under these conventions, how many splits do 5 nodes have? Of the 2⁵ = 32 ways to label every node left or right, drop “all left” and “all right”, then divide by 2 (swapping sides counts once):

> (2⁵ − 2) / 2 = **15**

```callout mistake The original quiz’s 16
The original quiz says 16. The extra one is “one group empty, the other everything”. This course enumerates the non-empty, unlabelled bisections of G01, and the tests assert exactly 15.
```

Enumerating 15 is fine for 5 nodes, but hopeless once there are many. The spectral idea is: **give every point a number first, line them up, and cut only between neighbours on that line**. With n nodes there are only n − 1 candidates.

## {#m06-laplacian} From edge weights to the Laplacian

```terms
degree d(v) | 度 | The sum of the weights of the edges at v. A’s degree = 5 + 1 = 6.
adjacency matrix A | 邻接矩阵 | A[u][v] = w(u, v); 0 where there is no edge.
Laplacian L = D − A | 拉普拉斯矩阵 | Degrees on the diagonal, negative edge weights off it. The D here is the degree matrix, not the inter-cluster delay D of Module 09.
```

Each undirected edge (u, v, w) contributes to four entries of L: L[u][u] += w, L[v][v] += w, L[u][v] −= w, L[v][u] −= w. The L of G01 (rows and columns A–E):

| | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| A | 6 | −5 | −1 | 0 | 0 |
| B | −5 | 9 | −4 | 0 | 0 |
| C | −1 | −4 | 8 | −2 | −1 |
| D | 0 | 0 | −2 | 7 | −5 |
| E | 0 | 0 | −1 | −5 | 6 |

Two self-checks: **L is symmetric**, and **every row sums to 0** (the degree on the diagonal equals the sum of the negative weights in its row). Row sums of 0 mean the all-ones vector satisfies L·1 = 0: λ = 0 is always an eigenvalue of L.

## {#m06-quadratic} The quadratic form: why tightly linked points get close numbers

Give every node a number x_v. L has one key property:

> **xᵀLx = Σ w(u, v)·(x_u − x_v)²**, summed once over every undirected edge.

If x may only be +1 (left group) or −1 (right group), a cut edge contributes w·(2)² = 4w and an uncut edge contributes 0, so **xᵀLx = 4·cut**. The indicator vector of ABC | DE gives 4 × 3 = 12.

Minimising the cut is hard because x must be ±1. The spectral method **relaxes** that condition: x may be any real vector, as long as it is not constant (orthogonal to all-ones) and has fixed length. The optimum of the relaxed problem is the eigenvector of the second-smallest eigenvalue λ2.

```callout analogy The spring analogy (only here)
Picture each edge as a spring, stiffer for a larger weight; xᵀLx is like the total “energy” of all the stretched springs. Stiff springs pull tightly linked nodes together, so their numbers come out close. This is only a picture to help with the quadratic form: this page runs no physical simulation, the weights are not real stiffnesses, and the algorithms in other modules have nothing to do with springs.
```

## {#m06-fiedler} The Fiedler vector and its conditions

```terms
eigenvalue / eigenvector | 特征值 / 特征向量 | A number λ and a non-zero vector x with Lx = λx.
Fiedler vector | Fiedler 向量 | The eigenvector of the second-smallest eigenvalue λ2 (pronounced “FEED-ler”). λ2 is also called the algebraic connectivity.
```

The eigenvalues of G01 (solved live in this page’s browser, matching NumPy):

> λ1 ≈ 0, **λ2 ≈ 1.7733143437**, λ3 ≈ 8.455, λ4 ≈ 11.605, λ5 ≈ 14.166

The Fiedler vector (sign fixed so that A is positive) is about A 0.519, B 0.418, C 0.106, D −0.489, E −0.553.

Three conditions to watch:

- **Connected**: in a connected graph λ1 = 0 occurs once; when the graph falls apart, λ2 is 0 as well, and the vector only tells you which points share a connected component.
- **Degenerate**: if λ2 = λ3, the second eigenvector is not unique; any direction in that eigenspace is equally valid, and the order can differ.
- **Sign flip**: if x is an eigenvector, so is −x. Flipping the whole vector only reverses the order and swaps left and right; the grouping is unchanged.

## {#m06-sweep} The sweep: try every cut inside the window

Sort by Fiedler value, smallest first: **E, D, C, B, A**. Cut between neighbours, with the first k as one group:

| k | Left | Right | cut | 40/60 window (2–3 a side) |
| --- | --- | --- | --- | --- |
| 1 | E | D C B A | 6 | not legal |
| 2 | E D | C B A | **3** | legal |
| 3 | E D C | B A | 5 | legal |
| 4 | E D C B | A | 6 | not legal |

Inside the window, k = 2 has the least cut: **DE | ABC, cut 3**. Two things to notice:

- “Cutting right in the middle” (k = 3) is not better: its cut is 5.
- On this graph the sign boundary also happens to fall at k = 2; in general the sign does not guarantee a split inside the window, which is why we sweep.

The original author’s page let students choose k by hand and see the cut live; this chapter’s lab keeps that interaction.

## {#m06-errors} Three common misunderstandings, corrected

1. **The number of bisections is 15, not 16** (see section 1).
2. **Without a balance constraint, the optimum does not have to isolate one node.** Isolating a node cuts exactly its degree: A 6, B 9, C 8, D 7, E 6, so at least 6; yet ABC | DE cuts only 3. The correct statement: without a constraint a group **can** come out too small, so declare a window.
3. **A precomputed vector is not a solver.** The original page stores a vector to three decimals; changing k recomputes the cut live, but changing the graph does not recompute the vector. The residual ‖Lx − λx‖/‖x‖ of the three-decimal vector is about 0.0044; that is rounding, not a failed solve. This course solves live in the browser with Jacobi rotations (residual about 10⁻¹⁵) and keeps the original values for comparison.

## {#m06-pseudocode} Pseudocode and numerical self-checks

```pseudo spectral
L ← D − A                                   || Each edge contributes to four entries; check symmetry and zero row sums.
(λ, x) ← eigendecomposition of L, ascending  || This page: Jacobi rotations; Python: the same pure-Python solver, NumPy optional as a cross-check.
check λ1 ≈ 0, connectivity, degenerate λ2, residual || Warn when disconnected or degenerate: the order may only reflect components, or the direction is not unique.
f ← eigenvector of λ2, sign fixed             || A flip only swaps sides; fixing the sign just keeps the display stable.
order ← nodes by f ascending, ties by name    || n points on one number line.
for k = 1 … n−1: left = order[:k], compute cut || n − 1 candidate cuts; record whether each is inside the balance window.
return the k with least cut inside the window || The spectral method gives a good candidate, not a guaranteed global optimum.
```

**How it maps to Python**: line 1 → `laplacian()`; line 2 → the provided `jacobi_eigen()`; lines 6–7 → `sweep()` and `spectral_bisection()`. The checker also verifies the residual, sign-flip equivalence, and λ2 = 0 on a disconnected graph.

**In EDA**, spectral methods often give large partitioning problems a first solution with a global view, which is then handed to local improvement methods such as KL/FM: exactly the next two modules.
