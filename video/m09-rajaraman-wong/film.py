"""Module 09 · Rajaraman–Wong —— 两集：《关键路径的代价（上）：模型与标记》《（下）：恢复与复制》.
Data: site/data/m09-rajaraman-wong/traces.json (engines/rw.js) and no-replication.json (exhaustive search).
The 12-node DAG is a candidate reconstruction; every scene that shows it carries a 'candidate' tag."""
import json
from pathlib import Path
from types import SimpleNamespace
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, number_box)

T = load_trace("m09-rajaraman-wong")
ROOT = Path(__file__).resolve().parents[2]
NR = json.loads((ROOT / "site/data/m09-rajaraman-wong/no-replication.json").read_text())
DAG = T["dag"]
R = T["run"]["result"]
EVS = T["run"]["events"]
LABEL_EV = {e["after"]["node"]: e for e in EVS if e["kind"] == "label"}
SEL_EV = [e for e in EVS if e["kind"] == "select-cluster"]
POS = fit({k: tuple(v) for k, v in DAG["positions"].items()}, (150, 210, 1080, 790))
PIS, POS_O = DAG["PI"], DAG["PO"]


def candidate_tag(cv, alpha=1.0):
    tag(cv, 300, 872, "候选复原数据 · 平票为假设", PURPLE, alpha, 22)


def dag(cv, pos=POS, hl_nodes=(), cluster=(), labels=None, alpha=1.0, r=30, focus=None, edge_hl=None):
    for u, v in DAG["edges"]:
        k = f"{u}>{v}"
        inside = u in cluster and v in cluster
        col = GOLD if (edge_hl and k in edge_hl) else ("#9fc9bf" if inside else "#5d7c80")
        cv.arrow(*pos[u], *pos[v], col, 3 if inside else 2.4, 14, alpha, shorten=r + 4)
    for n, p in pos.items():
        fill = TEAL if n in cluster else (BLUE if n in PIS else ("#e39fb8" if n in POS_O else "#a9bdb8"))
        node(cv, *p, n, fill, r, alpha, GOLD if n == focus else None, size=26)
        if labels and n in labels:
            cv.text(p[0], p[1] - r - 12, f"l={labels[n]}", 22, GOLD, "bold", "center", alpha=alpha)


def labels_upto(node_name=None):
    out = {p: 1 for p in PIS}
    for n, e in LABEL_EV.items():
        out[n] = e["after"]["label"]
        if n == node_name:
            break
    return out


# ------------------------------------------------------------------ part 1
def p1_title(cv, c):
    title_card(cv, "关键路径的代价（上）", "Rajaraman–Wong · 模型与标记 · Module 09", c.p(0, 1.2))


def chain(cv, groups, D=3, y=420, alpha=1.0, label=""):
    ids = ["P", "X", "Y", "O"]
    x = lambda i: 360 + i * 300
    start = 0
    for gi, g in enumerate(groups):
        x0, x1 = x(start) - 80, x(start + len(g) - 1) + 80
        cv.rect(x0, y - 90, x1 - x0, 180, stroke=GROUP[gi], width=3, r=40, alpha=alpha, dash=[12, 8])
        start += len(g)
    where = {n: gi for gi, g in enumerate(groups) for n in g}
    t = 0
    for i, n in enumerate(ids):
        if i:
            cross = where[ids[i - 1]] != where[n]
            t += D if cross else 0
            cv.arrow(x(i - 1) + 44, y, x(i) - 44, y, RED if cross else "#9fc9bf", 4, 16, alpha, dash=[12, 8] if cross else None)
            cv.text((x(i - 1) + x(i)) / 2, y - 26, f"+{D}" if cross else "+0", 28, RED if cross else MUTED, "bold", "center", alpha=alpha)
        t += 1
        node(cv, x(i), y, n, "#a9bdb8", 40, alpha)
        cv.text(x(i), y + 76, f"到达 {t}", 26, GOLD, "bold", "center", alpha=alpha)
    if label:
        cv.text(W / 2, y + 150, label, 32, INK, "bold", "center", alpha=alpha)


def p1_goal(cv, c):
    if not c.on(2):
        chain(cv, [["P", "X"], ["Y", "O"]], alpha=c.p(0), label="跨界 1 次：延迟 7" if c.on(1) else "")
    else:
        chain(cv, [["P"], ["X", "Y"], ["O"]], alpha=c.p(2), label="跨界 2 次：延迟 10")
    if c.on(3):
        tag(cv, W / 2, 820, "延迟看的是最长路径跨了几次边界，不是总共切断了几条线", GOLD, c.p(3), 28)


