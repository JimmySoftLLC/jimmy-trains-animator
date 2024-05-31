import board
import busio
import storage
import sdcardio
import wifi
import socketpool
import files

# Initialize SD card (if using one)
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

cfg = files.read_json_file("/sd/cfg.json")

import socketpool
import mdns
import wifi
from adafruit_httpserver import Server, Request, FileResponse, Response, POST

print("Connecting to WiFi")

# default for manufacturing and shows
SSID = "jimmytrainsguest"
PASSWORD = ""


try:
    env = files.read_json_file("/sd/env.json")
    SSID = env["WIFI_SSID"]
    PASSWORD = env["WIFI_PASSWORD"]
    print("Using env ssid")
except:
    print("Using default ssid")

try:
    # connect to your SSID
    wifi.radio.connect(SSID, PASSWORD)

    # setup mdns server
    mdns = mdns.Server(wifi.radio)
    mdns.hostname = cfg["HOST_NAME"]
    mdns.advertise_service(service_type="_http", protocol="_tcp", port=80)

    # files.log_items IP address to REPL
    files.log_item("IP is" + str(wifi.radio.ipv4_address))
    files.log_item("Connected")

    # set up server
    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)
      

    @server.route("/")
    def base(request: Request):
        return FileResponse(request, "index.html", "/")

    @server.route("/mui.min.css")
    def base(req: HTTPRequest):
        return FileResponse(req, "/sd/mui.min.css", "/")

    @server.route("/mui.min.js")
    def base(req: HTTPRequest):
        return FileResponse(req, "/sd/mui.min.js", "/")

    @server.route("/upload", [POST])
    def handle_request(req: Request):
        content_length = int(req.headers.get("Content-Length", 0))
        content_type = req.headers.get("Content-Type")
        if not content_type or "boundary=" not in content_type:
            return Response(req, "Invalid content type", 400)

        boundary = content_type.split("boundary=")[1].encode()
        boundary_start = b"--" + boundary + b"\r\n"
        boundary_end = b"--" + boundary + b"--"

        # Read the entire body at once
        body = req.body
        remaining = len(body)
        buffer = b""
        file = None
        file_path = None

        while remaining > 0:
            chunk_size = min(remaining, 2048)
            chunk = body[:chunk_size]
            body = body[chunk_size:]
            remaining -= chunk_size
            buffer += chunk

            if boundary_start in buffer:
                parts = buffer.split(boundary_start)
                header, buffer = parts[1].split(b"\r\n\r\n", 1)
                header = header.decode()
                for line in header.split("\r\n"):
                    if "filename=" in line:
                        file_name = line.split("filename=")[1].strip('"')
                        file_path = f"/sd/{file_name}"
                        if not file:
                            file = open(file_path, "wb")
                        break

            if file:
                if boundary_end in buffer:
                    body, buffer = buffer.split(boundary_end, 1)
                    file.write(body[:-2])  # Remove trailing CRLF
                    file.close()
                    break
                elif boundary_start in buffer:
                    part, buffer = buffer.split(boundary_start, 1)
                    file.write(part)
                else:
                    file.write(buffer)
                    buffer = b""

        if file_path:
            return Response(req, f"File uploaded successfully to {file_path}")
        else:
            return Response(req, "File upload failed", 400)

            
except Exception as e:
    web = False
    print(e)

server.start(str(wifi.radio.ipv4_address))

print("My IP address is " + str(wifi.radio.ipv4_address))

while True:
    server.poll()

