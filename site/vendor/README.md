# Third-party files served with the course

| Path | What | Version | Licence |
| --- | --- | --- | --- |
| `pyodide/` | [Pyodide](https://pyodide.org): CPython compiled to WebAssembly, used by the in-browser code lab. Core files only (no extra packages). Loaded only when a learner first presses Run. | 0.28.3 (npm `pyodide`) | Mozilla Public License 2.0; CPython itself under the PSF License |
| `codemirror.js` | [CodeMirror 6](https://codemirror.net) editor with Python mode, bundled into one ES module with esbuild (`codemirror` 6.0.1, `@codemirror/lang-python` 6.1.7). | see `package.json` versions in the bundle header | MIT, © Marijn Haverbeke and others |

Neither is modified. Rebuild: `npm install pyodide@0.28.3 codemirror@6.0.1 @codemirror/lang-python@6.1.7 esbuild`, then
bundle an entry that re-exports `EditorView, basicSetup` (codemirror), `EditorState, Compartment` (@codemirror/state),
`keymap` (@codemirror/view), `indentWithTab` (@codemirror/commands), `indentUnit` (@codemirror/language) and `python`
(@codemirror/lang-python) with `esbuild --bundle --format=esm --minify --legal-comments=eof`.
