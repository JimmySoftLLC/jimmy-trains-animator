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
import pygame
import gc
import files
import utilities
import psutil

def gc_col(collection_point):
    gc.collect()
    start_mem = psutil.virtual_memory()[1]
    print("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))
    
gc_col("Imports gc, files")

################################################################################
# Setup io hardware

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

l_s = Debouncer(switch_io_1)
r_s = Debouncer(switch_io_2)
w_s = Debouncer(switch_io_3)
b_s = Debouncer(switch_io_4)

################################################################################
# Setup sound hardware
#i2s audio is setup on pi with an overlay

# Setup the mixer to play wav files
pygame.mixer.init()
mix = pygame.mixer.music
mix.load('/home/pi/Videos/left_speaker_right_speaker.wav')
mix.set_volume(.05)
mix.play(loops=0)

#audio experiments to understand
# pygame.mixer.init()
# pygame.mixer.music.load('/home/pi/Videos/left_speaker_right_speaker.wav')
# pygame.mixer.music.unload
# pygame.mixer.music.rewind()
# pygame.mixer.music.stop()
# pygame.mixer.music.pause()
# pygame.mixer.music.set_volume(0.01)
# pygame.mixer.music.play(loops=0)
# pos=pygame.mixer.music.get_pos()

################################################################################
# Setup video hardware
#i2s audio is setup on pi with an overlay

# create vlc media player object for playing video, music etc
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()

movie = []
#movie.append("/media/pi/EMBROIDERY/Videos/Addams Family Train Wreck Scenes.mp4")
movie.append("/home/pi/Videos/Addams Family Train Wreck Scenes.mp4")
#movie.append("/home/pi/Videos/Baltimore & Ohio Railroad Passenger Train.mp4")
#movie.append("/home/pi/Videos/Black River Railroad System.mp4")
#movie.append("/home/pi/Videos/Classic Pennsy WideScreen DVD Preview.mp4")
#movie.append("/home/pi/Videos/The Brave Locomotive.mp4")
#movie.append("/home/pi/Videos/Toy Trains_Model Railroads.mp4")

run_movie_cont = True
volume = 20
movie_index = 0
media_player.audio_set_volume(volume)

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
        for i in range(num_px):
            pixel_index = (i * 256 // num_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_px):
            pixel_index = (i * 256 // num_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
        


################################################################################
# Setup servo hardware
m1_pwm = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50) #D23
m2_pwm = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=50) #D24
m3_pwm = pwmio.PWMOut(board.D23, duty_cycle=2 ** 15, frequency=50) #D25
m4_pwm = pwmio.PWMOut(board.D24, duty_cycle=2 ** 15, frequency=50) #D6
m5_pwm = pwmio.PWMOut(board.D25, duty_cycle=2 ** 15, frequency=50) #D13
m6_pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=50) #D12
m7_pwm = pwmio.PWMOut(board.D16, duty_cycle=2 ** 15, frequency=50) #D16
m8_pwm = pwmio.PWMOut(board.D20, duty_cycle=2 ** 15, frequency=50) #D20

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

################################################################################
# Setup neo pixels
num_px=10
led = neopixel_spi.NeoPixel_SPI(board.SPI(), num_px, brightness=1.0, auto_write=False)

################################################################################
# Sd card config variables

cfg = files.read_json_file("/home/pi/cfg.json")
print(cfg)

snd_opt = files.return_directory("", "/home/pi/snds", ".wav")

cust_snd_opt = files.return_directory(
    "customers_owned_music_", "/home/pi/customers_owned_music", ".wav")

all_snd_opt = []
all_snd_opt.extend(snd_opt)
all_snd_opt.extend(cust_snd_opt)

menu_snd_opt = []
menu_snd_opt.extend(snd_opt)
rnd_opt = ['random all', 'random built in', 'random my']
menu_snd_opt.extend(rnd_opt)
menu_snd_opt.extend(cust_snd_opt)

