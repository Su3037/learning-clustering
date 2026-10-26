# Prompts

Paste-ready prompts, one per production step. Run `00-kickoff.md` first; then, per module, `01`–`11`, `13`,
`14`; then `12` (home intro) once all modules exist; then `15`. Replace every `{{…}}` placeholder.

| # | Prompt | Output |
| --- | --- | --- |
| 00 | [Kick-off](00-kickoff.md) | scope, tools, four working documents, pilot choice |
| 01 | [Audit the sources](01-audit-sources.md) | per-module audit, fixtures, errors to fix |
| 02 | [Module outline](02-module-outline.md) | `module.md` (before anything else) |
| 03 | [Engine and traces](03-engine-and-traces.md) | JS engine, Python reference, cross-check, tests, traces |
| 04 | [Site shell](04-site-shell.md) | generator, design system, i18n, shared pages and components |
| 05 | [Module page](05-module-page.md) | `module.json`, `lesson.md` |
| 06 | [Challenges](06-challenges.md) | 6–7 engine-checked challenges |
| 07 | [Code lab](07-code-lab.md) | starter / reference / check / fixtures + visualiser |
| 08 | [Popular film](08-film-popular.md) | 科普 film cut to the chosen track |
| 09 | [Concise film](09-film-concise.md) | 精讲 film |
| 10 | [Advanced film](10-film-advanced.md) | 进阶 film |
| 11 | [Lab walkthrough](11-film-lab-walkthrough.md) | 实验演示 film recorded from the real page |
| 12 | [Home intro film](12-film-home-intro.md) | 导论 film for the home page |
| 13 | [Slides](13-slides.md) | PDF, PPTX with notes, web viewer |
| 14 | [English version](14-translation.md) | all English sources, films, walkthrough |
| 15 | [QA and release](15-qa-and-release.md) | tests, browser pass, report, deploy |

Tips for any tool:
- Give the agent the whole `course-playbook/` folder (or at least `SKILL.md` + the reference file the prompt
  names). The prompts are short because the rules live in `SKILL.md` and `reference/`.
- Run one module at a time. Start a fresh session per module if the context gets long; resume from
  `handoff-state.md`.
- If the tool cannot render video or drive a browser, ask it to produce the scripts and exact commands,
  then run them yourself.
