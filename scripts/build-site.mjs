#!/usr/bin/env node
// Builds every static page of the course from content/ into site/. No dependencies.
// Pages use relative links only, so the site works under any GitHub Pages project subpath.
import fs from 'node:fs';
import path from 'node:path';
import { render, sections, esc, inline } from './lib/md.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SITE = path.join(ROOT, 'site'), CONTENT = path.join(ROOT, 'content');
const read = p => fs.readFileSync(p, 'utf8');
const readJSON = p => JSON.parse(read(p));
const write = (p, s) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, s); };
const exists = p => fs.existsSync(p);

const course = readJSON(path.join(CONTENT, 'course.json'));
const modules = course.modules.filter(id => exists(path.join(CONTENT, 'modules', id, 'module.json'))).map(id => {
  const dir = path.join(CONTENT, 'modules', id);
  const m = readJSON(path.join(dir, 'module.json'));
  m.lesson = exists(path.join(dir, 'lesson.md')) ? sections(read(path.join(dir, 'lesson.md'))) : [];
  m.outlineMd = exists(path.join(dir, 'module.md'));
  const film = path.join(SITE, 'media', id, 'film.json');
  m.film = exists(film) ? readJSON(film) : { status: 'planned' };
  const deck = path.join(SITE, 'slides', id, 'slides.json');
  m.deck = exists(deck) ? readJSON(deck) : { status: 'planned' };
  m.challengeMeta = exists(path.join(dir, 'challenges.json')) ? readJSON(path.join(dir, 'challenges.json')) : [];
  return m;
});
const glossary = readJSON(path.join(CONTENT, 'glossary.json'));

// Registry consumed by the shell (home progress bars, import validation).
write(path.join(SITE, 'data', 'registry.json'), JSON.stringify({
  schemaVersion: 1, contentVersion: course.contentVersion, generated: new Date().toISOString().slice(0, 10),
  modules: modules.map(m => ({ moduleId: m.moduleId, displayOrder: m.displayOrder, display: m.display, title: m.title, topic: m.topic,
    author: m.credits.student.name, sourceIssue: m.sourceIssue, teacherMappingStatus: m.teacherMappingStatus, challenges: m.challengeMeta.map(c => c.id) }))
}, null, 2));

const BRAND = `<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="9" cy="11" r="5" fill="#0f6b5c"/><circle cx="23" cy="9" r="4" fill="#2f5e9e"/><circle cx="20" cy="23" r="5" fill="#8a6114"/><path d="M9 11 23 9M9 11 20 23" stroke="#56625b" stroke-width="1.6"/><path d="M23 9 20 23" stroke="#a33b3b" stroke-width="1.6" stroke-dasharray="2.5 2"/></svg>`;

function shell({ title, rel, active = '', body, scripts = '', description = '' }) {
  const nav = [['index.html', '首页', 'home'], ['foundations/index.html', '基础速查', 'foundations'], ['glossary/index.html', '术语表', 'glossary'],
    ['guide/index.html', '如何挑战', 'guide'], ['credits/index.html', '资源与贡献', 'credits'], ['progress/index.html', '学习记录', 'progress']];
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description || course.description)}">
<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(BRAND.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))}">
<link rel="stylesheet" href="${rel}assets/course.css">
</head>
<body>
<a class="skip" href="#main">跳到正文</a>
<header class="topbar"><div class="wrap">
<a class="brand" href="${rel}index.html">${BRAND}<span>Learning Clustering<br><small>连接与分组 · Clustering for EDA</small></span></a>
<nav class="topnav" aria-label="课程">${nav.map(([href, t, k]) => `<a href="${rel}${href}"${k === active ? ' aria-current="page"' : ''}>${t}</a>`).join('')}</nav>
</div></header>
${body}
<footer class="footer"><div class="wrap">
<span>Learning Clustering · 整合已关闭 Clustering 提交 Module 02–09。原作者署名见<a href="${rel}credits/index.html">资源与贡献</a>。</span>
<span><button class="btn quiet small" type="button" data-pref="reduceMotion">减少动态</button> <button class="btn quiet small" type="button" data-pref="sound">声音</button> · 内容版本 ${course.contentVersion}</span>
</div></footer>
<script type="module">import { initShell } from '${rel}assets/core.js'; initShell();</script>
${scripts}
</body>
</html>
`;
}

const mmss = t => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, '0')}`;
const filmDuration = m => m.film.status === 'ready' ? (m.film.films ? m.film.films.map(f => mmss(f.duration)).join(' + ') : mmss(m.film.duration)) : '计划中';

