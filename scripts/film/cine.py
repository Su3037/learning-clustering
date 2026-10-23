"""Cinematic film kit (v2), modelled on the author's original Lab05 film 《圈子从哪里来》.

Dark technical picture: radial backdrop, outlined nodes with serif names, thin wires with a soft glow
layer (cairo draws a half-resolution copy that is blurred and added), letter-spaced chapter heads,
and captions over a soft shade instead of a hard band. Every film is rendered once per language:

  zh: Chinese caption, with the English line small underneath (as in the original film)
  en: English caption only; on-screen labels in English

Strings are written as L("中文", "English") or as a (zh, en) tuple; they are resolved at draw time
with the language set by set_lang(). Beat durations use the longer reading time of the two
languages, so both versions share one timeline (same chapters, same scene times).
"""
import math
import re

import cairo
import numpy as np
from PIL import Image, ImageFilter

W, H, FPS = 1920, 1080, 30

# ---------------------------------------------------------------- palette (from the original film)
BG, BG2 = "#061219", "#0b1f29"
IVORY, MUTED, FAINT, DIM = "#eeeadd", "#8fa3a3", "#2a4048", "#3d5d64"
GOLD, TEAL, BLUE, ROSE = "#ddbd78", "#76cbb5", "#86a9e0", "#d99a9a"
AMBER, SAGE, LILAC, CORAL = "#d9b06c", "#a3b26f", "#a18bc0", "#d58f62"
PANEL_BG, NODE_BG = "#081a22", "#0b2029"
HUES = [TEAL, GOLD, BLUE, ROSE, LILAC, SAGE, CORAL, "#7fd0e0"]

# ---------------------------------------------------------------- language
LANG = "zh"
FACES = {
    "zh": {"sans": "Noto Sans SC", "serif": "Noto Serif SC", "mono": "JetBrains Mono"},
    "en": {"sans": "Noto Sans", "serif": "Newsreader", "mono": "JetBrains Mono"},
}
SYMBOLS = set("ℓ→←↔⇄⇒Σ∑≤≥≠×÷∈√✓✗↻")  # missing from the Latin faces; drawn with Noto Sans SC
CJK_FACE = {"sans": "Noto Sans SC", "serif": "Noto Serif SC", "mono": "Noto Sans SC"}


def set_lang(lang):
    global LANG
    LANG = lang


class L(tuple):
    """A bilingual string. str(L(...)) gives the current language."""

    def __new__(cls, zh, en=None):
        return super().__new__(cls, (zh, zh if en is None else en))

    def __str__(self):
        return self[1] if LANG == "en" else self[0]

    def format(self, *a, **k):
        return L(self[0].format(*a, **k), self[1].format(*a, **k))


def tr(s):
    """Resolve L / (zh, en) / plain str for the current language."""
    if s is None:
        return ""
    if isinstance(s, tuple):
        return s[1] if LANG == "en" else s[0]
    return str(s)


def both(s):
    if s is None:
        return ("", "")
    if isinstance(s, tuple):
        return (s[0], s[1])
    return (str(s), str(s))


def is_cjk(ch):
    return ord(ch) >= 0x2E80 or ch in "，。、；：！？（）「」『』《》“”‘’…—"


def min_read(text, lang):
    """Minimum on-screen time: Chinese ~4.5 characters/s, English ~15 characters/s, plus 0.8 s."""
    if not text:
        return 0.0
    if lang == "en":
        return len(text.strip()) / 15.0 + 0.8
    return sum(1 for ch in text if not ch.isspace()) / 4.5 + 0.8


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return ease((t - a) / (b - a)) if b > a else float(t >= a)


def window(t, a, b, fade=0.45):
    return ramp(t, a, a + fade) * (1 - ramp(t, b - fade, b))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


def hexc(c, a=1.0):
    return (int(c[1:3], 16) / 255, int(c[3:5], 16) / 255, int(c[5:7], 16) / 255, a)


def mixc(a, b, t):
    pa, pb = hexc(a), hexc(b)
    return "#" + "".join(f"{round(255 * lerp(x, y, clamp(t))):02x}" for x, y in zip(pa[:3], pb[:3]))


