"""Homepage · the introduction film: clustering as the common background of all eight modules.

  intro     popular science, cut to "We Never (Remix)": a wedding seating plan (you are already clustering), what
            clustering is, why it matters on a chip, the cut, why trying every split is hopeless, and a short tour of
            the three families of methods in this course (score and merge; let groups emerge; improve a grouping),
            plus the delay-driven last module.

The five friends are the course graph G01 (site/data/m07-kernighan-lin/traces.json); the chip is the fictional
24-cell circuit and its label-propagation result (site/data/m05-label-propagation/traces.json). The seating plan is
an illustration drawn from a fixed random graph, not course data.
"""
import json
import math
from itertools import product
from pathlib import Path

import numpy as np

from cine import (W, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, HUES, clamp, ease, lerp, lerp2, graph, fit, badge, note, substrate, count_hits, pulse)
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
G01 = json.loads((ROOT / "site/data/m07-kernighan-lin/traces.json").read_text())["g01"]
LP = json.loads((ROOT / "site/data/m05-label-propagation/traces.json").read_text())
CIRC = LP["circuit"]["graph"]
CRUN = LP["circuit"]["run"]["result"]
BRAND = L("Learning Clustering · 导论", "Learning Clustering · Introduction")

FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
E5 = [(FR[u], FR[v], w) for u, v, w in G01["edges"]]
P5RAW = {FR[k]: tuple(v) for k, v in G01["positions"].items()}


def cut5(groups):
    side = {FR[n]: i for i, g in enumerate(groups) for n in g}
    return sum(w for u, v, w in E5 if side[u] != side[v])


def splits(n):
    """Ways to split n labelled items into two non-empty unordered groups."""
    return (2 ** n - 2) // 2


# facts the captions state
assert cut5(["ABC", "DE"]) == 3 and cut5(["AE", "BCD"]) == 12
assert splits(5) == 15 and len(str(splits(100))) == 30
assert CRUN["cut"] == 2 and len(set(CRUN["labels"].values())) == 3
assert len(list(p for p in product((0, 1), repeat=5) if 0 < sum(p) < 5)) // 2 == 15

MODS = [("M02", L("亲和度指标", "Affinity metrics"), 0), ("M03", L("贪心成对合并", "Greedy pair merge"), 0),
        ("M04", L("容量约束凝聚聚类", "Size-constrained merging"), 0), ("M05", L("标签传播", "Label propagation"), 1),
        ("M06", L("谱二分", "Spectral bisection"), 1), ("M07", L("Kernighan–Lin 改进", "Kernighan–Lin"), 2),
        ("M08", L("Fiduccia–Mattheyses 改进", "Fiduccia–Mattheyses"), 2), ("M09", L("Rajaraman–Wong 延迟导向", "Rajaraman–Wong"), 3)]
FAM = [(L("打分与合并", "SCORE AND MERGE"), TEAL), (L("让分组长出来", "LET GROUPS EMERGE"), BLUE),
       (L("改进已有分组", "IMPROVE A GROUPING"), GOLD), (L("目标换成速度", "AIM FOR SPEED"), ROSE)]


# ---------------------------------------------------------------- the seating plan
def _guests(seed=12):
    rng = np.random.RandomState(seed)
    n, k = 30, 3
    grp = [i // 10 for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.rand() < (0.42 if grp[i] == grp[j] else 0.035):
                edges.append((i, j))
    start = []
    while len(start) < n:
        p = (rng.uniform(300, 1620), rng.uniform(230, 780))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) > 70 for q in start):
            start.append(p)
    tables = [(420, 500), (960, 500), (1500, 500)]
    end = []
    for i in range(n):
        g, s = grp[i], i % 10
        t = 2 * math.pi * s / 10 - math.pi / 2
        end.append((tables[g][0] + 135 * math.cos(t), tables[g][1] + 135 * math.sin(t)))
    return grp, edges, start, end, tables


GRP, GEDGES, GSTART, GEND, TABLES = _guests()
GCOL = [TEAL, GOLD, BLUE]
CROSS = sum(1 for i, j in GEDGES if GRP[i] != GRP[j])


