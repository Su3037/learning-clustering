"""Module 05 · 标签传播 —— 核心片《圈子从哪里来》与慢速推演《一票一票》.
Narrative follows the author's own Lab05 film; every label, vote, round and cut is read from
site/data/m05-label-propagation/traces.json (engines/lp.js, adapted from the author's engine)."""
from types import SimpleNamespace
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, PINK, GREEN, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, bar, number_box)

T = load_trace("m05-label-propagation")
G = T["g01"]
POS5 = fit({k: tuple(v) for k, v in G["positions"].items()}, (230, 240, 900, 790))
E5 = [tuple(e) for e in G["edges"]]
GOLDEN = T["golden"]
CIRC, CRUN = T["circuit"]["graph"], T["circuit"]["run"]
CON, CONRUN = T["contacts"]["graph"], T["contacts"]["run"]
LABEL_COLOR = {}


def lab_color(label, universe):
    """Stable colour for a label name within one graph."""
    key = (tuple(sorted(universe)), label)
    if key not in LABEL_COLOR:
        LABEL_COLOR[key] = GROUP[sorted(universe).index(label) % len(GROUP)] if label in universe else "#a9bdb8"
    return LABEL_COLOR[key]


def round_states(run):
    """Labels after each complete round (index 0 = initial)."""
    nodes = sorted(run["result"]["labels"])
    states = [{n: n for n in nodes}]
    for e in run["events"]:
        if e["kind"] == "update-round-end":
            states.append(dict(e["after"]))
    return states


def big_graph(cv, g, pos, labels, alpha=1.0, r=15, names=None, colorize=True, cut_hl=True):
    universe = g["nodes"]
    if labels and not set(labels.values()) <= set(universe):
        universe = sorted(set(labels.values()))  # labels such as L/M/R rather than node names
    for u, v, w in g["edges"]:
        diff = labels and labels[u] != labels[v]
        st = "cut" if (diff and cut_hl) else "normal"
        cv.line(*pos[u], *pos[v], "#db7b72" if st == "cut" else "#4f7377", 2.4 if st == "cut" else 1.8, alpha * (0.95 if st == "cut" else 0.7), dash=[8, 6] if st == "cut" else None)
    for n in g["nodes"]:
        x, y = pos[n]
        col = lab_color(labels[n], universe) if (labels and colorize) else "#a9bdb8"
        cv.circle(x, y, r, fill=col, stroke="#061418", width=2, alpha=alpha)
        if names:
            cv.text(x, y + r + 22, names.get(n, n), 18, MUTED, align="center", alpha=alpha)


def cut_of(g, labels):
    return sum(w for u, v, w in g["edges"] if labels[u] != labels[v])


# ------------------------------------------------------------------ core film
CPOS = fit({k: tuple(v) for k, v in CON["positions"].items()}, (200, 200, 1250, 820))
CIRCPOS = fit({k: tuple(v) for k, v in CIRC["positions"].items()}, (160, 210, 1290, 800))
CONSTATES = round_states(CONRUN)
CIRCSTATES = round_states(CRUN)


def s_title(cv, c):
    title_card(cv, "圈子从哪里来", "Label propagation · Module 05", c.p(0, 1.2))


def s_contacts(cv, c):
    big_graph(cv, CON, CPOS, None, c.p(0, 1.2), 16, CON.get("names"))
    panel(cv, 1330, 220, 470, 420, "一本通讯录", c.p(1))
    if c.on(1):
        cv.paragraph(1370, 320, f"{len(CON['nodes'])} 个名字，{len(CON['edges'])} 条联系。线越粗，联系越多（虚构）。", 30, 400, INK, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1370, 470, "怎样分成几个圈子？只看谁和谁常联系。", 30, 400, GOLD, alpha=c.p(2))


