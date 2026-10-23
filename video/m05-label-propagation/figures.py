"""Slide figures for Module 05."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("lp_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, fit, INK, MUTED, GOLD, TEAL, RED  # noqa: E402


class _C:
    k, t = 99, 1e9
    def on(self, k): return True
    def p(self, *a, **kw): return 1.0
    def since(self, k): return 1e9


def contacts(cv, a):
    pos = fit({k: tuple(v) for k, v in F.CON["positions"].items()}, (900, 220, 1820, 820))
    F.big_graph(cv, F.CON, pos, F.CONSTATES[-1], 1.0, 14, F.CON.get("names"))
    r = F.CONRUN["result"]
    tag(cv, 1360, 930, f"{r['rounds']} 轮停下，切开的联系 {r['cut']}", TEAL)


def circuit(cv, a):
    pos = fit({k: tuple(v) for k, v in F.CIRC["positions"].items()}, (900, 240, 1820, 800))
    which = a.get("which", "lp")
    labels = F.T["circuit"]["geometric"]["labels"] if which == "geo" else F.CIRCSTATES[-1]
    F.big_graph(cv, F.CIRC, pos, labels, 1.0, 14)
    tag(cv, 1360, 930, f"尺子切法 cut {F.T['circuit']['geometric']['cut']}" if which == "geo" else f"标签传播 {F.CRUN['result']['rounds']} 轮，cut {F.CRUN['result']['cut']}", RED if which == "geo" else TEAL)


def g5(cv, labels, focus=None):
    with cv.place(780, 20, 1.0):
        F.g5_labels(cv, labels, focus)


def labels0(cv, a):
    g5(cv, {n: n for n in "ABCDE"})


def vote(cv, a):
    ev = next(e for e in F.GOLDEN["events"] if e["round"] == 1 and e["node"] == "C")
    with cv.place(800, 200, 0.7):
        F.g5_labels(cv, ev["before"], "C")
    F.ballot(cv, 1340, 330, ev["votes"], ev["label"], 1.0, "C 的票（第 1 轮）")


def round1(cv, a):
    r1 = [e for e in F.GOLDEN["events"] if e["round"] == 1]
    rows = [["访问", "票数", "新标签", "改变"]] + [[e["node"], "，".join(f"{l}:{v}" for l, v in e["votes"].items()), e["label"], "是" if e["changed"] else "否"] for e in r1]
    table(cv, 960, 290, [110, 330, 170, 120], rows, 32, 76)
    tag(cv, 1330, 820, f"第 2 轮零变化 → stable，{F.GOLDEN['result']['rounds']} 轮，cut {F.GOLDEN['result']['cut']}", TEAL)


def sync(cv, a):
    with cv.place(760, 150, 0.6):
        F.s_sync(cv, _C())
    rows = [["轮", "A", "B", "C", "D", "E"]]
    st = [{n: n for n in "ABCDE"}] + [e["after"] for e in F.T["syncG01"]["events"] if e["kind"] == "update-round-end"]
    for i, s in enumerate(st):
        rows.append([str(i)] + [s[n] for n in "ABCDE"])
    table(cv, 1000, 720, [100] + [110] * 5, rows, 28, 50)


def bridge(cv, a):
    h = F.T["heavy"]
    with cv.place(780, 40, 1.0):
        labels = h["result"]["labels"]
        for u, v, w in F.E5:
            ww = 10 if (u, v) == ("C", "D") else w
            F.edge(cv, F.POS5[u], F.POS5[v], ww, "hl" if (u, v) == ("C", "D") else ("cut" if labels[u] != labels[v] else "inside"))
        for n, p in F.POS5.items():
            F.node(cv, *p, n, F.lab_color(labels[n], list("ABCDE")), 40)
    tag(cv, 1350, 930, f"C–D = 10：{h['result']['grouping'].replace(',', '')}，cut {h['result']['cut']}", GOLD)


def pseudo(cv, a):
    lines = ["labels[v] ← v", "repeat 每一轮:", "  for v in 访问顺序:", "    votes ← 按邻居标签累加边权", "    new ← 最大票（平票规则）", "    异步：立即写回；同步：先记下", "  同步：轮末一起提交", "  零变化 → stable；重复 → cycle"]
    code(cv, 930, 300, lines, (4, 5), 27, 64, w=900)


FIGURES = {"contacts": contacts, "circuit": circuit, "labels0": labels0, "vote": vote, "round1": round1, "sync": sync, "bridge": bridge, "pseudo": pseudo}
