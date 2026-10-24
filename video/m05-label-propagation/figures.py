"""Slide figures for Module 05 (drawn with the slide kit, once per language).
Every label, vote and cut is read from site/data/m05-label-propagation/traces.json."""
import json
from pathlib import Path

import kit
from kit import X, table, code, tag, fit, node, edge, panel, bar, clamp, INK, MUTED, GOLD, TEAL, RED, GROUP

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m05-label-propagation/traces.json").read_text())
G = T["g01"]
E5 = [tuple(e) for e in G["edges"]]
POS5 = fit({k: tuple(v) for k, v in G["positions"].items()}, (230, 240, 900, 790))
GOLDEN = T["golden"]
CON, CONRUN = T["contacts"]["graph"], T["contacts"]["run"]
CIRC, CRUN = T["circuit"]["graph"], T["circuit"]["run"]


def lab_color(label, universe):
    u = sorted(universe)
    return GROUP[u.index(label) % len(GROUP)] if label in u else "#a9bdb8"


def round_states(run):
    nodes = sorted(run["result"]["labels"])
    states = [{n: n for n in nodes}]
    for e in run["events"]:
        if e["kind"] == "update-round-end":
            states.append(dict(e["after"]))
    return states


def big_graph(cv, g, pos, labels, r=15, names=None):
    universe = sorted(set(labels.values())) if labels else []
    for u, v, w in g["edges"]:
        diff = labels and labels[u] != labels[v]
        cv.line(*pos[u], *pos[v], RED if diff else "#4f7377", 2.4 if diff else 1.8, 0.95 if diff else 0.7, dash=[8, 6] if diff else None)
    for n in g["nodes"]:
        x, y = pos[n]
        cv.circle(x, y, r, fill=lab_color(labels[n], universe) if labels else "#a9bdb8", stroke="#061418", width=2)
        if names:
            cv.text(x, y + r + 22, names.get(n, n), 18, MUTED, align="center")


def g5_labels(cv, labels, focus=None):
    for u, v, w in E5:
        edge(cv, POS5[u], POS5[v], w, "cut" if labels[u] != labels[v] else "inside")
    for n, p in POS5.items():
        node(cv, *p, n, lab_color(labels[n], list("ABCDE")), 40, 1.0, GOLD if focus == n else None)
        tag(cv, p[0], p[1] + 84, X(f"标签 {labels[n]}", f"label {labels[n]}"), lab_color(labels[n], list("ABCDE")), 1.0, 22)


def ballot(cv, x, y, votes, winner, title):
    panel(cv, x, y, 560, 120 + 80 * max(1, len(votes)), title)
    mx = max([1] + list(votes.values()))
    for i, (l, v) in enumerate(sorted(votes.items(), key=lambda t: (-t[1], t[0]))):
        yy = y + 110 + i * 80
        cv.text(x + 30, yy, X(f"标签 {l}", f"label {l}"), 30, INK)
        bar(cv, x + 170, yy - 22, 280, 22, v / mx, GOLD if l == winner else TEAL)
        cv.text(x + 520, yy, str(v), 34, GOLD if l == winner else INK, "bold", "right")


def contacts(cv, a):
    pos = fit({k: tuple(v) for k, v in CON["positions"].items()}, (900, 220, 1820, 820))
    big_graph(cv, CON, pos, round_states(CONRUN)[-1], 14, CON.get("names") if kit.LANG == "zh" else None)
    r = CONRUN["result"]
    tag(cv, 1360, 930, X(f"{r['rounds']} 轮停下，切开的联系 {r['cut']}", f"stable after {r['rounds']} rounds, cut {r['cut']}"), TEAL)


def circuit(cv, a):
    pos = fit({k: tuple(v) for k, v in CIRC["positions"].items()}, (900, 240, 1820, 800))
    geo = a.get("which", "lp") == "geo"
    big_graph(cv, CIRC, pos, T["circuit"]["geometric"]["labels"] if geo else round_states(CRUN)[-1], 14)
    gc, r = T["circuit"]["geometric"]["cut"], CRUN["result"]
    tag(cv, 1360, 930, X(f"尺子切法 cut {gc}", f"ruler split, cut {gc}") if geo else X(f"标签传播 {r['rounds']} 轮，cut {r['cut']}", f"label propagation, {r['rounds']} rounds, cut {r['cut']}"), RED if geo else TEAL)


