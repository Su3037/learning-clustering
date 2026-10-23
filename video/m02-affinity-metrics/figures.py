"""Slide figures for Module 02 (film drawing functions, same traces)."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("aff_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, formula, tag, score_box, INK, MUTED, GOLD, TEAL, RED, BLUE  # noqa: E402


class _C:
    """A frozen clock: every beat already shown."""
    def __init__(self, k=99): self.k, self.t = k, 1e9
    def on(self, k): return True
    def p(self, *a, **kw): return 1.0
    def since(self, k): return 1e9


def graph_right(cv, **kw):
    with cv.place(800, 40, 1.0):
        F.g5(cv, **kw)


def g01(cv, a):
    graph_right(cv)
    cv.text(1380, 960, "课程公共图 G01（总权 18）", 30, MUTED, "bold", "center")


def model(cv, a):
    with cv.place(880, 160, 0.5):
        F.s_model(cv, _C())


def edge_rank(cv, a):
    rows = [["名次", "节点对", "分数"]] + [[str(i + 1), f"{x['u']}–{x['v']}", str(x["score"])] for i, x in enumerate(F.EDGE_RANK)]
    table(cv, 1000, 300, [170, 300, 170], rows, 38, 84, {1: GOLD, 2: GOLD})


def shared_table(cv, a):
    rows = [["节点对", "直接", "经共同邻居", "分数"]]
    for p in F.T["shared"]:
        via = " + ".join(f"{v['x']}:{v['min']}" for v in p["parts"]["via"]) or "—"
        rows.append([f"{p['u']}–{p['v']}", str(p["parts"]["direct"]), via, str(p["score"])])
    hl = {i: GOLD for i, r in enumerate(rows) if r[0] in ("A–C", "B–D")}
    table(cv, 980, 250, [170, 120, 330, 120], rows, 32, 66, hl)


def hand(cv, a):
    pair = tuple(a.get("pair", "AC"))
    s = F.SHARED[pair]
    items = [(f"直接边 w({pair[0]},{pair[1]})", s["parts"]["direct"], TEAL, 1)] + [(f"经 {x['x']}：min({x['wu']}, {x['wv']})", x["min"], GOLD, 1) for x in s["parts"]["via"]]
    with cv.place(880, 120, 0.62):
        F.g5(cv, {"|".join(sorted((pair[0], x["x"]))): "hl" for x in s["parts"]["via"]} | {"|".join(sorted((pair[1], x["x"]))): "hl" for x in s["parts"]["via"]}, {pair[0]: GOLD, pair[1]: GOLD})
    score_box(cv, 1440, 260, 400, items, s["score"], 1.0, f"{pair[0]}–{pair[1]}", 28)


def priority(cv, a):
    with cv.place(860, 180, 0.52):
        F.s_priority(cv, _C())


def pin(cv, a):
    with cv.place(840, 100, 0.55):
        F.netlist(cv, 1.0, 0, ("E", "F"))
    raw = {(p["u"], p["v"]): p["score"] for p in F.PIN["raw"]}
    sc = {(p["u"], p["v"]): p["score"] for p in F.PIN["scores"]}
    rows = [["", "按 net 计数", "pin-count"], ["A–B", str(raw[("A", "B")]), f"{sc[('A', 'B')]:g}"], ["E–F", str(raw[("E", "F")]), f"{sc[('E', 'F')]:g}"]]
    table(cv, 1000, 620, [150, 260, 240], rows, 36, 76, {2: GOLD})


def pseudo(cv, a):
    code(cv, 930, 300, F.CODE, (3, 4), 26, 64, w=900)


FIGURES = {"g01": g01, "model": model, "edge_rank": edge_rank, "shared_table": shared_table, "hand": hand, "priority": priority, "pin": pin, "pseudo": pseudo}
