// Static checks of the built site: scope, naming, links, media, slides, crosswalk and teacher-feedback hooks.
// Run after `scripts/build.sh` (and after rendering media/slides).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SITE = path.join(ROOT, 'site');
const read = p => fs.readFileSync(path.join(SITE, p), 'utf8');
const exists = p => fs.existsSync(path.join(SITE, p));
const course = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/course.json'), 'utf8'));
const IDS = course.modules;

// GitHub Pages is case-sensitive while macOS usually is not: compare every path segment exactly.
function existsExact(p) {
  const rel = path.relative(SITE, p);
  if (rel.startsWith('..')) return fs.existsSync(p);
  let cur = SITE;
  for (const seg of rel.split(path.sep).filter(Boolean)) {
    if (!fs.existsSync(cur) || !fs.statSync(cur).isDirectory() || !fs.readdirSync(cur).includes(seg)) return false;
    cur = path.join(cur, seg);
  }
  return true;
}

function htmlFiles(dir = SITE, out = []) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) htmlFiles(p, out);
    else if (f.endsWith('.html')) out.push(p);
  }
  return out;
}

test('scope: exactly the eight closed Clustering submissions, Module 02–09', () => {
  assert.deepEqual(IDS, ['m02-affinity-metrics', 'm03-greedy-pair-merge', 'm04-size-constrained-agglomerative', 'm05-label-propagation',
    'm06-spectral-bisection', 'm07-kernighan-lin', 'm08-fiduccia-mattheyses', 'm09-rajaraman-wong']);
  const home = read('index.html');
  assert.equal((home.match(/class="mod-card"/g) || []).length, 8);
  for (let n = 2; n <= 9; n++) assert.ok(home.includes(`Module 0${n}`));
  assert.ok(!/Module (01|1[0-4])\b/.test(home), 'no extra numbered modules');
  assert.ok(!/Partitioning/.test(home));
});

test('T01: learners see "Module", Lab/Lesson appear only as source mapping', () => {
  for (const f of htmlFiles()) {
    if (f.includes('/labs/')) continue; // compatibility stubs mention the old path on purpose
    const visible = fs.readFileSync(f, 'utf8').replace(/<script[\s\S]*?<\/script>/g, '').replace(/<[^>]+>/g, ' ');
    const lines = visible.split(/[。\n]/).filter(l => /\bLab ?0\d\b/.test(l));
    for (const l of lines) assert.ok(/教师|目录|来源|映射|旧|Lesson|原课程|Issue|实现|仓库|teacher|catalogue|source|mapping|original|repository/i.test(l), `“Lab” used as a learning unit in ${path.relative(SITE, f)}: ${l.trim().slice(0, 80)}`);
  }
});

test('M09: mapping pending is visible, Multilevel path is not redirected to RW', () => {
  const p = read('modules/m09-rajaraman-wong/index.html');
  assert.ok(p.includes('教师目录对应待确认') && p.includes('Multilevel'));
  assert.ok(!exists('labs/multilevel-clustering/index.html'));
  assert.ok(read('index.html').includes('对应关系尚待教师确认'));
  for (const slug of ['affinity-metrics', 'greedy-pair-merge', 'size-constrained-agglomerative', 'label-propagation', 'spectral-bisection', 'kernighan-lin', 'fiduccia-mattheyses'])
    assert.ok(exists(`labs/${slug}/index.html`), `compat entry ${slug}`);
});

