#!/usr/bin/env node
// Builds every static page of the course from content/ into site/, once per language. No dependencies.
// Chinese pages keep their original paths (site/…); English pages mirror them under site/en/….
// English text comes from *.en.json overlays and *.en.md files next to the Chinese sources; where a translation
// does not exist yet, the English page shows the Chinese text under a visible "not translated yet" note.
// Pages use relative links only, so the site works under any GitHub Pages project subpath.
import fs from 'node:fs';
import path from 'node:path';
import { render, sections, esc, inline, setLang } from './lib/md.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SITE = path.join(ROOT, 'site'), CONTENT = path.join(ROOT, 'content');
const LANGS = ['zh', 'en'];
const read = p => fs.readFileSync(p, 'utf8');
const readJSON = p => JSON.parse(read(p));
const write = (p, s) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, s); };
const exists = p => fs.existsSync(p);

/** Overlay translated fields onto the Chinese source. Arrays of objects merge by index, so ids and links stay shared. */
function overlay(base, over) {
  if (over === undefined) return base;
  if (Array.isArray(base) && Array.isArray(over)) return base.map((b, i) => (i < over.length ? overlay(b, over[i]) : b));
  if (base && typeof base === 'object' && over && typeof over === 'object' && !Array.isArray(base)) {
    const out = { ...base };
    for (const [k, v] of Object.entries(over)) out[k] = overlay(base[k], v);
    return out;
  }
  return over;
}
/** Read <name>.json (zh) and, for English, overlay <name>.en.json. Returns [data, translated?]. */
function readLocalized(file, lang) {
  const base = readJSON(file);
  if (lang === 'zh') return [base, true];
  const en = file.replace(/\.json$/, '.en.json');
  return exists(en) ? [overlay(base, readJSON(en)), true] : [base, false];
}
/** Read <name>.md (zh) or <name>.en.md. Returns [text, translated?]. */
function readLocalizedMd(file, lang) {
  const en = file.replace(/\.md$/, '.en.md');
  if (lang === 'en' && exists(en)) return [read(en), true];
  return [read(file), lang === 'zh'];
}

const course0 = readJSON(path.join(CONTENT, 'course.json'));
const BRAND = `<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M9 11 23 9M9 11 20 23" stroke="#8b958e" stroke-width="1.3"/><path d="M23 9 20 23" stroke="#a33b3b" stroke-width="1.3" stroke-dasharray="2.2 2"/><circle cx="9" cy="11" r="4.6" fill="#0f6b5c"/><circle cx="23" cy="9" r="3.6" fill="#2f5e9e"/><circle cx="20" cy="23" r="4.6" fill="#946a17"/></svg>`;
const PLAYBOOK = 'https://github.com/Su3037/learning-clustering/tree/main/course-playbook';

for (const lang of LANGS) buildLanguage(lang);
console.log('built zh + en');

