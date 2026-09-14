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

import utilities
from adafruit_debouncer import Debouncer
import neopixel
from rainbowio import colorwheel
from analogio import AnalogIn
import asyncio
import pwmio
import microcontroller
import rtc
import random
import board
import digitalio
import busio
import audiomp3
import audiomixer
import audiobusio
import time
import gc
import files
import os
import audiocore
import sdcardio
import storage
from adafruit_motor import servo


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free() 
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def f_exists(filename):
    try:
        status = os.stat(filename)
        f_exists = True
    except OSError:
        f_exists = False
    return f_exists


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")

################################################################################
# Globals

debug_voltage_multiplier = 1

animations_folder = "snds/"
mvc_folder = "mvc/"
mvc_folder_local = "mvc/"

elves_folder = "elves/"
bells_folder = "bells/"
horns_folder = "horns/"
stops_folder = "stops/"
santa_folder = "santa/"
story_folder = "story/"

FOLDER_MAP = {
    'A': animations_folder,
    'E': elves_folder,
    'B': bells_folder,
    'H': horns_folder,
    'T': stops_folder,
    'S': santa_folder,
    'C': story_folder
}

media_index = {'A': 0, 'E': 0, 'B': 0, 'H': 0, 'T': 0, 'S': 0, 'C': 0}

################################################################################
# Flash data

cfg = files.read_json_file("/cfg.json")

snd_opt = []
menu_snd_opt = []

def upd_media():
    global snd_opt, menu_snd_opt
    snd_opt = files.return_directory("", animations_folder, ".json")
    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all']
    menu_snd_opt.extend(rnd_opt)

upd_media()

web = cfg["serve_webpage"]

cfg_main = files.read_json_file(mvc_folder + "main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(mvc_folder + "web_menu.json")
web_m = cfg_web["web_menu"]

cfg_add_song = files.read_json_file(mvc_folder +
                                    "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cfg_muse_set = files.read_json_file(mvc_folder +
                                    "museum_settings.json")
muse_set = cfg_muse_set["museum_settings"]


local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

gc_col("config setup")

ts_mode = False

flsh_i = 0
flsh_t = []

t_s = []
t_elsp = 0.0
srt_t = 0.0

an_running = False
an_just_added = False

################################################################################
# Setup the servos
s_1_pin = board.GP22
s_2_pin = board.GP17
s_3_pin = board.GP16

s_1 = pwmio.PWMOut(s_1_pin, duty_cycle=2 ** 15, frequency=50)
s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)

s_2 = pwmio.PWMOut(s_2_pin, duty_cycle=2 ** 15, frequency=50)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)

s_3 = pwmio.PWMOut(s_3_pin, duty_cycle=2 ** 15, frequency=50)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

p_arr = [90, 90, 90]
s_arr = [s_1, s_2, s_3]

# Allowed dance target ranges for each snowman
dance_min = [55, 65, 45]
dance_max = [125, 135, 115]

# Starting targets
dance_target = [110, 75, 105]

# Time between one-degree servo movements
dance_interval = .02


def m_servo(n, p):
    global p_arr

    if p < 0:
        p = 0

    if p > 180:
        p = 180

    s_arr[n].angle = p
    p_arr[n] = p


async def move_servo(n, target, spd):
    start_pos = p_arr[n]
    st = time.monotonic()

    if target > start_pos:
        direction = 1
    elif target < start_pos:
        direction = -1
    else:
        return

    while True:
        if exit_set_hdw_async:
            return

        elapsed = time.monotonic() - st
        steps = int(elapsed / spd)

        new_pos = start_pos + steps * direction

        if direction > 0:
            if new_pos >= target:
                m_servo(n, target)
                return
        else:
            if new_pos <= target:
                m_servo(n, target)
                return

        if new_pos != p_arr[n]:
            m_servo(n, new_pos)

        await asyncio.sleep(0)


async def dance(st, dur):
    next_move = st

    while True:
        if exit_set_hdw_async:
            return

        now = time.monotonic()

        if now - st >= dur:
            return

        if now >= next_move:
            next_move += dance_interval

            for n in range(3):
                if p_arr[n] == dance_target[n]:
                    dance_target[n] = random.randint(dance_min[n], dance_max[n])

                if p_arr[n] < dance_target[n]:
                    m_servo(n, p_arr[n] + 1)

                elif p_arr[n] > dance_target[n]:
                    m_servo(n, p_arr[n] - 1)

        await asyncio.sleep(0)



################################################################################
# Setup hardware

# Setup pin for v
a_in = AnalogIn(board.A2)

track_a_in = AnalogIn(board.A0)

aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

# Setup the switches
l_sw_io = digitalio.DigitalInOut(board.GP11)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)

r_sw_io = digitalio.DigitalInOut(board.GP15)
r_sw_io.direction = digitalio.Direction.INPUT
r_sw_io.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw_io)

# setup i2s audio
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer to play mp3 files
mix = audiomixer.Mixer(
    voice_count=2,
    sample_rate=22050,
    channel_count=2,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=16384,
)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

aud_en.value = True

if cfg["use_sd_card"]:
    spi = busio.SPI(sck, si, so)
    try:
        sd = sdcardio.SDCard(spi, cs)
        vfs = storage.VfsFat(sd)
        storage.mount(vfs, "/sd")
    except Exception as e:
        files.log_item(e)
        cfg["use_sd_card"] = False
        w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
        mix.voice[0].play(w0, loop=False)
        while mix.voice[0].playing:
            pass

aud_en.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Setup neo pixels

n_px = 3

led1 = neopixel.NeoPixel(board.GP0, 1, auto_write=False)
led2 = neopixel.NeoPixel(board.GP1, 1, auto_write=False)
led3 = neopixel.NeoPixel(board.GP6, 1, auto_write=False)

led_channels = [led1, led2, led3]


class SeparateNeoPixels:
    def __init__(self, channels):
        self.channels = channels
        self._brightness = 1.0

    def __len__(self):
        return len(self.channels)

    def __setitem__(self, index, color):
        self.channels[index][0] = color

    def __getitem__(self, index):
        return self.channels[index][0]

    def fill(self, color):
        for channel in self.channels:
            channel[0] = color

    def show(self):
        for channel in self.channels:
            channel.show()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        for channel in self.channels:
            channel.brightness = value


led = SeparateNeoPixels(led_channels)

led.fill((255, 255, 255))
led.show()

gc_col("Neopixels setup")


################################################################################
# Dialog and sound play methods


def upd_vol(s, bckgrnd_ratio=None):
    global bckgrnd_vol
    if bckgrnd_ratio is not None:
        bckgrnd_vol = bckgrnd_ratio
    if bckgrnd_vol > 100:
        bckgrnd_vol = 100
    if bckgrnd_vol < 0:
        bckgrnd_vol = 0
    try:
        volume = int(cfg["volume"]) / 100
        bckgrnd_volume = volume * (bckgrnd_vol / 100)
    except Exception as e:
        files.log_item(e)
        volume = .5
        bckgrnd_volume = .5
    if volume < 0 or volume > 1:
        volume = .5
    if bckgrnd_volume < 0 or bckgrnd_volume > 1:
        bckgrnd_volume = .5
    mix.voice[0].level = bckgrnd_volume
    mix.voice[1].level = volume
    time.sleep(s)


