/**
 * GraphView: one SVG renderer for every module. State is encoded with more than colour:
 * group tags under nodes, dashed red cut edges, dashed outlines for locked nodes, a gold ring
 * for the node in focus, and a red ring for blocked candidates.
 */
import { h, L } from './core.js';

export const PALETTE = ['#77cdbb', '#8fb1e6', '#d8bb78', '#c2a6e6', '#e39fb8', '#9fd27f', '#e8a06a', '#7fd0e0'];
const NS = 'http://www.w3.org/2000/svg';

function hull(points) {
  const p = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (p.length < 3) return p;
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cross(lo.at(-2), lo.at(-1), q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.reverse()) { while (up.length >= 2 && cross(up.at(-2), up.at(-1), q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}

export class GraphView {
  constructor(container, { graph, positions, width = 760, height = 500, directed = false, light = false, radius = 24, title = L('图', 'Graph'), onNodeClick = null, margin = 40 } = {}) {
    this.container = container; this.directed = directed; this.r = radius; this.onNodeClick = onNodeClick; this.title = title;
    this.setGraph(graph, positions, width, height, margin);
    this.svg = h('svg', { viewBox: `0 0 ${this.W} ${this.H}`, class: 'gv' + (light ? ' gv-light' : ''), role: 'img', 'aria-label': title });
    container.replaceChildren(this.svg);
  }
  setGraph(graph, positions, width = this.W, height = this.H, margin = 40) {
    this.graph = graph;
    const ids = graph.nodes.map(n => typeof n === 'string' ? n : n.id);
    this.ids = ids;
    this.edges = (graph.edges || []).map(e => Array.isArray(e) ? { u: e[0], v: e[1], w: e[2] } : { u: e.u ?? e.from, v: e.v ?? e.to, w: e.w });
    const pos = positions || circleLayout(ids, width, height);
    // Fit given coordinates into the box with a margin.
    const xs = ids.map(i => pos[i][0]), ys = ids.map(i => pos[i][1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const sx = (width - 2 * margin) / Math.max(1, maxX - minX), sy = (height - 2 * margin - 22) / Math.max(1, maxY - minY), s = Math.min(sx, sy, 1.6);
    const ox = (width - (maxX - minX) * s) / 2, oy = (height - 22 - (maxY - minY) * s) / 2;
    this.pos = Object.fromEntries(ids.map(i => [i, [ox + (pos[i][0] - minX) * s, oy + (pos[i][1] - minY) * s]]));
    this.W = width; this.H = height;
  }
  colorFor(key, order) {
    const i = order ? order.indexOf(key) : -1;
    return PALETTE[(i >= 0 ? i : Math.abs(hash(String(key)))) % PALETTE.length];
  }
  /** state: {groups:{id:key}, groupOrder, tags:{id:text}, cut:bool, highlight:[[u,v]], inside:[[u,v]],
   *  focus:[id], locked:[id], blocked:[id], hulls:[{members,label,color}], fills:{id:color}, edgeLabels:{key:text}, sideLabels:[text,text], summary } */
  render(state = {}) {
    const s = this.svg, groups = state.groups || {}, order = state.groupOrder || [...new Set(this.ids.map(i => groups[i]))].sort();
    s.replaceChildren();
    s.setAttribute('aria-label', state.summary || this.title);
    if (this.directed) {
      s.append(h('defs', {}, h('marker', { id: 'arrow', viewBox: '0 0 10 10', refX: '9', refY: '5', markerWidth: '7', markerHeight: '7', orient: 'auto-start-reverse' },
        h('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: '#8aa7a6' }))));
    }
    for (const hl of state.hulls || []) {
      const pts = hl.members.map(m => this.pos[m]).filter(Boolean);
      if (!pts.length) continue;
      const hp = hull(pts), color = hl.color || '#77cdbb';
      const d = hp.length === 1 ? `M ${hp[0][0] - 0.1} ${hp[0][1]} L ${hp[0][0] + 0.1} ${hp[0][1]}` : 'M ' + hp.map(p => p.join(' ')).join(' L ') + ' Z';
      s.append(h('g', { opacity: '.2' }, h('path', { d, fill: color, stroke: color, 'stroke-width': 2 * this.r + 22, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' })));
      if (hl.label) {
        const top = hp.reduce((a, b) => (b[1] < a[1] ? b : a)), bottom = hp.reduce((a, b) => (b[1] > a[1] ? b : a));
        const above = top[1] - this.r - 18 > 16;
        s.append(h('text', { x: above ? top[0] : bottom[0], y: above ? top[1] - this.r - 18 : Math.min(this.H - 6, bottom[1] + this.r + 30), 'text-anchor': 'middle', class: 'side-label', fill: color }, hl.label));
      }
    }
    const hiKey = new Set((state.highlight || []).map(([a, b]) => [a, b].sort().join('|')));
    const inKey = new Set((state.inside || []).map(([a, b]) => [a, b].sort().join('|')));
    for (const e of this.edges) {
      const [x1, y1] = this.pos[e.u], [x2, y2] = this.pos[e.v], key = [e.u, e.v].sort().join('|');
      const isCut = state.cut && groups[e.u] !== undefined && groups[e.u] !== groups[e.v];
      let cls = 'edge' + (isCut ? ' cut' : '') + (hiKey.has(key) ? ' hl' : '') + (inKey.has(key) ? ' inside' : '');
      let ax = x2, ay = y2;
      if (this.directed) { const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1; ax = x2 - dx / L * (this.r + 4); ay = y2 - dy / L * (this.r + 4); }
      const line = h('line', { x1, y1, x2: ax, y2: ay, class: cls, 'marker-end': this.directed ? 'url(#arrow)' : null });
      if (state.edgeStyle?.[key]) line.setAttribute('style', state.edgeStyle[key]);
      s.append(line);
      const label = state.edgeLabels?.[key] ?? (e.w !== undefined && !this.directed ? e.w : null);
      if (label !== null && label !== undefined && label !== '') {
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = y2 - y1, dy = x1 - x2, L = Math.hypot(dx, dy) || 1;
        s.append(h('text', { x: mx + dx / L * 13, y: my + dy / L * 13 + 5, 'text-anchor': 'middle', class: 'w' }, String(label)));
      }
    }
    const focus = new Set(state.focus || []), locked = new Set(state.locked || []), blocked = new Set(state.blocked || []);
    for (const id of this.ids) {
      const [x, y] = this.pos[id];
      const fill = state.fills?.[id] || (groups[id] !== undefined ? this.colorFor(groups[id], order) : '#a9bdb8');
      const g = h('g', { class: 'node' + (focus.has(id) ? ' focus' : '') + (locked.has(id) ? ' locked' : '') + (blocked.has(id) ? ' blocked' : ''), transform: `translate(${x} ${y})` },
        h('circle', { r: this.r, fill }), h('text', { 'text-anchor': 'middle', y: 6 }, id));
      const tag = state.tags?.[id];
      if (tag) g.append(h('text', { class: 'tag-text', 'text-anchor': 'middle', y: this.r + 18 }, tag));
      if (this.onNodeClick) {
        g.setAttribute('tabindex', '0'); g.setAttribute('role', 'button'); g.setAttribute('aria-label', L(`节点 ${id}${tag ? '，' + tag : ''}`, `Node ${id}${tag ? ', ' + tag : ''}`));
        g.style.cursor = 'pointer';
        g.addEventListener('click', () => this.onNodeClick(id));
        g.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); this.onNodeClick(id); } });
      }
      s.append(g);
    }
    if (state.sideLabels) {
      s.append(h('text', { x: 14, y: this.H - 8, class: 'side-label' }, state.sideLabels[0]));
      s.append(h('text', { x: this.W - 14, y: this.H - 8, class: 'side-label', 'text-anchor': 'end' }, state.sideLabels[1]));
    }
    if (state.caption) s.append(h('text', { x: this.W / 2, y: this.H - 8, class: 'side-label', 'text-anchor': 'middle' }, state.caption));
  }
}

function hash(s) { let x = 0; for (const c of s) x = (x * 31 + c.charCodeAt(0)) | 0; return x; }
export function circleLayout(ids, W = 760, H = 500) {
  const cx = W / 2, cy = H / 2 - 10, r = Math.min(W, H) / 2 - 70;
  return Object.fromEntries(ids.map((id, i) => [id, [cx + r * Math.cos(-Math.PI / 2 + 2 * Math.PI * i / ids.length), cy + r * Math.sin(-Math.PI / 2 + 2 * Math.PI * i / ids.length)]]));
}
export { NS };