function buildLanguage(lang) {
  setLang(lang);
  const EN = lang === 'en';
  const T = (zh, en) => (EN ? en : zh);
  const [course] = readLocalized(path.join(CONTENT, 'course.json'), lang);
  const out = p => path.join(SITE, EN ? 'en' : '', p);       // where a page is written
  const depth = p => p.split('/').length - 1 + (EN ? 1 : 0);  // directories between the page and site/
  const relOf = p => '../'.repeat(p.split('/').length - 1);   // from the page to its own language root
  const rootOf = p => '../'.repeat(depth(p));                 // from the page to site/ (shared assets, media, data)

  const modules = course.modules.filter(id => exists(path.join(CONTENT, 'modules', id, 'module.json'))).map(id => {
    const dir = path.join(CONTENT, 'modules', id);
    const [m, mt] = readLocalized(path.join(dir, 'module.json'), lang);
    let lt = true;
    if (exists(path.join(dir, 'lesson.md'))) { const [src, ok] = readLocalizedMd(path.join(dir, 'lesson.md'), lang); m.lesson = sections(src); lt = ok; } else m.lesson = [];
    m.translated = mt && lt;
    m.outlineMd = exists(path.join(dir, 'module.md'));
    const film = path.join(SITE, 'media', id, 'film.json');
    m.film = exists(film) ? readJSON(film) : { status: 'planned' };
    const deck = path.join(SITE, 'slides', id, 'slides.json');
    m.deck = exists(deck) ? readJSON(deck) : { status: 'planned' };
    m.challengeMeta = exists(path.join(dir, 'challenges.json')) ? readLocalized(path.join(dir, 'challenges.json'), lang)[0] : [];
    return m;
  });
  const [glossary, glossaryTranslated] = readLocalized(path.join(CONTENT, 'glossary.json'), lang);

  // Registry consumed by the shell (home progress bars, import validation). Language-neutral ids; titles per language.
  if (!EN) write(path.join(SITE, 'data', 'registry.json'), JSON.stringify({
    schemaVersion: 1, contentVersion: course.contentVersion, generated: new Date().toISOString().slice(0, 10),
    modules: modules.map(m => ({ moduleId: m.moduleId, displayOrder: m.displayOrder, display: m.display, title: m.title, topic: m.topic,
      author: m.credits.student.name, sourceIssue: m.sourceIssue, teacherMappingStatus: m.teacherMappingStatus, challenges: m.challengeMeta.map(c => c.id) }))
  }, null, 2));
  else { // English titles for the shared registry (progress page, home cards)
    const reg = readJSON(path.join(SITE, 'data', 'registry.json'));
    for (const r of reg.modules) r.titleEn = modules.find(m => m.moduleId === r.moduleId)?.title;
    write(path.join(SITE, 'data', 'registry.json'), JSON.stringify(reg, null, 2));
  }

  const NAV = [['index.html', '首页', 'Home', 'home'], ['foundations/index.html', '基础速查', 'Foundations', 'foundations'], ['glossary/index.html', '术语表', 'Glossary', 'glossary'],
    ['guide/index.html', '如何挑战', 'Challenges', 'guide'], ['credits/index.html', '资源与贡献', 'Credits', 'credits'], ['progress/index.html', '学习记录', 'Progress', 'progress']];

  /** Notice shown on an English page whose text is still the Chinese original. */
  const untranslated = (p, what) => EN ? `<div class="wrap"><p class="i18n-note" lang="en"><b>Translation in progress.</b> ${what} is still shown in the original Chinese. The English edition is being written chapter by chapter. <a href="${rootOf(p)}${p}" hreflang="zh-CN" data-lang-link="zh">Open the Chinese page</a></p></div>` : '';

  function shell({ page, title, active = '', body, scripts = '', description = '' }) {
    const rel = relOf(page), root = rootOf(page);
    const zhHref = root + page, enHref = root + 'en/' + page;
    return `<!doctype html>
<html lang="${EN ? 'en' : 'zh-CN'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description || course.description)}">
<link rel="alternate" hreflang="zh-CN" href="${zhHref}">
<link rel="alternate" hreflang="en" href="${enHref}">
<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(BRAND.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))}">
<link rel="preload" href="${root}assets/fonts/${EN ? 'newsreader-400' : 'noto-serif-sc-400'}.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="${root}assets/course.css">
</head>
<body>
<a class="skip" href="#main">${T('跳到正文', 'Skip to content')}</a>
<header class="topbar"><div class="wrap">
<a class="brand" href="${rel}index.html">${BRAND}<span class="brand-name">Learning Clustering</span><span class="brand-sub">${T('连接与分组', 'Connect & group')}</span></a>
<nav class="topnav" aria-label="${T('课程', 'Course')}">${NAV.map(([href, zh, en, k]) => `<a href="${rel}${href}"${k === active ? ' aria-current="page"' : ''}>${T(zh, en)}</a>`).join('')}</nav>
<div class="lang-switch" role="group" aria-label="${T('语言', 'Language')}">${EN
    ? `<a href="${zhHref}" hreflang="zh-CN" lang="zh-CN" data-lang-link="zh">中文</a><span aria-current="true">EN</span>`
    : `<span aria-current="true">中文</span><a href="${enHref}" hreflang="en" lang="en" data-lang-link="en">EN</a>`}</div>
</div></header>
${body}
<footer class="footer"><div class="wrap">
<p>${T(`Learning Clustering · 整合已关闭 Clustering 提交 Module 02–09。原作者署名见<a href="${rel}credits/index.html">资源与贡献</a>。`,
    `Learning Clustering · Modules 02–09, built from eight closed Clustering submissions. Original authors are credited on the <a href="${rel}credits/index.html">Credits</a> page.`)}</p>
<p>${T(`想用同样的方法做别的课？制作手册（skill 与提示词，适用于 Claude、Codex、Cursor、DeepSeek 等）见 <a href="${PLAYBOOK}">GitHub 上的 course-playbook</a>，欢迎参考。`,
    `Making another course? The production playbook (a skill and prompts for Claude, Codex, Cursor, DeepSeek and others) is in <a href="${PLAYBOOK}">course-playbook on GitHub</a>, free to reuse.`)}</p>
<p><button class="btn quiet small" type="button" data-pref="reduceMotion">${T('减少动态', 'Reduce motion')}</button> <button class="btn quiet small" type="button" data-pref="sound">${T('声音', 'Sound')}</button> · ${T('内容版本', 'Content version')} ${course.contentVersion}</p>
</div></footer>
<script type="module">import { initShell } from '${root || './'}assets/core.js'; initShell();</script>
${scripts}
</body>
</html>
`;
  }

  const mmss = t => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, '0')}`;
  const filmVersion = f => f.versions ? (f.versions[lang] || f.versions.zh) : f;
  const filmDuration = m => m.film.status === 'ready' ? (m.film.films ? m.film.films.map(f => mmss(filmVersion(f).duration)).join(' + ') : mmss(m.film.duration)) : T('计划中', 'planned');
  const eyebrow = (n, zh, en) => `<p class="eyebrow"><span class="eyebrow-no">${String(n).padStart(2, '0')}</span> / ${T(zh, en)}</p>`;
  // Course-authored links inside content point at Chinese pages (../../foundations/…); they resolve the same way on English pages.

  /* ---------------- module pages ---------------- */
  function modulePage(m, idx) {
    const page = `modules/${m.moduleId}/index.html`, rel = relOf(page), root = rootOf(page);
    const prev = modules[idx - 1], next = modules[idx + 1];
    const navItems = [['goals', '目标与问题', 'Goals'], ['film', '影片', 'Films'], ['lesson', '讲解', 'Lesson'], ['slides', '课件', 'Slides'], ['lab', '实验', 'Lab'],
      ['challenges', '挑战', 'Challenges'], ['python', 'Python', 'Python'], ['mistakes', '易错与局限', 'Pitfalls'], ['sources', '来源', 'Sources']];
    const objectives = m.objectives.map(o => `<li id="obj-${o.id}">${inline(o.text)}<span class="links">${(o.where || []).map(w => `<a href="#${w}">${esc(sectionTitle(m, w))}</a>`).join(' · ')}</span></li>`).join('');
    const p = m.problem;
    const problem = [['输入', 'Input', p.input], ['输出', 'Output', p.output], ['目标', 'Objective', p.objective], ['约束', 'Constraints', p.constraints], ['假设', 'Assumptions', p.assumptions], ['停止 / 完成', 'Stopping', p.stop]]
      .map(([zh, en, v]) => `<div><b>${T(zh, en)}</b><p>${inline(v)}</p></div>`).join('');
    const lessonToc = m.lesson.map((s, i) => `<a href="#${s.id}"><span>${String(i + 1).padStart(2, '0')}</span>${esc(s.title)}</a>`).join('');
    const lesson = m.lesson.map((s, i) => `<section class="lesson-part" aria-labelledby="${s.id}"><h3 id="${s.id}"><span class="part-no">§ ${i + 1}</span>${esc(s.title)}</h3>${s.html}</section>`).join('\n');
    const mistakes = m.mistakes.map(x => `<article class="mistake"><h4>${inline(x.title)}</h4><dl><dt>${T('错误结果', 'Wrong result')}</dt><dd>${inline(x.wrong)}</dd><dt>${T('错因', 'Why')}</dt><dd>${inline(x.why)}</dd><dt>${T('反例 / 证据', 'Counterexample')}</dt><dd>${inline(x.counter)}</dd><dt>${T('修正', 'Fix')}</dt><dd>${inline(x.fix)}</dd></dl></article>`).join('');
    const py = m.pythonPackage;
    const status = m.teacherMappingStatus === 'pending'
      ? `<div class="notice"><strong>${T('来源映射待确认：', 'Source mapping pending: ')}</strong>${inline(m.mappingNote)}</div>` : '';
    const c = m.credits;
    const body = `