def g5(cv, labels, focus=None):
    with cv.place(780, 20, 1.0):
        g5_labels(cv, labels, focus)


def labels0(cv, a):
    g5(cv, {n: n for n in "ABCDE"})


def vote(cv, a):
    ev = next(e for e in GOLDEN["events"] if e["round"] == 1 and e["node"] == "C")
    with cv.place(700, 230, 0.62):
        g5_labels(cv, ev["before"], "C")
    ballot(cv, 1340, 330, ev["votes"], ev["label"], X("C 的票（第 1 轮）", "C's votes (round 1)"))


def round1(cv, a):
    r1 = [e for e in GOLDEN["events"] if e["round"] == 1]
    rows = [[X("访问", "visit"), X("票数", "votes"), X("新标签", "new label"), X("改变", "changed")]] + \
           [[e["node"], X("，", ", ").join(f"{l}:{v}" for l, v in e["votes"].items()), e["label"], X("是", "yes") if e["changed"] else X("否", "no")] for e in r1]
    table(cv, 960, 290, [110, 330, 200, 120], rows, 32, 76)
    g = GOLDEN["result"]
    tag(cv, 1330, 820, X(f"第 2 轮零变化 → stable，{g['rounds']} 轮，cut {g['cut']}", f"round 2 unchanged → stable, {g['rounds']} rounds, cut {g['cut']}"), TEAL)


def sync(cv, a):
    pa, pb = (1060, 420), (1660, 420)
    edge(cv, pa, pb, 1, "cut")
    for n, p, l in (("A", pa, "B"), ("B", pb, "A")):
        node(cv, *p, n, lab_color(l, ["A", "B"]), 56, size=40)
        tag(cv, p[0], p[1] + 110, X(f"标签 {l} ⇄", f"label {l} ⇄"), lab_color(l, ["A", "B"]), 1.0, 26)
    cv.text(1360, 290, X("同步：两节点每轮交换标签", "Synchronous: the two nodes swap every round"), 32, GOLD, align="center")
    rows = [[X("轮", "round"), "A", "B", "C", "D", "E"]]
    st = round_states(T["syncG01"])
    for i, s in enumerate(st):
        rows.append([str(i)] + [s[n] for n in "ABCDE"])
    table(cv, 1000, 680, [120] + [110] * 5, rows, 28, 50, highlight={2: RED, 4: RED})


def bridge(cv, a):
    h = T["heavy"]
    with cv.place(780, 40, 1.0):
        labels = h["result"]["labels"]
        for u, v, w in E5:
            edge(cv, POS5[u], POS5[v], 10 if (u, v) == ("C", "D") else w, "hl" if (u, v) == ("C", "D") else ("cut" if labels[u] != labels[v] else "inside"))
        for n, p in POS5.items():
            node(cv, *p, n, lab_color(labels[n], list("ABCDE")), 40)
    grouping = h["result"]["grouping"].replace(",", "")
    tag(cv, 1350, 930, X(f"C–D = 10：{grouping}，cut {h['result']['cut']}", f"C–D = 10: {grouping}, cut {h['result']['cut']}"), GOLD)


def pseudo(cv, a):
    lines = ["labels[v] ← v", X("repeat 每一轮:", "repeat each round:"), X("  for v in 访问顺序:", "  for v in visiting order:"),
             X("    votes ← 按邻居标签累加边权", "    votes ← sum edge weights per neighbour label"), X("    new ← 最大票（平票规则）", "    new ← top vote (tie rule)"),
             X("    异步：立即写回；同步：先记下", "    async: write now; sync: note it"), X("  同步：轮末一起提交", "  sync: commit at round end"),
             X("  零变化 → stable；重复 → cycle", "  no change → stable; repeat → cycle")]
    code(cv, 930, 300, lines, (4, 5), 27, 64, w=900)


FIGURES = {"contacts": contacts, "circuit": circuit, "labels0": labels0, "vote": vote, "round1": round1, "sync": sync, "bridge": bridge, "pseudo": pseudo}
