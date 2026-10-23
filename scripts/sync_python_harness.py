#!/usr/bin/env python3
"""把 python/_shared/harness.py 复制进每个练习包的 check.py（标记之间），保持每个包自包含。"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
harness = (ROOT / "python/_shared/harness.py").read_text(encoding="utf-8")
start, end = "# ---- 自包含检查框架", "# ---- 框架结束 ----\n"
for check in sorted(ROOT.glob("python/m*/check.py")):
    text = check.read_text(encoding="utf-8")
    a, b = text.index(start), text.index(end) + len(end)
    check.write_text(text[:a] + harness + text[b:], encoding="utf-8")
    print("synced", check.relative_to(ROOT))