<nav class="module-nav" aria-label="${T('本模块', 'This module')}"><div class="wrap">${navItems.map(([id, zh, en], i) => `<a href="#${id}"><span>${String(i + 1).padStart(2, '0')}</span>${T(zh, en)}</a>`).join('')}</div></nav>
<main id="main">
${m.translated ? '' : untranslated(page, 'This chapter')}
<section class="mod-hero"><div class="wrap">
<div class="mod-hero-text">
<p class="eyebrow">${esc(m.display)} / ${esc(m.topic)}</p>
<h1>${esc(m.title)}</h1>
<p class="sub">${inline(m.hook)}</p>
<p class="byline">${T('原作者', 'Original author')} ${esc(c.student.name)} · ${T('来源', 'Source')} Issue #${m.sourceIssue.number} · ${m.teacherMappingStatus === 'pending' ? `<span class="warn">${T('教师目录对应待确认', 'Mapping to the teacher’s catalogue pending')}</span>` : T('来源映射已核对', 'Source mapping verified')}</p>
${status}
<nav class="pager" aria-label="${T('上一模块与下一模块', 'Previous and next module')}">${prev ? `<a href="../${prev.moduleId}/index.html">← ${esc(prev.display)} ${esc(prev.title)}</a>` : `<a href="../../index.html">← ${T('课程首页', 'Course home')}</a>`}${next ? `<a href="../${next.moduleId}/index.html">${esc(next.display)} ${esc(next.title)} →</a>` : `<a href="../../index.html#synthesis">${T('八个模块的综合对比', 'All eight modules compared')} →</a>`}</nav>
</div>
<aside class="factbox" aria-label="${T('本模块概况', 'At a glance')}"><dl>
<dt>${T('前置', 'Before')}</dt><dd>${inline(m.prerequisitesText)}</dd>
<dt>${T('接下来', 'Next')}</dt><dd>${inline(m.nextText)}</dd>
<dt>${T('影片', 'Films')}</dt><dd>${filmDuration(m)}</dd>
<dt>${T('课件', 'Slides')}</dt><dd>${m.deck.status === 'ready' ? T(`${m.deck.slides.length} 页，16:9，含页码`, `${m.deck.slides.length} pages, 16:9, numbered`) : T('计划中', 'planned')}</dd>
<dt>${T('挑战', 'Challenges')}</dt><dd>${T(`${m.challengeMeta.length} 题`, `${m.challengeMeta.length}`)} · ${[...new Set(m.challengeMeta.map(x => x.type))].map(t => `[${esc(t)}]`).join(' ')}</dd>
<dt>Python</dt><dd>${m.codelab ? T('在浏览器里直接写、直接运行', 'Write and run it right in the browser') : T('下载练习包，本地运行', 'Download the exercise pack and run it locally')}</dd>
</dl></aside>
</div></section>

<section class="section" id="goals"><div class="wrap">
<div class="section-head"><div>${eyebrow(1, '目标与问题', 'Goals and problem')}<h2>${T('这一模块要解决什么', 'What this module solves')}</h2></div><p>${T('先看问题和成功标准，再看算法。每个目标后面的链接指向讲它的地方。', 'Start with the problem and what counts as success, then the algorithm. Each goal links to where it is taught.')}</p></div>
${m.review ? `<p class="review"><b>${T('复习', 'Recap')}</b>${inline(m.review)}</p>` : ''}
<div class="grid-2 goals"><div><h3>${T('学习目标', 'Learning goals')}</h3><ol class="objectives">${objectives}</ol></div>
<div><h3>${T('问题定义', 'Problem statement')}</h3><div class="problem">${problem}</div></div></div>
</div></section>

