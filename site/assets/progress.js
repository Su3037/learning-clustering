// Progress page: table, export, validated import, clear.
import { h, loadProgress, saveProgress, exportProgress, importProgress, fetchJSON, storageAvailable } from './core.js';
const root = document.getElementById('progress-root');
const reg = await fetchJSON(new URL('../data/registry.json', import.meta.url), root);
const known = reg ? Object.fromEntries(reg.modules.map(m => [m.moduleId, m.challenges])) : null;
const label = { solved: '独立完成', 'solved-after-answer': '看过答案后完成', attempted: '尝试中' };
function paint() {
  if (!reg) return;
  const p = loadProgress();
  root.replaceChildren(
    storageAvailable() ? '' : h('p.notice', '本浏览器禁止本地存储：记录只在本页打开期间有效，请及时导出。'),
    h('table.progress-table', {}, h('thead', {}, h('tr', {}, h('th', '模块'), h('th', '独立完成'), h('th', '看过答案后完成'), h('th', '尝试中'), h('th', '未开始'))),
      h('tbody', {}, reg.modules.map(m => {
        const ch = p.modules[m.moduleId]?.challenges || {};
        const n = s => m.challenges.filter(c => ch[c]?.status === s).length;
        return h('tr', {}, h('td', {}, h('a', { href: `../modules/${m.moduleId}/index.html#challenges` }, `${m.display} ${m.title}`)),
          h('td', String(n('solved'))), h('td', String(n('solved-after-answer'))), h('td', String(n('attempted'))), h('td', String(m.challenges.length - n('solved') - n('solved-after-answer') - n('attempted'))));
      }))),
    h('p.small.muted', p.savedAt ? `最后保存：${new Date(p.savedAt).toLocaleString('zh-CN')}` : '还没有记录。'));
}
paint();
document.getElementById('export').addEventListener('click', exportProgress);
const msg = document.getElementById('import-msg');
document.getElementById('import').addEventListener('change', async ev => {
  const f = ev.target.files[0]; if (!f) return;
  const r = await importProgress(f, known);
  msg.textContent = r.ok ? '导入成功。' : '没有导入：' + r.errors.slice(0, 4).join('；') + (r.errors.length > 4 ? ' …' : '');
  ev.target.value = ''; paint();
});
document.getElementById('clear').addEventListener('click', () => {
  if (!confirm('清除这台设备上的全部挑战记录？建议先导出。')) return;
  const p = loadProgress(); p.modules = {}; saveProgress(p); paint(); msg.textContent = '已清除。';
});