async def upd_vol_async(s, bckgrnd_ratio=None):
    global bckgrnd_vol
    if bckgrnd_ratio is not None:
        bckgrnd_vol = bckgrnd_ratio
    if bckgrnd_vol > 100:
        bckgrnd_vol = 100
    if bckgrnd_vol < 0:
        bckgrnd_vol = 0
    try:
        volume = int(cfg["volume"]) / 100
        bckgrnd_volume = volume * (bckgrnd_vol / 100)
    except Exception as e:
        files.log_item(e)
        volume = .5
        bckgrnd_volume = .5
    if volume < 0 or volume > 1:
        volume = .5
    if bckgrnd_volume < 0 or bckgrnd_volume > 1:
        bckgrnd_volume = .5
    mix.voice[0].level = bckgrnd_volume
    mix.voice[1].level = volume
    await asyncio.sleep(s)


def ch_vol(action):
    v = int(cfg["volume"])
    if "volume" in action:
        v = action.split("volume")
        v = int(v[1])
    if action == "lower1":
        v -= 1
    elif action == "raise1":
        v += 1
    if action == "lower5":
        v -= 5
    elif action == "raise5":
        v += 5
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
    if not mix.voice[0].playing:
        save_cfg_safely()
        ply_a_0(mvc_folder + "volume.mp3")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name, wait=True, repeat=False):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1)
    if file_name.lower().endswith(".mp3"):
        w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w0 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)
    mix.voice[0].play(w0, loop=repeat)
    if wait:
        while mix.voice[0].playing:
            upd_vol(0.1)
            pass


def ply_a_1(file_name, wait=True, repeat=False):
    if mix.voice[1].playing:
        mix.voice[1].stop()
        while mix.voice[1].playing:
            upd_vol(0.1)
    if file_name.lower().endswith(".mp3"):
        w1 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w1 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)
    mix.voice[1].play(w1, loop=repeat)
    if wait:
        while mix.voice[1].playing:
            upd_vol(0.1)
            pass


async def ply_a_1_async(file_name, repeat=False):
    if mix.voice[1].playing:
        mix.voice[1].stop()
        while mix.voice[1].playing:
            await asyncio.sleep(0)
    if file_name.lower().endswith(".mp3"):
        w1 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w1 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)
    mix.voice[1].play(w1, loop=repeat)
    while mix.voice[1].playing:
        await asyncio.sleep(0)


def wait_snd():
    while mix.voice[0].playing:
        pass


async def wait_snd_1():
    while mix.voice[1].playing:
        if an_running:
            if await animation_wait(.01):
                return True
        else:
            await asyncio.sleep(0)
    return False


def stp_a_0():
    mix.voice[0].stop()
    wait_snd()


async def stp_a_1():
    mix.voice[1].stop()
    await wait_snd_1()


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            ply_a_0(mvc_folder + character + ".mp3")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0(mvc_folder + "dot.mp3")
        ply_a_0(mvc_folder + "local.mp3")


def l_r_but():
    ply_a_0(mvc_folder + "press_left_button_right_button.mp3")


def sel_web():
    ply_a_0(mvc_folder + "web_menu.mp3")
    l_r_but()


def sel_museum():
    ply_a_0(mvc_folder + "museum_settings_menu.mp3")
    l_r_but()


def opt_sel():
    ply_a_0(mvc_folder + "option_selected.mp3")


def spk_sng_num(song_number):
    ply_a_0(mvc_folder + "song.mp3")
    spk_str(song_number, False)


async def no_trk():
    ply_a_0(mvc_folder + "no_user_soundtrack_found.mp3")
    while True:
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        l_sw.update()
        r_sw.update()
        if sw == "left":
            break
        if sw == "right":
            ply_a_0(mvc_folder + "create_sound_track_files.mp3")
            break
        await asyncio.sleep(.1)


def spk_web():
    ply_a_0(mvc_folder + "animator_available_on_network.mp3")
    ply_a_0(mvc_folder + "to_access_type.mp3")
    if cfg["HOST_NAME"] == "animator-trolley":
        ply_a_0(mvc_folder + "animator_trolley.mp3")
        ply_a_0(mvc_folder + "dot.mp3")
        ply_a_0(mvc_folder + "local.mp3")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0(mvc_folder + "in_your_browser.mp3")


def get_snds(dir, typ):
    sds = []
    s = files.return_directory("", dir, ".mp3")
    for el in s:
        p = el.split('_')
        if p[0] == typ:
            sds.append(el)
    mx = len(sds) - 1
    i = random.randint(0, mx)
    fn = dir + "/" + sds[i] + ".mp3"
    return fn

MIN_TRACK_VOLTAGE = 9.0


################################################################################
# WiFi setup access point methods
#
# These are deliberately top-level so they can be called later from the
# physical buttons or from one of the menu states.

def url_decode(value):
    result = ""
    i = 0
    while i < len(value):
        if value[i] == "%" and i + 2 < len(value):
            try:
                result += chr(int(value[i + 1:i + 3], 16))
                i += 3
                continue
            except:
                pass
        if value[i] == "+":
            result += " "
        else:
            result += value[i]
        i += 1
    return result

def scan_wifi_networks():
    import wifi
    networks = []
    try:
        print("Scanning for WiFi networks...")
        for network in wifi.radio.start_scanning_networks():
            ssid = network.ssid
            if not ssid:
                continue
            found = False
            for item in networks:
                if item["ssid"] == ssid:
                    found = True
                    if network.rssi > item["rssi"]:
                        item["rssi"] = network.rssi
                    break
            if not found:
                networks.append({
                    "ssid": ssid,
                    "rssi": network.rssi
                })
        wifi.radio.stop_scanning_networks()
    except Exception as e:
        print("WiFi scan error:", e)
        try:
            wifi.radio.stop_scanning_networks()
        except:
            pass
    networks.sort(key=lambda item: item["rssi"], reverse=True)
    return networks


