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
import adafruit_vl53l4cd
import rotaryio
import audiomp3


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def f_exists(filename):
    try:
        _ = os.stat(filename)
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

elves_folder = "elves/"
bells_folder = "bells/"
horns_folder = "horns/"
stops_folder = "stops/"
santa_folder = "santa/"
story_folder = "story/"
operator_folder = "operator/"
quotes_folder = "quotes/"

FOLDER_MAP = {
    'E': elves_folder,
    'B': bells_folder,
    'H': horns_folder,
    'T': stops_folder,
    'A': santa_folder,
    'C': story_folder,
    'O': operator_folder,
    'Q': quotes_folder
}

media_index = {'E': 0, 'B': 0, 'H': 0, 'T': 0, 'A': 0, 'C': 0, 'O': 0, 'Q': 0}

################################################################################
# Setup hardware

# Setup pin for vol
a_in = AnalogIn(board.A0)
track_a_in = AnalogIn(board.A2)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

# Setup the switches
l_sw_io = digitalio.DigitalInOut(board.GP6)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)

r_sw_io = digitalio.DigitalInOut(board.GP7)
r_sw_io.direction = digitalio.Direction.INPUT
r_sw_io.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw_io)

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup sdCard
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

aud_en.value = True
try:
    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
except Exception as e:
    files.log_item(e)
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[1].play(w0, loop=False)
    while mix.voice[1].playing:
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
                mix.voice[1].play(w0, loop=False)
                while mix.voice[1].playing:
                    pass
            except Exception as e:
                files.log_item(e)
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[1].play(w0, loop=False)
                while mix.voice[1].playing:
                    pass

aud_en.value = False

# Setup the servos
s_1 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)

s_arr = [s_1]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

br = 100
vr = 100

################################################################################
# setup distance sensor

i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)

vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.distance_mode = 1  # 1 = Short, 2 = Long
vl53.timing_budget = 200  # 200 ms

print("VL53L4CD Simple Test.")
print("--------------------")
model_id, module_type = vl53.model_info
print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

vl53.start_ranging()

while not vl53.data_ready:
    print("data not ready")
    time.sleep(.2)

for _ in range(3):
    vl53.clear_interrupt()
    car_pos = vl53.distance
    print("Distance is: ", car_pos)
    time.sleep(.5)

################################################################################
# Setup motor controller
p_frq = 10000  # Custom PWM frequency in Hz; PWMOut min/max 1Hz/50kHz, default is 500Hz
d_mde = motor.SLOW_DECAY  # Set controller to Slow Decay (braking) mode

# DC motor setup; Set pins to custom PWM frequency, 17 16 on incline, 0 1 on demo
pwm_a = pwmio.PWMOut(board.GP17, frequency=p_frq)
pwm_b = pwmio.PWMOut(board.GP16, frequency=p_frq)
car = motor.DCMotor(pwm_a, pwm_b)
car.decay_mode = d_mde
car_pos = 0
car.throttle = 0
home_car_pos = 0
cal_factor = 27.5

################################################################################
# Setup encoder

# Initialize the encoder with pins A and B, GP11 and GP12 were m2 and m3 now GP14 and GP15 which are m5 and m6, 8 and 9 on demo
encoder = rotaryio.IncrementalEncoder(board.GP14, board.GP15)

last_encoder_pos = encoder.position

print("Encoder position is: ", last_encoder_pos)

################################################################################
# Sd card config variables

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = []
menu_snd_opt = []


def upd_media():
    global snd_opt, menu_snd_opt

    snd_opt = files.return_directory("", "/sd/snds", ".json")

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

