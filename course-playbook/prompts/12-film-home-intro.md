# Prompt 12 · Home introduction film (导论)

---

Make the home-page introduction film for **{{course}}** (zh + en, one track ≈ 3:10, the chosen music).
Model: `video/home/films.py`. Do this after all modules exist, because it tours them.

Purpose: the **common background** of every module, told once, so chapter films do not repeat it.

Arc (adapt to the field):
1. **Everyday hook** where the viewer already does the thing (Learning Clustering: a wedding seating plan —
   you are already clustering). Lands on the opening hits; punchline in the silence.
2. **What the concept is**, said plainly, on a small picture.
3. **Why it matters** in the real field (chips: short wires inside a block, long wires between blocks).
4. **The measure** everyone in the course uses (the cut) on the course's small graph.
5. **Why brute force fails** with real counts (5 people: 15 ways; 100 people: a 30-digit number).
6. **A tour of the method families** in the course, one picture each, each named as on the module cards
   (score and merge; let groups emerge; improve a grouping; …).
7. **Invitation** to start with Module 1; music credit.

Same rules: real data where it is course data, illustrations labelled as illustrations, numbers asserted,
dark palette, shared bilingual timeline, 0 reading violations. Output `site/media/home/intro.{zh,en}.*` and a
place for it at the top of the home page with a one-paragraph "why watch this".