def seating(fr, c, k_move=0.0, halo=0.0, tables=0.0):
    T = c.T
    k = ease(k_move)
    pos = [lerp2(a, b, k) for a, b in zip(GSTART, GEND)]
    for (x, y) in TABLES:
        if tables > 0:
            fr.dot((x, y), 80, PANEL_BG, 0.9 * tables)
            fr.ring((x, y), 80, FAINT, 1.6, tables)
    for i, j in GEDGES:
        a = min(landed(T, INTRO_HITS, i % 6), landed(T, INTRO_HITS, j % 6))
        if a <= 0:
            continue
        same = GRP[i] == GRP[j]
        col = (GCOL[GRP[i]] if same else ROSE) if k > 0.5 else DIM
        fr.line(pos[i], pos[j], col, 1.4 if same else 1.8, a * (0.45 if same or k <= 0.5 else 0.8), glow=0.3 * a * (not same and k > 0.5))
    for i, p in enumerate(pos):
        a = landed(T, INTRO_HITS, i % 6)
        if a <= 0:
            continue
        col = GCOL[GRP[i]] if k > 0.5 else "#9fbcbc"
        fr.dot(p, 18, NODE_BG, a)
        fr.ring(p, 18, col, 2.4, a)
    if halo > 0:
        for g, (x, y) in enumerate(TABLES):
            fr.ring((x, y), 178, GCOL[g], 1.6, 0.6 * halo, dash=[8, 8])
        fr.text(L("组内：联系紧", "inside: tightly linked"), 960, 790, 26, TEAL, halo, anchor="c", role="serif")
        fr.text(L(f"组间：只有 {CROSS} 条", f"between: only {CROSS} links"), 960, 830, 26, ROSE, halo, anchor="c", role="serif")


def h_seat(fr, c):
    seating(fr, c, tables=landed(c.T, INTRO_HITS, 0))


def h_seat2(fr, c):
    seating(fr, c, k_move=clamp((c.T - S["intro_end"] - 0.3) / 3.2), tables=1.0)


def h_what(fr, c):
    seating(fr, c, k_move=1.0, halo=c.p(0, 1.0), tables=1.0)


def h_title(fr, c):
    title_assemble(fr, c, L("连接与分组", "Connect & Group"), L("什么是聚类 · WHAT IS CLUSTERING", "WHAT IS CLUSTERING"), "LEARNING CLUSTERING")


# ---------------------------------------------------------------- the chip
CPOS = fit({k: tuple(v) for k, v in CIRC["positions"].items()}, (260, 230, 1240, 760))


def chip(fr, labels, alpha=1.0, focus=None):
    cmap = {l: HUES[i % len(HUES)] for i, l in enumerate(sorted(set(labels.values())))} if labels else {}
    for u, v, w in CIRC["edges"]:
        same = labels and labels[u] == labels[v]
        col = cmap[labels[u]] if same else (ROSE if labels else "#6f9da0")
        fr.line(CPOS[u], CPOS[v], col, 0.8 + w * 0.45, (0.25 + w * 0.08) * alpha, glow=0.12 * alpha)
    for n, (x, y) in CPOS.items():
        col = cmap[labels[n]] if labels else "#9fbcbc"
        fr.rect(x - 25, y - 13, 50, 26, fill=NODE_BG, stroke=col, width=1.6, alpha=alpha, r=3)
        for side in (-1, 1):
            for dy in (-6, 6):
                fr.line((x + side * 25, y + dy), (x + side * 30, y + dy), col, 1.3, alpha * 0.8)


def h_chip(fr, c):
    a = c.p(0, 1.0)
    substrate(fr, 0.5 * a)
    lit = c.T >= FILL1[0]
    chip(fr, CRUN["labels"] if lit else None, a)
    x = 1560
    if c.on(1):
        q = c.p(1)
        fr.line((x - 160, 380), (x - 40, 380), TEAL, 4, q, glow=0.5 * q)
        fr.text(L("组内：导线短", "inside a group: short wires"), x - 100, 430, 24, TEAL, q, anchor="c")
    if c.on(2):
        q = c.p(2)
        fr.line((x - 260, 540), (x + 60, 540), ROSE, 2.5, q, glow=0.4 * q, dash=[10, 8])
        fr.text(L("跨组：长、慢、费电", "between groups: long, slow, costly"), x - 100, 590, 24, ROSE, q, anchor="c")


