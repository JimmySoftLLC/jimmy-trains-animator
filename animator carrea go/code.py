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
from analogio import AnalogIn
import asyncio
from adafruit_motor import servo, motor
import pwmio
import microcontroller
import rtc
import random
import board
import digitalio
import busio
import storage
import sdcardio
import audiobusio
import audiomixer
import audiocore
import time
import gc
import files
import os
from rainbowio import colorwheel
import audiomp3


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

animations_folder = "/sd/snds/"
mvc_folder = "/sd/mvc/"

m_folder = "msnds/"
l_folder = "lsnds/"
h_folder = "starthorns/"

FOLDER_MAP = {
    'A': animations_folder,
    'M': m_folder,
    'L': l_folder,
    'N': mvc_folder,
    'H': h_folder
}

media_index = {'A': 0, 'L': 0, 'M': 0, 'N': 0, 'H': 0}

################################################################################
# Setup hardware

# Setup pin for vol
a_in = AnalogIn(board.A0)

# Setup pins for Carrera Go throttles
# Wire each as:
# 3.3V -> 2.7K resistor -> ADC pin -> throttle -> GND
# A0 is already used for volume, so use A1 and A2 for the two lanes

car_throttle_left_in = AnalogIn(board.A1)
car_throttle_right_in = AnalogIn(board.A2)

# Calibrate these from real readings on your hardware
# released = higher ADC value
# fully pressed = lower ADC value
CAR_THR_LEFT_RELEASED = 51600
CAR_THR_LEFT_PRESSED = 13500

CAR_THR_RIGHT_RELEASED = 51600
CAR_THR_RIGHT_PRESSED = 13500

# Ignore tiny movement near released position
CAR_THR_LEFT_DEADBAND = 3   # percent
CAR_THR_RIGHT_DEADBAND = 3  # percent

# True = throttles drive cars
# False = throttles act like left/right menu buttons
use_live_car_throttle = False

# A throttle "press" means throttle percentage rises above this threshold
CAR_THR_PRESS_THRESHOLD = 20  # percent
CAR_THR_RELEASE_THRESHOLD = 5  # percent

# Left throttle shutdown sequence:
# number of completed left-button presses required
LEFT_THR_SHUTOFF_COUNT = 10

# maximum allowed time gap between consecutive completed presses
LEFT_THR_SHUTOFF_MAX_GAP = 2.0  # seconds

# Throttle held time to emulate throttle held down
THR_HOLD_TIME = 3.0  # seconds

# Runtime state
left_shutoff_press_times = []

left_throttle_pressed = False
right_throttle_pressed = False

left_throttle_press_time = 0.0
right_throttle_press_time = 0.0

left_throttle_hold_sent = False
right_throttle_hold_sent = False

race_running = False

# Slight dual-throttle press band to start driving
CAR_THR_START = 8       # percent
CAR_THR_START_MAX = 18  # percent

# How long live driving stays enabled after run_start()
CAR_DRIVE_TIME = 60.0   # seconds

# Drive cycle state
CAR_DRIVE_ARMED = "armed"
CAR_DRIVE_STARTING = "starting"
CAR_DRIVE_DRIVING = "driving"

LOW_SOUND_TIME = 1.5
HIGH_SOUND_TIME = 4.0

CAR_MOVING_THRESHOLD = 5.0  # percent


# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP6)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP8)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup sdCard
aud_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=2, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

try:
    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