def s_gather(cv, c):
    k = min(c.k, len(CONSTATES) - 1)
    labels = CONSTATES[k]
    big_graph(cv, CON, CPOS, labels, 1.0, 16, CON.get("names"))
    panel(cv, 1330, 220, 470, 520, "看邻居，跟最强")
    cv.text(1370, 320, f"第 {k} 轮" if k else "开始：每人一个标签", 34, GOLD, "bold")
    groups = {}
    for n, l in labels.items():
        groups.setdefault(l, []).append(n)
    cv.text(1370, 390, f"{len(groups)} 个标签", 30, INK)
    cv.text(1370, 450, f"切开的联系 {cut_of(CON, labels)}", 30, RED if k < len(CONSTATES) - 1 else TEAL)
    if k == len(CONSTATES) - 1:
        sizes = sorted((len(v) for v in groups.values()), reverse=True)
        tag(cv, 1565, 560, f"{' + '.join(map(str, sizes))} 人 · {CONRUN['result']['rounds']} 轮停下", TEAL, 1.0, 26)


def s_chip(cv, c):
    geo = T["circuit"]["geometric"]
    big_graph(cv, CIRC, CIRCPOS, geo["labels"] if c.on(1) else None, 1.0, 18, None, colorize=c.on(1))
    if c.on(1):
        for xline in (700, 1200):
            x = fit({"a": (xline, 172), "b": (xline, 822), **{k: tuple(v) for k, v in CIRC["positions"].items()}}, (160, 210, 1290, 800))["a"][0]
            cv.line(x, 200, x, 820, GOLD, 3, c.p(1), dash=[12, 8])
    panel(cv, 1350, 220, 450, 520, "芯片里的同一个问题")
    cv.paragraph(1390, 320, f"{len(CIRC['nodes'])} 个单元，{len(CIRC['edges'])} 条连线，总权 {sum(e[2] for e in CIRC['edges'])}（虚构）。", 30, 380, INK)
    if c.on(1):
        cv.paragraph(1390, 470, f"按位置拿尺子切三块：切断 {geo['cut']}。", 32, 380, RED, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1390, 590, "平分三组就有 1,577,585,295 种——试不完。", 28, 380, MUTED, alpha=c.p(2))


