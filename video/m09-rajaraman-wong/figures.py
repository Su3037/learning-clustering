"""Slide figures for Module 09 (candidate DAG is labelled on every figure that shows it)."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("rw_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, fit, INK, MUTED, GOLD, TEAL, RED, PURPLE  # noqa: E402

POS = fit({k: tuple(v) for k, v in F.DAG["positions"].items()}, (960, 240, 1800, 780))


def chain(cv, a):
    with cv.place(500, 200, 0.62):
        F.chain(cv, [["P", "X"], ["Y", "O"]], label="跨界 1 次：延迟 7")
    with cv.place(500, 520, 0.62):
        F.chain(cv, [["P"], ["X", "Y"], ["O"]], label="跨界 2 次：延迟 10")


def dag(cv, a):
    F.dag(cv, POS, labels=({n: e["after"]["label"] for n, e in F.LABEL_EV.items()} | {p: 1 for p in F.PIS}) if a.get("labels") else None, r=24,
          cluster=F.LABEL_EV[a["cluster"]]["after"]["cluster"] if a.get("cluster") else (), focus=a.get("cluster"))
    tag(cv, 1380, 900, "候选复原数据 · 平票为假设", PURPLE, 1.0, 22)


def replica(cv, a):
    with cv.place(460, 100, 0.7):
        F.p1_replica(cv, _C())


def label_i(cv, a):
    e = F.LABEL_EV["i"]
    rows = [["祖先", "l(x)", "Δ", "得分", ""]] + [[x["x"], str(x["l"]), str(x["delta"]), str(x["score"]), "簇内" if x["inCluster"] else "簇外"] for x in e["candidates"]]
    table(cv, 1000, 270, [120, 120, 100, 120, 130], rows, 32, 66, {i + 1: TEAL for i, x in enumerate(e["candidates"]) if x["inCluster"]})
    tag(cv, 1330, 860, f"l1 = {e['metrics']['l1']}，l2 = {e['metrics']['l2']}，l(i) = {e['metrics']['label']}", GOLD)


def instances(cv, a):
    with cv.place(860, 180, 0.56):
        F.instances_view(cv, highlight=a.get("highlight"))
    tag(cv, 1360, 760, f"{len(F.R['selected'])} 簇 · {F.R['instanceCount']} 实例 · 输出 {F.R['maxDelay']}", GOLD)


def compare(cv, a):
    rows = [["", "允许复制（RW）", "禁止复制（穷举）"], ["最大延迟", str(F.R["maxDelay"]), str(F.NR["bestMaxDelay"])], ["实例 / 面积", str(F.R["instanceCount"]), str(F.R["logicalCount"])]]
    table(cv, 980, 330, [260, 300, 320], rows, 36, 96, {1: TEAL})
    cv.text(980, 660, "不复制的最好方案之一：" + " | ".join("".join(x) for x in F.NR["example"]), 28, INK)


def pseudo(cv, a):
    code(cv, 930, 280, F.CODE1 if a.get("part", 1) == 1 else F.CODE2, a.get("active", (4, 5)), 26, 60, w=900)


class _C:
    k, t = 99, 1e9
    def on(self, k): return True
    def p(self, *a, **kw): return 1.0


FIGURES = {"chain": chain, "dag": dag, "replica": replica, "label_i": label_i, "instances": instances, "compare": compare, "pseudo": pseudo}
