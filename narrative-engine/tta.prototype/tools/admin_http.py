#!/usr/bin/env python3
import json
import sys
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / 'core', ROOT / 'database'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldStateManager


class AdminHandler(BaseHTTPRequestHandler):
    wsm: WorldStateManager | None = None

    def _json(self, code: int, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse.urlparse(self.path)
        if parsed.path.startswith('/worlds/') and parsed.path.endswith('/summary'):
            world_id = parsed.path.split('/')[2]
            data = self.wsm.get_world_summary_dict(world_id)
            return self._json(200, data)
        if parsed.path == '/admin/metrics':
            data = self.wsm.get_debug_metrics_summary()
            return self._json(200, data)
        self._json(404, {'error': 'not found'})

    def do_POST(self):
        parsed = urlparse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length) if length else b''
        if parsed.path.startswith('/worlds/') and parsed.path.endswith('/export'):
            world_id = parsed.path.split('/')[2]
            # naive: return JSON export
            data = self.wsm.export_world_state(world_id)
            if data:
                return self._json(200, {'world_id': world_id, 'data': json.loads(data)})
            return self._json(400, {'error': 'export failed'})
        if parsed.path == '/worlds/import':
            try:
                payload = json.loads(body.decode('utf-8'))
                data = payload.get('data')
                ws = self.wsm.import_world_state(json.dumps(data) if isinstance(data, dict) else data)
                return self._json(200, {'ok': bool(ws)})
            except Exception as e:
                return self._json(400, {'error': str(e)})
        self._json(404, {'error': 'not found'})


def run(host='127.0.0.1', port=8080):
    AdminHandler.wsm = WorldStateManager()
    srv = HTTPServer((host, port), AdminHandler)
    print(f"Admin HTTP running at http://{host}:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == '__main__':
    run()

