/**
 * ExperimentController (event player), TraceInspector (table view of the same events),
 * Pseudocode panel and run export. The player only moves an index over events that an
 * engine already computed; changing inputs means a new run (new runId), never a silent recompute.
 */
import { h, $, $$, download, reducedMotion, L } from './core.js';

let runCounter = 0;

export class Player {
  constructor(root, { onIndex, speed = 1100 } = {}) {
    this.root = root; this.onIndex = onIndex; this.events = []; this.i = 0; this.timer = null; this.speed = speed;
    this.btn = {
      reset: h('button.btn.small', { type: 'button', onclick: () => this.go(0) }, L('⟲ 重置', '⟲ Reset')),
      prev: h('button.btn.small', { type: 'button', onclick: () => this.go(this.i - 1), 'aria-label': L('上一步', 'Previous step') }, L('‹ 上一步', '‹ Back')),
      next: h('button.btn.small.primary', { type: 'button', onclick: () => this.go(this.i + 1), 'aria-label': L('下一步', 'Next step') }, L('下一步 ›', 'Step ›')),
      play: h('button.btn.small', { type: 'button', onclick: () => this.toggle() }, L('▶ 自动播放', '▶ Play')),
      end: h('button.btn.small', { type: 'button', onclick: () => this.go(this.events.length - 1) }, L('跳到结束 ⇥', 'To the end ⇥'))
    };
    this.pos = h('span.pos', { 'aria-live': 'polite' });
    root.replaceChildren(h('div.player', {}, Object.values(this.btn), this.pos));
    root.addEventListener('keydown', ev => {
      if (ev.target.matches('input,select,textarea')) return;
      if (ev.key === 'ArrowRight') { ev.preventDefault(); this.go(this.i + 1); }
      if (ev.key === 'ArrowLeft') { ev.preventDefault(); this.go(this.i - 1); }
    });
  }
  load(events, start = 0) { this.stop(); this.events = events; this.runId = ++runCounter; this.go(start); }
  go(i) {
    if (!this.events.length) { this.pos.textContent = L('没有事件', 'No events'); return; }
    this.i = Math.max(0, Math.min(this.events.length - 1, i));
    this.btn.prev.disabled = this.i === 0; this.btn.reset.disabled = this.i === 0;
    this.btn.next.disabled = this.btn.end.disabled = this.i === this.events.length - 1;
    this.pos.textContent = L(`事件 ${this.i + 1} / ${this.events.length}`, `Event ${this.i + 1} / ${this.events.length}`);
    this.onIndex?.(this.i, this.events[this.i], this.events);
    if (this.i === this.events.length - 1) this.stop();
  }
  toggle() { this.timer ? this.stop() : this.play(); }
  play() {
    if (this.i >= this.events.length - 1) this.go(0);
    this.btn.play.textContent = L('❚❚ 暂停', '❚❚ Pause');
    const tick = () => { this.go(this.i + 1); if (this.timer) this.timer = setTimeout(tick, reducedMotion() ? this.speed * 1.6 : this.speed); };
    this.timer = setTimeout(tick, this.speed);
  }
  stop() { clearTimeout(this.timer); this.timer = null; this.btn.play.textContent = L('▶ 自动播放', '▶ Play'); }
}

export class TraceInspector {
  /** columns: [{label, get(event)}] */
  constructor(root, { columns, onPick, title = L('逐步记录（表格视图）', 'Step-by-step log (table)') }) {
    this.columns = columns; this.onPick = onPick;
    this.body = h('tbody');
    root.replaceChildren(h('details.trace', {}, h('summary', title),
      h('div.table-scroll', {}, h('table', {}, h('thead', {}, h('tr', {}, h('th', '#'), columns.map(c => h('th', c.label)))), this.body))));
  }
  load(events) {
    this.body.replaceChildren(...events.map((e, i) => h('tr', { tabindex: '0', onclick: () => this.onPick?.(i), onkeydown: ev => { if (ev.key === 'Enter') this.onPick?.(i); } },
      h('td', String(i + 1)), this.columns.map(c => h('td', String(c.get(e) ?? ''))))));
  }
  mark(i) {
    $$('tr', this.body).forEach((tr, k) => tr.classList.toggle('on', k === i));
    const tr = this.body.children[i];
    if (tr && tr.closest('details')?.open) tr.scrollIntoView({ block: 'nearest' });
  }
}

/** Pseudocode block rendered by the build (ol > li[data-line]) plus an explanation pane. */
export class Pseudocode {
  constructor(root) {
    this.root = root; this.lines = $$('li[data-line]', root); this.explain = $('.explain', root);
    this.notes = Object.fromEntries(this.lines.map(li => [li.dataset.line, li.dataset.note || '']));
    this.lines.forEach(li => li.addEventListener('click', () => this.show([+li.dataset.line], '')));
    this.lines.forEach(li => { li.tabIndex = 0; li.addEventListener('keydown', ev => { if (ev.key === 'Enter') this.show([+li.dataset.line], ''); }); });
  }
  show(lines, context) {
    this.lines.forEach(li => li.classList.toggle('on', lines.includes(+li.dataset.line)));
    if (!this.explain) return;
    this.explain.replaceChildren(
      h('p', {}, h('span.line-no', L(`第 ${lines.join('、')} 行`, `Line${lines.length > 1 ? 's' : ''} ${lines.join(', ')}`)), context ? ' · ' + context : ''),
      ...lines.map(l => h('p', this.notes[l] || '')));
  }
}

export function exportRun(moduleId, payload) {
  const body = { moduleId, exportedAt: new Date().toISOString(), ...payload };
  download(new Blob([JSON.stringify(body, null, 2)], { type: 'application/json' }), `${moduleId}-run-${Date.now()}.json`);
}

export function metrics(root, items) {
  root.replaceChildren(...items.map(([label, value]) => h('div', {}, h('span', label), h('strong', String(value)))));
}
export function status(root, kind, text) {
  root.className = 'status ' + (kind || '');
  root.textContent = text;
}
/** A <select> + labelled control row. */
export function select(label, options, value, onchange) {
  const s = h('select', { onchange: () => onchange(s.value) }, options.map(([v, t]) => h('option', { value: v, selected: v === value }, t)));
  return h('label', {}, label, s);
}
export function numberInput(label, value, onchange, { min = 0, max = 99, step = 1, allowEmpty = false } = {}) {
  const i = h('input', { type: 'number', value: value ?? '', min, max, step, placeholder: allowEmpty ? L('不限', 'any') : '' });
  i.addEventListener('change', () => onchange(i.value === '' && allowEmpty ? null : Number(i.value)));
  return h('label', {}, label, i);
}