def p1_model(cv, c):
    panel(cv, 160, 170, 1600, 640, "RW 的模型")
    items = [("组合电路 DAG", "信号沿有向边流动，没有环；PI 是输入，PO 是输出"), ("节点延迟 δ(v)", "经过每个节点需要的时间；这里 δ = 1"),
             ("簇内 0，跨簇 D", "连线两端在不同簇时多加 D；这里 D = 3（不是度矩阵）"), ("容量 M", "每个簇最多放 M 个单位；这里 M = 4"),
             ("允许复制", "同一个逻辑节点可以放进多个簇——最优性结论的前提")]
    for i, (a, b) in enumerate(items):
        if c.on(i):
            cv.text(220, 280 + i * 104, a, 34, GOLD, "bold", alpha=c.p(i))
            cv.text(620, 280 + i * 104, b, 30, INK, alpha=c.p(i))


def p1_replica(cv, c):
    # schematic: g feeds i and j, which sit in two clusters
    a = c.p(0)
    cv.rect(560, 230, 340, 420, stroke=TEAL, width=3, r=30, alpha=a, dash=[12, 8])
    cv.rect(1020, 230, 340, 420, stroke=BLUE, width=3, r=30, alpha=a, dash=[12, 8])
    cv.text(730, 280, "簇 1", 26, TEAL, "bold", "center", alpha=a); cv.text(1190, 280, "簇 2", 26, BLUE, "bold", "center", alpha=a)
    node(cv, 730, 540, "i", "#a9bdb8", 38, a); node(cv, 1190, 540, "j", "#a9bdb8", 38, a)
    if not c.on(2):
        node(cv, 730, 380, "g", GOLD, 38, a)
        cv.arrow(730, 380, 730, 540, "#9fc9bf", 3, 14, a, shorten=42)
        cv.arrow(730, 380, 1190, 540, RED, 3, 14, a, shorten=42, dash=[10, 7])
        if c.on(1):
            tag(cv, 980, 430, "跨簇 +D", RED, c.p(1), 26)
    else:
        q = c.p(2)
        node(cv, 730, 380, "g", GOLD, 38, q, dashed=True); node(cv, 1190, 380, "g", GOLD, 38, q, dashed=True)
        cv.text(730, 450, "g@簇1", 22, MUTED, align="center", alpha=q); cv.text(1190, 450, "g@簇2", 22, MUTED, align="center", alpha=q)
        cv.arrow(730, 380, 730, 540, "#9fc9bf", 3, 14, q, shorten=42); cv.arrow(1190, 380, 1190, 540, "#9fc9bf", 3, 14, q, shorten=42)
        cv.line(770, 380, 1150, 380, PURPLE, 2, q, dash=[6, 8])
        cv.text(960, 365, "同一个逻辑节点的两个实例", 24, PURPLE, align="center", alpha=q)
    if c.on(3):
        tag(cv, W / 2, 760, "代价：多一个实例，多占一份面积（示意图）", GOLD, c.p(3), 28)


def p1_dag(cv, c):
    dag(cv, alpha=c.p(0, 1.2), edge_hl={"b>e", "e>g", "g>i", "i>k"} if c.on(2) else None, hl_nodes=())
    candidate_tag(cv, c.p(0))
    panel(cv, 1180, 210, 620, 560, "原作的 12 节点算例")
    lines = [f"PI：{'、'.join(PIS)}；PO：{'、'.join(POS_O)}", "δ = 1，D = 3，容量 4", "Δ(x, v)：x 到 v 的最长节点延迟（计 v 不计 x）", f"Δ(b, k) = {R['delta']['b']['k']}：b→e→g→i→k"]
    for i, s in enumerate(lines):
        if c.on(min(i, 3)):
            cv.paragraph(1220, 310 + i * 110, s, 30, 560, GOLD if i == 3 else INK, alpha=c.p(min(i, 3)))


