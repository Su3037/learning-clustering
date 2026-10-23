# 实施日志

只记录实际执行的操作、命令和结果。日期均为 2026-10-23（本机时间）。

## 1. 读取与环境

- 读取交接文档 `Claude_Clustering_Course_Handoff_EN.md`（用户上传）与参考包全部 100 个文件，顺序按交接 §4。参考包与 ZIP 未改动（ZIP SHA-256 `4b1457b57dd588f26ab40423a1d17ba53e9953c93edfec6d9775349cd4da35c1`）。
- 同时读取 `output/_clustering-research/raw/files/`（审计时下载的学生源码，只读）中的 thy031 `index.html` greedy() 与 FM 附件 `inline.js`，用于精确复现原错误。
- 风格参考：克隆 `Su3037/clustering-lab5-label-propagation` 到会话临时目录并检出 `7b4eca7`（发布版），抽取 `circles.mp4` 每 30 秒一帧做成联系表目检；读 `site/style.css`、`render_film_v4.py`、`THIRD_PARTY_NOTICES.md`。本机 `Daily-SZY/label-propagation-lab5` 是较旧的 codex/video-v2 分支，未改动。
- 工具核对：Node v26.5.0，Python 3.13.9（anaconda），FFmpeg（libx264、aac），Homebrew libcairo 2（Python 通过 ctypes 调用，测试 1920×1080 帧约 2 ms，中文 Hiragino Sans GB 渲染正常），python-pptx 1.0.2 / reportlab / pypdfium2 位于本机已有的 codex 运行时 Python（`~/.cache/codex-runtimes/.../python`），未安装任何新包。无 Playwright 浏览器二进制、无 LibreOffice。

## 2. 引擎与正确性（S1）

新建 `site/engines/`：graph、affinity、merge（M03/M04）、lp（改写自用户 LP 引擎）、spectral（Jacobi 实时求解）、kl、fm（net 模型 + FM 增量更新）、rw（逻辑/实例分离）。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| Node 回归与性质测试 | `node --test tests/*.test.mjs` | 14/14 通过 |
| JS ↔ Python 交叉 | `python3 tests/crosscheck.py` | PASS：1324 项比较（M03/M05/M07/M08 逐步） |
| 练习参考实现（在 /tmp 目录运行） | `python3 python/<id>/check.py python/<id>/reference.py` | 8 个包全部 PASS（6/7/6/7/8/5/8/5 项） |
| 练习起始代码 | `python3 python/<id>/check.py` | 均为 INCOMPLETE（M04 的已提供 oracle 一项 PASS），无 FAIL |

已复现并修正的问题：

- **M03**：`legacyComparator` 选项逐字复现原 `cand < best`（含 i、j 下标的字符串比较），四配置 cut 9/16/12/16、首步 A–C@1；修正后 `compareKeys` 逐字段比较得 3/8/8/3，轨迹 18→13→8→3；另测 10 vs 2、2.5 vs 2、200 个随机图 cut 下降=亲和度。
- **M04**：`diagnose()` 输出 infeasible-by-bound（原图 K2 C2，下界 3）/ greedy-stuck（greedy_trap 3 簇，穷举 AC|BD cut 10）/ feasible-suboptimal（suboptimal 18 vs 11）。
- **M06**：Jacobi λ2 = 1.7733143437197103（审计 NumPy 1.7733143437197119，差 <1e-14）；sweep 6/3/5/6；15 个非空无标签二分（穷举计数也为 15）；无约束最优 ABC|DE=3，不是单点（单点最小 6）；原作三位小数向量残差 0.004406。
- **M07**：AE|BCD cut12 → A↔D 9、E↔C −8，前缀 1，cut3；次轮 −8,−6 空前缀；AB=1 时 cut8、g(A,D)=5。300 个随机图首步与独立穷举一致。
- **M08**：种子 D(+3) A(+6) C(−2) E(−6) B(−1)，cut 12,9,3,5,11,12，k*=2；原 hillclimb：初始 18、E 合法 +10、首轮最佳 8=平衡最优（原文 9→4 证伪）；替换反例 `NEG_ESCAPE`（种子 4198 搜索得到）：初始合法 gain 全 ≤0，FM −1、−1、+4，cut 6→4=穷举最优；第三例确认只有 2-pin 边；多引脚 net gain 单测；250 个随机图增量 gain = 从零重算 gain。
- **M09**：候选 DAG 在“lv 降序、逆拓扑平票”假设下得 8 簇、20 实例、k=l=8，与审计脚本一致；有环报错；链 7/10；120 个随机 DAG 上实例图合法且输出到达时间 = 标签。

