import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/', '/health'):
            self.send_response(404); self.end_headers(); return
        ready = bool(os.getenv('CLOUDINARY_URL')) and bool(os.getenv('METRICOOL_API_TOKEN'))
        body = ('{"service":"storyagent","status":"configured"}' if ready else '{"service":"storyagent","status":"setup_required"}').encode()
        self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)

if __name__ == '__main__':
    HTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