def p1_early(cv, c):
    order = ["d", "e", "f", "g", "h"]
    k = min(c.k, len(order) - 1)
    n = order[k]
    e = LABEL_EV[n]
    dag(cv, cluster=e["after"]["cluster"], labels=labels_upto(n), focus=n)
    candidate_tag(cv)
    panel(cv, 1180, 210, 620, 520, f"标记 {n}")
    cv.text(1220, 310, "PI 的标签 = 自身延迟 1", 28, MUTED)
    cv.text(1220, 390, f"候选簇 {{{', '.join(e['after']['cluster'])}}}", 32, TEAL, "bold")
    cv.text(1220, 470, f"l1 = {e['metrics']['l1']}，l2 = {e['metrics']['l2']}", 32, INK)
    cv.text(1220, 560, f"l({n}) = {e['metrics']['label']}", 40, GOLD, "bold")


def p1_label_i(cv, c):
    e = LABEL_EV["i"]
    dag(cv, cluster=e["after"]["cluster"] if c.on(2) else (), labels=labels_upto("h") | ({"i": 7} if c.on(4) else {}), focus="i")
    candidate_tag(cv)
    rows = [["祖先", "l(x)", "Δ", "得分", ""]] + [[x["x"], str(x["l"]), str(x["delta"]), str(x["score"]), ("簇内" if x["inCluster"] else "簇外") if c.on(2) else ""] for x in e["candidates"]]
    table(cv, 1160, 250, [110, 110, 100, 110, 120], rows[: 1 + (len(e["candidates"]) if c.on(1) else 0)], 30, 58, {i + 1: TEAL for i, x in enumerate(e["candidates"]) if x["inCluster"] and c.on(2)})
    if c.on(3):
        cv.text(1160, 760, f"l1 = {e['metrics']['l1']}（簇内 PI c）；l2 = 4 + 3 = {e['metrics']['l2']}（簇外 b）", 28, INK, alpha=c.p(3))
    if c.on(4):
        tag(cv, 1460, 840, f"l(i) = max({e['metrics']['l1']}, {e['metrics']['l2']}) = {e['metrics']['label']}", GOLD, c.p(4), 30)


def p1_rest(cv, c):
    order = ["j", "k", "l"]
    n = order[min(c.k, 2)]
    e = LABEL_EV[n]
    dag(cv, cluster=e["after"]["cluster"], labels=labels_upto(n), focus=n)
    candidate_tag(cv)
    panel(cv, 1180, 210, 620, 520, f"标记 {n}")
    cv.text(1220, 330, f"候选簇 {{{', '.join(e['after']['cluster'])}}}", 32, TEAL, "bold")
    cv.text(1220, 420, f"l1 = {e['metrics']['l1']}，l2 = {e['metrics']['l2']}", 32, INK)
    cv.text(1220, 520, f"l({n}) = {e['metrics']['label']}", 40, GOLD, "bold")
    if n in POS_O:
        cv.paragraph(1220, 610, "输出端的标签：信号最早可能在这个时间到达。", 28, 560, MUTED)


CODE1 = ["检查 DAG；拓扑序；算 Δ(x, v)", "PI：l(p) ← δ(p)", "for 非 PI 节点 v（拓扑序）:", "  score(x) ← l(x) + Δ(x, v)", "  候选簇 ← v + 得分最高的祖先（≤ M）", "  l1 ← 簇内 PI 最大得分", "  l2 ← 簇外最大得分 + D", "  l(v) ← max(l1, l2)"]


def p1_code(cv, c):
    active = [(1, 2), (3, 4), (5,), (6, 7, 8)][min(c.k, 3)]
    code(cv, 170, 270, CODE1, active, 30, 66, w=1040)
    notes = ["有环直接报错。", "得分：从 x 出发到 v 的最早时间。", "平票：拓扑序靠后优先（假设）。", "簇外的路径必须跨一次边界。"]
    cv.paragraph(1290, 360, notes[min(c.k, 3)], 36, 520, INK, alpha=c.p(c.k, 0.5))


