"""Module 06 · 谱二分 —— 影片《给每个点一个数》. Data: site/data/m06-spectral-bisection/traces.json
(engines/spectral.js: Laplacian, Jacobi eigen-solve, sweep). The spring picture appears only in the
quadratic-form scene and is labelled as an analogy."""
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, lerp2, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, number_box)

ID, TITLE = "spectral", "给每个点一个数"
MODULE = "Module 06 · 谱二分"
MOOD, SEED = "calm", 6
WHY = "约 3 分半：矩阵装配与二次型放慢；扫描四个切点逐个停留。完整代数证明不放进主片。"
T = load_trace("m06-spectral-bisection")
R = T["run"]["result"]
IDS = R["ids"]
E5 = [tuple(e) for e in T["g01"]["edges"]]
POS = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (200, 230, 860, 780))
LMAT = T["laplacian"]["L"]


def g5(cv, groups=None, alpha=1.0, pos=None, tags=None, hl=None):
    pos = pos or POS
    for u, v, w in E5:
        st = (hl or {}).get(f"{u}|{v}") or ("cut" if groups and groups[u] != groups[v] else "normal")
        edge(cv, pos[u], pos[v], w, st, alpha)
    for n in IDS:
        col = (TEAL if groups[n] == "L" else BLUE) if groups else "#a9bdb8"
        node(cv, *pos[n], n, col, 40, alpha)
        if tags and tags.get(n) is not None:
            cv.text(pos[n][0], pos[n][1] + 78, tags[n], 26, GOLD, "bold", "center", alpha=alpha)


def matrix(cv, x, y, M, cell=96, filled=None, hi=None, alpha=1.0, size=34):
    for j, n in enumerate(IDS):
        cv.text(x + cell * j + cell / 2, y - 18, n, 26, MUTED, "bold", "center", alpha=alpha)
        cv.text(x - 30, y + cell * j + cell * 0.62, n, 26, MUTED, "bold", "center", alpha=alpha)
    for i in range(len(IDS)):
        for j in range(len(IDS)):
            on = filled is None or (i, j) in filled
            h_ = hi and (i, j) in hi
            cv.rect(x + cell * j, y + cell * i, cell - 6, cell - 6, fill="#173a40" if h_ else PANEL2, stroke=GOLD if h_ else "#24474d", width=2, r=8, alpha=alpha)
            if on:
                v = M[i][j]
                cv.text(x + cell * j + cell / 2 - 3, y + cell * i + cell * 0.62, f"{v:g}".replace("-", "−"), size, GOLD if i == j else (INK if v else FAINT), "bold" if i == j else "normal", "center", alpha=alpha)


def s_title(cv, c):
    title_card(cv, "给每个点一个数", "Spectral bisection · Module 06", c.p(0, 1.2))


def s_hook(cv, c):
    g5(cv, alpha=c.p(0))
    if c.on(1):
        q = c.p(1, 1.4)
        y = 860 - 20
        cv.line(1050, 520, 1780, 520, "#5d7c80", 3, q)
        for i, n in enumerate(R["order"]):
            x = 1050 + 730 * (R["orderValues"][i] - min(R["orderValues"])) / (max(R["orderValues"]) - min(R["orderValues"]))
            node(cv, x, 520, n, "#a9bdb8", 32, q, size=28)
        cv.text(1415, 440, "给每个点一个数，排成一条线", 32, GOLD, "bold", "center", alpha=q)
    if c.on(2):
        cv.text(1415, 640, "然后只在线上的相邻位置之间切一刀", 30, INK, align="center", alpha=c.p(2))


def s_goal(cv, c):
    panel(cv, 160, 170, 1600, 640, "先写清问题")
    items = [("只要 cut 最小？", "全部放进一组，cut = 0——毫无用处。", RED), ("两组都非空，不分左右", "ABC | DE 与 DE | ABC 是同一个分法。", INK),
             ("5 个节点有多少种？", "(2⁵ − 2) ÷ 2 = 15（原题库写 16，多算了空组那一种）", GOLD), ("再加平衡窗口", "每组 40%–60%：这里每组 2 或 3 个节点。", TEAL)]
    for i, (a, b, col) in enumerate(items):
        if c.on(i):
            cv.text(220, 290 + i * 130, a, 36, col, "bold", alpha=c.p(i))
            cv.text(220, 340 + i * 130, b, 30, INK, alpha=c.p(i))


