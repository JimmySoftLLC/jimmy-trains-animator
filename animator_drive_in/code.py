# MIT License
#
# Copyright (c) 2024 JimmySoftLLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#######################################################
# this code requires the following installs

# blinka is a lib that allows you to use circuit python libraries for servos, light etc. search adafruit blinka for instructions

# control lifx lights using lifxlan 1.2.7 and confirm its version
# pip install lifxlan==1.2.7
# pip show lifxlan

# to use lifx lan you must use the bytestring 3.1.9 library and confirm its version
# pip install bitstring==3.1.9
# pip show bitstring

# on screen keyboard, onboard
# sudo apt install onboard

# text to speech using gtts 2.5.3 and confirm its version
# pip install gtts
# pip show gtts

# Units with a touchscreen use a html page and material UI for styling
# Midori, a lightweight browser, is used so it can run on any pi
# install midori and confirm its version
# sudo apt install midori==7.0
# midori --version

# Scripts can be modified via a webpage that the drivein will serve to your location network.
# It might be easier to use a spreadsheet program.  So install libra office on the pi so
# customers can use it to modify scripts too.
# Install with
# sudo apt update
# sudo apt install libreoffice


# for touch screen products the display on vnc will default to the touch screen
# resolution which is very low.  During dev you might want to use these three commands
# to set it higher, note these will reset at reboot.  Do not make these permanent.
# xrandr --newmode "1920x1080_60.00"  173.00  1920 2048 2248 2576  1080 1083 1088 1120 -hsync +vsync
# xrandr --addmode HDMI-1 "1920x1080_60.00"
# xrandr --output HDMI-1 --mode "1920x1080_60.00"

# i2s audio is setup on pi itself using an overlay, there is no hardware that needs to be set up in python
# the i2s amps are on the JimmyTrains ANPISBC HAT which provides the audio.  The amps have an audio enable
# feature that is contorlled via pin 26.  It is enabled by this program just before it annouces the animations are active
# The volume is also controlled by this program.  So the volume control on the pi has no effect.
# The amp circuits are set to the highest possible gain so audio tracks and movies should be normalized to -8.0dB to avoid
# clipping.

#######################################################
# prod files are located in the code folder on the user machine
# debug the code.py, files.py and utilities.py in the home directory
# Delete code.py, files.py and utilities.py in the home directory after release


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
import random
from gtts import gTTS
import requests
import signal
from lifxlan import BLUE, CYAN, GREEN, LifxLAN, ORANGE, PINK, PURPLE, RED, YELLOW
import sys

aud_en = digitalio.DigitalInOut(board.D26)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False


def get_home_path(subpath=""):
    # Get the current user's home directory
    home_dir = os.path.expanduser("~")
    # Return the full path by appending the optional subpath
    return os.path.join(home_dir, subpath)


code_folder = get_home_path() + "code/"
media_folder = get_home_path() + "media/"

def f_exists(filename):
    try:
        status = os.stat(filename)
        f_exists = True
    except OSError:
        f_exists = False
    return f_exists


def gc_col(collection_point):
    gc.collect()
    start_mem = psutil.virtual_memory()[1]
    print("Point " + collection_point +
          " Available memory: {} bytes".format(start_mem))


def restart_pi():
    os.system('sudo reboot')


def restart_pi_timer():
    delay = 5
    timer = threading.Timer(delay, restart_pi)
    timer.start()


gc_col("Imports gc, files")

################################################################################
# config variables

cfg = files.read_json_file(code_folder + "cfg.json")

def get_media_files(main_folder, extensions):
    media_dict = {}
    
    # Normalize extensions (e.g., ensure they all start with a dot)
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    # Loop through each folder (topic) in the main media directory
    for topic in os.listdir(main_folder):
        topic_path = os.path.join(main_folder, topic)
        
        # Ensure it's a directory before proceeding
        if os.path.isdir(topic_path):
            # Get all files that match the specified extensions
            files = [f for f in os.listdir(topic_path)
                     if os.path.isfile(os.path.join(topic_path, f)) and f.lower().endswith(tuple(extensions))]
            media_dict[topic] = files
    
    return media_dict


def upd_media():
    extensions = ['.mp3', '.wav', '.mp4']  # List of extensions to filter by
    media_files = get_media_files(media_folder, extensions)
    print(media_files)

    global sndtrk_opt, plylst_opt, mysndtrk_opt, all_snd_opt, menu_snd_opt
    sndtrk_opt = files.return_directory(
        "", media_folder + "sndtrk", ".wav", False)
    video_opt = files.return_directory(
        "", media_folder + "sndtrk", ".mp4", False)
    sndtrk_opt.extend(video_opt)
    # print("Sound tracks: " + str(sndtrk_opt))

    plylst_opt = files.return_directory(
        "plylst_", media_folder + "plylst", ".json", True)
    # print("Play lists: " + str(plylst_opt))

    mysndtrk_opt = files.return_directory(
        "customers_owned_music_", media_folder + "customers_owned_music", ".wav", False)
    myvideo_opt = files.return_directory(
        "customers_owned_music_", media_folder + "customers_owned_music", ".mp4", False)
    mysndtrk_opt.extend(myvideo_opt)
    # print("My sound tracks: " + str(mysndtrk_opt))

    all_snd_opt = []
    all_snd_opt.extend(plylst_opt)
    all_snd_opt.extend(sndtrk_opt)
    all_snd_opt.extend(mysndtrk_opt)

    menu_snd_opt = []
    menu_snd_opt.extend(files.return_directory(
        "", media_folder + "plylst", ".json", False, ".mp3"))
    menu_snd_opt.extend(files.return_directory(
        "", media_folder + "sndtrk", ".wav", False))
    rnd_opt = ['rnd plylst.wav', 'random built in.wav',
               'random my.wav', 'random all.wav']
    menu_snd_opt.extend(rnd_opt)

    # print("Menu sound tracks: " + str(menu_snd_opt))


upd_media()

web = cfg["serve_webpage"]

