"""Module 04 · 容量约束凝聚聚类 —— 影片《装得下吗》. Data: site/data/m04-size-constrained-agglomerative/traces.json."""
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, node, edge, panel, tag, table, code, title_card, fit, load_trace, hull, bar, number_box)

ID, TITLE = "capacity", "装得下吗"
MODULE = "Module 04 · 容量约束凝聚聚类"
MOOD, SEED = "steady", 4
WHY = "约 4 分钟：五节点部分压缩为一段对照，把时间留给“不可能”与“走错路”两个独立反例。"
T = load_trace("m04-size-constrained-agglomerative")
G01POS = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
G01E = [tuple(e) for e in T["g01"]["edges"]]
TRAP = T["graphs"]["greedy_trap"]
SUB = T["graphs"]["suboptimal"]
UNEVEN = T["uneven"]  # same engine: A has size 2, capacity 3, K = 2


def sizes_of(g):
    return {n if isinstance(n, str) else n["id"]: 1 if isinstance(n, str) else n.get("size", 1) for n in g["nodes"]}


def draw_state(cv, pos, edges, clusters, size, cap, focus=(), blocked=(), alpha=1.0, r=40, show_cap=True, colors=None):
    where = {m: c["label"] for c in clusters for m in c["members"]}
    for i, c in enumerate(clusters):
        if len(c["members"]) > 1:
            col = (colors or {}).get(c["label"], GROUP[i % len(GROUP)])
            hull(cv, [pos[m] for m in c["members"]], col, r + 24, alpha, f"{c['label']} · {c['size']}/{cap}" if show_cap else c["label"])
    for u, v, w in edges:
        edge(cv, pos[u], pos[v], w, "inside" if where[u] == where[v] else "cut", alpha)
    for n, p in pos.items():
        node(cv, *p, n, "#a9bdb8", r, alpha, RED if n in blocked else (GOLD if n in focus else None))
        cv.text(p[0], p[1] + r + 34, f"s={size[n]}", 24, MUTED, "bold", "center", alpha=alpha)


def events(run, kind=None):
    return [e for e in run["events"] if kind is None or e["kind"] == kind]


def s_title(cv, c):
    title_card(cv, "装得下吗", "Size-constrained agglomerative clustering · Module 04", c.p(0, 1.2))


def s_hook(cv, c):
    pos = fit(G01POS, (200, 230, 900, 790))
    ev = events(T["cap2"]["run"], "merge")[0]
    draw_state(cv, pos, G01E, ev["after"], sizes_of(T["g01"]), 2, focus=("A", "B", "C") if c.on(1) else ())
    panel(cv, 1080, 200, 700, 380, "一个簇最多放 2 个单元")
    for i in range(3):
        col = TEAL if i < 2 else RED
        cv.rect(1130 + i * 150, 330, 130, 90, fill=col, r=10, alpha=(1 if i < 2 else c.p(1)))
    cv.line(1130 + 2 * 150 - 10, 300, 1130 + 2 * 150 - 10, 450, GOLD, 4, 1.0, dash=[8, 6])
    cv.text(1130, 500, "AB 已经满了。C 连得很紧，却放不进去。", 30, INK, alpha=c.p(1))
    if c.on(2):
        tag(cv, 1430, 680, "这时该怎么办？", GOLD, c.p(2))


def s_terms(cv, c):
    panel(cv, 160, 170, 1600, 640, "四件事，分开报告")
    rows = [["报告项", "含义", "G01，容量 2，K = 2"], ["count", "实际簇数", "3"], ["capacityCompliant", "每簇大小 ≤ C", "是"], ["targetReached", "簇数 ≤ K", "否"], ["stopReason", "为什么停下", "capacity-blocked"]]
    shown = 1 + min(4, c.k + 1)
    table(cv, 220, 290, [430, 430, 560], rows[:shown], 36, 92, {3: GOLD} if c.on(3) else None)


