#!/usr/bin/env node
// Writes content/modules/<id>/challenges.json (metadata only) from the module's challenges.js,
// so the page header, registry, progress validation and crosswalk all list the same challenges.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const course = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/course.json'), 'utf8'));
const TYPES = ['概念', '推演', '探索', '约束', '纠错', '解释', '决策', '实现', '应用', '合法性', '回退', '拓展', '基础', '进阶'];
let bad = 0;
for (const id of course.modules) {
  const file = path.join(ROOT, 'site/modules', id, 'challenges.js');
  if (!fs.existsSync(file)) { console.log('skip', id); continue; }
  const { challenges } = await import(pathToFileURL(file));
  const meta = challenges.map(c => {
    for (const k of ['id', 'type', 'difficulty', 'title', 'why', 'task', 'objectiveId', 'answer', 'explanation']) if (!c[k]) { console.error(`${id}/${c.id}: missing ${k}`); bad++; }
    if (!TYPES.includes(c.type)) { console.error(`${id}/${c.id}: unknown type ${c.type}`); bad++; }
    if (!['Intro', 'Practice', 'Stretch'].includes(c.difficulty)) { console.error(`${id}/${c.id}: difficulty`); bad++; }
    if (c.hints?.length !== 2) { console.error(`${id}/${c.id}: needs exactly two hints`); bad++; }
    return { id: c.id, type: c.type, difficulty: c.difficulty, title: c.title, objectiveId: c.objectiveId, validatorId: `${id}/${c.id}` };
  });
  const order = { Intro: 0, Practice: 1, Stretch: 2 };
  meta.forEach((m, i) => { if (i && order[m.difficulty] < order[meta[i - 1].difficulty]) { console.error(`${id}: ${m.id} is easier than the challenge before it (T16 easy→hard)`); bad++; } });
  fs.writeFileSync(path.join(ROOT, 'content/modules', id, 'challenges.json'), JSON.stringify(meta, null, 2));
  console.log(id, meta.length, 'challenges');
}
process.exit(bad ? 1 : 0);