/* ---------------- module pages ---------------- */
function modulePage(m, idx) {
  const rel = '../../', prev = modules[idx - 1], next = modules[idx + 1];
  const navItems = [['goals', '目标与问题'], ['film', '影片'], ['lesson', '讲解'], ['slides', '课件'], ['lab', '实验'], ['challenges', '挑战'], ['python', 'Python'], ['mistakes', '易错与局限'], ['sources', '来源']];
  const objectives = m.objectives.map(o => `<li id="obj-${o.id}">${inline(o.text)}<span class="links">${(o.where || []).map(w => `<a href="#${w}">${esc(sectionTitle(m, w))}</a>`).join(' · ')}</span></li>`).join('');
  const p = m.problem;
  const problem = [['输入', p.input], ['输出', p.output], ['目标', p.objective], ['约束', p.constraints], ['假设', p.assumptions], ['停止 / 完成', p.stop]]
    .map(([k, v]) => `<div><b>${k}</b><p>${inline(v)}</p></div>`).join('');
  const lessonToc = m.lesson.map((s, i) => `<a class="btn small" href="#${s.id}">${i + 1}. ${esc(s.title)}</a>`).join(' ');
  const lesson = m.lesson.map((s, i) => `<section class="lesson-part" aria-labelledby="${s.id}"><h3 id="${s.id}"><span class="eyebrow" style="display:block;margin:0">第 ${i + 1} 节</span>${esc(s.title)}</h3>${s.html}</section>`).join('\n');
  const mistakes = m.mistakes.map(x => `<article class="mistake"><h4>${inline(x.title)}</h4><dl><dt>错误结果</dt><dd>${inline(x.wrong)}</dd><dt>错因</dt><dd>${inline(x.why)}</dd><dt>反例 / 证据</dt><dd>${inline(x.counter)}</dd><dt>修正</dt><dd>${inline(x.fix)}</dd></dl></article>`).join('');
  const py = m.pythonPackage;
  const status = m.teacherMappingStatus === 'pending'
    ? `<div class="notice"><strong>来源映射待确认：</strong>${inline(m.mappingNote)}</div>` : '';
  const c = m.credits;
  const body = `
<nav class="module-nav" aria-label="本模块"><div class="wrap">${navItems.map(([id, t]) => `<a href="#${id}">${t}</a>`).join('')}</div></nav>
<main id="main">
<section class="mod-hero"><div class="wrap">
<div>
<p class="eyebrow">${esc(m.display)} · ${esc(m.topic)}</p>
<h1>${esc(m.title)}</h1>
<p class="sub">${inline(m.hook)}</p>
<div class="btn-row"><span class="tag">原作者 ${esc(c.student.name)}</span><span class="tag">来源 Issue #${m.sourceIssue.number}</span>${m.teacherMappingStatus === 'pending' ? '<span class="tag warn">教师目录对应待确认</span>' : '<span class="tag ok">来源映射已核对</span>'}</div>
${status}
<nav class="pager" aria-label="上一模块与下一模块">${prev ? `<a href="../${prev.moduleId}/index.html">← ${esc(prev.display)} ${esc(prev.title)}</a>` : '<a href="../../index.html">← 课程首页</a>'}${next ? `<a href="../${next.moduleId}/index.html">${esc(next.display)} ${esc(next.title)} →</a>` : '<a href="../../index.html#synthesis">八个模块的综合对比 →</a>'}</nav>
</div>
<aside class="factbox" aria-label="本模块概况"><dl>
<dt>前置</dt><dd>${inline(m.prerequisitesText)}</dd>
<dt>接下来</dt><dd>${inline(m.nextText)}</dd>
<dt>影片</dt><dd>${filmDuration(m)}</dd>
<dt>课件</dt><dd>${m.deck.status === 'ready' ? `${m.deck.slides.length} 页，16:9，含页码` : '计划中'}</dd>
<dt>挑战</dt><dd>${m.challengeMeta.length} 题（${[...new Set(m.challengeMeta.map(x => x.type))].map(t => `[${t}]`).join('')}）</dd>
<dt>Python</dt><dd>下载练习包，本地运行（网页不运行 Python）</dd>
</dl></aside>
</div></section>

<section class="section" id="goals"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">目标与问题</p><h2>这一模块要解决什么</h2></div><p>先看问题和成功标准，再看算法。每个目标后面的链接指向讲它的地方。</p></div>
${m.review ? `<p class="review"><b>复习卡</b> · ${inline(m.review)}</p>` : ''}
<div class="grid-2"><div><h3 style="margin-top:0">学习目标</h3><ol class="objectives">${objectives}</ol></div>
<div><h3 style="margin-top:0">问题定义</h3><div class="problem" style="grid-template-columns:1fr 1fr">${problem}</div></div></div>
</div></section>

<section class="section dark" id="film"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">影片 · 二维科普短片</p><h2>${esc(m.filmTitle || '核心短片')}</h2></div><p>${inline(m.filmNote || '画面中的每个数字都来自本页同一个引擎的运行记录。')}</p></div>
<div id="film-root"><p class="muted">正在载入影片…</p></div>
</div></section>

<section class="section" id="lesson"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">讲解 · 由浅入深</p><h2>从例子到伪代码</h2></div><p>章节编号与影片章节、课件页对应；完整对应表见本页末尾的 crosswalk。</p></div>
<nav class="btn-row" aria-label="讲解小节" style="margin-bottom:24px">${lessonToc}</nav>
<div class="prose">${lesson}</div>
</div></section>

<section class="section" id="slides"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">课件 · 带页码与讲稿</p><h2>课堂课件</h2></div><p>页码与 PDF 完全一致；当前页的讲稿在幻灯片下方，不遮挡图。</p></div>
<div id="slides-root"><p class="muted">正在载入课件…</p></div>
</div></section>

<section class="section dark" id="lab"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">实验 · 浏览器内实时计算</p><h2>${esc(m.labTitle || '动手实验')}</h2></div><p>${inline(m.labNote || '自由实验不判分。单步、自动播放、改参数都由真实引擎重新计算；可以导出本次运行记录。')}</p></div>
<div id="lab-root" tabindex="-1"><p class="muted">正在载入实验…（需要通过 HTTP 打开页面；直接双击 HTML 时浏览器会阻止模块脚本。）</p></div>
</div></section>

<section class="section" id="challenges"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">挑战 · 由易到难</p><h2>分组挑战</h2></div><p>类别写在方括号里，难度单独标注。答案由引擎或明确规则判定；看答案不扣分，记录会如实区分。</p></div>
<p class="ch-guide">第一次用？先读<a href="${rel}guide/index.html">如何挑战</a>：读任务 → 预测 → 操作 → 提交 → 看解释 → 再试。${m.challengeTip ? inline(m.challengeTip) : ''}</p>
<div class="ch-list" id="challenge-root"><p class="muted">正在载入挑战…</p></div>
</div></section>

<section class="section" id="python"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">Python 实现轨道 · 可选</p><h2>${esc(py.title)}</h2></div><p>网页基础轨道不需要 Python。下载后在任意空目录运行；只用标准库${py.optional ? `（${esc(py.optional)}）` : ''}。</p></div>
<div class="grid-2"><div class="prose">${render(py.md)}</div>
<div><div class="py-files"><div><code>starter.py</code><br>起始代码：留有 TODO</div><div><code>check.py</code><br>检查器：未完成报 INCOMPLETE，不算 PASS</div><div><code>reference.py</code><br>参考实现：卡住时再看</div><div><code>fixtures/</code><br>本章例子的 JSON</div><div><code>README.md</code><br>任务、两级提示与样例</div></div>
<p><a class="btn primary" href="${rel}downloads/${m.moduleId}-python.zip" download>下载练习包（.zip）</a></p>
<pre><code>python3 check.py              # 检查你的 starter.py
python3 check.py reference.py # 看参考实现全部通过</code></pre></div></div>
</div></section>

<section class="section" id="mistakes"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">常见错误与局限</p><h2>容易错在哪里</h2></div><p>每条都给错误结果、错因、反例和修正；反例的数值都由测试复算。</p></div>
<div class="mistakes">${mistakes}</div>
<div class="prose" style="margin-top:26px"><h3>适用范围与局限</h3>${render(m.limits)}</div>
</div></section>

<section class="section" id="sources"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">资料与原作者</p><h2>来源</h2></div><p>本模块在统一课程中重写了讲解、引擎与媒体；原作的贡献在此署名，未复制无许可的源代码或音轨。</p></div>
<div class="grid-2"><div class="prose">
<h3 style="margin-top:0">原作者与保留的贡献</h3>
<p><strong>${esc(c.student.name)}</strong> · <a href="${c.student.website}">原网站</a> · <a href="${c.student.repository}">${c.student.repository.includes('/user-attachments/') ? 'Issue 附件' : '原仓库'}</a>${c.student.commit ? `（固定 <code>${c.student.commit.slice(0, 7)}</code>）` : ''}</p>
<ul>${c.kept.map(k => `<li>${inline(k)}</li>`).join('')}</ul>
<p class="small muted">${inline(c.licenseNote)}</p>
</div><div class="prose">
<h3 style="margin-top:0">来源映射</h3>
<table><tbody><tr><th>本课程</th><td>${esc(m.display)} · <code>${m.moduleId}</code></td></tr><tr><th>提交</th><td><a href="${m.sourceIssue.url}">Issue #${m.sourceIssue.number}</a>（${esc(m.sourceIssue.title)}）</td></tr><tr><th>教师目录</th><td>${esc(m.teacherFolder)}</td></tr><tr><th>状态</th><td>${m.teacherMappingStatus === 'pending' ? '待教师确认' : '已核对'}</td></tr></tbody></table>
<h3>参考文献</h3><ul>${c.references.map(r => `<li>${inline(r)}</li>`).join('')}</ul>
<p><a href="${rel}data/${m.moduleId}/crosswalk.json">本模块 crosswalk（目标 → 讲解 → 影片 → 课件 → 实验 → 挑战 → Python）</a> · <a href="${rel}downloads/${m.moduleId}-outline.md">Markdown 大纲</a></p>
</div></div>
</div></section>
</main>`;
  return shell({ title: `${m.display} ${m.title} · Learning Clustering`, rel, body, description: m.description,
    scripts: `<script type="module" src="./lab.js"></script>` });
}
function sectionTitle(m, id) {
  const top = { goals: '目标与问题', film: '影片', lesson: '讲解', slides: '课件', lab: '实验', challenges: '挑战', python: 'Python', mistakes: '易错' };
  if (top[id]) return top[id];
  const s = m.lesson.find(x => x.id === id); if (s) return s.title;
  const c = m.challengeMeta.find(x => `challenge-${x.id}` === id); if (c) return `[${c.type}] ${c.title}`;
  return id;
}

