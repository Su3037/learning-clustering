# Prompt 05 · Module page and lesson

---

Write the page content for **{{Module NN · topic}}** from its outline `module.md` and the engine traces.
Use `content/modules/m07-kernighan-lin/module.json` and `lesson.md` in the reference repo as the model for
shape, tone and depth (see `course-playbook/reference/02-volume-and-depth.md` for targets).

`module.json`:
- `title`, `topic`, `description` (one sentence), `hook` (one question), `cardText` (two sentences),
  prerequisites and next-module text, a review card.
- `objectives` o1–o6 with `where` links (lesson anchors, challenge ids, `python`, `lab`).
- `problem`: `input`, `output`, `objective`, `constraints`, `assumptions`, `stop`.
- `filmNote` (what the four films cover), `labTitle` + `labNote`, `challengeTip`.
- `mistakes` (4–5): `title`, `wrong`, `why`, `counter` (real numbers from the engine), `fix`.
- `limits` (bullets), `pythonPackage` (task + two hints), `credits` (student, site, repo, pinned commit,
  kept list, licence note incl. music), `references` (real citations).

`lesson.md` (6–8 sections, Chinese ≈ 6,000–9,000 characters):
- Each section `## {#mNN-topic} Title`. Start from a story-free statement of the problem on the course's
  small example, with every intermediate number in a table.
- `terms` blocks before first use (`中文 | english | definition`).
- Explain why each rule is needed with the counterexample that breaks the naive version.
- A `callout warn` for the one thing beginners get wrong.
- Background with a real citation; an application with honest limits.
- A `pseudo` block, one comment per line, matching the engine and the Python reference.

Write plainly: short sentences, one idea each; no filler, no hype; numbers exactly as the engine gives them.
Then write `module.en.json` and `lesson.en.md` (see prompt 14) and rebuild the site.
