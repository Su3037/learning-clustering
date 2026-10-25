// Home page: the introduction film, and per-module challenge progress on the eight cards.
import { loadProgress, fetchJSON, L } from './core.js';
import { mountVideo } from './media.js';

const intro = document.querySelector('#intro-film-root');
if (intro) mountVideo(intro, new URL('../media/home/film.json', import.meta.url));
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
    card.querySelector('.progress-text').textContent = own + after ? L(`挑战 ${own + after}/${m.challenges.length}${after ? `（其中 ${after} 题看过答案）` : ''}`, `Challenges ${own + after}/${m.challenges.length}${after ? ` (${after} after seeing the answer)` : ''}`) : L(`挑战 0/${m.challenges.length}`, `Challenges 0/${m.challenges.length}`);
  }
}
paint();
document.addEventListener('progress-changed', paint);