<section class="section dark" id="film"><div class="wrap">
<div class="section-head"><div>${eyebrow(2, '影片', 'Films')}<h2>${esc(m.filmTitle || T('核心短片', 'The film'))}</h2></div><p>${inline(m.filmNote || T('画面中的每个数字都来自本页同一个引擎的运行记录。', 'Every number on screen comes from a run of the same engine this page uses.'))}</p></div>
<div id="film-root"><p class="muted">${T('正在载入影片…', 'Loading the film…')}</p></div>
</div></section>

<section class="section" id="lesson"><div class="wrap">
<div class="section-head"><div>${eyebrow(3, '讲解 · 由浅入深', 'Lesson · from intuition to pseudocode')}<h2>${T('从例子到伪代码', 'From an example to pseudocode')}</h2></div><p>${T('章节编号与影片章节、课件页对应；完整对应表见本页末尾的 crosswalk。', 'Section numbers match the film chapters and slide pages; the full map is in the crosswalk at the end of this page.')}</p></div>
<div class="lesson-layout"><nav class="lesson-toc" aria-label="${T('讲解小节', 'Lesson sections')}">${lessonToc}</nav>
<div class="prose">${lesson}</div></div>
</div></section>

<section class="section" id="slides"><div class="wrap">
<div class="section-head"><div>${eyebrow(4, '课件 · 带页码与讲稿', 'Slides · numbered, with notes')}<h2>${T('课堂课件', 'Classroom slides')}</h2></div><p>${T('页码与 PDF 完全一致；当前页的讲稿在幻灯片下方，不遮挡图。', 'Page numbers match the PDF exactly; the notes for each page sit below the slide.')}</p></div>
<div id="slides-root"><p class="muted">${T('正在载入课件…', 'Loading the slides…')}</p></div>
</div></section>

<section class="section dark" id="lab"><div class="wrap">
<div class="section-head"><div>${eyebrow(5, '实验 · 浏览器内实时计算', 'Lab · computed live in your browser')}<h2>${esc(m.labTitle || T('动手实验', 'Hands-on lab'))}</h2></div><p>${inline(m.labNote || T('自由实验不判分。单步、自动播放、改参数都由真实引擎重新计算；可以导出本次运行记录。', 'Nothing here is graded. Every step, replay and parameter change is recomputed by the real engine; you can export the run.'))}</p></div>
<div id="lab-root" tabindex="-1"><p class="muted">${T('正在载入实验…（需要通过 HTTP 打开页面；直接双击 HTML 时浏览器会阻止模块脚本。）', 'Loading the lab… (open the page over HTTP; browsers block module scripts in files opened directly.)')}</p></div>
</div></section>

<section class="section" id="challenges"><div class="wrap">
<div class="section-head"><div>${eyebrow(6, '挑战 · 由易到难', 'Challenges · easy to hard')}<h2>${T('分组挑战', 'Grouping challenges')}</h2></div><p>${T('类别写在方括号里，难度单独标注。答案由引擎或明确规则判定；看答案不扣分，记录会如实区分。', 'The category is in brackets and the difficulty is marked separately. Answers are checked by the engine or an explicit rule; looking at an answer costs nothing, and your record says so honestly.')}</p></div>
<p class="ch-guide">${T(`第一次用？先读<a href="${rel}guide/index.html">如何挑战</a>：读任务 → 预测 → 操作 → 提交 → 看解释 → 再试。`, `First time? Read <a href="${rel}guide/index.html">how challenges work</a>: read the task, predict, act, submit, read the explanation, try again.`)}${m.challengeTip ? ' ' + inline(m.challengeTip) : ''}</p>
<div class="ch-list" id="challenge-root"><p class="muted">${T('正在载入挑战…', 'Loading the challenges…')}</p></div>
</div></section>

