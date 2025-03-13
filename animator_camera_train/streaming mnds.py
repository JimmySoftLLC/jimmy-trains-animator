import io
import json
import logging
import socket
import socketserver
import asyncio
from http import server
from threading import Condition, Thread
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from zeroconf import ServiceInfo

# PAGE HTML for the camera feed
PAGE = """
<html>
<head>
<title>PiCamera2 MJPEG Streaming</title>
</head>
<body>
<h1>PiCamera2 MJPEG Streaming</h1>
<img src="stream.mjpg" width="640" height="480" /><br>
<button onclick="startCamera()">Start Camera</button>
<button onclick="stopCamera()">Stop Camera</button>
<button onclick="snapshot()">Take Snapshot</button>
<script>
function startCamera() {
    fetch('/start_camera').then(response => console.log('Camera started'));
}
function stopCamera() {
    fetch('/stop_camera').then(response => console.log('Camera stopped'));
}
function snapshot() {
    fetch('/snapshot').then(response => console.log('Snapshot taken!'));
}
</script>
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        global recording, camera_running
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            if not camera_running:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'Camera not running')
                return
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while camera_running:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

        elif self.path == '/snapshot':
            if not camera_running:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'Camera not running')
                return
            try:
                picam2.stop_recording()
                picam2.switch_mode_and_capture_file(picam2.create_still_configuration(), 'test.jpg')
                picam2.start_recording(JpegEncoder(), FileOutput(output))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Snapshot taken')
            except Exception as e:
                logging.error(f"Failed to take snapshot: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Failed to take snapshot: {e}".encode())

        elif self.path == '/start_camera':
            if not camera_running:
                start_camera_server()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Camera started')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Camera already running')

        elif self.path == '/stop_camera':
            if camera_running:
                stop_camera_server()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Camera stopped')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Camera not running')

        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Global state
camera_running = False
picam2 = None
output = None
camera_thread = None

def start_camera_server():
    global camera_running, picam2, output, camera_thread
    if not camera_running:
        picam2 = Picamera2()
        picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
        output = StreamingOutput()
        picam2.start_recording(JpegEncoder(), FileOutput(output))
        camera_running = True
        camera_thread = Thread(target=run_camera_server, daemon=True)
        camera_thread.start()

def run_camera_server():
    address = ('', 8000)
    camera_server = StreamingServer(address, StreamingHandler)
    camera_server.serve_forever()

def stop_camera_server():
    global camera_running, picam2, camera_thread
    if camera_running:
        picam2.stop_recording()
        picam2.close()
        camera_running = False
        if camera_thread and camera_thread.is_alive():
            camera_thread.join()
        camera_thread = None

# Main server code
if web:
    if wait_for_network():
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")

        QUEUE_PORT = 8001
        PORT = 8083

        httpd = None

        def start_http_server():
            global httpd
            handler = MyHttpRequestHandler
            httpd = socketserver.TCPServer((local_ip, PORT), handler)
            httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(f"Serving on {local_ip}:{PORT}")
            httpd.serve_forever()

        def get_mdns_info():
            name_str = cfg["HOST_NAME"] + "._http._tcp.local."
            server_str = cfg["HOST_NAME"] + ".local."
            desc = {'path': '/'}
            mdns_info = ServiceInfo(
                "_http._tcp.local.",
                name_str,
                addresses=[socket.inet_aton(local_ip)],
                port=PORT,
                properties=desc,
                server=server_str
            )
            return mdns_info

        mdns_info = get_mdns_info()

        # Register mDNS for camera server
        camera_mdns_info = ServiceInfo(
            "_http._tcp.local.",
            f"{cfg['HOST_NAME']}-camera._http._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=8000,
            properties={'path': '/'},
            server=f"{cfg['HOST_NAME']}.local."
        )

        async def command_queue_handler(websocket, path):
            global current_media_playing
            print("WebSocket connection established")
            try:
                while True:
                    if command_queue:
                        commands = list(command_queue)
                        response = {
                            'commands': commands,
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))
                    else:
                        response = {
                            'commands': [],
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))

                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in command_queue_handler: {e}")
            finally:
                print("WebSocket connection closed")

        async def websocket_server():
            async with websockets.serve(command_queue_handler, "0.0.0.0", QUEUE_PORT):
                print(f"WebSocket server running on port {QUEUE_PORT}")
                await asyncio.Future()

        # Start the main HTTP server
        server_thread = Thread(target=start_http_server, daemon=True)
        server_thread.start()

        # Start the websocket server
        asyncio.run(websocket_server())

    else:
        web = False

gc_col("web server")
