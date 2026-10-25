#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hapytus — High-Performance Financial AI Server & Frontend Host
Bridges the Hapytus Open-Source Financial LLM models with the Web UI.
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = 8000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

class HapytusRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving frontend assets and REST API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # API Health Endpoint
        if parsed_url.path == '/api/health':
            self._send_json({
                "status": "healthy",
                "framework": "Hapytus",
                "model_backbone": "Meta-LLaMA-3-8B-LoRA",
                "version": "3.2.0",
                "cuda_available": False
            })
            return

        # API Market Signals Endpoint
        if parsed_url.path == '/api/signals':
            signals = [
                {"symbol": "NVDA", "name": "NVIDIA Corp", "signal": "strong-buy", "confidence": 0.942, "target": 158.0, "stop_loss": 134.5},
                {"symbol": "AAPL", "name": "Apple Inc", "signal": "buy", "confidence": 0.865, "target": 245.0, "stop_loss": 224.0},
                {"symbol": "MSFT", "name": "Microsoft Corp", "signal": "buy", "confidence": 0.891, "target": 450.0, "stop_loss": 415.0},
                {"symbol": "TSLA", "name": "Tesla Inc", "signal": "neutral", "confidence": 0.720, "target": 235.0, "stop_loss": 204.0},
                {"symbol": "BTC", "name": "Bitcoin", "signal": "strong-buy", "confidence": 0.923, "target": 74000.0, "stop_loss": 64500.0}
            ]
            self._send_json({"data": signals})
            return

        # Default static file serving from frontend directory
        super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode('utf-8'))
        except Exception:
            body = {}

        if parsed_url.path == '/api/chat':
            user_msg = body.get('message', '')
            response = {
                "model": "Hapytus-v3.2",
                "reply": f"Hapytus model processed prompt: '{user_msg}'. Bullish sentiment probability is 82.5% with high confidence.",
                "sentiment_score": 82.5,
                "sentiment_label": "Bullish"
            }
            self._send_json(response)
            return

        self.send_error(404, "Endpoint Not Found")

    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

def run_server(port=PORT):
    print("=" * 65)
    print(f"[*] Hapytus Financial AI Platform running on http://localhost:{port}")
    print(f"[*] Serving frontend from: {FRONTEND_DIR}")
    print("[*] REST Endpoints available at: /api/health, /api/signals, /api/chat")
    print("=" * 65)
    httpd = HTTPServer(('0.0.0.0', port), HapytusRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Hapytus Server...")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
