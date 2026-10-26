# 03 · Films

Each module has four films. The home page has one introduction film. All are 2D, dark, technical, drawn from
real algorithm data, captioned, and without voice-over. This document is the style bible; the reference
renderer is `scripts/film/cine.py` (drawing kit), `scripts/film/cinema.py` (renderer),
`scripts/film/story.py` (music-structured popular films), `scripts/film/hooks.py` (chapter cold opens),
`scripts/film/walkthrough.py` + `recorder.mjs` (lab walkthrough).

## 1. The five film types

| Film | Job | Length | Music | Scenes |
| --- | --- | --- | --- | --- |
| **Home intro** (导论) | The common background of the whole course: what the field is, why it matters, why brute force fails, a tour of the method families | one track (3:10) | the chosen track | ~15 |
| **Popular science** (科普, `story`) | One algorithm as a story for curious non-specialists, opening with a hook about *this* algorithm | one track (3:10) | the chosen track | 15–17 |
| **Concise** (精讲, `concise`) | The algorithm start to finish on the course example, for review | 1:50–2:35 | original score | 7–11 |
| **Advanced** (进阶, `advanced`) | Why each rule, what-ifs, cost, limits, link to the next module | 2:10–2:50 (longer if needed) | original score | 7–14 |
| **Lab walkthrough** (实验演示, `lab`) | How to use the lab and code lab, recorded from the real page | 2:20–3:00 | original score | 5–7 chapters |

Page order is always: 科普 → 精讲 → 进阶 → 实验演示. Each film card on the page carries a one-paragraph
"why watch this" (`film.json → why`).

## 2. Art direction

