from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Import the engine logic
try:
    from engine import process_variant
except ImportError:
    # Fallback for Vercel environment where imports might be tricky
    try:
        from api.engine import process_variant
    except ImportError:
        # Define a mock if imports fail (should not happen in correct setup)
        def process_variant(variant, api_keys):
            return {"error": "Import failed", "details": str(sys.path)}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode('utf-8'))
            variant = body.get('variant')
            api_keys = body.get('api_keys', {})

            if not variant:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No variant provided"}).encode('utf-8'))
                return

            # Process the variant
            result = process_variant(variant, api_keys)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()
