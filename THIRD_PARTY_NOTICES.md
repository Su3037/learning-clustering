# 第三方材料与工具

## 随仓库分发

- **Noto Sans SC**（Regular、Bold），来自 [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) 提交 `f8d157532fbfaeda587e826d4cd5b21a49186f7c` 的 `Sans/SubsetOTF/SC/`。Copyright © 2014–2021 Adobe (http://www.adobe.com/)；“Noto”是 Google 的商标。该字体未声明保留字体名（Reserved Font Name）。按 SIL Open Font License 1.1 分发，许可全文见 `fonts/noto-sans-sc/OFL.txt` 与 `site/assets/fonts/OFL.txt`。`site/assets/fonts/*.woff` 是用 fontTools 按本课程用字裁剪的子集（保留字体内的版权与许可信息）。课件 PDF 嵌入该字体的字形子集。
  - 原始文件 SHA-256：Regular `faa6c9df652116dde789d351359f3d7e5d2285a2b2a1f04a2d7244df706d5ea9`，Bold `c6cb5a93abaa9edc8ee7463b7ebb7f42d618d40e6ed2f7a5371c97b0b64767c0`。
- **Noto Serif SC**（Regular、SemiBold，© Adobe）、**Newsreader**（Regular、Medium、Italic，© The Newsreader Project Authors）、**Noto Sans**（Regular、SemiBold、Italic，© The Noto Project Authors）、**JetBrains Mono**（Regular、Medium，© The JetBrains Mono Project Authors）：均来自 Google Fonts 的静态字重，SIL Open Font License 1.1，未声明保留字体名；许可与来源见 `fonts/<face>/OFL.txt`，网站加载 `site/assets/fonts/` 中按本课程用字裁剪的 woff2 子集（`site/assets/fonts/OFL-<face>.txt`）。影片画面（中文版用 Noto Sans SC / Noto Serif SC，英文版用 Noto Sans / Newsreader，代码用 JetBrains Mono）只以像素形式出现，不嵌入字体文件。
- **Pyodide 0.28.3**（`site/vendor/pyodide/`，Mozilla Public License 2.0；其中 CPython 按 PSF License）：在线编程用的浏览器内 Python，原样分发，未修改。
- **CodeMirror 6**（`site/vendor/codemirror.js`，MIT，© Marijn Haverbeke 等）：在线编程的代码编辑器，用 esbuild 打包，未修改。版本与重建步骤见 `site/vendor/README.md`。
- **Module 05 引擎**改写自 [Su3037/clustering-lab5-label-propagation](https://github.com/Su3037/clustering-lab5-label-propagation)（MIT，Copyright (c) 2026 Su3037）。

## 只在本地生成时使用，不随网站分发

- **libcairo**（LGPL-2.1 / MPL-1.1）：经 Python ctypes 调用，逐帧绘制影片与课件。
- **FFmpeg**（libx264、AAC）：编码 MP4；许可取决于编译选项，见 https://ffmpeg.org/legal.html 。
- **NumPy**（BSD-3-Clause）：合成原创配乐；Module 06 检查器的可选对照。
- **fontTools**（MIT）：生成网站字体子集。
- **python-pptx**（MIT）：生成可编辑 PPTX。**pypdfium2**（Apache-2.0 / BSD）：PDF 页面检查。
- **Menlo**（macOS 系统字体）：只用于把旧版影片中的代码行渲染成画面像素，不嵌入、不分发。
- **pycairo**（LGPL-2.1 / MPL-1.1）、**Pillow**（HPND）：新版影片（`scripts/film/cine.py`）的逐帧绘制与发光层。
- **Playwright**（Apache-2.0）与 Chromium：录制“实验演示”影片时驱动真实课程页面（`scripts/film/recorder.mjs`）。
- **esbuild**（MIT）：打包 CodeMirror。

## 配乐

精讲、进阶与实验演示影片的配乐由 `scripts/film/music.py` 程序合成，是本课程的原创作品，按 CC BY 4.0 提供。

**科普影片**按作者的指定使用第三方录音《We Never (Remix)（若如初见）》，Hi Noise / 秋成，来源 https://www.bilibili.com/video/BV134Ho6qENu/ 。Module 05 的科普片就是作者原作《圈子从哪里来》（第四版，来自 Su3037/clustering-lab5-label-propagation），原样收录。这段音乐不属于本课程的 MIT 或 CC BY 4.0 许可，本课程不授予任何转载、改编或其他使用权；仓库与网站都不提供单独的音轨文件，渲染时使用的音频只保存在本地（见 `scripts/film/cinema.py`）。

## 算法来源

Kernighan & Lin 1970；Fiduccia & Mattheyses 1982；Fiedler 1973；Raghavan, Albert & Kumara 2007；Rajaraman & Wong 1993 / 1995；Lawler, Levitt & Turner 1969。只使用数学概念并引用来源，未复制论文图版。
