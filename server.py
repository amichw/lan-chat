#!/usr/bin/env python3
"""Local signaling server for P2P Chat WebRTC sessions.

Usage:
    python3 server.py

Then open the printed URL on both devices.
"""

import json
import os
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# ── In-memory signal store ────────────────────────────────────────────────────
_lock = threading.Lock()
_signals = {}   # id -> signal dict
SIGNAL_TTL = 60  # seconds before a signal is purged


def _purge_old():
    """Remove signals older than SIGNAL_TTL. Must be called under _lock."""
    cutoff = time.time() - SIGNAL_TTL
    expired = [k for k, v in _signals.items() if v['ts'] < cutoff]
    for k in expired:
        del _signals[k]


# ── Request handler ───────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # suppress per-request noise

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        # ── Signal API ──
        if parsed.path == '/api/signal':
            qs = parse_qs(parsed.query)
            exclude = qs.get('exclude', [None])[0]
            with _lock:
                result = [s for s in _signals.values() if s.get('from') != exclude]
            body = json.dumps(result).encode()
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── Static files ──
        rel = parsed.path.lstrip('/')
        if not rel:
            rel = 'chat.html'

        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.normpath(os.path.join(base_dir, rel))

        # Prevent path traversal
        if not full_path.startswith(base_dir + os.sep) and full_path != base_dir:
            self.send_response(403)
            self.end_headers()
            return

        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            content_types = {
                '.html': 'text/html; charset=utf-8',
                '.js':   'application/javascript',
                '.css':  'text/css',
                '.json': 'application/json',
                '.png':  'image/png',
                '.ico':  'image/x-icon',
            }
            ct = content_types.get(ext, 'application/octet-stream')
            with open(full_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', ct)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/signal':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        try:
            sig = json.loads(raw)
        except (ValueError, TypeError):
            self.send_response(400)
            self.end_headers()
            return

        sig_id = str(uuid.uuid4())
        sig['id'] = sig_id
        sig['ts'] = time.time()

        with _lock:
            _purge_old()
            _signals[sig_id] = sig

        body = json.dumps({'id': sig_id}).encode()
        self.send_response(201)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        # /api/signal/<id>
        if len(parts) == 3 and parts[0] == 'api' and parts[1] == 'signal':
            sig_id = parts[2]
            with _lock:
                _signals.pop(sig_id, None)
            self.send_response(204)
            self._cors()
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


# ── LAN IP detection ──────────────────────────────────────────────────────────
def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    PORT = 8080
    ip = get_lan_ip()
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print()
    print('  P2P Chat — signaling server')
    print('  Open on both devices: http://{}:{}/chat.html'.format(ip, PORT))
    print()
    print('  Ctrl+C to stop')
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
