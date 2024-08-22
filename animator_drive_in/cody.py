import http.server
import socket
import socketserver
import threading
from zeroconf import ServiceInfo, Zeroconf
import json
import os
import gc
import vlc
import time
import board
import digitalio
from adafruit_debouncer import Debouncer
import neopixel_spi
from rainbowio import colorwheel
import pwmio
from adafruit_motor import servo

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
            self.path = "/indexmdns.html"
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
        if self.path == "/upload":
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']

            if 'multipart/form-data' in content_type:
                boundary = content_type.split("boundary=")[1].encode()
                body = self.rfile.read(content_length)
                
                parts = body.split(b'--' + boundary)
                for part in parts:
                    gc.collect()
                    if part:
                        try:
                            headers, content = part.split(b'\r\n\r\n', 1)
                        except ValueError:
                            continue
                        content = content.rstrip(b'\r\n--')
                        header_lines = headers.decode().split('\r\n')
                        headers_dict = {}
                        for line in header_lines:
                            if ': ' in line:
                                key, value = line.split(': ', 1)
                                headers_dict[key] = value
                        
                        if 'Content-Disposition' in headers_dict:
                            disposition = headers_dict['Content-Disposition']
                            if 'filename=' in disposition:
                                file_name = disposition.split('filename=')[1].strip('"')
                                # Ensure the uploads directory exists
                                os.makedirs("uploads", exist_ok=True)
                                file_path = os.path.join("uploads", file_name)

                                with open(file_path, "wb") as f:
                                    f.write(content)

                                self.send_response(200)
                                self.send_header("Content-type", "application/json")
                                self.end_headers()
                                response = {"status": "success", "message": "File uploaded successfully"}
                                self.wfile.write(json.dumps(response).encode('utf-8'))
                                return
                
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": "No file part"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(f"Received POST data: {post_data.decode('utf-8')}")

            # Respond to the POST request
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "success",
                        "data": post_data.decode('utf-8')}
            self.wfile.write(json.dumps(response).encode('utf-8'))


# Get the local IP address
local_ip = get_local_ip()
print(f"Local IP address: {local_ip}")

# Set up the HTTP server
PORT = 8083  # Use port 80 for default HTTP access
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

# Setup the switches, there are two the Left and Right and two unused 3 and 4
switch_io_1 = digitalio.DigitalInOut(board.D17)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP

switch_io_2 = digitalio.DigitalInOut(board.D27)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP

switch_io_3 = digitalio.DigitalInOut(board.D22)
switch_io_3.direction = digitalio.Direction.INPUT
switch_io_3.pull = digitalio.Pull.UP

switch_io_4 = digitalio.DigitalInOut(board.D5)
switch_io_4.direction = digitalio.Direction.INPUT
switch_io_4.pull = digitalio.Pull.UP

aud_en = digitalio.DigitalInOut(board.D26)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

left_switch = Debouncer(switch_io_1)
right_switch = Debouncer(switch_io_2)
white_switch = Debouncer(switch_io_3)
blue_switch = Debouncer(switch_io_4)

# Setup the servo
m1_pwm = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50)
m2_pwm = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=50)
m3_pwm = pwmio.PWMOut(board.D23, duty_cycle=2 ** 15, frequency=50)
m4_pwm = pwmio.PWMOut(board.D24, duty_cycle=2 ** 15, frequency=50)
m5_pwm = pwmio.PWMOut(board.D25, duty_cycle=2 ** 15, frequency=50)
m6_pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=50)
m7_pwm = pwmio.PWMOut(board.D16, duty_cycle=2 ** 15, frequency=50)
m8_pwm = pwmio.PWMOut(board.D20, duty_cycle=2 ** 15, frequency=50)

m1_servo = servo.Servo(m1_pwm)
m2_servo = servo.Servo(m2_pwm)
m3_servo = servo.Servo(m3_pwm)
m4_servo = servo.Servo(m4_pwm)
m5_servo = servo.Servo(m5_pwm)
m6_servo = servo.Servo(m6_pwm)
m7_servo = servo.Servo(m7_pwm)
m8_servo = servo.Servo(m8_pwm)

m1_servo.angle = 180
m2_servo.angle = 180
m3_servo.angle = 180
m4_servo.angle = 180
m5_servo.angle = 180
m6_servo.angle = 180
m7_servo.angle = 180
m8_servo.angle = 180

# setup neopixels on spi GP10
num_pixels_rgb=10
ledStripRGB = neopixel_spi.NeoPixel_SPI(board.SPI(), num_pixels_rgb, brightness=1.0, auto_write=False)


# create vlc media player object for playing video, music etc
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()

movie = []
movie.append("/media/pi/EMBROIDERY/Videos/Addams Family Train Wreck Scenes.mp4")
#movie.append("/home/pi/Videos/Addams Family Train Wreck Scenes.mp4")
#movie.append("/home/pi/Videos/Baltimore & Ohio Railroad Passenger Train.mp4")
#movie.append("/home/pi/Videos/Black River Railroad System.mp4")
#movie.append("/home/pi/Videos/Classic Pennsy WideScreen DVD Preview.mp4")
#movie.append("/home/pi/Videos/The Brave Locomotive.mp4")
#movie.append("/home/pi/Videos/Toy Trains_Model Railroads.mp4")

run_movie_cont = False
volume = 70
movie_index = 0

def play_movies():
    global movie_index
    if movie_index > 7: movie_index = 0
    media = vlc.Media(movie[movie_index])
    media_player.set_media(media)
    play_movie()
    movie_index +=1
    
def pause_movie():
    media_player.pause()
    
def play_movie():
    media_player.play()

def rainbow(speed,duration):
    startTime = time.monotonic()
    for j in range(0,255,1):
        for i in range(num_pixels_rgb):
            pixel_index = (i * 256 // num_pixels_rgb) + j
            ledStripRGB[i] = colorwheel(pixel_index & 255)
        ledStripRGB.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_pixels_rgb):
            pixel_index = (i * 256 // num_pixels_rgb) + j
            ledStripRGB[i] = colorwheel(pixel_index & 255)
        ledStripRGB.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
        
media_player.audio_set_volume(volume)

while True:
    if not media_player.is_playing() and run_movie_cont:
        print("play movies: " + str(run_movie_cont))
        play_movies()
        while not media_player.is_playing():
            time.sleep(.5)
    left_switch.update()
    right_switch.update()
    white_switch.update()
    blue_switch.update()
    if left_switch.fell:
        if media_player.is_playing(): pause_movie()
        run_movie_cont = True
        print ("left fell")
    if right_switch.fell:
        print ("right fell")
        if media_player.is_playing():
            run_movie_cont = False
            pause_movie()
        else:
            play_movie()
            rainbow(.005,5)
    if white_switch.fell:
        print ("white fell")
        volume = volume - 10
        if volume < 0: volume = 0
        media_player.audio_set_volume(volume)
    if blue_switch.fell:
        print ("blue fell")
        volume = volume + 10
        if volume > 100: volume = 100
        media_player.audio_set_volume(volume)
    time.sleep(.1)
    pass

media_player.stop()  

try:
    input("Press enter to exit...\n\n")
finally:
    print("Unregistering mDNS service...")
    zeroconf.unregister_service(info)
    zeroconf.close()
    httpd.shutdown()
