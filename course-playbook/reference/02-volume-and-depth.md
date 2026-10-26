# 02 · Volume and depth

"Same content volume and depth" is measurable. These are the numbers of the finished Learning Clustering
course (October 2026). Aim for the same range; a module may go outside it when its topic clearly needs it,
and the decision log should say why.

## 1. Measured per module

| Module | Lesson zh (chars) | Lesson en (words) | Slides | Challenges | Concise | Advanced | Lab walk. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M02 Affinity metrics | 8,853 | 1,710 | 12 | 7 | 1:53 | 2:44 | 2:44 |
| M03 Greedy pair merge | 6,909 | 1,320 | 12 | 6 | 2:04 | 2:42 | 2:48 |
| M04 Size-constrained merge | 6,387 | 1,247 | 11 | 6 | 2:24 | 2:37 | 2:39 |
| M05 Label propagation | 7,248 | 1,512 | 12 | 6 | 2:34 | 4:54 | 2:19 |
| M06 Spectral bisection | 6,982 | 1,416 | 11 | 6 | 2:02 | 2:27 | 2:57 |
| M07 Kernighan–Lin | 5,852 | 1,182 | 14 | 6 | 1:56 | 2:10 | 2:41 |
| M08 Fiduccia–Mattheyses | 7,085 | 1,448 | 12 | 6 | 1:48 | 2:21 | 2:35 |
| M09 Rajaraman–Wong | 7,734 | 1,531 | 12 | 6 | 2:10 | 2:19 | 2:34 |

Every popular film is 3:10 (the length of the chosen track, 189.8 s), 15–17 scenes, about 30 captions.
The home intro film is also 3:10. Each module also has 6 objectives, 4–5 common mistakes, 5–9 term cards,
6–8 lesson sections, one pseudocode block, one lab and one code lab. Course-wide: 44 automated site/engine
tests, 1,324 JS ↔ Python step comparisons, 8 Python packs whose reference passes every check.

## 2. The depth bar, artefact by artefact

Depth is not length. Each artefact has a job; it is deep enough when it does that job for a beginner and
still teaches something to someone who already knows the algorithm.

### Lesson
- Starts from a **hand-checkable example** on the course's shared small graph (5 nodes, 6 weighted edges)
  and shows every intermediate number in a table.
- Explains **why** each rule is the way it is, with the counterexample that breaks the naive version
  (e.g. KL's gain must subtract 2w: without it, E↔D looks worth 9 but actually loses 1).
- Goes past the happy path: a harder case, a negative step, a tie, a failure mode, the stop condition.
- Has background with a real citation, an application with honest limits, and a limitations list.
- Pseudocode is explained line by line and matches the engine and the Python reference.

### Popular film (科普)
- A newcomer understands the opening without knowing any terms.
- It carries one complete argument: hook → problem → rule → worked step → twist → result → wider picture →
  invitation to the lab. It is not a trailer.
- It still states correct numbers from the engine.

### Concise film (精讲)
- The algorithm, start to finish, on the course example: problem, key quantity, one full round, the stop.
- No hook, no story. A learner reviewing before an exam should be able to watch only this.

### Advanced film (进阶)
- Answers the "why" and "what if" questions: why this formula, why this step is allowed, what changes with
  a different seed / order / tie rule, what it costs, where it breaks, how it relates to the next module.
- Every claim is backed by a run (engine or cross-checked reference), and the script asserts the numbers.

### Lab walkthrough (实验演示)
- Recorded from the real page. Shows how to use the lab, at least one "change a parameter and see why"
  experiment, and the code lab (typing one function, running checks, running your own code).

### Challenges
- Each tests one objective and says why it exists. At least three categories per module
  (trace / explain / decide / implement / explore / constraint / fix / apply).
- Wrong answers get targeted feedback that names the likely misconception, computed from the engine.

### Code lab
- Two functions that hold the algorithm's core idea (not boilerplate). The checker runs the learner's code on
  the course example and on random graphs (e.g. 120 random cases), reporting PASS / FAIL / INCOMPLETE per
  named check. Unfinished code never shows as PASS.

### Slides
- One idea per slide, numbered `Module 0X · title · p/total`, transcript below, film timestamp where a slide
  matches a film scene. The deck is teachable on its own in a classroom.

## 3. Things that must not be uniform

Do not force identical analogies, durations, section counts or challenge counts on every module. Keep each
original submission's distinctive strengths (a good story, a striking experiment, a particular dataset).
Uniform means the same structure, quality bar and visual language — not the same content shape.