<section class="section" id="python"><div class="wrap">
${m.codelab ? `<div class="section-head"><div>${eyebrow(7, '在线编程 · 在浏览器里运行 Python', 'Code it · Python in your browser')}<h2>${esc(py.title)}</h2></div><p>${T('不用安装任何东西：Python 在你的浏览器里运行（Pyodide），代码只保存在本机。检查器与下载包里的 check.py 完全相同。', 'Nothing to install: Python runs in your browser (Pyodide) and your code stays on this device. The checker is the same check.py as in the download.')}</p></div>
<div class="grid-2 cl-intro"><div class="prose">${render(py.md)}</div>
<div class="cl-howto"><h3>${T('怎么用', 'How it works')}</h3><ol><li>${T('在编辑器里补全标着 TODO 的函数。', 'Fill in the functions marked TODO in the editor.')}</li><li>${T('按 <b>运行检查</b>（Ctrl/⌘ + Enter）：每一项给出 PASS、FAIL 或 INCOMPLETE。', 'Press <b>Run checks</b> (Ctrl/⌘ + Enter): each check reports PASS, FAIL or INCOMPLETE.')}</li><li>${T('全部通过后，在下方用<b>你自己的</b>函数跑一遍例子，逐步对照课程引擎。', 'Once everything passes, run the examples below with <b>your own</b> functions and compare them step by step with the course engine.')}</li></ol>
<p class="small muted">${T('第一次运行会下载约 12 MB 的 Python 运行环境，之后由浏览器缓存。想离线做？', 'The first run downloads about 12 MB of Python runtime; the browser caches it afterwards. Prefer working offline?')} <a href="${root}downloads/${m.moduleId}-python${EN ? '-en' : ''}.zip" download>${T('下载练习包（.zip）', 'Download the pack (.zip)')}</a></p></div></div>
<div id="codelab-root" class="cl-root"><p class="muted">${T('正在载入在线编程…', 'Loading the code lab…')}</p></div>` : `<div class="section-head"><div>${eyebrow(7, 'Python 实现轨道 · 可选', 'Python track · optional')}<h2>${esc(py.title)}</h2></div><p>${T(`网页基础轨道不需要 Python。下载后在任意空目录运行；只用标准库${py.optional ? `（${esc(py.optional)}）` : ''}。`, `The web track needs no Python. Unzip anywhere and run it; it uses only the standard library${py.optional ? ` (${esc(py.optional)})` : ''}.`)}</p></div>
<div class="grid-2"><div class="prose">${render(py.md)}</div>
<div><div class="py-files"><div><code>starter.py</code>${T('起始代码：留有 TODO', 'Starter code with TODOs')}</div><div><code>check.py</code>${T('检查器：未完成报 INCOMPLETE，不算 PASS', 'Checker: unfinished work reports INCOMPLETE, never PASS')}</div><div><code>reference.py</code>${T('参考实现：卡住时再看', 'Reference solution, for when you are stuck')}</div><div><code>fixtures/</code>${T('本章例子的 JSON', 'The chapter’s examples as JSON')}</div><div><code>README.md</code>${T('任务、两级提示与样例', 'Task, two hints and samples')}</div></div>
<p><a class="btn primary" href="${root}downloads/${m.moduleId}-python.zip" download>${T('下载练习包（.zip）', 'Download the pack (.zip)')}</a></p>
<pre><code>python3 check.py              ${T('# 检查你的 starter.py', '# check your starter.py')}
python3 check.py reference.py ${T('# 看参考实现全部通过', '# the reference passes every check')}</code></pre></div></div>`}
</div></section>

<section class="section" id="mistakes"><div class="wrap">
<div class="section-head"><div>${eyebrow(8, '常见错误与局限', 'Common mistakes and limits')}<h2>${T('容易错在哪里', 'Where it goes wrong')}</h2></div><p>${T('每条都给错误结果、错因、反例和修正；反例的数值都由测试复算。', 'Each entry gives the wrong result, the cause, a counterexample and the fix; every number in the counterexamples is recomputed by the tests.')}</p></div>
<div class="mistakes">${mistakes}</div>
<div class="prose limits"><h3>${T('适用范围与局限', 'Scope and limits')}</h3>${render(m.limits)}</div>
</div></section>

<section class="section" id="sources"><div class="wrap">
<div class="section-head"><div>${eyebrow(9, '资料与原作者', 'References and original author')}<h2>${T('来源', 'Sources')}</h2></div><p>${T('本模块在统一课程中重写了讲解、引擎与媒体；原作的贡献在此署名。第三方音乐只在作者指定的影片里使用，并单独注明不在本课程许可范围内。', 'This module rewrote the lesson, engine and media for the unified course; the original work is credited here. Third-party music appears only in films where the author chose it, and is marked as outside this course\'s licences.')}</p></div>
<div class="grid-2"><div class="prose">
<h3>${T('原作者与保留的贡献', 'Original author and what was kept')}</h3>
<p><strong>${esc(c.student.name)}</strong> · <a href="${c.student.website}">${T('原网站', 'original site')}</a> · <a href="${c.student.repository}">${c.student.repository.includes('/user-attachments/') ? T('Issue 附件', 'Issue attachment') : T('原仓库', 'original repository')}</a>${c.student.commit ? T(`（固定 <code>${c.student.commit.slice(0, 7)}</code>）`, ` (pinned at <code>${c.student.commit.slice(0, 7)}</code>)`) : ''}</p>
<ul>${c.kept.map(k => `<li>${inline(k)}</li>`).join('')}</ul>
<p class="small muted">${inline(c.licenseNote)}</p>
</div><div class="prose">
<h3>${T('来源映射', 'Source mapping')}</h3>
<table><tbody><tr><th>${T('本课程', 'This course')}</th><td>${esc(m.display)} · <code>${m.moduleId}</code></td></tr><tr><th>${T('提交', 'Submission')}</th><td><a href="${m.sourceIssue.url}">Issue #${m.sourceIssue.number}</a> (${esc(m.sourceIssue.title)})</td></tr><tr><th>${T('教师目录', 'Teacher’s catalogue')}</th><td>${esc(m.teacherFolder)}</td></tr><tr><th>${T('状态', 'Status')}</th><td>${m.teacherMappingStatus === 'pending' ? T('待教师确认', 'awaiting the teacher’s confirmation') : T('已核对', 'verified')}</td></tr></tbody></table>
<h3>${T('参考文献', 'References')}</h3><ul>${c.references.map(r => `<li>${inline(r)}</li>`).join('')}</ul>
<p><a href="${root}data/${m.moduleId}/crosswalk.json">${T('本模块 crosswalk（目标 → 讲解 → 影片 → 课件 → 实验 → 挑战 → Python）', 'Crosswalk for this module (goal → lesson → film → slide → lab → challenge → Python)')}</a> · <a href="${root}downloads/${m.moduleId}-outline.md">${T('Markdown 大纲', 'Markdown outline')}</a></p>
</div></div>
</div></section>
</main>`;
    return shell({ page, title: `${m.display} ${m.title} · Learning Clustering`, body, description: m.description, active: '',
      scripts: `<script type="module" src="${root}modules/${m.moduleId}/lab.js"></script>` });
  }
  function sectionTitle(m, id) {
    const top = { goals: T('目标与问题', 'Goals'), film: T('影片', 'Film'), lesson: T('讲解', 'Lesson'), slides: T('课件', 'Slides'), lab: T('实验', 'Lab'), challenges: T('挑战', 'Challenges'), python: 'Python', mistakes: T('易错', 'Pitfalls') };
    if (top[id]) return top[id];
    const s = m.lesson.find(x => x.id === id); if (s) return s.title;
    const c = m.challengeMeta.find(x => `challenge-${x.id}` === id); if (c) return `[${c.type}] ${c.title}`;
    return id;
  }

  /* ---------------- home ---------------- */
  function home() {
    const page = 'index.html', root = rootOf(page);
    const cards = modules.map(m => `<a class="mod-card" href="modules/${m.moduleId}/index.html" data-module="${m.moduleId}">
