"""Slide figures for Module 07, drawn with the film's own functions (same traces, same look)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("kl_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, formula, panel, tag, INK, MUTED, GOLD, TEAL, RED  # noqa: E402


def graph_at(cv, side, lay, **kw):
    with cv.place(738, 77, 0.95):
        F.stage(cv, side, lay, **kw)


def seed(cv, a):
    graph_at(cv, F.SEEDSIDE, F.L0)
    cv.text(1345, 900, f"种子 AE | BCD：cut = {F.cut_of(F.SEEDSIDE)}", 32, GOLD, "bold", "center")


def dtable(cv, a):
    d = F.TRIAL1["dValues"]
    rows = [["节点", "侧", "外部", "内部", "D = 外 − 内"]] + [[n, "左" if F.SEEDSIDE[n] == 0 else "右", str(d[n]["ext"]), str(d[n]["int"]), f"{d[n]['D']:+d}"] for n in "ABCDE"]
    table(cv, 960, 300, [130, 110, 150, 150, 240], rows, 38, 82)


def pairs(cv, a):
    formula(cv, 1340, 290, [("g(a,b) = D(a) + D(b) − ", INK), ("2w(a,b)", RED)], 44)
    rows = [["左 a", "右 b", "D(a)+D(b)", "−2w", "g"]] + [[x["a"], x["b"], str(x["Da"] + x["Db"]), str(-2 * x["w"]), f"{x['gain']:+d}"] for x in F.TRIAL1["candidates"]]
    table(cv, 960, 400, [120, 120, 220, 140, 140], rows, 36, 74, {1: GOLD})


def minus2w(cv, a):
    graph_at(cv, F.SEEDSIDE, F.L0, edge_states={"D|E": "hl"}, rings={"E": GOLD, "D": GOLD})
    cv.text(1345, 900, "E↔D：DE 交换前后都被切 → 扣回 2 × 5", 30, GOLD, "bold", "center")


def trial1(cv, a):
    graph_at(cv, F.S1, F.L1, locked=("A", "D"))
    cv.text(1345, 900, f"试探 A↔D：g = +9，cut {F.TRIAL1['metrics']['cutBefore']} → {F.TRIAL1['metrics']['cut']}", 32, GOLD, "bold", "center")


def trial2(cv, a):
    graph_at(cv, F.S2, F.L2, locked=("A", "D", "E", "C"))
    cv.text(1345, 900, f"试探 E↔C：g = −8，cut 暂升到 {F.TRIAL2['metrics']['cut']}", 32, RED, "bold", "center")


def prefix(cv, a):
    F.prefix_chart(cv, 1000, 250, F.PASS1["prefixGains"], F.PASS1["bestK"], 1.0, 1.0, True)
    tag(cv, 1320, 800, f"接受前 {F.PASS1['bestK']} 步：ABC | DE，cut {F.PASS1['acceptedCut']}", TEAL)


def pass2(cv, a):
    F.prefix_chart(cv, 1000, 250, F.PASS2["prefixGains"], F.PASS2["bestK"], 1.0, 1.0, True, "第二轮的累计收益")
    tag(cv, 1320, 800, "空前缀 k = 0 胜出 → 停止，cut 3", GOLD)


def pseudo(cv, a):
    code(cv, 960, 300, F.CODE, a.get("active", (4, 5)), 28, 64, w=860)


FIGURES = {"seed": seed, "dtable": dtable, "pairs": pairs, "minus2w": minus2w, "trial1": trial1, "trial2": trial2, "prefix": prefix, "pass2": pass2, "pseudo": pseudo}