def start_wifi_setup():
    global wifi_setup_restart, web
    import socketpool
    import wifi
    import ipaddress
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    wifi_setup_restart = False
    web = False
    networks = scan_wifi_networks()
    try:
        wifi.radio.stop_station()
    except Exception as e:
        print("Stop station:", e)
    print("Starting setup access point...")
    wifi.radio.start_ap("JimmyTrainsAnimator", "")
    wifi.radio.set_ipv4_address_ap(
        ipv4=ipaddress.IPv4Address("10.10.10.10"),
        netmask=ipaddress.IPv4Address("255.255.255.0"),
        gateway=ipaddress.IPv4Address("10.10.10.10")
    )
    wifi.radio.start_dhcp_ap()
    setup_ip = "10.10.10.10"
    print("")
    print("======================================")
    print("WiFi setup access point is running")
    print("SSID: JimmyTrainsAnimator")
    print("Password:")
    print("Connect your computer or phone to that WiFi network")
    print("Use: http://10.10.10.10")
    print("======================================")
    print("")
    setup_pool = socketpool.SocketPool(wifi.radio)
    setup_server = Server(setup_pool, "/", debug=False)

    ply_a_0(mvc_folder + "enter_ssid_password.mp3")


    @setup_server.route("/")
    def setup_home(request: Request):
        return FileResponse(request, "wifi_setup.html", "/")

    @setup_server.route("/scan-wifi")
    def setup_scan_wifi(request: Request):
        return JSONResponse(request, networks)

    @setup_server.route("/save-wifi", [POST])
    def setup_save_wifi(request: Request):
        global wifi_setup_restart
        try:
            rq_d = request.json()
            ssid = rq_d["ssid"].strip()
            password = rq_d["password"]
            if ssid == "":
                return Response(request, "Please select a WiFi network.")
            env = {
                "WIFI_SSID": ssid,
                "WIFI_PASSWORD": password
            }
            files.write_json_file("env.json", env)
            print("WiFi settings saved for:", ssid)
            wifi_setup_restart = True
            return Response(request, "WiFi saved. Animator restarting...")
        
        except Exception as e:
            print("WiFi setup save error:", e)
            return Response(request, "Unable to save WiFi settings.")
    setup_server.start(setup_ip, port=80)
    while True:
        try:
            setup_server.poll()
        except OSError as e:
            print("Setup HTTP error:", e)
        except Exception as e:
            print("Setup server error:", e)
        if wifi_setup_restart:
            time.sleep(2)
            microcontroller.reset()
        time.sleep(.01)


################################################################################
# Normal WiFi connection and web server

