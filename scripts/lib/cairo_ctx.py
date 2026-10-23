"""Thin ctypes binding to libcairo plus a small drawing API shared by the film renderer and the
slide builder. No pycairo needed: only the system/Homebrew libcairo shared library.

Set LC_CAIRO_LIB to point at libcairo if it is not in a standard place.
Fonts: LC_SANS_FONT / LC_SERIF_FONT / LC_MONO_FONT (family names) override the defaults.
"""
import ctypes
import ctypes.util
import math
import os

_CANDIDATES = [os.environ.get("LC_CAIRO_LIB"), "/opt/homebrew/lib/libcairo.2.dylib", "/usr/local/lib/libcairo.2.dylib",
               ctypes.util.find_library("cairo"), "libcairo.so.2"]
for _p in _CANDIDATES:
    if not _p:
        continue
    try:
        C = ctypes.CDLL(_p)
        break
    except OSError:
        continue
else:
    raise OSError("找不到 libcairo：请安装 cairo（如 brew install cairo）或设置 LC_CAIRO_LIB")

P, D, I, S = ctypes.c_void_p, ctypes.c_double, ctypes.c_int, ctypes.c_char_p


class TextExtents(ctypes.Structure):
    _fields_ = [("x_bearing", D), ("y_bearing", D), ("width", D), ("height", D), ("x_advance", D), ("y_advance", D)]


class FontExtents(ctypes.Structure):
    _fields_ = [("ascent", D), ("descent", D), ("height", D), ("max_x_advance", D), ("max_y_advance", D)]


_SIG = {
    "cairo_image_surface_create": ([I, I, I], P), "cairo_pdf_surface_create": ([S, D, D], P),
    "cairo_create": ([P], P), "cairo_destroy": ([P], None), "cairo_surface_destroy": ([P], None),
    "cairo_surface_flush": ([P], None), "cairo_surface_finish": ([P], None),
    "cairo_image_surface_get_data": ([P], ctypes.POINTER(ctypes.c_ubyte)), "cairo_image_surface_get_stride": ([P], I),
    "cairo_surface_write_to_png": ([P, S], I), "cairo_show_page": ([P], None),
    "cairo_save": ([P], None), "cairo_restore": ([P], None),
    "cairo_set_source_rgba": ([P, D, D, D, D], None), "cairo_paint": ([P], None), "cairo_paint_with_alpha": ([P, D], None),
    "cairo_rectangle": ([P, D, D, D, D], None), "cairo_arc": ([P, D, D, D, D, D], None),
    "cairo_move_to": ([P, D, D], None), "cairo_line_to": ([P, D, D], None), "cairo_rel_line_to": ([P, D, D], None),
    "cairo_curve_to": ([P, D, D, D, D, D, D], None), "cairo_close_path": ([P], None), "cairo_new_path": ([P], None),
    "cairo_new_sub_path": ([P], None), "cairo_fill": ([P], None), "cairo_fill_preserve": ([P], None),
    "cairo_stroke": ([P], None), "cairo_stroke_preserve": ([P], None), "cairo_set_line_width": ([P, D], None),
    "cairo_set_line_cap": ([P, I], None), "cairo_set_line_join": ([P, I], None),
    "cairo_set_dash": ([P, ctypes.POINTER(D), I, D], None),
    "cairo_select_font_face": ([P, S, I, I], None), "cairo_set_font_size": ([P, D], None),
    "cairo_show_text": ([P, S], None), "cairo_text_extents": ([P, S, ctypes.POINTER(TextExtents)], None),
    "cairo_font_extents": ([P, ctypes.POINTER(FontExtents)], None),
    "cairo_translate": ([P, D, D], None), "cairo_scale": ([P, D, D], None), "cairo_rotate": ([P, D], None),
    "cairo_pattern_create_linear": ([D, D, D, D], P), "cairo_pattern_create_radial": ([D, D, D, D, D, D], P),
    "cairo_pattern_add_color_stop_rgba": ([P, D, D, D, D, D], None), "cairo_set_source": ([P, P], None),
    "cairo_pattern_destroy": ([P], None), "cairo_clip": ([P], None), "cairo_reset_clip": ([P], None),
    "cairo_push_group": ([P], None), "cairo_pop_group_to_source": ([P], None),
}
for _name, (_args, _res) in _SIG.items():
    fn = getattr(C, _name)
    fn.argtypes, fn.restype = _args, _res

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fonts", "noto-sans-sc")