/* ---------------- home ---------------- */
function home() {
  const cards = modules.map(m => `<a class="mod-card" href="modules/${m.moduleId}/index.html" data-module="${m.moduleId}">
<span class="num">${esc(m.display)}</span><h3>${esc(m.title)}</h3><p>${inline(m.cardText)}</p>
<div class="meta">${m.teacherMappingStatus === 'pending' ? '<span class="tag warn">目录对应待确认</span>' : ''}<span class="tag">${esc(m.credits.student.name)}</span><span class="tag">影片 ${filmDuration(m)}</span></div>
<div class="bar" aria-hidden="true"><i></i></div><span class="small muted progress-text"></span></a>`).join('');
  const body = `<main id="main">
<section class="wrap hero"><div>
<p class="eyebrow">Learning Clustering · Clustering for EDA</p>
<h1>连接与分组</h1>
<p class="lead">芯片里成千上万个单元彼此连线。把联系紧密的单元放在一起，跨组的连线就少、短、快。八个模块从“怎么给一对单元打分”走到“怎样分组才让关键路径最快”。</p>
<div class="btn-row"><a class="btn primary" href="modules/m02-affinity-metrics/index.html">从 Module 02 开始</a><a class="btn" href="foundations/index.html">先看基础速查</a><a class="btn quiet" href="progress/index.html">我的学习记录</a></div>
</div>
<figure style="margin:0"><svg viewBox="0 0 420 300" role="img" aria-label="五个节点 A 到 E 的示例图，ABC 与 DE 两组之间只有权重 3 的连线被切开">
<rect width="420" height="300" rx="10" fill="#071c22"/>
<g stroke="#5d7c80" stroke-width="2.5"><line x1="80" y1="70" x2="210" y2="58"/><line x1="80" y1="70" x2="160" y2="160"/><line x1="210" y1="58" x2="160" y2="160"/><line x1="300" y1="220" x2="150" y2="250"/></g>
<g stroke="#db7b72" stroke-width="2.5" stroke-dasharray="7 5"><line x1="160" y1="160" x2="300" y2="220"/><line x1="160" y1="160" x2="150" y2="250"/></g>
<g font-family="Noto Sans SC Course, sans-serif" font-size="14" font-weight="600" fill="#d9e4e1"><text x="140" y="56">5</text><text x="108" y="125">1</text><text x="192" y="112">4</text><text x="236" y="186">2</text><text x="160" y="212">1</text><text x="226" y="250">5</text></g>
<g font-family="Noto Sans SC Course, sans-serif" font-size="17" font-weight="700" text-anchor="middle"><circle cx="80" cy="70" r="20" fill="#77cdbb"/><text x="80" y="76">A</text><circle cx="210" cy="58" r="20" fill="#77cdbb"/><text x="210" y="64">B</text><circle cx="160" cy="160" r="20" fill="#77cdbb"/><text x="160" y="166">C</text><circle cx="300" cy="220" r="20" fill="#8fb1e6"/><text x="300" y="226">D</text><circle cx="150" cy="250" r="20" fill="#8fb1e6"/><text x="150" y="256">E</text></g>
<text x="210" y="290" text-anchor="middle" font-family="Noto Sans SC Course, sans-serif" font-size="13" fill="#bcd2d0">课程公共图 G01：ABC | DE 只切断 2+1 = 3</text></svg></figure>
</section>
<section class="section"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">学习路线</p><h2>八个模块</h2></div><p>前三章讲评分与合并，LP 与谱方法给出两种产生初始分组的机制，KL/FM 改进已有分组，RW 把目标换成延迟。每章可以单独打开。</p></div>
<div class="route">${cards}</div>
<p class="route-legend">编号沿用提交顺序（Issue #1–#8 对应 Module 02–09）。Module 09 的提交主题是 Rajaraman–Wong；教师课程目录中的 Lab 09 是 Multilevel，对应关系尚待教师确认，课程不会把两者混为一谈。</p>
</div></section>
<section class="section" id="synthesis"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">综合对比</p><h2>同一张五节点图，七种不同的操作</h2></div><p>Module 02–08 都用到课程公共图 G01，但每一章学的操作不同；Module 09 换成有向延迟模型，不使用这张图。</p></div>
${render(read(path.join(CONTENT, 'synthesis.md')))}
</div></section>
</main>`;
  return shell({ title: 'Learning Clustering · 连接与分组', rel: '', active: 'home', body, scripts: `<script type="module" src="assets/home.js"></script>` });
}