if web:
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    gc_col("config wifi imports")
    files.log_item("Connecting to WiFi")
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""
    try:
        env = files.read_json_file("env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except Exception:
        print("Using default ssid and password")
    wifi_connected = False
    for i in range(3):
        led[0] = (0, 0, 255)
        led.show()
        try:
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            wifi_connected = True
            break
        except Exception as e:
            files.log_item(e)
            time.sleep(1)
    if not wifi_connected:
        print("Unable to connect to configured WiFi")
        print("WiFi setup access point is available from the physical/menu command")
        web = False
    else:
        gc_col("wifi connect")
        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(service_type="_http", protocol="_tcp", port=80)
        local_ip = str(wifi.radio.ipv4_address)
        files.log_item("IP is " + local_ip)
        files.log_item("Connected")
        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=False)
        server.port = 80
        gc_col("wifi server")

        def create_directory_if_needed(path):
            if path == "" or path == "/":
                return

            path = path.replace("\\", "/")

            if not path.startswith("/"):
                path = "/" + path

            parts = path.strip("/").split("/")
            current_path = ""

            for part in parts:
                if part == "":
                    continue

                current_path += "/" + part

                try:
                    os.stat(current_path)
                except OSError:
                    print("Creating directory:", current_path)
                    os.mkdir(current_path)

        ################################################################################
        # Setup routes

        @server.route("/")
        def base(req: Request):
            return FileResponse(req, "index.html", "/")

        @server.route("/mui.min.css")
        def base(req: Request):
            return FileResponse(req, "mui.min.css", "/")

        @server.route("/mui.min.js")
        def base(req: Request):
            return FileResponse(req, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def btn(request: Request):
            rq_d = request.json()
            cfg["option_selected"] = rq_d["an"]
            add_cmd("AN_" + cfg["option_selected"])
            if not mix.voice[0].playing:
                save_cfg_safely()
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def btn(request: Request):
            stop_all_cmds()
            rq_d = request.json()
            if rq_d["an"] == "reset_to_defaults":
                rst_def()
                save_cfg_safely()
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                st_mch.go_to('base_state')
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/mode", [POST])
        def btn(request: Request):
            global ts_mode
            rq_d = request.json()
            if rq_d["an"] == "left":
                ovrde_sw_st["switch_value"] = "left"
            elif rq_d["an"] == "left_held":
                ovrde_sw_st["switch_value"] = "left_held"
            elif rq_d["an"] == "right":
                ovrde_sw_st["switch_value"] = "right"
            elif rq_d["an"] == "right_held":
                ovrde_sw_st["switch_value"] = "right_held"
            elif rq_d["an"] == "three":
                ovrde_sw_st["switch_value"] = "three"
            elif rq_d["an"] == "four":
                ovrde_sw_st["switch_value"] = "four"
            elif rq_d["an"] == "cont_mode_on":
                stop_all_cmds()
                ply_a_0(mvc_folder + "continuous_mode_activated.mp3")
                cfg["cont_mode"] = True
                save_cfg_safely()
            elif rq_d["an"] == "cont_mode_off":
                stop_all_cmds()
                ply_a_0(mvc_folder + "continuous_mode_deactivated.mp3")
                cfg["cont_mode"] = False
                save_cfg_safely()
            elif rq_d["an"] == "timestamp_mode_on":
                stop_all_cmds()
                ts_mode = True
                ply_a_0(mvc_folder + "timestamp_mode_on.mp3")
                ply_a_0(mvc_folder + "timestamp_instructions.mp3")
            elif rq_d["an"] == "timestamp_mode_off":
                stop_all_cmds()
                ts_mode = False
                ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
            elif rq_d["an"] == "museum_mode_on":
                stop_all_cmds()
                cfg["museum_mode"] = True
                save_cfg_safely()
                ply_a_0(mvc_folder + "museum_mode_on.mp3")
            elif rq_d["an"] == "museum_mode_off":
                stop_all_cmds()
                cfg["museum_mode"] = False
                ply_a_0(mvc_folder + "museum_mode_off.mp3")
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/speaker", [POST])
        def btn(request: Request):
            stop_all_cmds()
            rq_d = request.json()
            if rq_d["an"] == "speaker_test":
                ply_a_0(mvc_folder + "left_speaker_right_speaker.mp3")
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/lights", [POST])
        def btn(request: Request):
            rq_d = request.json()
            command = rq_d["an"]
            add_command_to_ts(command)
            set_hdw_not_async(command)
            return Response(request, "Utility: " + "Utility: set lights")

        @server.route("/set-item-lights", [POST])
        def btn(request: Request):
            rq_d = request.json()
            command = "LN0_" + str(rq_d["r"]) + "_" + \
                str(rq_d["g"]) + "_" + str(rq_d["b"])
            add_command_to_ts(command)
            set_hdw_not_async(command)
            return Response(request, "Utility: " + "Utility: set lights")

        @server.route("/get-wifi-signal", [POST])
        def get_local_ip(request: Request):
            avg_rssi = measure_signal_strength(WIFI_SSID, 10)
            return Response(request, str(avg_rssi))

        @server.route("/get-track-voltage", [POST])
        def btn(request: Request):
            track_voltage = get_track_voltage()
            return Response(request, str(track_voltage))

        @server.route("/update-host-name", [POST])
        def btn(request: Request):
            stop_all_cmds()
            rq_d = request.json()
            cfg["HOST_NAME"] = rq_d["an"]
            save_cfg_safely()
            mdns.hostname = cfg["HOST_NAME"]
            spk_web()
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def btn(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-local-ip", [POST])
        def buttonpress(req: Request):
            return Response(req, local_ip)

        @server.route("/update-volume", [POST])
        def btn(request: Request):
            stop_all_cmds()
            rq_d = request.json()
            ch_vol(rq_d["action"])
            save_cfg_safely()
            return Response(request, cfg["volume"])

        @server.route("/get-options", [POST])
        def btn(request: Request):
            rq_d = {
                "queuing": cfg["queuing"]
            }
            my_string = files.json_stringify(rq_d)
            return Response(request, my_string)

        @server.route("/update-options", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["queuing"] = rq_d["queuing"]
            save_cfg_safely()
            my_string = files.json_stringify(cfg)
            return Response(request, my_string)

        @server.route("/get-volume", [POST])
        def btn(request: Request):
            return Response(request, cfg["volume"])

        @server.route("/get-animations", [POST])
        def btn(request: Request):
            stop_all_cmds()
            sounds = []
            sounds.extend(snd_opt)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/create-animation", [POST])
        def btn(request: Request):
            stop_all_cmds()
            try:
                global data, animations_folder
                rq_d = request.json()  # Parse the incoming JSON
                print(rq_d)
                f_n = animations_folder + rq_d["fn"] + ".json"
                print(f_n)
                an_data = ["0.0|MB0name of your track.wav", "1.0|"]
                files.write_json_file(f_n, an_data)
                upd_media()
                return Response(request, "Created animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error creating animation.")

        @server.route("/rename-animation", [POST])
        def btn(request: Request):
            stop_all_cmds()
            try:
                global data, animations_folder
                rq_d = request.json()  # Parse the incoming JSON
                fo = animations_folder + rq_d["fo"] + ".json"
                fn = animations_folder + rq_d["fn"] + ".json"
                os.rename(fo, fn)
                upd_media()
                return Response(request, "Renamed animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error setting lights.")

        @server.route("/delete-animation", [POST])
        def btn(request: Request):
            stop_all_cmds()
            try:
                global data, animations_folder
                rq_d = request.json()  # Parse the incoming JSON
                print(rq_d)
                f_n = animations_folder + rq_d["fn"] + ".json"
                print(f_n)
                os.remove(f_n)
                upd_media()
                return Response(request, "Delete animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error setting lights.")

        @server.route("/test-animation", [POST])
        def btn(request: Request):
            try:
                rq_d = request.json()
                add_cmd(rq_d["an"])
                return Response(request, "success")
            except Exception as e:
                print(e)
                return Response(request, "error")

        @server.route("/get-animation", [POST])
        def btn(request: Request):
            stop_all_cmds()
            rq_d = request.json()
            snd_f = rq_d["an"]
            if (f_exists(animations_folder + snd_f + ".json") == True):
                f_n = animations_folder + snd_f + ".json"
                return FileResponse(request, f_n, "/")
            else:
                f_n = "/t_s_def/timestamp mode.json"
                return FileResponse(request, f_n, "/")

        data = []

        @server.route("/save-data", [POST])
        def btn(request: Request):
            global data
            stop_all_cmds()
            rq_d = request.json()
            try:
                if rq_d[0] == 0:
                    data = []
                data.extend(rq_d[2])
                if rq_d[0] == rq_d[1]:
                    f_n = animations_folder + \
                        rq_d[3] + ".json"
                    files.write_json_file(f_n, data)
                    data = []
                upd_media()
            except Exception as e:
                files.log_item(e)
                data = []
                return Response(request, "out of memory")
            return Response(request, "success")

        @server.route("/get-sound-files", [POST])
        def get_sound_files(request: Request):
            try:
                sound_files = []
                for filename in os.listdir(animations_folder):
                    lower_name = filename.lower()
                    if lower_name.endswith(".mp3") or lower_name.endswith(".wav"):
                        sound_files.append(filename)
                sound_files.sort()
                return Response(request, files.json_stringify(sound_files))

            except Exception as e:
                print("Get sound files error:", e)
                return Response(request, "[]")


        @server.route("/delete-sound-file", [POST])
        def delete_sound_file(request: Request):
            try:
                rq_d = request.json()
                filename = rq_d["filename"]
                filename = filename.replace("\\", "/")
                filename = filename.split("/")[-1]
                if not filename:
                    return Response(request, "invalid filename")
                lower_name = filename.lower()
                if not lower_name.endswith(".mp3") and not lower_name.endswith(".wav"):
                    return Response(request, "invalid file type")
                file_path = animations_folder + filename
                if not f_exists(file_path):
                    return Response(request, "file not found")
                os.remove(file_path)
                print("Deleted sound file:", filename)
                return Response(request, "success")
            except Exception as e:
                print("Delete sound file error:", e)
                return Response(request, "error")


        @server.route("/upload-sound", [POST])
        def upload_sound(request: Request):
            try:
                filename = request.query_params.get("filename")
                location = request.query_params.get("location", "")
                offset = int(request.query_params.get("offset", "0"))

                if not filename:
                    return Response(request, "missing filename")

                filename = url_decode(filename)
                location = url_decode(location)

                filename = filename.replace("\\", "/")
                filename = filename.split("/")[-1]

                location = location.replace("\\", "/")

                if not filename:
                    return Response(request, "invalid filename")

                if location == "":
                    location = "/"

                if not location.startswith("/"):
                    location = "/" + location

                if location != "/" and not location.endswith("/"):
                    location += "/"

                file_path = location + filename
                chunk_size = len(request.body)

                if offset == 0:
                    create_directory_if_needed(location)

                    with open(file_path, "wb") as f:
                        f.write(request.body)

                else:
                    if not f_exists(file_path):
                        return Response(request, "file not found")

                    with open(file_path, "r+b") as f:
                        f.seek(offset)
                        f.write(request.body)

                print("Uploaded:", file_path, "offset:", offset, "bytes:", chunk_size)

                return Response(request, "success")

            except Exception as e:
                print("Upload error:", e)
                return Response(request, "error")

 
        @server.route("/upload-sound-complete", [POST])
        def upload_sound_complete(request: Request):
            try:
                rq_d = request.json()

                filename = rq_d["filename"]
                location = rq_d.get("location", "")
                expected_size = int(rq_d["size"])

                filename = filename.replace("\\", "/")
                filename = filename.split("/")[-1]

                location = location.replace("\\", "/")

                if not filename:
                    return Response(request, "invalid filename")

                if location == "":
                    location = "/"

                if location != "/" and not location.endswith("/"):
                    location += "/"

                file_path = location + filename

                if not f_exists(file_path):
                    return Response(request, "file not found")

                actual_size = os.stat(file_path)[6]

                print("Upload complete:", file_path)
                print("Expected size:", expected_size)
                print("Actual size:", actual_size)

                if actual_size != expected_size:
                    return Response(request, "size mismatch")

                return Response(request, "success")

            except Exception as e:
                print("Upload complete error:", e)
                return Response(request, "error")


         
gc_col("web server")

def measure_signal_strength(MY_SSID, cycles):
    if not web:
        return 0
    print("Monitoring signal for:", MY_SSID)
    print("Showing current RSSI + running average (simple sum + count)\n")
    total_sum = 0.0
    count = 0
    while True:
        current_rssi = None
        found = False
        try:
            for network in wifi.radio.start_scanning_networks():
                if network.ssid == MY_SSID:
                    current_rssi = network.rssi
                    print(
                        f"{time.monotonic():.1f}s | {MY_SSID} → RSSI = {current_rssi} dBm", end="")
                    found = True
                    break
            wifi.radio.stop_scanning_networks()
            if found and current_rssi is not None:
                total_sum += current_rssi
                count += 1
                if count > 0:
                    avg_rssi = total_sum / count
                    print(f"   |   Avg ({count} readings): {avg_rssi:.1f} dBm")
                else:
                    print("   |   Avg: waiting...")
            else:
                print(
                    "   |   Could not see your SSID (hidden, out of range, or scan miss)")
        except Exception as e:
            print(f"Scan error: {e}")
            wifi.radio.stop_scanning_networks()  # cleanup on error
        time.sleep(0.1)
        if count > cycles:
            return avg_rssi

cycles = 10

if web:
    avg_rssi = measure_signal_strength(WIFI_SSID, cycles)
    print(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")
else:
    avg_rssi = 0

################################################################################
# Command queue
command_queue = []


def add_cmd(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        print("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        print("Command added to the end:", command)


async def process_cmd():
    while command_queue:
        cmd = command_queue.pop(0)
        print("Processing command:", cmd)
        if cmd[:2] == 'AN':
            cmd_split = cmd.split("_")
            clr_cmd_queue()
            if cmd_split[1] == "customers":
                await an_async(cmd_split[1]+"_"+cmd_split[2]+"_"+cmd_split[3]+"_"+cmd_split[4])
            else:
                await an_async(cmd_split[1])
        else:
            await set_hdw_async(cmd)
        await asyncio.sleep(0)


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_cmds(cont_mode_off=True):
    global exit_set_hdw_async
    if cont_mode_off:
        cfg["cont_mode"] = False
    mix.voice[0].stop()
    mix.voice[1].stop()
    led.fill((0, 0, 0))
    led.show()
    clr_cmd_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")

async def animation_wait(wait_time):
    global an_running, flsh_i, srt_t
    start_time = time.monotonic()
    spoken = False
    power_off_time = 0
    sw = ""
    while time.monotonic() - start_time < wait_time:
        if ovrde_sw_st["switch_value"] == "left":
            sw = utilities.switch_state(
                l_sw, r_sw, upd_vol, 1.0, ovrde_sw_st, False)
        else:
            sw = utilities.switch_state(l_sw, r_sw, upd_vol, 1.0, ovrde_sw_st, False)
            if sw == "none" and time.monotonic() - srt_t > 2:
                if get_track_voltage() < MIN_TRACK_VOLTAGE:
                    if cfg["museum_mode"]:
                        aud_en.value = False
                        led.brightness = 0
                        led.show()
                    else:
                        stop_all_cmds(False)
                    power_off_start = time.monotonic()
                    while get_track_voltage() < MIN_TRACK_VOLTAGE:
                        power_off_time = time.monotonic() - power_off_start
                        if cfg["cont_mode"]:
                            if not cfg["museum_mode"] and power_off_time > 1 and power_off_time < 3 and not spoken:
                                spoken = True
                                asyncio.create_task(ply_a_1_async(mvc_folder_local + "continuous_mode_deactivated.mp3"))
                        else:
                            if not cfg["museum_mode"] and power_off_time <= 1 and not spoken:
                                spoken = True
                                asyncio.create_task(ply_a_1_async(mvc_folder_local + "animation_canceled.mp3"))
                        await asyncio.sleep(0)
                    power_off_time = time.monotonic() - power_off_start
                    if power_off_time <= 1:
                        if cfg["museum_mode"]:
                            aud_en.value = True
                            led.brightness = 1
                            led.show()
                            return False
                        sw = "left"
                    elif power_off_time > 1 and power_off_time < 3:
                        if cfg["museum_mode"]:
                            stop_all_cmds(False)
                            aud_en.value = True
                            led.brightness = 1
                            led.show()
                            an_running = False
                            return True
                        sw = "left_held"
                    else:
                        led.fill((1, 1, 1))
                        led.show()
                        await asyncio.sleep(0)
        if sw == "left":
            if spoken:
                await asyncio.sleep(1)
                while mix.voice[1].playing:
                    await asyncio.sleep(0)
            else:
                stop_all_cmds(False)
                asyncio.create_task(ply_a_1_async(mvc_folder_local + "animation_canceled.mp3"))
                await asyncio.sleep(1)
                while mix.voice[1].playing:
                    await asyncio.sleep(0)
            an_running = False
            return True
        if sw == "left_held":
            if cfg["cont_mode"] == True:
                if spoken:
                    await asyncio.sleep(1)
                    while mix.voice[1].playing:
                        await asyncio.sleep(0)
                else:
                    stop_all_cmds(False)
                    asyncio.create_task(ply_a_1_async(mvc_folder_local + "continuous_mode_deactivated.mp3"))
                    await asyncio.sleep(1)
                    while mix.voice[1].playing:
                        await asyncio.sleep(0)
                cfg["cont_mode"] = False
                save_cfg_safely()
            else:
                if spoken:
                    await asyncio.sleep(1)
                    while mix.voice[1].playing:
                        await asyncio.sleep(0)
                else:
                    stop_all_cmds(False)
                    asyncio.create_task(ply_a_1_async(mvc_folder_local + "animation_canceled.mp3"))
                    await asyncio.sleep(1)
                    while mix.voice[1].playing:
                        await asyncio.sleep(0)
            an_running = False
            return True
        await asyncio.sleep(0)
    return False


def save_cfg_safely():
    if get_track_voltage() >= MIN_TRACK_VOLTAGE:
        files.write_json_file("/sd/cfg.json", cfg)


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)

################################################################################
# Misc Methods


def get_track_voltage(samples=20):
    total = 0.0
    for _ in range(samples):
        total += track_a_in.value / 65536 * 3.3 * 15.684 * debug_voltage_multiplier
        time.sleep(.0017)
    return total / samples


def rst_def():
    cfg["option_selected"] = "random all"
    cfg["cont_mode"] = False
    cfg["volume"] = "50"
    cfg["HOST_NAME"] = "animator-trolley"
    cfg["serve_webpage"] = True
    cfg["museum_mode"] = False


################################################################################
# Animations

lst_opt = ""


async def an_async(f_nm):
    global lst_opt, ts_mode
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random all":
            h_i = len(snd_opt) - 1
            cur_opt = snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(snd_opt) > 1:
                cur_opt = snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            await an_ts(cur_opt)
        else:
            await an_light_async(cur_opt)
    except Exception as e:
        files.log_item(e)
        await no_trk()
        cfg["option_selected"] = "random all"
        return
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    global flsh_i, flsh_t, an_running, exit_set_hdw_async, t_elsp, srt_t, bckgrnd_vol
    an_running = True
    bckgrnd_vol = 100
    stp_a_0()
    flsh_t = []
    w0_exists = False
    if f_exists(animations_folder + f_nm + ".json") == True:
        flsh_t = files.read_json_file(animations_folder + f_nm + ".json")
    flsh_i = 0
    if len(flsh_t) > 0:
        ft1 = flsh_t[flsh_i].split("|")
        w0_exists = await set_hdw_async(ft1[1])
        srt_t = time.monotonic()
        ft1 = []
        ft2 = []
        ft_last = flsh_t[len(flsh_t)-1].split("|")
        tm_last = float(ft_last[0]) + .1
        flsh_t.append(str(tm_last) + "|")
        if w0_exists:
            flsh_i += 1
    else:
        an_running = False
        return
    while True:
        t_elsp = time.monotonic()-srt_t
        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0
        if flsh_i < len(flsh_t)-1 and t_elsp > float(ft1[0]) - 0.25:
            files.log_item("time elapsed: " + str(t_elsp) +
                           " Timestamp: " + ft1[0] + " Command: " + ft1[1])
            if len(ft1) == 1 or ft1[1] == "":
                result = await set_hdw_async("", dur)
                if result == "STOP":
                    an_running = False
                    return
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    an_running = False
                    return
            flsh_i += 1
        if (not mix.voice[0].playing and w0_exists == "w0_true") or not flsh_i < len(flsh_t)-1:
            mix.voice[0].stop()
            mix.voice[1].stop()
            result = await set_hdw_async("TA_0_2", 0)
            result = await set_hdw_async("VR100", 0)
            an_running = False
            return
        upd_vol(0)
        if await animation_wait(.1):
            result = await set_hdw_async("TA_0_2", 0)
            result = await set_hdw_async("VR100", 0)
            return


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)


async def an_ts(f_nm):
    print("time stamp mode")
    global t_s, t_elsp, ts_mode, ovrde_sw_st, an_running, bckgrnd_vol
    an_running = True
    bckgrnd_vol = 100
    stp_a_0()
    t_elsp = 0
    t_s = [""]
    if (f_exists(animations_folder + f_nm + ".json") == True):
        t_s_from_file = files.read_json_file(
            animations_folder + f_nm + ".json")
    else:
        return
    if len(t_s) > 0:
        t_s[0] = t_s_from_file[0]
        ft1 = t_s[0].split("|")
        w0_exists = await set_hdw_async(ft1[1])
        if not w0_exists:
            return
    else:
        return
    startTime = time.monotonic()
    upd_vol(.1)
    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell or ovrde_sw_st["switch_value"]:
            add_command_to_ts("ZRAND")
            ovrde_sw_st["switch_value"] = ""
        if not mix.voice[0].playing:
            add_command_to_ts("B100,TA_0_1,F0,LN0_0_0_0,B100")
            led.fill((0, 0, 0))
            led.show()
            files.write_json_file(
                animations_folder + f_nm + ".json", t_s)
            break
        await asyncio.sleep(.1)
    ts_mode = False
    ply_a_0(mvc_folder + "timestamp_saved.mp3")
    ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
    ply_a_0(mvc_folder + "animations_are_now_active.mp3")


##############################
# animation effects

brightness = 0
bckgrnd_vol = 100

e_media_file_index = 0
t_media_file_index = 0
c_media_file_index = 0
s_media_file_index = 0
h_media_file_index = 0


def set_hdw_not_async(seg):
    global brightness

    # lights LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1 to 999) RGB 0 to 255
    if seg[:2] == 'LN':
        seg_split = seg.split("_")
        light_n = int(seg_split[0][2:])-1
        r = int(seg_split[1])
        g = int(seg_split[2])
        b = int(seg_split[3])
        set_neo_to(light_n, r, g, b)

    # BXXX = Brightness XXX 0 to 100
    elif seg[0] == 'B':
        brightness = int(seg[1:])
        led.brightness = float(brightness / 100)
        led.show()


async def set_hdw_async(cmd, dur=3):
    global brightness, current_throttle, media_index, exit_set_hdw_async
    global bckgrnd_vol

    if cmd == "":
        return "NOCMDS"
    st = time.monotonic()
    segs = cmd.split(",")
    for seg in segs:
        if exit_set_hdw_async:
            return "STOP"

        # SNXXX = Servo N (0 All, 1-3) XXX 0 to 180
        # SNXXX_SPD = Servo N to XXX at 1 degree every SPD seconds
        elif seg[0] == 'S':
            parts = seg.split("_")
            num = int(parts[0][1])
            v = int(parts[0][2:])
            if len(parts) > 1:
                spd = float(parts[1])
                if num == 0:
                    for i in range(3):
                        asyncio.create_task(move_servo(i, v, spd))
                else:
                    asyncio.create_task(move_servo(num-1, v, spd))
            else:
                if num == 0:
                    for i in range(3):
                        m_servo(i, v)
                else:
                    m_servo(num-1, v)

        # ZDANCE = Dance snowmen for duration of timestamp segment
        elif seg == "ZDANCE":
            asyncio.create_task(dance(st, dur))

        # ZRAND = Random rainbow, fire, or color change
        elif seg == 'ZRAND':
            random_effect(st, 1, 3, dur)

        # ZRWBTTT = red, white, blue wheel, TTT cycle speed in decimal seconds
        elif seg[:4] == 'ZRWB':
            v = float(seg[4:])
            asyncio.create_task(rwb_bow(st, v, dur))

        # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
        elif seg[:2] == 'ZR':
            v = float(seg[2:])
            asyncio.create_task(rbow(st, v, dur))

        # ZFIRE_R_G_B = Fire effect R, G, B, (0-255 or None)
        elif seg.startswith("ZFIRE"):
            parts = seg.split("_")
            r = None
            g = None
            b = None
            if len(parts) > 1 and parts[1] != "None":
                r = int(parts[1])
            if len(parts) > 2 and parts[2] != "None":
                g = int(parts[2])
            if len(parts) > 3 and parts[3] != "None":
                b = int(parts[3])
            asyncio.create_task(fire(st, dur, r, g, b))

        # ZCOLCH_R_G_B_C = Color change R, G, B, (0-255 or None), C one color (True or False)
        elif seg.startswith("ZCOLCH"):
            parts = seg.split("_")
            r = None
            g = None
            b = None
            set_one_color = True
            if len(parts) > 1 and parts[1] != "None":
                r = int(parts[1])
            if len(parts) > 2 and parts[2] != "None":
                g = int(parts[2])
            if len(parts) > 3 and parts[3] != "None":
                b = int(parts[3])
            if len(parts) > 4:
                set_one_color = parts[4].lower() == "true"
            multi_color(r, g, b, set_one_color)
            if exit_set_hdw_async:
                return "STOP"

        # VRFXXX = Fade background volume to XXX, 0 to 100
        elif seg[:3] == 'VRF':
            try:
                target_vol = int(seg[3:])
                if target_vol > 100:
                    target_vol = 100
                if target_vol < 0:
                    target_vol = 0
                while bckgrnd_vol != target_vol:
                    if bckgrnd_vol < target_vol:
                        new_vol = min(bckgrnd_vol + 2, target_vol)
                    else:
                        new_vol = max(bckgrnd_vol - 2, target_vol)
                    await upd_vol_async(0, new_vol)
                    if an_running:
                        if await animation_wait(.03):
                            return "STOP"
                    else:
                        await asyncio.sleep(.03)
            except Exception as e:
                print("VRF error:", e)

        # VRXXX = Set background volume to XXX, 0 to 100
        elif seg[:2] == 'VR':
            try:
                target_vol = int(seg[2:])
                if target_vol > 100:
                    target_vol = 100
                if target_vol < 0:
                    target_vol = 0
                await upd_vol_async(0, target_vol)
            except Exception as e:
                print("VR error:", e)

        # MBXfilename = Background media
        elif seg[:2] == 'MB':
            repeat = seg[2]
            file_nm = seg[3:]
            w0_exists = f_exists(animations_folder + file_nm)
            if w0_exists:
                if repeat == "1":
                    repeat = True
                else:
                    repeat = False
                ply_a_0(animations_folder + file_nm, False, repeat)
                return "w0_true"
            else:
                return "w0_false"

        # MALXXX = Play file, A (P play music, W play music wait, S stop music), L = file location (A animations, E elves, B bells, H horns, T stops, C christmas story) XXX (file name, if RAND random selection of folder, SEQN play next in sequence, SEQF play first in sequence)
        elif seg[0] == 'M':
            if seg[1] == "S":
                stp_a_0()
            elif seg[1] == "W" or seg[1] == "P":
                if seg[2] in FOLDER_MAP:
                    folder = FOLDER_MAP[seg[2]]
                    code = seg[3:]
                    if code == "SEQN":
                        filename, media_index[seg[2]] = get_indexed_media_file(folder, "mp3", media_index[seg[2]])
                    elif code == "SEQF":
                        filename, media_index[seg[2]] = get_indexed_media_file(folder, "mp3", 0)
                    elif code == "RAND":
                        filename = get_random_media_file(folder)
                    else:
                        filename = code
                    w1 = audiomp3.MP3Decoder(open(folder + filename + ".mp3", "rb"))
                if seg[1] == "W" or seg[1] == "P":
                    await stp_a_1()
                    mix.voice[1].play(w1, loop=False)
                if seg[1] == "W":
                    if await wait_snd_1():
                        return "STOP"
                    
        # MBRXXX = Music background, R repeat (0 no, 1 yes), XXX file name
        elif seg[0] == 'H':
            await stp_a_1()
            if seg[1] == "B":
                fn = get_snds("bells/", "bell")
                w1 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[1].play(w1, loop=False)
            elif seg[1] == "H":
                fn = get_snds("horns/", "horn")
                w1 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[1].play(w1, loop=False)

        # some commands need non async access so split those out in another method
        elif seg[:2] == 'LN' or seg[0] == 'B':
            set_hdw_not_async(seg)

        # FXXX = Fade NeoPixel brightness to XXX
        elif seg[0] == 'F':
            target_brightness = int(seg[1:])
            while brightness != target_brightness:
                if brightness < target_brightness:
                    brightness += 1
                    led.brightness = float(brightness / 100)
                else:
                    brightness -= 1
                    led.brightness = float(brightness / 100)
                led.show()
                time.sleep(.01)

        elif seg[0] == 'W':
            s = float(seg[1:])
            if an_running:
                if await animation_wait(s):
                    return "STOP"
            else:
                await asyncio.sleep(s)

        # QXXXX = Add command XXXX any command ie AN_filename to add new animation not run if queuing is turned off
        elif seg[0] == 'Q':
            if cfg["queuing"] == True:
                add_cmd(seg[1:])


def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):
            led[i] = (r, g, b)
    else:
        led[light_n] = (r, g, b)
    led.show()


def random_effect(st, il, ih, dur):
    i = random.randint(il, ih)
    if i == 1:
        asyncio.create_task(rbow(st, 0.012, dur))
    elif i == 2:
        multi_color()
    elif i == 3:
        asyncio.create_task(fire(st, dur))


async def rbow(st, spd, dur):
    last_j = -1
    while True:
        if exit_set_hdw_async:
            return
        now = time.monotonic()
        elapsed = now - st
        if elapsed >= dur:
            return
        j = int(elapsed / spd) & 255
        if j != last_j:
            last_j = j
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
        await asyncio.sleep(0)

def red_white_blue_wheel(pos):
    pos &= 255
    if pos < 64:
        v = pos << 2
        return (255 << 16) | (v << 8) | v
    if pos < 128:
        v = (pos - 64) << 2
        x = 255 - v
        return (x << 16) | (x << 8) | 255
    if pos < 192:
        v = (pos - 128) << 2
        return (v << 16) | (v << 8) | 255
    v = (pos - 192) << 2
    x = 255 - v
    return (255 << 16) | (x << 8) | x

async def rwb_bow(st, spd, dur):
    last_j = -1
    while True:
        if exit_set_hdw_async:
            return
        now = time.monotonic()
        elapsed = now - st
        if elapsed >= dur:
            return
        j = int(elapsed / spd) & 255
        if j != last_j:
            last_j = j
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = red_white_blue_wheel(pixel_index & 255)
            led.show()
        await asyncio.sleep(0)


def multi_color(r=None, g=None, b=None, set_one_color=True):
    if r is None:
        r = random.randint(128, 255)
    if g is None:
        g = random.randint(128, 255)
    if b is None:
        b = random.randint(128, 255)
    for i in range(n_px):
        if set_one_color:
            c = random.randint(0, 2)
            if c == 0:
                r1 = r
                g1 = 0
                b1 = 0
            elif c == 1:
                r1 = 0
                g1 = g
                b1 = 0
            else:
                r1 = 0
                g1 = 0
                b1 = b
            led[i] = (r1, g1, b1)
        else:
            led[i] = (r, g, b)
    led.show()
    return False


async def fire(st, dur, r=None, g=None, b=None):
    next_change = st
    if r is None:
        r = random.randint(128, 255)
    if g is None:
        g = random.randint(128, 255)
    if b is None:
        b = random.randint(128, 255)
    while True:
        if exit_set_hdw_async:
            return
        now = time.monotonic()
        if now - st >= dur:
            return
        if now >= next_change:
            next_change = now + random.uniform(0.05, 0.1)
            for i in range(n_px):
                f = random.randint(0, 110)
                r1 = bnd(r-f, 0, 255)
                g1 = bnd(g-f, 0, 255)
                b1 = bnd(b-f, 0, 255)
                led[i] = (r1, g1, b1)
            led.show()
            upd_vol(0)
        await asyncio.sleep(0)


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


def get_random_media_file(folder_to_search):
    myfiles = files.return_directory("", folder_to_search, ".mp3")
    return random.choice(myfiles) if myfiles else None


def get_indexed_media_file(folder_to_search, file_ext, index):
    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext
    file_ext = file_ext.lower()
    myfiles = files.return_directory("", folder_to_search, file_ext)
    if not myfiles:
        return None, 0
    index = index % len(myfiles)
    selected_file = myfiles[index]
    new_index = (index + 1) % len(myfiles)
    print(f"playing: {selected_file}  ({index}/{len(myfiles)})")
    return selected_file, new_index


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
        ply_a_0(mvc_folder + "animations_are_now_active.mp3")
        files.log_item("Entered base state")
        l_sw.update()
        r_sw.update()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global an_just_added, MIN_TRACK_VOLTAGE
        if an_running:
            return
        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0, ovrde_sw_st, wait_at_end = False)
        spoken = False
        if sw == "none":
            if get_track_voltage() < MIN_TRACK_VOLTAGE:
                led.fill((0, 0, 0))
                led.show()
                power_off_start = time.monotonic()
                while get_track_voltage() < MIN_TRACK_VOLTAGE:
                    power_off_time = time.monotonic() - power_off_start
                    if not cfg["cont_mode"] and not cfg["museum_mode"]:
                        if power_off_time > 1 and power_off_time < 3 and not spoken:
                            spoken = True
                            ply_a_1(mvc_folder_local + "continuous_mode_activated.mp3", wait=False)
                power_off_time = time.monotonic() - power_off_start
                if power_off_time <= 1:
                    sw = "left"
                elif power_off_time > 1 and power_off_time < 3:
                    if not cfg["museum_mode"]:
                        sw = "left_held"
                else:
                    led.fill((1, 1, 1))
                    led.show()
        if sw == "left":
            if not mix.voice[0].playing and not an_running and not an_just_added:
                add_cmd("AN_" + cfg["option_selected"])
                an_just_added = True
        elif sw == "left_held":
            if not cfg["cont_mode"]:
                if spoken:
                    time.sleep(1)
                    while mix.voice[1].playing:
                        time.sleep(.1)
                else:
                    ply_a_1(mvc_folder_local + "continuous_mode_activated.mp3", wait=False)
                    time.sleep(1)
                    while mix.voice[1].playing:
                        time.sleep(.1)
                cfg["cont_mode"] = True
                save_cfg_safely()
        elif sw == "right":
            if not mix.voice[0].playing:
                mch.go_to("main_menu")
        if cfg["cont_mode"] and not mix.voice[0].playing and not an_running and not an_just_added:
            add_cmd("AN_" + cfg["option_selected"])
            an_just_added = True


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        ply_a_0(mvc_folder + "main_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + main_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "volume_level_adjustment":
                vol_adj_mode = True
                ply_a_0(mvc_folder + "volume_adjustment_menu.mp3")
                while vol_adj_mode:
                    sw = utilities.switch_state(
                        l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
                    if sw == "left" and vol_adj_mode:
                        ch_vol("lower")
                    elif sw == "right" and vol_adj_mode:
                        ch_vol("raise")
                    elif sw == "right_held" and vol_adj_mode:
                        save_cfg_safely()
                        ply_a_0(mvc_folder + "all_changes_complete.mp3")
                        vol_adj_mode = False
                        mch.go_to('base_state')
                        upd_vol(0.1)
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "museum_settings":
                mch.go_to('museum_settings')
            else:
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
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
        ply_a_0(mvc_folder + "sound_selection_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    w0 = audiomp3.MP3Decoder(open(
                        "/sd/snd_opt/" + menu_snd_opt[self.i] + ".mp3", "rb"))
                    mix.voice[0].play(w0, loop=False)
                except Exception as e:
                    files.log_item(e)
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if sw == "right":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                save_cfg_safely()
                w0 = audiomp3.MP3Decoder(
                    open(mvc_folder + "option_selected.mp3", "rb"))
                mix.voice[0].play(w0, loop=False)
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
        ply_a_0(mvc_folder + "add_sounds_animate.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(
                mvc_folder + add_snd[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_0(mvc_folder + "create_sound_track_files.mp3")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_0(mvc_folder + "timestamp_mode_on.mp3")
                ply_a_0(mvc_folder + "timestamp_instructions.mp3")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
            else:
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
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
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + web_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if sw == "right":
            selected_menu_item = web_m[self.sel_i]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                opt_sel()
                sel_web()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                opt_sel()
                sel_web()
            elif selected_menu_item == "enter_web_credentials":
                if not mix.voice[0].playing:
                    print("Right button held - starting WiFi setup")
                    start_wifi_setup()
            elif selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            else:
                save_cfg_safely()
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')

class MuseumOpt(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'museum_settings'

    def enter(self, mch):
        files.log_item('Set museum Options')
        sel_museum()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + muse_set[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(muse_set)-1:
                self.i = 0
        if sw == "right":
            selected_menu_item = muse_set[self.sel_i]
            if selected_menu_item == "museum_mode_on":
                cfg["museum_mode"] = True
                save_cfg_safely()
                mch.go_to('base_state')
            elif selected_menu_item == "museum_mode_off":
                cfg["museum_mode"] = False
                save_cfg_safely()
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')
            else:
                save_cfg_safely()
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())
st_mch.add(AddSnds())
st_mch.add(WebOpt())
st_mch.add(MuseumOpt())

aud_en.value = True

upd_vol(.1)


if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        led2[0] = (0, 255, 0)
        led.show()
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        dbm_string = str(-int(avg_rssi))+"dbm"
        spk_str(dbm_string, False)
        spk_web()
    except Exception as e:
        files.log_item(e)
        # time.sleep(5)
        files.log_item("restarting...")
        web = False
        # rst()
else:
    led2[0] = (255, 0, 0)
    led.show()
    time.sleep(3)

# initialize items
upd_vol(.5)

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

###############################################################################
# Main task handling

async def process_cmd_tsk():
    """Task to continuously process commands."""
    while True:
        try:
            await process_cmd()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)


async def server_poll_tsk(server):
    while True:
        try:
            server.poll()
        except OSError as e:
            if e.errno == 5:
                files.log_item("HTTP client connection closed (Errno 5)")
            elif e.errno == 116:
                files.log_item("HTTP client timeout (Errno 116)")
            else:
                files.log_item("HTTP OSError: " + str(e))
        except Exception as e:
            files.log_item("HTTP poll exception: " + str(e))
        await asyncio.sleep(0)


async def state_mach_upd_task(st_mch):
    global an_just_added
    while True:
        st_mch.upd()
        if an_just_added:
            await asyncio.sleep(3)
            an_just_added = False
        else:
            await asyncio.sleep(0)


async def main():
    tasks = [
        process_cmd_tsk(),
        state_mach_upd_task(st_mch),
    ]
    if web:
        tasks.append(server_poll_tsk(server))
    await asyncio.gather(*tasks)
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