def register_bundled_fonts():
    """Make fonts/noto-sans-sc/*.otf visible to cairo for this process only (no system install).
    macOS: CoreText process scope. Elsewhere cairo uses fontconfig: install the files or set LC_SANS_FONT."""
    files = sorted(f for f in os.listdir(FONT_DIR) if f.endswith(".otf")) if os.path.isdir(FONT_DIR) else []
    if not files or not os.path.isdir("/System/Library/Frameworks/CoreText.framework"):
        return []
    cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    ct = ctypes.CDLL("/System/Library/Frameworks/CoreText.framework/CoreText")
    cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
    cf.CFURLCreateFromFileSystemRepresentation.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_bool]
    ct.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool
    ct.CTFontManagerRegisterFontsForURL.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    done = []
    for f in files:
        path = os.path.abspath(os.path.join(FONT_DIR, f)).encode()
        url = cf.CFURLCreateFromFileSystemRepresentation(None, path, len(path), False)
        if ct.CTFontManagerRegisterFontsForURL(url, 1, None):  # 1 = kCTFontManagerScopeProcess
            done.append(f)
    return done


BUNDLED_FONTS = register_bundled_fonts()

# Noto Sans SC (SIL OFL 1.1, fonts/noto-sans-sc) for every Chinese/Latin role; the serif role is kept
# as a name so titles can be restyled later, but it uses the same face.
SANS = os.environ.get("LC_SANS_FONT", "Noto Sans SC")
SERIF = os.environ.get("LC_SERIF_FONT", SANS)
MONO = os.environ.get("LC_MONO_FONT", "Menlo")

# Noto Sans SC has no sub/superscript code points: draw them as smaller digits/letters shifted off the
# baseline (scale, baseline offset as a fraction of the font size).
SUB = dict(zip("₀₁₂₃₄₅₆₇₈₉ₓₑ₍₎", "0123456789xe()"))
SUP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻ⁿᵀ", "0123456789−nT"))
SHIFT = {"sub": (0.62, 0.16), "sup": (0.62, -0.40), None: (1.0, 0.0)}
# Remaining characters the face lacks, drawn with a face that has them (toy text API has no fallback).
GLYPH_FALLBACK = {"⌈": "Menlo", "⌉": "Menlo"}


def runs(s, family):
    """Split s into (text, family, mode) runs: mode is None, "sub" or "sup"."""
    out, cur, key = [], "", None
    for ch in s:
        if ch in SUB:
            k, ch = (family, "sub"), SUB[ch]
        elif ch in SUP:
            k, ch = (family, "sup"), SUP[ch]
        else:
            k = (GLYPH_FALLBACK.get(ch, family), None)
        if key is not None and k != key:
            out.append((cur, *key)); cur = ""
        cur += ch; key = k
    if cur:
        out.append((cur, *key))
    return out


def hexc(c, a=1.0):
    c = c.lstrip("#")
    return (int(c[0:2], 16) / 255, int(c[2:4], 16) / 255, int(c[4:6], 16) / 255, a)


def mix(a, b, t):
    ca, cb = hexc(a), hexc(b)
    return "#" + "".join(f"{round((x + (y - x) * t) * 255):02x}" for x, y in zip(ca[:3], cb[:3]))


