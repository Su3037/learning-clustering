# Prompt 02 · Module outline (write before any page, slide or film)

---

Write `content/modules/{{id}}/module.md` for **{{Module NN · topic}}** using
`course-playbook/templates/module-outline.md`. Read the module's audit first, and look at
`content/modules/m07-kernighan-lin/module.md` in the reference repo as a finished example.

Required sections:

1. **Problem definition** in one paragraph: input → operation → output → stop.
2. **Objectives** `o1…o6`: each one a verb a learner can be tested on (compute, trace, decide, explain,
   implement, name the limits). Cover: inputs/outputs, the key quantity, one full run, the subtle step,
   pseudocode + Python, limits.
3. **Lesson order**: 6–8 anchors `mNN-topic`, from the hand-checkable example to pseudocode and limits.
4. **Acceptance numbers**: every value the lesson, films and challenges will state, as produced by the engine
   (per-step values, results, stop reason, a variant or two, the random-test properties).
5. **Four films**, each with title and section list:
   - 科普 (≈ 3:10, the chosen track): hook about THIS algorithm → … → invitation to the lab
   - 精讲 (1:50–2:35): problem → key quantity → one full round → stop → summary
   - 进阶 (2:10–2:50): 4–6 "why / what if" sections, each backed by a run → summary
   - 实验演示: what the walkthrough will show in the lab and code lab
6. **Slides** (11–14 titles) and **challenges** (6–7: `[category] title`, Intro → Practice → Stretch).
7. **Dedup**: what this module explains in full, and what it only links to (foundations or another module).

Rules: terms are defined before they are used; examples go from simple to harder to counterexample;
the hook must be about this algorithm, not about the field in general. Keep the original submission's
strengths. Do not invent numbers: if the engine does not exist yet, mark values as "to be confirmed by engine".
