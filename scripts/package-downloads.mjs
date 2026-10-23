#!/usr/bin/env node
// Zips each python/<id>/ exercise package into site/downloads/<id>-python.zip (uses the system `zip`).
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const out = path.join(ROOT, 'site/downloads');
fs.mkdirSync(out, { recursive: true });
for (const id of fs.readdirSync(path.join(ROOT, 'python')).filter(d => d.startsWith('m'))) {
  const zip = path.join(out, `${id}-python.zip`);
  fs.rmSync(zip, { force: true });
  execFileSync('zip', ['-q', '-r', '-X', zip, id, '-x', '*/__pycache__/*', '*.pyc', '*/.DS_Store'], { cwd: path.join(ROOT, 'python') });
  console.log('packed', path.relative(ROOT, zip));
}
