/**
 * VideoPlayer (real chapters from the render, transcript in sync, visible failure state) and
 * SlideViewer (stable slideId, "Module 0X · p/total", notes under the slide, thumbnails, search).
 */
import { h, $, fetchJSON } from './core.js';

const mmss = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;

export async function mountVideo(root, manifestUrl) {
  const m = await fetchJSON(manifestUrl, root);
  if (!m) return;
  const films = m.films || [m];
  root.replaceChildren();
  if (films.length > 1) {
    const tabs = h('div.btn-row', { role: 'tablist', style: 'margin-bottom:14px' });
    const area = h('div');
    films.forEach((f, i) => tabs.append(h('button.btn.small', { type: 'button', role: 'tab', 'aria-selected': i === 0, onclick: ev => {
      tabs.querySelectorAll('button').forEach(b => b.setAttribute('aria-selected', b === ev.currentTarget));
      renderFilm(area, f, new URL('.', manifestUrl));
    } }, f.title)));
    root.append(tabs, area);
    renderFilm(area, films[0], new URL('.', manifestUrl));
  } else renderFilm(root, films[0], new URL('.', manifestUrl));
}

function renderFilm(root, f, base) {
  if (f.status !== 'ready') {
    root.replaceChildren(h('div.film-layout', {}, h('div.film-frame', {}, h('div.film-missing', {}, h('strong', '影片尚未制作'), h('span', f.note || '本章影片处于计划状态；文字稿与课件已可使用。'))), h('div')));
    return;
  }
  const video = h('video', { controls: true, preload: 'metadata', playsinline: true, poster: f.poster ? new URL(f.poster, base) : null, 'aria-label': f.title },
    h('source', { src: new URL(f.src, base), type: 'video/mp4' }),
    f.vtt ? h('track', { kind: 'subtitles', srclang: 'zh', label: '中文（外挂字幕，画面已烧录，可不开）', src: new URL(f.vtt, base) }) : null);
  const frame = h('div.film-frame', {}, video);
  video.addEventListener('error', () => frame.replaceChildren(h('div.film-missing', {}, h('strong', '影片加载失败'), h('span', '网络中断或文件不可用。可刷新重试，或先阅读下方文字稿。'))), true);
  const chapterBtns = (f.chapters || []).map(c => h('button', { type: 'button', onclick: () => { video.currentTime = c.t; video.play?.().catch(() => {}); } }, h('span', mmss(c.t)), c.title));
  const lines = (f.transcript || []).map(l => h('p', { 'data-start': l.start, 'data-end': l.end }, h('time', mmss(l.start)), l.text));
  const transcript = h('div.transcript', { tabindex: '0', 'aria-label': '影片文字稿' }, lines);
  video.addEventListener('timeupdate', () => {
    const t = video.currentTime;
    chapterBtns.forEach((b, i) => b.classList.toggle('on', t >= f.chapters[i].t && (i === f.chapters.length - 1 || t < f.chapters[i + 1].t)));
    for (const p of lines) {
      const on = t >= +p.dataset.start && t < +p.dataset.end;
      if (on && !p.classList.contains('on')) { lines.forEach(q => q.classList.remove('on')); p.classList.add('on'); if (!transcript.matches(':hover')) p.scrollIntoView({ block: 'nearest' }); }
    }
  });
  root.replaceChildren(h('div.film-layout', {},
    h('div', {}, frame,
      h('div.film-meta', {}, h('span', `时长 ${mmss(f.duration)}`), h('span', '中文字幕已烧录 · 无配音'), f.music ? h('span', `配乐：${f.music}`) : null,
        h('a', { href: new URL(f.src, base), download: '' }, '下载 MP4'), f.vtt ? h('a', { href: new URL(f.vtt, base), download: '' }, 'WebVTT') : null),
      h('details', {}, h('summary', { style: 'cursor:pointer;margin-top:12px;color:var(--c-muted)' }, '展开全文字稿'), transcript)),
    h('nav.chapters', { 'aria-label': '影片章节' }, h('h3', '章节'), chapterBtns, f.why ? h('p.small.muted', { style: 'margin-top:12px' }, f.why) : null)));
}

