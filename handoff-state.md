# 交接状态

更新：2026-10-23。contentVersion 1，ENGINE_VERSION 1.0.0。本地 git 仓库在 `main`，没有远程，没有推送。

## 已完成

- 8 个模块（Module 02–09）的引擎、模块页、实验、挑战、影片（10 部）、课件（8 套 96 页，PDF / PPTX / 预览图）、Python 练习包、crosswalk、旧路径兼容入口（M02–M08）。
- 公共页：首页（含综合对比）、基础速查、术语表、如何挑战、学习记录、资源与贡献、404。
- 测试与验收全部通过，详见 `implementation-log.md` §5、`docs/COMPLETION_REPORT.md`、`docs/teacher-feedback-verification.md`。
- 部署配置已写好未执行：`.github/workflows/pages.yml`、`docs/DEPLOYMENT.md`；README、LICENSE（MIT）、LICENSE-CONTENT.md、THIRD_PARTY_NOTICES.md。

## 作者已决定（2026-10-23）

- 仓库 `Su3037/learning-clustering`（公开）；代码 MIT，内容、影片与原创配乐 CC BY 4.0；字体 Noto Sans SC（OFL，已下载并全部重渲染）。

## 已发布（2026-10-23）

- 公开仓库 https://github.com/Su3037/learning-clustering ，网站 https://su3037.github.io/learning-clustering/ 。远程 `main` 来自本地 `publish` 分支（单提交起点）；本地 `main` 保留完整开发历史，不推送。
- 以后更新：在本地 `main` 提交后，把改动带到 `publish`（如 `git checkout publish && git checkout main -- . && git commit`），再 `git push origin publish:main`；工作流会先测试再部署。公开验证结果见 COMPLETION_REPORT §7。

## 改版进行中（2026-10-23 起，分支 `redesign`）

- 作者要求：版式更雅致（参照原 LP 站）；每章四部影片（科普 / 精讲 / 进阶 / 实验演示）；Python/Tcl 离线练习改为浏览器内在线编程；中英双语可切换。顺序：Module 05 试点 → M02→M09 逐章，每章做完请作者确认。
- 已完成：新版式、在线编程（Pyodide + CodeMirror）、i18n（英文页在 `site/en/`，来自 `*.en.json` / `*.en.md`）、Module 05 四部影片（中英）、英文课件。
- 科普片配乐用《We Never (Remix)》（作者指定，第三方录音，不进仓库，见 docs/BUILD.md）。
- 推送受阻：本会话的 GitHub App 未安装到该仓库；改动以 bundle 保存在 `/mnt/project-files/redesign-v1/`。

## 2026-10-25 迭代（分支 claude/project-thread-ses2xv）

- 改动前的版本保存在远程分支 `saved/v1-redesign`（= main ba074c6）。
- 首页综合对比写出方法名；首页新增导论片（`video/home/films.py` → `site/media/home/`）。
- 各章科普片开场改为本章算法的生活例子（`scripts/film/hooks.py`）；Module 05 新做科普片《跟着邻居走》，作者原作改为“原作”一栏（`original.*`）。

## 如何继续

- 改文本：编辑 `content/`，运行 `./scripts/build.sh`。
- 四部影片（新）：`video/<id>/films.py` → `scripts/film/cinema.py <id>`；实验演示 `video/<id>/walkthrough.mjs` → `scripts/film/walkthrough.py <id>`（见 docs/BUILD.md）。
- 旧影片：编辑 `video/<id>/film.py`，运行 `python3 scripts/film/render.py <id>`（`--stills` 出静帧，`--sample a b` 出片段）。
- 改课件：`~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/slides/build_slides.py <id>`（需要 python-pptx）。
- 改了内容里的字：`./scripts/build.sh` 会重新裁剪网站字体（需要 fontTools）。
- 每次改动后：`node --test tests/*.test.mjs`、`python3 tests/crosscheck.py`。

## 不要做

- 不再推送或改动公开仓库设置，除非用户明确要求；不评论 Issue、不联系教师或同学。
- 不把 M09 改名 Multilevel，不为 `multilevel-clustering` 旧路径生成跳转。
- 不把 `legacyComparator`、`LEGACY_HILLCLIMB` 当教学结论展示（只作“已修复错误”说明与回归）。
- 不改动参考包 `output/clustering-course-prompt-pack`。
