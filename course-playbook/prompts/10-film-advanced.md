# Prompt 10 · Advanced film (进阶)

---

Make the advanced film for **{{Module NN · topic}}** (zh + en, about 2:10–2:50; longer only if the topic
needs it; original score). Model: the `advanced` film in `video/m07-kernighan-lin/films.py` and in
`video/m05-label-propagation/films.py`.

Purpose: the questions a strong student asks after the concise film. Each section answers one "why" or
"what if" and **shows the run that proves it**.

Pick 4–6 sections from:
- Why the formula has its exact form (show the naive version failing with real numbers).
- Why a surprising step is allowed or required (a negative step that opens a larger gain — find a real case).
- Why a constraint matters (consecutive prefix, capacity, balance window) — show what breaks without it.
- Sensitivity: different seed / order / tie rule / sync vs async → different result (from real runs).
- Guarantees and non-guarantees: convergence, cycles, optimality, balance; counts vs areas.
- Cost: what one round costs, what real implementations do instead.
- Variants and the link to the next module.

End with a summary scene. Scene ids `a01…`. New examples (other graphs, seeds) come from the Python reference,
which the cross-check ties to the engine; add the facts to the engine tests too. Assert every number.
Output: `site/media/{{id}}/advanced.{zh,en}.*` and its `film.json` entry.
