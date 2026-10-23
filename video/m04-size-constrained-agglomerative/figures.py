"""Slide figures for Module 04."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("cap_film", Path(__file__).with_name("film.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
from kit import table, code, tag, fit, INK, MUTED, GOLD, TEAL, RED, BLUE  # noqa: E402


def g01(cv, cap_key, cap, x=900, y=250, w=600, h=520):
    run = F.T[cap_key]["run"]
    ev = F.events(run)[-1]
    pos = fit(F.G01POS, (x, y, x + w, y + h))
    blocked = sorted({m for cnd in ev.get("candidates", []) for m in (cnd["a"] + cnd["b"])}) if ev["kind"] == "stopped" else ()
    F.draw_state(cv, pos, F.G01E, ev["after"], F.sizes_of(F.T["g01"]), cap, blocked=blocked, r=34)
    r = run["result"]
    tag(cv, x + w / 2, y + h + 150, f"{' | '.join(r['labels'])} · cut {r['cut']}", TEAL if r["targetReached"] else GOLD, 1.0, 26)
    cv.text(x + w / 2, y - 70, f"容量 {cap}：{'达到' if r['targetReached'] else '未达到'} K", 30, INK, "bold", "center")


def report(cv, a):
    rows = [["报告项", "容量 2，K = 2"], ["count", "3"], ["capacityCompliant", "是"], ["targetReached", "否"], ["stopReason", "capacity-blocked"]]
    table(cv, 980, 320, [420, 360], rows, 36, 88, {3: GOLD})


def fork(cv, a):
    g01(cv, "cap3", 3, 960, 330, 330, 430)
    g01(cv, "cap2", 2, 1440, 330, 330, 430)


def fork2(cv, a):
    g01(cv, "cap2", 2, 1050, 240)


def bound(cv, a):
    with cv.place(800, 120, 0.62):
        F.s_bound(cv, _C())


def small_graph(cv, g, clusters, cap, box, colors=None, blocked=()):
    pos = fit({k: tuple(v) for k, v in g["positions"].items()}, box)
    F.draw_state(cv, pos, [tuple(e) for e in g["edges"]], clusters, F.sizes_of(g), cap, r=36, colors=colors, blocked=blocked)


def trap(cv, a):
    run = F.T["trap"]["run"]
    stop = F.events(run)[-1]
    small_graph(cv, F.TRAP, stop["after"], 3, (960, 300, 1780, 520), blocked=("A", "B"))
    tag(cv, 1370, 690, f"贪心：{' | '.join(run['result']['labels'])}，3 簇", GOLD, 1.0, 26)
    best = F.T["trap"]["oracle"]["bestCutAtK"]
    tag(cv, 1370, 790, f"穷举：{' | '.join(''.join(x) for x in best['clusters'])}，2 簇，cut {best['cut']}", TEAL, 1.0, 26)


def sub(cv, a):
    run, best = F.T["suboptimal"]["run"], F.T["suboptimal"]["oracle"]["bestCutAtK"]
    small_graph(cv, F.SUB, F.events(run)[-1]["after"], 2, (960, 330, 1300, 680), colors={"AB": TEAL, "CD": BLUE})
    clusters = [{"label": "".join(x), "members": x, "size": len(x)} for x in best["clusters"]]
    small_graph(cv, F.SUB, clusters, 2, (1470, 330, 1810, 680), colors={"AC": TEAL, "BD": BLUE})
    cv.text(1130, 270, "贪心", 30, INK, "bold", "center"); cv.text(1640, 270, "穷举最优", 30, INK, "bold", "center")
    tag(cv, 1130, 850, f"cut {run['result']['cut']}", RED, 1.0, 28); tag(cv, 1640, 850, f"cut {best['cut']}", TEAL, 1.0, 28)


def uneven(cv, a):
    ev = F.UNEVEN["events"][-1]
    pos = fit(F.G01POS, (1000, 260, 1700, 760))
    F.draw_state(cv, pos, F.G01E, ev["after"], {n: 2 if n == "A" else 1 for n in "ABCDE"}, 3, r=36)
    tag(cv, 1350, 920, f"{' | '.join(F.UNEVEN['result']['labels'])}，cut {F.UNEVEN['result']['cut']}", GOLD, 1.0, 28)


def pseudo(cv, a):
    code(cv, 930, 300, F.CODE, (4, 5), 27, 64, w=900)


class _C:
    k, t = 99, 1e9

    class scene:
        beats = [0] * 9

    def on(self, k): return True
    def p(self, *a, **kw): return 1.0


FIGURES = {"report": report, "fork": fork, "fork2": fork2, "bound": bound, "trap": trap, "sub": sub, "uneven": uneven, "pseudo": pseudo}