def s_rule(cv, c):
    panel(cv, 260, 230, 1400, 500, None)
    formula(cv, W / 2, 400, [("新标签(v) = ", INK), ("argmax", GOLD), ("  Σ  w(u, v)", INK)], 60, c.p(0))
    cv.text(W / 2, 470, "对每个候选标签 L：把带着 L 的邻居 u 的边权加起来，取最大", 30, MUTED, align="center", alpha=c.p(0))
    if c.on(1):
        items = ["“最强”怎么算？", "谁先更新？", "什么时候停？", "一定会停吗？", "平票怎么办？", "分得好不好？"]
        for i, s in enumerate(items):
            x = 360 + (i % 3) * 420
            y = 590 + (i // 3) * 90
            cv.text(x, y, s, 32, GOLD if i == c.k - 1 else INK, alpha=c.p(1))


def g5_labels(cv, labels, focus=None, alpha=1.0, tags=True, edge_state=None):
    universe = ["A", "B", "C", "D", "E"]
    for u, v, w in E5:
        st = (edge_state or {}).get(f"{u}|{v}") or ("cut" if labels[u] != labels[v] else "inside")
        edge(cv, POS5[u], POS5[v], w, st, alpha)
    for n, p in POS5.items():
        node(cv, *p, n, lab_color(labels[n], universe), 40, alpha, GOLD if focus == n else None)
        if tags:
            tag(cv, p[0], p[1] + 84, f"标签 {labels[n]}", lab_color(labels[n], universe), alpha, 22)


def ballot(cv, x, y, votes, winner, p=1.0, title="票数"):
    panel(cv, x, y, 560, 120 + 80 * max(1, len(votes)), title)
    mx = max([1] + list(votes.values()))
    for i, (l, v) in enumerate(sorted(votes.items(), key=lambda t: (-t[1], t[0]))):
        yy = y + 110 + i * 80
        cv.text(x + 30, yy, f"标签 {l}", 30, INK)
        bar(cv, x + 170, yy - 22, 280 * clamp(p * 1.2 - i * 0.15), 22, v / mx, GOLD if l == winner else TEAL)
        cv.text(x + 520, yy, str(v), 34, GOLD if l == winner else INK, "bold", "right", alpha=clamp(p * 2 - i * 0.3))


def s_labels(cv, c):
    g5_labels(cv, {n: n for n in "ABCDE"})
    panel(cv, 1080, 230, 700, 460, "第 1 层 · 名字与标签")
    lines = ["名字是身份：A 永远是 A。", "标签是归属：会被改写。", "开始时，标签就是自己的名字。"]
    for i, s in enumerate(lines):
        if c.on(i):
            cv.text(1120, 340 + i * 100, s, 34, GOLD if i == 1 else INK, alpha=c.p(i))


def s_vote(cv, c):
    ev = next(e for e in GOLDEN["events"] if e["round"] == 1 and e["node"] == "C")
    g5_labels(cv, ev["before"], "C", edge_state={"A|C": "hl", "B|C": "hl"} if c.on(1) else None)
    ballot(cv, 1160, 230, ev["votes"], ev["label"] if c.on(2) else None, c.p(1, 1.2), "C 的票（第 1 轮）")
    if c.on(3):
        cv.paragraph(1180, 700, "比的是边权之和，不是邻居个数。", 32, 560, GOLD, alpha=c.p(3))


def s_round(cv, c):
    r1 = [e for e in GOLDEN["events"] if e["round"] == 1]
    k = min(c.k, 2)
    labels = {n: n for n in "ABCDE"} if k == 0 else (r1[-1]["after"])
    g5_labels(cv, labels)
    rows = [["访问", "票数", "新标签", "改变"]] + [[e["node"], "，".join(f"{l}:{v}" for l, v in e["votes"].items()), e["label"], "是" if e["changed"] else "否"] for e in r1]
    panel(cv, 1020, 190, 820, 520, "第 1 轮（异步，A→E）")
    table(cv, 1060, 290, [110, 330, 170, 120], rows[: 1 + (5 if c.on(1) else 1)], 30, 64)
    if c.on(2):
        tag(cv, 1430, 760, f"第 2 轮：全部不变 → stable，共 {GOLDEN['result']['rounds']} 轮，cut {GOLDEN['result']['cut']}", TEAL, c.p(2), 26)


def s_sync(cv, c):
    pr = T["pairSync"]
    states = [{"A": "A", "B": "B"}] + [e["after"] for e in pr["events"] if e["kind"] == "update-round-end"]
    k = min(int(c.since(1) / 1.6), len(states) - 1) if c.on(1) else 0
    lab = states[k]
    pa, pb = (560, 480), (1360, 480)
    edge(cv, pa, pb, 1, "cut" if lab["A"] != lab["B"] else "inside")
    for n, p in (("A", pa), ("B", pb)):
        node(cv, *p, n, lab_color(lab[n], ["A", "B"]), 64, size=44)
        tag(cv, p[0], p[1] + 130, f"标签 {lab[n]}", lab_color(lab[n], ["A", "B"]), 1.0, 30)
    cv.text(W / 2, 300, "同步：大家读同一张旧快照，轮末一起提交", 34, GOLD, align="center", alpha=c.p(0))
    if c.on(1):
        cv.text(W / 2, 760, f"第 {k} 轮", 30, MUTED, align="center")
    if c.on(2):
        tag(cv, W / 2, 840, f"状态重复 → cycle（G01 同步也会以周期 2 振荡，cut 停在 {T['syncG01']['result']['cut']}）", RED, c.p(2), 26)


def s_bridge(cv, c):
    h = T["heavy"]
    labels = h["result"]["labels"] if c.on(1) else GOLDEN["result"]["labels"]
    for u, v, w in E5:
        ww = 10 if (u, v) == ("C", "D") else w
        st = "hl" if (u, v) == ("C", "D") else ("cut" if labels[u] != labels[v] else "inside")
        edge(cv, POS5[u], POS5[v], ww, st)
    for n, p in POS5.items():
        node(cv, *p, n, lab_color(labels[n], list("ABCDE")), 40)
    number_box(cv, 1250, 260, 420, 170, "C–D 改为 10，重新运行", f"cut {h['result']['cut']}" if c.on(1) else "cut 3", GOLD, 1.0, 64)
    if c.on(1):
        cv.paragraph(1250, 520, f"D 把 C 拉了过去：{h['result']['grouping'].replace(',', '')}。", 32, 520, INK, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1250, 640, "比较不同参数时，要从同一个初始状态重新开始。", 28, 520, MUTED, alpha=c.p(2))


def s_circuit(cv, c):
    k = min(c.k * 2, len(CIRCSTATES) - 1) if c.k < 3 else len(CIRCSTATES) - 1
    labels = CIRCSTATES[k]
    big_graph(cv, CIRC, CIRCPOS, labels, 1.0, 18)
    panel(cv, 1350, 220, 450, 520, "回到芯片")
    cv.text(1390, 320, f"第 {k} 轮" if k else "开始", 34, GOLD, "bold")
    cv.text(1390, 390, f"切断 {cut_of(CIRC, labels)}", 34, RED if k < len(CIRCSTATES) - 1 else TEAL, "bold")
    if k == len(CIRCSTATES) - 1:
        cv.paragraph(1390, 480, f"{CRUN['result']['rounds']} 轮停下，只切断 {CRUN['result']['cut']}；尺子切法是 {T['circuit']['geometric']['cut']}。", 28, 380, INK)
        cv.paragraph(1390, 620, "虚构教学图；不说明一般最优。", 24, 380, MUTED)


def s_limits(cv, c):
    items = ["不指定 K，也不保证各组大小均衡", "结果依赖访问顺序、同步/异步与平票规则", "同步可能振荡：要报告 cycle，而不是说收敛", "下一模块：不再局部投票，改用全图的谱信息"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


CORE = SimpleNamespace(
    ID="circles", TITLE="圈子从哪里来", MODULE="Module 05 · 标签传播", MOOD="curious", SEED=5, POSTER_AT=40.0,
    WHY="核心片约 3 分半：通讯录→芯片→一条规则→逐层拆开；慢速推演另成一段，一票一票走完 G01。",
    SCENES=[
        Scene("s00-title", s_title, [Beat("", 2.6)]),
        Scene("s01-contacts", s_contacts, [Beat("一本通讯录，几十个名字。", 2.4), Beat("只要看：谁和谁常联系。", 2.6), Beat("没有人画圈，圈子能自己浮现吗？", 3.0)], chapter="序 · 通讯录"),
        Scene("s02-gather", s_gather, [Beat("每个人看看朋友们现在属于哪个圈子，", 2.8), Beat("然后加入联系最多的那一个。", 2.6), Beat("一遍遍重复……", 2.0), Beat("圈子自己浮现，切开的联系越来越少。", 3.2)], chapter="一 · 一个极简的办法"),
        Scene("s03-chip", s_chip, [Beat("芯片里是同一个问题：单元由导线连成一张网。", 3.4), Beat("按位置拿尺子切成三块，会切断很多连线。", 3.4), Beat("试遍所有分法？光是 24 个单元平分三组就有十五亿种。", 3.8)], chapter="二 · 芯片里的同一个问题"),
        Scene("s04-rule", s_rule, [Beat("把通讯录的规则借过来：看邻居的标签，跟最强的那一组。", 3.8), Beat("这一句话，留下六个问题。", 2.6), Beat("“最强”怎么算？谁先更新？什么时候停？", 3.2)], chapter="三 · 一条局部规则"),
        Scene("s05-labels", s_labels, [Beat("回到课程的五节点图。先分清两个词。", 2.6), Beat("名字是身份，永远不变；标签是归属，可以改写。", 3.4), Beat("开始时，每个点的标签就是自己的名字。", 2.8)], chapter="四 · 逐层拆开"),
        Scene("s06-vote", s_vote, [Beat("轮到 C。A 已经改为标签 B，B 仍是 B。", 3.0), Beat("同一标签的边权加起来：B = 1 + 4 = 5。", 3.2), Beat("D = 2，E = 1。C 的标签改为 B。", 2.8), Beat("比的是权重之和，不是人数。", 2.6)]),
        Scene("s07-round", s_round, [Beat("一整轮：A、B、C、D、E 依次更新，每次立刻写回。", 3.4), Beat("第 1 轮结束：B B B E E，改了 3 个。", 3.2), Beat("第 2 轮全部不变，才确认稳定：共 2 轮。", 3.4)]),
        Scene("s08-sync", s_sync, [Beat("换成同步：大家读同一张旧快照。", 2.8), Beat("A 读到 B，B 读到 A——同时交换，再换回来。", 4.4), Beat("状态重复，永远停不下：这叫 cycle，不能叫收敛。", 3.6)], chapter="五 · 同步、平票与边权"),
        Scene("s09-bridge", s_bridge, [Beat("把 C–D 这座桥加粗到 10，重新运行。", 2.8), Beat("D 把 C 拉了过去：AB | CDE，cut 5。", 3.2), Beat("改了参数，要从同一个起点重新比较。", 3.0)]),
        Scene("s10-circuit", s_circuit, [Beat("回到 24 个单元的电路。", 2.2), Beat("颜色沿着最强的连线扩散。", 2.6), Beat("几轮之后，各块之间只剩很少的连线。", 3.0), Beat("尺子切 88，标签传播只切 2——这只是这张虚构图上的结果。", 4.0)], chapter="六 · 回到芯片"),
        Scene("s11-limits", s_limits, [Beat("标签传播的边界：", 1.6), Beat("规则一变，轮数和结果都可能变。", 2.6), Beat("同步可能振荡。", 2.0), Beat("下一模块：用全图的谱信息来分。", 3.0)], tail=1.2),
    ])


# ------------------------------------------------------------------ slow derivation film
def slow_scene(ev):
    def draw(cv, c):
        g5_labels(cv, ev["before"], ev["node"], edge_state={"|".join(sorted((ev["node"], nb["node"]))): "hl" for nb in ev["neighbors"]} if c.on(1) else None)
        ballot(cv, 1160, 230, ev["votes"], ev["label"] if c.on(1) else None, c.p(0, 1.0), f"第 {ev['round']} 轮 · {ev['node']} 的票")
        msg = f"{ev['node']}：{ev['old']} → {ev['label']}" if ev["changed"] else f"{ev['node']} 保持 {ev['old']}"
        tag(cv, 1440, 760, msg, GOLD if ev["changed"] else MUTED, c.p(1), 30)
    return draw


def s_slow_intro(cv, c):
    g5_labels(cv, {n: n for n in "ABCDE"})
    panel(cv, 1080, 260, 700, 380, "慢速推演")
    cv.paragraph(1120, 360, "A→E 异步，平票取字典序最小。每一票都在右边列出来。", 32, 620, INK, alpha=c.p(0))


def s_slow_end(cv, c):
    g5_labels(cv, GOLDEN["result"]["labels"])
    panel(cv, 1080, 260, 700, 380, "结果")
    cv.paragraph(1120, 360, f"第 2 轮零变化 → stable。{GOLDEN['result']['rounds']} 轮，分组 {GOLDEN['result']['grouping'].replace(',', '')}，cut {GOLDEN['result']['cut']}。", 32, 620, INK, alpha=c.p(0))


def _slow_beats(ev):
    votes = "，".join(f"{l} = {v}" for l, v in sorted(ev["votes"].items(), key=lambda t: (-t[1], t[0])))
    first = f"第 {ev['round']} 轮，轮到 {ev['node']}：{votes}。"
    second = f"{ev['node']} 的标签改为 {ev['label']}。" if ev["changed"] else f"{ev['label']} 最大，{ev['node']} 保持不变。"
    return [Beat(first, 3.0), Beat(second, 2.2)]


SLOW = SimpleNamespace(
    ID="slow", TITLE="一票一票（慢速推演）", MODULE="Module 05 · 标签传播", MOOD="calm", SEED=55, POSTER_AT=20.0, FADE_SCENES=True,
    WHY="慢速推演：两轮共 10 次更新，每次停留到票数读完。",
    SCENES=[Scene("t00-intro", s_slow_intro, [Beat("慢速推演：按 A→E 异步更新，平票取最小。", 3.4)], chapter="慢速推演 · 第 1 轮")]
    + [Scene(f"t{i + 1:02d}-{e['node']}{e['round']}", slow_scene(e), _slow_beats(e), chapter="第 2 轮 · 确认零变化" if (e["round"] == 2 and e["node"] == "A") else None) for i, e in enumerate(GOLDEN["events"])]
    + [Scene("t99-end", s_slow_end, [Beat("第 2 轮没有任何改变：确认稳定，共 2 轮，cut 3。", 3.6)], chapter="结果 · 稳定", tail=1.0)])

FILMS = [CORE, SLOW]
