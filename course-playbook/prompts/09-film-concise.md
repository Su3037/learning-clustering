# Prompt 09 · Concise film (精讲)

---

Make the concise film for **{{Module NN · topic}}** (zh + en, 1:50–2:35, original score `score:steady` or
similar). Model: the `concise` film in `video/m07-kernighan-lin/films.py`.

Purpose: the whole algorithm on the course example, for a learner reviewing before an exam. No hook, no
story, no detours.

Structure (scene ids `k01…`, 7–11 scenes):
1. Title card.
2. The problem: input, what is fixed, the objective, the seed / starting state with its value.
3. The key quantity (e.g. D values) with every number on screen.
4. The core rule (e.g. pair gain with −2w), computed for the candidates.
5. One full round, step by step, including the subtle step (negative gain, tie, blocked merge).
6. The selection / acceptance rule (best prefix, rollback) and the next round.
7. The stop condition and the final result.
8. Summary: the rule in one screen, matching the pseudocode.

Same rules as every film: numbers asserted from traces, functional objects, dark palette, captions sized
for both languages, 0 reading violations, contact sheet before full render.
Output: `site/media/{{id}}/concise.{zh,en}.*` and its `film.json` entry with a `why` paragraph.