class Canvas:
    """Drawing context. kind='image' (W×H pixels, ARGB32) or kind='pdf' (W×H points, multi-page)."""

    def __init__(self, W, H, kind="image", path=None):
        self.W, self.H, self.kind = W, H, kind
        self.surface = C.cairo_pdf_surface_create(path.encode(), W, H) if kind == "pdf" else C.cairo_image_surface_create(0, W, H)
        self.cr = C.cairo_create(self.surface)
        self._font = None
        self.alpha = 1.0

    # ---- state ----
    def save(self): C.cairo_save(self.cr)

    def restore(self):
        C.cairo_restore(self.cr)
        self._font = None
    def translate(self, x, y): C.cairo_translate(self.cr, x, y)
    def scale(self, sx, sy=None): C.cairo_scale(self.cr, sx, sx if sy is None else sy)
    def rotate(self, a): C.cairo_rotate(self.cr, a)

    def color(self, c, a=1.0):
        r, g, b, aa = hexc(c, a) if isinstance(c, str) else c
        C.cairo_set_source_rgba(self.cr, r, g, b, aa * self.alpha)

    def group(self):
        C.cairo_push_group(self.cr)  # push/pop save and restore the gstate, including the font
        self._font = None

    def end_group(self, alpha=1.0):
        C.cairo_pop_group_to_source(self.cr)
        self._font = None
        C.cairo_paint_with_alpha(self.cr, max(0.0, min(1.0, alpha)))

    def clip_rect(self, x, y, w, h):
        C.cairo_rectangle(self.cr, x, y, w, h); C.cairo_clip(self.cr)

    def reset_clip(self): C.cairo_reset_clip(self.cr)

    # ---- shapes ----
    def fill_all(self, c):
        self.color(c); C.cairo_paint(self.cr)

    def gradient(self, x0, y0, x1, y1, stops, rect=None, radial=None):
        pat = C.cairo_pattern_create_radial(*radial) if radial else C.cairo_pattern_create_linear(x0, y0, x1, y1)
        for off, col, a in stops:
            r, g, b, _ = hexc(col)
            C.cairo_pattern_add_color_stop_rgba(pat, off, r, g, b, a)
        C.cairo_set_source(self.cr, pat)
        if rect:
            C.cairo_rectangle(self.cr, *rect); C.cairo_fill(self.cr)
        else:
            C.cairo_paint(self.cr)
        C.cairo_pattern_destroy(pat)

    def _path_rrect(self, x, y, w, h, r):
        r = max(0, min(r, w / 2, h / 2))
        cr = self.cr
        C.cairo_new_sub_path(cr)
        C.cairo_arc(cr, x + w - r, y + r, r, -math.pi / 2, 0)
        C.cairo_arc(cr, x + w - r, y + h - r, r, 0, math.pi / 2)
        C.cairo_arc(cr, x + r, y + h - r, r, math.pi / 2, math.pi)
        C.cairo_arc(cr, x + r, y + r, r, math.pi, 1.5 * math.pi)
        C.cairo_close_path(cr)

    def rect(self, x, y, w, h, fill=None, stroke=None, width=1.5, r=0, alpha=1.0, dash=None):
        self._path_rrect(x, y, w, h, r) if r else C.cairo_rectangle(self.cr, x, y, w, h)
        self._paint(fill, stroke, width, alpha, dash)

    def circle(self, x, y, rad, fill=None, stroke=None, width=2, alpha=1.0, dash=None):
        C.cairo_new_sub_path(self.cr)
        C.cairo_arc(self.cr, x, y, rad, 0, 2 * math.pi)
        self._paint(fill, stroke, width, alpha, dash)

    def poly(self, pts, fill=None, stroke=None, width=2, alpha=1.0, close=True, dash=None, join=1):
        C.cairo_set_line_join(self.cr, join)
        C.cairo_move_to(self.cr, *pts[0])
        for p in pts[1:]:
            C.cairo_line_to(self.cr, *p)
        if close:
            C.cairo_close_path(self.cr)
        self._paint(fill, stroke, width, alpha, dash)

    def line(self, x1, y1, x2, y2, c, width=2, alpha=1.0, dash=None, cap=1):
        C.cairo_set_line_cap(self.cr, cap)
        C.cairo_move_to(self.cr, x1, y1); C.cairo_line_to(self.cr, x2, y2)
        self._paint(None, c, width, alpha, dash)

    def curve(self, pts, c, width=2, alpha=1.0, dash=None):
        C.cairo_move_to(self.cr, *pts[0]); C.cairo_curve_to(self.cr, *pts[1], *pts[2], *pts[3])
        self._paint(None, c, width, alpha, dash)

    def arrow(self, x1, y1, x2, y2, c, width=2.5, head=12, alpha=1.0, dash=None, shorten=0):
        ang = math.atan2(y2 - y1, x2 - x1)
        x2 -= math.cos(ang) * shorten; y2 -= math.sin(ang) * shorten
        x1 += math.cos(ang) * shorten * 0; y1 += 0
        self.line(x1, y1, x2 - math.cos(ang) * head * .6, y2 - math.sin(ang) * head * .6, c, width, alpha, dash)
        pts = [(x2, y2), (x2 - head * math.cos(ang - .42), y2 - head * math.sin(ang - .42)), (x2 - head * math.cos(ang + .42), y2 - head * math.sin(ang + .42))]
        self.poly(pts, fill=c, alpha=alpha)

    def _paint(self, fill, stroke, width, alpha, dash):
        cr = self.cr
        if fill is not None:
            self.color(fill, alpha)
            (C.cairo_fill_preserve if stroke is not None else C.cairo_fill)(cr)
        if stroke is not None:
            self.color(stroke, alpha)
            C.cairo_set_line_width(cr, width)
            if dash:
                arr = (D * len(dash))(*dash)
                C.cairo_set_dash(cr, arr, len(dash), 0)
            C.cairo_stroke(cr)
            if dash:
                C.cairo_set_dash(cr, None, 0, 0)
        if fill is None and stroke is None:
            C.cairo_new_path(cr)

    # ---- text ----
    def font(self, size, weight="normal", family=None, italic=False):
        fam = family or SANS
        key = (fam, size, weight, italic)
        if self._font != key:
            C.cairo_select_font_face(self.cr, fam.encode(), 1 if italic else 0, 1 if weight == "bold" else 0)
            C.cairo_set_font_size(self.cr, size)
            self._font = key

    def measure(self, s, size, weight="normal", family=None):
        total = 0.0
        for part, fam, mode in runs(s, family or SANS):
            self.font(size * SHIFT[mode][0], weight, fam)
            e = TextExtents()
            C.cairo_text_extents(self.cr, part.encode(), ctypes.byref(e))
            total += e.x_advance
        return total

    def text(self, x, y, s, size=32, c="#f2f3e9", weight="normal", align="left", family=None, alpha=1.0, baseline=True):
        """y is the baseline unless baseline=False (then y is the top of the line box)."""
        if s is None or s == "":
            return 0
        s = str(s)
        w = self.measure(s, size, weight, family)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        if not baseline:
            y += size * 0.88
        self.color(c, alpha)
        for part, fam, mode in runs(s, family or SANS):
            scale, dy = SHIFT[mode]
            self.font(size * scale, weight, fam)
            C.cairo_move_to(self.cr, x, y + dy * size)
            C.cairo_show_text(self.cr, part.encode())
            e = TextExtents()
            C.cairo_text_extents(self.cr, part.encode(), ctypes.byref(e))
            x += e.x_advance
        return w

    def text_mixed(self, x, y, s, size=28, c="#f2f3e9", latin=None, cjk=None, alpha=1.0, weight="normal"):
        """Monospace for ASCII runs, a CJK face for everything else (code with Chinese comments)."""
        latin, cjk = latin or MONO, cjk or SANS
        run, kind, xx = "", None, x
        for ch in str(s) + "\0":
            k = "l" if ch.isascii() else "c"
            if ch == "\0" or (kind and k != kind):
                if run:
                    xx += self.text(xx, y, run, size, c, weight, family=latin if kind == "l" else cjk, alpha=alpha)
                run = ""
            kind = k
            run += ch
        return xx - x

    def wrap(self, s, size, max_w, weight="normal", family=None):
        """Greedy wrap for mixed Chinese/Latin text: break between CJK characters or at spaces."""
        lines = []
        for para in str(s).split("\n"):
            tokens, buf = [], ""
            for ch in para:
                if ord(ch) > 0x2E7F or ch == " ":
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
                if line and self.measure(trial, size, weight, family) > max_w and tok not in "，。、；：！？）」』》,.;:!?)":
                    lines.append(line.rstrip()); line = tok.lstrip()
                else:
                    line = trial
            lines.append(line.rstrip())
        return lines

    def paragraph(self, x, y, s, size, max_w, c="#f2f3e9", lh=1.55, weight="normal", family=None, alpha=1.0, align="left"):
        lines = self.wrap(s, size, max_w, weight, family)
        for i, ln in enumerate(lines):
            self.text(x if align == "left" else (x + max_w / 2 if align == "center" else x + max_w), y + i * size * lh, ln, size, c, weight, align, family, alpha)
        return len(lines) * size * lh

    # ---- output ----
    def bgra(self):
        C.cairo_surface_flush(self.surface)
        stride = C.cairo_image_surface_get_stride(self.surface)
        data = C.cairo_image_surface_get_data(self.surface)
        return ctypes.string_at(data, stride * self.H)

    def png(self, path):
        C.cairo_surface_flush(self.surface)
        C.cairo_surface_write_to_png(self.surface, str(path).encode())

    def next_page(self):
        C.cairo_show_page(self.cr)

    def close(self):
        C.cairo_destroy(self.cr)
        C.cairo_surface_finish(self.surface)
        C.cairo_surface_destroy(self.surface)
