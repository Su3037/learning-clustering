/**
 * VideoPlayer (real chapters from the render, transcript in sync, visible failure state) and
 * SlideViewer (stable slideId, "Module 0X · p/total", notes under the slide, thumbnails, search).
 */
import { h, $, fetchJSON, L, LANG } from './core.js';

const mmss = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;

const KINDS = {
  popular: [L('科普', 'Popular science'), L('从生活里的问题讲起，适合第一次接触', 'Starts from an everyday problem; good for a first look')],
  concise: [L('精讲', 'Concise'), L('只讲必须掌握的内容', 'Only what you must know')],
  advanced: [L('进阶', 'Advanced'), L('为什么成立、什么时候失效、真实用法', 'Why it works, when it fails, how it is used')],
  lab: [L('实验演示', 'Walkthrough'), L('跟着做一遍实验和在线编程', 'Follow along with the lab and the code lab')]
};

// Schema 2 (one entry per film, one version per language) → the flat shape renderFilm expects.
function flatten(f) {
  if (!f.versions) return f;
  const v = f.versions[LANG] || f.versions.zh || Object.values(f.versions)[0];
  const title = typeof f.title === 'object' ? L(f.title.zh, f.title.en) : f.title;
  const music = f.music && typeof f.music === 'object' ? L(f.music.zh, f.music.en) : f.music;
  const why = f.why && typeof f.why === 'object' ? L(f.why.zh, f.why.en) : f.why;
  const tracks = Object.entries(f.versions).filter(([, x]) => x.vtt).map(([lg, x]) => ({ lang: lg, src: x.vtt }));
  const uniq = [...new Map(tracks.map(t => [t.src, t])).values()];
  return { ...v, id: f.id, kind: f.kind, status: f.status, title, music, why, tracks: uniq, external: f.external, captionsNote: v.captions };
}

