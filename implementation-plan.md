# 实施计划：Learning Clustering · 连接与分组

更新：2026-10-23。参考根：`/Users/su/Documents/ChatGPT/Daily-SZY/output/clustering-course-prompt-pack`（ZIP SHA-256 `4b1457b5…a1d17ba53e9953c93edfec6d9775349cd4da35c1`，未改动）。实现目录：本目录。

## 1. 范围（不可变）

只整合 `yongfu-li/eda-learning` 已关闭 Clustering Issue #1–#8，对应 Module 02–09：

| 显示 | moduleId | 主题 | 作者 | 备注 |
| --- | --- | --- | --- | --- |
| Module 02 | m02-affinity-metrics | 亲和度指标 | Capeur | |
| Module 03 | m03-greedy-pair-merge | 贪心成对合并 | thy031 | 补交网址已在 #2 评论，不算第 9 份 |
| Module 04 | m04-size-constrained-agglomerative | 容量约束凝聚聚类 | GateUltra | |
| Module 05 | m05-label-propagation | 标签传播 | Su3037 | 用户本人作品，MIT |
| Module 06 | m06-spectral-bisection | 谱二分 | xingguangyaoyu | |
| Module 07 | m07-kernighan-lin | KL 改进 | FanqinZeng | |
| Module 08 | m08-fiduccia-mattheyses | FM 改进 | stephQ-lab | 有效成果为 Issue 附件，非 TCLhw |
| Module 09 | m09-rajaraman-wong | RW 延迟导向聚类 | muranfei | 教师目录 Lab09 为 Multilevel，映射待确认 |

不做 Partitioning、Module 01/10–14、Multilevel。公共页（首页、基础速查、术语、挑战指南、资源与贡献、学习记录）不是新模块。

## 2. 实际工具（2026-10-23 在本机核对）

| 能力 | 采用 | 说明 |
| --- | --- | --- |
| 网站 | 纯静态 HTML/CSS/ES modules | 无框架、无 CDN；Node 脚本把内容 JSON/Markdown 生成为每模块独立静态页，支持 GitHub Pages 子路径 |
| 算法引擎 | `site/engines/*.js`（ES module） | 同一份代码供网页、挑战判定、影片 trace、Node 测试使用 |
| 独立核对 | `python/<id>/reference.py` + `tests/` | Python 独立实现，与 JS 逐步比较；另有穷举 oracle |
| 影片 | Python + libcairo（ctypes 直接调用 Homebrew 的 libcairo）+ FFmpeg libx264/aac | 逐帧确定性绘制，读真实 trace；约 2 ms/帧 |
| 配乐 | NumPy 程序合成原创电子氛围音 | 不使用 We Never 或任何第三方音轨 |
| 课件 | 同一 slide JSON → cairo PDF（真文字）+ PNG 预览；python-pptx 原生可编辑 PPTX | python-pptx 1.0.2 来自本机已有 codex 运行时 Python 环境，未新装包 |
| 字体 | macOS 系统 Hiragino Sans GB / Songti（渲染、PDF 子集嵌入），网页用访问者系统字体 | 不打包字体文件；可通过环境变量换 Noto（OFL） |
| 浏览器检查 | 应用内置浏览器 + 本地静态服务器 | 无 Playwright 浏览器二进制 |

## 3. 架构与公共契约（contentVersion 1）

```
site/                    可部署静态根（basePath 由 <base>/相对路径决定）
  index.html             首页：8 张模块卡、学习路线、M09 映射状态
  foundations/ glossary/ guide/ credits/ progress/
  modules/<id>/index.html  由 scripts/build-site.mjs 生成
  assets/shell.css shell.js   Shell、导航、进度、声音、导入导出
  assets/components/*.js      VideoPlayer SlideViewer ExperimentController TraceInspector ChallengeEngine CreditsPanel
  engines/*.js                graph affinity merge lp spectral kl fm rw
  modules/<id>/lab.js         本章实验与 validator（只调用引擎）
  data/<id>/*.json            fixture 与 trace（由引擎生成）
  media/<id>/                 mp4 vtt chapters.json poster
  slides/<id>/                PNG 预览、PDF、PPTX
  downloads/<id>-python.zip
  labs/<旧slug>/index.html    兼容入口（M09 不接管 multilevel）
content/modules/<id>/        module.md（大纲）algorithm-spec.md module.json slides.json crosswalk.json credits.json
video/<id>/                  storyboard.json（镜头、trace 绑定、最短阅读时长）script.md
python/<id>/                 starter.py reference.py check.py README.md fixtures/
scripts/  tests/  docs/
```

