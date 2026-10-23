#!/usr/bin/env python3
"""Render a course film from video/<moduleId>/film.py.

  python3 scripts/film/render.py m07-kernighan-lin --stills          # one still per scene + contact sheet
  python3 scripts/film/render.py m07-kernighan-lin --sample 12 52     # a time range → build/samples/
  python3 scripts/film/render.py m07-kernighan-lin                     # full film → site/media/<id>/

Each scene is a list of beats (caption, minimum hold). A beat lasts at least the caption's reading
time (min_read: ~4.5 characters/second + 0.8 s). Captions are burned into the caption band and
also written as WebVTT; chapters and the transcript come from the same timeline, so their times
are the real times in the MP4.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import kit  # noqa: E402
from kit import Frame, W, H, FPS, header, caption, min_read, clamp  # noqa: E402
import music  # noqa: E402

FADE = 0.45


class Beat:
    def __init__(self, text="", hold=0.0, sub=None):
        self.text, self.sub = text, sub
        self.dur = max(hold, min_read(text) if text else 0.0, 0.6)


class Scene:
    def __init__(self, sid, draw, beats, chapter=None, title=None, tail=0.4):
        self.id, self.draw, self.chapter, self.title = sid, draw, chapter, title
        self.beats = [b if isinstance(b, Beat) else Beat(*b) if isinstance(b, tuple) else Beat(b) for b in beats]
        self.starts = []
        acc = 0.0
        for b in self.beats:
            self.starts.append(acc)
            acc += b.dur
        self.dur = acc + tail


class Clock:
    """What a scene's draw() receives: local time and beat helpers."""

    def __init__(self, scene, t):
        self.scene, self.t = scene, t
        self.k = max(i for i, s in enumerate(scene.starts) if s <= t + 1e-9) if scene.starts else 0

    def at(self, k):
        return self.scene.starts[min(k, len(self.scene.starts) - 1)] if k < len(self.scene.starts) else self.scene.dur

    def since(self, k):
        return self.t - self.at(k)

    def p(self, k, d=0.8, delay=0.0):
        """Eased 0→1 transition that starts `delay` seconds after beat k begins."""
        return kit.ease((self.t - self.at(k) - delay) / d) if d > 0 else float(self.t >= self.at(k) + delay)

    def on(self, k):
        return self.t >= self.at(k)


