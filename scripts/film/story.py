"""Shared structure for the popular-science films, which are cut to "We Never (Remix)" like the author's original
Lab05 film. The section times come from the measured onsets in scripts/film/cues/wenever.json (spectral flux,
not hand-annotated downbeats); every popular film pins its scenes to them with Scene(until=...).

  0.00–10.75   sparse hits            the cold open lands on the hits
  10.75–17.41  no onsets at all       the punchline plays in silence
  17.41        groove enters          the turn
  32.03–34.17  sixteenth-note roll    the title assembles, one piece per hit, and locks on 34.17
  49.06–51.18  fill                   a result lands
  63.15        phrase accent
  66.08–68.20  fill                   a list fills
  80.16–85.22  phrase plus fill       a twist flips on the strong hits
  97.19–102.50 thinner, a breath      the film breathes
  102.50       re-entry
  117.14–119.27 fill                  a result surfaces
  134.16–136.16 fill                  the wider picture lights up
  136.16–170.6 softer outro           the reflective ending
  170.6–189.82 sparse, then quiet     invitation to the lab and credits
"""
import math

from cine import (W, H, L, tr, GOLD, TEAL, IVORY, MUTED, FAINT, clamp, ease, cues, hits_between, pulse)
import cine

TIMES, STRENGTH = cues("wenever")
S = dict(intro_end=10.75, groove=17.41, roll=32.03, lock=34.17, fill1=49.06, fill1_end=51.18, accent=63.15,
         fill2=66.08, fill2_end=68.20, phrase=80.16, phrase_end=85.22, breath=97.19, reentry=102.50,
         fill3=117.14, fill3_end=119.27, fill4=134.16, outro=136.16, quiet=170.6, end=189.82)
TRACK = "track:wenever"


def strong(a, b, k=0.8):
    """Hits in [a, b) at least k × the 85th-percentile onset strength."""
    vals = sorted(STRENGTH.values())
    thr = vals[int(len(vals) * 0.85)] * k
    return [t for t in hits_between(TIMES, a, b) if STRENGTH.get(round(t, 3), 0) >= thr]


INTRO_HITS = strong(0, S["intro_end"])
ROLL_HITS = strong(S["roll"] - 0.05, S["lock"] + 0.05)
FILL1, FILL2 = strong(S["fill1"] - 0.05, S["fill1_end"] + 0.05), strong(S["fill2"] - 0.05, S["fill2_end"] + 0.05)
PHRASE = strong(S["phrase"] - 0.05, S["phrase_end"] + 0.05)
FILL3, FILL4 = strong(S["fill3"] - 0.05, S["fill3_end"] + 0.05), strong(S["fill4"] - 0.05, S["outro"] + 0.05)


def landed(T, hits, i):
    """0→1 ease after the i-th hit (clamped to the list)."""
    if not hits:
        return 1.0
    t = hits[min(i, len(hits) - 1)]
    return ease((T - t) / 0.35)


def title_assemble(fr, c, title, subtitle, kicker):
    """The title builds one piece per hit of the drum roll (characters in Chinese, words in English) and locks
    with a glow on the last hit."""
    s = tr(title)
    zh = cine.LANG == "zh"
    pieces = list(s) if zh else s.split(" ")
    hits = ROLL_HITS or [S["roll"] + i * 0.27 for i in range(9)]
    step = max(1, len(hits) // max(1, len(pieces)))
    size = 84 if zh else 86
    spacing = 14 if zh else 1
    gap = fr.measure(" ", size, "serif") if not zh else 0
    widths = [fr.measure(p, size, "serif", spacing=spacing) for p in pieces]
    total = sum(widths) + gap * (len(pieces) - 1)
    x = W / 2 - total / 2
    lock = pulse(c.T, [S["lock"]], 0.9) if c.T >= S["lock"] else 0
    for i, (p, w) in enumerate(zip(pieces, widths)):
        t_hit = hits[min(i * step, len(hits) - 1)]
        a = ease((c.T - t_hit) / 0.18)
        if a > 0:
            dy = (1 - a) * 22
            fr.text(p, x, 486 + dy, size, GOLD, a * c.p(0, 0.2), role="serif", spacing=spacing, glow=0.25 * a + 0.5 * lock)
        x += w + gap
    after = ease((c.T - S["lock"]) / 0.8)
    fr.text(kicker, W / 2, 370, 20, MUTED, after, anchor="c", spacing=4)
    fr.text(subtitle, W / 2, 560, 22, IVORY, 0.9 * after, anchor="c", spacing=3)
    fr.line((W / 2 - 220 * after, 610), (W / 2 + 220 * after, 610), GOLD, 1.2, 0.5 * after, glow=0.3 * after)


def credits(fr, c, lines, k=0):
    """Closing card: course line, original author, music credit."""
    a = c.p(k, 1.2)
    y = 400
    for i, (s, col, size) in enumerate(lines):
        fr.text(s, W / 2, y + i * 54, size, col, a * clamp(c.since(k) * 1.2 - i * 0.25), anchor="c", spacing=1)


MUSIC_LINE = L("音乐 · We Never (Remix)（若如初见）· Hi Noise / 秋成（第三方录音，不在本课程许可范围内）",
               "Music · “We Never (Remix)” · Hi Noise / 秋成 (third-party recording, not covered by this course’s licences)")
