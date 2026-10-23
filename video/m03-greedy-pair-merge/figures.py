"""Slide figures for Module 03."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("merge_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, INK, MUTED, GOLD, TEAL, RED, MONO  # noqa: E402


def graph(cv, clusters, small=False, **kw):
    with cv.place(760, 40, 1.0) if not small else cv.place(780, 120, 0.8):
        F.state_graph(cv, clusters, **kw)


def start(cv, a):
    graph(cv, F.RUN["events"][0]["after"])
    tag(cv, 1350, 960, "单点簇：cut = 18", RED)


def step(cv, a):
    ev = F.MERGES[a.get("i", 0)]
    graph(cv, ev["after"], small=True, focus=[m for c in ev["after"] if c["label"] == ev["decision"]["merged"] for m in c["members"]])
    rows = [["候选", "亲和度"]] + [[f"{c['a']}–{c['b']}", str(c["affinity"])] for c in ev["candidates"][:4]]
    table(cv, 1580, 300, [150, 120], rows, 28, 56, {1: GOLD})
    tag(cv, 1350, 960, f"cut {ev['metrics']['cutBefore']} → {ev['metrics']['cut']}", TEAL)


def trajectory(cv, a):
    rows = [["步", "合并", "亲和度", "cut"], ["0", "—", "—", "18"]] + [[str(e["step"]), f"{e['decision']['a']} + {e['decision']['b']}", str(e["decision"]["affinity"]), str(e["metrics"]["cut"])] for e in F.MERGES]
    table(cv, 980, 300, [110, 300, 180, 140], rows, 36, 86, {4: TEAL})


def bug(cv, a):
    cv.text(960, 330, '[−5, "A", "B"]  →  "-5,A,B"', 36, INK, family=MONO)
    cv.text(960, 400, '[−1, "A", "C"]  →  "-1,A,C"', 36, INK, family=MONO)
    cv.text(960, 480, "字符 1 < 5：亲和度 1 的 A–C 被当成更好", 30, RED, "bold")
    rows = [["配置", "原网页", "正确"], ["K=2", "9", "3"], ["K=3", "16", "8"], ["K=2 容量2", "12", "8"], ["K=2 容量3", "16", "3"]]
    table(cv, 980, 590, [300, 180, 180], rows, 32, 66)


def capacity(cv, a):
    stop = [e for e in F.CAP2["events"] if e["kind"] == "stopped"][0]
    graph(cv, stop["after"])
    tag(cv, 1350, 960, "容量 2：AB | C | DE，cut 8，未达到 K", GOLD)


def pseudo(cv, a):
    code(cv, 930, 300, F.CODE, (4, 5, 6), 27, 64, w=900)


FIGURES = {"start": start, "step": step, "trajectory": trajectory, "bug": bug, "capacity": capacity, "pseudo": pseudo}