export async function mountSlides(root, url, moduleLabel) {
  const deck = await fetchJSON(url, root);
  if (!deck) return;
  if (deck.status !== 'ready') { root.replaceChildren(h('p.notice', '课件尚在制作中。')); return; }
  const base = new URL('.', url);
  let i = 0;
  const img = h('img', { alt: '' });
  const pageno = h('span.pageno', { 'aria-live': 'polite' });
  const title = h('strong');
  const notes = h('div.slide-notes', { 'aria-live': 'polite' });
  const prev = h('button.btn.small', { type: 'button', onclick: () => go(i - 1) }, '‹ 上一页');
  const next = h('button.btn.small', { type: 'button', onclick: () => go(i + 1) }, '下一页 ›');
  const thumbs = h('div.slide-thumbs', { role: 'tablist', 'aria-label': '课件页' }, deck.slides.map((s, k) =>
    h('button', { type: 'button', role: 'tab', onclick: () => go(k), 'aria-label': `第 ${s.pageNumber} 页：${s.title}` }, h('img', { src: new URL(s.thumb || s.image, base), alt: '', loading: 'lazy' }), h('span', `p${s.pageNumber}`))));
  const search = h('input', { type: 'search', placeholder: '在讲稿中搜索', 'aria-label': '在课件讲稿中搜索', style: 'min-height:32px;padding:3px 8px;border:1px solid var(--line);border-radius:6px' });
  const results = h('div.small');
  search.addEventListener('input', () => {
    const q = search.value.trim();
    if (!q) { results.replaceChildren(); return; }
    const hits = deck.slides.filter(s => (s.title + s.transcript).includes(q));
    results.replaceChildren(hits.length ? h('span', '出现在：') : h('span', '没有找到'), ...hits.map(s => h('button.btn.quiet.small', { type: 'button', onclick: () => go(s.pageNumber - 1) }, `p${s.pageNumber}`)));
  });
  const stage = h('div.slide-stage', { tabindex: '0', 'aria-label': '课件，左右方向键翻页' }, img);
  stage.addEventListener('keydown', ev => { if (ev.key === 'ArrowRight') { ev.preventDefault(); go(i + 1); } if (ev.key === 'ArrowLeft') { ev.preventDefault(); go(i - 1); } });
  function go(k, initial = false) {
    i = Math.max(0, Math.min(deck.slides.length - 1, k));
    const s = deck.slides[i];
    img.src = new URL(s.image, base); img.alt = s.alt || s.title;
    pageno.textContent = `${moduleLabel} · p${s.pageNumber}/${s.pageCount}`;
    title.textContent = s.title;
    notes.replaceChildren(h('h4', `第 ${s.pageNumber} 页讲稿`), ...s.transcript.split('\n').filter(Boolean).map(p => h('p', p)));
    prev.disabled = i === 0; next.disabled = i === deck.slides.length - 1;
    [...thumbs.children].forEach((b, j) => b.setAttribute('aria-current', j === i));
    // Deep link to the page being viewed, but leave the address alone while the page is still opening.
    if (!initial && (location.hash.startsWith('#slide-') || location.hash === '#slides')) history.replaceState(null, '', `#slide-${s.slideId}`);
  }
  root.replaceChildren(h('div.slides', {},
    h('div.slide-bar', {}, h('div', {}, pageno, ' ', title), h('div.btn-row', {}, prev, next)),
    stage, notes, thumbs),
    h('div.btn-row', { style: 'margin-top:12px' },
      deck.pdf ? h('a.btn', { href: new URL(deck.pdf, base), download: '' }, `下载 PDF（${deck.slides.length} 页）`) : null,
      deck.pptx ? h('a.btn', { href: new URL(deck.pptx, base), download: '' }, '下载可编辑 PPTX') : null,
      search, results),
    h('p.small.muted', { style: 'margin-top:8px' }, deck.aspectNote || ''),
    deck.pptx ? h('p.small.muted', {}, 'PPTX 使用免费字体 Noto Sans SC（SIL OFL 1.1）；电脑上没有这款字体时，PowerPoint 会换用其他字体。可从 ',
      h('a', { href: 'https://fonts.google.com/noto/specimen/Noto+Sans+SC', rel: 'noopener' }, 'Google Fonts'), ' 免费安装。PDF 已内嵌字体。') : null);
  const fromHash = () => {
    const want = location.hash.match(/^#slide-(.+)$/);
    return want ? deck.slides.findIndex(s => s.slideId === decodeURIComponent(want[1])) : -1;
  };
  go(Math.max(0, fromHash()), true);
  // A slide link followed on the same page (e.g. from the crosswalk) changes only the hash.
  addEventListener('hashchange', () => {
    const k = fromHash();
    if (k >= 0 && k !== i) { go(k, true); root.closest('section')?.scrollIntoView({ behavior: 'instant' }); }
  });
}
