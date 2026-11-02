"""Serve the report and read-only memory API on this computer only."""
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from research_store import ROOT, connect, current_snapshot, history_payload


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/history':
            return self.send_json(history_payload())
        if path == '/api/research':
            with connect() as db:
                row = current_snapshot(db)
                if row:
                    return self.send_json(json.loads(row['payload']))
            return self.send_error(503, 'Run build.py first')
        # Serve only generated reading artifacts; never expose database or sources.
        filename = 'index.html' if path == '/' else path.removeprefix('/')
        if filename not in {'index.html', 'technologies.html', 'statistics.html', 'trends.html'}:
            return self.send_error(404)
        file = ROOT / filename
        if not file.is_file():
            return self.send_error(404)
        self.send_bytes(file.read_bytes(), mimetypes.guess_type(filename)[0] + '; charset=utf-8')

    def send_json(self, value):
        self.send_bytes(json.dumps(value, ensure_ascii=False).encode(), 'application/json; charset=utf-8')

    def send_bytes(self, body, content_type):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    print('Research Newspaper：http://127.0.0.1:8766/statistics.html', flush=True)
    server = ThreadingHTTPServer(('127.0.0.1', 8766), Handler)
    if '--open' in sys.argv:
        webbrowser.open('http://127.0.0.1:8766/statistics.html')
    server.serve_forever()
