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

l_sw = Debouncer(switch_io_1)
r_sw = Debouncer(switch_io_2)
w_sw = Debouncer(switch_io_3)
b_sw = Debouncer(switch_io_4)

################################################################################
# Setup sound
#i2s audio is setup on pi with an overlay

# Setup the mixer to play wav files
pygame.mixer.init()
mix = pygame.mixer.music

################################################################################
# Setup video hardware

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

cfg["volume"]="5"
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
    mix.set_volume(volume)
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
    if mix.get_busy():
        mix.stop()
        while mix.get_busy():
            upd_vol(0.1)
    mix.load(file_name)
    mix.play(loops=0)
    while mix.get_busy():
        exit_early()


def stop_a_0():
    mix.stop()
    while mix.get_busy():
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
    if cfg["HOST_NAME"] == "animator-drive-in":
        play_a_0("/home/pi/mvc/animator_dash_bandstand.wav")
        play_a_0("/home/pi/mvc/dot.wav")
        play_a_0("/home/pi/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_a_0("/home/pi/mvc/in_your_browser.wav")   

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
        play_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
                play_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                play_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
            an(cfg["option_selected"])
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
        play_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0("/sd/mvc/" + main_m[self.i] + ".wav")
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
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
        play_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    wave0 = audiocore.WaveFile(open(
                        "/sd/o_snds/" + menu_snd_opt[self.i] + ".wav", "rb"))
                    mix.voice[0].play(wave0, loop=False)
                except Exception as e:
                    files.log_item(e)
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                wave0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play(wave0, loop=False)
                while mix.voice[0].playing:
                    pass
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
        play_a_0("/sd/mvc/add_sounds_animate.wav")
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
                "/sd/mvc/" + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                play_a_0("/sd/mvc/create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                play_a_0("/sd/mvc/timestamp_mode_on.wav")
                play_a_0("/sd/mvc/timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                play_a_0("/sd/mvc/timestamp_mode_off.wav")
            else:
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
        play_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0("/sd/mvc/" + vol_set[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(vol_set)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = vol_set[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                play_a_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        ch_vol("lower")
                    elif switch_state == "right":
                        ch_vol("raise")
                    elif switch_state == "right_held":
                        files.write_json_file(
                            "/sd/cfg.json", cfg)
                        play_a_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
            play_a_0("/sd/mvc/" + web_m[self.i] + ".wav")
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
                play_a_0("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
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

aud_en.value = True

upd_vol(.1)

if (web):
    files.log_item("starting server...")
    try:
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

upd_vol(.5)

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.upd()
    upd_vol(.1)
    if not media_player.is_playing() and run_movie_cont:
        print("play movies: " + str(run_movie_cont))
        play_movies()
        while not media_player.is_playing():
            time.sleep(.5)
        l_sw.update()
        r_sw.update()
        w_sw.update()
        b_sw.update()
        if l_sw.fell:
            if media_player.is_playing(): pause_movie()
            run_movie_cont = True
            print ("left fell")
        if r_sw.fell:
            print ("right fell")
            if media_player.is_playing():
                run_movie_cont = False
                pause_movie()
            else:
                play_movie()
                rainbow(.005,5)
        if w_sw.fell:
            print ("white fell")
            volume = volume - 10
            if volume < 0: volume = 0
            media_player.audio_set_volume(volume)
        if b_sw.fell:
            print ("blue fell")
            volume = volume + 10
            if volume > 100: volume = 100
            media_player.audio_set_volume(volume)
        time.sleep(.1)
        pass
        try:
            input("Press enter to exit...\n\n")
        finally:
            print("Unregistering mDNS service...")
            zeroconf.unregister_service(info)
            zeroconf.close()
            httpd.shutdown()
            quit()