## 3. 网站、内容与练习（S2–S3）

- 公共壳 `site/assets/`（样式、进度存储与导入导出校验、图形视图、实验播放器、挑战组件、影片与课件播放器）；`scripts/build-site.mjs` 从 `content/` 生成首页、公共页与 8 个模块页；`scripts/lib/md.mjs` 支持 pseudo / terms / callout / html 围栏。
- 8 个模块的 `module.json`、`module.md`、`lesson.md`、`slides.json`、实验 `lab.js`、挑战 `challenges.js`（共 49 题，两级提示）。
- 修复：lab.js 中 `bootModule` 调用早于常量定义导致 TDZ 报错，统一移到文件末尾；M07 轨迹列对空 decision 调用 `replace`；M09 事件名 `init` → `pi-labels`；M05 几何分组标签为灰色；数轴标签重叠改为错位排布。

## 4. 影片与课件（S4–S5）

- 渲染器 `scripts/film/`：Python + libcairo（ctypes）逐帧绘制，FFmpeg 编码，`music.py` 用 NumPy 合成原创配乐；字幕按阅读时长自动延长并检查。
- 先渲染 M07 最佳前缀 40 秒小样发到线程，再批量渲染 10 部片。
- 字形问题：苹方 / 冬青缺 −、↔，ᵀ、⌈⌉、下标与上标缺失 → 默认字体换为黑体-简，并为这些字符指定回退字体。cairo 的 group 会重置字体但缓存未清，导致部分画面字体错误 → group / end_group / restore 时清缓存，重渲染 M02、M03、M04、M05、M07（`build/rerender.log`）。
- 课件：同一套绘制原语输出 PDF（真实文字，嵌入字体）、PNG/JPG 预览与原生 PPTX（python-pptx，讲稿写入备注）。8 套共 96 页。

## 5. 验收（S6）

| 检查 | 结果 |
| --- | --- |
| `./scripts/build.sh` | 成功 |
| `node --test tests/*.test.mjs` | 38/38（新增 `tests/challenges.test.mjs`、`tests/site.test.mjs`） |
| `python3 tests/crosscheck.py` | PASS 1324 |
| 8 个 Python 包 reference / starter | 全 PASS / 全 INCOMPLETE 无 FAIL |
| PPTX / PDF 页数与备注 | 与 slides.json 一致 |
| 375 px 宽 14 个页面 | 无横向滚动 |
| 键盘单步、localStorage 被禁、导入校验、404 | 正常 |

site.test 首轮的 3 个失败及处理：M05 慢速推演只有 2 个章节 → 增加“结果 · 稳定”章节并重渲染；外链检查把正文里的“Tailwind CDN”误判 → 改为只检查 script / link / img / video 等资源属性；M05 页两处“作者 Lab05”改写为“原作（作者的 Lab05 仓库）”。抽帧发现 M04“合法但不是最优”场景簇标签压住面板标题 → 图下移并重渲染。

## 6. 作者决定后的收尾（字体、许可、Pages）

- 作者确认：仓库 `Su3037/learning-clustering`；代码 MIT，内容与影片 CC BY 4.0（配乐为原创，同样 CC BY 4.0）；字体改为 Noto Sans SC。
- 从 notofonts/noto-cjk 固定提交 `f8d1575` 下载 Regular / Bold（SHA-256 记在 THIRD_PARTY_NOTICES）到 `fonts/noto-sans-sc/`，OFL.txt 前加版权行。`cairo_ctx.py` 在 macOS 上用 CoreText 进程范围注册（注意：新系统上 CoreText 二进制在共享缓存里，不能用文件存在判断）。Noto 无上下标码位 → 改为缩小并升降的普通字符；PPTX 用 baseline 属性。
- 网站：`scripts/build-fonts.py`（fontTools）按全站用字裁出 WOFF 子集，约 240 KB / 字重；`course.css` 用 @font-face；`coverage.json` 记录保留字与补字。
- 重新渲染 10 部影片、8 套课件；PDF 只嵌入 Noto。抽帧发现并修正：M03 簇标签压住边权（下方簇标签改到簇下方、标签加底色）、M06 公式 xᵤ 下标。
- 浏览器发现并修正课件深链接：首次加载不再改写地址；`#slide-<id>` 刷新后滚到课件区；同页 hashchange 翻页；锚点滚动用 instant（平滑滚动在后台标签页里可能不执行）。
- 新增 site 测试 3 项（41/41）：路径大小写精确匹配、CSS url() 与 OFL、字体子集覆盖、`.nojekyll`。

## 7. 下一步

见 handoff-state.md。