<span class="num">${esc(m.display)}</span><h3>${esc(m.title)}</h3><p>${inline(m.cardText)}</p>
<p class="meta">${m.teacherMappingStatus === 'pending' ? `<span class="warn">${T('目录对应待确认', 'mapping pending')}</span> · ` : ''}${esc(m.credits.student.name)} · ${T('影片', 'film')} ${filmDuration(m)}</p>
<div class="bar" aria-hidden="true"><i></i></div><span class="small muted progress-text"></span></a>`).join('');
    const [synth, synthOk] = readLocalizedMd(path.join(CONTENT, 'synthesis.md'), lang);
    const body = `<main id="main">
<section class="wrap hero"><div class="hero-text">
<p class="eyebrow">Learning Clustering / ${T('八个模块', 'Eight modules')} / Clustering for EDA</p>
<h1>${T('连接与分组', 'Connect &amp; Group')}</h1>
<p class="hero-sub">${T('芯片里的分块，和通讯录里的圈子，<br>是同一个问题。', 'Blocks on a chip and circles in an address book are the same problem.')}</p>
<p class="lead">${T('芯片里成千上万个单元彼此连线。把联系紧密的单元放在一起，跨组的连线就少、短、快。八个模块从“怎么给一对单元打分”走到“怎样分组才让关键路径最快”。',
      'Thousands of cells on a chip are wired to each other. Put tightly connected cells together and the wires between groups become fewer, shorter and faster. Eight modules lead from “how do we score a pair of cells?” to “how should we group them so the critical path is fastest?”')}</p>
<div class="btn-row"><a class="btn primary" href="modules/m02-affinity-metrics/index.html">${T('从 Module 02 开始', 'Start with Module 02')} <span aria-hidden="true">→</span></a><a class="btn quiet" href="foundations/index.html">${T('先看基础速查', 'Foundations first')}</a><a class="btn quiet" href="progress/index.html">${T('我的学习记录', 'My progress')}</a></div>
<p class="byline">${T('开放课程 · 浏览器本地计算 · 代码 MIT，内容 CC BY 4.0', 'Open course · computed in your browser · code MIT, content CC BY 4.0')}</p>
</div>
<figure class="hero-art"><svg viewBox="0 0 440 300" role="img" aria-label="${T('五个节点 A 到 E 的示例图，ABC 与 DE 两组之间只有权重 3 的连线被切开', 'Example graph with five nodes A–E; only weight 3 is cut between the groups ABC and DE')}">
<path d="M86 88 C 40 160 120 230 190 196 C 250 168 260 60 196 50 C 150 42 110 54 86 88Z" fill="#0f6b5c" fill-opacity=".07" stroke="#0f6b5c" stroke-opacity=".35" stroke-dasharray="4 5"/>
<path d="M300 180 C 360 168 392 236 352 262 C 310 288 232 284 238 248 C 242 222 262 188 300 180Z" fill="#2f5e9e" fill-opacity=".07" stroke="#2f5e9e" stroke-opacity=".35" stroke-dasharray="4 5"/>
<g stroke="#9aa59e" stroke-width="1.6"><line x1="96" y1="94" x2="206" y2="74"/><line x1="96" y1="94" x2="164" y2="170"/><line x1="206" y1="74" x2="164" y2="170"/><line x1="324" y1="218" x2="262" y2="252"/></g>
<g stroke="#a33b3b" stroke-width="1.6" stroke-dasharray="5 4"><line x1="164" y1="170" x2="324" y2="218"/><line x1="164" y1="170" x2="262" y2="252"/></g>
<g class="art-w" font-size="14" fill="#5b665f"><text x="146" y="76">5</text><text x="116" y="140">1</text><text x="192" y="126">4</text><text x="246" y="186">2</text><text x="200" y="224">1</text><text x="298" y="250">5</text></g>
<g class="art-n" font-size="16" text-anchor="middle" fill="#fffdf8"><circle cx="96" cy="94" r="17" fill="#0f6b5c"/><text x="96" y="100">A</text><circle cx="206" cy="74" r="17" fill="#0f6b5c"/><text x="206" y="80">B</text><circle cx="164" cy="170" r="17" fill="#0f6b5c"/><text x="164" y="176">C</text><circle cx="324" cy="218" r="17" fill="#2f5e9e"/><text x="324" y="224">D</text><circle cx="262" cy="252" r="17" fill="#2f5e9e"/><text x="262" y="258">E</text></g>
</svg><figcaption>${T('课程公共图 G01：分成 ABC | DE，只切断 2 + 1 = 3。', 'The course graph G01: split into ABC | DE, only 2 + 1 = 3 is cut.')}</figcaption></figure>
</section>
<section class="section dark" id="intro"><div class="wrap">
<div class="section-head"><div>${eyebrow(1, '导论', 'Introduction')}<h2>${T('什么是聚类', 'What clustering is')}</h2></div><p>${T('八个模块的共同背景：从排座位讲起，什么是聚类、为什么芯片设计离不开它，以及这门课的几类方法。每章的科普片再从各自算法的生活例子讲起。', 'The background all eight modules share: from a seating plan to what clustering is, why chip design depends on it, and the families of methods in this course. Each module’s own popular film then starts from an everyday example of its algorithm.')}</p></div>
<div id="intro-film-root"><p class="muted">${T('正在载入影片…', 'Loading the film…')}</p></div>
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><div>${eyebrow(2, '学习路线', 'The route')}<h2>${T('八个模块', 'Eight modules')}</h2></div><p>${T('前三章讲评分与合并，LP 与谱方法给出两种产生初始分组的机制，KL/FM 改进已有分组，RW 把目标换成延迟。每章可以单独打开。', 'The first three score and merge; label propagation and spectral methods are two ways to produce a first grouping; KL and FM improve a grouping; RW changes the goal to delay. Each module stands on its own.')}</p></div>
<div class="route">${cards}</div>
<p class="route-legend">${T('编号沿用提交顺序（Issue #1–#8 对应 Module 02–09）。Module 09 的提交主题是 Rajaraman–Wong；教师课程目录中的 Lab 09 是 Multilevel，对应关系尚待教师确认，课程不会把两者混为一谈。',
      'Numbers follow the order of submission (Issues #1–#8 → Modules 02–09). The Module 09 submission is about Rajaraman–Wong; Lab 09 in the teacher’s catalogue is Multilevel. Their correspondence is awaiting the teacher’s confirmation, and the course keeps the two apart.')}</p>
