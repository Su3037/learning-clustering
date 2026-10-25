#!/usr/bin/env python3
"""Bring the author's original popular-science film into Module 05, as made.

  python3 video/m05-label-propagation/import_story.py /path/to/clustering-lab5-label-propagation

Copies site/media/circles.mp4 (v4, 6:20, We Never (Remix) played twice), its zh/en WebVTT and cover
from Su3037/clustering-lab5-label-propagation, and adds the film to site/media/m05-label-propagation/film.json
as the "original" film (the chapter's own popular film is rendered from films.py). The picture already carries Chinese captions with English underneath, so one MP4
serves both languages; the English page offers the English WebVTT track.

With --music it also extracts one play of the track (0–189.82 s, at the film's mix level) for
use as the score of the other modules' popular-science films. That file is third-party audio: it is
written outside the repository and must never be committed.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "film"))
from cinema import merge_manifest, TRACKS  # noqa: E402

MEDIA = ROOT / "site" / "media" / "m05-label-propagation"
CHAPTER_EN = {
    "序 · 通讯录": "PROLOGUE · CONTACTS", "一 · 一个极简的办法": "I · A VERY SIMPLE IDEA", "二 · 芯片里的同一个问题": "II · THE SAME PROBLEM IN A CHIP",
    "三 · 尺子与穷举": "III · THE RULER AND BRUTE FORCE", "四 · 一条局部规则": "IV · ONE LOCAL RULE", "第 1 层 · 标签": "LAYER 1 · LABELS",
    "第 2 层 · 怎样算最强": "LAYER 2 · WHAT \"STRONGEST\" MEANS", "第 3 层 · 一次更新": "LAYER 3 · ONE UPDATE", "第 4 层 · 一整轮": "LAYER 4 · A WHOLE ROUND",
    "第 5 层 · 何时停止": "LAYER 5 · WHEN TO STOP", "第 6 层 · 同时还是轮流": "LAYER 6 · ALL AT ONCE, OR IN TURN", "第 7 层 · 分得好不好": "LAYER 7 · IS THE SPLIT GOOD?",
    "第 8 层 · 回到芯片": "LAYER 8 · BACK TO THE CHIP", "第 9 层 · 它做不到的事": "LAYER 9 · WHAT IT CANNOT DO", "现实中的用法": "IN PRACTICE",
}


def parse_vtt(path):
    out = []
    for block in path.read_text(encoding="utf-8").split("\n\n"):
        m = re.search(r"(\d+):(\d+):(\d+\.\d+) --> (\d+):(\d+):(\d+\.\d+)\n(.+)", block, re.S)
        if m:
            h1, m1, s1, h2, m2, s2, text = m.groups()
            out.append({"start": round(int(h1) * 3600 + int(m1) * 60 + float(s1), 3), "end": round(int(h2) * 3600 + int(m2) * 60 + float(s2), 3), "text": text.strip()})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="checkout of Su3037/clustering-lab5-label-propagation")
    ap.add_argument("--music", default=None, help="also extract one play of the track to this .m4a path (outside the repo)")
    a = ap.parse_args()
    src = Path(a.source)
    commit = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    MEDIA.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src / "site/media/circles.mp4", MEDIA / "original.mp4")
    for lg in ("zh", "en"):
        shutil.copyfile(src / f"site/media/circles.{lg}.vtt", MEDIA / f"original.{lg}.vtt")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src / "site/media/circles-cover.jpg"), "-vf", "scale=1280:-1", "-q:v", "4", str(MEDIA / "original.jpg")], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(MEDIA / "original.mp4")], capture_output=True, text=True).stdout)
    chapters = json.loads((src / "video/chapters-v4.json").read_text(encoding="utf-8"))
    board = json.loads((src / "video/storyboard-v4.json").read_text(encoding="utf-8"))
    versions = {}
    for lg in ("zh", "en"):
        versions[lg] = {"src": "original.mp4", "vtt": f"original.{lg}.vtt", "poster": "original.jpg", "duration": round(dur, 2), "captions": "zh+en",
                        "chapters": [{"t": c["start"], "title": c["title"] if lg == "zh" else CHAPTER_EN[c["title"]], "sceneId": c["id"]} for c in chapters],
                        "transcript": parse_vtt(MEDIA / f"original.{lg}.vtt"), "bytes": (MEDIA / "original.mp4").stat().st_size}
    merge_manifest("m05-label-propagation", [{
        "id": "original", "kind": "original", "status": "ready", "external": True,
        "title": {"zh": "圈子从哪里来", "en": "Where Do Clusters Come From?"},
        "why": {"zh": "作者原作的科普片（第四版），原样收录：从通讯录到芯片，再逐层拆开九层规则。",
                "en": "The author's original popular-science film (version 4), included as made: from a contact list to a chip, then the rule taken apart in nine layers."},
        "music": TRACKS["wenever"]["credit"],
        "source": {"repository": "https://github.com/Su3037/clustering-lab5-label-propagation", "commit": commit, "file": "site/media/circles.mp4"},
        "scenes": [{"sceneId": s["id"], "start": s["start"], "end": s["end"]} for s in board["scenes"]],
        "fps": 30, "size": [1920, 1080], "versions": versions}], ["story", "concise", "advanced", "lab", "original"])
    print("story →", MEDIA / "original.mp4", f"{dur:.1f}s")
    if a.music:
        # The film mixes the track at gain 0.45 from 0 s and again from 189.82 s; take the first play at the film's own level (peak −4 dBFS).
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src / "site/media/circles.mp4"), "-vn", "-t", "189.82",
                        "-c:a", "aac", "-b:a", "192k", a.music], check=True)
        print("music →", a.music)


if __name__ == "__main__":
    main()
