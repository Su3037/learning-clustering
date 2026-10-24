// Progress page: table, export, validated import, clear.
import { h, loadProgress, saveProgress, exportProgress, importProgress, fetchJSON, storageAvailable, L } from './core.js';
const root = document.getElementById('progress-root');
const reg = await fetchJSON(new URL('../data/registry.json', import.meta.url), root);
const known = reg ? Object.fromEntries(reg.modules.map(m => [m.moduleId, m.challenges])) : null;
const label = { solved: L('独立完成', 'Solved on your own'), 'solved-after-answer': L('看过答案后完成', 'Solved after the answer'), attempted: L('尝试中', 'In progress') };
function paint() {
  if (!reg) return;
  const p = loadProgress();
  root.replaceChildren(
    storageAvailable() ? '' : h('p.notice', L('本浏览器禁止本地存储：记录只在本页打开期间有效，请及时导出。', 'This browser blocks local storage: your record lasts only while this page is open, so export it.')),
    h('table.progress-table', {}, h('thead', {}, h('tr', {}, h('th', L('模块', 'Module')), h('th', label.solved), h('th', label['solved-after-answer']), h('th', label.attempted), h('th', L('未开始', 'Not started')))),
      h('tbody', {}, reg.modules.map(m => {
        const ch = p.modules[m.moduleId]?.challenges || {};
        const n = s => m.challenges.filter(c => ch[c]?.status === s).length;
        return h('tr', {}, h('td', {}, h('a', { href: `../modules/${m.moduleId}/index.html#challenges` }, `${m.display} ${L(m.title, m.titleEn)}`)),
          h('td', String(n('solved'))), h('td', String(n('solved-after-answer'))), h('td', String(n('attempted'))), h('td', String(m.challenges.length - n('solved') - n('solved-after-answer') - n('attempted'))));
      }))),
    h('p.small.muted', p.savedAt ? L(`最后保存：${new Date(p.savedAt).toLocaleString('zh-CN')}`, `Last saved: ${new Date(p.savedAt).toLocaleString('en')}`) : L('还没有记录。', 'Nothing recorded yet.')));
}
paint();
document.getElementById('export').addEventListener('click', exportProgress);
const msg = document.getElementById('import-msg');
document.getElementById('import').addEventListener('change', async ev => {
  const f = ev.target.files[0]; if (!f) return;
  const r = await importProgress(f, known);
  msg.textContent = r.ok ? L('导入成功。', 'Imported.') : L('没有导入：', 'Not imported: ') + r.errors.slice(0, 4).join(L('；', '; ')) + (r.errors.length > 4 ? ' …' : '');
  ev.target.value = ''; paint();
});
document.getElementById('clear').addEventListener('click', () => {
  if (!confirm(L('清除这台设备上的全部挑战记录？建议先导出。', 'Clear every challenge record on this device? Export first if you want a copy.'))) return;
  const p = loadProgress(); p.modules = {}; saveProgress(p); paint(); msg.textContent = L('已清除。', 'Cleared.');
});
