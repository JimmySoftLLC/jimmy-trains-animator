import http.server
import socket
import socketserver
import threading
import json
from zeroconf import ServiceInfo, Zeroconf

# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Define the web server handler
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle /get-host-name endpoint
        if self.path == "/get-host-name":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"hostname": socket.gethostname()}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Serve the HTML content from a local file
        if self.path == "/":
            self.path = "/index.html"
        # Set content type based on file extension
        if self.path.endswith(".css"):
            content_type = "text/css"
        elif self.path.endswith(".js"):
            content_type = "application/javascript"
        else:
            content_type = "text/html"
        try:
            file_path = self.path.lstrip("/")
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received POST data: {post_data.decode('utf-8')}")
        
        # Respond to the POST request
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"status": "success", "data": post_data.decode('utf-8')}
        self.wfile.write(json.dumps(response).encode('utf-8'))    

# Get the local IP address
local_ip = get_local_ip()
print(f"Local IP address: {local_ip}")

# Set up the HTTP server
PORT = 80  # Use port 80 for default HTTP access
handler = MyHttpRequestHandler
httpd = socketserver.TCPServer((local_ip, PORT), handler)

# Function to start the web server
def start_server():
    print(f"Serving on {local_ip}:{PORT}")
    httpd.serve_forever()

# Set up mDNS service info
desc = {'path': '/'}
info = ServiceInfo(
    "_http._tcp.local.",
    "dude._http._tcp.local.",
    addresses=[socket.inet_aton(local_ip)],
    port=PORT,
    properties=desc,
    server="dude.local."
)

# Register mDNS service
zeroconf = Zeroconf()
print("Registering mDNS service...")
zeroconf.register_service(info)

# Run the server in a separate thread to allow mDNS to work simultaneously
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

try:
    input("Press enter to exit...\n\n")
finally:
    print("Unregistering mDNS service...")
    zeroconf.unregister_service(info)
    zeroconf.close()
    httpd.shutdown()
