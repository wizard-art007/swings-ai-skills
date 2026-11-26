import http.server
import json
import requests
import socketserver

# Simple LLM Router Proxy
# If primary fails, tries secondary. 
# Compatible with OpenAI-style API endpoints.

class MoatProxy(http.server.BaseHTTPRequestHandler):
    PRIMARY_URL = "http://localhost:11434/v1/chat/completions"
    FALLBACK_URL = "https://api.openai.com/v1/chat/completions"

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        headers = {'Content-Type': 'application/json', 'Authorization': self.headers.get('Authorization', '')}

        try:
            resp = requests.post(self.PRIMARY_URL, data=body, headers=headers, timeout=5)
            resp.raise_for_status()
            self.send_response(resp.status_code)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception:
            # Fallback to secondary
            try:
                resp = requests.post(self.FALLBACK_URL, data=body, headers=headers, timeout=10)
                self.send_response(resp.status_code)
                self.end_headers()
                self.wfile.write(resp.content)
            except Exception as e:
                self.send_error(502, f"Moat Error: {str(e)}")

def run(port=8080):
    with socketserver.TCPServer(("", port), MoatProxy) as httpd:
        httpd.serve_forever()
