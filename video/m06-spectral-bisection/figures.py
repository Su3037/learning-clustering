"""Slide figures for Module 06."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("sp_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, fit, formula, INK, MUTED, GOLD, TEAL, RED, BLUE  # noqa: E402

R = F.R


def g01(cv, a):
    with cv.place(800, 40, 1.0):
        F.g5(cv)


def matrix(cv, a):
    F.matrix(cv, 1000, 260, F.LMAT, 112)
    for i in range(5):
        cv.text(1580, 260 + 112 * i + 70, "行和 0", 26, TEAL, "bold")


def quad(cv, a):
    ind = {n: (1 if n in "ABC" else -1) for n in F.IDS}
    F.g5(cv, {n: "L" if ind[n] > 0 else "R" for n in F.IDS}, 1.0, pos=fit({k: tuple(v) for k, v in F.T["g01"]["positions"].items()}, (1000, 260, 1700, 760)), tags={n: f"{ind[n]:+d}" for n in F.IDS})
    tag(cv, 1350, 930, "xᵀLx = 4 × cut = 12", GOLD)


def line(cv, a):
    F.number_line(cv, 980, 1760, 420, R["orderValues"], R["order"], a.get("k"))
    ev = R["eigenvalues"]
    cv.text(980, 640, "λ = " + "，".join("0" if abs(v) < 1e-9 else f"{v:.4f}" for v in ev), 28, INK)
    cv.text(980, 700, "Fiedler 排序：" + "，".join(R["order"]), 30, GOLD, "bold")


def sweep(cv, a):
    F.number_line(cv, 980, 1760, 330, R["orderValues"], R["order"], R["bestK"])
    rows = [["k", "左组", "cut", "40/60 窗口"]] + [[str(x["k"]), "".join(x["left"]), str(x["cut"]), "合法" if x["legal"] else "—"] for x in R["sweep"]]
    table(cv, 1000, 560, [90, 230, 120, 200], rows, 32, 66, {R["bestK"]: GOLD})


def fix(cv, a):
    L = F.LMAT
    rows = [["孤立", "cut = 度数"]] + [[n, f"{L[i][i]:g}"] for i, n in enumerate(F.IDS)]
    table(cv, 1000, 280, [180, 260], rows, 32, 64)
    rows2 = [["向量来源", "残差"], ["实时求解", f"{R['diagnostics']['residual']:.1e}"], ["原作三位小数", f"{F.T['stored']['residual']:.4f}"]]
    table(cv, 1000, 760, [300, 220], rows2, 30, 60)


def disc(cv, a):
    D = F.T["disconnected"]
    pos = fit({k: tuple(v) for k, v in D["graph"]["positions"].items()}, (1000, 320, 1760, 620))
    for u, v, w in D["graph"]["edges"]:
        F.edge(cv, pos[u], pos[v], w, "normal")
    for n, p in pos.items():
        F.node(cv, *p, n, TEAL if n in "ABC" else BLUE, 38)
    tag(cv, 1380, 820, "λ1 = λ2 = 0：排序只反映连通分量", RED)


def pseudo(cv, a):
    code(cv, 930, 300, F.CODE, (5, 6, 7), 27, 66, w=900)


FIGURES = {"g01": g01, "matrix": matrix, "quad": quad, "line": line, "sweep": sweep, "fix": fix, "disc": disc, "pseudo": pseudo}
