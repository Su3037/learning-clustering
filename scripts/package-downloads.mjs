#!/usr/bin/env node
// Zips each python/<id>/ exercise package into site/downloads/<id>-python.zip (uses the system `zip`).
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const out = path.join(ROOT, 'site/downloads');
fs.mkdirSync(out, { recursive: true });
for (const id of fs.readdirSync(path.join(ROOT, 'python')).filter(d => d.startsWith('m'))) {
  const zip = path.join(out, `${id}-python.zip`);
  fs.rmSync(zip, { force: true });
  execFileSync('zip', ['-q', '-r', '-X', zip, id, '-x', '*/__pycache__/*', '*.pyc', '*/.DS_Store', `${id}/en/*`], { cwd: path.join(ROOT, 'python') });
  console.log('packed', path.relative(ROOT, zip));
  // English pack: the same checker and fixtures, with the English starter, reference and README from python/<id>/en/.
  const en = path.join(ROOT, 'python', id, 'en');
  if (!fs.existsSync(en)) continue;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pack-')), dst = path.join(tmp, id);
  fs.cpSync(path.join(ROOT, 'python', id), dst, { recursive: true, filter: s => !s.includes('__pycache__') && !s.startsWith(en) });
  for (const f of fs.readdirSync(en).filter(f => fs.statSync(path.join(en, f)).isFile())) fs.copyFileSync(path.join(en, f), path.join(dst, f));
  const zipEn = path.join(out, `${id}-python-en.zip`);
  fs.rmSync(zipEn, { force: true });
  execFileSync('zip', ['-q', '-r', '-X', zipEn, id, '-x', '*/.DS_Store'], { cwd: tmp });
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('packed', path.relative(ROOT, zipEn));
}
