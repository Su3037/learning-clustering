#!/usr/bin/env python3
"""Build one module's deck from content/modules/<id>/slides.json.

The same slide description is drawn three ways:
  * PDF with real (selectable) text, through libcairo         → site/slides/<id>/<id>.pdf
  * PNG previews for the web viewer (1600×900) and thumbnails  → site/slides/<id>/p01.png …
  * editable PPTX with native text boxes, shapes, notes          → site/slides/<id>/<id>.pptx
Every page carries "Module 0X · 名称" and "p/total" in its footer; the web viewer shows the same
numbers. Figures are drawn by video/<id>/figures.py with the film's drawing kit, so diagrams in
slides and films share one visual language and read the same engine traces.

Run with the Python that has python-pptx (see docs/BUILD.md):
  ~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/slides/build_slides.py m07-kernighan-lin
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "film"))
# Slides are redistributed as PDF/PPTX: every role, code included, uses the bundled Noto Sans SC (OFL).
os.environ.setdefault("LC_MONO_FONT", "Noto Sans SC")
from cairo_ctx import Canvas, SANS, SERIF, MONO, hexc, runs  # noqa: E402
import kit  # noqa: E402
from kit import INK, MUTED, FAINT, GOLD, TEAL, RED, BLUE, PANEL2  # noqa: E402

W, H = 1920, 1080


class Recorder:
    """Records the subset of the Canvas API that kit.py and figures use."""

    def __init__(self):
        self.ops = []
        self._m = Canvas(64, 64)
        self.alpha = 1.0
        self.tf = [(0.0, 0.0, 1.0)]

    def place(self, dx, dy, s=1.0):
        """Context manager: draw a film-sized figure into a sub-area (offset dx, dy, scale s)."""
        rec = self

        class _P:
            def __enter__(self_):
                ox, oy, os_ = rec.tf[-1]
                rec.tf.append((ox + dx * os_, oy + dy * os_, os_ * s))

            def __exit__(self_, *a):
                rec.tf.pop()
        return _P()

    def _T(self, x, y):
        ox, oy, s = self.tf[-1]
        return ox + x * s, oy + y * s

    def _S(self, v):
        return v * self.tf[-1][2]

    def _D(self, dash):
        return [self._S(d) for d in dash] if dash else None

    def measure(self, s, size, weight="normal", family=None):
        return self._m.measure(s, size, weight, family)

    def wrap(self, *a, **k):
        return self._m.wrap(*a, **k)

    def rect(self, x, y, w, h, fill=None, stroke=None, width=1.5, r=0, alpha=1.0, dash=None):
        x, y = self._T(x, y)
        self.ops.append(("rect", dict(x=x, y=y, w=self._S(w), h=self._S(h), fill=fill, stroke=stroke, width=self._S(width), r=self._S(r), alpha=alpha, dash=self._D(dash))))

    def circle(self, x, y, rad, fill=None, stroke=None, width=2, alpha=1.0, dash=None):
        x, y = self._T(x, y)
        self.ops.append(("circle", dict(x=x, y=y, rad=self._S(rad), fill=fill, stroke=stroke, width=self._S(width), alpha=alpha, dash=self._D(dash))))

    def line(self, x1, y1, x2, y2, c, width=2, alpha=1.0, dash=None, cap=1):
        x1, y1 = self._T(x1, y1); x2, y2 = self._T(x2, y2)
        self.ops.append(("line", dict(x1=x1, y1=y1, x2=x2, y2=y2, c=c, width=self._S(width), alpha=alpha, dash=self._D(dash))))

    def poly(self, pts, fill=None, stroke=None, width=2, alpha=1.0, close=True, dash=None, join=1):
        self.ops.append(("poly", dict(pts=[self._T(*p) for p in pts], fill=fill, stroke=stroke, width=self._S(width), alpha=alpha, close=close, dash=self._D(dash))))

    def arrow(self, x1, y1, x2, y2, c, width=2.5, head=12, alpha=1.0, dash=None, shorten=0):
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        x2 -= math.cos(ang) * shorten; y2 -= math.sin(ang) * shorten
        self.line(x1, y1, x2 - math.cos(ang) * head * .6, y2 - math.sin(ang) * head * .6, c, width, alpha, dash)
        self.poly([(x2, y2), (x2 - head * math.cos(ang - .42), y2 - head * math.sin(ang - .42)), (x2 - head * math.cos(ang + .42), y2 - head * math.sin(ang + .42))], fill=c, alpha=alpha)

    def text(self, x, y, s, size=32, c=INK, weight="normal", align="left", family=None, alpha=1.0, baseline=True):
        if s is None or s == "":
            return 0
        s = str(s)
        w = self.measure(s, size, weight, family)
        if not baseline:
            y += size * 0.88
        tx, ty = self._T(x, y)
        self.ops.append(("text", dict(x=tx, y=ty, s=s, size=self._S(size), c=c, weight=weight, align=align, family=family or SANS, alpha=alpha, w=self._S(w))))
        return w

    def text_mixed(self, x, y, s, size=28, c=INK, latin=None, cjk=None, alpha=1.0, weight="normal"):
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

    def paragraph(self, x, y, s, size, max_w, c=INK, lh=1.55, weight="normal", family=None, alpha=1.0, align="left"):
        """One wrapped paragraph: PDF/PNG draw the wrapped lines, PPTX gets a single wrapping text box."""
        lines = self.wrap(s, size, max_w, weight, family)
        tx, ty = self._T(x, y)
        self.ops.append(("para", dict(x=tx, y=ty, s=str(s), lines=lines, size=self._S(size), max_w=self._S(max_w), c=c, lh=lh, weight=weight,
                                      family=family or SANS, alpha=alpha, align=align)))
        return len(lines) * size * lh

    def color(self, *a, **k):
        pass


def replay_cairo(ops, cv, s=1.0):
    for kind, o in ops:
        if kind == "rect":
            cv.rect(o["x"] * s, o["y"] * s, o["w"] * s, o["h"] * s, o["fill"], o["stroke"], o["width"] * s, o["r"] * s, o["alpha"], [d * s for d in o["dash"]] if o["dash"] else None)
        elif kind == "circle":
            cv.circle(o["x"] * s, o["y"] * s, o["rad"] * s, o["fill"], o["stroke"], o["width"] * s, o["alpha"], [d * s for d in o["dash"]] if o["dash"] else None)
        elif kind == "line":
            cv.line(o["x1"] * s, o["y1"] * s, o["x2"] * s, o["y2"] * s, o["c"], o["width"] * s, o["alpha"], [d * s for d in o["dash"]] if o["dash"] else None)
        elif kind == "poly":
            cv.poly([(x * s, y * s) for x, y in o["pts"]], o["fill"], o["stroke"], o["width"] * s, o["alpha"], o["close"], [d * s for d in o["dash"]] if o["dash"] else None)
        elif kind == "text":
            cv.text(o["x"] * s, o["y"] * s, o["s"], o["size"] * s, o["c"], o["weight"], o["align"], o["family"], o["alpha"])
        elif kind == "para":
            for i, ln in enumerate(o["lines"]):
                x = o["x"] if o["align"] == "left" else (o["x"] + o["max_w"] / 2 if o["align"] == "center" else o["x"] + o["max_w"])
                cv.text(x * s, (o["y"] + i * o["size"] * o["lh"]) * s, ln, o["size"] * s, o["c"], o["weight"], o["align"], o["family"], o["alpha"])


# ---------------- PPTX backend ----------------
def replay_pptx(ops, slide, Emu, RGBColor, MSO_SHAPE, MSO_CONNECTOR, MSO_LINE, PP_ALIGN):
    px = 6350  # 1920 px ↔ 13.333 in
    from pptx.oxml.ns import qn

    def set_alpha(fill_elm, alpha):
        if alpha >= 0.999:
            return
        clr = fill_elm.find(qn("a:srgbClr"))
        if clr is not None:
            a = clr.makeelement(qn("a:alpha"), {"val": str(int(alpha * 100000))})
            clr.append(a)

    def style_line(line, c, width, dash, alpha=1.0):
        if c is None:
            line.fill.background()
            return
        line.color.rgb = RGBColor.from_string(c.lstrip("#")[:6])
        line.width = Emu(int(width * px))
        if dash:
            line.dash_style = MSO_LINE.DASH
        if alpha < 0.999:
            set_alpha(line._get_or_add_ln().find(qn("a:solidFill")), alpha)

    for kind, o in ops:
        if kind in ("rect", "circle"):
            if kind == "rect":
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if o["r"] else MSO_SHAPE.RECTANGLE, Emu(int(o["x"] * px)), Emu(int(o["y"] * px)), Emu(int(max(1, o["w"]) * px)), Emu(int(max(1, o["h"]) * px)))
                if o["r"]:
                    shape.adjustments[0] = min(0.5, o["r"] / max(1, min(o["w"], o["h"])))
            else:
                r = o["rad"]
                shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Emu(int((o["x"] - r) * px)), Emu(int((o["y"] - r) * px)), Emu(int(2 * r * px)), Emu(int(2 * r * px)))
            shape.shadow.inherit = False
            if o["fill"]:
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor.from_string(o["fill"].lstrip("#")[:6])
                set_alpha(shape.fill._xPr.find(qn("a:solidFill")), o["alpha"])
            else:
                shape.fill.background()
            style_line(shape.line, o["stroke"], o["width"], o["dash"], o["alpha"])
            shape.text_frame.text = ""
        elif kind == "line":
            ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(o["x1"] * px)), Emu(int(o["y1"] * px)), Emu(int(o["x2"] * px)), Emu(int(o["y2"] * px)))
            style_line(ln.line, o["c"], o["width"], o["dash"], o["alpha"])
        elif kind == "poly":
            pts = o["pts"]
            fb = slide.shapes.build_freeform(Emu(int(pts[0][0] * px)), Emu(int(pts[0][1] * px)), scale=1.0)
            fb.add_line_segments([(Emu(int(x * px)), Emu(int(y * px))) for x, y in pts[1:]], close=o["close"])
            shape = fb.convert_to_shape()
            if o["fill"]:
                shape.fill.solid(); shape.fill.fore_color.rgb = RGBColor.from_string(o["fill"].lstrip("#")[:6])
            else:
                shape.fill.background()
            style_line(shape.line, o["stroke"], o["width"], o["dash"], o["alpha"])
        elif kind == "para":
            top = o["y"] - o["size"] * 1.02
            tb = slide.shapes.add_textbox(Emu(int(o["x"] * px)), Emu(int(top * px)), Emu(int((o["max_w"] + o["size"] * 0.5) * px)), Emu(int(len(o["lines"]) * o["size"] * o["lh"] * px)))
            tf = tb.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[o["align"]]
            p.line_spacing = o["lh"] * 0.84
            add_runs(p, o, px, Emu, RGBColor)
        elif kind == "text":
            w = o["w"] + o["size"] * 0.6
            x = o["x"] - (w / 2 if o["align"] == "center" else w - o["size"] * 0.3 if o["align"] == "right" else o["size"] * 0.05)
            top = o["y"] - o["size"] * 1.02
            tb = slide.shapes.add_textbox(Emu(int(x * px)), Emu(int(top * px)), Emu(int(w * px)), Emu(int(o["size"] * 1.35 * px)))
            tf = tb.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.word_wrap = False
            p = tf.paragraphs[0]
            p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[o["align"]]
            add_runs(p, o, px, Emu, RGBColor)


def add_runs(p, o, px, Emu, RGBColor):
    from pptx.oxml.ns import qn
    """One PPTX run per font/sub/superscript segment, all in the bundled face."""
    for part, fam, mode in runs(o["s"], o["family"] or SANS):
        run = p.add_run()
        run.text = part
        f = run.font
        f.size = Emu(int(o["size"] * px))  # font em size: px in the 1920 design space → EMU
        f.bold = o["weight"] == "bold"
        f.color.rgb = RGBColor.from_string(o["c"].lstrip("#")[:6])
        f.name = fam
        rPr = run._r.get_or_add_rPr()
        if mode:
            rPr.set("baseline", "-25000" if mode == "sub" else "30000")
        rPr.append(rPr.makeelement(qn("a:ea"), {"typeface": fam}))


# ---------------- slide layouts ----------------
def chrome(cv, deck, s, page, total, anchor):
    kit_bg(cv)
    if s.get("layout") != "title":
        cv.text(90, 128, s["title"], 56, INK, family=SERIF)
        cv.rect(90, 152, 90, 4, fill=GOLD)
    cv.line(90, 1012, W - 90, 1012, "#1d3d43", 2)
    cv.text(90, 1050, f"{deck['display']} · {deck['title']}", 24, FAINT)
    cv.text(W - 90, 1050, f"p{page}/{total}", 26, MUTED, "bold", "right")
    if anchor:
        cv.text(W - 90, 84, f"影片 {anchor}", 24, FAINT, align="right")


def kit_bg(cv):
    cv.rect(0, 0, W, H, fill="#071c22")
    cv.rect(0, 0, W, 6, fill=TEAL, alpha=0.6)


def bullets(cv, items, x, y, w, size=36, gap=1.0):
    yy = y
    for it in items:
        if isinstance(it, dict):
            txt, col, sz = it.get("text", ""), {"gold": GOLD, "teal": TEAL, "red": RED, "muted": MUTED}.get(it.get("color"), INK), it.get("size", size)
        else:
            txt, col, sz = it, INK, size
        cv.circle(x + 8, yy - sz * 0.34, 6, fill=GOLD)
        h = cv.paragraph(x + 34, yy, txt, sz, w - 34, col, lh=1.45)
        yy += h + sz * 0.55 * gap
    return yy


def draw_slide(cv, deck, s, page, total, figs, anchor):
    chrome(cv, deck, s, page, total, anchor)
    lay = s.get("layout", "text")
    if lay == "title":
        cv.text(W / 2, 470, s["title"], 104, GOLD, align="center", family=SERIF)
        if s.get("subtitle"):
            cv.text(W / 2, 560, s["subtitle"], 34, MUTED, align="center")
        if s.get("byline"):
            cv.text(W / 2, 680, s["byline"], 28, FAINT, align="center")
    elif lay == "statement":
        y = 360
        for i, ln in enumerate(s["lines"]):
            big = i == 0
            y += cv.paragraph(160, y, ln, 60 if big else 38, W - 320, GOLD if big else INK, lh=1.45, family=SERIF if big else None) + 30
    else:
        has_fig = bool(s.get("figure"))
        bw = 760 if has_fig else W - 260
        y = 260
        if s.get("lead"):
            y += cv.paragraph(110, y, s["lead"], 40, bw, TEAL, lh=1.45) + 28
        if s.get("bullets"):
            y = bullets(cv, s["bullets"], 110, y, bw, s.get("size", 34))
        if s.get("note"):
            cv.paragraph(110, max(y + 10, 900 if has_fig else y + 10), s["note"], 26, bw, MUTED, lh=1.45)
        if has_fig:
            figs[s["figure"]](cv, s.get("args", {}))


def mmss(t):
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def main(module_id):
    spec_path = ROOT / "content" / "modules" / module_id / "slides.json"
    deck = json.loads(spec_path.read_text(encoding="utf-8"))
    figmod = ROOT / "video" / module_id / "figures.py"
    sp = importlib.util.spec_from_file_location("figs", figmod)
    fm = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(fm)
    figs = fm.FIGURES
    film = ROOT / "site" / "media" / module_id / "film.json"
    scenes = {}
    if film.exists():
        fj = json.loads(film.read_text())
        for f in (fj.get("films") or [fj]):
            for sc in f.get("scenes", []):
                scenes[sc["sceneId"]] = (f.get("title", ""), sc["start"], f.get("id"))
    out = ROOT / "site" / "slides" / module_id
    out.mkdir(parents=True, exist_ok=True)
    slides = deck["slides"]
    total = len(slides)
    ids = [s["id"] for s in slides]
    assert len(set(ids)) == len(ids), "slideId 必须唯一"
    recs = []
    for i, s in enumerate(slides, 1):
        anchor = None
        if s.get("scene") and s["scene"] in scenes:
            ftitle, start, fid = scenes[s["scene"]]
            anchor = (f"《{ftitle}》 " if len(fj.get("films", [])) > 1 else "") + mmss(start)
        rec = Recorder()
        draw_slide(rec, deck, s, i, total, figs, anchor)
        recs.append((s, rec, anchor))
    # PDF (960×540 pt) with selectable text
    pdf = out / f"{module_id}.pdf"
    cv = Canvas(960, 540, "pdf", str(pdf))
    for s, rec, _ in recs:
        replay_cairo(rec.ops, cv, 0.5)
        cv.next_page()
    cv.close()
    # PNG previews + thumbnails
    manifest = []
    for i, (s, rec, anchor) in enumerate(recs, 1):
        img = Canvas(1600, 900)
        replay_cairo(rec.ops, img, 1600 / W)
        p = out / f"p{i:02d}.png"
        img.png(p)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", "scale=1600:-1", "-q:v", "3", str(out / f"p{i:02d}.jpg")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", "scale=320:-1", "-q:v", "5", str(out / f"t{i:02d}.jpg")], check=True)
        p.unlink()
        manifest.append({"slideId": s["id"], "pageNumber": i, "pageCount": total, "title": s["title"], "image": f"p{i:02d}.jpg", "thumb": f"t{i:02d}.jpg",
                         "alt": s.get("alt") or s["title"] + "：" + "；".join(b if isinstance(b, str) else b.get("text", "") for b in s.get("bullets", []))[:300],
                         "transcript": s.get("transcript", ""), "videoAnchor": anchor, "sceneId": s.get("scene"), "objectiveIds": s.get("objectives", [])})
    # PPTX
    try:
        from pptx import Presentation
        from pptx.util import Emu
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
        from pptx.enum.dml import MSO_LINE
        from pptx.enum.text import PP_ALIGN
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(W * 6350), Emu(H * 6350)
        blank = prs.slide_layouts[6]
        for s, rec, _ in recs:
            sl = prs.slides.add_slide(blank)
            replay_pptx(rec.ops, sl, Emu, RGBColor, MSO_SHAPE, MSO_CONNECTOR, MSO_LINE, PP_ALIGN)
            sl.notes_slide.notes_text_frame.text = s.get("transcript", "")
        prs.core_properties.title = f"{deck['display']} {deck['title']}"
        prs.core_properties.author = "Learning Clustering（统一课程）"
        prs.save(out / f"{module_id}.pptx")
        pptx_name = f"{module_id}.pptx"
    except ImportError:
        print("python-pptx 不可用：跳过 PPTX（不会把 PNG 截图冒充可编辑课件）")
        pptx_name = None
    data = {"status": "ready", "moduleId": module_id, "slides": manifest, "pdf": pdf.name, "pptx": pptx_name, "contentVersion": deck.get("contentVersion"),
            "aspectNote": "16:9 是本课程的设计选择（与影片一致、适合投影），不是教师指定的比例。PDF 页码与网页 p/total 完全一致；PPTX 中文字、形状与表格均可编辑，讲稿在备注里。"}
    (out / "slides.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{module_id}: {total} slides → {pdf.name}, {pptx_name}, previews")


if __name__ == "__main__":
    for m in sys.argv[1:]:
        main(m)
