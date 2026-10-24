#!/usr/bin/env python3
"""Print each pinned scene's slot against the reading time its captions need (for cutting a film to music).
  python3 scripts/film/slots.py m02-affinity-metrics story"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cine
import cinema

mod_id, film_id = sys.argv[1], sys.argv[2]
cine.Film.__init__.__defaults__  # noqa: B018
orig = cine.Film.__init__


def lenient(self, *a, **k):
    scenes = k.get("scenes") if "scenes" in k else a[5]
    t = 0.0
    if (k.get("id") or a[0]) == film_id:
        for sc in scenes:
            need = sum(max(cine.min_read(cine.both(b.text)[0], "zh"), cine.min_read(cine.both(b.text)[1], "en"), 0.6) if b.text else 0.6 for b in sc.beats)
            holds = sum(b.dur for b in sc.beats)
            end = sc.until if sc.until is not None else t + sc.dur
            flag = "  <-- short" if end - t < holds + 0.05 else ""
            print(f"{sc.id:<14} {t:7.2f}–{end:7.2f}  slot {end - t:6.2f}  read {need:6.2f}  with holds {holds:6.2f}{flag}")
            for b in sc.beats:
                if b.text:
                    zh, en = cine.both(b.text)
                    print(f"      zh {cine.min_read(zh, 'zh'):5.2f}  en {cine.min_read(en, 'en'):5.2f}  hold→{b.dur:5.2f}  {en[:70]}")
            t = end
        for sc in scenes:
            sc.until = None
    orig(self, *a, **k)


cine.Film.__init__ = lenient
cinema.load(mod_id)