# ---------------------------------------------------------------- frame
class Frame:
    """A 1920×1080 cairo surface plus a half-resolution glow layer and a 2D camera."""

    def __init__(self):
        self.s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.s)
        self.gs = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // 2, H // 2)
        self.g = cairo.Context(self.gs)
        self.g.scale(0.5, 0.5)
        self.cam = (W / 2, H / 2, 1.0)
        self.alpha = 1.0  # global multiplier (scene fades)

    def clear(self):
        self.g.save(); self.g.set_operator(cairo.OPERATOR_CLEAR); self.g.paint(); self.g.restore()
        self.cam = (W / 2, H / 2, 1.0)
        self.alpha = 1.0

    # camera: world point (cx, cy) appears at the screen centre, scaled by z
    def set_cam(self, cx=W / 2, cy=H / 2, z=1.0):
        self.cam = (cx, cy, z)

    def w2s(self, p):
        cx, cy, z = self.cam
        return ((p[0] - cx) * z + W / 2, (p[1] - cy) * z + H / 2)

    def _ctxs(self, glow):
        return ((self.c, 1.0),) + (((self.g, glow),) if glow else ())

    def line(self, a, b, col, width=1.5, alpha=1.0, glow=0.0, screen=False, dash=None):
        alpha *= self.alpha
        if alpha <= 0.002:
            return
        z = 1 if screen else self.cam[2]
        a, b = (a, b) if screen else (self.w2s(a), self.w2s(b))
        for ctx, k in self._ctxs(glow):
            ctx.set_source_rgba(*hexc(col, alpha * k))
            ctx.set_line_width(width * z * (2.2 if ctx is self.g else 1))
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_dash([d * z for d in dash] if dash else [])
            ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
            ctx.set_dash([])

    def polyline(self, pts, col, width=1.5, alpha=1.0, glow=0.0, screen=False, close=False, fill=None, fill_alpha=None):
        alpha *= self.alpha
        if alpha <= 0.002 or len(pts) < 2:
            return
        z = 1 if screen else self.cam[2]
        sp = pts if screen else [self.w2s(p) for p in pts]
        for ctx, k in self._ctxs(glow):
            ctx.new_path()
            ctx.move_to(*sp[0])
            for p in sp[1:]:
                ctx.line_to(*p)
            if close:
                ctx.close_path()
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            if fill:
                ctx.set_source_rgba(*hexc(fill, (fill_alpha if fill_alpha is not None else alpha) * k * self.alpha))
                ctx.fill_preserve()
            ctx.set_source_rgba(*hexc(col, alpha * k))
            ctx.set_line_width(width * z)
            ctx.stroke()

    def dot(self, p, r, col, alpha=1.0, glow=0.0, screen=False):
        alpha *= self.alpha
        if alpha <= 0.002:
            return
        z = 1 if screen else self.cam[2]
        q = p if screen else self.w2s(p)
        for ctx, k in self._ctxs(glow):
            rr = r * (2.2 if ctx is self.g else 1)
            ctx.set_source_rgba(*hexc(col, alpha * k))
            ctx.new_sub_path(); ctx.arc(q[0], q[1], rr * z, 0, math.tau); ctx.fill()

    def ring(self, p, r, col, width=2.0, alpha=1.0, glow=0.0, screen=False, frac=1.0, dash=None):
        alpha *= self.alpha
        if alpha <= 0.002:
            return
        z = 1 if screen else self.cam[2]
        q = p if screen else self.w2s(p)
        for ctx, k in self._ctxs(glow):
            ctx.set_source_rgba(*hexc(col, alpha * k))
            ctx.set_line_width(width * z)
            ctx.set_dash([d * z for d in dash] if dash else [])
            ctx.new_sub_path(); ctx.arc(q[0], q[1], r * z, -math.pi / 2, -math.pi / 2 + math.tau * frac); ctx.stroke()
            ctx.set_dash([])

    def rect(self, x, y, w, h, fill=None, stroke=None, width=1.4, alpha=1.0, r=4, screen=False, glow=0.0, dash=None):
        alpha *= self.alpha
        if alpha <= 0.002:
            return
        z = 1 if screen else self.cam[2]
        (x, y) = (x, y) if screen else self.w2s((x, y))
        w, h, r = w * z, h * z, min(r * z, w / 2, h / 2)
        for ctx, k in self._ctxs(glow):
            ctx.new_sub_path()
            ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
            ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
            ctx.close_path()
            if fill:
                ctx.set_source_rgba(*hexc(fill, alpha * k))
                ctx.fill_preserve() if stroke else ctx.fill()
            if stroke:
                ctx.set_source_rgba(*hexc(stroke, alpha * k))
                ctx.set_line_width(width * z)
                ctx.set_dash([d * z for d in dash] if dash else [])
                ctx.stroke()
                ctx.set_dash([])

    def arrow(self, a, b, col, width=2.0, alpha=1.0, head=12, glow=0.0, screen=False, shorten=0):
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        a = (a[0] + ux * shorten, a[1] + uy * shorten)
        b = (b[0] - ux * shorten, b[1] - uy * shorten)
        self.line(a, b, col, width, alpha, glow, screen)
        for s in (1, -1):
            p = (b[0] - ux * head - s * uy * head * 0.55, b[1] - uy * head + s * ux * head * 0.55)
            self.line(b, p, col, width, alpha, glow, screen)

    # ---- text: runs of CJK / Latin get the matching face (the toy API has no glyph fallback)
    def _runs(self, s, role):
        fam = FACES[LANG][role]
        if LANG == "zh" and role != "mono":
            return [(s, fam)]
        out, cur, key = [], "", None
        for ch in s:
            if is_cjk(ch) or ch in SYMBOLS:
                k = CJK_FACE["sans"] if role == "mono" else CJK_FACE[role] if ch not in SYMBOLS else "Noto Sans SC"
            else:
                k = fam
            if key is not None and k != key:
                out.append((cur, key)); cur = ""
            cur += ch; key = k
        if cur:
            out.append((cur, key))
        return out

    def _set_font(self, ctx, fam, size, bold, italic):
        ctx.select_font_face(fam, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)

    def measure(self, s, size, role="sans", bold=False, italic=False, spacing=0):
        s = tr(s)
        w = 0.0
        for part, fam in self._runs(s, role):
            self._set_font(self.c, fam, size, bold, italic)
            w += self.c.text_extents(part).x_advance
        return w + spacing * max(0, len(s) - 1)

    def text(self, s, x, y, size=28, col=IVORY, alpha=1.0, role="sans", bold=False, italic=False, anchor="l",
             screen=True, glow=0.0, spacing=0):
        s = tr(s)
        alpha *= self.alpha
        if alpha <= 0.003 or not s:
            return 0
        z = 1 if screen else self.cam[2]
        (x, y) = (x, y) if screen else self.w2s((x, y))
        size_z = size * z
        width = self.measure(s, size_z, role, bold, italic, spacing * z)
        ox = {"l": 0, "c": -width / 2, "r": -width}[anchor]
        for ctx, k in self._ctxs(glow):
            cx = x + ox
            ctx.set_source_rgba(*hexc(col, alpha * k))
            for part, fam in self._runs(s, role):
                self._set_font(ctx, fam, size_z, bold, italic)
                if spacing:
                    for ch in part:
                        ctx.move_to(cx, y); ctx.show_text(ch)
                        cx += ctx.text_extents(ch).x_advance + spacing * z
                else:
                    ctx.move_to(cx, y); ctx.show_text(part)
                    cx += ctx.text_extents(part).x_advance
        return width

    def wrap(self, s, size, max_w, role="sans", bold=False):
        s = tr(s)
        lines = []
        for para in s.split("\n"):
            tokens, buf = [], ""
            for ch in para:
                if is_cjk(ch) or ch == " ":
                    if buf:
                        tokens.append(buf); buf = ""
                    tokens.append(ch)
                else:
                    buf += ch
            if buf:
                tokens.append(buf)
            line = ""
            for tok in tokens:
                trial = line + tok
                if line.strip() and self.measure(trial.rstrip(), size, role, bold) > max_w and tok not in "，。、；：！？）」』》”,.;:!?)":
                    lines.append(line.rstrip()); line = tok.lstrip()
                else:
                    line = trial
            lines.append(line.rstrip())
        return lines

    def paragraph(self, s, x, y, size, max_w, col=IVORY, alpha=1.0, lh=1.5, role="sans", bold=False, anchor="l"):
        lines = self.wrap(s, size, max_w, role, bold)
        for i, ln in enumerate(lines):
            self.text(ln, x, y + i * size * lh, size, col, alpha, role, bold, anchor=anchor)
        return len(lines) * size * lh

    def image(self, surf, x, y, w, h, alpha=1.0, screen=True, r=0):
        """Paint a cairo ImageSurface scaled into (x, y, w, h)."""
        alpha *= self.alpha
        if alpha <= 0.002:
            return
        z = 1 if screen else self.cam[2]
        (x, y) = (x, y) if screen else self.w2s((x, y))
        w, h = w * z, h * z
        ctx = self.c
        ctx.save()
        if r:
            rr = r * z
            ctx.new_sub_path()
            ctx.arc(x + w - rr, y + rr, rr, -math.pi / 2, 0); ctx.arc(x + w - rr, y + h - rr, rr, 0, math.pi / 2)
            ctx.arc(x + rr, y + h - rr, rr, math.pi / 2, math.pi); ctx.arc(x + rr, y + rr, rr, math.pi, 1.5 * math.pi)
            ctx.close_path(); ctx.clip()
        ctx.translate(x, y)
        ctx.scale(w / surf.get_width(), h / surf.get_height())
        ctx.set_source_surface(surf, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint_with_alpha(alpha)
        ctx.restore()

    def finish(self):
        """Compose the frame: base + blurred glow. Returns an RGB uint8 array."""
        self.gs.flush()
        glow = Image.frombuffer("RGBA", (W // 2, H // 2), bytes(self.gs.get_data()), "raw", "BGRA", 0, 1)
        glow = glow.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.Resampling.BILINEAR)
        self.s.flush()
        base = np.frombuffer(self.s.get_data(), np.uint8).reshape(H, W, 4)[:, :, 2::-1].astype(np.uint16)
        g = np.asarray(glow, np.uint16)[:, :, :3]
        return np.minimum(base + g, 255).astype(np.uint8)


# ---------------------------------------------------------------- backdrop and furniture
_BACK = None


def backdrop(fr):
    global _BACK
    if _BACK is None:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        grad = cairo.RadialGradient(W * 0.42, H * 0.42, 80, W * 0.5, H * 0.5, W * 0.75)
        grad.add_color_stop_rgb(0, *hexc(BG2)[:3]); grad.add_color_stop_rgb(1, *hexc(BG)[:3])
        c.set_source(grad); c.paint()
        _BACK = surf
    fr.c.set_source_surface(_BACK); fr.c.paint()


def substrate(fr, alpha):
    """Fine placement grid that moves with the camera: rows of standard-cell sites (for chip scenes)."""
    if alpha <= 0:
        return
    for i in range(-2, 40):
        y = 120 + i * 28
        fr.line((-400, y), (2300, y), "#173039", 0.8, alpha * (0.55 if i % 5 else 1))
    for j in range(-10, 60):
        for i in range(-2, 40, 5):
            fr.dot((j * 56, 120 + i * 28), 1.3, "#2b4a52", alpha)


_SHADE = None


def caption(fr, text, alpha=1.0):
    """Caption over a soft shade. zh: Chinese line + small English line; en: the English line alone."""
    global _SHADE
    if _SHADE is None:
        _SHADE = cairo.LinearGradient(0, 850, 0, 1080)
        _SHADE.add_color_stop_rgba(0, *hexc(BG, 0)); _SHADE.add_color_stop_rgba(0.35, *hexc(BG, 0.85)); _SHADE.add_color_stop_rgba(1, *hexc(BG, 0.92))
    fr.c.set_source(_SHADE); fr.c.rectangle(0, 850, W, 230); fr.c.fill()
    if not text or alpha <= 0:
        return
    zh, en = both(text)
    if LANG == "zh":
        lines = fr.wrap(zh, 44, W - 360, bold=True)
        size = 44 if len(lines) == 1 else 38
        lines = fr.wrap(zh, size, W - 300, bold=True)[:2]
        y0 = 972 - (len(lines) - 1) * 26
        for i, ln in enumerate(lines):
            fr.text(ln, W / 2, y0 + i * 52, size, IVORY, alpha, bold=True, anchor="c", spacing=1)
        if en:
            set_lang("en")
            fr.text(en, W / 2, 1036 if len(lines) == 1 else 1048, 24, MUTED, alpha, italic=True, anchor="c")
            set_lang("zh")
    else:
        lines = fr.wrap(en, 42, W - 340, bold=True)
        size = 42 if len(lines) == 1 else 38
        lines = fr.wrap(en, size, W - 300, bold=True)[:2]
        y0 = 990 - (len(lines) - 1) * 26
        for i, ln in enumerate(lines):
            fr.text(ln, W / 2, y0 + i * 52, size, IVORY, alpha, bold=True, anchor="c")


def furniture(fr, brand, chapter, chapter_alpha=1.0):
    fr.text(brand, 64, 64, 16, MUTED, 0.75, spacing=1)
    if chapter:
        fr.text(chapter, W / 2, 70, 22, GOLD, 0.95 * chapter_alpha, anchor="c", spacing=4 if LANG == "zh" else 2.5)


def title_card(fr, title, subtitle, alpha=1.0, y=470, kicker=None):
    if kicker:
        fr.text(kicker, W / 2, y - 120, 20, MUTED, alpha, anchor="c", spacing=4)
    fr.text(title, W / 2, y, 76 if LANG == "zh" else 80, GOLD, alpha, role="serif", anchor="c", spacing=12 if LANG == "zh" else 1, glow=0.2 * alpha)
    fr.text(subtitle, W / 2, y + 66, 22, IVORY, alpha * 0.9, anchor="c", spacing=3)


def panel(fr, x, y, w, h, alpha=1.0, title=None, accent=None):
    if alpha <= 0:
        return
    fr.rect(x, y, w, h, fill=PANEL_BG, stroke=accent or FAINT, width=1.2, alpha=0.93 * alpha, r=8, screen=True)
    if title:
        fr.text(title, x + 30, y + 46, 21, MUTED, alpha, spacing=2 if LANG == "zh" else 1)


def badge(fr, x, y, s, col, alpha=1.0, size=16, screen=False, w=None, role="sans"):
    s = tr(s)
    tw = w or fr.measure(s, size, role) + 24
    fr.rect(x - tw / 2, y - size + 1, tw, size + 14, fill=NODE_BG, stroke=col, width=1.2, alpha=alpha, r=4, screen=screen)
    fr.text(s, x, y + 6, size, col, alpha, role=role, anchor="c", screen=screen)


def note(fr, s, alpha=1.0, col=MUTED, y=842):
    """Annotation line just above the caption: short, factual side notes."""
    fr.text(s, W / 2, y, 19, col, alpha, anchor="c", spacing=1 if LANG == "zh" else 0.5)


def bar(fr, x, y, w, h, frac, col, alpha=1.0, back="#11262f", glow=0.0):
    fr.rect(x, y, w, h, fill=back, alpha=alpha, r=h / 2 if h < 12 else 4, screen=True)
    if frac > 0:
        fr.rect(x, y, max(h, w * clamp(frac)), h, fill=col, alpha=alpha, r=h / 2 if h < 12 else 4, screen=True, glow=glow)


def code_panel(fr, x, y, w, lines, active=(), alpha=1.0, size=24, lh=40, title=None, done=()):
    """Monospace listing; `active` line numbers glow gold, `done` ones are dimmed teal."""
    h = len(lines) * lh + 40 + (50 if title else 0)
    panel(fr, x, y, w, h, alpha, title)
    y0 = y + (96 if title else 50)
    for i, ln in enumerate(lines):
        n = i + 1
        yy = y0 + i * lh
        on = n in active
        if on:
            fr.rect(x + 2, yy - size - 2, w - 4, lh - 4, fill="#1d2f2a", alpha=alpha, r=2, screen=True)
            fr.rect(x + 2, yy - size - 2, 4, lh - 4, fill=GOLD, alpha=alpha, r=1, screen=True)
        fr.text(str(n), x + 40, yy, size - 6, FAINT if not on else GOLD, alpha, role="mono", anchor="r")
        fr.text(ln, x + 60, yy, size, GOLD if on else (TEAL if n in done else "#d7ddd2"), alpha, role="mono")
    return h


def table(fr, x, y, widths, rows, alpha=1.0, size=24, lh=46, highlight=None, colors=None, header=True):
    for i, row in enumerate(rows):
        yy = y + i * lh
        if highlight and i in highlight:
            fr.rect(x - 14, yy - size - 10, sum(widths) + 28, lh - 4, fill=highlight[i], alpha=0.16 * alpha, r=4, screen=True)
        xx = x
        for j, cell in enumerate(row):
            hd = header and i == 0
            col = (colors or {}).get((i, j), MUTED if hd else IVORY)
            fr.text(cell, xx, yy, size - (4 if hd else 0), col, alpha, spacing=1 if hd and LANG == "zh" else 0)
            xx += widths[j]
        if header and i == 0:
            fr.line((x - 6, yy + 14), (x + sum(widths), yy + 14), FAINT, 1.2, alpha, screen=True)


# ---------------------------------------------------------------- graph view
def nbrs(edges, n):
    return [(v if u == n else u, w) for u, v, w in edges if n in (u, v)]


def badge_dir(n, pos, edges):
    vs = [pos[v] for v, _ in nbrs(edges, n)]
    if not vs:
        return (0, 1)
    mx = sum(p[0] for p in vs) / len(vs) - pos[n][0]
    my = sum(p[1] for p in vs) / len(vs) - pos[n][1]
    d = math.hypot(mx, my) or 1
    return (-mx / d, -my / d)


def graph(fr, pos, edges, colors=None, alpha=1.0, r=36, active=None, cut=None, weights=True, hl_edges=(), edge_alpha=None,
          badges=None, badge_cols=None, badge_dirs=None, names=True, name_size=33, node_alpha=None, glow_nodes=(), dim=0.0, wscale=0.9):
    """Outlined nodes with serif names, weighted wires. colors: {node: colour}; cut: set of 'u|v' keys drawn rose.
    badges: {node: text} drawn on the side away from the wires."""
    colors = colors or {}
    cut = cut or set()
    for u, v, w in edges:
        key = "|".join(sorted((u, v)))
        ea = (edge_alpha(u, v) if edge_alpha else 1.0) * alpha
        if ea <= 0:
            continue
        crossing = key in cut
        hot = key in hl_edges or active in (u, v)
        col = ROSE if crossing else (GOLD if key in hl_edges else ("#7aa5a6" if hot else DIM))
        dimk = 1 - dim * (0 if (active in (u, v) or key in hl_edges) else 1)
        p, q = pos[u], pos[v]
        fr.line(p, q, col, 1 + w * wscale if isinstance(w, (int, float)) else 2, ea * dimk * (0.95 if crossing or hot else 0.55),
                glow=(0.6 if crossing else 0.5 if key in hl_edges else 0) * ea * dimk)
        if weights:
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            fr.dot(m, 17, "#0a1c24", ea * dimk)
            fr.text(f"{w:g}" if isinstance(w, (int, float)) else str(w), m[0], m[1] + 6, 17,
                    ROSE if crossing else (GOLD if key in hl_edges else MUTED), ea * dimk, anchor="c", screen=False)
    for n, p in pos.items():
        na = (node_alpha(n) if node_alpha else 1.0) * alpha * (1 - dim * 0.7 * (n != active))
        if na <= 0:
            continue
        col = colors.get(n, "#9fbcbc")
        fr.dot(p, r, NODE_BG, na)
        fr.ring(p, r, col, 2.8, na, glow=0.6 * na if (n == active or n in glow_nodes) else 0)
        if names:
            fr.text(n, p[0], p[1] + name_size * 0.36, name_size, IVORY, na, role="serif", anchor="c", screen=False)
        if badges and n in badges:
            d = (badge_dirs or {}).get(n) or badge_dir(n, pos, edges)
            bx, by = p[0] + d[0] * (r + 40), p[1] + d[1] * (r + 26)
            badge(fr, bx, by, badges[n], (badge_cols or colors).get(n, col), na)


def vote_panel(fr, x, y, votes, alpha, title, winner=None, hl=0.0, colors=None, unit=46, slots=6, label_word=None, grow=1.0):
    """One register per label: bars proportional to the summed weight."""
    order = sorted(votes, key=lambda l: (-votes[l], l))
    h = 110 + 92 * len(order)
    panel(fr, x, y, 640, h, alpha, title)
    lw = label_word if label_word is not None else L("标签", "label")
    for i, lab in enumerate(order):
        yy = y + 110 + i * 92
        on = (lab == winner) * hl
        col = (colors or {}).get(lab, GOLD)
        fr.text(f"{tr(lw)} {lab}", x + 30, yy + 9, 25, col, alpha)
        fr.rect(x + 150, yy - 15, unit * slots, 30, fill="#11262f", alpha=alpha, r=4, screen=True)
        v = votes[lab] * clamp(grow * 1.4 - i * 0.2)
        if v > 0:
            fr.rect(x + 150, yy - 15, min(unit * slots, unit * v), 30, fill=col, alpha=alpha * (0.5 + 0.5 * on), r=4, screen=True, glow=0.6 * on)
        fr.text(f"{votes[lab]:g}", x + 150 + unit * slots + 34, yy + 12, 32, IVORY if on else MUTED, alpha * clamp(grow * 2 - i * 0.3), bold=bool(on))
    return h


def fit(pos, box):
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / max(1e-9, max(xs) - min(xs)), (y1 - y0) / max(1e-9, max(ys) - min(ys)))
    ox = x0 + ((x1 - x0) - s * (max(xs) - min(xs))) / 2
    oy = y0 + ((y1 - y0) - s * (max(ys) - min(ys))) / 2
    return {k: (ox + (p[0] - min(xs)) * s, oy + (p[1] - min(ys)) * s) for k, p in pos.items()}


def cut_keys(edges, labels):
    return {"|".join(sorted((u, v))) for u, v, w in edges if labels[u] != labels[v]}


def cut_value(edges, labels):
    return sum(w for u, v, w in edges if labels[u] != labels[v])


# ---------------------------------------------------------------- timeline
class Beat:
    def __init__(self, text=None, hold=0.0):
        self.text = text
        zh, en = both(text)
        self.dur = max(hold, min_read(zh, "zh"), min_read(en, "en"), 0.6) if text else max(hold, 0.6)


class Scene:
    def __init__(self, sid, draw, beats, chapter=None, tail=0.4, fade=True):
        self.id, self.draw, self.chapter, self.fade = sid, draw, chapter, fade
        self.beats = [b if isinstance(b, Beat) else Beat(*b) if isinstance(b, list) else Beat(b) for b in beats]
        self.starts, acc = [], 0.0
        for b in self.beats:
            self.starts.append(acc)
            acc += b.dur
        self.dur = acc + tail


class Clock:
    """Local scene time with beat helpers, handed to each scene's draw(fr, c)."""

    def __init__(self, scene, t):
        self.scene, self.t = scene, t
        self.k = max([i for i, s in enumerate(scene.starts) if s <= t + 1e-9] or [0])

    def at(self, k):
        return self.scene.starts[k] if k < len(self.scene.starts) else self.scene.dur

    def since(self, k):
        return self.t - self.at(k)

    def p(self, k, d=0.8, delay=0.0):
        return ease((self.t - self.at(k) - delay) / d) if d > 0 else float(self.t >= self.at(k) + delay)

    def on(self, k):
        return self.t >= self.at(k)

    def span(self, k0, k1=None):
        """0→1 progress across beats k0..k1 (exclusive end)."""
        a, b = self.at(k0), self.at(k1 if k1 is not None else k0 + 1)
        return clamp((self.t - a) / max(1e-6, b - a))


class Film:
    def __init__(self, id, kind, title, subtitle, brand, scenes, music="score:calm", seed=7, poster_at=None, why=None, langs=("zh", "en")):
        self.ID, self.KIND, self.TITLE, self.SUBTITLE, self.BRAND = id, kind, title, subtitle, brand
        self.SCENES, self.MUSIC, self.SEED, self.POSTER_AT, self.WHY, self.LANGS = scenes, music, seed, poster_at, why, langs
        self.rows, t = [], 0.0
        for sc in scenes:
            self.rows.append((t, sc))
            t += sc.dur
        self.total = t

    def chapter_at(self, i):
        for j in range(i, -1, -1):
            if self.rows[j][1].chapter:
                return self.rows[j][1].chapter, self.rows[j][0]
        return None, 0

    def render(self, fr, T):
        for i, (t0, sc) in enumerate(self.rows):
            if T < t0 + sc.dur or i == len(self.rows) - 1:
                break
        lt = T - t0
        fr.clear()
        backdrop(fr)
        clock = Clock(sc, lt)
        fade = clamp(lt / 0.45) * clamp((sc.dur - lt) / 0.45) if sc.fade else 1.0
        fr.alpha = fade
        sc.draw(fr, clock)
        fr.set_cam()
        fr.alpha = 1.0
        ch, ch_t = self.chapter_at(i)
        furniture(fr, self.BRAND, ch, ramp(T, ch_t, ch_t + 0.8))
        b = sc.beats[clock.k] if sc.beats else None
        text_alpha = 0.0
        if b and b.text:
            k, bt = clock.k, lt - sc.starts[clock.k]
            prev_same = k > 0 and sc.beats[k - 1].text == b.text
            next_same = k + 1 < len(sc.beats) and sc.beats[k + 1].text == b.text
            text_alpha = (1.0 if prev_same else clamp(bt / 0.25)) * (1.0 if next_same else clamp((b.dur - bt) / 0.25)) * fade
        caption(fr, b.text if b else None, text_alpha)
        img = fr.finish()
        g = ramp(T, 0, 0.6) * (1 - ramp(T, self.total - 1.2, self.total))
        if g < 1:
            img = (img.astype(np.float32) * g).astype(np.uint8)
        return img

    def captions(self, lang):
        out = []
        for t0, sc in self.rows:
            for b, s in zip(sc.beats, sc.starts):
                if not b.text:
                    continue
                text = both(b.text)[1 if lang == "en" else 0]
                start, end = t0 + s, t0 + s + b.dur
                if out and out[-1]["text"] == text and abs(out[-1]["end"] - start) < 1e-6:
                    out[-1]["end"] = round(end, 3)
                else:
                    out.append({"start": round(start, 3), "end": round(end, 3), "text": text, "sceneId": sc.id})
        return out

    def chapters(self, lang):
        out, seen = [], None
        for t0, sc in self.rows:
            if sc.chapter and sc.chapter != seen:
                seen = sc.chapter
                out.append({"t": round(t0, 2), "title": both(sc.chapter)[1 if lang == "en" else 0], "sceneId": sc.id})
        return out


def math_line(fr, parts, cx, y, size=60, alpha=1.0, anchor="c"):
    """One line of serif maths. parts: (text, colour[, "sub" | "sup" | "under"]). "under" sits centred below
    the previous part (argmax over L, a sum's index)."""
    def m(p):
        mode = p[2] if len(p) > 2 else None
        return fr.measure(tr(p[0]), size * (0.5 if mode else 1), "serif")
    total, prev_w = 0.0, 0.0
    for p in parts:
        mode = p[2] if len(p) > 2 else None
        w = m(p)
        total += max(0.0, w - prev_w) if mode == "under" else w
        prev_w = w if mode != "under" else prev_w
    x = cx - total / 2 if anchor == "c" else cx
    last = (x, 0.0)
    for p in parts:
        mode = p[2] if len(p) > 2 else None
        w = m(p)
        if mode == "under":
            lx, lw = last
            fr.text(p[0], lx + lw / 2, y + size * 0.5, size * 0.42, p[1], alpha, role="serif", anchor="c")
            continue
        sz, dy = (size * 0.5, size * 0.22) if mode == "sub" else (size * 0.5, -size * 0.42) if mode == "sup" else (size, 0)
        fr.text(p[0], x, y + dy, sz, p[1], alpha, role="serif")
        last = (x, w)
        x += w
    return total
