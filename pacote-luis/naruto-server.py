"""
Servidor HTTP simples para o dashboard Naruto Analytics
"""
import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs

PORT = 8000

class NarutoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Rota para dados JSON
        if self.path.startswith('/api/data'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Ler arquivo JSON
            try:
                if os.path.exists('naruto_log.json'):
                    with open('naruto_log.json', 'r') as f:
                        data = json.load(f)
                    self.wfile.write(json.dumps(data).encode())
                else:
                    # Retornar dados vazios se arquivo não existir
                    self.wfile.write(json.dumps({
                        "frames": 0,
                        "combos": 0,
                        "exotericas": 0,
                        "last_frame": None,
                        "last_action": {"text": "Aguardando...", "type": ""}
                    }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            # Servir arquivos estáticos normalmente
            super().do_GET()

    def log_message(self, format, *args):
        # Silenciar logs do servidor
        pass

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), NarutoHandler) as httpd:
        print("=" * 70)
        print("")
        print("   NARUTO ANALYTICS - SERVIDOR WEB")
        print("")
        print(f"   Dashboard: http://localhost:{PORT}/naruto-dashboard.html")
        print("")
        print("   Pressione Ctrl+C para parar")
        print("")
        print("=" * 70)
        print("")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n[*] Servidor encerrado")
