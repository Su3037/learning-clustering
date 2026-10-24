#!/usr/bin/env python3
"""Render the films in video/<moduleId>/films.py (cinematic kit, one MP4 per language).

  python3 scripts/film/cinema.py m05-label-propagation --film concise --stills          # contact sheet per language
  python3 scripts/film/cinema.py m05-label-propagation --film concise --lang en --sample 20 40
  python3 scripts/film/cinema.py m05-label-propagation --film concise                   # zh + en → site/media/<id>/

Writes <film>.<lang>.mp4, <film>.<lang>.vtt and <film>.<lang>.jpg, then merges the film into
site/media/<id>/film.json (schema 2: one entry per film with a version per language).

Music: "score:<mood>" is the course's original NumPy score (scripts/film/music.py). "track:<name>"
mixes a third-party recording the author chose (e.g. We Never (Remix) for the popular-science films);
the audio file is never committed: point LC_MUSIC_<NAME> at it, or keep it at
/mnt/project-files/private-music/<name>.m4a.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cine  # noqa: E402
import music  # noqa: E402

TRACKS = {
    "wenever": {
        "title": "We Never (Remix)（若如初见）", "artists": "Hi Noise / 秋成",
        "source": "https://www.bilibili.com/video/BV134Ho6qENu/",
        "credit": {"zh": "《We Never (Remix)（若如初见）》Hi Noise / 秋成（第三方录音，不在本课程许可范围内）",
                   "en": "“We Never (Remix)” by Hi Noise / 秋成 (third-party recording, not covered by this course's licences)"},
    }
}
SCORE_CREDIT = {"zh": "本课程原创程序合成配乐（NumPy），CC BY 4.0", "en": "Original score synthesised for this course (NumPy), CC BY 4.0"}


def load(module_id):
    path = ROOT / "video" / module_id / "films.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"films_{module_id.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def track_path(name):
    env = os.environ.get(f"LC_MUSIC_{name.upper()}")
    for p in [env, f"/mnt/project-files/private-music/{name}.m4a", str(ROOT / "build" / "private" / f"{name}.m4a")]:
        if p and Path(p).exists():
            return Path(p)
    raise SystemExit(f"music track '{name}' not found: set LC_MUSIC_{name.upper()}")


def audio_for(film, build):
    wav = build / f"{film.ID}-audio.wav"
    kind, _, name = film.MUSIC.partition(":")
    if kind == "track":
        src = track_path(name)
        fade = 3.0
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{film.total + 0.5:.3f}",
                        "-af", f"afade=t=in:d=0.6,afade=t=out:st={max(0, film.total - fade):.3f}:d={fade},volume=0.9",
                        "-ar", "48000", "-ac", "2", str(wav)], check=True)
        return wav, TRACKS[name]["credit"]
    cues = [t0 for t0, _ in film.rows]
    music.write_wav(wav, music.score(film.total + 1.0, cues, name or "calm", film.SEED))
    return wav, SCORE_CREDIT


def encode(film, t0, t1, out, audio=None, crf=21):
    fr = cine.Frame()
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{cine.W}x{cine.H}", "-r", str(cine.FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", f"{t0:.3f}", "-i", str(audio)]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-tune", "animation", "-pix_fmt", "yuv420p", "-g", str(cine.FPS * 4), "-movflags", "+faststart"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += [str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    n0, n1 = round(t0 * cine.FPS), round(t1 * cine.FPS)
    for n in range(n0, n1):
        p.stdin.write(film.render(fr, n / cine.FPS).tobytes())
        if (n - n0) % (cine.FPS * 30) == 0:
            print(f"  {film.ID}.{cine.LANG} frame {n - n0}/{n1 - n0}  {time.time() - start:.0f}s", flush=True)
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg failed")


def vtt(caps):
    def ts(x):
        h, r = divmod(x, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
    return "WEBVTT\n\n" + "\n".join(f"{i + 1}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for i, c in enumerate(caps))


def still(film, T, path):
    from PIL import Image
    Image.fromarray(film.render(cine.Frame(), T)).save(path)


def merge_manifest(module_id, entries, order):
    path = ROOT / "site" / "media" / module_id / "film.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    films = {f["id"]: f for f in old.get("films", []) if old.get("schema") == 2}
    for e in entries:
        prev = films.get(e["id"], {})
        e["versions"] = {**prev.get("versions", {}), **e["versions"]}
        films[e["id"]] = {**prev, **e}
    ordered = [films[i] for i in order if i in films] + [f for i, f in films.items() if i not in order]
    path.write_text(json.dumps({"schema": 2, "status": "ready", "films": ordered}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("manifest →", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--film", action="append", help="film id (repeatable); default: all")
    ap.add_argument("--lang", choices=["zh", "en"], action="append")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--at", nargs="*", type=float, help="still times in seconds (default: one per scene)")
    ap.add_argument("--sample", nargs=2, type=float)
    ap.add_argument("--crf", type=int, default=21)
    a = ap.parse_args()
    mod = load(a.module)
    films = [f for f in mod.FILMS if not a.film or f.ID in a.film]
    build = ROOT / "build" / a.module
    build.mkdir(parents=True, exist_ok=True)
    media = ROOT / "site" / "media" / a.module
    media.mkdir(parents=True, exist_ok=True)
    entries = []
    for film in films:
        if getattr(film, "EXTERNAL", False):
            continue
        langs = a.lang or list(film.LANGS)
        bad = {lg: [c for c in film.captions(lg) if c["end"] - c["start"] + 0.005 < cine.min_read(c["text"], lg)] for lg in langs}
        print(f"{film.ID}: {len(film.SCENES)} scenes, {film.total:.1f} s; reading-time violations: { {k: len(v) for k, v in bad.items()} }")
        if a.stills:
            for lg in langs:
                cine.set_lang(lg)
                times = a.at or [t0 + sc.dur * 0.72 for t0, sc in film.rows]
                for f in build.glob(f"{film.ID}.{lg}-still-*.png"):
                    f.unlink()
                for i, T in enumerate(times):
                    still(film, T, build / f"{film.ID}.{lg}-still-{i:02d}.png")
                cols = 4
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(build / f"{film.ID}.{lg}-still-*.png"),
                                "-vf", f"scale=640:-1,tile={cols}x{(len(times) + cols - 1) // cols}:padding=6:color=0x222222", "-frames:v", "1",
                                str(build / f"{film.ID}.{lg}-contact.jpg")], check=True)
                print("stills →", build / f"{film.ID}.{lg}-contact.jpg")
            continue
        audio, credit = audio_for(film, build)
        if a.sample:
            for lg in langs:
                cine.set_lang(lg)
                out = ROOT / "build" / "samples" / f"{film.ID}.{lg}-{a.sample[0]:.0f}-{a.sample[1]:.0f}.mp4"
                out.parent.mkdir(parents=True, exist_ok=True)
                encode(film, a.sample[0], a.sample[1], out, audio, a.crf)
                print("sample →", out)
            continue
        versions = {}
        for lg in langs:
            cine.set_lang(lg)
            mp4 = media / f"{film.ID}.{lg}.mp4"
            encode(film, 0, film.total, mp4, audio, a.crf)
            caps = film.captions(lg)
            (media / f"{film.ID}.{lg}.vtt").write_text(vtt(caps), encoding="utf-8")
            png = build / f"{film.ID}.{lg}-poster.png"
            still(film, film.POSTER_AT if film.POSTER_AT is not None else film.total * 0.4, png)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "scale=1280:-1", "-q:v", "4", str(media / f"{film.ID}.{lg}.jpg")], check=True)
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout)
            versions[lg] = {"src": mp4.name, "vtt": f"{film.ID}.{lg}.vtt", "poster": f"{film.ID}.{lg}.jpg", "duration": round(dur, 2),
                            "captions": "zh+en" if lg == "zh" else "en", "chapters": film.chapters(lg), "transcript": caps, "readingViolations": len(bad[lg]),
                            "bytes": mp4.stat().st_size}
            print("film →", mp4, f"{dur:.1f}s {mp4.stat().st_size / 1e6:.1f} MB")
        entries.append({"id": film.ID, "kind": film.KIND, "status": "ready", "title": dict(zip(("zh", "en"), cine.both(film.TITLE))),
                        "why": dict(zip(("zh", "en"), cine.both(film.WHY))) if film.WHY else None, "music": credit,
                        "scenes": [{"sceneId": sc.id, "start": round(t0, 2), "end": round(t0 + sc.dur, 2)} for t0, sc in film.rows],
                        "fps": cine.FPS, "size": [cine.W, cine.H], "versions": versions})
    if entries:
        merge_manifest(a.module, entries, getattr(mod, "ORDER", [f.ID for f in mod.FILMS]))


if __name__ == "__main__":
    main()
