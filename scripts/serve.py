#!/usr/bin/env python3
"""Serve site/ under a project subpath, like GitHub Pages: http://127.0.0.1:8790/learning-clustering/"""
import functools, http.server, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / "site"
PREFIX = "/" + (sys.argv[2] if len(sys.argv) > 2 else "learning-clustering")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8790

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".mjs": "text/javascript", ".vtt": "text/vtt", ".json": "application/json"}
    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        if p == "/" or not p.startswith(PREFIX):
            return str(ROOT / "__outside_prefix__")
        rel = p[len(PREFIX):].lstrip("/")
        return str(ROOT / rel)
    def send_error(self, code, message=None, explain=None):
        if code == 404 and (ROOT / "404.html").exists():
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            return
        super().send_error(code, message, explain)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

os.chdir(ROOT)
print(f"serving {ROOT} at http://127.0.0.1:{PORT}{PREFIX}/")
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(Handler, directory=str(ROOT))).serve_forever()
