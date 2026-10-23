// Minimal, dependency-free Markdown → HTML for course-authored content (trusted input).
// Supports: ## {#id} headings, paragraphs, - / 1. lists, > blockquotes, pipe tables, ``` code,
// **bold**, *em*, `code`, [links](url), and course fences: pseudo, terms, callout, problem, html.
export const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
  s = esc(s)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) => `<a href="${u}"${/^https?:/.test(u) ? ' rel="noopener"' : ''}>${t}</a>`);
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(codes[+i])}</code>`);
}

function table(lines) {
  const rows = lines.map(l => l.trim().replace(/^\||\|$/g, '').split(/(?<!\\)\|/).map(c => c.trim().replace(/\\\|/g, '|')));
  const [head, , ...body] = rows;
  return `<table><thead><tr>${head.map(c => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${body.map(r => `<tr>${r.map(c => `<td>${inline(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

const fences = {
  pseudo(body, arg) {
    const rows = body.split('\n').filter(l => l.trim() !== '').map(l => { const [code, note = ''] = l.split('||'); return { code: code.replace(/\s+$/, ''), note: note.trim().replace(/\*\*/g, '') }; });
    return `<div class="pseudo" data-pseudo="${esc(arg || 'main')}"><ol aria-label="伪代码">${rows.map((r, i) => `<li data-line="${i + 1}" data-note="${esc(r.note)}">${esc(r.code)}</li>`).join('')}</ol><div class="explain"><p class="muted">点击任一行看解释；在实验中单步时，当前执行的行会自动高亮。</p></div></div>`;
  },
  terms(body) {
    const items = body.split('\n').filter(l => l.trim()).map(l => l.split('|').map(s => s.trim()));
    return `<div class="terms">${items.map(([zh, en, def]) => `<div class="term" id="term-${esc(en.toLowerCase().replace(/[^a-z0-9]+/g, '-'))}"><h4>${inline(zh)}</h4><span class="en">${esc(en)}</span><p>${inline(def)}</p></div>`).join('')}</div>`;
  },
  callout(body, arg) {
    const [kind = 'note', ...t] = (arg || 'note').split(' ');
    const title = t.join(' ');
    return `<div class="callout ${esc(kind)}">${title ? `<strong>${inline(title)}</strong>` : ''}${render(body)}</div>`;
  },
  html(body) { return body; }
};

export function render(src) {
  const lines = src.replace(/\r/g, '').split('\n');
  const out = [];
  let i = 0;
  const para = [];
  const flush = () => { if (para.length) { out.push(`<p>${inline(para.join(''))}</p>`); para.length = 0; } };
  while (i < lines.length) {
    const l = lines[i];
    const fence = l.match(/^```(\w+)?\s*(.*)$/);
    if (fence) {
      flush();
      const body = []; i++;
      while (i < lines.length && !lines[i].startsWith('```')) body.push(lines[i++]);
      i++;
      const kind = fence[1];
      out.push(fences[kind] ? fences[kind](body.join('\n'), fence[2]) : `<pre><code>${esc(body.join('\n'))}</code></pre>`);
      continue;
    }
    const hd = l.match(/^(#{2,4})\s+(?:\{#([\w-]+)\}\s*)?(.+)$/);
    if (hd) { flush(); const n = hd[1].length; out.push(`<h${n}${hd[2] ? ` id="${hd[2]}"` : ''}>${inline(hd[3])}</h${n}>`); i++; continue; }
    if (/^\s*\|.*\|\s*$/.test(l) && /^\s*\|[\s:-]+\|/.test(lines[i + 1] || '')) {
      flush(); const t = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) t.push(lines[i++]);
      out.push(table(t)); continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
      flush();
      const ordered = /^\s*\d+\./.test(l), items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ''); i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) item += lines[i++].trim();
        items.push(`<li>${inline(item)}</li>`);
      }
      out.push(ordered ? `<ol>${items.join('')}</ol>` : `<ul>${items.join('')}</ul>`); continue;
    }
    if (/^>\s?/.test(l)) {
      flush(); const q = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) q.push(lines[i++].replace(/^>\s?/, ''));
      out.push(`<blockquote class="callout">${render(q.join('\n'))}</blockquote>`); continue;
    }
    if (l.trim() === '') { flush(); i++; continue; }
    para.push(l.trim()); i++;
  }
  flush();
  return out.join('\n');
}

/** Split a lesson into sections at "## {#id} Title". */
export function sections(src) {
  const parts = [];
  let cur = null;
  for (const line of src.replace(/\r/g, '').split('\n')) {
    const m = line.match(/^##\s+\{#([\w-]+)\}\s*(.+)$/);
    if (m) { if (cur) parts.push(cur); cur = { id: m[1], title: m[2].trim(), body: [] }; continue; }
    if (cur) cur.body.push(line);
  }
  if (cur) parts.push(cur);
  return parts.map(p => ({ id: p.id, title: p.title, html: render(p.body.join('\n')), md: p.body.join('\n') }));
}
