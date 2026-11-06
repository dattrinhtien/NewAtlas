#!/usr/bin/env python3
"""
NewAtlas 3D Local Server
Hỗ trợ đa luồng (ThreadingHTTPServer), byte-range streaming và CORS
"""

import sys
import os
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

class AnatomyRequestHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        '': 'application/octet-stream',
        '.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.mjs': 'application/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.glb': 'model/gltf-binary',
        '.gltf': 'model/gltf+json',
        '.bin': 'application/octet-stream',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.wasm': 'application/wasm',
    }

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def try_open_browser(url):
    try:
        subprocess.Popen(['open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def start_server(port=8080):
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)

    server_address = ('', port)
    try:
        httpd = ThreadingHTTPServer(server_address, AnatomyRequestHandler)
    except OSError:
        port = 8081
        server_address = ('', port)
        httpd = ThreadingHTTPServer(server_address, AnatomyRequestHandler)

    url = f"http://127.0.0.1:{port}"
    print("=" * 70)
    print("  🚀 NEWATLAS 3D PRO LOCAL SERVER ĐÃ KHỞI CHẠY!")
    print(f"  👉 Click mở ngay: {url}")
    print(f"  👉 Hoặc địa chỉ:   http://localhost:{port}")
    print("  👉 Nhấn Ctrl + C để dừng máy chủ bất cứ lúc nào.")
    print("=" * 70)

    try_open_browser(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[NewAtlas] Đã dừng máy chủ thành công.")
        sys.exit(0)

if __name__ == '__main__':
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(p)