cfg_main = files.read_json_file(code_folder + "mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(code_folder + "mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file(code_folder + "mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    code_folder + "mvc/add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False
lst_opt = ''
an_running = False
is_gtts_reachable = False
stop_play_list = False

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

l_sw = Debouncer(switch_io_1)
r_sw = Debouncer(switch_io_2)
w_sw = Debouncer(switch_io_3)
b_sw = Debouncer(switch_io_4)

################################################################################
# Setup sound

# Setup the mixer to play wav files
pygame.mixer.init()
mix = pygame.mixer.music

################################################################################
# Setup video hardware

# create vlc media player object for playing video, music etc
instance = vlc.Instance()
media_player = vlc.MediaPlayer(instance)


def play_movie_file(movie_filename):
    global media_player

    # Release the media player to reset state before the next video
    media_player.release()

    # Create a fresh VLC instance and media player for each video
    instance = vlc.Instance()
    media_player = vlc.MediaPlayer(instance)
    media_player.toggle_fullscreen()

    # Load media
    media = instance.media_new(movie_filename)
    media_player.set_media(media)

    # Set the volume explicitly for each media file
    upd_vol(0.05)

    # Play the video
    media_player.play()

    while not media_player.is_playing():
        time.sleep(.05)


def pause_movie():
    media_player.pause()


def play_movie():
    media_player.play()


################################################################################
# Setup servo hardware
m1_pwm = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50)  # D23
m2_pwm = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=50)  # D24
m3_pwm = pwmio.PWMOut(board.D23, duty_cycle=2 ** 15, frequency=50)  # D25
m4_pwm = pwmio.PWMOut(board.D24, duty_cycle=2 ** 15, frequency=50)  # D6
m5_pwm = pwmio.PWMOut(board.D25, duty_cycle=2 ** 15, frequency=50)  # D13
m6_pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=50)  # D12
m7_pwm = pwmio.PWMOut(board.D16, duty_cycle=2 ** 15, frequency=50)  # D16
m8_pwm = pwmio.PWMOut(board.D20, duty_cycle=2 ** 15, frequency=50)  # D20

m1_servo = servo.Servo(m1_pwm)
m2_servo = servo.Servo(m2_pwm)
m3_servo = servo.Servo(m3_pwm)
m4_servo = servo.Servo(m4_pwm)
m5_servo = servo.Servo(m5_pwm)
m6_servo = servo.Servo(m6_pwm)
m7_servo = servo.Servo(m7_pwm)
m8_servo = servo.Servo(m8_pwm)

m1_servo.angle = 90
m2_servo.angle = 90
m3_servo.angle = 90
m4_servo.angle = 90
m5_servo.angle = 90
m6_servo.angle = 90
m7_servo.angle = 90
m8_servo.angle = 90

################################################################################
# Setup neo pixels

trees = []
canes = []
ornmnts = []
stars = []
brnchs = []
cane_s = []
cane_e = []

bars = []
bolts = []
noods = []
neos = []

bar_arr = []
bolt_arr = []
neo_arr = []

n_px = 0
led = neopixel_spi.NeoPixel_SPI(
    board.SPI(), n_px, brightness=1.0, auto_write=False)


def bld_tree(p):
    i = []
    for t in trees:
        for ledi in t:
            si = ledi
            break
        if p == "ornaments":
            for ledi in range(0, 7):
                i.append(ledi+si)
        if p == "star":
            for ledi in range(7, 14):
                i.append(ledi+si)
        if p == "branches":
            for ledi in range(14, 21):
                i.append(ledi+si)
    return i


def bld_cane(p):
    i = []
    for c in canes:
        for led_i in c:
            si = led_i
            break
        if p == "end":
            for led_i in range(0, 2):
                i.append(led_i+si)
        if p == "start":
            for led_i in range(2, 4):
                i.append(led_i+si)
    return i


def bld_bar():
    i = []
    for b in bars:
        for l in b:
            si = l
            break
        for l in range(0, 10):
            i.append(l+si)
    return i


def bld_bolt():
    i = []
    for b in bolts:
        for l in b:
            si = l
            break
        if len(b) == 4:
            for l in range(0, 4):
                i.append(l+si)
        if len(b) == 1:
            for l in range(0, 1):
                i.append(l+si)
    return i


def bld_neo():
    i = []
    for n in neos:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l+si)
    return i


def show_l():
    led.show()
    time.sleep(.3)
    led.fill((0, 0, 0))
    led.show()


def l_tst():
    global ornmnts, stars, brnchs, cane_s, cane_e, bar_arr, bolt_arr, neo_arr

    # Christmas items
    ornmnts = bld_tree("ornaments")
    stars = bld_tree("star")
    brnchs = bld_tree("branches")
    cane_s = bld_cane("start")
    cane_e = bld_cane("end")

    # Lightning items
    bar_arr = bld_bar()
    bolt_arr = bld_bolt()

    # Neo items
    neo_arr = bld_neo()

    # cane test
    cnt = 0
    for i in cane_s:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0
    for i in cane_e:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0

    # tree test
    cnt = 0
    for i in ornmnts:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in stars:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in brnchs:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0

    # bar test
    for b in bars:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # bolt test
    for b in bolts:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # nood test
    for n in noods:
        led[n[0]] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # neo test
    for n in neos:
        for i in n:
            led[i] = (0, 50, 0)
            time.sleep(.3)
            led.show()
            led[i] = (50, 0, 0)
            time.sleep(.3)
            led.show()
            led[i] = (0, 0, 50)
            time.sleep(.3)
            led.show()
            time.sleep(.3)
            led.fill((0, 0, 0))
            led.show()


def upd_l_str():
    global trees, canes, bars, bolts, noods, neos, n_px, led
    trees = []
    canes = []
    bars = []
    bolts = []
    noods = []
    neos = []

    n_px = 0

    els = cfg["light_string"].split(',')

    for el in els:
        p = el.split('-')
        if len(p) == 2:
            typ, qty = p
            qty = int(qty)
            if typ == 'grandtree':
                s = list(range(n_px, n_px + qty))
                trees.append(s)
                n_px += qty
            elif typ == 'cane':
                s = list(range(n_px, n_px + qty))
                canes.append(s)
                n_px += qty
            if typ == 'bar':
                s = list(range(n_px, n_px + qty))
                bars.append(s)
                n_px += qty
            elif typ == 'bolt' and qty < 4:
                s = [n_px, qty]
                noods.append(s)
                n_px += 1
            elif typ == 'bolt' and qty == 4:
                s = list(range(n_px, n_px + qty))
                bolts.append(s)
                n_px += qty
            if typ == 'neo':
                if qty == 6:
                    neoqty = 2
                if qty == 12:
                    neoqty = 4
                s = list(range(n_px, n_px + neoqty))
                neos.append(s)
                n_px += neoqty

    print("Number of pixels total: ", n_px)
    led = None
    led = neopixel_spi.NeoPixel_SPI(
        board.SPI(), n_px, brightness=1.0, auto_write=False)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()