PART1 = SimpleNamespace(
    ID="rw1", TITLE="关键路径的代价（上）：模型与标记", MODULE="Module 09 · Rajaraman–Wong 延迟导向聚类", MOOD="steady", SEED=91, POSTER_AT=95.0,
    WHY="RW 内容多，拆成两集：上集讲目标、模型与标记阶段。",
    SCENES=[
        Scene("a00-title", p1_title, [Beat("", 2.6)]),
        Scene("a01-goal", p1_goal, [Beat("一条链：P → X → Y → O，每个节点延迟 1，跨簇加 3。", 3.6), Beat("分成 {P,X} 和 {Y,O}：跨一次边界，延迟 7。", 3.2), Beat("换一种分法，跨两次边界：延迟 10。", 3.0), Beat("延迟只看最长路径跨了几次边界。", 2.8)], chapter="一 · 目标变了"),
        Scene("a02-model", p1_model, [Beat("Rajaraman 与 Wong 的模型：组合电路是一张有向无环图。", 3.4), Beat("每个节点有延迟 δ。", 2.0), Beat("簇内连线不加延迟，跨簇连线固定加 D。", 3.0), Beat("每个簇有容量上限 M。", 2.2), Beat("还有关键的一条：允许复制节点。", 2.6)], chapter="二 · 模型"),
        Scene("a03-replica", p1_replica, [Beat("为什么要复制？g 同时供给两个簇里的 i 和 j。", 3.2), Beat("g 只能放在一边：另一边要跨簇取信号，多付 D。", 3.4), Beat("复制一份 g：两边都在簇内拿到它。", 2.8), Beat("代价是面积：多一个实例，多占一份面积。", 2.8)], chapter="三 · 复制"),
        Scene("a04-dag", p1_dag, [Beat("原作的 12 节点算例，由影片画面复原——这是候选数据。", 3.6), Beat("容量 4，D = 3，每个节点延迟 1。", 2.6), Beat("Δ(x, v)：从 x 到 v 的最长节点延迟，计 v 不计 x。", 3.4), Beat("例如 b 到 k 经过 e、g、i、k：Δ = 4。", 3.0)], chapter="四 · 初始化"),
        Scene("a05-early", p1_early, [Beat("按拓扑序逐个打标签。d 的祖先 a、b 都能放进簇。", 3.4), Beat("e、f 同理：标签都是 2。", 2.6), Beat("f：只有一个祖先 a。", 2.2), Beat("g 的祖先 b、c、e 都在簇内：l(g) = 3。", 3.0), Beat("h：l = 2。", 1.8)], chapter="五 · 标记"),
        Scene("a06-label-i", p1_label_i, [Beat("i 有 7 个祖先，容量只够放 3 个。", 2.8), Beat("每个祖先的得分：l(x) + Δ(x, i)。", 3.0), Beat("取得分最高的 g、e、c；得分相同时，拓扑序靠后的优先——这是假设。", 4.2), Beat("簇内的 PI 是 c：l1 = 4。簇外最大是 b：l2 = 4 + 3 = 7。", 4.0), Beat("l(i) = 7：在这个模型里，信号最早 7 到达 i。", 3.4)]),
        Scene("a07-rest", p1_rest, [Beat("j 同理：l(j) = 7。", 2.2), Beat("k：候选簇 {k, j, i, g}，l(k) = 8。", 3.0), Beat("l：候选簇 {l, j, g, e}，l(l) = 8。", 3.0)]),
        Scene("a08-code", p1_code, [Beat("标记阶段的伪代码：先算 Δ，PI 的标签等于自身延迟。", 3.4), Beat("对每个节点，按得分排序祖先。", 2.6), Beat("把得分最高的放进候选簇，直到容量。", 2.8), Beat("l = max(l1, l2)。下一集：从输出倒推出真正的簇。", 3.8)], chapter="六 · 伪代码"),
    ])


# ------------------------------------------------------------------ part 2
def p2_title(cv, c):
    title_card(cv, "关键路径的代价（下）", "Rajaraman–Wong · 恢复与复制 · Module 09", c.p(0, 1.2))


def p2_recap(cv, c):
    dag(cv, labels=labels_upto(None) | {n: e["after"]["label"] for n, e in LABEL_EV.items()})
    candidate_tag(cv)
    panel(cv, 1180, 210, 620, 400, "上集的结果")
    cv.paragraph(1220, 310, "每个节点都有标签 l(v) 和一个候选簇。", 30, 560, INK)
    cv.paragraph(1220, 420, "候选簇只是“可能用到”的簇。真正用到哪些，要从输出端倒推。", 30, 560, GOLD, alpha=c.p(1))


def p2_select(cv, c):
    k = min(c.k, len(SEL_EV) - 1)
    e = SEL_EV[k]
    members = e["after"]["members"]
    dag(cv, cluster=members, focus=e["after"]["root"])
    candidate_tag(cv)
    panel(cv, 1180, 210, 620, 560, "从输出倒推")
    done = [x["after"]["root"] for x in SEL_EV[: k + 1]]
    cv.text(1220, 300, f"选中以 {e['after']['root']} 为根的簇", 32, GOLD, "bold")
    cv.text(1220, 370, "成员 {" + ", ".join(members) + "}", 30, TEAL)
    cv.paragraph(1220, 450, ("簇外输入 " + "、".join(e["after"]["inputs"]) + " 成为新的簇根") if e["after"]["inputs"] else "没有簇外输入（PI 或只靠 PI）", 28, 560, INK)
    cv.text(1220, 600, f"已选 {len(done)} 个：{' '.join(done)}", 26, MUTED)


