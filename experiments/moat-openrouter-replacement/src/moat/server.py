import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from moat.router import MoatRouter, LLMProvider

router = MoatRouter(strategy="fallback")
# Example default mock/local provider
router.add_provider(LLMProvider("local-ollama", "http://localhost:11434/v1"))

class MoatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode('utf-8'))
                result = router.route_chat(payload)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                err_resp = {"error": {"message": str(e), "type": "moat_gateway_error"}}
                self.wfile.write(json.dumps(err_resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "status": "healthy",
                "providers": [{"name": p.name, "healthy": p.is_healthy, "latency_ms": p.latency_ms} for p in router.providers]
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=MoatHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Moat router running on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
