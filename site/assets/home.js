// Home page: show per-module challenge progress on the eight cards.
import { loadProgress, fetchJSON } from './core.js';
const reg = await fetchJSON(new URL('../data/registry.json', import.meta.url));
function paint() {
  if (!reg) return;
  const p = loadProgress();
  for (const m of reg.modules) {
    const card = document.querySelector(`[data-module="${m.moduleId}"]`);
    if (!card || !m.challenges.length) continue;
    const ch = p.modules[m.moduleId]?.challenges || {};
    const own = m.challenges.filter(c => ch[c]?.status === 'solved').length;
    const after = m.challenges.filter(c => ch[c]?.status === 'solved-after-answer').length;
    card.querySelector('.bar i').style.width = `${100 * (own + after) / m.challenges.length}%`;
    card.querySelector('.progress-text').textContent = own + after ? `挑战 ${own + after}/${m.challenges.length}${after ? `（其中 ${after} 题看过答案）` : ''}` : `挑战 0/${m.challenges.length}`;
  }
}
paint();
document.addEventListener('progress-changed', paint);