def instances_view(cv, x0=140, y0=200, w=1640, hgt=640, alpha=1.0, upto=99, highlight=None):
    roots = R["selected"][:upto]
    cols = 4
    cw, ch = w / cols, hgt / 2
    pos = {}
    for ci, root in enumerate(roots):
        col, row = ci % cols, ci // cols
        bx, by = x0 + col * cw + 10, y0 + row * ch + 10
        members = R["clusters"][root]
        cv.rect(bx, by, cw - 20, ch - 20, fill=PANEL2, stroke=GROUP[ci % len(GROUP)], width=2, r=16, alpha=alpha)
        cv.text(bx + 16, by + 34, f"簇根 {root} · {len(members)}/4", 24, GROUP[ci % len(GROUP)], "bold", alpha=alpha)
        for mi, m in enumerate(members):
            px, py = bx + 70 + (mi % 2) * 150, by + 90 + (mi // 2) * 110
            pos[f"{m}@{root}"] = (px, py)
    for e in R["instanceEdges"]:
        if e["from"] in pos and e["to"] in pos:
            cv.line(*pos[e["from"]], *pos[e["to"]], RED if e["cost"] else "#9fc9bf", 2 if e["cost"] else 3, alpha * (0.45 if e["cost"] else 1), dash=[8, 7] if e["cost"] else None)
    copies = {}
    for i in R["instances"]:
        copies[i["logicalId"]] = copies.get(i["logicalId"], 0) + 1
    for iid, (px, py) in pos.items():
        lg = iid.split("@")[0]
        rep = copies[lg] > 1
        node(cv, px, py, lg, GOLD if (rep and (highlight is None or lg == highlight)) else "#a9bdb8", 30, alpha, None, rep, size=24)
        cv.text(px + 40, py + 8, str(R["arrival"][iid]), 22, MUTED, alpha=alpha)
    return pos


def p2_instances(cv, c):
    instances_view(cv, highlight="b" if c.on(2) else None)
    candidate_tag(cv)
    if c.on(1):
        tag(cv, W / 2, 880 - 10, f"{len(R['selected'])} 个簇、{R['instanceCount']} 个实例（逻辑节点 {R['logicalCount']} 个）", GOLD, c.p(1), 26)


def p2_arrival(cv, c):
    instances_view(cv)
    candidate_tag(cv)
    tag(cv, W / 2, 870, f"输出到达：k = {R['outputDelays']['k']}，l = {R['outputDelays']['l']} —— 等于标签", TEAL, c.p(0), 28)


def p2_compare(cv, c):
    panel(cv, 140, 180, 800, 620, "允许复制（RW）", c.p(0))
    panel(cv, 980, 180, 800, 620, "禁止复制（穷举最好）", c.p(1))
    number_box(cv, 200, 300, 300, 160, "最大延迟", R["maxDelay"], TEAL, c.p(0))
    number_box(cv, 560, 300, 320, 160, "实例 / 面积", R["instanceCount"], GOLD, c.p(0))
    if c.on(1):
        number_box(cv, 1040, 300, 300, 160, "最大延迟", NR["bestMaxDelay"], RED, c.p(1))
        number_box(cv, 1400, 300, 320, 160, "实例 / 面积", R["logicalCount"], INK, c.p(1))
        cv.text(1040, 560, "例：" + " | ".join("".join(x) for x in NR["example"]), 28, INK, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(200, 580, "多 8 个实例，换来 2 个单位的延迟。", 32, 680, GOLD, alpha=c.p(2))
    if c.on(3):
        cv.paragraph(1040, 640, "最优性结论以“允许复制”为前提；禁止复制时不能沿用。", 28, 680, MUTED, alpha=c.p(3))


def p2_scope(cv, c):
    items = ["最优性来自论文，只在模型内成立：DAG、δ、簇内 0、跨簇 D、容量、允许复制",
             "12 节点例子是候选复原；平票“逆拓扑序优先”是假设，待原作者确认",
             "本课程的测试检查实现一致与实例合法，不证明最优",
             "这份提交编号 Lesson 9，教师目录 Lab 09 是 Multilevel：对应待教师确认"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(160, 210 + i * 150, 1600, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(210, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(300, 282 + i * 150, s, 31, INK, alpha=c.p(i))


CODE2 = ["queue ← 所有 PO", "while queue 非空:", "  r ← 取出；选中 r 的候选簇", "  簇外输入 u → 加入 queue（新簇根）", "for 每个选中的簇根 r、成员 m:", "  生成实例 m@r", "  簇内输入：u@r → m@r（+0）", "  簇外输入：u@u → m@r（+D）"]


def p2_code(cv, c):
    active = [(1, 2), (3, 4), (5, 6), (7, 8)][min(c.k, 3)]
    code(cv, 170, 270, CODE2, active, 30, 66, w=1040)
    notes = ["从输出端开始倒推。", "簇外的输入自己成为簇根。", "一个逻辑节点可以有多个实例。", "每个实例的输入都必须完整。"]
    cv.paragraph(1290, 360, notes[min(c.k, 3)], 36, 520, INK, alpha=c.p(c.k, 0.5))


PART2 = SimpleNamespace(
    ID="rw2", TITLE="关键路径的代价（下）：恢复与复制", MODULE="Module 09 · Rajaraman–Wong 延迟导向聚类", MOOD="steady", SEED=92, POSTER_AT=60.0,
    WHY="下集讲逆向恢复、实例与复制的代价，以及适用边界与待确认事项。",
    SCENES=[
        Scene("b00-title", p2_title, [Beat("", 2.6)]),
        Scene("b01-recap", p2_recap, [Beat("上一集，每个节点都得到了标签和一个候选簇。", 3.2), Beat("真正用到哪些簇，要从输出端倒推。", 2.8)], chapter="一 · 回顾"),
        Scene("b02-select", p2_select, [Beat("从输出 k 开始：选中 k 的候选簇 {k, j, i, g}。", 3.4), Beat("再看输出 l：{l, j, g, e}。g 和 j 又出现了一次。", 3.6), Beat("k 的簇外输入 d：它的簇是 {d, b, a}。", 3.0), Beat("e：{e, c, b}。", 2.0), Beat("f：{f, a}。", 1.8), Beat("h：{h, c}。", 1.8), Beat("b 和 c 是输入，各自单独成簇。", 2.6), Beat("一共 8 个簇。", 2.0)], chapter="二 · 逆向恢复"),
        Scene("b03-instances", p2_instances, [Beat("把每个簇的成员生成为实例：节点@簇根。", 3.0), Beat("8 个簇，20 个实例——逻辑节点只有 12 个。", 3.2), Beat("b 有 3 个实例：每个都是同一个逻辑门的副本。", 3.2), Beat("每个实例的输入都要完整：簇内取，或跨簇从簇根取。", 3.6)], chapter="三 · 实例与复制"),
        Scene("b04-arrival", p2_arrival, [Beat("沿实例图计算到达时间：簇内 +0，跨簇 +3。", 3.2), Beat("两个输出都在时间 8 到达，正好等于标签。", 3.0)]),
        Scene("b05-compare", p2_compare, [Beat("允许复制：最大延迟 8，用了 20 个实例。", 3.0), Beat("禁止复制：穷举所有合法分组，最好也只有 10。", 3.4), Beat("多 8 个实例，换来 2 个单位的延迟。", 2.8), Beat("所以最优性结论以允许复制为前提。", 2.8)], chapter="四 · 复制的代价"),
        Scene("b06-scope", p2_scope, [Beat("最后说清边界。最优性来自论文，只在它的模型里成立。", 3.6), Beat("这张 12 节点图是候选复原，平票规则是假设。", 3.2), Beat("测试检查实现一致，不证明最优。", 2.6), Beat("这份提交与教师目录的 Lab 09 不一致，对应待确认。", 3.4)], chapter="五 · 适用边界"),
        Scene("b07-code", p2_code, [Beat("恢复阶段的伪代码：从所有输出开始。", 2.6), Beat("选中簇根的候选簇，簇外输入成为新的簇根。", 3.2), Beat("每个选中的簇生成自己的实例。", 2.4), Beat("每个实例的输入都必须完整——这就是复制。", 3.2)], chapter="六 · 伪代码", tail=1.2),
    ])

FILMS = [PART1, PART2]