/* ---------------- simple pages ---------------- */
function simplePage(dir, active, title, mdFile, extraScript = '') {
  const md = read(path.join(CONTENT, mdFile));
  const body = `<main id="main"><section class="section"><div class="wrap"><div class="prose">${render(md)}</div></div></section></main>`;
  write(path.join(SITE, dir, 'index.html'), shell({ title: `${title} · Learning Clustering`, rel: '../', active, body, scripts: extraScript }));
}
function glossaryPage() {
  const rows = glossary.terms.map(t => `<tr id="g-${t.id}"><td>${esc(t.zh)}<br><span class="small muted">${esc(t.en)}</span></td><td>${inline(t.meaning)}</td><td>${inline(t.notConfuse)}</td><td>${t.modules.map(id => { const m = modules.find(x => x.moduleId === id); return `<a href="../modules/${id}/index.html">${m ? m.display.replace('Module ', 'M') : id}</a>`; }).join(' ')}</td></tr>`).join('');
  const body = `<main id="main"><section class="section"><div class="wrap">
<p class="eyebrow">术语表</p><h1>统一术语与符号</h1>
<p class="muted" style="max-width:760px">每个术语在首次相关的模块中展开解释；这里给统一的中文名、英文名和“不能混淆”的提醒。同一个字母在不同模块可能表示不同的东西（例如谱方法的度矩阵 D 与 RW 的跨簇延迟 D）。</p>
<div style="overflow-x:auto"><table class="glossary-table"><thead><tr><th>术语</th><th>含义</th><th>不能混淆</th><th>首次展开</th></tr></thead><tbody>${rows}</tbody></table></div>
<div class="prose" style="margin-top:28px">${render(glossary.pronunciationMd)}</div>
</div></section></main>`;
  write(path.join(SITE, 'glossary', 'index.html'), shell({ title: '术语表 · Learning Clustering', rel: '../', active: 'glossary', body }));
}