except Exception as e:
    files.log_item(e)
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        pass
    card_in = False
    while not card_in:
        l_sw.update()
        if l_sw.fell:
            try:
                sd = sdcardio.SDCard(spi, cs)
                vfs = storage.VfsFat(sd)
                storage.mount(vfs, "/sd")
                card_in = True
                w0 = audiocore.WaveFile(
                    open(mvc_folder + "micro_sd_card_success.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass
            except Exception as e:
                files.log_item(e)
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass

aud_en.value = False

# Setup the servos
s_1 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
s_2 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
s_3 = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

s_arr = [s_1, s_2, s_3]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Setup motor controller
p_frq = 10000
d_mde = motor.SLOW_DECAY

# DC motor setup; Set pins to custom PWM frequency
pwm_a = pwmio.PWMOut(board.GP15, frequency=p_frq) # M6
pwm_b = pwmio.PWMOut(board.GP14, frequency=p_frq) # M5
go_car_left = motor.DCMotor(pwm_a, pwm_b)
go_car_left.decay_mode = d_mde
car_pos = 0

################################################################################
# Setup motor controller
p_frq = 10000
d_mde = motor.SLOW_DECAY

# DC motor setup; Set pins to custom PWM frequency
pwm_c = pwmio.PWMOut(board.GP17, frequency=p_frq) # M8
pwm_d = pwmio.PWMOut(board.GP16, frequency=p_frq) # M7
go_car_right = motor.DCMotor(pwm_c, pwm_d)
go_car_right.decay_mode = d_mde
car_pos = 0

################################################################################
# Sd card config variables

animations_folder = "/sd/snds/"

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = []
menu_snd_opt = []
ts_jsons = []
rand_opt = []

def upd_media():
    global snd_opt, menu_snd_opt, ts_jsons, rand_opt

    snd_opt = files.return_directory("", animations_folder, ".json")

    rand_opt = [item for item in snd_opt if item not in ["horns", "start", "end", "test", "test1", "test2", "test3"]]

    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all']
    menu_snd_opt.extend(rnd_opt)

    ts_jsons = files.return_directory(
        "", "/sd/t_s_def", ".json")

upd_media()

web = cfg["serve_webpage"]

print("serve webpage :", web)

cfg_main = files.read_json_file(mvc_folder + "main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(mvc_folder + "web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file(mvc_folder + "volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_add_song = files.read_json_file(mvc_folder + "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cfg["cont_mode"] = False

cfg["max_speed"] = "60"

ts_mode = False

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

an_running = False
an_just_added = False

gc_col("config setup")

################################################################################
# Setup neo pixels

n_px = 7

# 15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP13, n_px)

gc_col("Neopixels setup")

################################################################################
# Setup wifi and web server


def measure_signal_strength(MY_SSID, cycles):
    print("Monitoring signal for:", MY_SSID)
    print("Showing current RSSI + running average (simple sum + count)\n")

    total_sum = 0.0      # running sum of all valid RSSI values
    count = 0            # number of valid readings so far

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
                # Update running total
                total_sum += current_rssi
                count += 1

                # Calculate and show average
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

        time.sleep(0.1)  # your fast polling; increase to 1–5 if needed
        if count > cycles:
            return avg_rssi


if web:
    import socketpool
    import mdns
    gc_col("config wifi imports")
    import wifi
    gc_col("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    gc_col("config wifi imports")

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except Exception as e:
        files.log_item(e)
        print("Using default ssid and password")

    for i in range(3):
        web = True
        led[2] = (0, 0, 255)
        led.show()
        try:
            # connect to your SSID
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            gc_col("wifi connect")

            # setup mdns server
            mdns = mdns.Server(wifi.radio)
            mdns.hostname = cfg["HOST_NAME"]
            mdns.advertise_service(
                service_type="_http", protocol="_tcp", port=80)

            local_ip = str(wifi.radio.ipv4_address)

            # files.log_items IP address to REPL
            files.log_item("IP is" + local_ip)
            files.log_item("Connected")

            # set up server
            pool = socketpool.SocketPool(wifi.radio)
            server = Server(pool, "/static", debug=True)

            gc_col("wifi server")

            ################################################################################
            # Setup routes

            @server.route("/")
            def base(request: HTTPRequest):
                stp_a_0()
                gc_col("Home page.")
                return FileResponse(request, "index.html", "/")

            @server.route("/mui.min.css")
            def base(request: HTTPRequest):
                stp_a_0()
                return FileResponse(request, "/sd/mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(request: HTTPRequest):
                stp_a_0()
                return FileResponse(request, "/sd/mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(request: Request):
                rq_d = request.json()
                cfg["option_selected"] = rq_d["an"]
                add_cmd("AN_" + cfg["option_selected"])
                if not mix.voice[0].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                rq_d = request.json()
                if rq_d["an"] == "reset_animation_timing_to_defaults":
                    for ts_fn in ts_jsons:
                        ts = files.read_json_file(
                            "/sd/t_s_def/" + ts_fn + ".json")
                        files.write_json_file(
                            "/sd/snds/"+ts_fn+".json", ts)
                    ply_a_0(mvc_folder + "all_changes_complete.wav")
                elif rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_0(mvc_folder + "all_changes_complete.wav")
                    st_mch.go_to('base_state')
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/mode", [POST])
            def btn(request: Request):
                global ts_mode
                rq_d = request.json()
                if rq_d["an"] == "left":
                    ovrde_sw_st["switch_value"] = "left"
                elif rq_d["an"] == "right":
                    ovrde_sw_st["switch_value"] = "right"
                elif rq_d["an"] == "right_held":
                    ovrde_sw_st["switch_value"] = "right_held"
                elif rq_d["an"] == "three":
                    ovrde_sw_st["switch_value"] = "three"
                elif rq_d["an"] == "four":
                    ovrde_sw_st["switch_value"] = "four"
                elif rq_d["an"] == "cont_mode_on":
                    cfg["cont_mode"] = True
                    ply_a_0(mvc_folder + "continuous_mode_activated.wav")
                elif rq_d["an"] == "cont_mode_off":
                    cfg["cont_mode"] = False
                    stop_all_cmds()
                    ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
                elif rq_d["an"] == "timestamp_mode_on":
                    cfg["cont_mode"] = False
                    stop_all_cmds()
                    ts_mode = True
                    ply_a_0(mvc_folder + "timestamp_mode_on.wav")
                    ply_a_0(mvc_folder + "timestamp_instructions.wav")
                elif rq_d["an"] == "timestamp_mode_off":
                    ts_mode = False
                    ply_a_0(mvc_folder + "timestamp_mode_off.wav")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/speaker", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_0(mvc_folder + "left_speaker_right_speaker.wav")
                elif rq_d["an"] == "volume_pot_off":
                    cfg["volume_pot"] = False
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_0(mvc_folder + "all_changes_complete.wav")
                elif rq_d["an"] == "volume_pot_on":
                    cfg["volume_pot"] = True
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_0(mvc_folder + "all_changes_complete.wav")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/lights", [POST])
            def btn(request: Request):
                stp_a_0()
                rq_d = request.json()
                add_cmd(rq_d["an"])
                return Response(request, "Utility: " + "Utility: set lights")

            @server.route("/update-host-name", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                rq_d = request.json()
                cfg["HOST_NAME"] = rq_d["an"]
                files.write_json_file("/sd/cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                spk_web()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def btn(request: Request):
                stp_a_0()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                stp_a_0()
                return Response(req, local_ip)

            @server.route("/update-volume", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                ch_vol(rq_d["action"])
                return Response(request, cfg["volume"])

            @server.route("/get-volume", [POST])
            def btn(request: Request):
                return Response(request, cfg["volume"])

            @server.route("/get-animations", [POST])
            def btn(request: Request):
                stp_a_0()
                sounds = []
                sounds.extend(snd_opt)
                my_string = files.json_stringify(sounds)
                return Response(request, my_string)

            @server.route("/create-animation", [POST])
            def btn(request: Request):
                try:
                    global data, animations_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    print(rq_d)
                    f_n = animations_folder + rq_d["fn"] + ".json"
                    print(f_n)
                    an_data = ["0.0|", "1.0|", "2.0|", "3.0|"]
                    files.write_json_file(f_n, an_data)
                    upd_media()
                    return Response(request, "Created animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error creating animation.")

            @server.route("/rename-animation", [POST])
            def btn(request: Request):
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
                    clr_cmd_queue()
                    add_cmd(rq_d["an"])
                    return Response(request, "success")
                except Exception as e:
                    print(e)
                    return Response(request, "error")

            @server.route("/get-animation", [POST])
            def btn(request: Request):
                stp_a_0()
                rq_d = request.json()
                snd_f = rq_d["an"]
                if (f_exists("/sd/snds/" + snd_f + ".json") == True):
                    f_n = "/sd/snds/" + snd_f + ".json"
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "/sd/t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")

            data = []

            @server.route("/save-data", [POST])
            def btn(request: Request):
                global data
                gc_col("prep save data")
                stp_a_0()
                rq_d = request.json()
                try:
                    if rq_d[0] == 0:
                        data = []
                    data.extend(rq_d[2])
                    if rq_d[0] == rq_d[1]:
                        f_n = "/sd/snds/" + \
                            rq_d[3] + ".json"
                        files.write_json_file(f_n, data)
                        data = []
                        gc_col("get data")
                    upd_media()
                except Exception as e:
                    files.log_item(e)
                    data = []
                    gc_col("get data")
                    return Response(request, "out of memory")
                return Response(request, "success")
            
            cycles = 10
            avg_rssi = measure_signal_strength(WIFI_SSID, cycles)
            print(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")

            break

        except Exception as e:
            web = False
            files.log_item(e)
            led[2] = (0, 0, 75)
            led.show()
            time.sleep(2)


gc_col("web server")


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
        cmd = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", cmd)
        # Process each command as an async operation
        if cmd[:2] == 'AN': # AN_XXX = Animation XXX filename
            cmd_split = cmd.split("_")
            clr_cmd_queue()
            if cmd_split[1] == "customers":
                await an_async(cmd_split[1]+"_"+cmd_split[2]+"_"+cmd_split[3]+"_"+cmd_split[4])
            else:
                await an_async(cmd_split[1])
        else:
            await set_hdw_async(cmd)
        await asyncio.sleep(0)  # Yield control to the event loop

def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")

def stop_all_cmds():
    global exit_set_hdw_async, flsh_i, flsh_t
    flsh_i = len(flsh_t)-1
    cfg["cont_mode"] = False
    mix.voice[0].stop()
    mix.voice[1].stop()
    clr_cmd_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")

################################################################################
# Misc Methods


def rst_def():
    cfg["option_selected"] = "random all"
    cfg["cont_mode"] = False
    cfg["volume"] = "20"
    cfg["HOST_NAME"] = "animator-go"
    cfg["serve_webpage"] = True

################################################################################
# Dialog and sound play methods


def upd_vol(s):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        time.sleep(s)
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except Exception as e:
            files.log_item(e)
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        time.sleep(s)


async def upd_vol_async(s):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        await asyncio.sleep(s)
    else:
        try:
            v = int(cfg["volume"]) / 100
        except Exception as e:
            files.log_item(e)
            v = .5
        if v < 0 or v > 1:
            v = .5
    mix.voice[0].level = v
    mix.voice[1].level = v


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
    if not mix.voice[0].playing:
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_0(mvc_folder + "volume.wav")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name, wait=True, repeat=False):
    # Stop if voice is currently playing
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1)

    # Choose decoder based on file extension
    if file_name.lower().endswith(".mp3"):
        w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w0 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)

    # Play the selected file
    mix.voice[0].play(w0, loop=repeat)

    # Wait until playback completes
    if wait:
        while mix.voice[0].playing:
            exit_early()
            pass


def wait_snd():
    while mix.voice[0].playing:
        exit_early()
        pass

def wait_snd_1():
    while mix.voice[1].playing:
        pass

def stp_a_0():
    mix.voice[0].stop()
    wait_snd()
    gc_col("stp snd")

def stp_a_1():
    mix.voice[1].stop()
    wait_snd_1()


def exit_early():
    upd_vol(0.1)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def spk_str(str_to_speak, addLocal = False):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            ply_a_0(mvc_folder + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0(mvc_folder + "dot.wav")
        ply_a_0(mvc_folder + "local.wav")


def l_r_but():
    ply_a_0(mvc_folder + "press_left_button_right_button.wav")


def sel_web():
    ply_a_0(mvc_folder + "web_menu.wav")
    l_r_but()


def opt_sel():
    ply_a_0(mvc_folder + "option_selected.wav")


def spk_sng_num(song_number):
    ply_a_0(mvc_folder + "song.wav")
    spk_str(song_number, False)


def no_trk():
    ply_a_0(mvc_folder + "no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            ply_a_0(mvc_folder + "create_sound_track_files.wav")
            break


def spk_web():
    ply_a_0(mvc_folder + "animator_available_on_network.wav")
    ply_a_0(mvc_folder + "to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-go":
        ply_a_0(mvc_folder + "animator_go.wav")
        ply_a_0(mvc_folder + "dot.wav")
        ply_a_0(mvc_folder + "local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0(mvc_folder + "in_your_browser.wav")


def get_snds(dir, typ):
    sds = []
    s = files.return_directory("", dir, ".wav")
    for el in s:
        p = el.split('_')
        if p[0] == typ:
            sds.append(el)
    mx = len(sds) - 1
    i = random.randint(0, mx)
    fn = dir + "/" + sds[i] + ".wav"
    return fn

################################################################################
# servo helpers


p_arr = [90, 90, 90, 90, 90, 90]


async def cyc_servo(n, s, p_up, p_dwn):
    global p_arr
    while mix.voice[0].playing:
        n_p = p_up
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)
        n_p = p_dwn
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)


def m_servo(n, p):
    global p_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    s_arr[n].angle = p
    p_arr[n][n] = p

################################################################################
# Animations


lst_opt = ""


async def an_async(f_nm):
    global cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random all":
            h_i = len(rand_opt) - 1
            cur_opt = rand_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(rand_opt) > 1:
                cur_opt = rand_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            await an_light_async(cur_opt)
            gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random all"
        return
    gc_col("Animation complete.")

async def an_light_async(f_nm):
    global flsh_i, flsh_t, an_running, exit_set_hdw_async

    an_running = True

    stp_a_0()

    flsh_t = []

    if (f_exists(animations_folder + f_nm + ".json") == True):
        flsh_t = files.read_json_file(
            animations_folder + f_nm + ".json")

    flsh_i = 0

    if flsh_i < len(flsh_t)-1:
        ft1 = flsh_t[flsh_i].split("|")
        result = await set_hdw_async(ft1[1])
        if result:
            result = result.split("_")
            print("Result split is: ", result)
            if result and len(result) > 1:
                w0_exists = f_exists(animations_folder + result[1])
                if w0_exists:
                    if result[0] == "1":
                        repeat = True
                    else:
                        repeat = False
                    ply_a_0(animations_folder + result[1], False, repeat)
                else:
                    return
                srt_t = time.monotonic()

                ft1 = []
                ft2 = []

                # add end command to time stamps so all table values can be used
                ft_last = flsh_t[len(flsh_t)-1].split("|")
                tm_last = float(ft_last[0]) + .1
                flsh_t.append(str(tm_last) + "|")
            else:
                return
        else:
            w0_exists = False
            srt_t = time.monotonic()
        flsh_i += 1
    else:
        return

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
            files.log_item("time elapsed: " + str(t_past) +
                           " Timestamp: " + ft1[0] + " Command: " + ft1[1])
            if (len(ft1) == 1 or ft1[1] == ""):
                result = await set_hdw_async("", dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            flsh_i += 1
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left":
            flsh_i = len(flsh_t)-1
            mix.voice[0].stop()
            mix.voice[1].stop()
            exit_set_hdw_async = True
            add_cmd("GL0,GR0")
            an_running = False
            return
        if sw == "left_held":
            mix.voice[0].stop()
            flsh_i = len(flsh_t) - 1
            if cfg["cont_mode"]:
                stop_all_cmds()
                cfg["cont_mode"] = False
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
        if (not mix.voice[0].playing and w0_exists) or not flsh_i < len(flsh_t)-1:
            mix.voice[0].stop()
            mix.voice[1].stop()
            add_cmd("GL0,GR0")
            an_running = False
            return
        await upd_vol_async(.1)

def an_ts(f_nm):
    print("time stamp mode")
    global ts_mode

    t_s = []

    f_nm = f_nm.replace("customers_owned_music_", "")

    w0 = audiocore.WaveFile(
        open("/sd/snds/" + f_nm + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            files.log_item(t_elsp)
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            files.write_json_file(
                "/sd/snds/" + f_nm + ".json", t_s)
            break

    ts_mode = False
    ply_a_0(mvc_folder + "timestamp_saved.wav")
    ply_a_0(mvc_folder + "timestamp_mode_off.wav")
    ply_a_0(mvc_folder + "animations_are_now_active.wav")

##############################
# animation effects


def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):  # in range(n_px)
            led[i] = (r, g, b)
    else:
        led[light_n] = (r, g, b)
    led.show()

async def random_effect(il, ih, d):
    if exit_set_hdw_async:
        return
    i = random.randint(il, ih)
    if i == 1:
        await rbow(.005, d)
    elif i == 2:
        multi_color()
        await asyncio.sleep(d)
    elif i == 3:
        await fire(d)


async def rbow(spd, dur):
    global exit_set_hdw_async
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw_async:
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
            if exit_set_hdw_async:
                return
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
            
def multi_color():
    for i in range(0, n_px):
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
    led.show()

async def fire(dur):
    st = time.monotonic()
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        for i in range(n_px):
            if exit_set_hdw_async:
                return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led[i] = (r1, g1, b1)
            led.show()
        upd_vol(random.uniform(0.05, 0.1))
        te = time.monotonic()-st
        if te > dur:
            return
        
def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


def read_left_car_throttle_raw():
    return car_throttle_left_in.value


def read_right_car_throttle_raw():
    return car_throttle_right_in.value


def read_left_car_throttle_percent():
    raw = car_throttle_left_in.value

    if raw < CAR_THR_LEFT_PRESSED:
        raw = CAR_THR_LEFT_PRESSED
    if raw > CAR_THR_LEFT_RELEASED:
        raw = CAR_THR_LEFT_RELEASED

    span = CAR_THR_LEFT_RELEASED - CAR_THR_LEFT_PRESSED
    if span <= 0:
        return 0.0

    pct = (CAR_THR_LEFT_RELEASED - raw) / span * 100.0

    if pct < CAR_THR_LEFT_DEADBAND:
        pct = 0.0
    if pct > float(cfg["max_speed"]):
        pct = float(cfg["max_speed"])
   
    return pct


def read_right_car_throttle_percent():
    raw = car_throttle_right_in.value

    if raw < CAR_THR_RIGHT_PRESSED:
        raw = CAR_THR_RIGHT_PRESSED
    if raw > CAR_THR_RIGHT_RELEASED:
        raw = CAR_THR_RIGHT_RELEASED

    span = CAR_THR_RIGHT_RELEASED - CAR_THR_RIGHT_PRESSED
    if span <= 0:
        return 0.0

    pct = (CAR_THR_RIGHT_RELEASED - raw) / span * 100.0

    if pct < CAR_THR_RIGHT_DEADBAND:
        pct = 0.0
    if pct > float(cfg["max_speed"]):
        pct = float(cfg["max_speed"])

    return pct


def read_left_car_throttle():
    return read_left_car_throttle_percent() / 100.0


def read_right_car_throttle():
    return read_right_car_throttle_percent() / 100.0

def throttle_is_pressed(percent_value):
    return percent_value >= CAR_THR_PRESS_THRESHOLD

def throttle_is_released(percent_value):
    return percent_value <= CAR_THR_RELEASE_THRESHOLD

def register_left_shutoff_press():
    global left_shutoff_press_times, use_live_car_throttle, race_running

    if not use_live_car_throttle:
        return

    now = time.monotonic()

    if len(left_shutoff_press_times) == 0:
        left_shutoff_press_times = [now]
    else:
        last_press_time = left_shutoff_press_times[-1]

        if (now - last_press_time) <= LEFT_THR_SHUTOFF_MAX_GAP:
            left_shutoff_press_times.append(now)
        else:
            # too much time passed, start count over
            left_shutoff_press_times = [now]

    print("left shutoff press count:", len(left_shutoff_press_times))

    if len(left_shutoff_press_times) >= LEFT_THR_SHUTOFF_COUNT:
        use_live_car_throttle = False
        race_running = False
        left_shutoff_press_times = []
        ply_a_0(mvc_folder + "throttles_off.wav")
        files.log_item("Live car throttle OFF")
        print("Live car throttle OFF")
        go_car_left.throttle = 0
        go_car_right.throttle = 0



def throttles_in_start_band(left_pct, right_pct):
    return (
        CAR_THR_START <= left_pct <= CAR_THR_START_MAX and
        CAR_THR_START <= right_pct <= CAR_THR_START_MAX
    )

async def run_start():
    print("run_start")
    result = await set_hdw_async("MWHhorn1", 0)
    result = await set_hdw_async("MWHhorn1", 0)
    result = await set_hdw_async("MWHhorn1", 0)
    result = await set_hdw_async("MWHhorn2", 0)
    await asyncio.sleep(0)

async def run_stop():
    print("run_stop")
    result = await set_hdw_async("MWHhorn2", 0)
    await asyncio.sleep(0)

async def left_sound():
    print("left_sound")
    result = await set_hdw_async("MPLRAND", 0)
    await asyncio.sleep(0)

async def right_sound():
    print("right_sound")
    result = await set_hdw_async("MPMRAND", 0)
    await asyncio.sleep(0)

def car_is_moving(percent_value):
    return percent_value > CAR_MOVING_THRESHOLD

async def car_movement_sound_task():
    while True:
        try:
            if use_live_car_throttle and race_running:
                wait_time = random.uniform(LOW_SOUND_TIME, HIGH_SOUND_TIME)
                await asyncio.sleep(wait_time)

                # Re-check after waiting
                if use_live_car_throttle and race_running:
                    left_pct = read_left_car_throttle_percent()
                    right_pct = read_right_car_throttle_percent()

                    left_moving = car_is_moving(left_pct)
                    right_moving = car_is_moving(right_pct)

                    if left_moving and right_moving:
                        # Randomize order a little
                        if random.randint(0, 1) == 0:
                            await left_sound()
                        else:
                            await right_sound()
                    elif left_moving:
                        await left_sound()
                    elif right_moving:
                        await right_sound()
            else:
                await asyncio.sleep(0.1)

        except Exception as e:
            files.log_item(e)
            await asyncio.sleep(0.1)


def handle_left_throttle_button(now, left_pct):
    global left_throttle_pressed
    global left_throttle_press_time
    global left_throttle_hold_sent

    if not left_throttle_pressed:
        if throttle_is_pressed(left_pct):
            left_throttle_pressed = True
            left_throttle_press_time = now
            left_throttle_hold_sent = False
    else:
        if throttle_is_released(left_pct):
            left_throttle_pressed = False

            if use_live_car_throttle:
                register_left_shutoff_press()
            else:
                ovrde_sw_st["switch_value"] = "left"

            left_throttle_press_time = 0.0
            left_throttle_hold_sent = False
        else:
            if (not use_live_car_throttle and
                not left_throttle_hold_sent and
                (now - left_throttle_press_time) >= THR_HOLD_TIME):
                ovrde_sw_st["switch_value"] = "left_held"
                left_throttle_hold_sent = True


def handle_right_throttle_button(now, right_pct):
    global right_throttle_pressed
    global right_throttle_press_time
    global right_throttle_hold_sent

    if not right_throttle_pressed:
        if throttle_is_pressed(right_pct):
            right_throttle_pressed = True
            right_throttle_press_time = now
            right_throttle_hold_sent = False
    else:
        if throttle_is_released(right_pct):
            right_throttle_pressed = False

            if not use_live_car_throttle and not right_throttle_hold_sent:
                ovrde_sw_st["switch_value"] = "right"

            right_throttle_press_time = 0.0
            right_throttle_hold_sent = False
        else:
            if (not use_live_car_throttle and
                not right_throttle_hold_sent and
                (now - right_throttle_press_time) >= THR_HOLD_TIME):
                ovrde_sw_st["switch_value"] = "right_held"
                right_throttle_hold_sent = True

br = 0


async def set_hdw_async(input_string, dur = 3):
    global br, car_pos, use_live_car_throttle
    # Split the input string into segments
    segs = input_string.split(",")

    # Process each segment
    for seg in segs:
        if seg == "":
            print("no command")
        # WXXX = Wait XXX decimal seconds
        elif seg[0] == 'W':  # wait time
            s = float(seg[1:])
            await asyncio.sleep(s)
        # ZRAND = Random rainbow, fire, or color change
        elif seg[0:] == 'ZRAND':
            await random_effect(1, 3, dur)
        # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
        elif seg[:2] == 'ZR':
            v = float(seg[2:])
            await rbow(v, dur)
        # ZFIRE = Fire
        elif seg[0:] == 'ZFIRE':
            await fire(dur)
        # ZCOLCH = Color change
        elif seg[0:] == 'ZCOLCH':
            multi_color()
            await asyncio.sleep(dur)  
        # OPEN open gate
        elif seg[:4] == 'OPEN':
            s_arr[0].angle = 90
        # CLOSE close gate
        elif seg[:5] == 'CLOSE':
            s_arr[0].angle = 5
        # MBRXXX = Music background, R repeat (0 no, 1 yes), XXX (file name) must be in first row all others ignored
        elif seg[:2] == 'MB':  # play file
            repeat = seg[2]
            file_nm = seg[3:]
            return repeat + "_" + file_nm
        # MALXXX = Play file, A (P play music, W play music wait, S stop music), L = file location (A snds, M mario, L luigi, M mvc, H horns) XXX (file name, if RAND random selection of folder, SEQN play next in sequence, SEQF play first in sequence)
        elif seg[0] == 'M':  # play file
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
                    stp_a_1()
                    mix.voice[1].play(w1, loop=False)        
                if seg[1] == "W":
                    wait_snd_1()
        # HORN = Blow horn
        elif seg[:4] == 'HORN':  # play file
            wait_snd()
            stp_a_0()
            fn = get_snds("/sd/mvc", "horn")
            w0 = audiocore.WaveFile(open(fn, "rb"))
            mix.voice[0].play(w0, loop=False)         
        # BELL = Ring bell
        elif seg[:4] == 'BELL':  # play file
            wait_snd()
            stp_a_0()
            fn = get_snds("/sd/mvc", "bell")
            w0 = audiocore.WaveFile(open(fn, "rb"))
            mix.voice[0].play(w0, loop=False)
        # SNXXX = Servo N (0 All, 1-6) XXX 0 to 180
        elif seg[0] == 'S':
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    s_arr[i].angle = v
            else:
                s_arr[num-1].angle = int(v)
        # LNZZZ_R_G_B = Neopixels ZZZ (0 All, 1 to 999) RGB 0 to 255
        elif seg[:2] == 'LN':
            segs_split = seg.split("_")
            light_n = int(segs_split[0][2:])-1
            r = int(segs_split[1])
            g = int(segs_split[2])
            b = int(segs_split[3])
            set_neo_to(light_n, r, g, b)
        # BXXX = Brightness XXX 0 to 100
        elif seg[0] == 'B':
            br = int(seg[1:])
            led.brightness = float(br/100)
        # FXXX = Fade brightness in or out XXX 0 to 100
        elif seg[0] == 'F':
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    led.brightness = float(br/100)
                else:
                    br -= 1
                    led.brightness = float(br/100)
                upd_vol_async(.01)
        # QXXXX = Add command XXXX any command ie AN_filename to add new animation
        elif seg[0] == 'Q':
                cmd = seg[1:]
                add_cmd(cmd)
        # GLXXX or GRXXX = Go left/right car, XXX throttle 0 to 100
        elif seg[0] == 'G':
            # Ignore scripted motor commands when live trigger mode is active
            if use_live_car_throttle:
                continue

            car_id = seg[1]
            v = int(seg[2:]) / 100

            if v < -1:
                v = 0
            if v > 1:
                v = 1

            if car_id == "L":
                go_car_left.throttle = v
            elif car_id == "R":
                go_car_right.throttle = v


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
        ply_a_0(mvc_folder + "animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global an_just_added
        global use_live_car_throttle

        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st
        )

        if sw == "left_held":
            if cfg["cont_mode"] == True:
                cfg["cont_mode"] = False
                stop_all_cmds()
                ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
            else:
                cfg["cont_mode"] = True
                ply_a_0(mvc_folder + "continuous_mode_activated.wav")

        elif sw == "right_held" and not use_live_car_throttle:
            use_live_car_throttle = True
            ply_a_0(mvc_folder + "throttles_on.wav")

        elif (sw == "left" or cfg["cont_mode"]) and not mix.voice[0].playing and not an_running:
            add_cmd("AN_" + cfg["option_selected"])
            an_just_added = True

        elif sw == "right" and not mix.voice[0].playing:
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
        ply_a_0(mvc_folder + "main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global use_live_car_throttle
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw == "right":
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
                ply_a_0(mvc_folder + "all_changes_complete.wav")
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
        ply_a_0(mvc_folder + "sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    w0 = audiocore.WaveFile(open(
                        "/sd/o_snds/" + menu_snd_opt[self.i] + ".wav", "rb"))
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
                files.write_json_file("/sd/cfg.json", cfg)
                w0 = audiocore.WaveFile(
                    open(mvc_folder + "option_selected.wav", "rb"))
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
        ply_a_0(mvc_folder + "add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left":
            ply_a_0(
                mvc_folder + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_0(mvc_folder + "create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_0(mvc_folder + "timestamp_mode_on.wav")
                ply_a_0(mvc_folder + "timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_0(mvc_folder + "timestamp_mode_off.wav")
            else:
                ply_a_0(mvc_folder + "all_changes_complete.wav")
                mch.go_to('base_state')


class VolSet(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0
        s.vol_adj_mode = False

    @property
    def name(s):
        return 'volume_settings'

    def enter(s, mch):
        files.log_item('Set Web Options')
        ply_a_0(mvc_folder + "volume_settings_menu.wav")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left" and not s.vol_adj_mode:
            ply_a_0(mvc_folder + vol_set[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(vol_set)-1:
                s.i = 0
        if vol_set[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw == "right":
                s.vol_adj_mode = True
                ply_a_0(mvc_folder + "volume_adjustment_menu.wav")
        elif sw == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw == "right_held" and s.vol_adj_mode:
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.wav")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1)
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.wav")
            mch.go_to('base_state')
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.wav")
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
            l_sw, r_sw, time.sleep, THR_HOLD_TIME, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + web_m[self.i] + ".wav")
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
            elif selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            elif selected_menu_item == "hear_instr_web":
                ply_a_0(mvc_folder + "web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "all_changes_complete.wav")
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
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        dbm_string = str(-int(avg_rssi))+"dbm"
        spk_str(dbm_string,False)
        spk_web()
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()

# initialize items
add_cmd("CLOSE")
upd_vol(.5)

# Make sure both cars are stopped at boot
go_car_left.throttle = 0
go_car_right.throttle = 0

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

# Main task handling


async def process_cmd_tsk():
    """Task to continuously process commands."""
    while True:
        try:
            await process_cmd()  # Async command processing
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks


async def server_poll_tsk(server):
    """Poll the web server."""
    while True:
        try:
            server.poll()  # Web server polling
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks


async def state_mach_upd_task(st_mch):
    global an_just_added
    while True:
        st_mch.upd()
        if an_just_added:
            await asyncio.sleep(3)
            an_just_added = False
        else:
            await asyncio.sleep(0)


async def car_throttle_motor_task():
    global race_running

    while True:
        try:
            left_pct = read_left_car_throttle_percent()
            right_pct = read_right_car_throttle_percent()

            if use_live_car_throttle and race_running:
                go_car_left.throttle = left_pct / 100.0
                go_car_right.throttle = right_pct / 100.0
            else:
                go_car_left.throttle = 0
                go_car_right.throttle = 0

        except Exception as e:
            files.log_item(e)

        await asyncio.sleep(0.002)

async def car_throttle_button_task():
    global use_live_car_throttle, race_running

    race_state = CAR_DRIVE_ARMED
    race_start_time = 0.0
    start_latched = False

    while True:
        try:
            now = time.monotonic()
            left_pct = read_left_car_throttle_percent()
            right_pct = read_right_car_throttle_percent()

            both_at_start = throttles_in_start_band(left_pct, right_pct)

            handle_left_throttle_button(now, left_pct)
            handle_right_throttle_button(now, right_pct)

            if not use_live_car_throttle:
                race_running = False
                race_state = CAR_DRIVE_ARMED
                race_start_time = 0.0
                start_latched = False
                go_car_left.throttle = 0
                go_car_right.throttle = 0

            else:
                if race_state == CAR_DRIVE_ARMED:
                    race_running = False

                    if both_at_start and not start_latched:
                        start_latched = True
                        race_state = CAR_DRIVE_STARTING
                    elif not both_at_start:
                        start_latched = False

                elif race_state == CAR_DRIVE_STARTING:
                    await run_start()
                    race_running = True
                    race_start_time = time.monotonic()
                    race_state = CAR_DRIVE_DRIVING

                elif race_state == CAR_DRIVE_DRIVING:
                    elapsed = time.monotonic() - race_start_time
                    if elapsed >= CAR_DRIVE_TIME:
                        print("run_stop because elapsed =", elapsed)
                        race_running = False
                        go_car_left.throttle = 0
                        go_car_right.throttle = 0
                        await run_stop()
                        race_state = CAR_DRIVE_ARMED
                        race_start_time = 0.0
                        start_latched = False

        except Exception as e:
            files.log_item(e)

        await asyncio.sleep(0.02)
        
async def main():
    # Create asyncio tasks
    tasks = [
        process_cmd_tsk(),
        state_mach_upd_task(st_mch),
        car_throttle_motor_task(),
        car_throttle_button_task(),
        car_movement_sound_task()
    ]

    if web:
        tasks.append(server_poll_tsk(server))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
