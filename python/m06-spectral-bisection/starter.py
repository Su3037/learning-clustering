"""Module 06 · 谱二分 —— 练习起始代码（Python 3.9+，仅标准库；NumPy 可选，仅检查器用于对照）。

L = D − A（未归一化拉普拉斯矩阵，D 是度矩阵，不是 RW 的跨簇延迟 D）。
连通图 λ1 = 0；第二小特征值 λ2 的特征向量（Fiedler 向量）给每个节点一个数。
按这个数排序，逐个位置扫描切分，只在声明的平衡窗口内选 cut 最小的一刀。
向量整体乘 −1 只交换左右名字，分组不变。
"""
import math


def laplacian(nodes, edges):
    """任务 1：构造 L = D − A（列表的列表，节点顺序同 nodes）。

    每条无向边 (u, v, w)：L[u][u] += w，L[v][v] += w，L[u][v] −= w，L[v][u] −= w。
    五节点图 A 行应为 [6, −5, −1, 0, 0]，每行和为 0。
    """
    raise NotImplementedError("laplacian")


def jacobi_eigen(M, tol=1e-13, max_sweeps=100):
    """对称矩阵的循环 Jacobi 旋转。返回按特征值升序的 [(λ, 向量), ...]。"""
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
    """任务 2：沿排序逐个位置切分。返回 [{"k","left","right","cut","legal"}, ...]，k = 1 … n−1。

    left = order[:k]；legal 表示两组大小都在 [lo, hi] 内。不要只切正中间，也不要只按正负号切。
    """
    raise NotImplementedError("sweep")


def balance_window(n, lo_frac=0.4, hi_frac=0.6):
    return max(1, math.ceil(lo_frac * n - 1e-9)), min(n - 1, math.floor(hi_frac * n + 1e-9))


def spectral_bisection(nodes, edges, balance_bounds=(0.4, 0.6)):
    L = laplacian(nodes, edges)
    pairs = jacobi_eigen(L)
    lam2, vec = pairs[1]
    # 统一符号：字典序第一个非零分量取正（翻号不改变分组）
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
    """任务 3：两组都非空、不区分左右的二分有多少种？（提示：2^n 里去掉哪两种，再除以几？）"""
    raise NotImplementedError("count_bipartitions")


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    r = spectral_bisection(g["nodes"], g["edges"])
    print("λ =", [round(x, 10) for x in r["eigenvalues"]])
    print("顺序", r["order"], "扫描", [c["cut"] for c in r["candidates"]], "选择", r["partition"], "cut", r["cut"])
    print("残差", r["diagnostics"]["residual"], "非空二分数", count_bipartitions(5))