</div></section>
<section class="section" id="synthesis"><div class="wrap">
<div class="section-head"><div>${eyebrow(3, '综合对比', 'Side by side')}<h2>${T('同一张五节点图，七种不同的操作', 'One five-node graph, seven different operations')}</h2></div><p>${T('Module 02–08 都用到课程公共图 G01，但每一章学的操作不同；Module 09 换成有向延迟模型，不使用这张图。', 'Modules 02–08 all use the course graph G01, but each teaches a different operation; Module 09 switches to a directed delay model and does not use it.')}</p></div>
${synthOk ? '' : untranslated(page, 'This comparison table').replace('<div class="wrap">', '<div>')}
<div class="prose wide">${render(synth)}</div>
</div></section>
</main>`;
    return shell({ page, title: T('Learning Clustering · 连接与分组', 'Learning Clustering · Connect & Group'), active: 'home', body, scripts: `<script type="module" src="${root}assets/home.js"></script>` });
  }

  /* ---------------- simple pages ---------------- */
  function simplePage(dir, active, title, mdFile, extraScript = '') {
    const page = `${dir}/index.html`;
    const [md, ok] = readLocalizedMd(path.join(CONTENT, mdFile), lang);
    const body = `<main id="main">${ok ? '' : untranslated(page, 'This page')}<section class="section page"><div class="wrap"><div class="prose">${render(md)}</div></div></section></main>`;
    write(out(page), shell({ page, title: `${title} · Learning Clustering`, active, body, scripts: extraScript.replaceAll('{root}', rootOf(page)) }));
  }
  function glossaryPage() {
    const page = 'glossary/index.html', rel = relOf(page);
    const rows = glossary.terms.map(t => `<tr id="g-${t.id}"><td>${EN ? `${esc(t.en)}<br><span class="small muted" lang="zh-CN">${esc(t.zh)}</span>` : `${esc(t.zh)}<br><span class="small muted">${esc(t.en)}</span>`}</td><td>${inline(t.meaning)}</td><td>${inline(t.notConfuse)}</td><td>${t.modules.map(id => { const m = modules.find(x => x.moduleId === id); return `<a href="${rel}modules/${id}/index.html">${m ? m.display.replace('Module ', 'M') : id}</a>`; }).join(' ')}</td></tr>`).join('');
    const body = `<main id="main">${glossaryTranslated ? '' : untranslated(page, 'The glossary')}<section class="section page"><div class="wrap">
<p class="eyebrow">${T('术语表', 'Glossary')}</p><h1>${T('统一术语与符号', 'Terms and symbols')}</h1>
<p class="lead">${T('每个术语在首次相关的模块中展开解释；这里给统一的中文名、英文名和“不能混淆”的提醒。同一个字母在不同模块可能表示不同的东西（例如谱方法的度矩阵 D 与 RW 的跨簇延迟 D）。',
      'Each term is explained in the first module that needs it; this page gives the shared Chinese and English names and what not to confuse it with. The same letter can mean different things in different modules (for example the degree matrix D in spectral methods and the inter-cluster delay D in RW).')}</p>
