# 教师反馈逐条核对（T01–T24）

每一项写明：改在哪里、怎样核对、结果。“自动”指 `node --test tests/*.test.mjs`（41 项，全部通过）中的对应测试；“浏览器”指本地 `scripts/serve.py` 子路径 `/learning-clustering/` 下的实测。日期 2026-10-23。

| # | 反馈 | 位置 | 核对方式 | 结果 |
| --- | --- | --- | --- | --- |
| T01 | lab → module | 首页 8 张卡、模块页标题、`credits/`；`labs/<旧slug>/` 兼容入口 | 自动：扫描全部页面可见文本，“Lab 0x”只出现在来源 / 映射语境 | 通过；8 张卡 Module 02–09，无 Partitioning，无 Module 01/10+ |
| T02 | 重复内容 | `foundations/`、各章复习卡、`docs/duplicate-content-decisions.md` | 文档逐行给出 keep / rewrite / link / delete 与去向 | 通过（9 行，含 Multilevel“不制作”） |
| T03 | 课件页码 | 每页页脚 `Module 0X · p / total`；网页课件标题旁同号 | 自动：`pageNumber`、`pageCount` 连续；脚本核对 PPTX 页数 = PDF 页数 = slides.json | 通过（12/12/11/12/11/14/12/12 页） |
| T04 | 影片长度 | `video/<id>/film.py`（WHY 字段写明定长理由） | 实测时长表见完成报告 | 通过：单片 2:57–3:45；M05 另有 1:28 慢速推演；M09 分两集 3:00 + 2:22 |
| T05 | definition | 各章“问题定义”卡 | 自动：输入 / 输出 / 目标 / 约束 / 假设 / 停止六字段都在页面上 | 通过（8 章） |
| T06 | 挑战用途 | `guide/`；每章挑战区回链；M02 排序题、M08 回退题带局部提示 | 浏览器：打开指南、从挑战区链接往返 | 通过 |
| T07 | 常见错误 | 各章 `#mistakes`（错误做法 / 为什么错 / 反例 / 修正） | 自动：每章 ≥3 条；反例数值来自引擎与 `tests/engines.test.mjs` | 通过 |
| T08 | 挑战分组 | `content/modules/<id>/challenges.json`（生成） | 自动：`[类别] 题名`，type 与 difficulty 分开，每章 ≥3 类 | 通过 |
| T09 | md 大纲 | `content/modules/<id>/module.md`；下载区 `downloads/<id>-outline.md` | 自动：下载文件存在 | 通过 |
| T10 | 背景 | 各章讲解“背景”节与来源区 | 人工：历史只写有文献的（KL 1970、FM 1982、Fiedler 1973、LP 2007、RW 1993/1995 等），附 DOI | 通过 |
| T11 | 例子 | 可手算的小图 → 更难例 / 反例（如 M04 三种结局、M08 NEG_ESCAPE） | 引擎复算；`tests/crosscheck.py` JS ↔ Python 1324 项一致 | 通过 |
| T12 | 动画 | `video/<id>/film.py`、`figures.py`；画面数据来自 `build/<id>` 的 trace | 每片 8–12 个场景，各章独有场景 ≥4，数值读自引擎 trace | 通过 |
| T13 | use case | 各章“应用”节（EDA 场景、输入输出、局限；虚构图注明） | 人工审阅 | 通过 |
| T14 | 速度 | 渲染器 `Beat` 最短阅读时长（字数 / 4.5 + 0.8 秒） | 自动：每部片 `readingViolations = 0`；VTT 条数 = 文字稿条数 | 通过（10 部片均为 0） |
| T15 | machine voice | decision-log D-MEDIA-1 | 不配音，烧录中文字幕 + 原创配乐 | 通过；无配音因而没有试听项 |
| T16 | 由易到难 | 讲解顺序；挑战 Intro → Practice → Stretch | 自动：难度序单调不降 | 通过 |
| T17 | 弹簧 | 只在 M06 二次型处出现，标“类比” | 自动：其他章节无“弹簧” | 通过 |
| T18 | tts | decision-log | 不默认使用 | 通过（未使用） |
| T19 | problem statement | 同 T05；M09 用延迟与复制表述 | 同 T05 | 通过 |
| T20 | jump | 前置卡 / 复习卡；章节锚点、影片章节、课件页、挑战锚点、上一章 / 下一章 | 自动：所有相对链接与资源可解析；浏览器：深链 `#lab`、404 页 | 通过 |
| T21 | 文字稿在课件下方 / 比例 | 网页课件：画面下方是该页讲稿；16:9（理由见 D-SLIDE） | 浏览器：讲稿顶边 = 画面底边；375 px 宽无横向滚动 | 通过 |
| T22 | 伪代码 | 各章伪代码 + 逐行注释；实验当前事件高亮对应行 | 自动：每章有 `pseudo` 块；浏览器（M03）：单步时高亮从第 1 行变为 3、4、6、7 行 | 通过 |
| T23 | python | `python/<id>/` starter / reference / check / fixtures；`downloads/<id>-python.zip` | `check.py reference.py` 8 包全 PASS（6/7/6/7/8/5/8/5 项）；`check.py`（starter）为 INCOMPLETE，无 FAIL | 通过 |
| T24 | 新术语 | 首次出现的术语卡；`glossary/`（含“不能混淆”列） | 自动：每章 ≥2 张术语卡 | 通过 |

未能自动核对、只做了人工或抽查的：T10、T13 的文字质量；T12 的画面逐帧（抽查了 6 帧，见完成报告）；真实手机与多浏览器矩阵（只用了 375 px 视口模拟）。
