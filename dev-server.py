#!/usr/bin/env python3
"""
Local dev server for the pedalboard app.
Serves static files AND exposes a /api/save-layout endpoint
so the Layout Editor can write directly to collection JSON files.

Usage:
    python3 dev-server.py          # serves on port 3456
    python3 dev-server.py 8080     # custom port
"""
import base64
import http.server
import json
import os
import sys
from pathlib import Path

PORT   = int(sys.argv[1]) if len(sys.argv) > 1 else 3456
ROOT   = Path(__file__).parent.resolve()
COLLECTIONS = ROOT / "collections"
IMAGES      = COLLECTIONS / "images"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/save-layout":
            self._save_layout()
        elif self.path == "/api/save-image":
            self._save_image()
        else:
            self.send_error(404)

    def _save_layout(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            collection_file = body["collection"]              # e.g. "strymon.json"
            model_id        = body["modelId"]                  # e.g. "bigsky"
            layout          = body["layout"]                   # the layout object
            model_group     = body.get("modelGroup", "pedals") # "pedals" or "amps"

            # Security: only allow writes under collections/
            target = (COLLECTIONS / collection_file).resolve()
            if not str(target).startswith(str(COLLECTIONS)):
                self.send_error(403, "Forbidden path")
                return

            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update the model's layout field (try the declared group, then the other)
            group = data.get(model_group) or data.get("pedals") or data.get("amps") or {}
            if model_id in group:
                group[model_id]["layout"] = layout
            else:
                self.send_error(404, f"Model '{model_id}' not found in {collection_file}")
                return

            with open(target, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def _save_image(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            original_filename = body["filename"]          # e.g. "boss-bd-2.jpg"
            data_url          = body["imageData"]         # data:image/png;base64,...
            collection_file   = body.get("collection")   # optional, e.g. "boss.json"
            model_id          = body.get("modelId")       # optional, e.g. "bd2"

            # Decode base64 PNG
            if "," not in data_url:
                self.send_error(400, "Invalid imageData"); return
            b64 = data_url.split(",", 1)[1]
            png_bytes = base64.b64decode(b64)

            # Always save as .png
            stem = Path(original_filename).stem
            new_filename = stem + ".png"

            target = (IMAGES / new_filename).resolve()
            if not str(target).startswith(str(IMAGES)):
                self.send_error(403, "Forbidden path"); return

            with open(target, "wb") as f:
                f.write(png_bytes)

            # If filename changed and collection info provided, update layout.image in JSON
            if new_filename != original_filename and collection_file and model_id:
                col_path = (COLLECTIONS / collection_file).resolve()
                if str(col_path).startswith(str(COLLECTIONS)) and col_path.exists():
                    with open(col_path, "r", encoding="utf-8") as f:
                        col_data = json.load(f)
                    pedal = col_data.get("pedals", {}).get(model_id)
                    if pedal and pedal.get("layout"):
                        pedal["layout"]["image"] = new_filename
                        with open(col_path, "w", encoding="utf-8") as f:
                            json.dump(col_data, f, indent=2, ensure_ascii=False)
                            f.write("\n")

            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "filename": new_filename}).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        # Suppress 200 OK noise; only show errors and saves
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)
        elif self.path == "/api/save-layout":
            super().log_message(fmt, *args)


print(f"Pedalboard dev server → http://localhost:{PORT}/index.html")
print(f"Layout saves write to:  {COLLECTIONS}/")
with http.server.HTTPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
