#!/usr/bin/env python3
"""Compose an experiment-walkthrough film from a screen recording made by scripts/film/recorder.mjs.

  node video/<id>/walkthrough.mjs <site base url> zh build/<id>/walk-zh
  python3 scripts/film/walkthrough.py <id> [--lang zh] [--stills]

The real page sits in a window on the film's dark backdrop, a drawn cursor glides to each control and
pulses on click, the view eases in on the part being explained, and captions follow the cine kit
(zh: Chinese with English underneath; en: English). Writes lab.<lang>.mp4/.vtt/.jpg and merges the
"lab" film into site/media/<id>/film.json.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import cairo
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cine  # noqa: E402
from cine import W, H, FPS, L, clamp, ease, lerp, IVORY, GOLD, MUTED, FAINT  # noqa: E402
import music  # noqa: E402
from cinema import vtt, merge_manifest, SCORE_CREDIT  # noqa: E402

WIN = (288, 112, 1344, 756)          # window on screen: x, y, w, h (16:9)
SRC = (1920, 1080)
MAX_ZOOM = 1.7
TITLE = 3.2
OUTRO = 2.6


def surface(path):
    img = Image.open(path).convert("RGB").resize(SRC) if Image.open(path).size != SRC else Image.open(path).convert("RGB")
    a = np.asarray(img)
    bgra = np.empty((a.shape[0], a.shape[1], 4), np.uint8)
    bgra[:, :, 0], bgra[:, :, 1], bgra[:, :, 2], bgra[:, :, 3] = a[:, :, 2], a[:, :, 1], a[:, :, 0], 255
    return cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, a.shape[1], a.shape[0]), bgra


def crop_for(zoom):
    """16:9 crop rectangle in screenshot pixels around a zoom box (or the full frame)."""
    if not zoom:
        return (0.0, 0.0, float(SRC[0]), float(SRC[1]))
    cx, cy = zoom["x"] + zoom["w"] / 2, zoom["y"] + zoom["h"] / 2
    w = max(zoom["w"], zoom["h"] * 16 / 9, SRC[0] / MAX_ZOOM)
    w = min(w, SRC[0])
    h = w * 9 / 16
    x = clamp(cx - w / 2, 0, SRC[0] - w)
    y = clamp(cy - h / 2, 0, SRC[1] - h)
    return (x, y, w, h)


class Walk:
    def __init__(self, module, lang, rec_dir, title, brand):
        self.module, self.lang, self.dir = module, lang, Path(rec_dir)
        self.tl = json.loads((self.dir / "timeline.json").read_text())
        self.title, self.brand = title, brand
        self.kicker = None
        self.rows, t = [], TITLE
        for s in self.tl["shots"]:
            cap = s["caption"][lang] if s["caption"] else ""
            dur = max(s["duration"] + s.get("hold", 0), cine.min_read(cap, lang) + 0.4)
            self.rows.append((t, dur, s))
            t += dur
        self.total = t + OUTRO
        self.cache = {}

    def frame_file(self, i, tau):
        t0, dur, s = self.rows[i]
        best = None
        for f in s["frames"]:
            if f["t"] <= tau + 1e-6:
                best = f["file"]
            else:
                break
        if best is None:
            if s["frames"]:
                best = s["frames"][0]["file"]
            elif i > 0:
                return self.frame_file(i - 1, 1e9)
        return best

    def surf(self, name):
        if name not in self.cache:
            if len(self.cache) > 6:
                self.cache.pop(next(iter(self.cache)))
            self.cache[name] = surface(self.dir / "frames" / name)  # (surface, backing array)
        return self.cache[name][0]

    def cursor_at(self, s, tau, prev_xy):
        x, y = prev_xy
        click = None
        for ev in s["cursor"]:
            if ev["t"] > tau:
                break
            if ev["kind"] == "move":
                k = ease((tau - ev["t"]) / ev.get("glide", 0.55))
                x, y = lerp(x, ev["x"], k), lerp(y, ev["y"], k)
                if k >= 1:
                    x, y = ev["x"], ev["y"]
            elif ev["kind"] in ("at", "click"):
                if ev["kind"] == "at" and ev["t"] == 0:
                    x, y = ev["x"], ev["y"]
                if ev["kind"] == "click":
                    click = tau - ev["t"]
        return (x, y), click

    def end_cursor(self, s, start_xy):
        xy = start_xy
        for ev in s["cursor"]:
            if ev["kind"] in ("move", "at", "click"):
                xy = (ev["x"], ev["y"])
        return xy

    def render(self, fr, T):
        fr.clear()
        cine.backdrop(fr)
        if T < TITLE:
            a = clamp(T / 0.8) * clamp((TITLE - T) / 0.5)
            cine.title_card(fr, self.title[0], self.title[1], a, kicker=self.kicker)
            return self.finish(fr, T, None)
        i = max(j for j, (t0, _, _) in enumerate(self.rows) if t0 <= T) if T < self.total - OUTRO else len(self.rows) - 1
        t0, dur, s = self.rows[i]
        tau = min(T - t0, dur)
        # camera: ease from the previous shot's crop into this one's
        prev = crop_for(self.rows[i - 1][2]["zoom"]) if i > 0 else crop_for(None)
        cur = crop_for(s["zoom"])
        k = ease(tau / 0.9)
        crop = tuple(lerp(a, b, k) for a, b in zip(prev, cur))
        x, y, w, h = WIN
        # window chrome
        fr.rect(x - 2, y - 30, w + 4, h + 32, fill="#0d1f26", stroke=FAINT, width=1.2, r=10, screen=True)
        for j, col in enumerate(("#d99a9a", "#ddbd78", "#76cbb5")):
            fr.dot((x + 18 + j * 20, y - 15), 5, col, 0.8, screen=True)
        fr.text(self.tl.get("url", "").split("//")[-1].replace("127.0.0.1:8800/", "su3037.github.io/"), x + w / 2, y - 9, 14, MUTED, 0.8, anchor="c")
        name = self.frame_file(i, tau)
        if name:
            src = self.surf(name)
            ctx = fr.c
            ctx.save()
            ctx.rectangle(x, y, w, h); ctx.clip()
            sx, sy = w / crop[2], h / crop[3]
            ctx.translate(x, y); ctx.scale(sx, sy); ctx.translate(-crop[0], -crop[1])
            ctx.set_source_surface(src, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint()
            ctx.restore()
        # cursor (screenshot pixels → screen)
        start = (SRC[0] * 0.62, SRC[1] * 0.55)
        for j in range(i):
            start = self.end_cursor(self.rows[j][2], start)
        (cx, cy), click = self.cursor_at(s, tau, start)
        px = x + (cx - crop[0]) * w / crop[2]
        py = y + (cy - crop[1]) * h / crop[3]
        if x <= px <= x + w and y <= py <= y + h:
            if click is not None and click < 0.6:
                fr.ring((px, py), 10 + 40 * click, GOLD, 3, 1 - click / 0.6, glow=0.6, screen=True)
            pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
            pts = [(px + u, py + v) for u, v in pts]
            fr.polyline(pts, "#0b2029", 2.2, 1.0, screen=True, close=True, fill="#f4f1e6", fill_alpha=1.0)
        chapter = None
        for j in range(i, -1, -1):
            if self.rows[j][2].get("chapter"):
                chapter = self.rows[j][2]["chapter"]
                break
        return self.finish(fr, T, s, chapter, tau, dur)

    def finish(self, fr, T, s, chapter=None, tau=0, dur=1):
        if chapter:
            cine.furniture(fr, self.brand, (chapter["zh"], chapter["en"]))
        elif s is None:
            cine.furniture(fr, self.brand, None)
        text = (s["caption"]["zh"], s["caption"]["en"]) if s and s["caption"] else None
        a = clamp(tau / 0.25) * clamp((dur - tau) / 0.25) if s else 0
        if T >= self.total - OUTRO:
            a = 0
        cine.caption(fr, text, a)
        if T >= self.total - OUTRO:
            k = clamp((T - (self.total - OUTRO)) / 0.6)
            fr.rect(0, 0, W, H, fill=cine.BG, alpha=0.75 * k, screen=True)
            fr.text(L("下面轮到你：打开实验和在线编程，亲手试一遍。", "Your turn: open the lab and the code lab and try it yourself."), W / 2, H / 2, 40, GOLD, k, anchor="c", role="serif")
        img = fr.finish()
        g = clamp(T / 0.6) * clamp((self.total - T) / 1.0)
        if g < 1:
            img = (img.astype(np.float32) * g).astype(np.uint8)
        return img

    def captions(self):
        return [{"start": round(t0, 3), "end": round(t0 + d, 3), "text": s["caption"][self.lang], "sceneId": f"shot-{s['index']:02d}"}
                for t0, d, s in self.rows if s["caption"] and s["caption"][self.lang]]

    def chapters(self):
        out = [{"t": 0.0, "title": "开始" if self.lang == "zh" else "START", "sceneId": "title"}]
        for t0, d, s in self.rows:
            if s.get("chapter"):
                out.append({"t": round(t0, 2), "title": s["chapter"][self.lang], "sceneId": f"shot-{s['index']:02d}"})
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--lang", choices=["zh", "en"], action="append")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--crf", type=int, default=23)
    a = ap.parse_args()
    meta = json.loads((ROOT / "video" / a.module / "walkthrough.json").read_text(encoding="utf-8"))
    media = ROOT / "site" / "media" / a.module
    build = ROOT / "build" / a.module
    versions, scenes = {}, None
    for lg in a.lang or ["zh", "en"]:
        cine.set_lang(lg)
        wk = Walk(a.module, lg, build / f"walk-{lg}", (tuple(meta["title"].values()), tuple(meta["subtitle"].values())),
                  tuple(meta["brand"].values()))
        wk.kicker = tuple(meta["kicker"].values())
        print(f"lab.{lg}: {len(wk.rows)} shots, {wk.total:.1f} s")
        fr = cine.Frame()
        if a.stills:
            times = [t0 + d * 0.8 for t0, d, _ in wk.rows]
            for f in build.glob(f"lab.{lg}-still-*.png"):
                f.unlink()
            for i, T in enumerate([1.5] + times):
                Image.fromarray(wk.render(fr, T)).save(build / f"lab.{lg}-still-{i:02d}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(build / f"lab.{lg}-still-*.png"),
                            "-vf", f"scale=640:-1,tile=4x{(len(times) + 4) // 4}:padding=6:color=0x222222", "-frames:v", "1", str(build / f"lab.{lg}-contact.jpg")], check=True)
            print("stills →", build / f"lab.{lg}-contact.jpg")
            continue
        wav = build / f"lab.{lg}-score.wav"
        music.write_wav(wav, music.score(wk.total + 1.0, [t0 for t0, _, s in wk.rows if s.get("chapter")], "steady", 41))
        mp4 = media / f"lab.{lg}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-g", str(FPS * 4), "-movflags", "+faststart",
               "-c:a", "aac", "-b:a", "128k", "-shortest", str(mp4)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        start = time.time()
        n = round(wk.total * FPS)
        for k in range(n):
            p.stdin.write(wk.render(fr, k / FPS).tobytes())
            if k % (FPS * 30) == 0:
                print(f"  lab.{lg} frame {k}/{n}  {time.time() - start:.0f}s", flush=True)
        p.stdin.close()
        if p.wait():
            raise SystemExit("ffmpeg failed")
        caps = wk.captions()
        (media / f"lab.{lg}.vtt").write_text(vtt(caps), encoding="utf-8")
        poster_t = wk.rows[min(len(wk.rows) - 1, meta.get("posterShot", 2))][0] + 1.5
        Image.fromarray(wk.render(fr, poster_t)).save(build / f"lab.{lg}-poster.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(build / f"lab.{lg}-poster.png"), "-vf", "scale=1280:-1", "-q:v", "4", str(media / f"lab.{lg}.jpg")], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout)
        versions[lg] = {"src": mp4.name, "vtt": f"lab.{lg}.vtt", "poster": f"lab.{lg}.jpg", "duration": round(dur, 2), "captions": "zh+en" if lg == "zh" else "en",
                        "chapters": wk.chapters(), "transcript": caps, "readingViolations": 0, "bytes": mp4.stat().st_size}
        print("film →", mp4, f"{dur:.1f}s {mp4.stat().st_size / 1e6:.1f} MB")
    if versions:
        merge_manifest(a.module, [{"id": "lab", "kind": "lab", "status": "ready", "title": meta["title"], "why": meta.get("why"), "music": SCORE_CREDIT,
                                   "recorded": "scripts/film/recorder.mjs + video/%s/walkthrough.mjs" % a.module, "fps": FPS, "size": [W, H], "versions": versions}],
                       meta.get("order", ["story", "concise", "advanced", "lab"]))


if __name__ == "__main__":
    main()