/* ---------------- compatibility entries for old teacher-directory Lab paths ---------------- */
function compat() {
  for (const m of modules) {
    if (!m.compatSlug) continue; // M09 deliberately has none: RW must not take over the multilevel path
    write(path.join(SITE, 'labs', m.compatSlug, 'index.html'), `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(m.display)} ${esc(m.title)}</title><meta http-equiv="refresh" content="0; url=../../modules/${m.moduleId}/index.html"><link rel="canonical" href="../../modules/${m.moduleId}/index.html"></head><body><p>旧路径 labs/${esc(m.compatSlug)}/ 已整合为 <a href="../../modules/${m.moduleId}/index.html">${esc(m.display)} ${esc(m.title)}</a>。</p></body></html>\n`);
  }
}

/* ---------------- crosswalk ---------------- */
function crosswalk(m) {
  const cw = readJSON(path.join(CONTENT, 'modules', m.moduleId, 'crosswalk.json'));
  // Fill in actual video chapter times and slide numbers from the rendered assets (never typed by hand).
  const chapters = m.film.status === 'ready' ? (m.film.films || [m.film]).flatMap((f, fi) => (f.chapters || []).map(c => ({ ...c, film: f.id || fi }))) : [];
  for (const o of cw.objectives) {
    o.video = (o.sceneIds || []).map(sid => { const c = chapters.find(x => x.sceneId === sid); return c ? { sceneId: sid, film: c.film, start: c.t } : { sceneId: sid, status: m.film.status === 'ready' ? 'scene-not-a-chapter' : 'planned' }; });
    o.slides = (o.slideIds || []).map(sid => { const s = m.deck.slides?.find(x => x.slideId === sid); return s ? { slideId: sid, page: s.pageNumber } : { slideId: sid, status: 'planned' }; });
  }
  cw.contentVersion = course.contentVersion; cw.generated = new Date().toISOString().slice(0, 10);
  write(path.join(SITE, 'data', m.moduleId, 'crosswalk.json'), JSON.stringify(cw, null, 2));
  // Markdown outline as a download (T09)
  if (m.outlineMd) write(path.join(SITE, 'downloads', `${m.moduleId}-outline.md`), read(path.join(CONTENT, 'modules', m.moduleId, 'module.md')));
}

