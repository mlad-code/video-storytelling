import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
from google import genai
from google.genai.types import Part
import os

PORT = 8000
PROJECT_ID = "mlad-argo"

class MCPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/mcp'):
            query_components = parse_qs(urlparse(self.path).query)
            family_name = query_components.get('family_name', [None])[0]

            if family_name:
                with open('/usr/local/google/home/mlad/adk-demo/mcp_data.json', 'r') as f:
                    data = json.load(f)
                
                if family_name in data:
                    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
                    
                    response_data = []
                    for character_data in data[family_name]:
                        image_path = urlparse(character_data["image_url"]).path
                        with open(image_path, "rb") as f:
                            image_bytes = f.read()
                        
                        # Analyze the image with Gemini
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                                "Extract the name and birth place of the person in this image. "
                                "Return the data in JSON format with keys 'name' and 'birth_place'. "
                                "If you can't determine the information, use 'Unknown'."
                            ]
                        )
                        
                        metadata = {"name": "Unknown", "birth_place": "Unknown"}
                        if response.candidates and response.candidates[0].content.parts:
                            try:
                                # The model output might have markdown ```json ... ```, so we need to clean it
                                json_str = response.candidates[0].content.parts[0].text.strip().replace("```json", "").replace("```", "")
                                metadata = json.loads(json_str)
                            except json.JSONDecodeError:
                                # If parsing fails, use the raw text as name
                                metadata["name"] = response.candidates[0].content.parts[0].text.strip()


                        response_data.append({
                            "name": metadata.get("name", character_data.get("name", "Unknown")),
                            "birth_place": metadata.get("birth_place", "Unknown"),
                            "image_url": character_data["image_url"]
                        })

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Family not found')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Missing family_name parameter')
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), MCPServer) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
