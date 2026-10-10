import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/', '/health'):
            self.send_response(404); self.end_headers(); return
        cloudinary = os.getenv('CLOUDINARY_URL', '')
        status = {
            "service": "storyagent",
            "hosting": "live",
            "cloudinary_credentials_present": cloudinary.startswith("cloudinary://") and "@" in cloudinary,
            "metricool_api_credentials_present": bool(os.getenv("METRICOOL_API_TOKEN")),
            "automatic_publishing_enabled": False,
            "note": "Credentials presence is not proof of successful uploads or posts."
        }
        body = json.dumps(status).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    HTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
