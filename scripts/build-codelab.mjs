#!/usr/bin/env node
// Packs each opted-in module's Python exercise (module.json "codelab": true) for the in-browser code lab:
// site/data/<id>/codelab.json = { files: check.py + fixtures, starter/reference per language, check names per language }.
// Check names come from running the real check.py on the reference, so page and download never disagree.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const course = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/course.json'), 'utf8'));
for (const id of course.modules) {
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/modules', id, 'module.json'), 'utf8'));
  if (!m.codelab) continue;
  const dir = path.join(ROOT, 'python', id), read = p => fs.readFileSync(path.join(dir, p), 'utf8');
  const exists = p => fs.existsSync(path.join(dir, p));
  const files = { 'check.py': read('check.py') };
  for (const f of fs.readdirSync(path.join(dir, 'fixtures')).sort()) files[`fixtures/${f}`] = read(`fixtures/${f}`);
  const names = lang => {
    const out = execFileSync('python3', ['check.py', exists(`${lang}/reference.py`) ? `${lang}/reference.py` : 'reference.py', '--json', '--lang', lang], { cwd: dir, encoding: 'utf8' });
    const r = JSON.parse(out.split('\n').find(l => l.startsWith('@@CHECK@@')).slice(9));
    if (!r.ok) throw new Error(`${id}: the reference does not pass every check (${lang})`);
    return r.results.map(x => x.name);
  };
  const zh = names('zh'), en = names('en');
  const data = {
    moduleId: id, python: '3.13 (Pyodide 0.28.3)', files,
    starter: { zh: read('starter.py'), en: exists('en/starter.py') ? read('en/starter.py') : read('starter.py') },
    reference: { zh: read('reference.py'), en: exists('en/reference.py') ? read('en/reference.py') : read('reference.py') },
    checks: zh.map((z, i) => ({ zh: z, en: en[i] }))
  };
  fs.mkdirSync(path.join(ROOT, 'site/data', id), { recursive: true });
  fs.writeFileSync(path.join(ROOT, 'site/data', id, 'codelab.json'), JSON.stringify(data));
  console.log(`codelab ${id}: ${zh.length} checks, ${Object.keys(files).length} files`);
}