def s_lap(cv, c):
    # assemble L edge by edge; each edge contributes four cells
    n_edges = clamp(int(c.since(1) / 0.9) + 1, 0, len(E5)) if c.on(1) else 0
    M = [[0] * 5 for _ in range(5)]
    hi = set()
    for k, (u, v, w) in enumerate(E5[:n_edges]):
        i, j = IDS.index(u), IDS.index(v)
        M[i][i] += w; M[j][j] += w; M[i][j] -= w; M[j][i] -= w
        if k == n_edges - 1 and not c.on(2):
            hi = {(i, i), (j, j), (i, j), (j, i)}
    if c.on(2):
        M = LMAT
    cur = E5[n_edges - 1] if n_edges and not c.on(2) else None
    g5(cv, hl={f"{cur[0]}|{cur[1]}": "hl"} if cur else None, pos=fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (150, 300, 640, 760)))
    matrix(cv, 900, 230, M, 104, hi=hi)
    if cur:
        tag(cv, 1160, 830, f"边 {cur[0]}–{cur[1]}（{cur[2]}）：两个对角 +{cur[2]}，两个非对角 −{cur[2]}", GOLD, 1.0, 26)
    if c.on(3):
        for i in range(5):
            cv.text(1460, 230 + 104 * i + 64, "行和 0", 26, TEAL, "bold", alpha=c.p(3))
    cv.text(900, 190, "L = D − A", 36, GOLD, "bold", family=SERIF, alpha=c.p(0))


def s_quad(cv, c):
    formula(cv, W / 2, 260, [("xᵀLx = ", INK), ("Σ", GOLD), (" w(u,v)·(x", INK), ("u", INK, "sub"), (" − x", INK), ("v", INK, "sub"), (")²", INK)], 54, c.p(0))
    if c.on(1):
        q = c.p(1)
        ind = {n: (1 if n in "ABC" else -1) for n in IDS}
        g5(cv, {n: "L" if ind[n] > 0 else "R" for n in IDS}, q, pos=fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (200, 360, 760, 800)), tags={n: f"{ind[n]:+d}" for n in IDS})
        panel(cv, 1000, 360, 760, 360, "x 只取 ±1 时", q)
        cv.paragraph(1040, 450, "没被切的边贡献 0；被切的边贡献 w·2² = 4w。", 32, 680, INK, alpha=q)
        cv.text(1040, 600, "xᵀLx = 4 × cut = 4 × 3 = 12", 40, GOLD, "bold", alpha=q)
    if c.on(3):
        q = c.p(3)
        cv.rect(1000, 750, 760, 100, fill="#1f1830", stroke=PURPLE, width=2, r=12, alpha=q)
        cv.text(1030, 812, "类比：边像弹簧，越硬越把两端拉近（不是物理模拟）", 28, PURPLE, "bold", alpha=q)


def number_line(cv, x0, x1, y, vals, order, k=None, alpha=1.0, flip=False, from_pos=None, p=1.0, r=34):
    lo, hi = min(vals), max(vals)
    sx = lambda v: x0 + (x1 - x0) * (v - lo) / ((hi - lo) or 1)
    cv.line(x0 - 30, y, x1 + 30, y, "#5d7c80", 3, alpha)
    pts, last_x, up = {}, None, False
    for i, n in enumerate(order):
        tx = sx(vals[i])
        crowded = last_x is not None and tx - last_x < 2 * r + 10
        up = (not up) if crowded else False
        ty = y - 2.4 * r if up else y
        last_x = tx
        pt = lerp2(from_pos[n], (tx, ty), ease(p)) if from_pos else (tx, ty)
        pts[n] = pt
        if up and p >= 1:
            cv.line(tx, ty + r, tx, y, "#5d7c80", 2, alpha)
            cv.circle(tx, y, 5, fill="#5d7c80", alpha=alpha)
        col = (TEAL if i < k else BLUE) if k else "#a9bdb8"
        node(cv, *pt, n, col, r, alpha, size=28)
        if p >= 1:
            cv.text(tx, y + 62 + (28 if i % 2 else 0), f"{vals[i]:+.3f}", 24, MUTED, align="center", alpha=alpha)
    if k:
        xm = (sx(vals[k - 1]) + sx(vals[k])) / 2
        cv.line(xm, y - 3 * r, xm, y + 50, GOLD, 4, alpha, dash=[10, 7])
    return pts


def s_fiedler(cv, c):
    ev = R["eigenvalues"]
    panel(cv, 1280, 170, 520, 440, "特征值（实时求解）")
    for i, v in enumerate(ev):
        cv.text(1320, 270 + i * 64, f"λ{i + 1} = {v:.4f}" if abs(v) > 1e-9 else f"λ{i + 1} = 0", 32, GOLD if i == 1 else INK, "bold" if i == 1 else "normal", alpha=c.p(0))
    p = c.p(2, 1.8)
    if not c.on(2):
        g5(cv, tags={n: f"{R['fiedler'][IDS.index(n)]:+.3f}" for n in IDS} if c.on(1) else None, pos=fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (200, 230, 860, 780)))
    else:
        number_line(cv, 220, 1180, 560, R["orderValues"], R["order"], from_pos=POS, p=p)
        cv.text(700, 420, "按 Fiedler 值从小到大：E, D, C, B, A", 32, GOLD, "bold", "center", alpha=p)
    if c.on(3):
        cv.paragraph(1300, 680, "连得紧的 A、B、C 数值接近；D、E 在另一端。", 28, 480, INK, alpha=c.p(3))