def load_film(module_id):
    path = ROOT / "video" / module_id / "film.py"
    spec = importlib.util.spec_from_file_location(f"film_{module_id.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def timeline(film):
    t, rows = 0.0, []
    for sc in film.SCENES:
        rows.append((t, sc))
        t += sc.dur
    return rows, t


def frame_at(fr, film, rows, T):
    for i, (t0, sc) in enumerate(rows):
        if T < t0 + sc.dur or i == len(rows) - 1:
            break
    lt = T - t0
    fr.backdrop(T)
    cv = fr.cv
    clock = Clock(sc, lt)
    fade = clamp(lt / FADE) * clamp((sc.dur - lt) / FADE) if getattr(film, "FADE_SCENES", True) else 1.0
    cv.group()
    sc.draw(cv, clock)
    cv.end_group(fade)
    header(cv, film.MODULE, sc.chapter_title if hasattr(sc, "chapter_title") else current_chapter(rows, i))
    b = sc.beats[clock.k] if sc.beats else None
    if b and b.text:
        k, bt = clock.k, lt - sc.starts[clock.k]
        prev_same = k > 0 and sc.beats[k - 1].text == b.text
        next_same = k + 1 < len(sc.beats) and sc.beats[k + 1].text == b.text
        a = (1.0 if prev_same else clamp(bt / 0.25)) * (1.0 if next_same else clamp((b.dur - bt) / 0.25))
        caption(cv, b.text, a * fade, b.sub)
    return cv


def current_chapter(rows, i):
    for j in range(i, -1, -1):
        if rows[j][1].chapter:
            return rows[j][1].chapter
    return ""


def captions(rows):
    out = []
    for t0, sc in rows:
        for b, s in zip(sc.beats, sc.starts):
            if not b.text:
                continue
            start, end = t0 + s, t0 + s + b.dur
            if out and out[-1]["text"] == b.text and abs(out[-1]["end"] - start) < 1e-6:
                out[-1]["end"] = end
            else:
                out.append({"start": round(start, 3), "end": round(end, 3), "text": b.text, "sceneId": sc.id})
    return out


def vtt(caps):
    def ts(x):
        h, r = divmod(x, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
    return "WEBVTT\n\n" + "\n".join(f"{i + 1}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for i, c in enumerate(caps))


def check_reading(caps):
    bad = [c for c in caps if c["end"] - c["start"] + 0.005 < min_read(c["text"])]
    return bad


def render_range(film, rows, t0, t1, out_mp4, audio=None):
    fr = Frame()
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", f"{t0:.3f}", "-i", str(audio)]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-g", str(FPS * 2), "-movflags", "+faststart"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += [str(out_mp4)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    for n in range(n0, n1):
        frame_at(fr, film, rows, n / FPS)
        p.stdin.write(fr.cv.bgra())
        if (n - n0) % (FPS * 20) == 0:
            print(f"  frame {n - n0}/{n1 - n0}  {time.time() - start:.0f}s", flush=True)
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--sample", nargs=2, type=float)
    ap.add_argument("--film", default=None, help="film id when a module has several films")
    ap.add_argument("--at", nargs="*", type=float, help="extra still times (seconds)")
    a = ap.parse_args()
    mod = load_film(a.module)
    films = mod.FILMS if hasattr(mod, "FILMS") else [mod]
    if a.film:
        films = [f for f in films if f.ID == a.film]
    build = ROOT / "build" / a.module
    build.mkdir(parents=True, exist_ok=True)
    manifest = []
    for film in films:
        rows, total = timeline(film)
        caps = captions(rows)
        bad = check_reading(caps)
        print(f"{film.ID}: {len(film.SCENES)} scenes, {total:.1f} s, {len(caps)} captions; reading-time violations: {len(bad)}")
        if a.stills:
            fr = Frame()
            times = [t0 + sc.dur * 0.72 for t0, sc in rows] + (a.at or [])
            sheet = []
            for i, T in enumerate(times):
                frame_at(fr, film, rows, T)
                p = build / f"{film.ID}-still-{i:02d}.png"
                fr.cv.png(p)
                sheet.append(p)
            cols = 4
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(build / f"{film.ID}-still-*.png"),
                            "-vf", f"scale=480:-1,tile={cols}x{(len(sheet) + cols - 1) // cols}:padding=6:color=0x222222", "-frames:v", "1", str(build / f"{film.ID}-contact.jpg")], check=True)
            print("stills →", build / f"{film.ID}-contact.jpg")
            continue
        cues = [t0 for t0, _ in rows]
        wav = build / f"{film.ID}-score.wav"
        music.write_wav(wav, music.score(total + 1.0, cues, getattr(film, "MOOD", "calm"), getattr(film, "SEED", 7)))
        if a.sample:
            out = ROOT / "build" / "samples" / f"{film.ID}-{a.sample[0]:.0f}-{a.sample[1]:.0f}.mp4"
            out.parent.mkdir(parents=True, exist_ok=True)
            render_range(film, rows, a.sample[0], a.sample[1], out, wav)
            print("sample →", out)
            continue
        media = ROOT / "site" / "media" / a.module
        media.mkdir(parents=True, exist_ok=True)
        mp4 = media / f"{film.ID}.mp4"
        render_range(film, rows, 0, total, mp4, wav)
        (media / f"{film.ID}.zh.vtt").write_text(vtt(caps), encoding="utf-8")
        # poster from a representative moment
        fr = Frame()
        frame_at(fr, film, rows, getattr(film, "POSTER_AT", total * 0.4))
        png = build / f"{film.ID}-poster.png"
        fr.cv.png(png)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "scale=1280:-1", "-q:v", "4", str(media / f"{film.ID}-poster.jpg")], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout)
        chapters, seen = [], set()
        for t0, sc in rows:
            if sc.chapter and sc.chapter not in seen:
                seen.add(sc.chapter)
                chapters.append({"t": round(t0, 2), "title": sc.chapter, "sceneId": sc.id})
        scenes = [{"sceneId": sc.id, "start": round(t0, 2), "end": round(t0 + sc.dur, 2)} for t0, sc in rows]
        manifest.append({"id": film.ID, "title": film.TITLE, "status": "ready", "src": mp4.name, "vtt": f"{film.ID}.zh.vtt", "poster": f"{film.ID}-poster.jpg",
                         "duration": round(dur, 2), "chapters": chapters, "scenes": scenes, "transcript": caps,
                         "music": "本课程原创程序合成配乐（NumPy），CC BY 4.0", "why": getattr(film, "WHY", ""),
                         "readingViolations": len(bad), "fps": FPS, "size": [W, H]})
        print("film →", mp4, f"{dur:.1f}s")
    if manifest:
        media = ROOT / "site" / "media" / a.module
        path = media / "film.json"
        old = json.loads(path.read_text()) if path.exists() else {}
        existing = {f["id"]: f for f in (old.get("films") or ([old] if old.get("status") == "ready" else []))}
        for f in manifest:
            existing[f["id"]] = f
        order = [f.ID for f in (mod.FILMS if hasattr(mod, "FILMS") else [mod])]
        allf = [existing[i] for i in order if i in existing]
        data = allf[0] if len(allf) == 1 else {"status": "ready", "films": allf}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("manifest →", path)


if __name__ == "__main__":
    main()
