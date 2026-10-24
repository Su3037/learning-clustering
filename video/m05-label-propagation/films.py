"""Module 05 · Label propagation — the four films.

  story     popular science: the author's original film 《圈子从哪里来》 (v4, 6:20, We Never (Remix)),
            shown as made; its source lives in Su3037/clustering-lab5-label-propagation.
  concise   the essentials in about two minutes.
  advanced  why asynchronous updates stop, why synchronous ones can cycle, the stopping tests,
            order dependence, cost, the trivial fixed point, and size-constrained variants for coarsening.
  lab       experiment walkthrough, composed from screen recordings of the real lab and code lab
            (video/m05-label-propagation/walkthrough.py).

Every label, vote, round count and cut is read from site/data/m05-label-propagation/traces.json,
which scripts/build-traces.mjs produces by running site/engines/lp.js.
"""
import json
import math
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, HUES, clamp, ease, ramp, lerp, lerp2, title_card, panel, badge, note, bar, code_panel, table,
                  graph, vote_panel, math_line, fit, cut_keys, cut_value, nbrs, mixc)

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m05-label-propagation/traces.json").read_text())
G = T["g01"]
E5 = [tuple(e) for e in G["edges"]]
GOLDEN = T["golden"]
BRAND = L("Learning Clustering · Module 05 · 标签传播", "Learning Clustering · Module 05 · Label propagation")
LAB = {"A": AMBER, "B": TEAL, "C": CORAL, "D": BLUE, "E": ROSE}
P5 = {"A": (330, 300), "B": (650, 250), "C": (540, 520), "D": (850, 660), "E": (370, 730)}
ALL = "ABCDE"
LW = L("标签", "label")


def lab_cols(labels):
    return {n: LAB.get(labels[n], MUTED) for n in labels}


def lab_badges(labels):
    return {n: f"{tr(LW)} {labels[n]}" for n in labels}


def g5(fr, labels, alpha=1.0, pos=P5, edges=E5, cut=False, **kw):
    graph(fr, pos, edges, lab_cols(labels), alpha, badges=lab_badges(labels), cut=cut_keys(edges, labels) if cut else None, **kw)


def round_ends(run):
    """Label state after each complete round; index 0 is the initial state."""
    nodes = sorted(run["result"]["labels"])
    states = [{n: n for n in nodes}]
    for e in run["events"]:
        if e["kind"] == "update-round-end":
            states.append(dict(e["after"] if e["committed"] else e["pending"]))
    return states


def tokens(fr, ev, k, pos, dests):
    """Each neighbour's weight travels (in its label colour) into C and on to the label's register.
    k: 0→1 progress over all neighbours. Returns the sums that have landed."""
    filled = {}
    order = sorted(ev["neighbors"], key=lambda d: d["node"])
    n = len(order)
    for i, nb in enumerate(order):
        a = i / (n + 0.6)
        q = clamp((k - a) / (1.6 / (n + 0.6)))
        if q >= 1:
            filled[nb["label"]] = filled.get(nb["label"], 0) + nb["weight"]
            continue
        if q <= 0:
            continue
        src, mid, dst = pos[nb["node"]], pos[ev["node"]], dests[nb["label"]]
        p = lerp2(src, mid, q * 2) if q < 0.5 else lerp2(mid, dst, (q - 0.5) * 2)
        fr.dot(p, 4 + nb["weight"] * 0.9, LAB.get(nb["label"], GOLD), 1, glow=1, screen=True)
    return filled