<div class="table-scroll"><table class="glossary-table"><thead><tr><th>${T('术语', 'Term')}</th><th>${T('含义', 'Meaning')}</th><th>${T('不能混淆', 'Do not confuse with')}</th><th>${T('首次展开', 'First explained')}</th></tr></thead><tbody>${rows}</tbody></table></div>
<div class="prose">${render(glossary.pronunciationMd)}</div>
</div></section></main>`;
    write(out(page), shell({ page, title: `${T('术语表', 'Glossary')} · Learning Clustering`, active: 'glossary', body }));
  }

  modules.forEach((m, i) => { write(out(`modules/${m.moduleId}/index.html`), modulePage(m, i)); if (!EN) crosswalk(m); });
  write(out('index.html'), home());
  simplePage('foundations', 'foundations', T('基础速查', 'Foundations'), 'foundations.md');
  simplePage('guide', 'guide', T('如何挑战', 'How challenges work'), 'guide.md');
  simplePage('credits', 'credits', T('资源与贡献', 'Credits'), 'credits.md');
  simplePage('progress', 'progress', T('学习记录', 'My progress'), 'progress.md', '<script type="module" src="{root}assets/progress.js"></script>');
  glossaryPage();
  if (!EN) { compat(modules); notFound(); }
}

/* ---------------- compatibility entries for old teacher-directory Lab paths ---------------- */
function compat(modules) {
  for (const m of modules) {
    if (!m.compatSlug) continue; // M09 deliberately has none: RW must not take over the multilevel path
    write(path.join(SITE, 'labs', m.compatSlug, 'index.html'), `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(m.display)} ${esc(m.title)}</title><meta http-equiv="refresh" content="0; url=../../modules/${m.moduleId}/index.html"><link rel="canonical" href="../../modules/${m.moduleId}/index.html"></head><body><p>旧路径 labs/${esc(m.compatSlug)}/ 已整合为 <a href="../../modules/${m.moduleId}/index.html">${esc(m.display)} ${esc(m.title)}</a>。</p></body></html>\n`);
  }
}

/* ---------------- crosswalk (language-neutral ids) ---------------- */
function crosswalk(m) {
  const cw = readJSON(path.join(CONTENT, 'modules', m.moduleId, 'crosswalk.json'));
  // Fill in actual video chapter times and slide numbers from the rendered assets (never typed by hand).
  // Schema 2 films list their scenes once (shared by both language versions); older films carry chapters only.
  const films = m.film.status === 'ready' ? (m.film.films || [m.film]) : [];
  const scenes = films.flatMap((f, fi) => [...(f.scenes || []).map(s => ({ sceneId: s.sceneId, t: s.start, film: f.id || fi })),
    ...((f.versions ? (f.versions.zh || Object.values(f.versions)[0]).chapters : f.chapters) || []).map(c => ({ ...c, film: f.id || fi }))]);
  for (const o of cw.objectives) {
    o.video = (o.sceneIds || []).map(sid => { const c = scenes.find(x => x.sceneId === sid); return c ? { sceneId: sid, film: c.film, start: c.t } : { sceneId: sid, status: m.film.status === 'ready' ? 'scene-not-found' : 'planned' }; });
    o.slides = (o.slideIds || []).map(sid => { const s = m.deck.slides?.find(x => x.slideId === sid); return s ? { slideId: sid, page: s.pageNumber } : { slideId: sid, status: 'planned' }; });
  }
  cw.contentVersion = course0.contentVersion; cw.generated = new Date().toISOString().slice(0, 10);
  write(path.join(SITE, 'data', m.moduleId, 'crosswalk.json'), JSON.stringify(cw, null, 2));
  // Markdown outline as a download (T09)
  if (m.outlineMd) write(path.join(SITE, 'downloads', `${m.moduleId}-outline.md`), read(path.join(CONTENT, 'modules', m.moduleId, 'module.md')));
}

// 404 is served for any missing path, at any depth, so it must not rely on relative links. Bilingual on one page.
function notFound() {
  write(path.join(SITE, '404.html'), `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>页面不存在 · Page not found · Learning Clustering</title>
<style>body{margin:0;font:17px/1.75 -apple-system,"PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;background:#f4f0e7;color:#1b2320}main{max-width:720px;margin:12vh auto;padding:0 20px}h1{font:400 40px/1.3 "Songti SC",Georgia,serif;margin:0 0 18px}a{color:#0f6b5c}.en{color:#5b665f;border-top:1px solid #d9d1c3;margin-top:28px;padding-top:20px}</style></head>
<body><main><h1>找不到这个页面</h1><p>地址可能已变更。所有模块都在 <a class="home" href="/">课程首页</a>。</p><p>如果你来自教师原课程的 Multilevel（Lab 09）链接：本课程的 Module 09 是另一份提交（Rajaraman–Wong 延迟导向聚类），对应关系待教师确认，它不替代 Multilevel。</p>
<div class="en" lang="en"><p><strong>Page not found.</strong> The address may have changed. Every module is listed on the <a class="home-en" href="/">course home page</a>.</p></div></main>
<script>/* GitHub Pages project sites live under /<repo>/ */var p=location.pathname.split('/').filter(Boolean);if(location.hostname.endsWith('github.io')&&p.length){document.querySelector('.home').href='/'+p[0]+'/';document.querySelector('.home-en').href='/'+p[0]+'/en/';}</script></body></html>
`);
}
