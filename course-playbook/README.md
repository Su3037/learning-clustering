# Course playbook · 课程制作手册

The production experience of **Learning Clustering · 连接与分组**, packaged so that anyone, with any AI
tool (Claude, Codex, Cursor, DeepSeek, Gemini…) or none, can make another course with the same style,
format, content volume and depth.

- Live example: https://su3037.github.io/learning-clustering/
- Reference implementation: this repository

## 中文简介

这个文件夹把本课程的制作经验整理成一套可复用的 skill 与提示词，用来做**其他主题的课程**，并保持同样的风格、
格式、内容量和深度：

- 每门课：首页导论片 + 若干模块 + 基础速查、术语表、挑战指南、学习记录、资源与贡献；全站中英可切换。
- 每个模块：目标与问题定义（六要素）→ 四部影片（科普 / 精讲 / 进阶 / 实验演示）→ 讲义（从可手算的例子到伪代码）
  → 课件（带页码与讲稿）→ 浏览器内实验台 → 分组挑战（两级提示）→ 浏览器内在线编程（Pyodide）→ 常见错误 → 来源。
- 科普片配作者选定的音乐（本课程为《We Never (Remix)》），开头用**本章算法自己的**生活例子；“这个领域是什么”只在首页导论片讲一次。
- 所有数字来自课程自己的算法引擎，影片脚本对字幕里的数字做断言；一章一章做到位，不要全部浅做。

使用方法：先把 `SKILL.md` 交给你的 AI 工具作为长期规则，再按 `prompts/` 里的顺序逐步粘贴提示词。
各工具的接入方法见 `adapters/README.md`。

## What is inside

| Path | What it is |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The master instructions: what a finished course is, the non-negotiables, the workflow, volume targets. Works as a Claude skill and as a system prompt anywhere. |
| [`reference/`](reference/) | The detail: [course anatomy](reference/01-course-anatomy.md), [volume and depth](reference/02-volume-and-depth.md), [films](reference/03-film-style.md), [site and design](reference/04-site-design.md), [workflow](reference/05-workflow.md), [quality and tests](reference/06-quality-and-tests.md), [lessons learned](reference/07-lessons-learned.md). |
| [`prompts/`](prompts/) | 16 paste-ready prompts, one per production step, from kick-off to release. |
| [`templates/`](templates/) | Module outline, film beat sheet, working documents, completion report. |
| [`checklists/`](checklists/) | Module acceptance, film review, release. |
| [`adapters/`](adapters/) | How to load the playbook in Claude Code, Claude.ai, Codex, Cursor, Gemini CLI, DeepSeek and other chat models. |

## Quick start

1. Create the new course repository. Either start empty, or copy this repository as a base (below).
2. Copy `course-playbook/` into it and wire it to your tool ([adapters](adapters/README.md)).
3. Run [`prompts/00-kickoff.md`](prompts/00-kickoff.md) with your course's scope filled in.
4. Per module: prompts `01`–`11`, `13`, `14`. Pilot one module first and review it; then one module at a time.
5. When all modules exist: prompt `12` (home intro film), then `15` (QA and release).

## Starting a new course from this repository

The machinery is reusable as is; the content is not.

| Keep (generic) | Replace (course-specific) |
| --- | --- |
| `scripts/build-site.mjs`, `scripts/build.sh`, `scripts/serve.py`, `scripts/build-fonts.py`, `scripts/package-downloads.mjs`, `scripts/build-codelab.mjs` | `content/` (course, modules, glossary, foundations, synthesis, credits) |
| `site/assets/` (styles, shell, player, slides viewer, lab frame, challenges, code lab, progress), `site/vendor/` (Pyodide, CodeMirror) | `site/engines/` (your algorithms), `site/modules/<id>/lab.js`, `challenges.js` |
| `scripts/film/cine.py`, `cinema.py`, `story.py`, `music.py`, `recorder.mjs`, `walkthrough.py` | `video/<id>/films.py`, `walkthrough.mjs`, `figures.py`; `scripts/film/hooks.py` (your hooks) |
| `scripts/slides/build_slides.py` | `python/<id>/` exercises, `scripts/build-traces.mjs` entries |
| `.github/workflows/pages.yml`, test harness structure in `tests/` | test expectations, `site/media/`, `site/slides/`, `site/downloads/` |

Rename the course title, localStorage key (`learning-clustering:v1`), brand strings and the repository
subpath. Third-party music is never in the repository; point the renderer at your own copy
(`LC_MUSIC_<NAME>=/path/to/audio`) and keep the onset file only.

## Licence

The playbook text is CC BY 4.0, like the rest of the course content; the code it points to is MIT.
Credit "Learning Clustering · 连接与分组 (Su3037)" when you reuse it.