# ====================================================================== concise film
def c_title(fr, c):
    title_card(fr, L("标签传播", "Label Propagation"), L("LABEL PROPAGATION  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2),
               kicker=L("MODULE 05", "MODULE 05"))


def c_problem(fr, c):
    plain = {n: "#9fbcbc" for n in ALL}
    graph(fr, P5, E5, plain, c.p(0, 1.0), wscale=0.9)
    if c.on(1):
        a = c.p(1)
        panel(fr, 1110, 280, 660, 340, a, L("要解决的问题", "THE PROBLEM"))
        hgt = fr.paragraph(L("输入：带权无向图。线越粗，连接越强。", "Input: a weighted graph. A thicker wire is a stronger tie."), 1140, 380, 28, 600, IVORY, a)
        fr.paragraph(L("输出：分组，组内连接紧，组间连接少。不预先给出组数 K。", "Output: groups that are tight inside and loosely linked to each other, with no K given in advance."), 1140, 380 + hgt + 20, 28, 600, GOLD, a * c.p(1, 0.8, 0.6))


def c_rule(fr, c):
    a = c.p(0)
    panel(fr, 260, 250, 1400, 430, a)
    y = 400
    math_line(fr, [(L("新标签", "new label"), IVORY), ("(v)  =  ", IVORY), ("argmax", GOLD), ("L", GOLD, "under"), ("      ", IVORY),
                   ("Σ", IVORY), (L("u ∈ N(v), 标签(u) = L", "u ∈ N(v), label(u) = L"), MUTED, "under"), ("      ", IVORY), ("w(u, v)", IVORY)], W / 2, y, 64, a)
    fr.text(L("对每个候选标签 L：把当前带着 L 的邻居 u 的边权加起来，取最大的那个", "for each candidate label L, add up the weights to neighbours u that carry L now, and take the largest"),
            W / 2, 530, 26, MUTED, a * c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("一个局部规则 · 每次只看一个点的邻居 · 不需要 K", "one local rule  ·  look only at one node's neighbours  ·  no K"), W / 2, 600, 24, TEAL, c.p(2), anchor="c",
                spacing=2 if True else 0)


def c_labels(fr, c):
    init = {n: n for n in ALL}
    g5(fr, init, 1.0, glow_nodes=ALL if c.on(1) else ())
    panel(fr, 1100, 280, 640, 380, c.p(0), L("名字与标签", "NAMES AND LABELS"))
    rows = [(L("名字 = 身份", "Name = identity"), L("A 永远是 A", "A is always A"), IVORY),
            (L("标签 = 归属", "Label = membership"), L("会被改写", "can be rewritten"), GOLD),
            (L("开始时", "At the start"), L("标签 = 自己的名字", "label = own name"), TEAL)]
    for i, (k, v, col) in enumerate(rows):
        if c.on(i):
            a = c.p(i)
            fr.text(k, 1140, 380 + i * 96, 30, col, a, bold=True)
            fr.text(v, 1140, 418 + i * 96, 24, MUTED, a)


EV_C = next(e for e in GOLDEN["events"] if e["round"] == 1 and e["node"] == "C")


def c_vote(fr, c):
    ev = EV_C
    hl = {"|".join(sorted(("C", nb["node"]))) for nb in ev["neighbors"]} if c.on(1) else set()
    g5(fr, ev["before"], 1.0, active="C", hl_edges=hl)
    order = sorted(ev["votes"], key=lambda l: (-ev["votes"][l], l))
    dests = {lab: (1130 + 150 + 20, 240 + 110 + i * 92) for i, lab in enumerate(order)}
    k = c.span(1, 2) if c.on(1) else 0
    filled = tokens(fr, ev, k, P5, dests) if c.on(1) and k < 1 else dict(ev["votes"]) if c.on(1) else {}
    shown = {lab: filled.get(lab, 0) for lab in order}
    vote_panel(fr, 1130, 240, {l: v for l, v in shown.items()} if any(shown.values()) else {l: 0 for l in order}, c.p(0), L("C 的票 · 第 1 轮", "C'S VOTES · ROUND 1"),
               winner=ev["label"] if c.on(2) else None, hl=c.p(2), colors=LAB, grow=1.0)
    if c.on(3):
        note(fr, L("A 和 B 都带标签 B：1 + 4 = 5", "A and B both carry label B: 1 + 4 = 5"), c.p(3), GOLD, y=760)


R1 = [e for e in GOLDEN["events"] if e["round"] == 1]
R2 = [e for e in GOLDEN["events"] if e["round"] == 2]


def round_view(fr, c, events, k_from, title, x=1080):
    """Animate one asynchronous round: each beat from k_from on updates one node."""
    i = clamp(c.k - k_from, -1, len(events) - 1) if c.on(k_from) else -1
    i = int(i)
    cur = events[i] if i >= 0 else None
    labels = (cur["after"] if cur else events[0]["before"])
    if cur:
        prog = c.p(k_from + i, 0.6)
        mix = dict(labels)
        if prog < 0.5:
            mix[cur["node"]] = cur["old"]
        labels = mix
    g5(fr, labels, 1.0, active=cur["node"] if cur else None)
    panel(fr, x, 220, 700, 120 + 64 * len(events), 1.0, title)
    head = [L("访问", "visit"), L("票数", "votes"), L("结果", "result")]
    rows = [[tr(h) for h in head]]
    cols = {}
    for j, e in enumerate(events[: i + 1]):
        votes = ", ".join(f"{l}:{v:g}" for l, v in sorted(e["votes"].items(), key=lambda t: (-t[1], t[0])))
        res = f"{e['old']} → {e['label']}" if e["changed"] else tr(L(f"保持 {e['old']}", f"keeps {e['old']}"))
        rows.append([e["node"], votes, res])
        cols[(j + 1, 2)] = GOLD if e["changed"] else MUTED
    table(fr, x + 40, 320, [110, 300, 220], rows, 1.0, 26, 64, colors=cols)
    return labels


def c_round1(fr, c):
    round_view(fr, c, R1, 1, L("第 1 轮 · 异步 · A→E", "ROUND 1 · ASYNC · A→E"))


def c_round2(fr, c):
    labels = round_view(fr, c, R2, 0, L("第 2 轮 · 确认", "ROUND 2 · CONFIRM"))
    if c.on(len(R2)):
        a = c.p(len(R2))
        badge(fr, W / 2 + 470, 800, L(f"零变化 → stable · {GOLDEN['result']['rounds']} 轮 · cut {GOLDEN['result']['cut']}",
                                      f"no change → stable · {GOLDEN['result']['rounds']} rounds · cut {GOLDEN['result']['cut']}"), TEAL, a, 22, screen=True)


def c_stops(fr, c):
    cards = [("stable", L("完整一轮零变化", "a full round with no change"), L("唯一可以叫“收敛”的情况", "the only case you may call converged"), TEAL),
             ("cycle", L("标签状态重复出现", "a label state repeats"), L("会一直循环，报告 cycle", "it loops forever: report cycle"), ROSE),
             ("limit", L("到达轮数上限", "the round limit is reached"), L("没停下，也没证明循环", "neither stopped nor proven to loop"), GOLD)]
    for i, (k, a1, a2, col) in enumerate(cards):
        if not c.on(i):
            continue
        a = c.p(i)
        x = 210 + i * 520
        panel(fr, x, 300, 460, 300, a, accent=col)
        fr.text(k, x + 40, 390, 52, col, a, role="mono", glow=0.25 * a)
        fr.paragraph(a1, x + 40, 470, 28, 390, IVORY, a)
        fr.paragraph(a2, x + 40, 540, 22, 390, MUTED, a)


PAIR_STATES = round_ends(T["pairSync"])


def c_sync(fr, c):
    pa, pb = (640, 480), (1280, 480)
    if c.on(1):
        k = min(int(c.since(1) / 1.4) + 1, 6)
    else:
        k = 0
    lab = {"A": "A", "B": "B"} if k % 2 == 0 else {"A": "B", "B": "A"}
    pos = {"A": pa, "B": pb}
    graph(fr, pos, [("A", "B", 1)], {n: LAB[lab[n]] for n in "AB"}, 1.0, r=56, name_size=48,
          badges={n: f"{tr(LW)} {lab[n]}" for n in "AB"}, cut={"A|B"})
    fr.text(L("同步：所有点读同一张旧快照，轮末一起提交", "Synchronous: everyone reads the same old snapshot, then all commit at round end"), W / 2, 280, 30, GOLD, c.p(0), anchor="c")
    if c.on(1):
        fr.text(L(f"第 {k} 轮", f"round {k}"), W / 2, 680, 26, MUTED, 1.0, anchor="c")
        for s in (-1, 1):
            fr.arrow((W / 2 - s * 150, 420 + s * 0), (W / 2 + s * 150, 420), MUTED, 2, 0.6 * c.p(1))
    if c.on(2):
        badge(fr, W / 2, 760, L("第 2 轮又回到第 0 轮 → cycle（周期 2）", "round 2 equals round 0 → cycle (period 2)"), ROSE, c.p(2), 22, screen=True)


REV = T["reverse"]
HEAVY = T["heavy"]
POS_SMALL = {k: (v[0] * 0.62, v[1] * 0.62) for k, v in P5.items()}


def mini(fr, ox, oy, labels, a, edges=E5, title=None, sub=None, sub_col=MUTED):
    pos = {k: (ox + (v[0] - 330) * 0.6, oy + (v[1] - 250) * 0.6) for k, v in P5.items()}
    graph(fr, pos, edges, lab_cols(labels), a, r=24, name_size=22, cut=cut_keys(edges, labels), wscale=0.6)
    if title:
        fr.text(title, ox + 150, oy - 70, 24, GOLD, a, anchor="c", spacing=1)
    if sub:
        fr.text(sub, ox + 150, oy + 380, 24, sub_col, a, anchor="c")


def c_knobs(fr, c):
    g = GOLDEN["result"]
    mini(fr, 180, 300, g["labels"], c.p(0), title=L("正序 A→E", "order A→E"),
         sub=L(f"{g['rounds']} 轮 · ABC | DE · cut {g['cut']}", f"{g['rounds']} rounds · ABC | DE · cut {g['cut']}"))
    if c.on(1):
        r = REV["result"]
        mini(fr, 780, 300, r["labels"], c.p(1), title=L("反序 E→A", "order E→A"),
             sub=L(f"{r['rounds']} 轮 · 标签名不同，分组相同", f"{r['rounds']} rounds · other names, same groups"), sub_col=TEAL)
    if c.on(2):
        h = HEAVY["result"]
        heavy_edges = [(u, v, 10 if (u, v) == ("C", "D") else w) for u, v, w in E5]
        mini(fr, 1380, 300, h["labels"], c.p(2), edges=heavy_edges, title=L("C–D 加到 10", "C–D raised to 10"),
             sub=L(f"AB | CDE · cut {h['cut']}", f"AB | CDE · cut {h['cut']}"), sub_col=ROSE)


def c_take(fr, c):
    items = [(L("不需要 K，规则是局部的", "No K; the rule is local"), TEAL),
             (L("每轮把每条边读两遍：很快", "Each round reads every edge twice: fast"), TEAL),
             (L("结果依赖顺序、同步方式与平票规则", "Results depend on order, update mode and tie rule"), GOLD),
             (L("不保证各组大小均衡；同步可能振荡", "No size balance; synchronous updates can cycle"), ROSE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(300, y, 1320, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 350, y + 58, 28, col, a, role="mono")
            fr.text(s, 440, y + 58, 32, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：规则与停止", "The essentials"), None, BRAND, poster_at=40.0, music="score:steady", seed=21,
    why=L("只讲必须掌握的：规则、计票、一轮异步、三种停止、同步振荡和三个旋钮。", "Only what you must know: the rule, the vote, one asynchronous round, the three ways to stop, the synchronous cycle and three knobs."),
    scenes=[
        Scene("k00-title", c_title, [Beat(None, 3.0)]),
        Scene("k01-problem", c_problem, [Beat(L("一张带权图：线越粗，连接越强。", "A weighted graph: the thicker the wire, the stronger the tie."), 2.6),
                                          Beat(L("目标：把连接紧密的点分到一组，而且不事先说分几组。", "Goal: put tightly linked nodes in one group, without saying how many groups."), 3.4)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-rule", c_rule, [Beat(L("规则只有一句：看邻居现在的标签，", "The whole rule: look at your neighbours' current labels,"), 2.6),
                                    Beat(L("加入边权之和最大的那一组。", "and join the label with the largest total weight."), 2.6),
                                    Beat(L("每次只看一个点和它的邻居。", "Each step looks at one node and its neighbours only."), 2.4)],
              chapter=L("规则", "THE RULE")),
        Scene("k03-labels", c_labels, [Beat(L("先分清两个词：名字是身份，永远不变；", "Two words first: a name is identity and never changes;"), 2.8),
                                        Beat(L("标签是归属，可以改写。", "a label is membership and can be rewritten."), 2.2),
                                        Beat(L("开始时，每个点的标签就是自己的名字。", "At the start, each node's label is its own name."), 2.4)]),
        Scene("k04-vote", c_vote, [Beat(L("轮到 C。A 已经改为标签 B。", "C's turn. A has already switched to label B."), 2.4),
                                    Beat(L("同一标签的边权加起来。", "Add up the weights per label."), 3.2),
                                    Beat(L("B = 5，D = 2，E = 1：C 的标签改为 B。", "B = 5, D = 2, E = 1: C takes label B."), 2.6),
                                    Beat(L("比的是权重之和，不是邻居个数。", "It is total weight that counts, not the number of neighbours."), 2.6)],
              chapter=L("计票", "THE VOTE")),
        Scene("k05-round1", c_round1, [Beat(L("异步更新：按 A→E 依次来，改完立刻生效。", "Asynchronous: visit A to E in turn; each change takes effect at once."), 2.4)]
              + [Beat(L(f"{e['node']}：{'改为 ' + e['label'] if e['changed'] else '保持 ' + e['old']}。", f"{e['node']}: {'switches to ' + e['label'] if e['changed'] else 'keeps ' + e['old']}."), 1.5) for e in R1]
              + [Beat(L("第 1 轮改了 3 个点。", "Round 1 changed three nodes."), 1.8)],
              chapter=L("一轮", "ONE ROUND")),
        Scene("k06-round2", c_round2, [Beat(L("第 2 轮：每个点再投一次。", "Round 2: every node votes again."), 1.2)] + [Beat(None, 0.9) for _ in R2[1:]]
              + [Beat(L("一个都没变，这才确认稳定：共 2 轮，cut 3。", "Nothing changed, and only now is it stable: 2 rounds, cut 3."), 3.2)]),
        Scene("k07-stops", c_stops, [Beat(L("停止有三种：stable，完整一轮零变化；", "There are three ways to stop: stable, a full round with no change;"), 3.0),
                                      Beat(L("cycle，状态重复出现；", "cycle, a state that repeats;"), 2.0),
                                      Beat(L("limit，到了轮数上限。只有 stable 才叫收敛。", "limit, the round cap. Only stable counts as converged."), 3.2)],
              chapter=L("停止", "STOPPING")),
        Scene("k08-sync", c_sync, [Beat(L("换成同步更新：大家读同一张旧快照。", "Switch to synchronous updates: everyone reads the same old snapshot."), 2.6),
                                    Beat(L("A 读到 B，B 读到 A，同时交换，再换回来。", "A sees B, B sees A: they swap, then swap back."), 4.2),
                                    Beat(L("状态重复：这是 cycle，不是收敛。", "The state repeats: that is a cycle, not convergence."), 2.6)]),
        Scene("k09-knobs", c_knobs, [Beat(L("三个旋钮会改变结果。", "Three knobs change the outcome."), 2.0),
                                      Beat(L("反过来访问：3 轮，标签名变了，分组不变。", "Reverse the order: 3 rounds, other label names, the same groups."), 3.0),
                                      Beat(L("把 C–D 加到 10：分组变成 AB | CDE，cut 5。", "Raise C–D to 10: the groups become AB | CDE, cut 5."), 3.4)],
              chapter=L("三个旋钮", "THREE KNOBS")),
        Scene("k10-take", c_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                    Beat(L("快、局部、不需要 K；", "Fast, local, no K;"), 1.6),
                                    Beat(L("但结果依赖规则，", "but the result depends on the rules,"), 1.8),
                                    Beat(L("也不保证均衡。下面的实验里亲手试一遍。", "and nothing balances the groups. Try it yourself in the lab below."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

# ====================================================================== advanced film
TOTAL5 = sum(w for _, _, w in E5)
CIRC = T["circuit"]["graph"]
CPOS = fit({k: tuple(v) for k, v in CIRC["positions"].items()}, (150, 210, 1150, 770))
CELL_W, CELL_H = 50, 26


def circuit(fr, labels, alpha=1.0, pos=CPOS, colors=None, wire_alpha=None, show_names=True, cut=True):
    """The fictional 24-cell schematic: cells with pins, wires coloured by group, cut wires rose."""
    universe = sorted(set(labels.values())) if labels else []
    cmap = colors or {l: HUES[i % len(HUES)] for i, l in enumerate(universe)}
    for u, v, w in CIRC["edges"]:
        same = labels and labels[u] == labels[v]
        col = cmap[labels[u]] if same else (ROSE if cut and labels else "#6f9da0")
        wa = (wire_alpha(u, v) if wire_alpha else 1.0) * alpha
        fr.line(pos[u], pos[v], col, 0.8 + w * 0.45, (0.22 + w * 0.08) * wa * (1.0 if same or not labels else 0.9), glow=0.12 * wa * w / 6)
    for n, (x, y) in pos.items():
        c = cmap[labels[n]] if labels else "#9fbcbc"
        fr.rect(x - CELL_W / 2, y - CELL_H / 2, CELL_W, CELL_H, fill=NODE_BG, stroke=c, width=1.6, alpha=alpha, r=3)
        for side in (-1, 1):
            for dy in (-6, 6):
                fr.line((x + side * CELL_W / 2, y + dy), (x + side * (CELL_W / 2 + 5), y + dy), c, 1.3, alpha * 0.8)
        if show_names:
            fr.text(n, x, y + 5, 13, IVORY, alpha * 0.9, role="mono", anchor="c", screen=False)


def a_title(fr, c):
    title_card(fr, L("标签传播 · 进阶", "Label Propagation, in Depth"), L("为什么停 · 为什么不停 · 代价与变体", "WHY IT STOPS  ·  WHY IT MAY NOT  ·  COST AND VARIANTS"), c.p(0, 1.2),
               kicker=L("MODULE 05 · 进阶", "MODULE 05 · ADVANCED"))


def a_recap(fr, c):
    g5(fr, GOLDEN["result"]["labels"], c.p(0), cut=True)
    panel(fr, 1100, 260, 660, 400, c.p(0), L("上一部讲了规则", "THE RULE, AS BEFORE"))
    math_line(fr, [("ℓ(v) ← ", IVORY), ("argmax", GOLD), ("L", GOLD, "under"), ("   Σ", IVORY), ("u: ℓ(u) = L", MUTED, "under"), ("   w(u, v)", IVORY)], 1430, 380, 44, c.p(0))
    qs = [L("它为什么会停？", "Why does it stop?"), L("什么时候停不下来？", "When does it fail to stop?"), L("每轮花多少工夫？", "How much work is a round?"), L("它会出什么错，怎么改？", "How does it go wrong, and how is it fixed?")]
    for i, q in enumerate(qs):
        if c.on(1):
            a = c.p(1, 0.6, i * 0.35)
            fr.text(f"0{i + 1}", 1140, 470 + i * 46, 22, GOLD, a, role="mono")
            fr.text(q, 1200, 470 + i * 46, 26, IVORY, a)


# --- why asynchronous updates stop: the cut can only go down
GEV = GOLDEN["events"]


def a_potential(fr, c):
    """Beat 0: all edges cut; beats 1..: one update per beat with the cut meter."""
    i = c.k - 1
    ev = GEV[i] if 0 <= i < len(GEV) else None
    labels = {n: n for n in ALL} if i < 0 else (ev["after"] if ev else GEV[-1]["after"])
    if ev and c.p(c.k, 0.6) < 0.5 and ev["changed"]:
        labels = dict(labels); labels[ev["node"]] = ev["old"]
    cutv = cut_value(E5, labels)
    g5(fr, labels, 1.0, cut=True, active=ev["node"] if ev else None)
    panel(fr, 1080, 230, 700, 470, 1.0, L("把 cut 当成计数器", "WATCH THE CUT"))
    fr.text("cut", 1120, 360, 30, MUTED, 1.0, role="mono")
    fr.text(f"{cutv:g}", 1230, 372, 84, ROSE if cutv > 3 else TEAL, 1.0, role="serif", glow=0.2)
    fr.text(f"/ {TOTAL5}", 1360, 372, 30, MUTED, 1.0, role="mono")
    bar(fr, 1120, 410, 600, 12, cutv / TOTAL5, ROSE if cutv > 3 else TEAL)
    # running log of the drops
    rows = []
    for e in GEV[: max(0, i + 1)]:
        old_v = e["votes"].get(e["old"], 0)
        new_v = e["votes"][e["label"]]
        rows.append((e, old_v, new_v))
    for j, (e, ov, nv) in enumerate(rows[-5:]):
        y = 480 + j * 40
        txt = (f"{e['node']}: {e['old']} → {e['label']}   −({nv:g} − {ov:g}) = −{nv - ov:g}" if e["changed"]
               else tr(L(f"{e['node']}: 保持 {e['old']}   cut 不变", f"{e['node']}: keeps {e['old']}   cut unchanged")))
        fr.text(txt, 1120, y, 22, GOLD if e["changed"] else MUTED, 1.0, role="mono")


def a_proof(fr, c):
    steps = [(L("只在新标签的票严格更多时才改", "change only when the new label has strictly more votes"), TEAL),
             (L("每次改动，cut 至少降 1（整数权重）", "each change lowers the cut by at least 1 (integer weights)"), TEAL),
             (L("cut 不能低于 0", "the cut cannot go below 0"), TEAL),
             (L("所以改动次数有限：异步一定停下", "so there are finitely many changes: asynchronous updates stop"), GOLD)]
    for i, (s, col) in enumerate(steps):
        if c.on(i):
            a = c.p(i)
            y = 250 + i * 110
            fr.rect(330, y, 1260, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"{i + 1}", 380, y + 54, 30, col, a, role="serif")
            fr.text(s, 450, y + 54, 30, IVORY if i < 3 else GOLD, a)
            if i < 3 and c.on(i + 1):
                fr.text("⇒" if False else "↓", 380 + 8, y + 104, 22, MUTED, c.p(i + 1))
    if c.on(4):
        note(fr, L("平票也改（min / max 规则）时 cut 不变，这个论证就管不住了：平票规则必须写清楚。",
                   "If a tie also triggers a change (min / max rules) the cut stays put and the argument no longer applies: state the tie rule."), c.p(4), ROSE, y=720)


# --- synchronous: the star
STAR = T["star"]
SPOS = {"H": (560, 470), "a": (330, 290), "b": (790, 290), "c": (790, 650), "d": (330, 650)}
SSTATES = round_ends(STAR["sync"])
SCOL = {"H": GOLD, "a": TEAL, "b": BLUE, "c": ROSE, "d": LILAC}


def a_star(fr, c):
    k = 0 if not c.on(1) else min(int(c.since(1) / 2.2) + 1, len(SSTATES) - 1)
    lab = SSTATES[k]
    sedges = [tuple(e) for e in STAR["graph"]["edges"]]
    graph(fr, SPOS, sedges, {n: SCOL[lab[n]] for n in lab}, 1.0, r=44, name_size=36, weights=False,
          badges={n: f"{tr(LW)} {lab[n]}" for n in lab}, badge_cols={n: SCOL[lab[n]] for n in lab}, badge_dirs={"H": (0, 1.25)}, cut=cut_keys(sedges, lab))
    panel(fr, 1080, 240, 700, 480, 1.0, L("同步 · 星形图", "SYNCHRONOUS · A STAR"))
    rows = [[tr(L("轮", "round")), "H", "a  b  c  d", "cut"]]
    hl = {}
    for r in range(0, k + 1):
        st = SSTATES[r]
        rows.append([str(r), st["H"], "  ".join(st[x] for x in "abcd"), str(cut_value(sedges, st))])
    if k >= 3:
        hl = {2: ROSE, 4: ROSE}
    table(fr, 1120, 330, [110, 120, 300, 100], rows, 1.0, 28, 60, highlight=hl)
    if c.on(3):
        badge(fr, 1430, 680, L("第 3 轮 = 第 1 轮 → cycle，周期 2", "round 3 = round 1 → cycle, period 2"), ROSE, c.p(3), 22, screen=True)


SYNC5 = round_ends(T["syncG01"])


def a_sync5(fr, c):
    k = min(int(c.t / 2.0), len(SYNC5) - 1)
    lab = SYNC5[k]
    g5(fr, lab, 1.0, cut=True)
    panel(fr, 1080, 260, 700, 380, 1.0, L("G01 也一样", "G01 DOES THE SAME"))
    fr.text(L(f"同步 · 第 {k} 轮", f"synchronous · round {k}"), 1120, 360, 30, GOLD, 1.0)
    fr.text(f"cut {cut_value(E5, lab)}", 1120, 430, 44, ROSE, 1.0, role="serif")
    fr.paragraph(L("两端各自追赶对方的旧标签。二分（或接近二分）的结构最容易这样来回交换。",
                   "Each side chases the other's old label. Bipartite and near-bipartite structures swap back and forth like this most easily."), 1120, 500, 24, 620, MUTED, c.p(1))


# --- stopping tests
def a_stoptests(fr, c):
    a0 = c.p(0)
    panel(fr, 180, 250, 760, 400, a0, L("本课程的判定", "THIS COURSE"))
    fr.paragraph(L("完整一轮零变化 → stable。平票规则固定（min / max / keep），所以结果可复现。",
                   "A full round with no change → stable. The tie rule is fixed (min / max / keep), so runs are reproducible."), 220, 350, 28, 680, IVORY, a0)
    fr.paragraph(L("每轮结束记下整张标签表；出现过的状态再出现 → cycle，并报告周期。",
                   "At each round end, store the whole labelling; a state seen before → cycle, with its period."), 220, 500, 26, 680, MUTED, a0 * c.p(1))
    if c.on(2):
        a = c.p(2)
        panel(fr, 980, 250, 760, 400, a, L("原论文（Raghavan 等，2007）", "THE PAPER (RAGHAVAN ET AL., 2007)"), accent=GOLD)
        fr.paragraph(L("每轮随机打乱访问顺序；平票时随机挑一个。",
                       "Shuffle the visit order every round; break ties uniformly at random."), 1020, 350, 28, 680, IVORY, a)
        fr.paragraph(L("随机平票可能让“零变化”永远不出现，所以论文改为：每个点的标签都是邻居中票数最多的标签之一，就停。",
                       "Random tie-breaks may never give a quiet round, so the paper stops when every node's label is one of the labels with the most votes among its neighbours."), 1020, 450, 24, 680, GOLD, a * c.p(3) if c.on(3) else 0)


# --- order dependence
ORD = T["orders"]


def histo(fr, x, y, w, data, title, alpha, col=GOLD, label_fmt=str, total=None):
    panel(fr, x, y, w, 120 + 70 * len(data), alpha, title)
    total = total or sum(v for _, v in data)
    for i, (k, v) in enumerate(data):
        yy = y + 110 + i * 70
        fr.text(label_fmt(k), x + 30, yy + 8, 24, IVORY, alpha)
        bar(fr, x + 290, yy - 12, w - 430, 24, v / total, col if i == 0 else ROSE, alpha)
        fr.text(f"{v}", x + w - 40, yy + 9, 26, IVORY, alpha, anchor="r", role="mono")


def a_orders(fr, c):
    g = ORD["g01"]
    histo(fr, 160, 230, 760, [(L(f"{r} 轮", f"{r} rounds"), n) for r, n in sorted(g["rounds"].items())],
          L(f"G01 · 全部 {g['orders']} 种访问顺序", f"G01 · ALL {g['orders']} VISIT ORDERS"), c.p(0), TEAL, tr)
    fr.text(L(f"分组都是 {g['outcomes'][0]['grouping'].replace(',', '')}", f"every order gives {g['outcomes'][0]['grouping'].replace(',', '')}"), 190, 520, 26, TEAL, c.p(0))
    if c.on(2):
        cc = ORD["circuit"]
        a = c.p(2)
        histo(fr, 1000, 230, 760, [(L(f"{o['sizes']} · cut {o['cut']}", f"{o['sizes']} · cut {o['cut']}"), o["count"]) for o in cc["outcomes"]],
              L(f"24 单元电路 · {cc['orders']} 个随机顺序", f"24-CELL CIRCUIT · {cc['orders']} RANDOM ORDERS"), a, TEAL, tr)
        rr = ", ".join(f"{r}:{n}" for r, n in sorted(cc["rounds"].items()))
        fr.text(L(f"轮数分布 {rr}", f"rounds {rr}"), 1030, 520, 22, MUTED, a, role="mono")


def a_orders_circ(fr, c):
    cc = ORD["circuit"]
    best, worst = cc["outcomes"][0], cc["outcomes"][-1]

    def labels_of(o):
        lab = {}
        for gi, grp in enumerate(o["grouping"].split(" | ")):
            for n in grp.split(","):
                lab[n] = f"G{gi}"
        return lab
    o = best if not c.on(1) else worst
    pos = fit({k: tuple(v) for k, v in CIRC["positions"].items()}, (170, 230, 1130, 760))
    circuit(fr, labels_of(o), 1.0, pos, colors={"G0": TEAL, "G1": GOLD, "G2": BLUE, "G3": ROSE})
    panel(fr, 1240, 260, 520, 360, 1.0, L("同一张图，不同顺序", "SAME GRAPH, ANOTHER ORDER"))
    fr.text(o["sizes"], 1280, 380, 44, TEAL if o is best else ROSE, 1.0, role="serif")
    fr.text(f"cut {o['cut']}", 1280, 450, 40, TEAL if o is best else ROSE, 1.0, role="serif")
    fr.text(L(f"{o['count']} / {cc['orders']} 个顺序", f"{o['count']} of {cc['orders']} orders"), 1280, 520, 24, MUTED, 1.0)


# --- cost
CON = T["contacts"]


def a_cost(fr, c):
    m = len(CON["graph"]["edges"])
    rounds = CON["run"]["result"]["rounds"]
    panel(fr, 260, 240, 1400, 460, c.p(0), L("一轮的工作量", "THE WORK IN ONE ROUND"))
    math_line(fr, [(L("每轮读邻居  =  Σ", "neighbour reads per round  =  Σ"), IVORY), ("v", MUTED, "under"), ("  deg(v)  =  2m", IVORY)], W / 2, 380, 52, c.p(0))
    if c.on(1):
        a = c.p(1)
        fr.text(L(f"通讯录：m = {m} 条联系 → 每轮 {2 * m} 次读取；{rounds} 轮停下，共 {2 * m * rounds} 次",
                  f"Contacts: m = {m} ties → {2 * m} reads per round; stable after {rounds} rounds, {2 * m * rounds} reads in all"), W / 2, 480, 28, TEAL, a, anchor="c")
    if c.on(2):
        a = c.p(2)
        fr.text(L("对照：24 个单元平分三组就有 1,577,585,295 种分法", "Compare: 24 cells split into three equal groups in 1,577,585,295 ways"), W / 2, 560, 26, MUTED, a, anchor="c")
        fr.text(L("轮数通常很少：这就是论文说的“近线性时间”", "Rounds are usually few: that is the paper's \"near linear time\""), W / 2, 630, 26, GOLD, a * c.p(3) if c.on(3) else 0, anchor="c")


# --- the trivial fixed point
TRI = T["twoTriangles"]
TPOS = {"A": (300, 330), "B": (300, 650), "C": (540, 490), "D": (860, 490), "E": (1100, 330), "F": (1100, 650)}
TE = [tuple(e) for e in TRI["graph"]["edges"]]


def tri_view(fr, run, alpha=1.0, ox=0):
    lab = run["result"]["labels"]
    universe = sorted(set(lab.values()))
    cols = {l: [TEAL, GOLD, BLUE, ROSE, LILAC, SAGE][i] for i, l in enumerate(universe)}
    pos = {k: (v[0] + ox, v[1]) for k, v in TPOS.items()}
    graph(fr, pos, TE, {n: cols[lab[n]] for n in lab}, alpha, r=36, cut=cut_keys(TE, lab), badges={n: f"{tr(LW)} {lab[n]}" for n in lab},
          badge_cols={n: cols[lab[n]] for n in lab}, badge_dirs={"C": (0, 1), "D": (0, 1)})


def a_monster(fr, c):
    run = TRI["min"] if c.k < 3 else TRI["max"] if c.k < 4 else TRI["cap3"]
    tri_view(fr, run, 1.0, -60)
    r = run["result"]
    title = {0: L("两个三角形，一座桥", "Two triangles, one bridge"), 1: L("平票取最小 (min)", "ties → smallest (min)"), 2: L("平票取最小 (min)", "ties → smallest (min)"),
             3: L("平票取最大 (max)", "ties → largest (max)"), 4: L("组大小上限 U = 3", "group size cap U = 3")}[min(c.k, 4)]
    panel(fr, 1250, 300, 520, 300, 1.0, L("结果", "RESULT"))
    fr.text(title, 1290, 400, 28, GOLD, 1.0)
    if c.k >= 1:
        fr.text(r["grouping"].replace(",", ""), 1290, 470, 34, IVORY, 1.0, role="serif")
        fr.text(f"cut {r['cut']}", 1290, 530, 34, TEAL if r["cut"] else ROSE, 1.0, role="serif")


# --- variants and coarsening
CAP = T["circuitCap4"]["result"]


def coarse_graph():
    lab = CAP["labels"]
    groups = {}
    for n, l in lab.items():
        groups.setdefault(l, []).append(n)
    cen = {l: (sum(CPOS[n][0] for n in ns) / len(ns), sum(CPOS[n][1] for n in ns) / len(ns)) for l, ns in groups.items()}
    w = {}
    for u, v, ww in CIRC["edges"]:
        a, b = lab[u], lab[v]
        if a != b:
            k = tuple(sorted((a, b)))
            w[k] = w.get(k, 0) + ww
    return groups, cen, [(a, b, x) for (a, b), x in sorted(w.items())]


GROUPS4, CEN4, CE4 = coarse_graph()
CAPCOL = {l: HUES[i % len(HUES)] for i, l in enumerate(sorted(GROUPS4))}


def a_variants(fr, c):
    items = [(L("LPAm（Barber 与 Clark，2009）", "LPAm (Barber & Clark, 2009)"),
              L("在投票里加入模块度惩罚，阻止一组吞掉一切。", "adds a modularity penalty to the vote, so one group cannot swallow everything.")),
             (L("限制组大小（Meyerhenke、Sanders、Schulz，2014）", "Size-constrained (Meyerhenke, Sanders & Schulz, 2014)"),
              L("只允许加入不超过上限 U 的组；用来给多层划分器做粗化。", "a node may only join a group that stays within a cap U; used to coarsen graphs in multilevel partitioners.")),
             (L("另外常见：随机顺序多跑几次再比较", "Also common: random orders, several runs, then compare"),
              L("把结果的波动当作信息，而不是噪声。", "treat the spread of results as information, not noise."))]
    for i, (h, b) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 240 + i * 170
            fr.rect(260, y, 1400, 140, fill=PANEL_BG, stroke=GOLD if i == 1 else FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(h, 310, y + 56, 30, GOLD if i == 1 else IVORY, a, bold=True)
            fr.text(b, 310, y + 104, 24, MUTED, a)


def a_coarsen(fr, c):
    lab = CAP["labels"]
    k = c.p(2, 1.6) if c.on(2) else 0.0
    circuit(fr, lab if c.on(1) else None, 1.0 - k, CPOS, colors=CAPCOL, cut=True)
    if k > 0:
        for a, b, w in CE4:
            fr.line(CEN4[a], CEN4[b], "#7aa5a6", 1 + w * 0.25, 0.7 * k)
            m = ((CEN4[a][0] + CEN4[b][0]) / 2, (CEN4[a][1] + CEN4[b][1]) / 2)
            fr.dot(m, 16, "#0a1c24", k)
            fr.text(f"{w}", m[0], m[1] + 6, 16, MUTED, k, anchor="c")
        for l, ns in GROUPS4.items():
            r = 18 + 9 * len(ns)
            fr.dot(CEN4[l], r, NODE_BG, k)
            fr.ring(CEN4[l], r, CAPCOL[l], 3, k, glow=0.4 * k)
            fr.text(str(len(ns)), CEN4[l][0], CEN4[l][1] + 10, 28, IVORY, k, role="serif", anchor="c")
    panel(fr, 1260, 250, 520, 420, 1.0, L("粗化一层", "ONE COARSENING LEVEL"))
    fr.text(L("上限 U = 4", "cap U = 4"), 1300, 340, 30, GOLD, 1.0)
    if c.on(1):
        sizes = "+".join(str(len(v)) for v in sorted(GROUPS4.values(), key=len, reverse=True))
        fr.text(L(f"{len(GROUPS4)} 组：{sizes}", f"{len(GROUPS4)} groups: {sizes}"), 1300, 400, 26, IVORY, c.p(1))
        fr.text(L(f"组间连线权重 {CAP['cut']}", f"weight between groups {CAP['cut']}"), 1300, 450, 26, ROSE, c.p(1))
    if c.on(2):
        fr.paragraph(L(f"每组收缩成一个点：24 个单元变成 {len(GROUPS4)} 个，再在小图上划分。",
                       f"Contract each group to one node: 24 cells become {len(GROUPS4)}, and the small graph is partitioned."), 1300, 520, 24, 440, TEAL, c.p(2))


def a_summary(fr, c):
    items = [(L("异步 + 严格改进：cut 只降不升，一定停下", "Async + strict improvement: the cut only falls, so it stops"), TEAL),
             (L("同步：读旧快照，二分结构会来回交换", "Sync: stale snapshots make bipartite parts swap forever"), ROSE),
             (L("停止判定、平票与顺序都要写清楚", "State the stopping test, the tie rule and the order"), GOLD),
             (L("每轮 2m 次读取；没有均衡，需要约束才能用于划分", "2m reads a round; no balance, so partitioning needs constraints"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 250 + i * 120
            fr.rect(260, y, 1400, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 310, y + 58, 28, col, a, role="mono")
            fr.text(s, 400, y + 58, 30, IVORY, a)


_pot_beats = [Beat(L("把 cut 当成一个计数器。开始时每条边都被切开：cut = 18。", "Treat the cut as a counter. At the start every edge is cut: cut = 18."), 3.2)]
for _e in GEV:
    if _e["changed"]:
        _d = _e["votes"][_e["label"]] - _e["votes"].get(_e["old"], 0)
        _pot_beats.append(Beat(L(f"{_e['node']} 改为 {_e['label']}：这 {_d:g} 的权重不再被切开，cut 减 {_d:g}。",
                                 f"{_e['node']} switches to {_e['label']}: {_d:g} of weight is no longer cut, so the cut drops by {_d:g}."), 2.4))
    else:
        _pot_beats.append(Beat(L(f"{_e['node']} 不变，cut 也不变。", f"{_e['node']} stays, and so does the cut."), 1.2))

_O1, _O2 = ORD["circuit"]["outcomes"][0], ORD["circuit"]["outcomes"][1]
_M, _R = len(CON["graph"]["edges"]), CON["run"]["result"]["rounds"]
assert len(ORD["circuit"]["outcomes"]) == 2 and set(ORD["g01"]["rounds"]) == {"2", "3"} and len(ORD["g01"]["outcomes"]) == 1
assert STAR["sync"]["events"][-1]["period"] == 2 and T["syncG01"]["result"]["cut"] == 17 and TRI["min"]["result"]["cut"] == 0
assert max(len(v) for v in GROUPS4.values()) <= 4

ADVANCED = Film(
    "advanced", "advanced", L("进阶：为什么停，为什么不停", "In depth: why it stops, and why it may not"), None, BRAND, poster_at=70.0, music="score:calm", seed=33,
    why=L("给想深入的人：异步停机的论证、同步振荡、两种停止判定、访问顺序、复杂度、平凡解，以及限制组大小的变体如何用于电路粗化。",
          "For those who want more: why asynchronous updates stop, synchronous oscillation, two stopping tests, order dependence, cost, the trivial fixed point, and how a size-constrained variant coarsens circuits."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.2)]),
        Scene("a01-recap", a_recap, [Beat(L("规则还是那一句：跟着邻居里权重最大的标签走。", "The rule is unchanged: follow the label with the most neighbour weight."), 3.0),
                                      Beat(L("这一部回答四个问题。", "This film answers four questions."), 4.0)], chapter=L("回顾", "RECAP")),
        Scene("a02-potential", a_potential, _pot_beats + [Beat(L("规律：异步改一次标签，cut 正好减少“新票 − 旧票”。", "The law: one asynchronous change lowers the cut by exactly new votes − old votes."), 3.6)],
              chapter=L("一 · 异步为什么会停", "I · WHY ASYNC STOPS")),
        Scene("a03-proof", a_proof, [Beat(L("如果只在新标签的票严格更多时才改，", "If a node changes only when the new label has strictly more votes,"), 2.6),
                                      Beat(L("每次改动 cut 至少降 1，", "each change lowers the cut by at least 1,"), 2.2),
                                      Beat(L("而 cut 不能低于 0，", "and the cut cannot go below 0,"), 1.8),
                                      Beat(L("所以改动只能有限次：异步更新一定停下。", "so there can only be finitely many changes: asynchronous updates stop."), 3.0),
                                      Beat(L("平票也改的规则不在这个论证之内。", "Rules that also change on a tie fall outside this argument."), 3.4)]),
        Scene("a04-star", a_star, [Beat(L("同步就不同了：所有点同时根据旧快照改。", "Synchronous updates are different: every node changes at once, from an old snapshot."), 2.6),
                                    Beat(L("星形图：中心随叶子改，叶子随中心改。", "A star: the hub follows the leaves while the leaves follow the hub."), 4.4),
                                    Beat(L("于是两边互换标签，cut 一直是 4。", "So the two sides trade labels and the cut stays at 4."), 2.8),
                                    Beat(L("第 3 轮回到第 1 轮：周期为 2 的循环。", "Round 3 repeats round 1: a cycle of period 2."), 3.0)],
              chapter=L("二 · 同步为什么振荡", "II · WHY SYNC OSCILLATES")),
        Scene("a05-sync5", a_sync5, [Beat(L("课程的 G01 同步也一样：cut 停在 17，周期 2。", "G01 under synchronous updates does the same: the cut sits at 17, period 2."), 3.4),
                                      Beat(L("二分或接近二分的结构，最容易这样来回交换。", "Bipartite and near-bipartite structures swap like this most easily."), 3.4)]),
        Scene("a06-stoptests", a_stoptests, [Beat(L("本课程的判定：完整一轮零变化才算 stable。", "This course's test: stable means a full round with no change."), 3.0),
                                              Beat(L("每轮结束记下整张标签表，重复出现就报告 cycle。", "Store the labelling at each round end; a repeat is reported as a cycle."), 3.2),
                                              Beat(L("原论文每轮随机打乱顺序，平票也随机。", "The paper shuffles the order each round and breaks ties at random."), 3.0),
                                              Beat(L("所以它换了判据：每个点的标签都是邻居中最多的之一，就停。", "So it uses another test: stop when each node holds one of its neighbours' most common labels."), 4.0)],
              chapter=L("三 · 两种停止判定", "III · TWO STOPPING TESTS")),
        Scene("a07-orders", a_orders, [Beat(L("访问顺序会改变什么？G01 的全部 120 种顺序：", "What does the visit order change? All 120 orders on G01:"), 3.0),
                                        Beat(L("分组都一样，只有轮数在 2 和 3 之间变化。", "the groups never change; only the rounds vary between 2 and 3."), 3.0),
                                        Beat(L("24 单元电路试 300 个随机顺序：", "On the 24-cell circuit, 300 random orders:"), 2.4),
                                        Beat(L(f"{_O1['count']} 次分成 {_O1['sizes']}、cut {_O1['cut']}；{_O2['count']} 次多切开一组，cut {_O2['cut']}。", f"{_O1['count']} give {_O1['sizes']} with cut {_O1['cut']}; {_O2['count']} split a group in two, cut {_O2['cut']}."), 3.6)],
              chapter=L("四 · 访问顺序", "IV · VISIT ORDER")),
        Scene("a08-orders-circ", a_orders_circ, [Beat(L("多数顺序找到三块；", "Most orders find the three blocks;"), 2.4),
                                                  Beat(L("少数顺序让中间一块被两个标签瓜分，停在一个更差的稳定状态。", "a few let two labels share the middle block, and it stops in a worse stable state."), 3.8)]),
        Scene("a09-cost", a_cost, [Beat(L("代价：一轮里每个点读一遍邻居，每条边被读两次。", "Cost: in one round every node reads its neighbours once, so every edge is read twice."), 3.4),
                                    Beat(L(f"通讯录 {_M} 条联系：每轮 {2 * _M} 次读取，{_R} 轮就停。", f"The {_M} contact ties: {2 * _M} reads per round, stable after {_R} rounds."), 3.0),
                                    Beat(L("相比之下，穷举分法根本数不完。", "Exhaustive search, by contrast, cannot even be counted through."), 2.6),
                                    Beat(L("只要轮数少，总工作量就和边数成正比。", "With few rounds, the total work grows in proportion to the number of edges."), 3.0)],
              chapter=L("五 · 代价", "V · COST")),
        Scene("a10-monster", a_monster, [Beat(L("再看一个陷阱：两个三角形，中间一座桥。", "One more trap: two triangles joined by a bridge."), 2.6),
                                          Beat(L("平票取最小：所有点最后都成了同一个标签，cut = 0。", "Ties to the smallest: every node ends up with one label, cut = 0."), 3.4),
                                          Beat(L("cut 最小的分法就是“全部一组”。这个规则没有任何力量阻止合并。", "The lowest cut of all is “everything in one group”. Nothing in the rule resists merging."), 4.2),
                                          Beat(L("换成平票取最大，恰好分开两个三角形。", "With ties to the largest it happens to split the two triangles."), 3.0),
                                          Beat(L("给组大小设上限 U = 3，结果不再依赖平票的运气。", "Cap each group at U = 3, and the result no longer rests on luck with ties."), 3.4)],
              chapter=L("六 · 一组吞掉一切", "VI · ONE GROUP TAKES ALL")),
        Scene("a11-variants", a_variants, [Beat(L("常见的改法有两类。", "Two common fixes."), 1.8),
                                            Beat(L("限制组大小的版本，正是多层划分器里常用的粗化手段。", "The size-constrained version is a common coarsening step in multilevel partitioners."), 3.6),
                                            Beat(L("此外，随机顺序多跑几次，比较结果的波动。", "Besides that: run several random orders and compare how much the results move."), 3.0)],
              chapter=L("七 · 变体与芯片", "VII · VARIANTS AND CHIPS")),
        Scene("a12-coarsen", a_coarsen, [Beat(L("回到 24 单元电路，给每组设上限 U = 4。", "Back to the 24-cell circuit, with a cap of U = 4 per group."), 2.8),
                                          Beat(L(f"标签传播分出 {len(GROUPS4)} 个小组，每组不超过 4 个单元。", f"Label propagation forms {len(GROUPS4)} small groups, none over 4 cells."), 3.0),
                                          Beat(L(f"每组收缩成一个点：24 个单元的图变成 {len(GROUPS4)} 个点的小图。", f"Each group contracts to one node: the 24-cell graph becomes a {len(GROUPS4)}-node graph."), 3.4),
                                          Beat(L("在小图上划分，再逐层展开、细化。这就是多层划分的第一步。", "Partition the small graph, then expand and refine level by level: the first step of multilevel partitioning."), 4.2)]),
        Scene("a13-summary", a_summary, [Beat(L("四句话带走：", "Four things to take away:"), 1.6),
                                          Beat(L("异步加严格改进，一定停；", "async with strict improvement always stops;"), 2.2),
                                          Beat(L("同步可能永远交换；", "sync can trade labels forever;"), 2.0),
                                          Beat(L("规则要写清楚；它快，但需要约束才能用来划分芯片。", "state your rules; it is fast, but partitioning a chip needs constraints."), 3.6)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [CONCISE, ADVANCED]
# Order on the page: popular science (imported by import_story.py), concise, advanced, walkthrough (walkthrough.py).
ORDER = ["story", "concise", "advanced", "lab"]
