"""Module 09 · Rajaraman–Wong delay-oriented clustering — the four films.

  story     popular science, cut to "We Never (Remix)": a dish passes through cooks a minute each, and carrying it
            across the yard to another kitchen costs three more; the slowest route decides; a banquet of twelve steps
            gets its earliest minutes one by one; two kitchens both need g and j, so each makes its own; working back
            from the finished dishes opens eight kitchens with twenty cooks; without copies the best is 10, not 8.
  concise   the essentials: from cut to delay on the chain, the model, Δ on the candidate DAG, the label of i
            (l1, l2), and the reverse recovery to 8 clusters, 20 instances and output 8.
  advanced  every label with its candidate cluster and the assumed tie rule, logic nodes versus instances, the
            exhaustive no-replication comparison, what the optimality result does and does not cover, and what in
            this chapter is candidate data awaiting confirmation.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every value is read from site/data/m09-rajaraman-wong/traces.json (scripts/build-traces.mjs runs site/engines/rw.js) and
no-replication.json (exhaustive search, scripts/research/rw_no_replication.py), and is checked here against the
course's Python reference, python/m09-rajaraman-wong/reference.py. The 12-node DAG is a candidate reconstruction:
every scene that shows it says so.
"""
import importlib.util
import json
import math
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, IVORY, MUTED, FAINT, DIM, LILAC,
                  PANEL_BG, NODE_BG, clamp, ease, title_card, panel, table, fit, pulse, substrate)
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m09-rajaraman-wong/traces.json").read_text())
NR = json.loads((ROOT / "site/data/m09-rajaraman-wong/no-replication.json").read_text())
BRAND = L("Learning Clustering · Module 09 · Rajaraman–Wong 延迟导向聚类", "Learning Clustering · Module 09 · Rajaraman–Wong delay-oriented clustering")
CAND = L("候选复原数据 · 平票规则为假设", "candidate data, reconstructed · tie rule assumed")