def fork_side(cv, run, x0, title, cap, upto):
    pos = fit(G01POS, (x0 + 60, 260, x0 + 760, 760))
    evs = events(run)
    e = evs[min(upto, len(evs) - 1)]
    panel(cv, x0, 160, 820, 700, title)
    blocked = []
    if e["kind"] == "stopped":
        blocked = sorted({m for cnd in e["candidates"] for m in (cnd["a"] + cnd["b"])})
    draw_state(cv, pos, G01E, e["after"], sizes_of(T["g01"]), cap, blocked=blocked, r=34)
    r = run["result"]
    if upto >= len(evs) - 1:
        tag(cv, x0 + 410, 830, f"{' | '.join(r['labels'])} · cut {r['cut']} · {'达到' if r['targetReached'] else '未达到'} K", TEAL if r["targetReached"] else GOLD, 1.0, 26)


def s_fork(cv, c):
    upto = c.k
    fork_side(cv, T["cap3"]["run"], 120, "容量 3", 3, upto)
    fork_side(cv, T["cap2"]["run"], 980, "容量 2", 2, upto)


def s_bound(cv, c):
    panel(cv, 160, 170, 1600, 640, "下界：至少需要几个簇")
    for i in range(5):
        cv.rect(260 + i * 130, 320, 100, 100, fill=TEAL, r=10, alpha=c.p(0))
        cv.text(310 + i * 130, 384, "ABCDE"[i], 38, "#0b1b1f", "bold", "center", alpha=c.p(0))
    if c.on(1):
        for b in range(3):
            x = 260 + b * 380
            cv.rect(x, 520, 330, 160, stroke=GOLD, width=4, r=16, alpha=c.p(1), dash=[12, 8])
            cv.text(x + 165, 720, f"簇 {b + 1}：最多 2", 26, GOLD, align="center", alpha=c.p(1))
        for i, n in enumerate("ABCDE"):
            b, k = divmod(i, 2)
            cv.rect(260 + b * 380 + 25 + k * 150, 550, 130, 100, fill=TEAL, r=10, alpha=c.p(1))
            cv.text(260 + b * 380 + 90 + k * 150, 614, n, 36, "#0b1b1f", "bold", "center", alpha=c.p(1))
    if c.on(2):
        cv.text(1560, 380, "5 ÷ 2 → 向上取整 = 3", 44, GOLD, "bold", align="center", alpha=c.p(2))
    if c.on(3):
        cv.paragraph(1400, 470, "K = 2 不存在合法解。贪心停在 3 簇，不是它的错。", 32, 340, INK, alpha=c.p(3))


def trap_scene(cv, c, reveal):
    pos = fit({k: tuple(v) for k, v in TRAP["positions"].items()}, (220, 300, 1100, 640))
    run = T["trap"]["run"]
    size = sizes_of(TRAP)
    evs = events(run)
    e = evs[min(c.k, len(evs) - 1)] if not reveal else evs[-1]
    edges = [tuple(x) for x in TRAP["edges"]]
    blocked = sorted({m for cnd in e.get("candidates", []) for m in (cnd["a"] + cnd["b"])}) if e["kind"] == "stopped" else ()
    draw_state(cv, pos, edges, e["after"], size, 3, blocked=blocked)
    if reveal:
        best = T["trap"]["oracle"]["bestCutAtK"]["clusters"]
        for i, grp in enumerate(best):
            pts = [pos[m] for m in grp]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            cv.rect(min(xs) - 80, min(ys) - 80, max(xs) - min(xs) + 160, max(ys) - min(ys) + 200, stroke=GOLD, width=4, r=50, alpha=c.p(c.k), dash=[14, 9])
    panel(cv, 1220, 180, 600, 640, "greedy_trap · 容量 3，K = 2")
    lb = T["trap"]["oracle"]["lowerBoundClusters"]
    lines = [f"下界：6 ÷ 3 向上取整 = {lb}，并没有排除 2 簇", f"贪心先合并 C–D（10）", "CD + A = 4 > 3，CD + B = 4 > 3", f"停在 3 簇，cut {run['result']['cut']}"]
    if reveal:
        lines = [f"穷举：{' | '.join(''.join(g) for g in T['trap']['oracle']['bestCutAtK']['clusters'])}", "两簇大小都是 3：合法", f"2 簇，cut {T['trap']['oracle']['bestCutAtK']['cut']}", "可行，只是贪心走不到"]
    for i, s in enumerate(lines):
        if c.on(min(i, len(c.scene.beats) - 1)):
            cv.paragraph(1260, 290 + i * 120, s, 32, 530, GOLD if i == 3 else INK, alpha=c.p(min(i, len(c.scene.beats) - 1)))


