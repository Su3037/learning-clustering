// ModuleRenderer runtime: mounts the shared film player, slide viewer, challenge engine and pseudocode
// panels on a generated module page, then hands the lab root to the module's own experiment code.
import { $, $$, h, fetchJSON, L } from './core.js';
import { mountVideo, mountSlides } from './media.js';
import { mountChallenges } from './challenges.js';
import { mountCodeLab } from './codelab.js';
import { Pseudocode } from './lab.js';

export async function bootModule({ moduleId, display, challenges, lab, visualize }) {
  const base = new URL('../', import.meta.url);
  const pseudo = Object.fromEntries($$('.pseudo').map(el => [el.dataset.pseudo, new Pseudocode(el)]));
  const tasks = [
    mountVideo($('#film-root'), new URL(`media/${moduleId}/film.json`, base)),
    mountSlides($('#slides-root'), new URL(`slides/${moduleId}/slides.json`, base), display)
  ];
  try { mountChallenges($('#challenge-root'), moduleId, challenges); }
  catch (e) { $('#challenge-root').replaceChildren(h('p.lab-error', L(`挑战加载失败：${e.message}`, `The challenges failed to load: ${e.message}`))); }
  const cl = $('#codelab-root');
  if (cl) tasks.push(fetchJSON(new URL(`data/${moduleId}/codelab.json`, base), cl).then(data => data && mountCodeLab(cl, { moduleId, base, data, visualize })));
  try { await lab($('#lab-root'), { pseudo, base, moduleId }); }
  catch (e) { console.error(e); $('#lab-root').replaceChildren(h('p.lab-error', L(`实验加载失败：${e.message}`, `The lab failed to load: ${e.message}`))); }
  await Promise.allSettled(tasks);
  // Re-apply the anchor once media and lab have their final height; #slide-<id> lands on the slide viewer.
  const id = decodeURIComponent(location.hash.slice(1));
  if (id) document.getElementById(id.startsWith('slide-') ? 'slides' : id)?.scrollIntoView({ behavior: 'instant' });
}