_spec = importlib.util.spec_from_file_location("m09ref", ROOT / "python/m09-rajaraman-wong/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

DAG = T["dag"]
NODES, EDGES = DAG["nodes"], [tuple(e) for e in DAG["edges"]]
PIS, POS_O = DAG["PI"], DAG["PO"]
DRAW = {k: tuple(v) for k, v in DAG["positions"].items()}
EVS = T["run"]["events"]
R = T["run"]["result"]
LABEL_EV = {e["after"]["node"]: e for e in EVS if e["kind"] == "label"}
SEL_EV = [e for e in EVS if e["kind"] == "select-cluster"]
LABELS = R["labels"]
ORDER = REF.topological_order(NODES, EDGES)
EI = LABEL_EV["i"]

# the reference, run independently, agrees with the engine's trace
_ref = REF.rajaraman_wong({"nodes": NODES, "edges": EDGES, "PI": PIS, "PO": POS_O, "capacity": DAG["capacity"], "D": DAG["D"]})
assert _ref["labels"] == LABELS and _ref["output_delay"] == R["outputDelays"]
assert {r: sorted(m) for r, m in _ref["clusters"].items()} == {r: sorted(m) for r, m in R["clusters"].items()}
assert len(_ref["instances"]) == R["instanceCount"] == 20 and R["logicalCount"] == 12 and R["totalSize"] == 20

# facts the captions state
assert DAG["capacity"] == 4 and DAG["D"] == 3 and DAG["nodeDelay"] == 1 and PIS == ["a", "b", "c"] and POS_O == ["k", "l"]
assert T["chainOne"]["maxDelay"] == 7 and T["chainOne"]["crossings"] == 1 and T["chainTwo"]["maxDelay"] == 10 and T["chainTwo"]["crossings"] == 2
assert LABELS == {"a": 1, "b": 1, "c": 1, "d": 2, "e": 2, "f": 2, "g": 3, "h": 2, "i": 7, "j": 7, "k": 8, "l": 8}
assert R["delta"]["b"]["k"] == 4
assert EI["after"]["cluster"] == ["i", "g", "e", "c"] and (EI["metrics"]["l1"], EI["metrics"]["l2"]) == (4, 7)
assert [(x["x"], x["score"], x["inCluster"]) for x in EI["candidates"]] == [("g", 4, True), ("e", 4, True), ("c", 4, True), ("b", 4, False), ("f", 3, False), ("d", 3, False), ("a", 3, False)]
assert R["selected"] == ["k", "l", "d", "e", "f", "h", "b", "c"]
assert R["clusters"]["k"] == ["g", "i", "j", "k"] and R["clusters"]["l"] == ["e", "g", "j", "l"]
assert {x["id"]: x["copies"] for x in R["replicated"]} == {"g": 2, "j": 2, "e": 2, "a": 2, "b": 3, "c": 3}
assert R["maxDelay"] == 8 and R["outputDelays"] == {"k": 8, "l": 8}
assert SEL_EV[0]["after"]["inputs"] == ["d", "e", "f", "h"] and SEL_EV[1]["after"]["inputs"] == ["b", "c", "h"]

# the longest route b → e → g → i → k: five steps, five minutes if no kitchen boundary is crossed
LONG = ["b", "e", "g", "i", "k"]
assert all((u, v) in EDGES for u, v in zip(LONG, LONG[1:])) and 1 + R["delta"]["b"]["k"] == 5
assert max(1 + R["delta"][p][o] for p in PIS for o in POS_O if R["delta"][p][o] is not None) == 5

# without replication: each node in one cluster; the exhaustive best is 10, re-evaluated here
NR_BEST = NR["example"]
_home = {v: i for i, grp in enumerate(NR_BEST) for v in grp}
_t = REF.evaluate_instance_delay({v: v for v in NODES}, [(u, v, 0 if _home[u] == _home[v] else DAG["D"]) for u, v in EDGES], {v: 1 for v in NODES})
assert NR["bestMaxDelay"] == 10 and max(_t[o] for o in POS_O) == 10 and all(len(g) <= 4 for g in NR_BEST)


def signed(x):
    return ("+" if x > 0 else "") + f"{x}"


def node_col(n, cluster=()):
    if n in cluster:
        return TEAL
    return BLUE if n in PIS else (ROSE if n in POS_O else "#9fbcbc")


def dag(fr, box, alpha=1.0, labels=None, cluster=(), focus=(), path=(), outside=(), r=30, lab_alpha=None, name_size=28):
    """The candidate DAG: arrows along the signal flow, PIs blue, POs rose, a candidate cluster teal; labels above."""
    pos = fit(DRAW, box)
    hot = set(zip(path, path[1:]))
    for u, v in EDGES:
        inside = u in cluster and v in cluster
        col = GOLD if (u, v) in hot else (TEAL if inside else DIM)
        fr.arrow(pos[u], pos[v], col, 3 if (u, v) in hot or inside else 2, alpha * (0.95 if (u, v) in hot or inside else 0.7),
                 head=12, glow=0.4 * alpha if (u, v) in hot else 0, shorten=r + 5)
    for n, p in pos.items():
        fr.dot(p, r, NODE_BG, alpha)
        fr.ring(p, r, node_col(n, cluster), 2.6, alpha, glow=0.5 * alpha if n in focus else 0)
        fr.text(n, p[0], p[1] + name_size * 0.36, name_size, IVORY, alpha, role="serif", anchor="c")
        if n in focus:
            fr.ring(p, r + 9, GOLD, 2.4, alpha, glow=0.5 * alpha)
        if n in outside:
            fr.ring(p, r + 9, ROSE, 2.0, alpha, dash=[5, 5])
        if labels and n in labels:
            la = (lab_alpha(n) if lab_alpha else 1.0) * alpha
            if la > 0:
                fr.text(str(labels[n]), p[0] + r * 0.9, p[1] - r * 0.9, 24, GOLD, la, role="mono", anchor="c", glow=0.2 * la)
    return pos


def cand_note(fr, alpha=1.0, x=W - 64, y=110):
    fr.text(CAND, x, y, 17, LILAC, 0.9 * alpha, anchor="r", spacing=1)


CHAIN = ["P", "X", "Y", "O"]


def chain(fr, groups, y, alpha=1.0, times=True, unit=L("分钟", "min"), D=3, word=None, cross_glow=0.0):
    """P → X → Y → O; each group a dashed box; crossings rose with +D; the arrival under each node."""
    x = lambda i: 450 + i * 340
    where = {n: gi for gi, g in enumerate(groups) for n in g}
    start = 0
    for gi, g in enumerate(groups):
        x0, x1 = x(start) - 92, x(start + len(g) - 1) + 92
        fr.rect(x0, y - 84, x1 - x0, 168, stroke=TEAL if gi % 2 == 0 else BLUE, width=1.8, alpha=0.8 * alpha, r=26, dash=[10, 7])
        if word:
            fr.text(tr(word).format(gi + 1), (x0 + x1) / 2, y - 100, 18, MUTED, alpha, anchor="c", spacing=1)
        start += len(g)
    t = 0
    for i, n in enumerate(CHAIN):
        if i:
            cross = where[CHAIN[i - 1]] != where[n]
            t += D if cross else 0
            fr.arrow((x(i - 1), y), (x(i), y), ROSE if cross else "#7aa5a6", 3 if cross else 2.4, alpha, head=14, shorten=46,
                     glow=(0.4 + cross_glow) * alpha if cross else 0)
            if cross:
                fr.text(f"+{D}", (x(i - 1) + x(i)) / 2, y - 22, 28, ROSE, alpha, anchor="c", role="mono")
        t += 1
        fr.dot((x(i), y), 42, NODE_BG, alpha)
        fr.ring((x(i), y), 42, "#9fbcbc", 2.6, alpha)
        fr.text(n, x(i), y + 12, 32, IVORY, alpha, role="serif", anchor="c")
        if times:
            fr.text(f"{t}", x(i), y + 82, 26, GOLD, alpha, anchor="c", role="mono")
    if times:
        fr.text(tr(unit), x(0) - 120, y + 82, 18, MUTED, alpha, anchor="r")
    return t


# the recovered clusters as boxes of instances, laid out by depth: PIs alone, then d e f h, then the two outputs
BOXES = {"f": (560, 205), "d": (560, 345), "e": (560, 485), "h": (560, 625), "b": (200, 380), "c": (200, 520),
         "k": (1080, 265), "l": (1080, 525)}
STEP = 92


def inst_pos():
    out = {}
    for root, (bx, by) in BOXES.items():
        for i, m in enumerate(R["clusters"][root]):
            out[f"{m}@{root}"] = (bx + 62 + STEP * i, by + 56)
    return out


IPOS = inst_pos()
COPIES = {x["id"]: x["copies"] for x in R["replicated"]}


def arc(fr, p, q, col, alpha, h=26):
    pts = [((1 - s) * p[0] + s * q[0], (1 - s) * p[1] + s * q[1] - h * math.sin(math.pi * s) - 22) for s in [i / 16 for i in range(17)]]
    fr.polyline(pts, col, 2, alpha)
    a, b = pts[-3], pts[-1]
    d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    for s in (1, -1):
        fr.line(b, (b[0] - ux * 10 - s * uy * 6, b[1] - uy * 10 + s * ux * 6), col, 2, alpha)


def instances(fr, alpha=1.0, shown=None, times=False, mark=(), dx=0, dy=0, box_alpha=None):
    """Selected clusters as boxes; members as instances (node@root); cross-cluster wires rose and drawn behind boxes."""
    shown = R["selected"] if shown is None else shown
    off = lambda p: (p[0] + dx, p[1] + dy)
    ba = box_alpha or (lambda r: 1.0)
    for e in R["instanceEdges"]:
        fr_r, to_r = e["from"].split("@")[1], e["to"].split("@")[1]
        if e["cost"] and fr_r in shown and to_r in shown:
            a = alpha * min(ba(fr_r), ba(to_r))
            fr.arrow(off(IPOS[e["from"]]), off(IPOS[e["to"]]), ROSE, 1.8, 0.75 * a, head=10, shorten=28)
    for root in shown:
        bx, by = BOXES[root]
        a = alpha * ba(root)
        if a <= 0:
            continue
        n = len(R["clusters"][root])
        fr.rect(bx + dx, by + dy, 34 + STEP * n, 104, fill=PANEL_BG, stroke=FAINT, width=1.4, alpha=a, r=12)
        fr.text(root, bx + dx + 10, by + dy - 10, 18, MUTED, a, role="mono")
        mem = R["clusters"][root]
        for u, v in EDGES:
            if u in mem and v in mem:
                arc(fr, off(IPOS[f"{u}@{root}"]), off(IPOS[f"{v}@{root}"]), "#7aa5a6", 0.8 * a, h=8 + 6 * abs(mem.index(v) - mem.index(u)))
        for m in mem:
            p = off(IPOS[f"{m}@{root}"])
            rep = COPIES.get(m, 1) > 1
            fr.dot(p, 26, NODE_BG, a)
            fr.ring(p, 26, GOLD if rep and (not mark or m in mark) else node_col(m), 2.4, a, dash=[5, 4] if rep else None)
            fr.text(m, p[0], p[1] + 9, 24, IVORY, a, role="serif", anchor="c")
            if times:
                fr.text(str(R["arrival"][f"{m}@{root}"]), p[0], p[1] + 50, 18, GOLD, a, role="mono", anchor="c")


# ====================================================================== popular film
KITCHEN = L("厨房 {}", "kitchen {}")
ONE, TWO = [["P", "X"], ["Y", "O"]], [["P"], ["X", "Y"], ["O"]]


def p_open(fr, c):
    x = lambda i: 450 + i * 340
    for i, n in enumerate(CHAIN):
        a = landed(c.T, INTRO_HITS, i)
        if a <= 0:
            continue
        if i:
            fr.arrow((x(i - 1), 470), (x(i), 470), "#7aa5a6", 2.4, a, head=14, shorten=46)
        fr.dot((x(i), 470), 42, NODE_BG, a)
        fr.ring((x(i), 470), 42, "#9fbcbc", 2.6, a)
        fr.text(n, x(i), 482, 32, IVORY, a, role="serif", anchor="c")
        fr.text(f"{i + 1}", x(i), 552, 26, GOLD, a * c.p(0, 1.0, 2.0), anchor="c", role="mono")
    if c.on(1):
        a = c.p(1)
        fr.text(L("一间厨房：两个人", "one kitchen: two cooks"), W / 2, 720, 28, MUTED, a, anchor="c", spacing=1)


def p_ask(fr, c):
    chain(fr, ONE, 470, 1.0, word=KITCHEN, cross_glow=0.4 * c.p(0))
    if c.on(0):
        fr.text(L("穿过院子：+3 分钟", "across the yard: +3 minutes"), W / 2, 300, 26, ROSE, c.p(0), anchor="c")
    if c.on(1):
        fr.text("7", W / 2, 760, 64, GOLD, c.p(1), anchor="c", role="mono", glow=0.3 * c.p(1))


def p_rule(fr, c):
    if not c.on(1):
        chain(fr, ONE, 470, 1 - c.p(0, 0.5) * 0.0, word=KITCHEN)
        fr.text("7", W / 2, 760, 64, GOLD, 1.0, anchor="c", role="mono")
    else:
        chain(fr, TWO, 470, c.p(1, 0.6), word=KITCHEN)
        fr.text("10", W / 2, 760, 64, ROSE, c.p(1), anchor="c", role="mono", glow=0.3 * c.p(1))
    if c.on(2):
        fr.text(L("快慢 = 最长那条路 + 3 × 跨院子的次数", "time = the longest route + 3 × the yard crossings"), W / 2, 830, 28, GOLD, c.p(2), anchor="c", role="serif")


def p_title(fr, c):
    title_assemble(fr, c, L("关键路径的代价", "The Cost of the Critical Path"), L("RAJARAMAN–WONG 延迟导向聚类", "RAJARAMAN–WONG DELAY-ORIENTED CLUSTERING"), "MODULE 09")


DAG_BOX = (330, 230, 1590, 760)


def p_dag(fr, c):
    a = c.p(0, 1.2)
    path = LONG if FILL1 and c.T >= FILL1[0] else (LONG if c.on(2) else ())
    dag(fr, DAG_BOX, a, path=path, focus=())
    cand_note(fr, a)
    if c.on(1):
        fr.text(L("三个起点（蓝）· 两道成品（红）· 每间厨房最多 4 人", "three starts (blue) · two finished dishes (rose) · up to 4 per kitchen"), W / 2, 830, 24, MUTED, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("最长：5 步", "the longest: 5 steps"), W / 2, 180, 30, GOLD, c.p(2), anchor="c", glow=0.3 * pulse(c.T, FILL1, 0.5))


def p_time(fr, c):
    early = ["a", "b", "c"] + (["d", "e", "f", "h"] if c.on(1) else []) + (["g"] if c.on(2) else [])
    cl = LABEL_EV["g"]["after"]["cluster"] if c.on(2) else ()
    dag(fr, DAG_BOX, 1.0, labels={n: LABELS[n] for n in early}, cluster=cl, focus=("g",) if c.on(2) else ())
    cand_note(fr)
    if not c.on(1):
        fr.text(L("金色数字：最早几分钟能到这里", "gold numbers: the earliest minute the dish can be here"), W / 2, 830, 26, GOLD, c.p(0), anchor="c")


def p_i(fr, c):
    cl = EI["after"]["cluster"]
    labels = {n: LABELS[n] for n in "abcdefgh"}
    stamp = FILL2 and c.T >= FILL2[0]
    if stamp or c.on(2):
        labels["i"] = 7
    dag(fr, DAG_BOX, 1.0, labels=labels, cluster=cl, focus=("i",), outside=("b",) if c.on(1) else ())
    cand_note(fr)
    if c.on(0) and not c.on(1):
        fr.text(L("i 和 g、e、c 挤进一间", "i shares a kitchen with g, e and c"), W / 2, 830, 26, TEAL, c.p(0), anchor="c")
    if c.on(1):
        fr.text(L("b 在院子外：4 + 3 = 7", "b is across the yard: 4 + 3 = 7"), W / 2, 830, 28, ROSE, c.p(1), anchor="c", role="mono",
                glow=0.3 * pulse(c.T, FILL2, 0.5))


def p_labels(fr, c):
    hits = []
    for t in PHRASE + [S["phrase"] + 1.6 * i for i in range(3)]:
        if not hits or t - hits[-1] >= 1.0:
            hits.append(t)
    hits = sorted(hits)[:3]
    order = ["j", "k", "l"]
    n_on = sum(1 for t in hits if c.T >= t)
    labels = {n: LABELS[n] for n in "abcdefghi"}
    for n in order[:n_on]:
        labels[n] = LABELS[n]
    focus = order[n_on - 1] if n_on else None
    dag(fr, DAG_BOX, 1.0, labels=labels, cluster=LABEL_EV[focus]["after"]["cluster"] if focus else (), focus=(focus,) if focus else (),
        lab_alpha=lambda n: (ease((c.T - hits[order.index(n)]) / 0.4) if n in order else 1.0))
    cand_note(fr)
    if c.on(2):
        fr.text(L("只是时间：厨房还没分", "only times: no kitchens yet"), W / 2, 830, 26, AMBER, c.p(2), anchor="c", role="serif")


def p_twins(fr, c):
    a = c.p(0, 1.0)
    instances(fr, a, shown=["k", "l"], mark=("g", "j"), dx=-200, dy=40)
    if c.on(1):
        fr.text(L("g、j 各做两份", "g and j: two of each"), 1500, 530, 30, GOLD, c.p(1), anchor="c", role="serif", glow=0.3 * c.p(1))
    cand_note(fr, a)


def p_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("同一道工序，为什么做两份？", "Why make the same step twice?"), W / 2, 500, 52, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def p_back(fr, c):
    # the two outputs open at once, then the six kitchens they need land one by one within the first caption
    seq = R["selected"]
    times = [0.3, 0.3] + [1.4 + 0.6 * i for i in range(6)]
    ba = lambda r: ease((c.t - times[seq.index(r)]) / 0.4)
    instances(fr, 1.0, box_alpha=ba, times=c.on(2))
    if c.on(1):
        fr.text(L("8 间厨房 · 20 个人 · 12 道工序", "8 kitchens · 20 cooks · 12 steps"), 1640, 200, 26, GOLD, c.p(1), anchor="r", role="mono")
    if c.on(2):
        fr.text(L("两道成品：第 8 分钟", "both dishes: minute 8"), 1500, 760, 30, TEAL, c.p(2), anchor="c", glow=0.3 * pulse(c.T, FILL3, 0.5))
    cand_note(fr)


def p_compare(fr, c):
    panel(fr, 220, 260, 680, 420, c.p(0), L("可以做两份", "COPIES ALLOWED"))
    panel(fr, 1020, 260, 680, 420, c.p(0), L("不许做两份 · 试遍所有分法", "NO COPIES · EVERY SPLIT TRIED"))
    fr.text(str(R["maxDelay"]), 560, 470, 120, TEAL, c.p(0), anchor="c", role="mono", glow=0.3)
    fr.text(L(f"{R['instanceCount']} 个人", f"{R['instanceCount']} cooks"), 560, 590, 30, IVORY, c.p(0), anchor="c")
    if c.on(0):
        fr.text(str(NR["bestMaxDelay"]), 1360, 470, 120, ROSE, c.p(0, 1.0, 0.8), anchor="c", role="mono", glow=0.3)
        fr.text(L(f"{R['logicalCount']} 个人", f"{R['logicalCount']} cooks"), 1360, 590, 30, IVORY, c.p(0, 1.0, 0.8), anchor="c")
    if c.on(1):
        fr.text(L("多 8 个人手，快 2 分钟", "8 more hands, 2 minutes faster"), W / 2, 780, 32, GOLD, c.p(1), anchor="c", role="serif")
    cand_note(fr, c.p(0))


def p_chip(fr, c):
    a = c.p(0, 0.8)
    substrate(fr, 0.6 * a)
    regions = [(300, 260, 560, 440), (980, 260, 640, 440)]
    for i, (x, y, w, h) in enumerate(regions):
        fr.rect(x, y, w, h, stroke=TEAL if i == 0 else BLUE, width=1.6, alpha=0.8 * a, r=8, dash=[10, 7])
    for i in range(6):
        for j in range(4):
            fr.rect(340 + i * 84, 300 + j * 100, 50, 36, fill=NODE_BG, stroke=TEAL, width=1.2, alpha=a, r=3)
            fr.rect(1020 + i * 96, 300 + j * 100, 50, 36, fill=NODE_BG, stroke=BLUE, width=1.2, alpha=a, r=3)
    go = clamp(c.since(0) / 2.4)
    p, q = (790, 418), (1045, 418)
    fr.line(p, ((1 - go) * p[0] + go * q[0], p[1]), ROSE, 3, a, glow=0.5 * a)
    fr.text(L("跨出区域：慢", "leaving the region: slow"), (p[0] + q[0]) / 2, 390, 22, ROSE, a * c.p(0, 0.6, 1.0), anchor="c")


def p_outro(fr, c):
    lines = [(L("快慢看最长的那条路", "Speed is set by the longest route"), TEAL, 0),
             (L("跨一次边界，多等 D", "Each crossing adds D"), ROSE, 1),
             (L("做两份能更快，也更占地方", "Copies buy speed and cost area"), GOLD, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("八个模块，八种分组的取舍", "Eight modules, eight ways to trade"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        dag(fr, (200, 260, 1000, 720), a, labels=LABELS)
        fr.text(L("单步看标签 · 看恢复出的实例 · 改 D 与容量", "step through the labels · see the recovered instances · change D and capacity"), 1440, 500, 24, GOLD, a, anchor="c")
        cand_note(fr, a)
    else:
        credits(fr, c, [(L("关键路径的代价", "The Cost of the Critical Path"), GOLD, 44),
                        (L("Learning Clustering · Module 09 · Rajaraman–Wong 延迟导向聚类", "Learning Clustering · Module 09 · Rajaraman–Wong delay-oriented clustering"), IVORY, 24),
                        (L("原作 muranfei（Issue #8）· 12 节点算例由原作影片复原，属候选数据", "Original work by muranfei (Issue #8) · the 12-node example is reconstructed from the original film: candidate data"), MUTED, 20),
                        (L("所有数值由本课程引擎 site/engines/rw.js 计算", "Every value is computed by this course's engine, site/engines/rw.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("关键路径的代价", "The Cost of the Critical Path"), None, BRAND, poster_at=60.0, music=TRACK, seed=9,
    why=L("一道菜经过几位厨师，每人一分钟，端去另一间厨房要多走三分钟：快慢看最长的那条路跨了几次院子。十二道工序的大菜逐个得到“最早几分钟”；两间厨房都要 g 和 j，就各做一份；从成品往回推，开出八间厨房、二十个人；不许做两份时，最快只有 10。",
          "A dish passes through cooks a minute each, and carrying it to another kitchen costs three more: speed depends on how often the longest route crosses the yard. A twelve-step banquet gets its earliest minutes one by one; two kitchens both need g and j, so each makes its own; working back from the dishes opens eight kitchens with twenty cooks; without copies the best is 10."),
    scenes=[
        Scene("p-open", p_open, [Beat(L("一道菜要经过四个人，每人一分钟。", "A dish passes through four cooks, a minute each."), 4.6),
                                 Beat(L("一间厨房只放得下两个人。", "A kitchen fits only two cooks."), 4.0)],
              chapter=L("序 · 一道菜", "PROLOGUE · ONE DISH"), until=S["intro_end"]),
        Scene("p-ask", p_ask, [Beat(L("穿过院子去另一间：多 3 分钟。", "Across the yard to the other kitchen: 3 more minutes."), 3.6),
                               Beat(L("这样分：7。", "This split: 7."), 2.0)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("换个分法，也都放得下。", "Another split, and everyone still fits."), 3.4),
                                 Beat(L("可是跨了两次院子：10 分钟。", "But it crosses the yard twice: 10 minutes."), 3.6),
                                 Beat(L("快慢只看最长那条路跨了几次院子。", "Speed depends on how often the longest route crosses the yard."), 5.0)],
              until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-dag", p_dag, [Beat(L("一桌大菜：十二道工序，三个起点，两道成品。", "A banquet: twelve steps, three starts, two finished dishes."), 4.6),
                               Beat(L("每间厨房最多四个人，穿院子还是 3 分钟。", "Each kitchen holds four; crossing the yard is still 3 minutes."), 4.4),
                               Beat(L("最长的一条路：五步。", "The longest route: five steps."), 3.0)],
              chapter=L("一 · 最早几分钟", "I · THE EARLIEST MINUTE"), until=S["fill1_end"]),
        Scene("p-time", p_time, [Beat(L("每道工序记一个数：最早几分钟到。", "Each step gets a number: its earliest minute."), 4.0),
                                 Beat(L("起点是 1，往后加。", "The starts are 1; then it adds up."), 2.8),
                                 Beat(L("g 和前面的都在一间：3。", "g shares a kitchen with all before it: 3."), 3.4)],
              until=S["accent"]),
        Scene("p-i", p_i, [Beat(L("i 前面七道工序，只剩三个位置。", "Seven steps before i, room for three."), 3.6),
                           Beat(L("b 在院子外：4 + 3 = 7。", "b is across the yard: 4 + 3 = 7."), 3.2),
                           Beat(L("i 最早第 7 分钟。", "i's earliest: minute 7."), 2.6)],
              until=74.0),
        Scene("p-labels", p_labels, [Beat(L("j 也是 7。", "j is 7 too."), 2.6),
                                     Beat(L("两道成品：都是 8。", "Both finished dishes: 8."), 3.4),
                                     Beat(L("这还只是时间，厨房还没分。", "These are only times; no kitchens yet."), 3.6)],
              until=89.0),
        Scene("p-twins", p_twins, [Beat(L("k 的厨房要 g 和 j，l 的厨房也要。", "k's kitchen needs g and j; so does l's."), 4.0),
                                   Beat(L("那就各做一份。", "So each makes its own."), 2.6)],
              chapter=L("二 · 做两份", "II · MAKE TWO"), until=S["breath"]),
        Scene("p-breath", p_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("p-back", p_back, [Beat(L("从成品往回推：缺什么，就再开一间厨房。", "Work back from the dishes: whatever is missing gets its own kitchen."), 5.0),
                                 Beat(L("八间厨房，二十个人，做十二道工序。", "Eight kitchens, twenty cooks, twelve steps."), 4.2),
                                 Beat(L("两道成品都在第 8 分钟出来。", "Both dishes come out at minute 8."), 3.4)],
              until=S["fill3_end"]),
        Scene("p-compare", p_compare, [Beat(L("不许做两份呢？试遍所有分法，最快也要 10。", "No copies? Try every split: the best is 10."), 4.6),
                                       Beat(L("多八个人手，快了两分钟。", "Eight more hands, two minutes faster."), 3.4),
                                       Beat(L("快，是用地方换来的。", "The speed is paid for in space."), 3.0)],
              chapter=L("三 · 人手换时间", "III · HANDS FOR TIME"), until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片上：信号跨出一块区域，就要多等。", "On a chip: a signal that leaves its region waits longer."), 5.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("快慢看最长的那条路。", "Speed is set by the longest route."), 6.0),
                                   Beat(L("每跨一次边界，就多等 D。", "Each boundary crossed adds D."), 6.0),
                                   Beat(L("复制能换来速度，也要占面积。", "Copies buy speed, and cost area."), 7.0),
                                   Beat(L("这是最后一章：回到首页，对比八种分组。", "The last module: compare all eight on the home page."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，单步看标签和恢复出的实例。", "In the lab below, step through the labels and the recovered instances."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("Rajaraman–Wong 延迟导向聚类", "Rajaraman–Wong Clustering"), L("RW  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 09")


def k_goal(fr, c):
    chain(fr, ONE, 360, c.p(0), word=L("簇 {}", "cluster {}"), unit="t")
    fr.text(L("跨界 1 次：7", "1 crossing: 7"), 1592, 372, 26, GOLD, c.p(0), role="mono")
    if c.on(1):
        chain(fr, TWO, 680, c.p(1), word=L("簇 {}", "cluster {}"), unit="t")
        fr.text(L("跨界 2 次：10", "2 crossings: 10"), 1592, 692, 26, ROSE, c.p(1), role="mono")
    if c.on(2):
        fr.text(L("目标：PI → PO 的最大延迟，不是 cut", "the goal: the largest PI → PO delay, not the cut"), W / 2, 200, 28, GOLD, c.p(2), anchor="c", role="serif")


def k_model(fr, c):
    dag(fr, (180, 260, 900, 740), c.p(0, 1.0), r=26, name_size=24)
    cand_note(fr, c.p(0))
    panel(fr, 1000, 230, 740, 560, c.p(0), L("RW 的模型", "THE RW MODEL"))
    items = [(L("组合电路 DAG：PI 蓝，PO 红", "A combinational DAG: PIs blue, POs rose"), IVORY),
             (L("节点延迟 δ(v)，这里 δ = 1", "Node delay δ(v), here δ = 1"), IVORY),
             (L("簇内连线 0，跨簇连线 D = 3", "Wires inside a cluster 0, between clusters D = 3"), ROSE),
             (L("簇容量 M = 4", "Cluster capacity M = 4"), IVORY),
             (L("允许复制逻辑节点", "Logic nodes may be replicated"), GOLD)]
    y = 330
    for i, (s, col) in enumerate(items):
        if c.on(min(i, 3) if i < 4 else 4):
            y += fr.paragraph(s, 1040, y, 26, 660, col, c.p(min(i, 3) if i < 4 else 4)) + 26


def k_delta(fr, c):
    dag(fr, (180, 260, 1100, 760), 1.0, path=LONG if c.on(1) else (), labels={p: 1 for p in PIS} if c.on(2) else None, r=28)
    cand_note(fr)
    panel(fr, 1220, 260, 520, 420, c.p(0), L("初始化", "INITIALISE"))
    fr.paragraph(L("Δ(x, v)：x 到 v 的最长节点延迟，计 v 不计 x", "Δ(x, v): the longest node delay from x to v, counting v, not x"), 1260, 350, 24, 440, IVORY, c.p(0))
    if c.on(1):
        fr.text(L(f"Δ(b, k) = {R['delta']['b']['k']}", f"Δ(b, k) = {R['delta']['b']['k']}"), 1260, 500, 32, GOLD, c.p(1), role="mono")
        fr.text("b → e → g → i → k", 1260, 550, 24, MUTED, c.p(1), role="mono")
    if c.on(2):
        fr.text(L("PI：l = δ = 1", "PIs: l = δ = 1"), 1260, 630, 28, BLUE, c.p(2), role="mono")


def k_label(fr, c):
    cl = EI["after"]["cluster"] if c.on(2) else ()
    labels = {n: LABELS[n] for n in "abcdefgh"}
    if c.on(3):
        labels["i"] = 7
    dag(fr, (150, 280, 860, 740), 1.0, labels=labels, cluster=cl, focus=("i",), outside=("b",) if c.on(3) else (), r=26, name_size=24)
    cand_note(fr)
    rows = [[L("祖先 x", "Ancestor x"), "l(x)", "Δ(x,i)", L("得分", "Score"), ""]]
    for x in EI["candidates"]:
        rows.append([x["x"], str(x["l"]), str(x["delta"]), str(x["score"]), (L("簇内", "inside") if x["inCluster"] else L("簇外", "outside")) if c.on(2) else ""])
    shown = rows[:1 + (len(EI["candidates"]) if c.on(1) else 0)]
    colors = {}
    if c.on(2):
        colors = {(i + 1, j): TEAL for i, x in enumerate(EI["candidates"]) if x["inCluster"] for j in range(5)}
    table(fr, 1000, 270, [170, 100, 130, 110, 120], [[tr(x) for x in r] for r in shown], c.p(0), size=26, lh=50, colors=colors)
    if c.on(3):
        fr.text(L("l1 = 4（簇内 PI c）  l2 = 4 + 3 = 7（簇外 b）", "l1 = 4 (PI c inside)   l2 = 4 + 3 = 7 (b outside)"), 1000, 720, 24, IVORY, c.p(3), role="mono")
    if c.on(4):
        fr.text(L("l(i) = max(l1, l2) = 7", "l(i) = max(l1, l2) = 7"), 1000, 790, 32, GOLD, c.p(4), role="mono", glow=0.2)


def k_back(fr, c):
    n = 2 if not c.on(1) else (6 if not c.on(2) else 8)
    instances(fr, 1.0, shown=R["selected"][:n], times=c.on(3), dx=-60, dy=10)
    cand_note(fr)
    if c.on(2):
        fr.text(L(f"{len(R['selected'])} 簇 · {R['instanceCount']} 实例", f"{len(R['selected'])} clusters · {R['instanceCount']} instances"), 1760, 220, 28, GOLD, c.p(2), anchor="r", role="mono")
        fr.text(L("金色虚线圈：复制的节点", "dashed gold: replicated nodes"), 1760, 262, 20, MUTED, c.p(2), anchor="r")
    if c.on(3):
        fr.text(L("输出到达 8 = 标签", "outputs arrive at 8 = the labels"), 1500, 800, 28, TEAL, c.p(3), anchor="c", role="mono")


def k_take(fr, c):
    items = [(L("目标是最大路径延迟：每跨一次簇加 D", "The goal is the largest path delay: each crossing adds D"), TEAL),
             (L("标签 l(v) 是时间：l = max(l1, l2)", "The label l(v) is a time: l = max(l1, l2)"), GOLD),
             (L("从输出倒推簇；逻辑节点与实例分开", "Recover clusters from the outputs; logic nodes apart from instances"), AMBER),
             (L("复制换来延迟，也付出面积", "Replication buys delay and costs area"), ROSE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 28, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：延迟、标签、恢复", "The essentials"), None, BRAND, poster_at=60.0, music="score:steady", seed=29,
    why=L("只讲必须掌握的：目标从 cut 换成延迟、RW 的模型、候选 DAG 上的 Δ、节点 i 的标签（l1、l2），以及从输出倒推得到 8 簇、20 实例、输出 8。",
          "Only what you must know: the goal changes from cut to delay, the RW model, Δ on the candidate DAG, the label of i (l1, l2), and the recovery from the outputs to 8 clusters, 20 instances and output 8."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-goal", k_goal, [Beat(L("一条链，每个节点延迟 1，跨簇加 D = 3。分成两簇：跨界一次，延迟 7。", "A chain, each node delay 1, crossing clusters adds D = 3. Two clusters: one crossing, delay 7."), 5.6),
                                   Beat(L("换一种分法，跨界两次：延迟 10。", "Another split crosses twice: delay 10."), 3.4),
                                   Beat(L("目标变了：最长路径的延迟，而不是 cut。", "The goal has changed: the longest path's delay, not the cut."), 4.0)],
              chapter=L("目标", "THE GOAL")),
        Scene("k02-model", k_model, [Beat(L("RW 的模型：组合电路是一张有向无环图。", "The RW model: a combinational circuit is a directed acyclic graph."), 4.0),
                                     Beat(L("每个节点有延迟 δ。", "Each node has a delay δ."), 2.4),
                                     Beat(L("簇内连线不加延迟，跨簇连线固定加 D。", "Wires inside a cluster add nothing; wires between clusters add a fixed D."), 4.2),
                                     Beat(L("每个簇有容量 M。", "Each cluster has a capacity M."), 2.4),
                                     Beat(L("而且允许复制节点：这是最优性的前提。", "And nodes may be replicated: the premise of the optimality result."), 4.0)],
              chapter=L("模型", "THE MODEL")),
        Scene("k03-delta", k_delta, [Beat(L("候选 DAG 由原作影片复原：12 个节点，PI a、b、c，PO k、l。", "The candidate DAG, reconstructed from the original film: 12 nodes, PIs a, b, c, POs k, l."), 5.0),
                                     Beat(L("Δ(b, k) = 4：沿 b、e、g、i、k，计终点不计起点。", "Δ(b, k) = 4: along b, e, g, i, k, counting the end, not the start."), 4.6),
                                     Beat(L("PI 的标签就是自己的延迟：1。", "A PI's label is its own delay: 1."), 3.0)],
              chapter=L("初始化", "INITIALISE")),
        Scene("k04-label", k_label, [Beat(L("按拓扑序打标签。看节点 i。", "Label in topological order. Take node i."), 3.0),
                                     Beat(L("每个祖先的得分：l(x) + Δ(x, i)。", "Each ancestor's score: l(x) + Δ(x, i)."), 3.4),
                                     Beat(L("容量 4：取得分最高的 g、e、c；平票时拓扑序靠后的优先，这是假设。", "Capacity 4: take the top scores g, e, c; ties go to the later node in topological order, an assumption."), 5.6),
                                     Beat(L("簇内 PI c 给 l1 = 4；簇外最大的 b 给 l2 = 4 + 3 = 7。", "PI c inside gives l1 = 4; b, the largest outside, gives l2 = 4 + 3 = 7."), 5.0),
                                     Beat(L("l(i) = 7。标签是时间。", "l(i) = 7. The label is a time."), 3.0)],
              chapter=L("标记", "LABEL")),
        Scene("k05-reconstruct", k_back, [Beat(L("从输出倒推：先取 k 和 l 的候选簇。", "Recover from the outputs: first the candidate clusters of k and l."), 3.8),
                                          Beat(L("簇外的输入 d、e、f、h 成为新的簇根。", "The outside inputs d, e, f, h become new roots."), 3.6),
                                          Beat(L("b、c 各自成簇：一共 8 簇、20 个实例。", "b and c form their own: 8 clusters, 20 instances."), 4.0),
                                          Beat(L("两个输出都在 8 到达，正好等于标签。", "Both outputs arrive at 8, exactly the labels."), 3.6)],
              chapter=L("恢复", "RECOVER")),
        Scene("k06-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("延迟看最长路径；标签是时间；", "Delay follows the longest path; labels are times;"), 3.6),
                                   Beat(L("从输出倒推，实例与逻辑节点分开；复制有面积代价。", "recover from the outputs, instances apart from logic nodes; replication costs area."), 4.2),
                                   Beat(L("下面的实验里，单步看标记与恢复。", "In the lab below, step through labelling and recovery."), 3.4)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def a_title(fr, c):
    title_card(fr, L("Rajaraman–Wong 延迟导向聚类", "Rajaraman–Wong Clustering"), L("进阶：标签、实例与边界", "IN DEPTH: LABELS, INSTANCES, LIMITS"), c.p(0, 1.2), kicker="MODULE 09")


A_ORDER = ["d", "e", "f", "g", "h", "i", "j", "k", "l"]


def a_labels(fr, c):
    k = min(len(A_ORDER), int(c.since(1) / 1.15) + 1) if c.on(1) else 0
    done = A_ORDER[:k]
    cur = done[-1] if done else None
    labels = {p: 1 for p in PIS} | {n: LABELS[n] for n in done}
    dag(fr, (160, 260, 880, 740), 1.0, labels=labels, cluster=LABEL_EV[cur]["after"]["cluster"] if cur else (), focus=(cur,) if cur else (), r=26, name_size=24)
    cand_note(fr)
    rows = [[L("节点", "Node"), L("候选簇", "Candidate cluster"), "l1", "l2", "l"]]
    for n in done:
        e = LABEL_EV[n]
        rows.append([n, "{" + ", ".join(e["after"]["cluster"]) + "}", str(e["metrics"]["l1"]), str(e["metrics"]["l2"]), str(e["metrics"]["label"])])
    table(fr, 1000, 240, [100, 300, 80, 80, 80], [[tr(x) for x in r] for r in rows], c.p(0), size=24, lh=46,
          colors={(i + 1, 4): GOLD for i in range(len(done))})
    if c.on(2):
        fr.text(L("平票：拓扑序靠后者优先（假设）", "ties: the later node in topological order (assumed)"), 1000, 760, 22, LILAC, c.p(2))


def a_instances(fr, c):
    instances(fr, 1.0, mark=("b",) if c.on(1) else (), dx=-60, dy=0)
    cand_note(fr)
    if c.on(1):
        ib = [i["instanceId"] for i in R["instances"] if i["logicalId"] == "b"]
        fr.text(tr(L("b 的实例：", "instances of b: ")) + "  ".join(ib), 1760, 220, 26, GOLD, c.p(1), anchor="r", role="mono")
    if c.on(2):
        fr.text(L("“节点 → 簇”的映射只能写一个簇", "a “node → cluster” map holds one cluster each"), 1500, 780, 24, ROSE, c.p(2), anchor="c")
    if c.on(3):
        fr.text(L("簇外输入 u 总是来自 u@u，代价 D", "an outside input u always comes from u@u, at cost D"), 1500, 830, 24, IVORY, c.p(3), anchor="c")


def a_compare(fr, c):
    rows = [["", L("允许复制（RW）", "Replication (RW)"), L("禁止复制（穷举）", "No replication (exhaustive)")],
            [L("最大延迟", "Largest delay"), str(R["maxDelay"]), str(NR["bestMaxDelay"])],
            [L("实例 / 面积", "Instances / area"), str(R["instanceCount"]), str(R["logicalCount"])]]
    table(fr, 300, 300, [360, 480, 520], [[tr(x) for x in r] for r in rows], c.p(0), size=32, lh=84,
          colors={(1, 1): TEAL, (1, 2): ROSE} if c.on(1) else {})
    if c.on(1):
        fr.text(tr(L("不复制的最好分组之一：", "one of the best groupings without copies: ")) + " | ".join("".join(g) for g in NR_BEST), W / 2, 620, 26, IVORY, c.p(1), anchor="c", role="mono")
    if c.on(2):
        fr.text(L("多 8 个实例，换 2 个单位延迟", "8 more instances buy 2 units of delay"), W / 2, 700, 30, GOLD, c.p(2), anchor="c", role="serif")
    cand_note(fr, c.p(0))


def a_scope(fr, c):
    items = [(L("论文（DAC 1993；IEEE TCAD 1995）：在模型内，允许复制时最大延迟最优", "The paper (DAC 1993; IEEE TCAD 1995): within its model, with replication, the largest delay is optimal"), TEAL),
             (L("模型：DAG、节点延迟、簇内 0、跨簇固定 D、容量", "The model: a DAG, node delays, 0 inside, a fixed D between, capacity"), IVORY),
             (L("禁止复制、或还要面积 / 引脚 / 功耗最优：结论不适用", "No replication, or also area / pins / power: the result does not apply"), ROSE),
             (L("本课程的测试检查实现一致、实例合法：不证明最优", "This course's tests check consistency and legal instances: they prove nothing optimal"), AMBER)]
    y = 230
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            fr.rect(200, y, 1520, 120, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 250, y + 70, 28, col, a, role="mono")
            fr.paragraph(s, 330, y + 50, 28, 1340, IVORY, a, lh=1.35)
        y += 140


def a_candidate(fr, c):
    dag(fr, (160, 260, 880, 740), c.p(0, 1.0), r=26, name_size=24)
    panel(fr, 1000, 230, 740, 560, c.p(0), L("哪些是候选", "WHAT IS CANDIDATE"))
    lines = [(L("边表：由原作影片 405 秒处的图复原（15 条边）", "The edges: reconstructed from the figure at 405 s of the original film (15 edges)"), IVORY, 0),
             (L("用 438 秒处的 Δ 表逐项核对，一致", "Checked entry by entry against the Δ table at 438 s: they agree"), TEAL, 1),
             (L("平票“逆拓扑序优先”：假设，它重现了 8 簇、20 实例、输出 8", "The tie rule, reverse topological order: an assumption that reproduces 8 clusters, 20 instances, output 8"), LILAC, 2),
             (L("教师目录的 Lab 09 是 Multilevel：本模块不替代它，对应待确认", "Lab 09 in the teacher's catalogue is Multilevel: this module does not replace it; the mapping awaits confirmation"), AMBER, 3)]
    y = 320
    for s, col, k in lines:
        if c.on(k):
            y += fr.paragraph(s, 1040, y, 24, 660, col, c.p(k)) + 24


def a_summary(fr, c):
    items = [(L("标签是时间：l = max(l1, l2)，按拓扑序", "Labels are times: l = max(l1, l2), in topological order"), GOLD),
             (L("恢复从输出倒推：簇外输入成为新簇根", "Recovery works back from the outputs: outside inputs become roots"), TEAL),
             (L("实例 m@r 与逻辑节点分开；每个实例输入完整", "Instances m@r apart from logic nodes; each with complete inputs"), AMBER),
             (L("复制：延迟 8 对 10，实例 20 对 12", "Replication: delay 8 against 10, instances 20 against 12"), ROSE),
             (L("最优性只在论文模型内；测试不证明它", "Optimality only within the paper's model; the tests don't prove it"), TEAL),
             (L("候选图与平票规则待原作者确认", "The candidate graph and tie rule await the author's confirmation"), LILAC)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：标签、实例与边界", "In depth: labels, instances, limits"), None, BRAND, poster_at=40.0, music="score:calm", seed=41,
    why=L("全部标签与候选簇、假设的平票规则、逻辑节点与实例的区分、穷举得到的不复制对照、最优性结论覆盖什么不覆盖什么，以及本章哪些是待确认的候选数据。",
          "Every label with its candidate cluster and the assumed tie rule, logic nodes versus instances, the exhaustive comparison without replication, what the optimality result does and does not cover, and what in this chapter is candidate data awaiting confirmation."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-labels", a_labels, [Beat(L("把标记阶段完整走一遍。", "Walk the whole labelling phase."), 2.6),
                                       Beat(L("d、e、f、h 是 2，g 是 3：祖先都放得进簇；i、j 是 7；k、l 是 8。", "d, e, f, h are 2, g is 3: every ancestor fits; i and j are 7; k and l are 8."), 10.4),
                                       Beat(L("得分相同时，本课程让拓扑序靠后的祖先优先，这是假设。", "On equal scores this course prefers the later ancestor in topological order, an assumption."), 4.6)],
              chapter=L("一 · 全部标签", "I · EVERY LABEL")),
        Scene("a02-instances", a_instances, [Beat(L("恢复出的 8 个簇里，同一个逻辑节点可以出现多次。", "In the 8 recovered clusters, one logic node can appear several times."), 4.2),
                                             Beat(L("b 有三个实例：b@b、b@d、b@e。", "b has three instances: b@b, b@d, b@e."), 3.6),
                                             Beat(L("所以不能用“节点 → 簇”的映射表示结果。", "So a “node → cluster” map cannot represent the result."), 3.6),
                                             Beat(L("每个实例的输入必须完整：簇内取，或从簇根 u@u 跨簇取。", "Each instance needs complete inputs: from inside, or across from the root u@u."), 4.8)],
              chapter=L("二 · 逻辑节点与实例", "II · LOGIC NODES AND INSTANCES")),
        Scene("a03-compare", a_compare, [Beat(L("复制换来了多少？", "What does replication buy?"), 2.4),
                                         Beat(L("禁止复制时，穷举所有容量合法的分组，最好的最大延迟是 10。", "Without replication, exhaustive search over every capacity-legal grouping gives a best largest delay of 10."), 5.2),
                                         Beat(L("RW 用 8 个额外实例，把它降到 8。", "RW brings it to 8 with 8 extra instances."), 3.4)],
              chapter=L("三 · 复制的代价", "III · THE COST OF COPIES")),
        Scene("a04-scope", a_scope, [Beat(L("最优性来自论文，只在它的模型里成立。", "The optimality comes from the paper and holds only within its model."), 3.8),
                                     Beat(L("模型：DAG、节点延迟、簇内 0、跨簇固定 D、容量，并允许复制。", "The model: a DAG, node delays, 0 inside, a fixed D between, capacity, and replication."), 5.0),
                                     Beat(L("禁止复制，或还要顾及面积、引脚、功耗，就不能沿用。", "Forbid replication, or also weigh area, pins or power, and it no longer applies."), 4.6),
                                     Beat(L("本课程的测试只检查实现一致与实例合法，不证明最优。", "This course's tests only check consistency and legal instances; they prove nothing optimal."), 4.6)],
              chapter=L("四 · 结论的边界", "IV · THE LIMITS OF THE RESULT")),
        Scene("a05-candidate", a_candidate, [Beat(L("这张 12 节点图来自原作影片的画面。", "This 12-node graph comes from frames of the original film."), 3.6),
                                             Beat(L("影片里的 Δ 表与复原的边表逐项一致。", "The film's Δ table agrees with the reconstructed edges entry by entry."), 3.8),
                                             Beat(L("平票规则是假设；它重现了原作的结果，但仍待原作者确认。", "The tie rule is an assumption; it reproduces the original result, but awaits the author's confirmation."), 5.0),
                                             Beat(L("另外，本模块与教师目录 Lab 09（Multilevel）的对应也待确认。", "And this module's place against Lab 09 (Multilevel) in the teacher's catalogue awaits confirmation."), 5.0)],
              chapter=L("五 · 候选数据", "V · CANDIDATE DATA")),
        Scene("a06-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("回到首页的综合对比，看八个模块各在做什么。", "Return to the comparison on the home page to see what all eight modules do."), 3.6)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