def s_sweep(cv, c):
    k = min(max(c.k, 1), 4) if c.k < 5 else R["bestK"]
    s = R["sweep"][k - 1]
    groups = {n: "L" if n in s["left"] else "R" for n in IDS}
    g5(cv, groups, pos=fit({k_: tuple(v) for k_, v in T["g01"]["positions"].items()}, (180, 220, 700, 640)))
    number_line(cv, 860, 1760, 330, R["orderValues"], R["order"], k)
    win = R["window"]
    rows = [["k", "左组", "cut", "窗口"]] + [[str(x["k"]), "".join(x["left"]), str(x["cut"]), "合法" if x["legal"] else "—"] for x in R["sweep"]]
    table(cv, 900, 560, [100, 260, 140, 160], rows[: 1 + k], 32, 62, {k: GOLD if s["legal"] else RED})
    if c.k >= 5:
        tag(cv, 1300, 880, f"窗口内最小：k = {R['bestK']}，{' | '.join(''.join(p) for p in R['partition'])}，cut {R['cut']}", TEAL, 1.0, 28)


def s_flip(cv, c):
    neg = [-v for v in R["orderValues"]][::-1]
    order = R["order"][::-1]
    if not c.on(1):
        number_line(cv, 300, 1620, 420, R["orderValues"], R["order"], R["bestK"])
    else:
        number_line(cv, 300, 1620, 420, neg, order, len(order) - R["bestK"])
    if c.on(2):
        tag(cv, W / 2, 680, f"同一刀：DE | ABC，cut {R['cut']}——只是左右换了名字", TEAL, c.p(2), 30)


def s_fix(cv, c):
    L = LMAT
    single = min(L[i][i] for i in range(5))
    panel(cv, 140, 170, 800, 640, "误解：无约束必切单点")
    rows = [["孤立", "cut = 度数"]] + [[n, f"{L[i][i]:g}"] for i, n in enumerate(IDS)]
    table(cv, 190, 280, [200, 300], rows, 32, 66, {i + 1: GOLD for i in range(5) if L[i][i] == single}, alpha=c.p(0))
    cv.text(190, 720, f"最小单点 {single}；ABC | DE 只有 {T['unconstrained']['cut']}", 32, TEAL, "bold", alpha=c.p(1))
    panel(cv, 1000, 170, 780, 640, "误解：存储值就是求解器", c.p(2))
    if c.on(2):
        rows = [["", "残差 ‖Lx−λx‖/‖x‖"], ["实时求解（本页）", f"{T['run']['result']['diagnostics']['residual']:.1e}"], ["原作三位小数", f"{T['stored']['residual']:.4f}"]]
        table(cv, 1040, 290, [320, 380], rows, 32, 76, alpha=c.p(2))
        cv.paragraph(1040, 560, "0.0044 是舍入，不是失败；但改图时存储值不会重算。", 30, 700, INK, alpha=c.p(3))


def s_disc(cv, c):
    D = T["disconnected"]
    pos = fit({k: tuple(v) for k, v in D["graph"]["positions"].items()}, (220, 300, 1000, 620))
    for u, v, w in D["graph"]["edges"]:
        edge(cv, pos[u], pos[v], w, "normal")
    for n, p in pos.items():
        node(cv, *p, n, TEAL if n in "ABC" else BLUE, 40)
    panel(cv, 1100, 200, 680, 560, "两个分量")
    ev = D["run"]["eigenvalues"]
    cv.text(1140, 300, f"λ1 = 0，λ2 = 0", 40, RED, "bold", alpha=c.p(0))
    cv.paragraph(1140, 380, "每个分量各贡献一个零特征值。", 30, 600, INK, alpha=c.p(0))
    if c.on(1):
        cv.paragraph(1140, 500, "这时 Fiedler 向量只说明“谁和谁在同一个分量”，不反映边的强弱。先检查连通性。", 30, 600, GOLD, alpha=c.p(1))


CODE = ["L ← D − A（检查对称、行和 0）", "(λ, x) ← 特征分解，升序", "检查 连通、简并、残差", "f ← λ2 的特征向量（统一符号）", "order ← 按 f 升序", "for k = 1 … n−1：计算 cut", "返回窗口内 cut 最小的 k"]