Palette (from the author's original Label Propagation film):

| Role | Hex |
| --- | --- |
| Background (radial) | `#061219` → `#0b1f29` |
| Ivory text | `#eeeadd` |
| Muted / faint / dim | `#8fa3a3` / `#2a4048` / `#3d5d64` |
| Gold (focus, results) | `#ddbd78` |
| Teal (side 0, good) | `#76cbb5` |
| Blue (side 1) | `#86a9e0` |
| Rose (loss, error) | `#d99a9a` |
| Extra hues | amber `#d9b06c`, sage `#a3b26f`, lilac `#a18bc0`, coral `#d58f62` |
| Panels / nodes | `#081a22` / `#0b2029` |

- Outlined nodes with serif names; thin wires with a soft glow layer; letter-spaced chapter heads;
  1920×1080, 30 fps.
- Typography: Noto Serif SC / Newsreader for titles, Noto Sans SC / Noto Sans for text, JetBrains Mono for
  numbers and code. Labels big enough to read on a laptop in a classroom.
- **Functional objects**, not decoration: an accumulator visibly adds incoming weights; a cut edge visibly
  crosses the partition; a lock visibly locks; a prefix bar chart boxes the best prefix in gold.
- **Every important verb is an observable action.** "Swap", "lock", "roll back", "merge", "vote" each move
  something on screen. Colour change alone is not animation.
- Change the scene when the concept changes. Use many visual carriers (graph, table, bar chart, code panel,
  everyday picture, chip die) instead of one diagram for three minutes.
- Camera moves the explanatory objects (push-in to a node, pull back to the whole), never pans the whole
  frame including captions to fake motion.

Rejected: bright cream / sage backgrounds, cartoon people, storybook rooms, photorealistic generated images,
HUD overload, constant orbiting particles, decorative waveforms, the same five-node graph in every shot,
tiny low-contrast labels.

## 3. Captions and language

- No voice-over by default. Captions are burned in on a soft dark shade at the bottom (y 850–1080) and also
  shipped as WebVTT (off by default on the page).
- Chinese version: Chinese line (44 px, bold, up to two lines) with the English line small and italic under it.
  English version: English line only; on-screen labels switch to English.
- **Both languages share one timeline.** Every beat lasts at least the longer of
  `chars/4.5 + 0.8 s` (Chinese) and `chars/15 + 0.8 s` (English). The renderer counts violations; it must be 0.
- Write natural captions: short sentences, one idea each, every line tied to what is on screen at that moment.
  Numbers in captions are read from data and asserted in the script.
- Strings are authored as pairs: `L("中文", "English")`.

## 4. Scenes and beats (the authoring model)

A film is a list of scenes; a scene is a draw function plus beats (caption + hold time). The draw function
gets the frame and a clock and reads the absolute film time, so animation can lock to music hits.

```python
Scene("p-swap", p_swap, [
    Beat(L("Ada 和 Dev 换屋：12 → 3。", "Ada and Dev swap: 12 → 3."), 3.4),
    Beat(L("两人锁定，这一轮不再动。", "Both lock for the rest of the round."), 3.6),
], chapter=L("一 · 一对", "I · A pair"), until=S["fill1_end"])
```

- `until=` pins a scene's end to a music time (popular films). Otherwise scenes run as long as their beats.
- `Beat(None, 4.5)` is a silent hold (title, breath).
- At the top of every `films.py`: load traces from the engine output, then `assert` every number the
  captions state. If the engine changes, the film refuses to render instead of lying.

## 5. The popular film, cut to music

The author chose one track for every popular film and the home intro: **"We Never (Remix)（若如初见）" by
Hi Noise / 秋成**, at its original speed. For a new course, the author may choose another track; the method
stays the same:

1. Analyse the real recording: onset strength (spectral flux) and sections. Store only the onset times
   (`scripts/film/cues/<track>.json`), never the audio, in the repo.
2. Name the sections and give each a narrative job. The We Never map used by this course:

| Time (s) | Music | Narrative job |
| --- | --- | --- |
| 0.00–10.75 | sparse hits | cold open: the hook lands on the hits |
| 10.75–17.41 | silence | the punchline of the hook plays in silence |
| 17.41 | groove enters | the turn: "this is exactly the problem…" |
| 32.03–34.17 | drum roll | the title assembles one piece per hit, locks on 34.17 |
| 49.06–51.18 | fill | a first result lands |
| 63.15 | accent | a key step |
| 66.08–68.20 | fill | a list or table fills |
| 80.16–85.22 | phrase + fill | the twist flips on the strong hits |
| 97.19–102.50 | thinner | a breath: let the result sit |
| 102.50 | re-entry | the second half: harder case |
| 117.14–119.27 | fill | a result surfaces |
| 134.16–136.16 | fill | the wider picture lights up (chips, EDA) |
| 136.16–170.6 | soft outro | reflective: what the rule leaves open |
| 170.6–189.82 | sparse, quiet | invitation to the lab, credits |

3. Meaningful events (a commit, a reveal, a twist) land on audible structure. Do not flash on every beat.
   Never cut caption reading time to hit a beat.
4. Verify the export: same recording, same speed, no clipping, no truncation, clean ending.

**Licensing:** the track is third-party. It appears only inside the finished popular-film MP4s; it is not in
the repo, not offered as a download, and every page's credits say it is excluded from the course licence.
The render reads it from an environment variable (`LC_MUSIC_WENEVER=/path/to/audio`). Concise, advanced and
walkthrough films use the course's own synthesised score (`scripts/film/music.py`, NumPy, CC BY), kept low
(around −24 dBFS RMS) so it never competes with reading.

### Popular film structure (≈ 15 scenes)

```
p-hook, p-hook2   cold open about THIS algorithm's idea in everyday life (0–17.4 s)
p-rule            the turn: the same idea as a small problem with real numbers
p-title           title assembles on the drum roll
p-…               4–6 scenes: the key quantity, one worked step, the surprising step, the result
p-breath          a held moment (97–102.5 s)
p-why / p-more    the harder case or the twist that justifies the rule
p-chip            where it matters (EDA / the real field)
p-outro           what the rule leaves open; a question to the viewer
p-end             invitation to the lab; music credit
```

### Hooks: one per algorithm, never the general field

The general "what is clustering" story is told once, in the home intro. Each chapter opens with a picture of
its own algorithm's key idea:

| Module | Hook | Idea it carries |
| --- | --- | --- |
| M02 Affinity metrics | ranking contacts by shared group chats | a score for "how related" |
| M03 Greedy pair merge | raindrops on a window: the two nearest always merge first | greedy pairwise merging |
| M04 Capacity merge | a two-seat chairlift: three best friends cannot ride together | size constraints |
| M05 Label propagation | a catchphrase spreading along a dorm floor | adopt the neighbours' majority |
| M06 Spectral bisection | sand on a bowed plate gathers on one line and splits it | the Fiedler vector |
| M07 Kernighan–Lin | a chess sacrifice: lose 3 now, take 9 two moves later | trial swaps, best prefix |
| M08 Fiduccia–Mattheyses | two boats, one person crosses at a time, neither too crowded | single moves, balance |
| M09 Rajaraman–Wong | a kitchen: one cook per step, crossing the yard costs 3 minutes | delay along paths |

A good hook: concrete, surprising, true to the algorithm's mechanism, and it pays off later in the film.
A forced analogy (e.g. a library and book-sharing for label propagation) is worse than a concrete technical
problem. Logical strength beats sentiment.

### The home intro film

Wedding seating plan (you already cluster) → what clustering is → why chips need it → the cut → why trying
every split fails (5 people: 15 ways; 100 people: a 30-digit count) → a tour of the method families in the
course (score and merge; let groups emerge; improve a grouping; delay-driven) → invitation to the modules.

## 6. Concise and advanced films

Concise (example, M07): problem and seed → D values → pair gain and −2w → one pass of trial swaps → best
prefix and roll-back → stop → summary. Scene ids `k01…`. Starts with a title card, no hook.

Advanced (example, M07): I · why −2w → II · why negative gains are tried (an 8-node case: −1 then +7) →
III · why a prefix must be consecutive → IV · seed dependence (AB | CDE stuck at 5) → V · counts versus
areas → VI · cost of a pass → summary. Scene ids `a01…`. Each section answers one "why" or "what if" and
shows the run that proves it. New examples come from the Python reference, which is cross-checked against
the engine.

## 7. Lab walkthrough

- A browser automation script (`video/<id>/walkthrough.mjs`, Playwright) opens the real module page in each
  language and performs "shots": scroll to the lab, choose a seed, step, change an edge weight, open the code
  lab, type one function, run checks, run the visualiser. Each shot carries a caption pair and optional
  chapter and zoom target.
- The compositor (`scripts/film/walkthrough.py`) puts the page in a window on the dark backdrop, draws a
  cursor that glides and pulses on click, eases the view in on the part being explained, and adds captions.
- Chapters: the lab → change parameters → code lab → your code visualised → challenges.
- When a long step would bore (typing four functions), type one on screen and fast-forward the rest, and say
  so in the caption.

## 8. Review loop for films

1. Write the beat sheet (`templates/film-beat-sheet.md`) and check it against the engine numbers.
2. Render **stills / contact sheets** (one frame per scene, both languages) and look at them.
3. For a new style or the first film of a course, render a **25–45 s sample** with the real music that shows
   a meaningful algorithm step (not a title sequence) and get the author's reaction before rendering all.
4. Render full films. Check: reading violations = 0, duration, resolution, audio present, faststart,
   seeking, VTT cue count = transcript lines, no text collisions (check entry, middle and exit of each scene).
5. Say honestly what was reviewed: "contact sheets + 10 sampled frames" is not "watched in full".

Technical spec: MP4, H.264 yuv420p, AAC, `+faststart`, 1920×1080, 30 fps; poster JPG; WebVTT; `film.json`
with chapters (actual times), transcript and `readingViolations`. Films here run 5–11 MB each; the whole
site with 8 modules × 4 films × 2 languages is about 600 MB, which GitHub Pages serves fine. If a course gets
much bigger, move films to Releases or LFS.