test('every relative link and asset in the built pages resolves', () => {
  const bad = [];
  for (const f of htmlFiles()) {
    const html = fs.readFileSync(f, 'utf8');
    for (const m of html.matchAll(/(?:href|src)="([^"#:]+)(#[^"]*)?"/g)) {
      const url = m[1];
      if (!url || url.startsWith('data:') || url.startsWith('/')) continue;
      const target = path.resolve(path.dirname(f), url);
      if (!existsExact(target)) bad.push(`${path.relative(SITE, f)} → ${url}`);
    }
  }
  assert.deepEqual(bad, []);
});

test('no external CDN or font service; no absolute root paths in pages', () => {
  for (const f of htmlFiles()) {
    const html = fs.readFileSync(f, 'utf8');
    const assets = [...html.matchAll(/<(?:script|link|img|video|source|track|iframe)\b[^>]*(?:src|href)="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(assets.filter(u => /^(https?:)?\/\//.test(u)), [], `external asset in ${path.relative(SITE, f)}`);
    if (!f.endsWith('404.html')) assert.ok(!/(href|src)="\/(?!\/)/.test(html), `root-absolute path in ${path.relative(SITE, f)}`);
  }
});

for (const id of IDS) {
  test(`${id}: page sections, problem statement, media, slides, crosswalk`, () => {
    const page = read(`modules/${id}/index.html`);
    for (const s of ['goals', 'film', 'lesson', 'slides', 'lab', 'challenges', 'python', 'mistakes', 'sources']) assert.ok(page.includes(`id="${s}"`), `section ${s}`);
    for (const k of ['输入', '输出', '目标', '约束', '假设', '停止']) assert.ok(page.includes(`<b>${k}`), `problem field ${k}`);   // T05/T19
    assert.ok(page.includes('class="pseudo"'), 'pseudocode with line notes');                                                    // T22
    assert.ok((page.match(/class="term"/g) || []).length >= 2, 'terms introduced');                                              // T24
    assert.ok((page.match(/class="mistake"/g) || []).length >= 3, 'common mistakes');                                            // T07
    const film = JSON.parse(read(`media/${id}/film.json`));
    const films = film.films || [film];
    for (const f of films) {
      assert.equal(f.status, 'ready');
      assert.ok(exists(`media/${id}/${f.src}`) && exists(`media/${id}/${f.vtt}`) && exists(`media/${id}/${f.poster}`));
      assert.equal(f.readingViolations, 0, 'every caption stays at least its reading time');                                     // T14
      assert.ok(f.chapters.length >= 3 && f.chapters.every((c, i) => i === 0 || c.t > f.chapters[i - 1].t));
      const vtt = read(`media/${id}/${f.vtt}`);
      assert.ok(vtt.startsWith('WEBVTT') && (vtt.match(/-->/g) || []).length === f.transcript.length);
    }
    const deck = JSON.parse(read(`slides/${id}/slides.json`));
    assert.equal(deck.status, 'ready');
    deck.slides.forEach((s, i) => { assert.equal(s.pageNumber, i + 1); assert.equal(s.pageCount, deck.slides.length); assert.ok(s.transcript.length > 20); assert.ok(exists(`slides/${id}/${s.image}`)); }); // T03/T21
    assert.ok(exists(`slides/${id}/${deck.pdf}`) && exists(`slides/${id}/${deck.pptx}`));
    const cw = JSON.parse(read(`data/${id}/crosswalk.json`));
    const m = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/modules', id, 'module.json'), 'utf8'));
    assert.deepEqual(cw.objectives.map(o => o.id), m.objectives.map(o => o.id), 'crosswalk covers every objective');
    const sceneIds = new Set(films.flatMap(f => f.scenes.map(s => s.sceneId))), slideIds = new Set(deck.slides.map(s => s.slideId));
    for (const o of cw.objectives) {
      assert.ok(o.sections.length, `${o.id} has a lesson section`);
      for (const s of o.sceneIds) assert.ok(sceneIds.has(s), `${o.id}: scene ${s} exists in the rendered film`);
      for (const s of o.slideIds) assert.ok(slideIds.has(s), `${o.id}: slide ${s} exists`);
      for (const sec of o.sections) assert.ok(page.includes(`id="${sec}"`), `${o.id}: section ${sec} on the page`);
    }
    assert.ok(exists(`downloads/${id}-python.zip`) && exists(`downloads/${id}-outline.md`));                                     // T23/T09
  });
}

test('T08/T16: challenges carry [category] titles, separate difficulty, ordered easy → hard', () => {
  const order = { Intro: 0, Practice: 1, Stretch: 2 };
  for (const id of IDS) {
    const meta = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/modules', id, 'challenges.json'), 'utf8'));
    assert.ok(meta.length >= 4);
    meta.forEach((c, i) => { assert.ok(c.type && c.difficulty && c.objectiveId); if (i) assert.ok(order[c.difficulty] >= order[meta[i - 1].difficulty]); });
    assert.ok(new Set(meta.map(c => c.type)).size >= 3, `${id}: several categories`);
  }
});

test('T17: the spring analogy appears only in Module 06, labelled as an analogy', () => {
  for (const id of IDS) {
    const page = read(`modules/${id}/index.html`).replace(/<[^>]+>/g, '');
    const has = page.includes('弹簧');
    if (id === 'm06-spectral-bisection') assert.ok(has && page.includes('类比'));
    else assert.ok(!has || page.includes('不使用弹簧'), `${id} mentions springs`);
  }
});

test('GitHub Pages: CSS url() targets exist with exact case; bundled font and its licence ship with the site', () => {
  const css = read('assets/course.css');
  const urls = [...css.matchAll(/url\(["']?([^"')]+)["']?\)/g)].map(m => m[1]).filter(u => !u.startsWith('data:'));
  assert.ok(urls.length >= 2);
  for (const u of urls) assert.ok(existsExact(path.resolve(SITE, 'assets', u)), `css url ${u}`);
  assert.ok(/Noto Sans SC Course/.test(css.match(/--sans:[^;]+/)[0]));
  assert.ok(/Noto Serif SC Course/.test(css.match(/--display:[^;]+/)[0]));
  for (const face of ['noto-sans-sc', 'noto-serif-sc', 'newsreader', 'jetbrains-mono']) {
    const ofl = read(`assets/fonts/OFL-${face}.txt`);
    assert.ok(ofl.includes('SIL OPEN FONT LICENSE') && /Copyright/.test(ofl), face);
    assert.ok(!/Reserved Font Name/i.test(ofl.split('---')[0]), `${face}: subsetting is only allowed without a Reserved Font Name`);
  }
});

test('font subset covers the Chinese text of every page (the rest falls back to system fonts)', () => {
  const cov = JSON.parse(read('assets/fonts/coverage.json'));
  const kept = new Set(cov.kept), fallback = new Set(cov.fallback);
  const missing = new Set();
  for (const f of htmlFiles()) for (const ch of fs.readFileSync(f, 'utf8')) if (ch.codePointAt(0) > 0x7f && !kept.has(ch) && !fallback.has(ch) && /\S/.test(ch)) missing.add(ch);
  assert.deepEqual([...missing], [], 'run scripts/build-fonts.py after changing content');
  assert.ok([...'聚类簇贪心标签谱二分'].every(c => kept.has(c)));
});

test('GitHub Pages: no Jekyll processing, and every module page is reachable from the home page', () => {
  assert.ok(exists('.nojekyll'));
  const home = read('index.html');
  for (const id of IDS) assert.ok(home.includes(`modules/${id}/index.html`) || home.includes(`modules/${id}/`), id);
});
