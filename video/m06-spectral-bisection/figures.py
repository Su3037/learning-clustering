"""Slide figures for Module 06 (drawn with the slide kit, once per language).
Every value is read from site/data/m06-spectral-bisection/traces.json."""
import json
from pathlib import Path

from kit import X, table, code, tag, node, edge, fit, INK, MUTED, FAINT, GOLD, TEAL, RED, BLUE, PANEL2

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m06-spectral-bisection/traces.json").read_text())
R = T["run"]["result"]
IDS = R["ids"]
E5 = [tuple(e) for e in T["g01"]["edges"]]
P5 = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
LMAT = T["laplacian"]["L"]


def g5(cv, pos, groups=None, tags=None):
    for u, v, w in E5:
        edge(cv, pos[u], pos[v], w, "cut" if groups and groups[u] != groups[v] else "normal")
    for n in IDS:
        node(cv, *pos[n], n, (TEAL if groups[n] == "L" else BLUE) if groups else "#a9bdb8", 40)
        if tags:
            cv.text(pos[n][0], pos[n][1] + 78, tags[n], 26, GOLD, "bold", "center")


def matrix(cv, x, y, M, cell=96, size=34):
    for j, n in enumerate(IDS):
        cv.text(x + cell * j + cell / 2, y - 18, n, 26, MUTED, "bold", "center")
        cv.text(x - 30, y + cell * j + cell * 0.62, n, 26, MUTED, "bold", "center")
    for i in range(len(IDS)):
        for j in range(len(IDS)):
            cv.rect(x + cell * j, y + cell * i, cell - 6, cell - 6, fill=PANEL2, stroke="#24474d", width=2, r=8)
            v = M[i][j]
            cv.text(x + cell * j + cell / 2 - 3, y + cell * i + cell * 0.62, f"{v:g}".replace("-", "−"), size,
                    GOLD if i == j else (INK if v else FAINT), "bold" if i == j else "normal", "center")


def number_line(cv, x0, x1, y, vals, order, k=None, r=34):
    """Nodes at their Fiedler values; a crowded neighbour steps up a row; gold dashes mark cut k."""
    lo, hi = min(vals), max(vals)
    sx = lambda v: x0 + (x1 - x0) * (v - lo) / ((hi - lo) or 1)
    cv.line(x0 - 30, y, x1 + 30, y, "#5d7c80", 3)
    last_x, up = None, False
    for i, n in enumerate(order):
        tx = sx(vals[i])
        up = (not up) if last_x is not None and tx - last_x < 2 * r + 10 else False
        ty = y - 2.4 * r if up else y
        last_x = tx
        if up:
            cv.line(tx, ty + r, tx, y, "#5d7c80", 2)
            cv.circle(tx, y, 5, fill="#5d7c80")
        node(cv, tx, ty, n, (TEAL if i < k else BLUE) if k else "#a9bdb8", r, size=28)
        cv.text(tx, y + 62 + (28 if i % 2 else 0), f"{vals[i]:+.3f}", 24, MUTED, align="center")
    if k:
        xm = (sx(vals[k - 1]) + sx(vals[k])) / 2
        cv.line(xm, y - 3 * r, xm, y + 50, GOLD, 4, dash=[10, 7])


def g01(cv, a):
    g5(cv, fit(P5, (1000, 260, 1700, 800)))


def matrix_fig(cv, a):
    matrix(cv, 1000, 260, LMAT, 112)
    for i in range(5):
        cv.text(1580, 260 + 112 * i + 70, X("行和 0", "row sum 0"), 26, TEAL, "bold")


def quad(cv, a):
    ind = {n: (1 if n in "ABC" else -1) for n in IDS}
    g5(cv, fit(P5, (1000, 260, 1700, 760)), {n: "L" if ind[n] > 0 else "R" for n in IDS})
    cv.text(1350, 850, X("青 = +1（A、B、C）  ·  蓝 = −1（D、E）", "teal = +1 (A, B, C)  ·  blue = −1 (D, E)"), 26, MUTED, "normal", "center")
    tag(cv, 1350, 930, "xᵀLx = 4 × cut = 12", GOLD)


def line(cv, a):
    number_line(cv, 980, 1760, 420, R["orderValues"], R["order"], a.get("k"))
    ev = R["eigenvalues"]
    cv.text(980, 640, "λ = " + X("，", ", ").join("0" if abs(v) < 1e-9 else f"{v:.4f}" for v in ev), 28, INK)
    cv.text(980, 700, X("Fiedler 排序：", "Fiedler order: ") + X("，", ", ").join(R["order"]), 30, GOLD, "bold")


def sweep(cv, a):
    number_line(cv, 980, 1760, 330, R["orderValues"], R["order"], R["bestK"])
    rows = [["k", X("左组", "Left"), "cut", X("40/60 窗口", "40/60 window")]] + \
           [[str(x["k"]), "".join(x["left"]), str(x["cut"]), X("合法", "legal") if x["legal"] else "—"] for x in R["sweep"]]
    table(cv, 1000, 560, [90, 230, 120, 220], rows, 32, 66, {R["bestK"]: GOLD})


def fix(cv, a):
    rows = [[X("孤立", "Isolate"), X("cut = 度数", "cut = degree")]] + [[n, f"{LMAT[i][i]:g}"] for i, n in enumerate(IDS)]
    table(cv, 1000, 280, [180, 260], rows, 32, 64)
    rows2 = [[X("向量来源", "Vector source"), X("残差", "Residual")], [X("实时求解", "solved live"), f"{R['diagnostics']['residual']:.1e}"],
             [X("原作三位小数", "original, 3 decimals"), f"{T['stored']['residual']:.4f}"]]
    table(cv, 1000, 760, [340, 220], rows2, 30, 60)


def disc(cv, a):
    D = T["disconnected"]
    pos = fit({k: tuple(v) for k, v in D["graph"]["positions"].items()}, (1000, 320, 1760, 620))
    for u, v, w in D["graph"]["edges"]:
        edge(cv, pos[u], pos[v], w, "normal")
    for n, p in pos.items():
        node(cv, *p, n, TEAL if n in "ABC" else BLUE, 38)
    tag(cv, 1380, 820, X("λ1 = λ2 = 0：排序只反映连通分量", "λ1 = λ2 = 0: the order only reflects components"), RED)


CODE = [X("L ← D − A（检查对称、行和 0）", "L ← D − A (check symmetry, row sums 0)"),
        X("(λ, x) ← 特征分解，升序", "(λ, x) ← eigendecomposition, ascending"),
        X("检查 连通、简并、残差", "check connectivity, degeneracy, residual"),
        X("f ← λ2 的特征向量（统一符号）", "f ← eigenvector of λ2 (fix the sign)"),
        X("order ← 按 f 升序", "order ← sort by f, ascending"),
        X("for k = 1 … n−1：计算 cut", "for k = 1 … n−1: compute cut"),
        X("返回窗口内 cut 最小的 k", "return the k with least cut in the window")]


def pseudo(cv, a):
    code(cv, 930, 300, CODE, (5, 6, 7), 27, 66, w=900)


FIGURES = {"g01": g01, "matrix": matrix_fig, "quad": quad, "line": line, "sweep": sweep, "fix": fix, "disc": disc, "pseudo": pseudo}