# ---------------------------------------------------------------- five friends and the cut
def friends(fr, box, groups=None, alpha=1.0, r=40, weights=True, name_size=22):
    pos = fit(P5RAW, box)
    side = {FR[n]: i for i, g in enumerate(groups) for n in g} if groups else None
    cols = {n: (TEAL if side[n] == 0 else BLUE) for n in pos} if side else {}
    cut = {"|".join(sorted((u, v))) for u, v, _ in E5 if side[u] != side[v]} if side else None
    graph(fr, pos, E5, cols, alpha, cut=cut, r=r, weights=weights, name_size=name_size)
    return pos


def h_friends(fr, c):
    friends(fr, (560, 220, 1360, 690), ["ABC", "DE"] if c.on(1) else None, c.p(0, 1.0), r=46)
    if c.on(1):
        fr.text(L("cut = 被切断的交情之和", "cut = total friendship split"), 960, 830, 28, GOLD, c.p(1), anchor="c", role="serif")


def h_count(fr, c):
    if not c.on(1):
        a = c.p(0)
        friends(fr, (180, 260, 820, 720), ["ABC", "DE"], a, r=34, name_size=18)
        friends(fr, (1100, 260, 1740, 720), ["AE", "BCD"], a, r=34, name_size=18)
        fr.text("ABC | DE · cut 3", 500, 800, 30, TEAL, a, anchor="c", role="mono")
        fr.text("AE | BCD · cut 12", 1420, 800, 30, ROSE, a, anchor="c", role="mono")
        return
    if not c.on(2):
        ways = [p for p in product((0, 1), repeat=5) if p[0] == 0 and 0 < sum(p) < 5]
        n = max(1, min(15, int(15 * c.span(1, 2) * 1.6) + 1))
        base = {n_: tuple(v) for n_, v in P5RAW.items()}
        for i, p in enumerate(ways[:n]):
            ox, oy = 250 + (i % 5) * 290, 250 + (i // 5) * 190
            groups = ["".join(k for k, s in zip("ABCDE", p) if s == 0), "".join(k for k, s in zip("ABCDE", p) if s == 1)]
            pos = fit(base, (ox, oy, ox + 200, oy + 130))
            side = {FR[k]: s for k, s in zip("ABCDE", p)}
            for u, v, w in E5:
                fr.line(pos[u], pos[v], ROSE if side[u] != side[v] else DIM, 1 + w * 0.3, 0.8)
            for k_, q in pos.items():
                fr.dot(q, 9, TEAL if side[k_] == 0 else BLUE, 0.95)
            fr.text(f"{cut5(groups)}", ox + 230, oy + 80, 22, GOLD if cut5(groups) == 3 else MUTED, 1.0, role="mono")
        return
    a = c.p(2)
    digits = str(splits(100))
    grouped = " ".join(digits[max(0, i - 3):i] for i in range(len(digits) % 3 or 3, len(digits) + 1, 3))
    fr.text(L("100 个人分两组", "100 people into two groups"), W / 2, 380, 30, MUTED, a, anchor="c")
    fr.text(grouped, W / 2, 500, 50, GOLD, a, anchor="c", role="mono", glow=0.3 * a)
    fr.text(L("种分法 · 30 位数", "ways · a 30-digit number"), W / 2, 580, 26, MUTED, a, anchor="c")


# ---------------------------------------------------------------- the course map
def cards(fr, alpha, lit, focus=None, y0=300):
    for i, (mid, name, fam) in enumerate(MODS):
        a = alpha * clamp(lit - i)
        if a <= 0:
            continue
        x, y = 200 + (i % 4) * 390, y0 + (i // 4) * 230
        col = FAM[fam][1]
        dim = 0.3 if focus is not None and fam not in focus else 1.0
        fr.rect(x, y, 350, 190, fill=PANEL_BG, stroke=col, width=1.6, alpha=0.95 * a * dim, r=10, screen=True,
                glow=0.25 * a if focus is not None and fam in focus else 0)
        fr.text(mid, x + 28, y + 52, 24, col, a * dim, role="mono")
        fr.paragraph(name, x + 28, y + 100, 26, 300, IVORY, a * dim, role="serif")
        fr.text(FAM[fam][0], x + 28, y + 170, 16, MUTED, a * dim, spacing=1)


def h_algos(fr, c):
    a = c.p(0, 1.0)
    if c.T < PHRASE[0]:
        return
    lit = count_hits(c.T, PHRASE[:8]) if c.T < PHRASE[7] + 0.4 else 8
    cards(fr, a, lit + 0.0 if lit < 8 else 8)
    if c.on(2):
        q = c.p(2)
        for k, (name, col) in enumerate(FAM):
            fr.text(name, 360 + k * 400, 800, 22, col, q, anchor="c", spacing=2)


def h_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("打分 · 生长 · 改进", "Score · grow · improve"), W / 2, 500, 56, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def h_families(fr, c):
    focus = {0} if not c.on(1) else {1}
    cards(fr, 1.0, 8, focus=focus)


def h_improve(fr, c):
    focus = {2} if not c.on(1) else {3}
    cards(fr, 1.0, 8, focus=focus)


def h_route(fr, c):
    p = pulse(c.T, FILL4, 0.5)
    cards(fr, 1.0, 8, focus={0, 1, 2, 3})
    for i in range(7):
        x0, y0 = 200 + (i % 4) * 390 + 350, 300 + (i // 4) * 230 + 95
        if i % 4 == 3:
            continue
        fr.line((x0 + 4, y0), (x0 + 36, y0), GOLD, 2, 0.6 + 0.4 * p, glow=0.3 * p)


def h_outro(fr, c):
    lines = [(L("聚类不是一个算法，而是一个问题", "Clustering is not one algorithm but one question"), TEAL, 0),
             (L("怎样分组，才让联系留在组内？", "How do we group so the links stay inside?"), GOLD, 1),
             (L("每一章，给出一种回答", "Each module gives one answer"), TEAL, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("从给一对单元打分开始", "It starts with scoring a pair"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def h_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        cards(fr, a, 8, focus={0})
    else:
        credits(fr, c, [(L("连接与分组", "Connect & Group"), GOLD, 44),
                        (L("Learning Clustering · 导论", "Learning Clustering · Introduction"), IVORY, 24),
                        (L("五个朋友是课程公共图 G01；芯片是 Module 05 的 24 单元虚构电路，分组由本课程引擎计算", "The five friends are the course graph G01; the chip is Module 05's fictional 24-cell circuit, grouped by this course's engine"), MUTED, 20),
                        (L("婚宴座位图是示意，不是课程数据", "The seating plan is an illustration, not course data"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


INTRO = Film(
    "intro", "intro", L("连接与分组", "Connect & Group"), None, BRAND, poster_at=36.5, music=TRACK, seed=1,
    why=L("全课程的共同背景：从婚宴排座位讲起，什么是聚类、为什么芯片设计离不开它、为什么不能一个个试，以及这门课的三类方法。",
          "The background every module shares: from a wedding seating plan to what clustering is, why chip design depends on it, why trying every split is hopeless, and the three families of methods in this course."),
    scenes=[
        Scene("h-seat", h_seat, [Beat(L("婚礼要排座位：三张桌子，三十位客人。", "A wedding seating plan: three tables, thirty guests."), 5.0),
                                 Beat(L("谁和谁坐一桌？", "Who sits with whom?"), 3.6)],
              chapter=L("序 · 排座位", "PROLOGUE · A SEATING PLAN"), until=S["intro_end"]),
        Scene("h-seat2", h_seat2, [Beat(L("熟人坐一桌，生人分开坐：你已经在做聚类。", "Friends together, strangers apart: you are already clustering."), 5.6)],
              until=S["groove"]),
        Scene("h-what", h_what, [Beat(L("聚类：把联系紧的放进一组，组和组之间联系少。", "Clustering: what is tightly linked goes in one group, with few links between groups."), 6.6),
                                 Beat(L("不必知道每个人是谁，只看谁和谁有联系。", "You need not know who anyone is, only who is linked to whom."), 5.4)],
              chapter=L("序 · 聚类", "PROLOGUE · CLUSTERING"), until=S["roll"]),
        Scene("h-title", h_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("h-chip", h_chip, [Beat(L("芯片里，几百万个单元由导线连成一张网。", "On a chip, millions of cells are wired into one network."), 4.8),
                                 Beat(L("同一组的单元放在一起，导线就短；", "Cells in one group sit together, so their wires are short;"), 4.4),
                                 Beat(L("跨组的导线又长又慢，还更费电。", "wires between groups are long, slow and costly."), 4.4)],
              chapter=L("一 · 为什么重要", "I · WHY IT MATTERS"), until=S["fill1_end"]),
        Scene("h-friends", h_friends, [Beat(L("课程里的五个朋友：线越粗，交情越深。", "The course's five friends: thicker line, closer friends."), 4.8),
                                       Beat(L("分成两组，切断的交情就叫 cut。", "Split them in two; the friendship cut is the cut."), 4.4)],
              until=S["accent"]),
        Scene("h-count", h_count, [Beat(L("ABC | DE 只切断 3；AE | BCD 切断 12。", "ABC | DE cuts only 3; AE | BCD cuts 12."), 2.9),
                                   Beat(L("五个人分两组：15 种分法，可以一个个试。", "Five people into two groups: 15 ways, easy to try them all."), 5.0),
                                   Beat(L("一百个人呢？分法的个数有 30 位。", "A hundred people? The count has 30 digits."), 4.6)],
              chapter=L("二 · 为什么难", "II · WHY IT IS HARD"), until=S["phrase"]),
        Scene("h-algos", h_algos, [Beat(L("一个个试，永远试不完。所以要靠算法。", "Trying them one by one never ends. So we need algorithms."), 5.0),
                                   Beat(L("这门课的八章，是八种回答。", "This course's eight modules are eight answers."), 5.0),
                                   Beat(L("它们大致分成几类。", "They fall into a few families."), 5.0)],
              chapter=L("三 · 算法", "III · ALGORITHMS"), until=S["breath"]),
        Scene("h-breath", h_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("h-families", h_families, [Beat(L("第一类：给每一对打分，把最亲近的一对对合并（M02–M04）。", "First: score every pair, then merge the closest, pair by pair (M02–M04)."), 7.0),
                                         Beat(L("第二类：让分组自己长出来，标签传播、谱方法（M05–M06）。", "Second: let groups emerge, by label propagation or spectral methods (M05–M06)."), 7.4)],
              chapter=L("四 · 三类方法", "IV · THREE FAMILIES"), until=S["fill3_end"]),
        Scene("h-improve", h_improve, [Beat(L("第三类：改进已有分组，成对交换或逐个搬（M07–M08）。", "Third: improve a grouping by swapping pairs or moving one at a time (M07–M08)."), 7.4),
                                       Beat(L("最后一章把目标换成速度：让最慢的路径最快（M09）。", "The last module aims for speed: make the slowest path fast (M09)."), 6.2)],
              until=S["fill4"]),
        Scene("h-route", h_route, [Beat(L("八章，同一个问题。", "Eight modules, one problem."), 5.4)], until=141.5),
        Scene("h-outro", h_outro, [Beat(L("聚类不是一个算法，而是一个问题：", "Clustering is not one algorithm but one question:"), 6.0),
                                   Beat(L("怎样分组，才让联系留在组内？", "how do we group things so the links stay inside?"), 7.0),
                                   Beat(L("每一章，给出一种回答。", "Each module gives one answer."), 6.0),
                                   Beat(L("从给一对单元打分开始。", "It starts with scoring a pair."), 7.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("h-end", h_end, [Beat(L("从 Module 02 开始。", "Start with Module 02."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])

FILMS = [INTRO]
ORDER = ["intro"]
