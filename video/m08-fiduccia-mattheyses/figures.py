"""Slide figures for Module 08."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("fm_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, fit, INK, MUTED, GOLD, TEAL, RED  # noqa: E402


class _C:
    def __init__(self, k=99): self.k, self.t = k, 1e9
    def on(self, k): return True
    def p(self, *a, **kw): return 1.0
    def since(self, k): return 1e9


def g(cv, side, **kw):
    with cv.place(800, 40, 1.0):
        F.graph(cv, F.POS, F.E5, side, **kw)


def gains(cv, a):
    with cv.place(800, 150, 0.56):
        F.graph(cv, F.POS, F.E5, F.T["seed"], blocked=("A", "E"), focus="D")
    F.gain_table(cv, F.EV[0]["gains"], 1320, 300, "D")


def fste(cv, a):
    g(cv, F.T["seed"], focus="D", hl={"D|E": "hl", "C|D": "trial"})
    tag(cv, 1350, 960, "FS D–E +5，TE C–D −2 → 收益 3", GOLD)


def walk(cv, a):
    rows = [["步", "移动", "收益", "cut", "累计"]] + [[str(i + 1), m["node"], f"{m['gain']:+d}", str(m["cutAfter"]), f"{m['cumulative']:+d}"] for i, m in enumerate(F.P1["moves"])]
    table(cv, 980, 300, [100, 140, 140, 140, 140], rows, 34, 76, {2: GOLD})


def prefix(cv, a):
    F.cum_chart(cv, 1000, 250, F.P1["prefixGains"], F.P1["bestK"])
    tag(cv, 1340, 780, f"接受前 {F.P1['bestK']} 步：ABC | DE，cut {F.P1['acceptedCut']}", TEAL)


def legacy(cv, a):
    L = F.T["legacy"]
    gE = next(g for g in L["run"]["events"][0]["gains"] if g["node"] == "E")
    rows = [["", "原文", "按数据计算"], ["初始 cut", "9", str(L["run"]["events"][0]["metrics"]["cut"])], ["合法收益", "全部 ≤ 0", f"E 合法 +{gE['gain']}"],
            ["最终 cut", "4", f"首轮 {L['run']['result']['passes'][0]['acceptedCut']}"], ["穷举最优", "—", str(L["optimum"]["cut"])]]
    table(cv, 980, 320, [240, 260, 340], rows, 34, 90, {i: RED for i in range(1, 5)})


def escape(cv, a):
    E = F.T["escape"]
    g = E["graph"]
    p = E["run"]["result"]["passes"][0]
    pos = fit({k: tuple(v) for k, v in g["positions"].items()}, (960, 250, 1400, 620))
    F.graph(cv, pos, [tuple(x) for x in g["edges"]], p["accepted"], r=34)
    rows = [["步", "移动", "收益", "cut"]] + [[str(i + 1), m["node"], f"{m['gain']:+d}", str(m["cutAfter"])] for i, m in enumerate(p["moves"][:3])]
    table(cv, 1480, 280, [70, 100, 100, 80], rows, 28, 58, {3: GOLD})
    tag(cv, 1350, 860, f"保留 3 步：cut {p['startCut']} → {p['acceptedCut']} = 穷举最优", TEAL)


def multipin(cv, a):
    with cv.place(700, 60, 0.95):
        pins = {"A": (360, 360), "B": (360, 560), "C": (560, 460), "D": (1000, 460)}
        hub = (760, 460)
        for n, p in pins.items():
            cv.line(*hub, *p, F.PURPLE, 4)
        cv.circle(*hub, 14, fill=F.PURPLE)
        cv.text(760, 420, "net（权 3）", 26, F.PURPLE, "bold", "center")
        for n, p in pins.items():
            F.node(cv, *p, n, F.SIDEC[0 if n != "D" else 1], 40)
        cv.line(820, 260, 820, 700, GOLD, 3, 1.0, dash=[10, 8])
    tag(cv, 1340, 860, "按引脚计数：A 0，D +3；拆成团：A −1", GOLD)


def pseudo(cv, a):
    code(cv, 930, 290, F.CODE, (3, 4), 27, 62, w=900)


FIGURES = {"gains": gains, "fste": fste, "walk": walk, "prefix": prefix, "legacy": legacy, "escape": escape, "multipin": multipin, "pseudo": pseudo}