ts_jsons = files.return_directory(
    "", "/home/pi/t_s_def", ".json")

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/home/pi/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/home/pi/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file("/home/pi/mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    "/home/pi/mvc/add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False


################################################################################
# Setup wifi and web server

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

################################################################################
# Setup routes

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

def start_server():
    print(f"Serving on {local_ip}:{PORT}")
    httpd.serve_forever()

# Set up mDNS service info
desc = {'path': '/'}
info = ServiceInfo(
    "_http._tcp.local.",
    "animator-drive-in._http._tcp.local.",
    addresses=[socket.inet_aton(local_ip)],
    port=PORT,
    properties=desc,
    server="animator-drive-in.local."
)

# Register mDNS service
zeroconf = Zeroconf()
print("Registering mDNS service...")
zeroconf.register_service(info)

# Run the server in a separate thread to allow mDNS to work simultaneously
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

gc_col("web server")

################################################################################
# Global Methods


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods


def upd_vol(seconds):
    try:
        volume = int(cfg["volume"]) / 100
    except Exception as e:
        files.log_item(e)
        volume = .5
    if volume < 0 or volume > 1:
        volume = .5
    mix.voice[0].level = volume
    time.sleep(seconds)


def ch_vol(action):
    v = int(cfg["volume"])
    if "volume" in action:
        v = action.split("volume")
        v = int(v[1])
    if action == "lower1":
        v -= 1
    elif action == "raise1":
        v += 1
    elif action == "lower":
        if v <= 10:
            v -= 1
        else:
            v -= 10
    elif action == "raise":
        if v < 10:
            v += 1
        else:
            v += 10
    if v > 100:
        v = 100
    if v < 1:
        v = 1
    cfg["volume"] = str(v)
    cfg["volume_pot"] = False
    files.write_json_file("/home/pi/cfg.json", cfg)
    play_a_0("/home/pi/mvc/volume.wav")
    spk_str(cfg["volume"], False)


def play_a_0(file_name):
    if mix.voice[0].playing:
        mix.stop()
        while mix.voice[0].playing:
            upd_vol(0.1)
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(wave0, loop=False)
    while mix.voice[0].playing:
        exit_early()


def stop_a_0():
    mix.stop()
    while mix.voice[0].playing:
        pass


def exit_early():
    upd_vol(0.1)
    l_sw.update()
    if l_sw.fell:
        mix.stop()


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_a_0("/home/pi/mvc/" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        play_a_0("/home/pi/mvc/dot.wav")
        play_a_0("/home/pi/mvc/local.wav")


def l_r_but():
    play_a_0("/home/pi/mvc/press_left_button_right_button.wav")


def sel_web():
    play_a_0("/home/pi/mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    play_a_0("/home/pi/mvc/option_selected.wav")


def spk_sng_num(song_number):
    play_a_0("/home/pi/mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    play_a_0("/home/pi/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            play_a_0("/home/pi/mvc/create_sound_track_files.wav")
            break


def spk_web():
    play_a_0("/home/pi/mvc/animator_available_on_network.wav")
    play_a_0("/home/pi/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-bandstand":
        play_a_0("/home/pi/mvc/animator_dash_bandstand.wav")
        play_a_0("/home/pi/mvc/dot.wav")
        play_a_0("/home/pi/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_a_0("/home/pi/mvc/in_your_browser.wav")    

while True:
    if not media_player.is_playing() and run_movie_cont:
        print("play movies: " + str(run_movie_cont))
        play_movies()
        while not media_player.is_playing():
            time.sleep(.5)
    l_s.update()
    r_s.update()
    w_s.update()
    b_s.update()
    if l_s.fell:
        if media_player.is_playing(): pause_movie()
        run_movie_cont = True
        print ("left fell")
    if r_s.fell:
        print ("right fell")
        if media_player.is_playing():
            run_movie_cont = False
            pause_movie()
        else:
            play_movie()
            rainbow(.005,5)
    if w_s.fell:
        print ("white fell")
        volume = volume - 10
        if volume < 0: volume = 0
        media_player.audio_set_volume(volume)
    if b_s.fell:
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
