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
        boundary_end = b"--" + boundary + b"--"

        # Read the raw request body
        body = req.raw_request

        parts = body.split(b"--" + boundary)

        file = None
        file_path = None

        index = 0
        for part in parts:
            index +=1
            print("part: " + str(index))
            if b"filename=" in part:
                headers, file_data = part.split(b"\r\n\r\n", 1)
                headers = headers.decode()
                file_data = file_data.rstrip(b"\r\n")

                for line in headers.split("\r\n"):
                    if "filename=" in line:
                        file_name = line.split("filename=")[1].strip('"')
                        file_path = f"/sd/{file_name}"
                        with open(file_path, "wb") as file:
                            file.write(file_data)
                        break
                break

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