cfg_add_song = files.read_json_file(mvc_folder + "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

ts_mode = False

flsh_i = 0
flsh_t = []

t_s = []
t_elsp = 0.0

an_running = False
an_just_added = False

cont_run = False
exit_set_hdw_async = False

srt_t_an = 0

gc_col("config setup")

################################################################################
# Setup neo pixels
n_px_up_house = 4
n_px_cars = 2
n_px_low_house = 4


def update_neo_pixels():
    global led_up, led_low, n_trk_sec, n_px_track, n_px_low
    n_trk_sec = int(cfg["n_trk_sec"])
    n_px_track = n_trk_sec * 14
    n_px_low = n_px_up_house + n_px_cars + n_px_low_house + n_px_track

    # 16 on demo, 17 tiny, 10 on large, 11 on incline motor2 pin
    led_up = neopixel.NeoPixel(board.GP11, n_px_up_house)
    led_up.auto_write = False
    led_up.brightness = .2
    led_up.fill((100, 100, 100))
    led_up.show()

    # 15 on demo 17 tiny 10 on large, 13 on incline motor4 pin
    led_low = neopixel.NeoPixel(board.GP13, n_px_low)
    led_low.auto_write = False
    led_low.brightness = .2
    led_low.fill((100, 100, 100))
    led_low.show()


update_neo_pixels()

gc_col("Neopixels setup")

################################################################################
# Setup wifi and web server

if (web):
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
        led_low[2] = (0, 0, 255)
        led_low.show()
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
            files.log_item("IP is " + local_ip)
            files.log_item("Connected")

            # set up server
            pool = socketpool.SocketPool(wifi.radio)
            server = Server(pool, "/static", debug=True)
            server.port = 80  # Explicitly set port to 80

            gc_col("wifi server")

            ################################################################################
            # Setup routes

            @server.route("/")
            def base(request: HTTPRequest):
                stp_a_0()
                stp_a_1()
                gc_col("Home page.")
                return FileResponse(request, "index.html", "/")

            @server.route("/mui.min.css")
            def base(request: HTTPRequest):
                stp_a_0()
                stp_a_1()
                return FileResponse(request, "/sd/mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(request: HTTPRequest):
                stp_a_0()
                stp_a_1()
                return FileResponse(request, "/sd/mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(request: Request):
                global cfg, cont_run, ts_mode
                rq_d = request.json()
                cfg["option_selected"] = rq_d["an"]
                add_cmd("AN_" + cfg["option_selected"])
                if not mix.voice[0].playing and not mix.voice[1].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                stp_a_1()
                rq_d = request.json()
                if rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_0(mvc_folder + "all_changes_complete.wav")
                    st_mch.go_to('base_state')
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/mode", [POST])
            def btn(request: Request):
                global cfg, cont_run, ts_mode
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
                    cont_run = True
                    ply_a_0(mvc_folder + "continuous_mode_activated.wav")
                elif rq_d["an"] == "cont_mode_off":
                    cont_run = False
                    stp_all_cmds()
                    ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
                elif rq_d["an"] == "timestamp_mode_on":
                    cont_run = False
                    stp_all_cmds()
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
                stp_a_1()
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_0(mvc_folder + "left_speaker_right_speaker.wav")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/lights", [POST])
            def btn(request: Request):
                stp_a_0()
                stp_a_1()
                rq_d = request.json()
                add_cmd(rq_d["an"])
                return Response(request, "Utility: " + "Utility: set lights")

            @server.route("/update-host-name", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                stp_a_1()
                rq_d = request.json()
                cfg["HOST_NAME"] = rq_d["an"]
                files.write_json_file("/sd/cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                spk_web()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-track-voltage", [POST])
            def btn(request: Request):
                track_voltage = get_track_voltage()
                return Response(request, str(track_voltage))

            @server.route("/get-host-name", [POST])
            def btn(request: Request):
                stp_a_0()
                stp_a_1()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                stp_a_0()
                stp_a_1()
                return Response(req, local_ip)

            @server.route("/get-volume", [POST])
            def btn(request: Request):
                return Response(request, cfg["volume"])

            @server.route("/update-volume", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                ch_vol(rq_d["action"])
                return Response(request, cfg["volume"])

            @server.route("/get-positions", [POST])
            def btn(request: Request):
                rq_d = {
                    "lower": cfg["LOWER"],
                    "upper": cfg["UPPER"]
                }
                my_string = files.json_stringify(rq_d)
                return Response(request, my_string)

            @server.route("/update-positions", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                cfg["LOWER"] = rq_d["settingsLower"]
                cfg["UPPER"] = rq_d["settingsUpper"]
                if not mix.voice[0].playing and not mix.voice[1].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                my_string = files.json_stringify(cfg)
                return Response(request, my_string)

            @server.route("/get-track-sections", [POST])
            def btn(request: Request):
                rq_d = {
                    "numberTrackSections": cfg["n_trk_sec"]
                }
                my_string = files.json_stringify(rq_d)
                return Response(request, my_string)

            @server.route("/update-track-sections", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                cfg["n_trk_sec"] = rq_d["numberTrackSections"]
                if not mix.voice[0].playing and not mix.voice[1].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                my_string = files.json_stringify(cfg)
                return Response(request, my_string)

            @server.route("/get-options", [POST])
            def btn(request: Request):
                rq_d = {
                    "queuing": cfg["queuing"],
                    "reset_lights": cfg["reset_lights"]
                }
                my_string = files.json_stringify(rq_d)
                return Response(request, my_string)

            @server.route("/update-options", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                cfg["queuing"] = rq_d["queuing"]
                cfg["reset_lights"] = rq_d["reset_lights"]
                if not mix.voice[0].playing and not mix.voice[1].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                my_string = files.json_stringify(cfg)
                return Response(request, my_string)

            @server.route("/get-encoder", [POST])
            def btn(request: Request):
                global last_encoder_pos, encoder
                last_encoder_pos = encoder.position
                return Response(request, str(last_encoder_pos))

            @server.route("/get-animations", [POST])
            def btn(request: Request):
                stp_a_0()
                stp_a_1()
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
                    an_data = ["0.0|MP0Sname of your track"]
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
                global cfg, cont_run, ts_mode
                stp_a_0()
                stp_a_1()
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
                stp_a_1()
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
                except Exception as e:
                    files.log_item(e)
                    data = []
                    gc_col("get data")
                    return Response(request, "out of memory")
                upd_media()
                gc_col("get data")
                return Response(request, "success")

            break

        except Exception as e:
            web = False
            files.log_item(e)
            led_low[2] = (0, 0, 75)
            led_low.show()
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
        command = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", command)
        # Process each command as an async operation
        await set_hdw_async(command)
        await asyncio.sleep(0)


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stp_all_cmds():
    global exit_set_hdw_async
    clr_cmd_queue()
    exit_set_hdw_async = True
    stp_a_0()
    stp_a_1()
    print("Processing stopped and command queue cleared.")


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)

################################################################################
# Misc Methods


def get_track_voltage(n=10, sample_interval=0.01):
    if n < 1:
        return 0.0

    total = 0.0
    count = 0

    for i in range(n):
        start = time.monotonic()

        raw = track_a_in.value
        if raw is not None:
            # 16-bit ADC 0–3.3V scaled track voltage
            voltage = (raw / 65536) * 3.3 * 14.7
            total += voltage
            count += 1

        # Try to keep consistent timing
        elapsed = time.monotonic() - start
        sleep_time = sample_interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    if count == 0:
        return 0.0

    return total / count


def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-incline"
    cfg["option_selected"] = "ride with comments"
    cfg["volume"] = "50"
    cfg["UPPER"] = "8"
    cfg["LOWER"] = "65"
    cfg["n_trk_sec"] = "3"

################################################################################
# Dialog and sound play methods


volume_trim = 0.5


def upd_vol(s, bckgrnd_snd_ratio):
    try:
        volume = int(cfg["volume"]) / 100 * volume_trim
        volume_ratio = int(cfg["volume"]) / 100 * \
            bckgrnd_snd_ratio/100 * volume_trim
    except Exception as e:
        files.log_item(e)
        volume = .5 * volume_trim
        volume_ratio = .5 * volume_trim
    if volume < 0 or volume > 1 * volume_trim:
        volume = .5 * volume_trim
    if volume_ratio < 0 or volume_ratio > 1 * volume_trim:
        volume_ratio = .5 * volume_trim
    mix.voice[0].level = volume_ratio
    mix.voice[1].level = volume
    time.sleep(s)


async def upd_vol_async(s, bckgrnd_snd_ratio):
    try:
        volume = int(cfg["volume"]) / 100 * volume_trim
        volume_ratio = int(cfg["volume"]) / 100 * \
            bckgrnd_snd_ratio/100 * volume_trim
    except Exception as e:
        files.log_item(e)
        volume = .5 * volume_trim
        volume_ratio = .5 * volume_trim
    if volume < 0 or volume > 1 * volume_trim:
        volume = .5 * volume_trim
    if volume_ratio < 0 or volume_ratio > 1 * volume_trim:
        volume_ratio = .5 * volume_trim
    mix.voice[0].level = volume_ratio
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
        v = 0
    cfg["volume"] = str(v)
    if not mix.voice[0].playing and not mix.voice[1].playing:
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_0(mvc_folder + "volume.wav")
        spk_str(cfg["volume"], False)


def wait_snd_0():
    while mix.voice[0].playing:
        exit_early_0()
        pass


def stp_a_0():
    try:
        mix.voice[0].stop()
        wait_snd_0()
        time.sleep(0.5)
        gc_col("stp snd 0")
    except Exception as e:
        files.log_item(e)
        print("Invalid character in string to speak")


def exit_early_1():
    upd_vol(0.1, vr)
    l_sw.update()
    if l_sw.fell:
        mix.voice[1].stop()


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1, vr)
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[1].play(w0, loop=False)
    while mix.voice[1].playing:
        exit_early_1()


def wait_snd_0():
    while mix.voice[0].playing:
        pass


def wait_snd_1():
    while mix.voice[1].playing:
        pass


def stp_a_0():
    mix.voice[0].stop()
    wait_snd_0()


def stp_a_1():
    mix.voice[1].stop()
    wait_snd_1()


def exit_early_0():
    upd_vol(0.1)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def spk_str(str_to_speak, addLocal):
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
    if cfg["HOST_NAME"] == "animator-incline":
        ply_a_0(mvc_folder + "animator_dash_incline.wav")
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
# Animations


lst_opt = ""


async def an_async(f_nm):
    global an_running, cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    an_running = True
    try:
        if f_nm == "random all":
            h_i = len(snd_opt) - 1
            cur_opt = snd_opt[random.randint(
                0, h_i)]
            while (cur_opt == "demo" or lst_opt == cur_opt) and len(snd_opt) > 1:
                cur_opt = snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            await an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            await an_light_async(cur_opt)
            gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random all"
    an_running = False
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    global exit_set_hdw_async, ts_mode, cont_run, vr, br, srt_t_an

    stp_a_0()
    stp_a_1()

    flsh_t = []

    if (f_exists("/sd/snds/" + f_nm + ".json") == True):
        flsh_t = files.read_json_file(
            "/sd/snds/" + f_nm + ".json")

    flsh_i = 0

    # add end command to time stamps so all table values can be used
    ft_last = flsh_t[len(flsh_t)-1].split("|")
    tm_last = float(ft_last[0]) + .1
    flsh_t.append(str(tm_last) + "|")

    srt_t_an = time.monotonic()

    ft1 = []
    ft2 = []

    while True:
        t_past_an = time.monotonic() - srt_t_an

        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0
        if t_past_an > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            files.log_item("time elapsed: " + str(t_past_an) +
                           " Timestamp: " + ft1[0])
            if (len(ft1) == 1 or ft1[1] == ""):
                result = await set_hdw_async("", dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            flsh_i += 1
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and cfg["can_cancel"]:
            mix.voice[0].stop()
            exit_set_hdw_async = True
            flsh_i = len(flsh_t) - 1
        if sw == "left_held":
            exit_set_hdw_async = True
            mix.voice[0].stop()
            flsh_i = len(flsh_t) - 1
            if cont_run:
                cont_run = False
                stp_all_cmds()
                ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
        if not flsh_i < len(flsh_t)-1 or exit_set_hdw_async:
            print("animation done clean up.")
            exit_set_hdw_async = False
            mix.voice[0].stop()
            if cfg["reset_lights"] == True:
                led_low.fill((0, 0, 0))
                led_low.show()
                led_up.fill((0, 0, 0))
                led_up.show()
            vr = 100
            br = 100
            await set_hdw_async("T0")
            await upd_vol_async(.1, vr)
            return
        await upd_vol_async(.1, vr)


async def an_ts(f_nm):
    print("time stamp mode")
    global ts_mode

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
        await set_hdw_async(ft1[1])
    else:
        return

    startTime = time.monotonic()
    upd_vol(.1, vr)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            files.log_item(t_elsp)
        if not mix.voice[0].playing:
            led_low.fill((0, 0, 0))
            led_low.show()
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
        for i in range(n_px_low):  # in range(n_px_low)
            led_low[i] = (r, g, b)
        for i in range(n_px_up_house):  # in range(n_px_up)
            led_up[i] = (r, g, b)
        led_low.show()
        led_up.show()
    else:
        if light_n in range(0, n_px_up_house):  # upper house 1 to 4
            print("upper house lights ", light_n)
            led_up[light_n] = (r, g, b)
            led_up.show()
        if light_n in range(n_px_up_house, n_px_up_house + n_px_low_house):  # lower house 5 to 8
            print("lower house lights ", light_n - n_px_up_house)
            led_low[light_n - n_px_up_house +
                    n_px_cars + n_px_track] = (r, g, b)
            led_low.show()
        if light_n in range(n_px_up_house + n_px_low_house, n_px_up_house + n_px_low_house + n_px_cars):  # cars 9 to 10
            print("car lights ", light_n - n_px_up_house - n_px_low_house)
            led_low[light_n - n_px_up_house - n_px_low_house] = (r, g, b)
            led_low.show()
        # track 11 to 53 + 14 * track sections over 3
        if light_n in range(n_px_up_house + n_px_low_house + n_px_cars, n_px_up_house + n_px_low_house + n_px_cars + n_px_track):
            print("track lights ", light_n -
                  n_px_up_house - n_px_low_house - n_px_cars)
            led_low[light_n - n_px_up_house - n_px_low_house] = (r, g, b)
            led_low.show()


def set_neo_range(start, end, r, g, b):
    show_led_up = False
    show_led_low = False
    try:
        for light_n in range(start, end + 1):  # set values to indexes start to end
            print("light_n ", light_n)
            if light_n in range(0, n_px_up_house):  # upper house 1 to 4
                print("upper house lights ", light_n)
                led_up[light_n] = (r, g, b)
                show_led_up = True
            # lower house 5 to 8
            if light_n in range(n_px_up_house, n_px_up_house + n_px_low_house):
                print("lower house lights ", light_n - n_px_up_house)
                led_low[light_n - n_px_up_house +
                        n_px_cars + n_px_track] = (r, g, b)
                show_led_low = True
            if light_n in range(n_px_up_house + n_px_low_house, n_px_up_house + n_px_low_house + n_px_cars):  # cars 9 to 10
                print("car lights ", light_n - n_px_up_house - n_px_low_house)
                led_low[light_n - n_px_up_house - n_px_low_house] = (r, g, b)
                show_led_low = True
            # track 11 to 52 + 14 * track sections over 3
            if light_n in range(n_px_up_house + n_px_low_house + n_px_cars, n_px_up_house + n_px_low_house + n_px_cars + n_px_track):
                print("track lights ", light_n -
                      n_px_up_house - n_px_low_house - n_px_cars)
                led_low[light_n - n_px_up_house - n_px_low_house] = (r, g, b)
                show_led_low = True
        if show_led_up:
            led_up.show()
        if show_led_low:
            led_low.show()
    except Exception as e:
        files.log_item(e)


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
            pressed_sw = not  l_sw_io.value
            if pressed_sw:
                ovrde_sw_st["switch_value"] = "left"
                return
            if exit_set_hdw_async:
                return
            for i in range(n_px_cars, n_px_cars + n_px_track):
                pixel_index = (i * 256 // n_px_low) + j
                led_low[i] = colorwheel(pixel_index & 255)
            led_low.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
        for j in reversed(range(0, 255, 1)):
            if exit_set_hdw_async:
                return
            for i in range(n_px_cars, n_px_cars + n_px_track):
                pixel_index = (i * 256 // n_px_low) + j
                led_low[i] = colorwheel(pixel_index & 255)
            led_low.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return


def multi_color():
    for i in range(n_px_cars, n_px_cars + n_px_track):
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
        led_low[i] = (r1, g1, b1)
        pressed_sw = not  l_sw_io.value
        if pressed_sw:
            ovrde_sw_st["switch_value"] = "left"
            return
    led_low.show()


async def fire(dur):
    st = time.monotonic()
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        for i in range(n_px_cars, n_px_cars + n_px_track):
            if exit_set_hdw_async:
                return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led_low[i] = (r1, g1, b1)
            led_low.show()
        pressed_sw = not  l_sw_io.value
        if pressed_sw:
            ovrde_sw_st["switch_value"] = "left"
            return
        upd_vol(random.uniform(0.05, 0.1), vr)
        te = time.monotonic()-st
        if te > dur:
            return


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


async def set_hdw_async(cmd, dur=3):
    global exit_set_hdw_async, br, vr, car_pos, cal_factor, srt_t_an
    if cmd == "":
        return "NOCMDS"
    # Split the input string into segments
    segs = cmd.split(",")

    # Process each segment
    for seg in segs:
        if exit_set_hdw_async:
            return "STOP"
        # end animation
        elif seg[0] == 'E':
            return "STOP"
        elif seg == "":
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
        # MACLXXX = Play file, A (P play music, W play music wait, S stop music, L loop music), C = channel (0 background, 1 overvoice wav, 2 overvoice mp3), L = file location (S sound tracks, M mvc folder, E elves, B bells, H horns, T stops, A santa, C story, O operator) XXX (file name, if RAND random selection of folder, SEQN play next in sequence, SEQF play first in sequence)
        elif seg[0] == 'M':  # play file
            if seg[2] == "0":
                if seg[1] == "S":
                    stp_a_0()
                elif seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                    stp_a_0()
                    if seg[3] == "S":
                        w0 = audiocore.WaveFile(
                            open("/sd/snds/" + seg[4:] + ".wav", "rb"))
                    elif seg[3] == "M":
                        w0 = audiocore.WaveFile(
                            open(mvc_folder + seg[4:] + ".wav", "rb"))
                    if seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                        if seg[1] == "L":
                            mix.voice[0].play(w0, loop=True)
                        else:
                            mix.voice[0].play(w0, loop=False)
                    if seg[1] == "W":
                        wait_snd_0()
            elif seg[2] == "1":
                stp_a_0()
                if seg[1] == "S":
                    stp_a_1()
                elif seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                    stp_a_1()
                    if seg[3] == "S":
                        w1 = audiocore.WaveFile(
                            open("/sd/snds/" + seg[4:] + ".wav", "rb"))
                    elif seg[3] == "M":
                        w1 = audiocore.WaveFile(
                            open(mvc_folder + seg[4:] + ".wav", "rb"))
                    if seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                        if seg[1] == "L":
                            mix.voice[1].play(w1, loop=True)
                        else:
                            mix.voice[1].play(w1, loop=False)
                    if seg[1] == "W":
                        wait_snd_1()
            elif seg[2] == "2":
                if seg[3] in FOLDER_MAP:
                    folder = FOLDER_MAP[seg[3]]
                    code = seg[4:]
                    if code == "SEQN":
                        filename, media_index[seg[3]] = get_indexed_media_file(
                            folder, "mp3", media_index[seg[3]])
                    elif code == "SEQF":
                        filename, media_index[seg[3]] = get_indexed_media_file(
                            folder, "mp3", 0)
                    elif code == "RAND":
                        filename = get_random_media_file(folder)
                    else:
                        filename = code
                    w1 = audiomp3.MP3Decoder(
                        open(folder + filename + ".mp3", "rb"))
                if seg[1] == "W" or seg[1] == "P":
                    stp_a_1()
                    mix.voice[1].play(w1, loop=False)
                if seg[1] == "W":
                    wait_snd_1()
        # SNXXX = Servo N (0 All, 1-6) XXX 0 to 180
        elif seg[0] == 'S':
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(len(s_arr)):
                    s_arr[i].angle = v
            else:
                s_arr[num-1].angle = int(v)
        # BXXX = Brightness XXX 0 to 100
        elif seg[0] == 'B':
            br = int(seg[1:])
            led_up.brightness = float(br/100)
            led_low.brightness = float(br/100)
            led_up.show()
            led_low.show()
        # FXXX = Fade brightness in or out XXX 0 to 100
        elif seg[0] == 'F':
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    print(br)
                    led_up.brightness = float(br/100)
                    led_low.brightness = float(br/100)
                else:
                    br -= 1
                    print(br)
                    led_up.brightness = float(br/100)
                    led_low.brightness = float(br/100)
                led_up.show()
                led_low.show()
                await upd_vol_async(.1, vr)
        # VRFXXX = Volume bckgrnd_snd_ratio fade up or down XXX 0 to 100
        elif seg[:3] == 'VRF':
            v = int(seg[3:])
            while not vr == v:
                if vr < v:
                    vr += 2
                else:
                    vr -= 2
                await upd_vol_async(.03, vr)
        # VRXXX = Volume bckgrnd_snd_ratio set to XXX
        elif seg[:2] == 'VR':
            vr = int(seg[2:])
            upd_vol(0, vr)
        # AN_XXX = Animation XXX filenamen_trk_sec
        elif seg[:2] == 'AN':
            seg_split = seg.split("_")
            # Process each command as an async operation
            if seg_split[1] == "customers":
                await an_async(seg_split[1]+"_"+seg_split[2]+"_"+seg_split[3]+"_"+seg_split[4])
            else:
                await an_async(seg_split[1])
        # TXXX = Car XXX throttle -100 to 100
        elif seg[0] == 'T':
            v = int(seg[1:])/100
            car.throttle = v
        # C_SSS_XXX_BBB_AAA_RRR = Move car SS speed 0 to 100, XXX Position in decimal cm, BBB target band in decimal (UPPER, LOWER, MIDDLE, RATIOYYY YYY 0 lower to 1 upper),
        # BBB target band in decimal cm, AAA acceleration decimal cm/sec, RRR = Ramp sound (True, False)
        elif seg[:2] == 'C_' or seg[:2] == 'CE' or seg[:2] == 'CH':
            MIN_SPEED = 0.2
            global encoder, home_car_pos
            seg_split = seg.split("_")
            spd = int(seg_split[1]) / 100
            if seg_split[2] == 'UPPER' or seg_split[2] == 'LOWER':
                target_pos = float(cfg[seg_split[2]])
            elif seg_split[2] == 'MIDDLE':
                target_pos = (float(cfg["LOWER"])+float(cfg["UPPER"]))/2
            elif seg_split[2][:5] == 'RATIO':
                position_ratio = float(seg_split[2][5:].strip())
                target_pos = (
                    float(cfg["UPPER"])-float(cfg["LOWER"])) * position_ratio + float(cfg["LOWER"])
            else:
                target_pos = float(seg_split[2])
            target_band = float(seg_split[3])
            acc = float(seg_split[4])
            if seg_split[5] == "True":
                ramping_down = True
                ramping_up = True
            else:
                ramping_down = False
                ramping_up = False

            # clear out measurements
            if seg[:2] == 'C_' or seg[:2] == 'CH':
                for _ in range(3):
                    vl53.clear_interrupt()
                    car_pos = vl53.distance
                    await asyncio.sleep(.1)

            # Use current throttle state directly
            current_speed = abs(car.throttle) if car.throttle else 0
            current_direction = 1 if car.throttle >= 0 else -1

            if seg[:2] == 'C_':
                vl53.clear_interrupt()
                car_pos = vl53.distance
            elif seg[:2] == 'CH':
                vl53.clear_interrupt()
                car_pos = vl53.distance

            elif seg[:2] == 'CE':
                car_pos = encoder.position / cal_factor + home_car_pos

            num_times_in_band = 0
            if seg[:2] == 'CH':
                n_trk_sec = int(cfg["n_trk_sec"])
                give_up = n_trk_sec * 20
            else:
                give_up = abs(car_pos - target_pos)
            srt_t_give_up = time.monotonic()

            while True:
                pressed_sw = not  l_sw_io.value
                if pressed_sw:
                    ovrde_sw_st["switch_value"] = "left"
                    return

                if exit_set_hdw_async:
                    car.throttle = 0
                    return

                # Calculate distance and target direction
                distance_to_target = abs(car_pos - target_pos)
                target_direction = 1 if car_pos < target_pos else -1  # 1 forward, -1 reverse

                # Calculate slowdown zone based on acceleration
                slowdown_distance = 4

                # Determine target speed
                if distance_to_target < slowdown_distance:
                    target_speed = max(
                        MIN_SPEED, spd * (distance_to_target / slowdown_distance))
                else:
                    target_speed = spd

                # Handle direction change or speed adjustment
                if current_direction != target_direction and current_speed > 0:
                    # Decelerate to stop before changing direction
                    current_speed -= acc * 0.05
                    if current_speed <= 0:
                        current_speed = 0
                        current_direction = target_direction  # Switch direction when stopped
                else:
                    # Adjust speed in correct direction
                    speed_diff = target_speed - current_speed
                    # Apply acceleration/deceleration
                    if speed_diff > 0:  # Need to accelerate
                        if ramping_up:
                            ramping_up = False
                            asyncio.create_task(set_hdw_async("VRF100"))
                        current_speed += min(acc * 0.05, speed_diff)
                    elif speed_diff < 0:  # Need to decelerate
                        if ramping_down:
                            ramping_down = False
                            asyncio.create_task(set_hdw_async("VRF0"))
                        current_speed += max(-acc * 0.05, speed_diff)
                    current_direction = target_direction

                # Apply clamped speed with direction
                current_speed = max(0, min(spd, current_speed))

                # --- One-time kickstart if motor is stalled ---
                # If the motor sometimes won't start at low throttle, nudge it up until
                # the encoder moves, then ramp back down to target speed.
                # Only do this once per segment run.
                if 'did_kickstart' not in locals():
                    did_kickstart = False

                if not did_kickstart and spd > 0:
                    # consider "not moving" if encoder didn't change for a brief window
                    start_ticks = encoder.position
                    await asyncio.sleep(0.05)
                    # tweak if needed
                    no_move = abs(encoder.position - start_ticks) < 1

                    if no_move:
                        did_kickstart = True
                        # Kick params (tune to taste)
                        # cap between 0.6..1.0
                        KICK_MAX = max(0.6, min(1.0, spd + 0.4))
                        KICK_STEP = 0.08
                        KICK_DT = 0.04
                        STALL_TICKS = 2  # how many encoder counts means "we're moving"

                        # Ramp UP until we see encoder movement or hit KICK_MAX
                        kick_throttle = max(current_speed, MIN_SPEED)
                        while kick_throttle < KICK_MAX:
                            car.throttle = kick_throttle * target_direction
                            await asyncio.sleep(KICK_DT)
                            if abs(encoder.position - start_ticks) >= STALL_TICKS:
                                break
                            kick_throttle += KICK_STEP

                        # Ramp DOWN from whatever we reached to current target_speed
                        # (keep direction consistent)
                        # Snapshot latest target to avoid overshoot if it changed
                        down_target = max(MIN_SPEED, target_speed)
                        while kick_throttle > down_target:
                            kick_throttle = max(
                                down_target, kick_throttle - KICK_STEP)
                            car.throttle = kick_throttle * target_direction
                            await asyncio.sleep(KICK_DT)

                        # Sync control variables so your main speed logic continues smoothly
                        current_speed = down_target
                        current_direction = target_direction

                car.throttle = current_speed * current_direction

                # Check if within target band
                if target_pos - target_band < car_pos < target_pos + target_band:
                    num_times_in_band += 1
                    if num_times_in_band > 2:
                        car.throttle = 0
                        if seg[:2] == 'CH':
                            encoder.position = 0
                            home_car_pos = car_pos
                        break

                print(
                    f"Pos: {car_pos:.1f}, Speed: {car.throttle:.2f}, Dist: {distance_to_target:.1f}")
                await upd_vol_async(.01, vr)

                t_past_give_up = time.monotonic() - srt_t_give_up
                if t_past_give_up > give_up:
                    car.throttle = 0
                    if seg[:2] == 'CH':
                        encoder.position = 0
                        home_car_pos = car_pos
                    break

                if seg[:2] == 'C_':
                    vl53.clear_interrupt()
                    car_pos = vl53.distance
                elif seg[:2] == 'CH':
                    vl53.clear_interrupt()
                    car_pos = vl53.distance
                elif seg[:2] == 'CE':
                    car_pos = encoder.position / cal_factor + home_car_pos
        # lights range LNR_SSS_EEE_R_G_B = Neo pixel lights SSS start, EEE end (0 All, 1-4 upper house, 5-8 lower house, 9-10 cars, track 11-52 + 14 * track sections over 3), RGB 0 to 255
        elif seg[:3] == 'LNR':
            seg_split = seg.split("_")
            start = int(seg_split[1]) - 1
            end = int(seg_split[2]) - 1
            r = int(seg_split[3])
            g = int(seg_split[4])
            b = int(seg_split[5])
            set_neo_range(start, end, r, g, b)
        # LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1-4 upper house, 5-8 lower house, 9-10 cars, track 11-52 + 14 * track sections over 3) RGB 0 to 255
        elif seg[:2] == 'LN':
            seg_split = seg.split("_")
            light_n = int(seg_split[0][2:])-1
            r = int(seg_split[1])
            g = int(seg_split[2])
            b = int(seg_split[3])
            set_neo_to(light_n, r, g, b)
        # QXXXX = Add command XXXX any command ie AN_filename to add new animation not run if queuing is turned off
        elif seg[0] == 'Q':
            if cfg["queuing"] == True:
                add_cmd(seg[1:])
        # RSTTME = Reset animation time to 0
        elif seg[:6] == "RSTTME":
            srt_t_an = time.monotonic()


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
        global cont_run, an_just_added
        if not an_running:
            sw = utilities.switch_state(
                l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
            if sw == "left_held":
                if cont_run:
                    cont_run = False
                    stp_all_cmds()
                    ply_a_0(mvc_folder + "continuous_mode_deactivated.wav")
                else:
                    cont_run = True
                    ply_a_0(mvc_folder + "continuous_mode_activated.wav")
            elif (sw == "left" or cont_run) and not mix.voice[0].playing and not an_running:
                add_cmd("AN_" + cfg["option_selected"])
                an_just_added = True
            elif sw == "right" and not mix.voice[1].playing:
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
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
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
            elif sel_mnu == "volume_level_adjustment":
                mch.go_to('volume_settings')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
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
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[1].playing:
                mix.voice[1].stop()
                while mix.voice[1].playing:
                    pass
            else:
                try:
                    w0 = audiocore.WaveFile(open(
                        "/sd/o_snds/" + menu_snd_opt[self.i] + ".wav", "rb"))
                    mix.voice[1].play(w0, loop=False)
                except Exception as e:
                    files.log_item(e)
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[1].playing:
                    pass
        if sw == "right":
            if mix.voice[1].playing:
                mix.voice[1].stop()
                while mix.voice[1].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                w0 = audiocore.WaveFile(
                    open(mvc_folder + "option_selected.wav", "rb"))
                mix.voice[1].play(w0, loop=False)
                while mix.voice[1].playing:
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
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
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
        ply_a_0(mvc_folder + "volume_adjustment_menu.wav")
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ch_vol("lower")
        elif sw == "right":
            ch_vol("raise")
        elif sw == "right_held":
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.wav")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1, vr)


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

upd_vol(.1, vr)


if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        led_low[3] = (0, 125, 0)
        led_low.show()
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        spk_web()
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        rst()
else:
    led_low[3] = (125, 0, 0)
    led_low.show()
    time.sleep(3)

upd_vol(.5, vr)

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

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
    """Poll the web server."""
    while True:
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
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
    # Create asyncio tasks
    tasks = [
        process_cmd_tsk(),
        state_mach_upd_task(st_mch)
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
