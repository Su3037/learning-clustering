"""Module 06 · Spectral bisection: reference implementation (Python 3.9+, standard library only; NumPy is optional and only used by the checker for comparison).

L = D − A (the unnormalised Laplacian; D is the degree matrix, not the inter-cluster delay D of RW).
A connected graph has λ1 = 0; the eigenvector of the second-smallest eigenvalue λ2 (the Fiedler vector) gives each node a number.
Sort by that number, sweep every cut position, and choose the least cut only inside the declared balance window.
Multiplying the whole vector by −1 only swaps the names left and right; the grouping is unchanged.
"""
import math


def laplacian(nodes, edges):
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    L = [[0.0] * n for _ in range(n)]
    for u, v, w in edges:
        i, j = idx[u], idx[v]
        L[i][i] += w
        L[j][j] += w
        L[i][j] -= w
        L[j][i] -= w
    return L


def jacobi_eigen(M, tol=1e-13, max_sweeps=100):
    """Cyclic Jacobi rotations for a symmetric matrix. Returns [(λ, vector), ...] in ascending order of eigenvalue."""
    n = len(M)
    A = [row[:] for row in M]
    V = [[float(i == j) for j in range(n)] for i in range(n)]
    for _ in range(max_sweeps):
        off = math.sqrt(sum(A[p][q] ** 2 for p in range(n) for q in range(p + 1, n)))
        if off < tol:
            break
        for p in range(n):
            for q in range(p + 1, n):
                if abs(A[p][q]) < 1e-300:
                    continue
                theta = (A[q][q] - A[p][p]) / (2 * A[p][q])
                t = (1 if theta >= 0 else -1) / (abs(theta) + math.sqrt(theta * theta + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(n):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p], A[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(n):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k], A[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p], V[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    pairs = [(A[i][i], [V[k][i] for k in range(n)]) for i in range(n)]
    return sorted(pairs, key=lambda t: t[0])


def residual(L, lam, x):
    n = len(x)
    r = [sum(L[i][j] * x[j] for j in range(n)) - lam * x[i] for i in range(n)]
    return math.sqrt(sum(v * v for v in r)) / (math.sqrt(sum(v * v for v in x)) or 1)


def cut(edges, left):
    return sum(w for u, v, w in edges if (u in left) != (v in left))


def sweep(order, edges, lo, hi):
    """Cut at every position along the order: the first k form one side. Compute each cut and mark whether it is inside the balance window [lo, hi]."""
    n = len(order)
    out = []
    for k in range(1, n):
        legal = lo <= k <= hi and lo <= n - k <= hi
        out.append({"k": k, "left": order[:k], "right": order[k:], "cut": cut(edges, set(order[:k])), "legal": legal})
    return out


def balance_window(n, lo_frac=0.4, hi_frac=0.6):
    return max(1, math.ceil(lo_frac * n - 1e-9)), min(n - 1, math.floor(hi_frac * n + 1e-9))


def spectral_bisection(nodes, edges, balance_bounds=(0.4, 0.6)):
    L = laplacian(nodes, edges)
    pairs = jacobi_eigen(L)
    lam2, vec = pairs[1]
    # fix the sign: the first non-zero entry in name order is positive (a flip does not change the grouping)
    for i in sorted(range(len(nodes)), key=lambda i: nodes[i]):
        if abs(vec[i]) > 1e-9:
            if vec[i] < 0:
                vec = [-x for x in vec]
            break
    order = [nodes[i] for i in sorted(range(len(nodes)), key=lambda i: (vec[i], nodes[i]))]
    lo, hi = balance_window(len(nodes), *balance_bounds)
    candidates = sweep(order, edges, lo, hi)
    legal = [c for c in candidates if c["legal"]]
    best = min(legal, key=lambda c: c["cut"]) if legal else None
    return {"eigenvalues": [p[0] for p in pairs], "vector": vec, "order": order, "candidates": candidates,
            "partition": (best["left"], best["right"]) if best else None, "cut": best["cut"] if best else None,
            "diagnostics": {"row_sums": [sum(r) for r in L], "residual": residual(L, lam2, vec),
                            "lambda2": lam2, "lambda3": pairs[2][0] if len(pairs) > 2 else None}}


def count_bipartitions(n):
    """Bipartitions with both sides non-empty and no left/right: (2^n − 2) / 2."""
    return (2 ** n - 2) // 2


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    r = spectral_bisection(g["nodes"], g["edges"])
    print("λ =", [round(x, 10) for x in r["eigenvalues"]])
    print("order", r["order"], "sweep", [c["cut"] for c in r["candidates"]], "chosen", r["partition"], "cut", r["cut"])
    print("residual", r["diagnostics"]["residual"], "non-empty bipartitions", count_bipartitions(5))
