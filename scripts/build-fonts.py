"""Subset the bundled OFL fonts (fonts/*) to the characters the site uses.

Faces (all SIL OFL 1.1, none with a Reserved Font Name, so subsets may keep their names):
  Noto Sans SC 400/700   body text on Chinese pages, and Chinese inside English pages
  Noto Sans 400/600/italic  body text on English pages (proportional Latin quotes and dashes)
  Noto Serif SC 400/600  Chinese display type (headings, leads, quotes)
  Newsreader 400/500/italic  Latin display type and display numerals
  JetBrains Mono 400/500 eyebrows, code, data

Writes site/assets/fonts/<face>-<weight>.woff2, one OFL-<face>.txt each, and coverage.json (the characters
kept, plus the ones no face has, which the browser draws with a system fallback). Needs fontTools + brotli;
without them the committed files are kept and the script says so. Run after build-site.mjs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets" / "fonts"
FACES = {
    "noto-sans-sc": {"dir": "noto-sans-sc", "cjk": True, "files": {"400": "NotoSansSC-Regular.otf", "700": "NotoSansSC-Bold.otf"}},
    "noto-serif-sc": {"dir": "noto-serif-sc", "cjk": True, "files": {"400": "NotoSerifSC-Regular.ttf", "600": "NotoSerifSC-SemiBold.ttf"}},
    "newsreader": {"dir": "newsreader", "cjk": False, "files": {"400": "Newsreader-Regular.ttf", "500": "Newsreader-Medium.ttf", "400i": "Newsreader-Italic.ttf"}},
    "noto-sans": {"dir": "noto-sans", "cjk": False, "files": {"400": "NotoSans-Regular.ttf", "600": "NotoSans-SemiBold.ttf", "400i": "NotoSans-Italic.ttf"}},
    "jetbrains-mono": {"dir": "jetbrains-mono", "cjk": False, "files": {"400": "JetBrainsMono-Regular.ttf", "500": "JetBrainsMono-Medium.ttf"}},
}

try:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    import brotli  # noqa: F401  (woff2 needs it)
except ImportError:
    print("fontTools/brotli 不可用：保留已提交的字体子集（site/assets/fonts/）")
    sys.exit(0)

chars = {chr(c) for c in range(0x20, 0x7F)} | {chr(c) for c in range(0xA0, 0x180)} | set("，。、；：！？（）《》「」『』“”‘’—…·–−×÷≤≥≈≠→←↔↑↓λΣδΔ∈∞⇥⌈⌉§¶†‡•′″")
for p in list((ROOT / "site").rglob("*")) + list((ROOT / "content").rglob("*")):
    if p.is_file() and p.suffix in {".html", ".js", ".json", ".md", ".css", ".vtt"} and "fonts" not in p.parts:
        chars |= set(p.read_text(encoding="utf8"))
chars = {c for c in chars if c.isprintable() and c != "\n"}

OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*.woff*"):
    old.unlink()
covered = set()
report = {}
for face, spec in FACES.items():
    src = ROOT / "fonts" / spec["dir"]
    first = next(iter(spec["files"].values()))
    cmap = TTFont(src / first).getBestCmap()
    want = chars if spec["cjk"] else {c for c in chars if ord(c) < 0x2E80}
    kept = sorted(c for c in want if ord(c) in cmap)
    covered |= set(kept)
    for weight, name in spec["files"].items():
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]          # keep the copyright and OFL notices in the name table
        opts.notdef_outline = True
        font = TTFont(src / name)
        sub = subset.Subsetter(opts)
        sub.populate(text="".join(kept))
        sub.subset(font)
        out = OUT / f"{face}-{weight}.woff2"
        font.flavor = "woff2"
        font.save(out)
        print(f"{out.relative_to(ROOT)}: {len(kept)} 字符，{out.stat().st_size / 1024:.0f} KB")
    (OUT / f"OFL-{face}.txt").write_text((src / "OFL.txt").read_text(encoding="utf8"), encoding="utf8")
    report[face] = len(kept)
missing = sorted(c for c in chars if c not in covered and ord(c) > 0x7F)
(OUT / "coverage.json").write_text(json.dumps({"faces": report, "kept": "".join(sorted(covered)), "fallback": "".join(missing)}, ensure_ascii=False, indent=1), encoding="utf8")
print("由系统字体补字：", "".join(missing))