def s_trap(cv, c):
    trap_scene(cv, c, False)


def s_trap2(cv, c):
    trap_scene(cv, c, True)


def s_sub(cv, c):
    pos0 = {k: tuple(v) for k, v in SUB["positions"].items()}
    edges = [tuple(x) for x in SUB["edges"]]
    run, best = T["suboptimal"]["run"], T["suboptimal"]["oracle"]["bestCutAtK"]
    for side, (x0, title) in enumerate([(120, "贪心：先拿最大的 10"), (980, "穷举：合法最优")]):
        panel(cv, x0, 160, 820, 700, title, c.p(0 if side == 0 else 2))
        pos = fit(pos0, (x0 + 130, 345, x0 + 690, 715))
        if side == 0:
            evs = events(run)
            e = evs[min(c.k + 1, len(evs) - 1)]
            draw_state(cv, pos, edges, e["after"], sizes_of(SUB), 2, alpha=c.p(0), colors={"AB": TEAL, "CD": BLUE})
            if c.on(1):
                tag(cv, x0 + 410, 830, f"{' | '.join(run['result']['labels'])} · cut {run['result']['cut']}", RED, c.p(1), 28)
        elif c.on(2):
            clusters = [{"label": "".join(g), "members": g, "size": len(g)} for g in best["clusters"]]
            draw_state(cv, pos, edges, clusters, sizes_of(SUB), 2, alpha=c.p(2), colors={"AC": TEAL, "BD": BLUE})
            tag(cv, x0 + 410, 830, f"{' | '.join(''.join(g) for g in best['clusters'])} · cut {best['cut']}", TEAL, c.p(2), 28)


def s_uneven(cv, c):
    pos = fit(G01POS, (200, 230, 900, 790))
    size = {n: 2 if n == "A" else 1 for n in "ABCDE"}
    evs = UNEVEN["events"]
    e = evs[min(c.k + 1, len(evs) - 1)]
    draw_state(cv, pos, G01E, e["after"], size, 3)
    panel(cv, 1060, 200, 720, 520, "A 的大小改成 2，容量 3")
    lines = ["A–B 合并：大小 2 + 1 = 3，已满", "AB + C = 4 > 3：被阻止", "D–E 合并，再把 C 放进 DE", f"结果 {' | '.join(UNEVEN['result']['labels'])}，cut {UNEVEN['result']['cut']}"]
    for i, s in enumerate(lines):
        if c.on(min(i, len(c.scene.beats) - 1)):
            cv.paragraph(1100, 300 + i * 100, s, 32, 640, GOLD if i == 3 else INK, alpha=c.p(min(i, len(c.scene.beats) - 1)))


CODE = ["若某个 s(v) > C：报告输入不合法",
        "while 簇数 > K:",
        "    cands ← 亲和度 > 0 的簇对",
        "    legal ← 合并后大小 ≤ C 的候选",
        "    if legal 为空: 停止（说明原因）",
        "    合并 legal 中选择键最小的一对",
        "报告：簇数、合法、达到 K、停止原因",
        "诊断：下界与小图穷举"]


def s_code(cv, c):
    active = [(1,), (4, 5), (6,), (7,), (8,)][min(c.k, 4)]
    code(cv, 170, 270, CODE, active, 32, 70, w=1040)
    notes = ["单点就放不下：没有任何合法分组。", "先筛合法，再比较亲和度。", "选择键与 Module 03 相同。", "四项分开报告。", "区分：不可能 / 卡住 / 非最优。"]
    cv.paragraph(1290, 360, notes[min(c.k, 4)], 36, 520, INK, alpha=c.p(c.k, 0.5))