modules.forEach((m, i) => { write(path.join(SITE, 'modules', m.moduleId, 'index.html'), modulePage(m, i)); crosswalk(m); });
write(path.join(SITE, 'index.html'), home());
simplePage('foundations', 'foundations', '基础速查', 'foundations.md');
simplePage('guide', 'guide', '如何挑战', 'guide.md');
simplePage('credits', 'credits', '资源与贡献', 'credits.md');
simplePage('progress', 'progress', '学习记录', 'progress.md', '<script type="module" src="../assets/progress.js"></script>');
glossaryPage();
compat();
// 404 is served for any missing path, at any depth, so it must not rely on relative links.
write(path.join(SITE, '404.html'), `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>页面不存在 · Learning Clustering</title>
<style>body{margin:0;font:17px/1.75 -apple-system,"PingFang SC","Hiragino Sans GB",sans-serif;background:#f3efe6;color:#1c2421}main{max-width:720px;margin:12vh auto;padding:0 20px}h1{font-weight:700}a{color:#0f6b5c}</style></head>
<body><main><h1>找不到这个页面</h1><p>地址可能已变更。所有模块都在 <a id="home" href="/">课程首页</a>。</p><p>如果你来自教师原课程的 Multilevel（Lab 09）链接：本课程的 Module 09 是另一份提交（Rajaraman–Wong 延迟导向聚类），对应关系待教师确认，它不替代 Multilevel。</p></main>
<script>/* GitHub Pages project sites live under /<repo>/ */var p=location.pathname.split('/').filter(Boolean);if(location.hostname.endsWith('github.io')&&p.length)document.getElementById('home').href='/'+p[0]+'/';</script></body></html>
`);
console.log(`built ${modules.length} module pages + home, foundations, glossary, guide, credits, progress, 404, ${modules.filter(m => m.compatSlug).length} compatibility entries`);