upd_l_str()

gc_col("Neopixels setup")


################################################################################
# Setup lifx lights

def test_lifx():
    num_lights = 18
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)

    # get devices
    devices = lifx.get_lights()
    bulb = devices[0]
    print("Selected {}".format(bulb.get_label()))

    # get original state
    print("Turning on all lights...")
    original_power = bulb.get_power()
    original_color = bulb.get_color()
    bulb.set_power("on")

    time.sleep(1)  # for looks

    print("Flashy fast rainbow")
    rainbow(bulb, 0.1)

    print("Smooth slow rainbow")
    rainbow(bulb, 1, smooth=True)

    print("Restoring original power and color...")
    # restore original power
    bulb.set_power(original_power)
    # restore original color
    time.sleep(0.5)  # for looks
    bulb.set_color(original_color)


def rainbow(bulb, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs*1000 if smooth else 0
    rapid = True if duration_secs < 1 else False
    for color in colors:
        bulb.set_color(color, transition_time_ms, rapid)
        time.sleep(duration_secs)


def discover_lights():
    # Initialize the LifxLAN object
    lifx = LifxLAN(20)

    # Discover LIFX devices on the local network
    devices = lifx.get_devices()

    # Report the count of discovered devices
    device_count = len(devices)
    print(f"Discovered {device_count} device(s).")

    # Iterate over each discovered device and control it
    for device in devices:
        print(f"Found device: {device.get_label()}")

        # Set light to a specific color (red in this case)
        # (Hue, Saturation, Brightness, Kelvin)
        # device.set_color([65535, 65535, 65535, 3500])
        # device.set_power("on")

# test_lifx()


################################################################################
# Setup wifi and web server

def wait_for_network():
    while True:
        try:
            # Attempt to connect to Google's public DNS server to check network availability
            socket.create_connection(("8.8.8.8", 53))
            print("Network is ready!")
            return
        except OSError:
            print("Waiting for network...")
            time.sleep(1)


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
        if self.path == "/":
            print(self.path)
            self.handle_serve_file("/code/index.html")
        elif self.path.endswith(".css"):
            print(self.path)
            self.handle_serve_file("/code" + self.path, "text/css")
        elif self.path.endswith(".js"):
            print(self.path)
            self.handle_serve_file("/code" + self.path,
                                   "application/javascript")
        else:
            self.handle_serve_file(self.path)

    def do_POST(self):
        if self.path == "/upload":
            self.handle_file_upload()
        else:
            self.handle_generic_post(self.path)

    def handle_serve_file(self, path, content_type="text/html"):
        file_path = path.lstrip("/")
        try:
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

    def handle_serve_file_name(self, f_n, content_type="text/html"):
        try:
            with open(f_n, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def handle_file_upload(self):
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
                            file_name = disposition.split(
                                'filename=')[1].strip('"')
                            # Ensure the uploads directory exists
                            os.makedirs("uploads", exist_ok=True)
                            file_path = os.path.join("uploads", file_name)

                            with open(file_path, "wb") as f:
                                f.write(content)

                            self.send_response(200)
                            self.send_header(
                                "Content-type", "application/json")
                            self.end_headers()
                            response = {"status": "success",
                                        "message": "File uploaded successfully"}
                            self.wfile.write(json.dumps(
                                response).encode('utf-8'))
                            return

            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "No file part"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()

    def handle_generic_post(self, path):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received POST data: {post_data.decode('utf-8')}")
        # Decode the byte string to a regular string
        post_data_obj = {}
        post_data_str = post_data.decode('utf-8')
        if post_data_str != '':
            post_data_obj = json.loads(post_data_str)
        if self.path == "/animation":
            self.animation_post(post_data_obj)
        elif self.path == "/mode":
            self.mode_post(post_data_obj)
        elif self.path == "/defaults":
            self.defaults_post(post_data_obj)
        elif self.path == "/get-built-in-sound-tracks":
            self.get_built_in_sound_tracks_post(post_data_obj)
        elif self.path == "/get-customers-sound-tracks":
            self.get_customers_sound_tracks_post(post_data_obj)
        elif self.path == "/speaker":
            self.speaker_post(post_data_obj)
        elif self.path == "/get-light-string":
            self.get_light_string_post(post_data_obj)
        elif self.path == "/update-host-name":
            self.update_host_name_post(post_data_obj)
        elif self.path == "/update-light-string":
            self.update_light_string_post(post_data_obj)
        elif self.path == "/defaults":
            self.defaults_post(post_data_obj)
        elif self.path == "/lights":
            self.lights_post(post_data_obj)
        elif self.path == "/update-host-name":
            self.update_host_name_post(post_data_obj)
        elif self.path == "/get-host-name":
            self.get_host_name_post(post_data_obj)
        elif self.path == "/update-volume":
            self.update_volume_post(post_data_obj)
        elif self.path == "/get-volume":
            self.get_volume_post(post_data_obj)
        elif self.path == "/get-scripts":
            self.get_scripts_post(post_data_obj)
        elif self.path == "/create-playlist":
            self.create_playlist_post(post_data_obj)
        elif self.path == "/get-animation":
            self.get_animation_post(post_data_obj)
        elif self.path == "/delete-playlist":
            self.delete_playlist_post(post_data_obj)
        elif self.path == "/save-data":
            self.save_data_post(post_data_obj)
        elif self.path == "/rename-playlist":
            self.rename_playlist_post(post_data_obj)
        elif self.path == "/stop":
            self.stop_post(post_data_obj)
        elif self.path == "/test-animation":
            self.test_animation_post(post_data_obj)

    def test_animation_post(self, rq_d):
        global an_running
        an_running = True
        set_hdw(rq_d["an"], 3)
        an_running = True
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "Set hardware: " + rq_d["an"]
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    def stop_post(self, rq_d):
        rst_an()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "rst an"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    def rename_playlist_post(self, rq_d):
        global data
        snd = rq_d["fo"].replace("plylst_", "")
        fo = media_folder + "plylst/" + snd + ".json"
        fn = media_folder + "plylst/" + rq_d["fn"] + ".json"
        mp3_name = media_folder + "o_snds/" + rq_d["fn"] + ".mp3"
        text_to_mp3_file(mp3_name, timeout_duration=5)
        os.rename(fo, fn)
        upd_media()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "your response message"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    data = []

    def save_data_post(self, rq_d):
        global data
        try:
            if rq_d[0] == 0:
                data = []
            data.extend(rq_d[2])
            if rq_d[0] == rq_d[1]:
                f_n = ""
                an = rq_d[3].split("_")
                if "plylst" == an[0]:
                    snd_f = rq_d[3].replace("plylst_", "")
                    snd_f = snd_f.replace(".mp3", "")
                    snd_f = snd_f.replace(".mp4", "")
                    snd_f = snd_f.replace(".wav", "")
                    f_n = media_folder + "plylst/" + \
                        snd_f + ".json"
                elif "customers" == an[0]:
                    snd_f = rq_d[3].replace("customers_owned_music_", "")
                    snd_f = snd_f.replace(".mp3", "")
                    snd_f = snd_f.replace(".mp4", "")
                    snd_f = snd_f.replace(".wav", "")
                    f_n = media_folder + "customers_owned_music/" + \
                        snd_f + ".json"
                else:
                    snd_f = rq_d[3].replace(".mp3", "")
                    snd_f = snd_f.replace(".mp4", "")
                    snd_f = snd_f.replace(".wav", "")
                    f_n = media_folder + "sndtrk/" + \
                        snd_f + ".json"
                files.write_json_file(f_n, data)
                upd_media()
                data = []
        except:
            data = []
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            response = "out of memory"
            self.wfile.write(response.encode('utf-8'))
            print("Response sent:", response)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "success"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    def delete_playlist_post(self, rq_d):
        snd_f = rq_d["fn"].replace("plylst_", "")
        f_n = media_folder + "plylst/" + snd_f + ".json"
        os.remove(f_n)
        upd_media()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["fn"] + " playlist file deleted"
        self.wfile.write(response.encode('utf-8'))

    def get_animation_post(self, rq_d):
        global cfg, cont_run, ts_mode
        snd_f = rq_d["an"]
        if "plylst_" in snd_f:
            snd_f = snd_f.replace("plylst_", "")
            if (f_exists(media_folder + "plylst/" + snd_f + ".json") == True):
                f_n = media_folder + "plylst/" + snd_f + ".json"
                self.handle_serve_file_name(f_n)
                return
            else:
                f_n = media_folder + "t_s_def/timestamp mode.json"
                self.handle_serve_file_name(f_n)
                return
        if "customers_owned_music_" in snd_f:
            snd_f = snd_f.replace("customers_owned_music_", "")
            snd_f = snd_f.replace(".mp3", "")
            snd_f = snd_f.replace(".mp4", "")
            snd_f = snd_f.replace(".wav", "")
            if (f_exists(media_folder + "customers_owned_music/" + snd_f + ".json") == True):
                f_n = media_folder + "customers_owned_music/" + snd_f + ".json"
                self.handle_serve_file_name(f_n)
            else:
                f_n = media_folder + "t_s_def/timestamp mode.json"
                self.handle_serve_file_name(f_n)
                return
        else:
            snd_f = snd_f.replace(".mp3", "")
            snd_f = snd_f.replace(".mp4", "")
            snd_f = snd_f.replace(".wav", "")
            if (f_exists(media_folder + "sndtrk/" + snd_f + ".json") == True):
                f_n = media_folder + "sndtrk/" + snd_f + ".json"
                self.handle_serve_file_name(f_n)
                return
            else:
                f_n = media_folder + "t_s_def/timestamp mode.json"
                self.handle_serve_file_name(f_n)
                return

    def get_scripts_post(self, rq_d):
        sounds = []
        sounds.extend(plylst_opt)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = sounds
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def create_playlist_post(self, rq_d):
        global data
        f_n = media_folder + "plylst/" + rq_d["fn"] + ".json"
        files.write_json_file(f_n, ["0.0|", "1.0|"])
        upd_media()
        gc_col("created playlist")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "created " + rq_d["fn"] + " playlist"
        self.wfile.write(response.encode('utf-8'))

    def update_light_string_post(self, rq_d):
        global cfg
        if rq_d["action"] == "save" or rq_d["action"] == "clear" or rq_d["action"] == "defaults":
            cfg["light_string"] = rq_d["text"]
            print("action: " +
                  rq_d["action"] + " data: " + cfg["light_string"])
            files.write_json_file(code_folder + "cfg.json", cfg)
            upd_l_str()
            play_a_0(code_folder + "mvc/all_changes_complete.wav")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            response = cfg["light_string"]
            self.wfile.write(response.encode('utf-8'))
            return
        if cfg["light_string"] == "":
            cfg["light_string"] = rq_d["text"]
        else:
            cfg["light_string"] = cfg["light_string"] + \
                "," + rq_d["text"]
        print("action: " + rq_d["action"] +
              " data: " + cfg["light_string"])
        files.write_json_file(code_folder + "cfg.json", cfg)
        upd_l_str()
        play_a_0(code_folder + "mvc/all_changes_complete.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["light_string"]
        self.wfile.write(response.encode('utf-8'))

    def mode_post(self, rq_d):
        print(rq_d)
        global cfg, cont_run, ts_mode
        if rq_d["an"] == "cont_mode_on":
            play_a_0(code_folder + "mvc/continuous_mode_activated.wav")
            cont_run = True
        elif rq_d["an"] == "cont_mode_off":
            play_a_0(code_folder + "mvc/continuous_mode_deactivated.wav")
            cont_run = False
        elif rq_d["an"] == "timestamp_mode_on":
            play_a_0(code_folder + "mvc/timestamp_mode_on.wav")
            play_a_0(code_folder + "mvc/timestamp_instructions.wav")
            ts_mode = True
        elif rq_d["an"] == "timestamp_mode_off":
            play_a_0(code_folder + "mvc/timestamp_mode_off.wav")
            ts_mode = False
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"mode processed": rq_d["an"]}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def animation_post(self, rq_d):
        global cfg, cont_run, ts_mode, stop_play_list
        cfg["option_selected"] = rq_d["an"]
        stop_play_list = False
        an(cfg["option_selected"])
        files.write_json_file(code_folder + "cfg.json", cfg)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"Ran animation": cfg["option_selected"]}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def defaults_post(self, rq_d):
        global cfg
        if rq_d["an"] == "reset_to_defaults":
            rst_def()
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_a_0(code_folder + "mvc/all_changes_complete.wav")
            st_mch.go_to('base_state')
        self.wfile.write("Utility: " + rq_d["an"])

    def speaker_post(self, rq_d):
        global cfg
        if rq_d["an"] == "speaker_test":
            cmd_snt = "speaker_test"
            play_a_0(code_folder + "mvc/left_speaker_right_speaker.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def get_light_string_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["light_string"]
        self.wfile.write(response.encode('utf-8'))

    def update_host_name_post(self, rq_d):
        global cfg
        cfg["HOST_NAME"] = rq_d["text"]
        files.write_json_file(code_folder + "cfg.json", cfg)
        spk_web()
        restart_pi_timer()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["HOST_NAME"]
        self.wfile.write(response.encode('utf-8'))

    def get_host_name_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["HOST_NAME"]
        self.wfile.write(response.encode('utf-8'))

    def update_volume_post(self, rq_d):
        global cfg
        ch_vol(rq_d["action"])
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["volume"]
        self.wfile.write(response.encode('utf-8'))

    def get_volume_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["volume"]
        self.wfile.write(response.encode('utf-8'))

    def get_customers_sound_tracks_post(self, rq_d):
        upd_media()
        response = []
        response.extend(mysndtrk_opt)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_built_in_sound_tracks_post(self, rq_d):
        upd_media()
        response = []
        response.extend(sndtrk_opt)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def defaults_post(self, rq_d):
        global cfg
        if rq_d["an"] == "reset_to_defaults":
            rst_def()
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_a_0(code_folder + "mvc/all_changes_complete.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "reset_to_defaults"
        self.wfile.write(response.encode('utf-8'))

    def lights_post(self, rq_d):
        set_hdw(rq_d["an"], 1)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))


# Get the local IP address
local_ip = get_local_ip()
print(f"Local IP address: {local_ip}")

# Set up the HTTP server
PORT = 8083  # Use port 80 for default HTTP access
handler = MyHttpRequestHandler
httpd = socketserver.TCPServer((local_ip, PORT), handler)
httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def start_server():
    print(f"Serving on {local_ip}:{PORT}")
    httpd.serve_forever()


# Set up mDNS service info
name_str = cfg["HOST_NAME"] + "._http._tcp.local."
server_str = cfg["HOST_NAME"] + ".local."
desc = {'path': '/'}
info = ServiceInfo(
    "_http._tcp.local.",
    name_str,
    addresses=[socket.inet_aton(local_ip)],
    port=PORT,
    properties=desc,
    server=server_str
)


gc_col("web server")

################################################################################
# Global Methods


def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-drive-in"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods


def upd_vol(seconds):
    volume = int(cfg["volume"])
    mix.set_volume(volume/100)
    media_player.audio_set_volume(volume)
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
    upd_vol(.01)
    files.write_json_file(code_folder + "cfg.json", cfg)
    play_a_0(code_folder + "mvc/volume.wav")
    spk_str(cfg["volume"], False)


def play_a_0(file_name, wait_until_done=True, allow_exit=True):
    print("playing " + file_name)
    if mix.get_busy():
        stop_media()
        while mix.get_busy():
            time.sleep(0.1)
    mix.load(file_name)
    upd_vol(.001)
    mix.play(loops=0)
    while mix.get_busy() and wait_until_done:
        if allow_exit:
            exit_early()
    print("done playing")


def wait_snd():
    while mix.get_busy():
        exit_early()
    print("done playing")


def stop_media():
    media_player.stop()
    mix.stop()
    while mix.get_busy() or media_player.is_playing():
        pass


def exit_early():
    l_sw.update()
    r_sw.update()
    if l_sw.fell:
        stop_media()
    time.sleep(0.1)


def rst_an():
    stop_media()
    led.fill((0, 0, 0))
    led.show()


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_a_0(code_folder + "mvc/" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        play_a_0(code_folder + "mvc/dot.wav")
        play_a_0(code_folder + "mvc/local.wav")


def l_r_but():
    play_a_0(code_folder + "mvc/press_left_button_right_button.wav")


def sel_web():
    play_a_0(code_folder + "mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    play_a_0(code_folder + "mvc/option_selected.wav")


def spk_sng_num(song_number):
    play_a_0(code_folder + "mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    play_a_0(code_folder + "mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            play_a_0(code_folder + "mvc/create_sound_track_files.wav")
            break


def spk_web():
    play_a_0(code_folder + "mvc/animator_available_on_network.wav")
    play_a_0(code_folder + "mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-drive-in":
        play_a_0(code_folder + "mvc/animator_dash_drive_dash_in.wav")
        play_a_0(code_folder + "mvc/dot.wav")
        play_a_0(code_folder + "mvc/local.wav")
        play_a_0(code_folder + "mvc/colon_8083.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_a_0(code_folder + "mvc/in_your_browser.wav")


###############################################################################
# Text to speech


def check_gtts_status():
    try:
        # gTTS API endpoint
        url = "https://translate.google.com"

        # Send a simple GET request
        response = requests.get(url, timeout=5)

        # Check the status code
        if response.status_code == 200:
            print("gTTS service is reachable.")
            return True
        else:
            print("gTTS service returned an unexpected status code: " +
                  response.status_code)
            return False

    except requests.ConnectionError:
        print("Failed to connect to gTTS service.")
        return False
    except requests.Timeout:
        print("The request to gTTS service timed out.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Custom exception for timeout
class TimeoutException(Exception):
    pass


# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutException("The operation timed out!")


# Set up a signal to call the handler after a timeout
signal.signal(signal.SIGALRM, timeout_handler)


def text_to_mp3_file(f_nm, timeout_duration):
    global is_gtts_reachable
    try:
        # Set the timeout (in seconds)
        signal.alarm(timeout_duration)

        # Convert text to mp3 file
        text = files.strip_path_and_extension(f_nm)
        tts = gTTS(text=text, lang='en')
        tts.save(f_nm)

        # Cancel the alarm if operation completes before timeout
        signal.alarm(0)

        play_a_0(f_nm)

    except TimeoutException:
        print("TTS operation timed out.")
        is_gtts_reachable = False
    except Exception as e:
        print(f"An error occurred: {e}")
        is_gtts_reachable = False


################################################################################
# Animation methods

def rst_an():
    stop_media()
    media_player.stop()
    led.fill((0, 0, 0))
    led.show()


def an(f_nm):
    global cfg, lst_opt, an_running
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random built in":
            h_i = len(sndtrk_opt) - 1
            cur_opt = sndtrk_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(sndtrk_opt) > 1:
                cur_opt = sndtrk_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        elif f_nm == "random my":
            h_i = len(mysndtrk_opt) - 1
            cur_opt = mysndtrk_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(mysndtrk_opt) > 1:
                cur_opt = mysndtrk_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        elif f_nm == "rnd plylst":
            h_i = len(plylst_opt) - 1
            cur_opt = plylst_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(plylst_opt) > 1:
                cur_opt = plylst_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            files.log_item("Random sound option: " + f_nm)
            files.log_item("Sound file: " + cur_opt)
        elif f_nm == "random all":
            h_i = len(all_snd_opt) - 1
            cur_opt = all_snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(all_snd_opt) > 1:
                cur_opt = all_snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            an_light(cur_opt)
            gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")


def an_light(f_nm):
    global ts_mode, an_running
    an_running = True
    if stop_play_list:
        return

    time.sleep(.1)

    cust_f = "customers_owned_music_" in f_nm
    plylst_f = "plylst_" in f_nm
    is_video = ".mp4" in f_nm
    json_fn = f_nm.replace(".mp4", "")
    json_fn = json_fn.replace(".wav", "")
    json_fn = json_fn.replace("customers_owned_music_", "")

    flsh_t = []

    if cust_f:
        f_nm = f_nm.replace("customers_owned_music_", "")
        if (f_exists(media_folder + "customers_owned_music/" + json_fn + ".json") == True):
            flsh_t = files.read_json_file(
                media_folder + "customers_owned_music/" + json_fn + ".json")
        else:
            try:
                flsh_t = files.read_json_file(
                    media_folder + "customers_owned_music/" + json_fn + ".json")
            except Exception as e:
                files.log_item(e)
                play_a_0(code_folder +
                         "mvc/no_timestamp_file_found.wav", True, False)
                time.sleep(.1)
                while True:
                    l_sw.update()
                    r_sw.update()
                    if l_sw.fell:
                        ts_mode = False
                        an_running = False
                        return
                    if r_sw.fell:
                        ts_mode = True
                        an_running = False
                        play_a_0(code_folder + "mvc/timestamp_instructions.wav")
                        return
    elif plylst_f:
        f_nm = f_nm.replace("plylst_", "")
        flsh_t = files.read_json_file(media_folder + "plylst/" + f_nm + ".json")
    else:
        if (f_exists(media_folder + "sndtrk/" + json_fn + ".json") == True):
            flsh_t = files.read_json_file(
                media_folder + "sndtrk/" + json_fn + ".json")

    flsh_i = 0

    ft1 = []
    ft2 = []

    ft1 = flsh_t[len(flsh_t)-1].split("|")
    tm = float(ft1[0]) + 1
    flsh_t.append(str(tm) + "|E")
    flsh_t.append(str(tm + 1) + "|E")

    if not plylst_f:
        if cust_f:
            media0 = media_folder + "customers_owned_music/" + f_nm
        else:
            media0 = media_folder + "sndtrk/" + f_nm
        if is_video:
            play_movie_file(media0)
        else:
            play_a_0(media0, False)

    srt_t = time.monotonic()  # perf_counter

    while True:
        t_past = time.monotonic()-srt_t

        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0
        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            t_elaspsed = "{:.1f}".format(t_past)
            files.log_item("Time elapsed: " + str(t_elaspsed) +
                           " Timestamp: " + ft1[0])
            resp = set_hdw(ft1[1], dur)
            if resp == "STOP":
                rst_an()
                time.sleep(.2)
                an_running = False
                return
            flsh_i += 1
        if not mix.get_busy() and not media_player.is_playing() and not plylst_f and not an_running:
            mix.stop()
            media_player.stop()
            rst_an()
            time.sleep(.2)
            an_running = False
            return "DONE"
        if flsh_i > len(flsh_t)-1:
            mix.stop()
            media_player.stop()
            rst_an()
            time.sleep(.2)
            an_running = False
            return "DONE"
        time.sleep(.1)


def an_ts(f_nm):
    print("time stamp mode")
    global ts_mode, an_running
    an_running = True

    cust_f = "customers_owned_music_" in f_nm
    is_video = ".mp4" in f_nm
    json_fn = f_nm.replace(".mp4", "")
    json_fn = json_fn.replace(".wav", "")
    json_fn = json_fn.replace("customers_owned_music_", "")

    t_s = []

    f_nm = f_nm.replace("customers_owned_music_", "")

    if cust_f:
        media0 = media_folder + "customers_owned_music/" + f_nm
    else:
        media0 = media_folder + "sndtrk/" + f_nm

    if is_video:
        play_movie_file(media0)
    else:
        play_a_0(media0, False)

    startTime = time.perf_counter()
    time.sleep(.1)

    while True:
        t_elsp = round(time.perf_counter()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            files.log_item(t_elsp)
        if not mix.get_busy() and not media_player.is_playing():
            led.fill((0, 0, 0))
            led.show()
            if cust_f:
                files.write_json_file(
                    media_folder + "customers_owned_music/" + json_fn + ".json", t_s)
            else:
                files.write_json_file(
                    media_folder + "sndtrk/" + json_fn + ".json", t_s)
            break

    ts_mode = False
    rst_an()
    play_a_0(code_folder + "mvc/timestamp_saved.wav")
    play_a_0(code_folder + "mvc/timestamp_mode_off.wav")
    play_a_0(code_folder + "mvc/animations_are_now_active.wav")


###############
# Animation helpers

br = 0


def is_neo(number, nested_array):
    return any(number in sublist for sublist in nested_array)


def set_all_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):  # in range(n_px)
            if is_neo(i, neos):
                led[i] = (g, r, b)
            else:
                led[i] = (r, g, b)
    else:
        if is_neo(light_n, neos):
            led[light_n] = (g, r, b)
        else:
            led[light_n] = (r, g, b)
    led.show()


def get_neo_ids():
    matches = []
    for num in range(n_px + 1):
        if any(num == sublist[0] for sublist in neos):
            matches.append(num)
    return matches


def set_neo_module(mod_n, ind, v):
    cur = []
    neo_ids = get_neo_ids()
    print(mod_n, ind, v, neo_ids)
    if mod_n == 0:
        for i in neo_ids:
            led[i] = (v, v, v)
            led[i+1] = (v, v, v)
    elif ind == 0:
        led[neo_ids[mod_n-1]] = (v, v, v)
        led[neo_ids[mod_n-1]+1] = (v, v, v)
    elif ind < 4:
        ind -= 1
        if ind == 0:
            ind = 1
        elif ind == 1:
            ind = 0
        cur = list(led[neo_ids[mod_n-1]])
        cur[ind] = v
        led[neo_ids[mod_n-1]] = (cur[0], cur[1], cur[2])
        print(led[neo_ids[mod_n-1]])
    else:
        ind -= 1
        if ind == 3:
            ind = 4
        elif ind == 4:
            ind = 3
        cur = list(led[neo_ids[mod_n-1]+1])
        cur[ind-3] = v
        led[neo_ids[mod_n-1]+1] = (cur[0], cur[1], cur[2])
    led.show()


def set_hdw(cmd, dur):
    global sp, br

    if cmd == "":
        return "NOCMDS"

    # Split the input string into segments
    segs = cmd.split(",")

    # Process each segment
    try:
        for seg in segs:
            f_nm = ""
            if seg[0] == 'E':  # end an
                return "STOP"
            # play file MALXXX = Play file, A (P play music, W play music wait, A play animation), L = file location (S sound tracks, M my sound tracks, P playlist) XXX (file name)
            elif seg[0] == 'M':
                if seg[1] == "S":
                    stop_media()
                elif seg[1] == "W" or seg[1] == "A" or seg[1] == "P":
                    stop_media()
                    if seg[2] == "S":
                        w0 = media_folder + "sndtrk/" + seg[3:]
                        f_nm = seg[3:]
                    elif seg[2] == "M":
                        w0 = media_folder + "customers_owned_music/" + \
                            seg[3:]
                        f_nm = "customers_owned_music_" + seg[3:]
                    elif seg[2] == "P":
                        f_nm = "plylst_" + seg[3:]
                    if seg[1] == "W" or seg[1] == "P":
                        play_a_0(w0, False)
                    if seg[1] == "A":
                        res = an(f_nm)
                        if res == "STOP":
                            return "STOP"
                    if seg[1] == "W":
                        wait_snd()
            # lights LNNN_R_G_B = All lights NNN (0 All, 1 to 999) RGB 0 to 255
            elif seg[0] == 'L':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][1:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_all_to(light_n, r, g, b)
            # modules MNNN_I_XXX = Neo modules MMM (0 All, 1 to 999) I index (0 All, 1 to 6) XXX 0 to 255
            elif seg[0] == 'N':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0][1:])
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_module(mod_n, index, v)
            # brightness BXXX = Brightness XXX 000 to 100
            elif seg[0] == 'B':
                br = int(seg[1:])
                led.brightness = float(br/100)
                led.show()
            # fade in or out FXXX_TTT = Fade brightness in or out XXX 0 to 100, TTT time between transitions in decimal seconds
            elif seg[0] == 'F':
                segs_split = seg.split("_")
                v = int(segs_split[0][1:])
                s = float(segs_split[1])
                while not br == v:
                    if br < v:
                        br += 1
                        led.brightness = float(br/100)
                    else:
                        br -= 1
                        led.brightness = float(br/100)
                    led.show()
                    time.sleep(s)
            # ZRAND = Random rainbow, fire, or color change
            elif seg[0:] == 'ZRAND':
                random_effect(1, 3, dur)
            # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                rbow(v, dur)
            # ZFIRE = Fire
            elif seg[0:] == 'ZFIRE':
                random_effect(3, 3, dur)
            # ZCOLCH = Color change
            elif seg[0:] == 'ZCOLCH':
                random_effect(2, 2, dur)
            # C_NN,..._TTT = Cycle, NN one or many commands separated by slashes, TTT interval in decimal seconds between commands
            elif seg[0] == 'C':
                print("not implemented")
    except Exception as e:
        files.log_item(e)

##############################
# Led color effects


def random_effect(il, ih, d):
    i = random.randint(il, ih)
    if i == 1:
        rbow(.005, d)
    elif i == 2:
        multi_color()
        time.sleep(d)
    elif i == 3:
        fire(d)


def rbow(spd, dur):
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            if not an_running:
                return
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
        for j in reversed(range(0, 255, 1)):
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return


def fire(dur):
    st = time.monotonic()

    firei = []

    firei.extend(ornmnts)
    firei.extend(cane_s)
    firei.extend(cane_e)

    stari = []
    stari.extend(stars)

    for i in stari:
        led[i] = (255, 255, 255)

    brnchsi = []
    brnchsi.extend((brnchs))

    for i in brnchsi:
        led[i] = (50, 50, 50)

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    print(len(firei))

    # Flicker, based on our initial RGB values
    while True:
        for i in firei:
            if not an_running:
                return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led[i] = (r1, g1, b1)
            led.show()
        time.sleep(random.uniform(0.05, 0.1))
        te = time.monotonic()-st
        if te > dur:
            return


def multi_color():
    for i in range(0, n_px):
        if not an_running:
            return
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        c = random.randint(0, 2)
        if c == 0:
            r1 = r
            g1 = 0
            b1 = 0
        elif c == 1:
            r1 = 0
            g1 = g
            b1 = 0
        elif c == 2:
            r1 = 0
            g1 = 0
            b1 = b
        led[i] = (r1, g1, b1)

    stari = []
    stari.extend(stars)

    for i in stari:
        led[i] = (255, 255, 255)

    brnchsi = []
    brnchsi.extend((brnchs))

    for i in brnchsi:
        led[i] = (7, 163, 30)

    canei = []
    canei.extend(cane_e)
    for i in canei:
        led[i] = (255, 255, 255)
    led.show()


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c

################################################################################
# State Machine


class StMch(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add(self, state):
        self.states[state.name] = state

    def go_to(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def upd(self):
        if self.state:
            self.state.upd(self)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, mch):
        pass

    def exit(self, mch):
        pass

    def upd(self, mch):
        pass


class BseSt(Ste):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, mch):
        play_a_0(code_folder + "mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, an_running, stop_play_list
        if not an_running:
            switch_state = utilities.switch_state(
                l_sw, r_sw, time.sleep, 3.0)
            if switch_state == "left_held":
                if cont_run:
                    cont_run = False
                    play_a_0(code_folder + "mvc/continuous_mode_deactivated.wav")
                else:
                    cont_run = True
                    play_a_0(code_folder + "mvc/continuous_mode_activated.wav")
            elif switch_state == "left" or cont_run:
                stop_play_list = False
                an(cfg["option_selected"])
                rst_an()
            elif switch_state == "right":
                mch.go_to('main_menu')


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        play_a_0(code_folder + "mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0(code_folder + "mvc/" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "volume_settings":
                mch.go_to('volume_settings')
            else:
                play_a_0(code_folder + "mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Snds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, mch):
        files.log_item('Choose sounds menu')
        play_a_0(code_folder + "mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            try:
                play_a_0(media_folder + "o_snds/" + menu_snd_opt[self.i])
            except Exception as e:
                files.log_item(e)
                spk_sng_num(str(self.i+1))
            self.sel_i = self.i
            self.i += 1
            if self.i > len(menu_snd_opt)-1:
                self.i = 0
        if r_sw.fell:
            cfg["option_selected"] = menu_snd_opt[self.sel_i]
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_a_0(code_folder + "mvc/option_selected.wav", "rb")
            mch.go_to('base_state')


class AddSnds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'add_sounds_animate'

    def enter(self, mch):
        files.log_item('Add sounds animate')
        play_a_0(code_folder + "mvc/add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0(
                code_folder + "mvc/" + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                play_a_0(code_folder + "mvc/create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                play_a_0(code_folder + "mvc/timestamp_mode_on.wav")
                play_a_0(code_folder + "mvc/timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                play_a_0(code_folder + "mvc/timestamp_mode_off.wav")
            else:
                play_a_0(code_folder + "mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class VolSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, mch):
        files.log_item('Set Web Options')
        play_a_0(code_folder + "mvc/volume_settings_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0(code_folder + "mvc/" + vol_set[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(vol_set)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = vol_set[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                play_a_0(code_folder + "mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, time.sleep, 3.0)
                    if switch_state == "left":
                        ch_vol("lower")
                    elif switch_state == "right":
                        ch_vol("raise")
                    elif switch_state == "right_held":
                        files.write_json_file(
                            code_folder + "cfg.json", cfg)
                        play_a_0(code_folder + "mvc/all_changes_complete.wav")
                        done = True
                        mch.go_to('base_state')
                    time.sleep(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file(code_folder + "cfg.json", cfg)
                play_a_0(code_folder + "mvc/all_changes_complete.wav")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file(code_folder + "cfg.json", cfg)
                play_a_0(code_folder + "mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class WebOpt(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'web_options'

    def enter(self, mch):
        files.log_item('Set Web Options')
        sel_web()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0(code_folder + "mvc/" + web_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if r_sw.fell:
            selected_menu_item = web_m[self.sel_i]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                opt_sel()
                sel_web()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                opt_sel()
                sel_web()
            elif selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            elif selected_menu_item == "hear_instr_web":
                play_a_0(code_folder + "mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file(code_folder + "cfg.json", cfg)
                play_a_0(code_folder + "mvc/all_changes_complete.wav")
                mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())
st_mch.add(AddSnds())
st_mch.add(VolSet())
st_mch.add(WebOpt())


time.sleep(0)
aud_en.value = True
upd_vol(1)

if (web):
    files.log_item("starting server...")
    try:
        # Wait for the network to be ready before continuing
        wait_for_network()

        # Register mDNS service
        zeroconf = Zeroconf()
        print("Registering mDNS service...")
        zeroconf.register_service(info)

        # Run the server in a separate thread to allow mDNS to work simultaneously
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        spk_web()
    except OSError:
        time.sleep(5)
        files.log_item("server did not start...")

# discover_lights()

is_gtts_reachable = check_gtts_status()

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")


def run_state_machine():
    while True:
        st_mch.upd()
        time.sleep(.1)


# Start the state machine in a separate thread
state_machine_thread = threading.Thread(target=run_state_machine)

# Daemonize the thread to end with the main program
state_machine_thread.daemon = True
state_machine_thread.start()


def run_stop_button_check():
    global an_running, stop_play_list
    while True:
        if an_running:
            l_sw.update()
            r_sw.update()
            if l_sw.fell and cfg["can_cancel"]:
                an_running = False
                stop_play_list = True
                mix.stop()
                media_player.stop()
                rst_an()
        time.sleep(.1)


# Start the state machine in a separate thread
check_stop_button_thread = threading.Thread(target=run_stop_button_check)

# Daemonize the thread to end with the main program
check_stop_button_thread.daemon = True
check_stop_button_thread.start()


while True:
    try:
        input("Press enter to exit...\n\n")
    finally:
        print("Unregistering mDNS service...")
        zeroconf.unregister_service(info)
        zeroconf.close()
        httpd.shutdown()
        rst_an()
        quit()


# type: ignore
