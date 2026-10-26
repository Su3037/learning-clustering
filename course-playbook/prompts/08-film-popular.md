# Prompt 08 · Popular-science film (科普)

---

Make the popular-science film for **{{Module NN · topic}}**, in Chinese and English, cut to the course's
chosen track ({{We Never (Remix) — Hi Noise / 秋成, or the track named in the kick-off}}).
Read `course-playbook/reference/03-film-style.md` §2–5 first. Model: `video/m07-kernighan-lin/films.py`
(the `story` film), `scripts/film/story.py`, `scripts/film/hooks.py`.

**Audience**: curious non-specialists. Accessible, not childish. One complete argument, not a trailer.

**Steps**

1. **Hook** (0–17.4 s on We Never): a concrete everyday picture of *this algorithm's* key idea — not of the
   field in general. It lands on the sparse hits and its punchline plays in the silence. It must be true to
   the mechanism and pay off later. Write three candidates, pick one, say why.
2. **Beat sheet** with `templates/film-beat-sheet.md`: ~15 scenes mapped to the music sections (turn at 17.41,
   title on the drum roll 32.03–34.17, results on fills, the twist on 80.16–85.22, a breath 97–102.5,
   wider picture at 134, soft outro, invitation + credits at the end). For each beat: caption zh, caption en,
   what moves on screen, the data it reads.
3. **Story vehicle**: give the course example a human face if it helps (five friends, two rooms), but every
   number stays the engine's. Then return to the real field (chips / EDA) near 134 s.
4. **Assert** every stated number at the top of the script from `site/data/{{id}}/traces.json`.
5. **Draw** with the dark palette and functional objects: each important verb is a visible action; scenes
   change when the concept changes; several visual carriers (picture, graph, table, bars, chip).
6. **Captions**: short, natural, one idea per beat; both languages fit the shared timeline
   (zh 4.5 chars/s, en 15 chars/s, +0.8 s). 0 reading violations.
7. **Review**: contact sheet per language → fix collisions and legibility → (first film of a course) a
   25–45 s cut with the music for the author → full render.
8. **Credits** at the end and on the page: the track title and artist, "not covered by the course licence".

Output: `site/media/{{id}}/story.{zh,en}.{mp4,vtt,jpg}`, `film.json` entry with `why`, chapters, transcript.
Never commit the audio. Never state the film's length inside the film.
