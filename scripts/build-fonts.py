"""Subset the bundled Noto Sans SC (SIL OFL 1.1, fonts/noto-sans-sc) to the characters the site uses.

Writes site/assets/fonts/noto-sans-sc-{400,700}.woff, OFL.txt and coverage.json (the characters kept,
plus the ones the face lacks, which the browser draws with a system fallback). Needs fontTools;
without it the committed files are kept and the script says so. Run after build-site.mjs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "noto-sans-sc"
OUT = ROOT / "site" / "assets" / "fonts"
WEIGHTS = {"400": "NotoSansSC-Regular.otf", "700": "NotoSansSC-Bold.otf"}

try:
    from fontTools import subset
    from fontTools.ttLib import TTFont
except ImportError:
    print("fontTools 不可用：保留已提交的字体子集（site/assets/fonts/）")
    sys.exit(0)

chars = {chr(c) for c in range(0x20, 0x7F)} | set("，。、；：！？（）《》「」『』“”‘’—…·–−×÷≤≥≈≠→←↔↑↓λΣδΔ∈∞⇥⌈⌉")
for p in list((ROOT / "site").rglob("*")) + list((ROOT / "content").rglob("*")):
    if p.is_file() and p.suffix in {".html", ".js", ".json", ".md", ".css", ".vtt"} and "fonts" not in p.parts:
        chars |= set(p.read_text(encoding="utf8"))
chars = {c for c in chars if c.isprintable() and c != "\n"}

OUT.mkdir(parents=True, exist_ok=True)
cmap = TTFont(SRC / WEIGHTS["400"]).getBestCmap()
kept = sorted(c for c in chars if ord(c) in cmap)
missing = sorted(c for c in chars if ord(c) not in cmap and ord(c) > 0x7F)
for weight, name in WEIGHTS.items():
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]          # keep the copyright and OFL notices in the name table
    opts.notdef_outline = True
    font = TTFont(SRC / name)
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(kept))
    sub.subset(font)
    out = OUT / f"noto-sans-sc-{weight}.woff"
    font.flavor = "woff"
    font.save(out)
    print(f"{out.relative_to(ROOT)}: {len(kept)} 字符，{out.stat().st_size / 1024:.0f} KB")
(OUT / "OFL.txt").write_text((SRC / "OFL.txt").read_text(encoding="utf8"), encoding="utf8")
(OUT / "coverage.json").write_text(json.dumps({"font": "Noto Sans SC", "kept": "".join(kept), "fallback": "".join(missing)}, ensure_ascii=False, indent=1), encoding="utf8")
print("由系统字体补字：", "".join(missing))