接口（冻结于 decision-log D-ENG-1）：`validate(input, options) -> {ok, errors}`；`run(input, options) -> {events, result, status, metadata}`。事件公共字段 `eventId phase step kind before after decision metrics sourceVersion`，按算法加 `candidates votes locks prefix instanceMap`。status ∈ `ready running completed stable cycle limit blocked invalid`。图：`nodes[{id,size}] edges[{u,v,w}]`；谱另含 `Lvariant balanceBounds solver precision diagnostics`；RW 为 `logicalDAG nodeDelay nodeSize capacity interClusterDelay instances[{instanceId,logicalId,clusterId}] instanceEdges`。

## 4. 执行阶段与内部任务

| 阶段 | 任务 | 交付 | 验证 |
| --- | --- | --- | --- |
| S1 正确性 | 写 8 个引擎与 Python 参考；复现 M03 比较器、M06 计数/平衡、M08 hillclimb、M09 候选图 | `site/engines/*` `python/*/reference.py` `tests/*` `data/*/traces` | `npm test`：fixture、跨语言、穷举、回归（含比较器 2/10 与小数） |
| S2 契约 | registry、module.json schema、tokens、进度模型、adapter；先用 M04 blocked、M05 cycle、M09 实例检验 | `site/data/registry.json` `docs/schema.md` | schema 校验脚本 |
| S3 公共壳 | Shell、首页、基础速查、术语、挑战指南、贡献、学习记录、组件 | `site/` | 子路径、深链刷新、键盘、减少动效、存储失败、导入校验 |
| S4 模块 | 按 audit/outline/adaptation 逐章写讲义、伪代码逐行、实验、挑战 | `content/modules/*` `site/modules/*` | 每章大纲验收数值由引擎复算 |
| S5 媒体 | 代表性小样（M07 最佳前缀）→ 检查 → 8 部影片、VTT、章节、文字稿、课件 PPTX/PDF | `media/` `slides/` `video/` | ffprobe、抽帧目检、页码、字幕区不遮挡 |
| S6 挑战/Python | 两级提示、重试、答案查看与独立完成区分；starter/reference/check | `python/*` `downloads/*.zip` | 干净目录跑 check：starter 报 INCOMPLETE，reference 报 PASS |
| S7 crosswalk | objective→section→scene/时间→slide→实验事件→challenge→Python 函数 | `content/modules/*/crosswalk.json` | 自动检查每个 objective 至少一处媒介 |
| S8 集成 | 无障碍、部署配置、署名、验收清单、完成报告 | `docs/` `.github/workflows/pages.yml`（不推送） | acceptance-checklist 逐项记录 |

## 5. 需求 → 任务 → 交付 → 检验（教师 24 项）