def s_limits(cv, c):
    items = ["下界只能证明“不可能”；证明“可能”需要真的找到合法分组",
             "穷举只适合教学小图，集合划分数量增长极快",
             "贪心不回撤：走进死胡同时，只能如实报告",
             "下一模块：不合并节点，而是让节点改“标签”"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)]),
    Scene("s01-hook", s_hook, [Beat("规则和上一模块一样：每次合并最亲近的一对。", 2.8), Beat("可是 AB 已经装了 2 个单元，C 再进来就是 3。", 3.4), Beat("容器放不下时，该怎么办？", 3.0)], chapter="一 · 装得下吗"),
    Scene("s02-terms", s_terms, [Beat("先说清结果里要报告什么。", 2.2), Beat("实际有几个簇。", 1.8), Beat("每个簇有没有超过容量。", 2.2), Beat("有没有达到目标 K——这和“合法”是两回事。", 3.2), Beat("以及为什么停下。", 2.0)], chapter="二 · 四个报告项"),
    Scene("s03-fork", s_fork, [Beat("同一张图，左边容量 3，右边容量 2。", 2.8), Beat("第一步相同：A–B。", 2.2), Beat("第二步：左边 AB+C 大小 3，合法；右边超容量，改选 D–E。", 4.2), Beat("左边再合并 D–E，达到 K；右边再也没有合法的合并。", 3.6)], chapter="三 · 同图两容量"),
    Scene("s04-bound", s_bound, [Beat("容量 2 时停在 3 簇，是贪心的错吗？", 2.8), Beat("把 5 个单位装进最多放 2 个的簇：", 2.6), Beat("至少需要 5 ÷ 2 向上取整 = 3 个簇。", 2.6), Beat("所以 K = 2 根本不可能。贪心停下，没有犯错。", 3.4)], chapter="四 · 不可能，还是走错了路"),
    Scene("s05-trap", s_trap, [Beat("另一张图：A、B 大小 2，C、D 大小 1，容量 3。", 3.2), Beat("下界是 6 ÷ 3 = 2，并没有排除 2 簇。", 3.0), Beat("贪心先拿最大的 C–D：10。", 2.6), Beat("之后 A、B 都放不进 CD，停在 3 簇。", 3.0)]),
    Scene("s06-trap2", s_trap2, [Beat("可是穷举找到了 AC | BD：", 2.4), Beat("两个簇的大小都是 3，合法。", 2.4), Beat("2 个簇，cut 10。", 2.2), Beat("这是“可行，但贪心卡住”：第一步就走进了死胡同。", 3.6)]),
    Scene("s07-sub", s_sub, [Beat("第三种结局：合法，也达到 K，但不是最优。", 3.0), Beat("贪心先合并 A–B（10），再合并 C–D：cut 18。", 3.4), Beat("合法的 AC | BD 只切断 10 和 1：cut 11。", 3.4), Beat("眼前最大的一步，把两条 9 都留在了 cut 里。", 3.4)], chapter="五 · 合法但不是最优"),
    Scene("s08-uneven", s_uneven, [Beat("单元大小也会改变结局：把 A 的大小改成 2，容量 3。", 3.4), Beat("A–B 合并后已经满了，AB + C 被阻止。", 3.0), Beat("改为合并 D–E，再把 C 放进去。", 2.6), Beat("结果 AB | CDE，cut 5，而不是 3。", 2.8)]),
    Scene("s09-code", s_code, [Beat("写成伪代码：先检查输入。", 2.2), Beat("每一步先筛合法，再选最大。", 2.6), Beat("选择键与上一模块相同。", 2.2), Beat("停下以后，四项分开报告。", 2.4), Beat("最后用下界和穷举诊断属于哪种结局。", 3.0)], chapter="六 · 伪代码与局限"),
    Scene("s10-limits", s_limits, [Beat("容量约束的边界：", 1.6), Beat("小图可以穷举，大图不行。", 2.4), Beat("贪心不回撤，走不出死胡同。", 2.4), Beat("下一模块：节点不合并，只改标签。", 3.0)], tail=1.2),
]
POSTER_AT = 98.0
