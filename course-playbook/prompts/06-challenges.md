# Prompt 06 · Challenges

---

Write 6–7 challenges for **{{Module NN · topic}}** in `site/modules/{{id}}/challenges.js`. Model:
`site/modules/m07-kernighan-lin/challenges.js`.

Each challenge has:
- `id` (c1…), `type` (category, zh/en) — at least three categories per module from: 推演 Trace,
  解释 Explain, 决策 Decide, 实现 Implement, 探索 Explore, 约束 Constraint, 纠错 Fix, 应用 Apply.
- `difficulty`: Intro / Practice / Stretch, a separate field from the category, ordered easy → hard.
- `objectiveId` (o1…o6), `title` shown as `[category] title`.
- `why`: one sentence on what it checks and why it exists.
- `task`: precise question on the course example.
- `build`: input widgets (number fields, choices, combinations).
- `check(answer)`: **computes the expected value by calling the engine**; returns targeted feedback for the
  likely misconception (not just "wrong"), and an explanation with the actual numbers when correct.
- `hints`: exactly two, the second more concrete than the first.
- `answer` and `explanation`.

Coverage: one or two Intro traces of the key quantity, a Practice item on the subtle step (the negative
gain, the tie, the blocked merge), a Decide item on the stop or selection rule, an Explain item on why a
formula has its form, and a Stretch implement / explore item (change the graph and recompute).

Status model: not started / trying / solved alone / solved after viewing the answer. Viewing the answer is
allowed and not punished; reset lets the learner retry. Add tests that each correct answer passes and that
typical wrong answers produce the intended message.
