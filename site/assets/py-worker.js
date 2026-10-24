// Python runner for the code lab: a module worker that hosts Pyodide (self-hosted under vendor/pyodide/).
// The page can terminate this worker at any time, which is how "Stop" ends an infinite loop.
// Messages in:  { id, files: {path: text}, code }   (files are written under /work, then `code` runs there)
// Messages out: { type: 'ready' } | { id, type: 'out' | 'err', text } | { id, type: 'done', value } | { id, type: 'error', text }
import { loadPyodide } from '../vendor/pyodide/pyodide.mjs';

let current = null;
const ready = loadPyodide({ indexURL: new URL('../vendor/pyodide/', import.meta.url).href }).then(py => {
  py.setStdout({ batched: text => postMessage({ id: current, type: 'out', text }) });
  py.setStderr({ batched: text => postMessage({ id: current, type: 'err', text }) });
  py.FS.mkdirTree('/work');
  postMessage({ type: 'ready', version: py.version });
  return py;
}).catch(e => { postMessage({ type: 'fatal', text: String(e && e.message || e) }); throw e; });

onmessage = async ({ data }) => {
  const py = await ready;
  current = data.id;
  try {
    for (const [p, text] of Object.entries(data.files || {})) {
      const full = '/work/' + p;
      py.FS.mkdirTree(full.slice(0, full.lastIndexOf('/')));
      py.FS.writeFile(full, text, { encoding: 'utf8' });
    }
    py.runPython("import os, sys\nos.chdir('/work')\nif '/work' not in sys.path: sys.path.insert(0, '/work')\nfor _m in [m for m in sys.modules if m in ('impl', 'impl_v', 'starter', 'reference')]: del sys.modules[_m]");
    const value = await py.runPythonAsync(data.code);
    postMessage({ id: data.id, type: 'done', value: value === undefined ? null : String(value) });
  } catch (e) {
    postMessage({ id: data.id, type: 'error', text: String(e && e.message || e) });
  }
};