| ID | 要点 | 任务 | 交付位置 | 检验方式 |
| --- | --- | --- | --- | --- |
| T01 | lab→module | 统一“Module/模块”；来源映射页保留 Lab/Issue；M09 不覆盖 multilevel | 首页卡、`credits/`、`labs/*` | `tests/site.test.mjs` 扫描可见文本无 “Lab 0x” 作为学习单元称呼（来源区除外）；8 张卡 |
| T02 | 重复内容 | 基础速查承载公共定义；各章短复习卡+回链；`docs/duplicate-content-decisions.md` 记录 keep/rewrite/link/delete | `foundations/`、各章“复习卡” | 文档逐行有去向 |
| T03 | 页码 | 每页页脚 `Module 0X · p/total`，网页 viewer 同号，PDF 页序一致 | `slides/<id>/` | PDF 渲染抽查；脚本核对 PDF 页数=slides.json |
| T04 | 片长 | 按知识量定长，RW 两段；不批量多版本 | `video/*/storyboard.json` 记录理由 | 时长实测表 |
| T05 | definition | 每章“问题定义”卡（输入/输出/目标/约束/假设/停止） | 各章 #problem | 脚本检查六字段非空 |
| T06 | 挑战用途 | 公共“如何挑战”指南；M02 排序、M08 回滚加局部提示 | `guide/` | 浏览器实操一次 |
| T07 | 常见错误 | 每章错误库：错因、错误结果、反例、修正，反例由引擎验证 | 各章 #mistakes | 反例数值进测试 |
| T08 | 挑战分组 | `[类别] 题名`，type 与 difficulty 分开 | module.json challenges | schema 检查 |
| T09 | md 大纲 | 每章 `content/modules/<id>/module.md` 先于页/片/课件 | 同左 | 存在且被 crosswalk 引用 |
| T10 | 背景 | 动机与课程位置；历史只写有来源的（RW 1993/1995、KL 1970、FM 1982、LP 2007、Fiedler 1973） | 各章 #background | 来源链接 |
| T11 | 例子 | 可手算 fixture，再到更难例/反例 | 各章讲义与实验 | 引擎复算 |
| T12 | 动画 | 每章 ≥4 个独有、由 trace 驱动的场景 | `video/<id>` | storyboard 每镜头有 traceEvent 或说明为何无 |
| T13 | use case | EDA 场景、输入输出、局限；虚构图标注 | 各章 #application | 文本审阅 |
| T14 | 速度 | 字幕最短阅读时长（中文约 4.5 字/秒起）、公式停留 | storyboard minRead | 自动检查每条字幕时长 ≥ 字数/4.5+0.8 秒 |
| T15 | machine voice | 默认无配音；若改旁白先试音 | decision-log D-MEDIA-1 | 记录“未配音，无听审项” |
| T16 | 由易到难 | 讲解顺序与挑战 Intro→Practice→Stretch | module.json | 难度序检查 |
| T17 | 弹簧 | 仅 M06 二次型使用，标“类比” | M06 讲义/影片 | 文本检索其他章无弹簧 |
| T18 | tts | 可选工具，不默认 | decision-log | — |
| T19 | problem statement | 同 T05；M09 用延迟与复制 | 各章 #problem | 同 T05 |
| T20 | jump | 叙事跳步（前置卡、复习卡）+界面跳转（章节、slide、挑战锚点、上一章/下一章） | 各章 | 链接检查脚本 + 浏览器实测 |
| T21 | 文字稿在课件下方/比例 | SlideViewer 下方 transcript；16:9 设计选择写明理由 | 各章 #slides | 窄屏截图检查无遮挡 |
| T22 | 伪代码 | 逐行解释表，行号与实验当前事件联动高亮 | 各章 #pseudocode | 实验中高亮行随事件变化 |
| T23 | python | 每章 starter/reference/check/fixtures | `python/<id>` | 干净目录运行记录 |
| T24 | 新术语 | 首次出现定义（中/英/直觉/符号），术语表统一 | `glossary/`、各章术语卡 | 术语表覆盖检查 |

## 6. 算法正确性清单（来自 handoff §7）

| 模块 | 必须成立 | 测试 |
| --- | --- | --- |
| M02 | edge 6 对、shared 10 对（A–C=5, B–D=2）；priority XY@5 / PQ@8；pin-count AB=0.5, EF=1, raw AB=2 | `tests/m02.test.mjs` + Python |
| M03 | 修复比较器：K2 无容量 18→13→8→3；K3 cut8；K2 cap2 AB\|C\|DE cut8 targetReached=false；cap3 cut3；2 vs 10、小数回归；cut 下降=affinity | 含“旧比较器”复现测试 |
| M04 | 区分 infeasible / greedy-stuck / feasible-suboptimal；greedy_trap 3 簇 vs 可达 2 簇 cut10；suboptimal 18 vs 11 | 穷举 oracle |
| M05 | B/B/B/E/E 两轮；sync 双点 cycle；CD=10 cut5；24 单元 cut88/LP cut2/5 轮；联系人 3 轮 cut4 | 与用户原 LP 实现及 Python 交叉 |
| M06 | λ2≈1.7733143437；sweep 6/3/5/6；40/60 窗口仅 k2/k3；非空无标签二分=15；翻号等价；断开图 λ2=0 | JS Jacobi 实时求解 + 残差/正交诊断 |
| M07 | AE\|BCD cut12；A↔D 9、E↔C −8、前缀 1、cut3；次 pass 空前缀；AB=1 时 cut8、g(A,D)=5 | 随机图穷举候选核对 |
| M08 | 种子 D(+3) A(+6) C(−2) E(−6) B(−1)，cut 12,9,3,5,11,12，k*=2；旧 hillclimb 证伪回归；新负增益反例经穷举核验 | 穷举 |
| M09 | 有环报错；链 7/10；候选 DAG 8 簇、20 实例、PO=8（candidate 状态）；实例 fanin 合法 | Python 复原脚本对照 |

## 7. 发布边界

本地完成与审阅。未经用户后续明确指示：不推送远程、不开 Pages、不改可见性、不在 Issue 评论、不联系老师或同学。`.github/workflows/pages.yml` 只作为配置文件提供。