def s_code(cv, c):
    active = [(1,), (2, 3), (4, 5), (6, 7)][min(c.k, 3)]
    code(cv, 170, 280, CODE, active, 32, 72, w=1040)
    notes = ["每条边贡献四处。", "本页用 Jacobi 旋转实时求解。", "翻号只交换左右。", "只在窗口内选；不保证全局最优。"]
    cv.paragraph(1290, 360, notes[min(c.k, 3)], 36, 520, INK, alpha=c.p(c.k, 0.5))


def s_limits(cv, c):
    items = ["谱二分给出好的候选，不保证全局最优", "断开或 λ2 简并时，排序可能没有意义", "弹簧只是二次型的类比，本页没有物理模拟", "下一模块：从这个二分出发，成对交换继续改进"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)]),
    Scene("s01-hook", s_hook, [Beat("同一张连接图，换一种想法。", 2.2), Beat("先给每个点一个数，把它们排成一条线。", 3.2), Beat("然后只在相邻的位置之间试切。", 2.8)], chapter="一 · 二分目标"),
    Scene("s02-goal", s_goal, [Beat("只要 cut 最小？把所有点放进一组就行——cut 是 0，毫无用处。", 3.8), Beat("所以要求两组都非空，并且不区分左右。", 3.0), Beat("这样 5 个节点一共 15 种分法，不是 16。", 3.2), Beat("再加一个平衡窗口：每组 2 到 3 个节点。", 3.0)]),
    Scene("s03-lap", s_lap, [Beat("先把边权装进一个矩阵：拉普拉斯矩阵 L = D − A。", 3.4), Beat("每条边贡献四处：两个对角加 w，两个非对角减 w。", 6.4), Beat("装完：对角是度数，其余是负的边权。", 2.8), Beat("检查一下：每一行加起来都是 0。", 2.8)], chapter="二 · 拉普拉斯矩阵"),
    Scene("s04-quad", s_quad, [Beat("这个矩阵有一个关键性质：xᵀLx 等于每条边的 w 乘上两端差的平方。", 4.2), Beat("如果 x 只取 +1 和 −1，被切的边贡献 4w。", 3.2), Beat("所以 xᵀLx = 4 × cut。最小化它，就是在最小化 cut。", 3.6), Beat("可以把边想成弹簧——这只是帮助理解的类比。", 3.2)], chapter="三 · 二次型直觉"),
    Scene("s05-fiedler", s_fiedler, [Beat("放松条件，让 x 取任意实数：答案是第二小特征值的特征向量。", 4.0), Beat("它叫 Fiedler 向量。每个节点得到一个数。", 3.0), Beat("按这个数排序：E、D、C、B、A。", 4.0), Beat("连得紧的点，数值彼此接近。", 2.6)], chapter="四 · Fiedler 向量"),
    Scene("s06-sweep", s_sweep, [Beat("沿着数轴，在每个相邻位置试切。", 2.6), Beat("k = 1：只切出 E，cut 6，超出窗口。", 3.0), Beat("k = 2：ED | CBA，cut 3，在窗口内。", 3.0), Beat("k = 3：正中间，cut 反而是 5。", 3.0), Beat("k = 4：只剩 A，cut 6，超出窗口。", 2.8), Beat("窗口内最小的是 k = 2：DE | ABC，cut 3。", 3.4)], chapter="五 · 排序扫描"),
    Scene("s07-flip", s_flip, [Beat("特征向量乘以 −1 仍然是特征向量。", 2.8), Beat("翻号以后，数轴整个反过来。", 2.6), Beat("同一刀两侧只是换了名字：分组不变，cut 不变。", 3.4)]),
    Scene("s08-fix", s_fix, [Beat("纠正一个说法：没有平衡约束，最优并不一定是孤立一个点。", 3.8), Beat("这张图上孤立一个点最少切 6，而 ABC | DE 只切 3。", 3.6), Beat("再纠正一个：原页面的特征向量是存储的三位小数。", 3.4), Beat("它的残差 0.0044 只是舍入；但改了图，它不会重算。", 3.6)], chapter="六 · 纠正误解"),
    Scene("s09-disc", s_disc, [Beat("还有一个陷阱：图不连通时，λ2 也是 0。", 3.2), Beat("这时排序只说明谁在同一个分量。先检查连通性。", 3.4)]),
    Scene("s10-code", s_code, [Beat("写成伪代码：先构造 L 并自检。", 2.6), Beat("求特征分解，检查连通、简并和残差。", 3.0), Beat("取 Fiedler 向量，排序。", 2.4), Beat("逐个位置扫描，只在窗口内选最小 cut。", 3.0)], chapter="七 · 伪代码与局限"),
    Scene("s11-limits", s_limits, [Beat("谱二分的边界：", 1.6), Beat("条件不满足时，排序可能没有意义。", 2.6), Beat("弹簧只是类比。", 2.0), Beat("下一模块：从这个二分出发，继续改进。", 3.0)], tail=1.2),
]
POSTER_AT = 112.0