export async function mountVideo(root, manifestUrl) {
  const m = await fetchJSON(manifestUrl, root);
  if (!m) return;
  const films = (m.films || [m]).map(flatten);
  const base = new URL('.', manifestUrl);
  root.replaceChildren();
  if (films.length > 1) {
    const area = h('div');
    const picker = h('div.film-picker', { role: 'tablist', 'aria-label': L('本章影片', 'Films in this chapter') });
    const pick = (i, focus) => {
      [...picker.children].forEach((b, j) => { b.setAttribute('aria-selected', j === i); b.tabIndex = j === i ? 0 : -1; });
      renderFilm(area, films[i], base);
      if (focus) picker.children[i].focus();
    };
    films.forEach((f, i) => {
      const kind = KINDS[f.kind];
      picker.append(h('button.film-card', { type: 'button', role: 'tab', 'aria-selected': i === 0, onclick: () => pick(i),
        onkeydown: ev => { if (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft') { ev.preventDefault(); pick((i + (ev.key === 'ArrowRight' ? 1 : films.length - 1)) % films.length, true); } } },
        f.poster ? h('img', { src: new URL(f.poster, base), alt: '', loading: 'lazy' }) : h('span.film-card-blank'),
        h('span.film-card-text', {},
          h('span.film-kind', kind ? kind[0] : (f.kind || L(`影片 ${i + 1}`, `Film ${i + 1}`))),
          h('strong', f.title),
          h('span.film-len', f.duration ? mmss(f.duration) : L('计划中', 'planned')))));
    });
    root.append(picker, area);
    pick(0);
  } else renderFilm(root, films[0], base);
}

function renderFilm(root, f, base) {
  if (f.status !== 'ready') {
    root.replaceChildren(h('div.film-layout', {}, h('div.film-frame', {}, h('div.film-missing', {}, h('strong', L('影片尚未制作', 'Film not made yet')), h('span', f.note || L('本章影片处于计划状态；文字稿与课件已可使用。', 'This film is still planned; the transcript and slides are available.')))), h('div')));
    return;
  }
  const video = h('video', { controls: true, preload: 'metadata', playsinline: true, poster: f.poster ? new URL(f.poster, base) : null, 'aria-label': f.title },
    h('source', { src: new URL(f.src, base), type: 'video/mp4' }),
    ...(f.tracks || (f.vtt ? [{ lang: 'zh', src: f.vtt }] : [])).map(t => h('track', { kind: 'subtitles', srclang: t.lang, label: t.lang === 'en' ? 'English' : '中文', src: new URL(t.src, base) })));
  const frame = h('div.film-frame', {}, video);
  video.addEventListener('error', () => frame.replaceChildren(h('div.film-missing', {}, h('strong', L('影片加载失败', 'The film failed to load')), h('span', L('网络中断或文件不可用。可刷新重试，或先阅读下方文字稿。', 'The network dropped or the file is unavailable. Reload to retry, or read the transcript below.')))), true);
  const chapterBtns = (f.chapters || []).map(c => h('button', { type: 'button', onclick: () => { video.currentTime = c.t; video.play?.().catch(() => {}); } }, h('span', mmss(c.t)), c.title));
  const lines = (f.transcript || []).map(l => h('p', { 'data-start': l.start, 'data-end': l.end }, h('time', mmss(l.start)), l.text));
  const transcript = h('div.transcript', { tabindex: '0', 'aria-label': L('影片文字稿', 'Film transcript') }, lines);
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
      h('div.film-meta', {}, h('span', L(`时长 ${mmss(f.duration)}`, `Length ${mmss(f.duration)}`)), h('span', f.captionsNote === 'en' ? L('英文字幕已烧录 · 无配音', 'English captions burned in · no narration') : f.captionsNote === 'zh+en' ? L('中英字幕已烧录 · 无配音', 'Chinese and English captions burned in · no narration') : L('中文字幕已烧录 · 无配音', 'Chinese captions burned in · no narration')), f.music ? h('span', L(`配乐：${f.music}`, `Music: ${f.music}`)) : null,
        h('a', { href: new URL(f.src, base), download: '' }, L('下载 MP4', 'Download MP4')), f.vtt ? h('a', { href: new URL(f.vtt, base), download: '' }, 'WebVTT') : null),
      f.kind && KINDS[f.kind] ? h('p.film-kind-note', {}, h('b', KINDS[f.kind][0]), ' · ', KINDS[f.kind][1]) : null,
      h('details', {}, h('summary', { style: 'cursor:pointer;margin-top:12px;color:var(--c-muted)' }, L('展开全文字稿', 'Show the full transcript')), transcript)),
    h('nav.chapters', { 'aria-label': L('影片章节', 'Film chapters') }, h('h3', L('章节', 'Chapters')), chapterBtns, f.why ? h('p.small.muted', { style: 'margin-top:12px' }, f.why) : null)));
}

