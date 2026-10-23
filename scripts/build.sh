#!/bin/sh
# Rebuild data and pages (fast). Media and slides are rebuilt separately: see docs/BUILD.md.
set -e
cd "$(dirname "$0")/.."
node scripts/build-traces.mjs
node scripts/extract-challenges.mjs
node scripts/build-site.mjs
node scripts/build-codelab.mjs
python3 scripts/build-fonts.py || echo "跳过字体子集（需要 Python 与 fontTools）"
node scripts/write-python-readmes.mjs
node scripts/package-downloads.mjs
