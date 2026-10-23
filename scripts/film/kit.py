"""Shared visual language for every course film: dark 2D science explainer, 1920×1080, 30 fps.
Typography follows specs/visual-design: title 56, subtitle 40, labels 30–36, captions 40,
and a caption band of 170 px at the bottom that diagrams never enter.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from cairo_ctx import Canvas, SANS, SERIF, MONO, SHIFT, mix  # noqa: E402

W, H, FPS = 1920, 1080, 30
BG, BG2, PANEL, PANEL2 = "#071c22", "#0b252b", "#123037", "#0d272d"
INK, MUTED, FAINT = "#f2f3e9", "#bcd2d0", "#6f8f8f"
TEAL, GOLD, RED, BLUE, PURPLE, PINK, GREEN = "#77cdbb", "#d8bb78", "#db7b72", "#8fb1e6", "#c2a6e6", "#e39fb8", "#9fd27f"
GROUP = [TEAL, BLUE, GOLD, PURPLE, PINK, GREEN, "#e8a06a", "#7fd0e0"]
CAPTION_TOP = H - 170          # diagrams stay above this line
STAGE = (90, 130, W - 90, CAPTION_TOP - 24)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return ease((t - a) / (b - a))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


def min_read(text):
    """Minimum on-screen time for a caption: ~4.5 Chinese characters per second plus 0.8 s."""
    n = sum(1 for ch in text if not ch.isspace())
    return n / 4.5 + 0.8


class Frame:
    def __init__(self):
        self.cv = Canvas(W, H)

    def backdrop(self, t=0.0):
        cv = self.cv
        cv.gradient(0, 0, 0, H, [(0, "#0a2229", 1), (0.6, BG, 1), (1, "#061418", 1)])
        # faint technical grid, slow drift only on the dot pattern (never on the diagram)
        for gx in range(0, W + 1, 120):
            cv.line(gx, 0, gx, CAPTION_TOP, "#11323a", 1)
        for gy in range(0, CAPTION_TOP, 120):
            cv.line(0, gy, W, gy, "#11323a", 1)
        cv.rect(0, CAPTION_TOP, W, H - CAPTION_TOP, fill="#051115", alpha=0.92)
        cv.line(0, CAPTION_TOP, W, CAPTION_TOP, "#1d3d43", 1.5)


def header(cv, module_label, chapter, alpha=1.0):
    cv.text(70, 64, module_label, 24, FAINT, alpha=alpha)
    if chapter:
        cv.text(W / 2, 64, chapter, 28, GOLD, align="center", alpha=alpha)


def caption(cv, text, alpha=1.0, sub=None):
    if not text:
        return
    lines = cv.wrap(text, 42, W - 300, "bold")
    y0 = CAPTION_TOP + 70 - (len(lines) - 1) * 26
    for i, ln in enumerate(lines[:2]):
        cv.text(W / 2, y0 + i * 58, ln, 42, INK, "bold", "center", alpha=alpha)
    if sub:
        cv.text(W / 2, H - 28, sub, 24, MUTED, align="center", alpha=alpha)


def title_card(cv, title, en, alpha=1.0, y=H / 2 - 40):
    cv.rect(0, y - 110, W, 220, fill="#081e24", alpha=0.85 * alpha)
    cv.text(W / 2, y, title, 92, GOLD, align="center", family=SERIF, alpha=alpha)
    cv.text(W / 2, y + 62, en, 26, MUTED, align="center", alpha=alpha)


def panel(cv, x, y, w, h, title=None, alpha=1.0, border=None):
    cv.rect(x, y, w, h, fill=PANEL2, stroke=border or "#24474d", width=2, r=14, alpha=0.96 * alpha)
    if title:
        cv.text(x + 26, y + 46, title, 28, GOLD, "bold", alpha=alpha)


def tag(cv, x, y, text, c=TEAL, alpha=1.0, size=26, fill=None, align="center"):
    w = cv.measure(text, size, "bold") + 30
    x0 = x - w / 2 if align == "center" else x
    cv.rect(x0, y - size - 8, w, size + 20, fill=fill or "#0a2126", stroke=c, width=2, r=(size + 20) / 2, alpha=alpha)
    cv.text(x0 + w / 2, y + 2, text, size, c, "bold", "center", alpha=alpha)
    return w


def node(cv, x, y, name, fill=TEAL, r=40, alpha=1.0, ring=None, dashed=False, label_color="#0b1b1f", size=34):
    if ring:
        cv.circle(x, y, r + 10, stroke=ring, width=5, alpha=alpha)
    cv.circle(x, y, r, fill=fill, stroke="#061418", width=3, alpha=alpha)
    if dashed:
        cv.circle(x, y, r + 1, stroke="#f2f3e9", width=3, alpha=alpha, dash=[7, 6])
    cv.text(x, y + size * 0.36, name, size, label_color, "bold", "center", alpha=alpha)


def edge(cv, p, q, w=None, state="normal", alpha=1.0, r=40, label_offset=24, wsize=32):
    color, width, dash = {"normal": ("#5d7c80", 4, None), "cut": (RED, 4, [16, 11]), "hl": (GOLD, 7, None),
                          "inside": ("#9fc9bf", 5, None), "faint": ("#2c4a4f", 3, None), "trial": (GOLD, 5, [10, 8])}[state]
    cv.line(p[0], p[1], q[0], q[1], color, width, alpha, dash)
    if w is not None:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        dx, dy = q[1] - p[1], p[0] - q[0]
        L = math.hypot(dx, dy) or 1
        x, y = mx + dx / L * label_offset, my + dy / L * label_offset
        cv.circle(x, y - wsize * 0.34, wsize * 0.72, fill=BG, alpha=alpha * 0.9)
        cv.text(x, y, str(w), wsize, GOLD if state == "hl" else "#d9e4e1", "bold", "center", alpha=alpha)


def graph(cv, pos, edges, groups=None, states=None, rings=None, tags=None, alpha=1.0, r=40, show_w=True, fills=None, dashed=(), order=None, label_offset=26):
    """pos: {id:(x,y)}, edges: [(u,v,w)], groups: {id: key} → colour; states: {"u|v": state}."""
    states = states or {}
    keys = order or sorted({groups[n] for n in pos} if groups else [])
    for u, v, w in edges:
        k = "|".join(sorted((u, v)))
        st = states.get(k) or ("cut" if groups and groups.get(u) != groups.get(v) else "normal")
        edge(cv, pos[u], pos[v], w if show_w else None, st, alpha, r, label_offset)
    for n, (x, y) in pos.items():
        fill = (fills or {}).get(n) or (GROUP[keys.index(groups[n]) % len(GROUP)] if groups else "#a9bdb8")
        node(cv, x, y, n, fill, r, alpha, (rings or {}).get(n), n in dashed)
        if tags and tags.get(n):
            cv.text(x, y + r + 40, tags[n], 26, MUTED, "bold", "center", alpha=alpha)


def bar(cv, x, y, w, h, frac, c=TEAL, alpha=1.0, back="#163a41"):
    cv.rect(x, y, w, h, fill=back, r=h / 2, alpha=alpha)
    if frac > 0:
        cv.rect(x, y, max(h, w * clamp(frac)), h, fill=c, r=h / 2, alpha=alpha)


def table(cv, x, y, widths, rows, size=30, lh=54, highlight=None, header=True, alpha=1.0, colors=None):
    """rows: list of lists of strings; highlight: {row_index: color}."""
    for i, row in enumerate(rows):
        yy = y + i * lh
        if highlight and i in highlight:
            cv.rect(x - 14, yy - size - 8, sum(widths) + 28, lh - 4, fill=highlight[i], r=8, alpha=0.22 * alpha)
        xx = x
        for j, cell in enumerate(row):
            col = MUTED if header and i == 0 else (colors or {}).get((i, j), INK)
            cv.text(xx, yy, cell, size - (4 if header and i == 0 else 0), col, "bold" if (header and i == 0) else "normal", alpha=alpha)
            xx += widths[j]
        if header and i == 0:
            cv.line(x - 6, yy + 16, x + sum(widths), yy + 16, "#2d4a4e", 2, alpha)


def code(cv, x, y, lines, active=(), size=28, lh=48, alpha=1.0, w=900):
    cv.rect(x - 24, y - 52, w, len(lines) * lh + 44, fill="#0a1c1f", stroke="#24474d", width=2, r=12, alpha=alpha)
    for i, ln in enumerate(lines):
        yy = y + i * lh
        on = i + 1 in active
        if on:
            cv.rect(x - 24, yy - size - 6, w, lh - 2, fill="#2a3d36", alpha=alpha)
            cv.rect(x - 24, yy - size - 6, 6, lh - 2, fill=GOLD, alpha=alpha)
        cv.text(x, yy, str(i + 1), size - 6, FAINT, family=MONO, alpha=alpha)
        cv.text_mixed(x + 46, yy, ln, size, GOLD if on else "#dfeadf", alpha=alpha)


def formula(cv, x, y, parts, size=46, alpha=1.0, align="center"):
    """parts: [(text, color)] or [(text, color, "sub" | "sup")], drawn on one line with the serif face."""
    def seg(p):
        scale, dy = SHIFT[p[2] if len(p) > 2 else None]
        return p[0], p[1], size * scale, dy * size
    total = sum(cv.measure(t, sz, family=SERIF) for t, _, sz, _ in map(seg, parts))
    xx = x - total / 2 if align == "center" else x
    for t, c, sz, dy in map(seg, parts):
        xx += cv.text(xx, y + dy, t, sz, c, family=SERIF, alpha=alpha)
    return total


def number_box(cv, x, y, w, h, label, value, c=TEAL, alpha=1.0, size=72):
    cv.rect(x, y, w, h, fill=PANEL2, stroke="#24474d", width=2, r=12, alpha=alpha)
    cv.text(x + 24, y + 42, label, 26, MUTED, alpha=alpha)
    cv.text(x + 24, y + h - 26, str(value), size, c, "bold", alpha=alpha)


def fit(pos, box, keep_aspect=True):
    """Scale {id: (x, y)} into box (x0, y0, x1, y1)."""
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    x0, y0, x1, y1 = box
    sx = (x1 - x0) / max(1e-9, max(xs) - min(xs))
    sy = (y1 - y0) / max(1e-9, max(ys) - min(ys))
    if keep_aspect:
        sx = sy = min(sx, sy)
    w, h = (max(xs) - min(xs)) * sx, (max(ys) - min(ys)) * sy
    ox, oy = x0 + (x1 - x0 - w) / 2, y0 + (y1 - y0 - h) / 2
    return {k: (ox + (p[0] - min(xs)) * sx, oy + (p[1] - min(ys)) * sy) for k, p in pos.items()}


def load_trace(module_id):
    import json
    root = Path(__file__).resolve().parents[2]
    return json.loads((root / "site" / "data" / module_id / "traces.json").read_text())


def score_box(cv, x, y, w, items, total=None, alpha=1.0, title=None, size=34):
    """A stacked 'sum' box: items = [(label, value, colour, progress 0..1)]; shows the running total."""
    h = 70 + len(items) * 64 + (70 if total is not None else 0)
    panel(cv, x, y, w, h, title, alpha)
    yy = y + (92 if title else 60)
    run = 0
    for label, val, col, p in items:
        if p <= 0:
            yy += 64
            continue
        a = alpha * clamp(p)
        cv.text(x + 30, yy, label, size - 4, MUTED, alpha=a)
        cv.text(x + w - 30, yy, f"{val:+g}" if run else f"{val:g}", size, col, "bold", "right", alpha=a)
        run += val if p >= 1 else 0
        yy += 64
    if total is not None:
        cv.line(x + 24, yy - 30, x + w - 24, yy - 30, "#3b5a5e", 2, alpha)
        cv.text(x + 30, yy + 14, "合计", size - 2, GOLD, "bold", alpha=alpha)
        cv.text(x + w - 30, yy + 14, f"{total:g}", size + 10, GOLD, "bold", "right", alpha=alpha)


def convex_hull(points):
    p = sorted(set(points))
    if len(p) < 3:
        return p
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def hull(cv, pts, color=TEAL, pad=62, alpha=1.0, label=None, below=False):
    """Soft rounded region around a cluster's members (a supernode)."""
    hp = convex_hull([(round(x, 2), round(y, 2)) for x, y in pts])
    if len(hp) == 1:
        hp = [(hp[0][0] - 0.5, hp[0][1]), (hp[0][0] + 0.5, hp[0][1])]
    if hasattr(cv, "group"):
        cv.group()
        cv.poly(hp, fill=color, stroke=color, width=2 * pad, close=True, join=1)
        cv.end_group(0.16 * alpha)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if label:
        lx, ly = sum(xs) / len(xs), (max(ys) + pad + 36) if below else (min(ys) - pad - 16)
        lw = cv.measure(label, 26, "bold")
        cv.rect(lx - lw / 2 - 10, ly - 26, lw + 20, 36, fill="#071c22", r=8, alpha=0.82 * alpha)  # keeps the label readable over edges
        cv.text(lx, ly, label, 26, color, "bold", "center", alpha=alpha)
    if not hasattr(cv, "group"):
        cv.rect(min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad, stroke=color, width=3, r=pad, alpha=alpha, dash=[12, 8])