export async function mountSlides(root, url, moduleLabel) {
  const deck = await fetchJSON(url, root);
  if (!deck) return;
  if (deck.status !== 'ready') { root.replaceChildren(h('p.notice', L('课件尚在制作中。', 'The slides are still being made.'))); return; }
  const base = new URL('.', url);
  let i = 0;
  const img = h('img', { alt: '' });
  const pageno = h('span.pageno', { 'aria-live': 'polite' });
  const title = h('strong');
  const notes = h('div.slide-notes', { 'aria-live': 'polite' });
  const prev = h('button.btn.small', { type: 'button', onclick: () => go(i - 1) }, L('‹ 上一页', '‹ Previous'));
  const next = h('button.btn.small', { type: 'button', onclick: () => go(i + 1) }, L('下一页 ›', 'Next ›'));
  const thumbs = h('div.slide-thumbs', { role: 'tablist', 'aria-label': L('课件页', 'Slide pages') }, deck.slides.map((s, k) =>
    h('button', { type: 'button', role: 'tab', onclick: () => go(k), 'aria-label': L(`第 ${s.pageNumber} 页：${s.title}`, `Page ${s.pageNumber}: ${s.title}`) }, h('img', { src: new URL(s.thumb || s.image, base), alt: '', loading: 'lazy' }), h('span', `p${s.pageNumber}`))));
  const search = h('input', { type: 'search', placeholder: L('在讲稿中搜索', 'Search the notes'), 'aria-label': L('在课件讲稿中搜索', 'Search the slide notes'), style: 'min-height:32px;padding:3px 8px;border:1px solid var(--line);border-radius:6px' });
  const results = h('div.small');
  search.addEventListener('input', () => {
    const q = search.value.trim();
    if (!q) { results.replaceChildren(); return; }
    const hits = deck.slides.filter(s => (s.title + s.transcript).includes(q));
    results.replaceChildren(hits.length ? h('span', L('出现在：', 'Found on: ')) : h('span', L('没有找到', 'Not found')), ...hits.map(s => h('button.btn.quiet.small', { type: 'button', onclick: () => go(s.pageNumber - 1) }, `p${s.pageNumber}`)));
  });
  const stage = h('div.slide-stage', { tabindex: '0', 'aria-label': L('课件，左右方向键翻页', 'Slides; use the arrow keys to turn pages') }, img);
  stage.addEventListener('keydown', ev => { if (ev.key === 'ArrowRight') { ev.preventDefault(); go(i + 1); } if (ev.key === 'ArrowLeft') { ev.preventDefault(); go(i - 1); } });
  function go(k, initial = false) {
    i = Math.max(0, Math.min(deck.slides.length - 1, k));
    const s = deck.slides[i];
    img.src = new URL(s.image, base); img.alt = s.alt || s.title;
    pageno.textContent = `${moduleLabel} · p${s.pageNumber}/${s.pageCount}`;
    title.textContent = s.title;
    notes.replaceChildren(h('h4', L(`第 ${s.pageNumber} 页讲稿`, `Notes for page ${s.pageNumber}`)), ...s.transcript.split('\n').filter(Boolean).map(p => h('p', p)));
    prev.disabled = i === 0; next.disabled = i === deck.slides.length - 1;
    [...thumbs.children].forEach((b, j) => b.setAttribute('aria-current', j === i));
    // Deep link to the page being viewed, but leave the address alone while the page is still opening.
    if (!initial && (location.hash.startsWith('#slide-') || location.hash === '#slides')) history.replaceState(null, '', `#slide-${s.slideId}`);
  }
  root.replaceChildren(h('div.slides', {},
    h('div.slide-bar', {}, h('div', {}, pageno, ' ', title), h('div.btn-row', {}, prev, next)),
    stage, notes, thumbs),
    h('div.btn-row', { style: 'margin-top:12px' },
      deck.pdf ? h('a.btn', { href: new URL(deck.pdf, base), download: '' }, L(`下载 PDF（${deck.slides.length} 页）`, `Download PDF (${deck.slides.length} pages)`)) : null,
      deck.pptx ? h('a.btn', { href: new URL(deck.pptx, base), download: '' }, L('下载可编辑 PPTX', 'Download editable PPTX')) : null,
      search, results),
    h('p.small.muted', { style: 'margin-top:8px' }, deck.aspectNote || ''),
    deck.pptx ? h('p.small.muted', {}, L('PPTX 使用免费字体 Noto Sans SC（SIL OFL 1.1）；电脑上没有这款字体时，PowerPoint 会换用其他字体。可从 ', 'The PPTX uses the free font Noto Sans SC (SIL OFL 1.1); without it PowerPoint substitutes another font. Install it free from '),
      h('a', { href: 'https://fonts.google.com/noto/specimen/Noto+Sans+SC', rel: 'noopener' }, 'Google Fonts'), L(' 免费安装。PDF 已内嵌字体。', '. The PDF embeds its fonts.')) : null);
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
