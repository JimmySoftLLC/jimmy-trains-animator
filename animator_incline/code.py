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
# Setup hardware

# Setup pin for vol
a_in = AnalogIn(board.A0)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP6)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP7)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

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
                    open("/sd/mvc/micro_sd_card_success.wav", "rb"))
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

animations_folder = "/sd/snds/"

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = []
menu_snd_opt = []
ts_jsons = []


def upd_media():
    global snd_opt, menu_snd_opt, ts_jsons

    snd_opt = files.return_directory("", "/sd/snds", ".json")

    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all']
    menu_snd_opt.extend(rnd_opt)

    ts_jsons = files.return_directory(
        "", "/sd/t_s_def", ".json")


upd_media()

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cont_run = False
ts_mode = False

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

exit_set_hdw_async = False
is_running_an = False

gc_col("config setup")

################################################################################
# Setup neo pixels
n_px_up = 4

# 16 on demo, 17 tiny, 10 on large, 11 on incline motor2 pin
led_up = neopixel.NeoPixel(board.GP11, n_px_up)
led_up.fill((100, 0, 0))
led_up.show()

n_px_low = 48

# 15 on demo 17 tiny 10 on large, 13 on incline motor4 pin
led_low = neopixel.NeoPixel(board.GP13, n_px_low)
led_low.fill((0, 0, 0))
led_low.show()

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
                if rq_d["an"] == "reset_animation_timing_to_defaults":
                    for ts_fn in ts_jsons:
                        ts = files.read_json_file(
                            "/sd/t_s_def/" + ts_fn + ".json")
                        files.write_json_file(
                            "/sd/snds/"+ts_fn+".json", ts)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
                elif rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
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
                    ply_a_1("/sd/mvc/continuous_mode_activated.wav")
                elif rq_d["an"] == "cont_mode_off":
                    cont_run = False
                    stp_all_cmds()
                    ply_a_1("/sd/mvc/continuous_mode_deactivated.wav")
                elif rq_d["an"] == "timestamp_mode_on":
                    cont_run = False
                    stp_all_cmds()
                    ts_mode = True
                    ply_a_1("/sd/mvc/timestamp_mode_on.wav")
                    ply_a_1("/sd/mvc/timestamp_instructions.wav")
                elif rq_d["an"] == "timestamp_mode_off":
                    ts_mode = False
                    ply_a_1("/sd/mvc/timestamp_mode_off.wav")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/speaker", [POST])
            def btn(request: Request):
                global cfg
                stp_a_0()
                stp_a_1()
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_1("/sd/mvc/left_speaker_right_speaker.wav")
                elif rq_d["an"] == "volume_pot_off":
                    cfg["volume_pot"] = False
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
                elif rq_d["an"] == "volume_pot_on":
                    cfg["volume_pot"] = True
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
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

            @server.route("/update-volume", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                ch_vol(rq_d["action"])
                return Response(request, cfg["volume"])

            @server.route("/get-volume", [POST])
            def btn(request: Request):
                return Response(request, cfg["volume"])

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

################################################################################
# Misc Methods


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-incline"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods


def upd_vol(s, ratio):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536 * ratio/100
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        time.sleep(s)
    else:
        try:
            volume = int(cfg["volume"]) / 100 * ratio/100
        except Exception as e:
            files.log_item(e)
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        time.sleep(s)


async def upd_vol_async(s, ratio):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536 * ratio/100
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        await asyncio.sleep(s)
    else:
        try:
            volume = int(cfg["volume"]) / 100 * ratio/100
        except Exception as e:
            files.log_item(e)
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
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
    cfg["volume_pot"] = False
    if not mix.voice[0].playing and not mix.voice[1].playing:
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_1("/sd/mvc/volume.wav")
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


def exit_early_0():
    upd_vol(0.1, vr)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def ply_a_1(file_name):
    if mix.voice[1].playing:
        mix.voice[1].stop()
        while mix.voice[1].playing:
            upd_vol(0.1, vr)
    w1 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[1].play(w1, loop=False)
    while mix.voice[1].playing:
        exit_early_0()


def wait_snd_1():
    while mix.voice[1].playing:
        exit_early_1()
        pass


def stp_a_1():
    try:
        mix.voice[1].stop()
        wait_snd_1()
        time.sleep(0.5)
        gc_col("stp snd 1")
    except Exception as e:
        files.log_item(e)
        print("Invalid character in string to speak")


def exit_early_1():
    upd_vol(0.1, vr)
    l_sw.update()
    if l_sw.fell:
        mix.voice[1].stop()


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            ply_a_1("/sd/mvc/" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_1("/sd/mvc/dot.wav")
        ply_a_1("/sd/mvc/local.wav")


def l_r_but():
    ply_a_1("/sd/mvc/press_left_button_right_button.wav")


def sel_web():
    ply_a_1("/sd/mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    ply_a_1("/sd/mvc/option_selected.wav")


def spk_sng_num(song_number):
    ply_a_1("/sd/mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    ply_a_1("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            ply_a_1("/sd/mvc/create_sound_track_files.wav")
            break


def spk_web():
    ply_a_1("/sd/mvc/animator_available_on_network.wav")
    ply_a_1("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-incline":
        ply_a_1("/sd/mvc/animator_incline.wav")
        ply_a_1("/sd/mvc/dot.wav")
        ply_a_1("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_1("/sd/mvc/in_your_browser.wav")


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
    while mix.voice[1].playing:
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
    global is_running_an, cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    is_running_an = True
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
            an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            await an_light_async(cur_opt)
            gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random all"
    is_running_an = False
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    global exit_set_hdw_async, ts_mode, cont_run, vr, br

    stp_a_0()
    stp_a_1()

    flsh_t = []

    if (f_exists("/sd/snds/" + f_nm + ".json") == True):
        flsh_t = files.read_json_file(
            "/sd/snds/" + f_nm + ".json")

    flsh_i = 0

    w0_exists = f_exists("/sd/snds/" + f_nm + ".wav")

    if w0_exists:
        w0 = audiocore.WaveFile(
            open("/sd/snds/" + f_nm + ".wav", "rb"))
        mix.voice[0].play(w0, loop=False)
    else:
        print("No wave found for this animation.")

    srt_t = time.monotonic()

    ft1 = []
    ft2 = []

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
                ply_a_1("/sd/mvc/continuous_mode_deactivated.wav")
        if (not mix.voice[0].playing and w0_exists) or not flsh_i < len(flsh_t)-1 or exit_set_hdw_async:
            print("animation done clean up.")
            exit_set_hdw_async = False
            mix.voice[0].stop()
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


def an_ts(f_nm):
    print("time stamp mode")
    global ts_mode

    t_s = []

    f_nm = f_nm.replace("customers_owned_music_", "")

    w0 = audiocore.WaveFile(
        open("/sd/snds/" + f_nm + ".wav", "rb"))
    mix.voice[1].play(w0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1, vr)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            files.log_item(t_elsp)
        if not mix.voice[1].playing:
            led_low.fill((0, 0, 0))
            led_low.show()
            files.write_json_file(
                "/sd/snds/" + f_nm + ".json", t_s)
            break

    ts_mode = False
    ply_a_1("/sd/mvc/timestamp_saved.wav")
    ply_a_1("/sd/mvc/timestamp_mode_off.wav")
    ply_a_1("/sd/mvc/animations_are_now_active.wav")

##############################
# animation effects


def set_neo_to(light_n, r, g, b):
    print("light ", light_n )
    if light_n == -1:
        for i in range(n_px_low):  # in range(n_px_low)
            led_low[i] = (r, g, b)
        for i in range(n_px_up):  # in range(n_px_up)
            led_up[i] = (r, g, b)
        led_low.show()
        led_up.show()
    else:
        if light_n in range(0, n_px_up):
            print("upper lights ", light_n)
            led_up[light_n] = (r, g, b)
            led_up.show()
        else:
            print("lower lights ", light_n - n_px_up)
            led_low[light_n - n_px_up] = (r, g, b)
            led_low.show()

def set_neo_range(start, end, r, g, b):
    show_led_up = False
    show_led_low = False
    try:
        for i in range(start, end+1):  # set values to indexes start to end
            if i < n_px_up:
                led_up[i] = (r, g, b)
                show_led_up = True
            else:
                cur_i = i - n_px_up
                led_low[cur_i] = (r, g, b)
                show_led_low = True
        if show_led_up:led_up.show()
        if show_led_low:led_low.show()
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
            if exit_set_hdw_async:
                return
            for i in range(n_px_low):
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
            for i in range(n_px_low):
                pixel_index = (i * 256 // n_px_low) + j
                led_low[i] = colorwheel(pixel_index & 255)
            led_low.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return


def multi_color():
    for i in range(0, n_px_low):
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
    led_low.show()


async def fire(dur):
    st = time.monotonic()
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        for i in range(n_px_low):
            if exit_set_hdw_async:
                return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led_low[i] = (r1, g1, b1)
            led_low.show()
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


async def set_hdw_async(input_string, dur=3):
    global exit_set_hdw_async, br, vr, car_pos, cal_factor
    # Split the input string into segments
    segs = input_string.split(",")

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
        # MACLXXX = Play file, A (P play music, W play music wait, S stop music, L loop music), C = channel (0 background, 1 overvoice), L = file location (S sound tracks, M mvc folder) XXX (file name)
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
                            open("/sd/mvc/" + seg[4:] + ".wav", "rb"))
                    if seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                        if seg[1] == "L":
                            mix.voice[0].play(w0, loop=True)
                        else:
                            mix.voice[0].play(w0, loop=False)
                    if seg[1] == "W":
                        wait_snd_0()
            elif seg[2] == "1":
                if seg[1] == "S":
                    stp_a_1()
                elif seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                    stp_a_1()
                    if seg[3] == "S":
                        w1 = audiocore.WaveFile(
                            open("/sd/snds/" + seg[4:] + ".wav", "rb"))
                    elif seg[3] == "M":
                        w1 = audiocore.WaveFile(
                            open("/sd/mvc/" + seg[4:] + ".wav", "rb"))
                    if seg[1] == "W" or seg[1] == "P" or seg[1] == "L":
                        if seg[1] == "L":
                            mix.voice[1].play(w1, loop=True)
                        else:
                            mix.voice[1].play(w1, loop=False)
                    if seg[1] == "W":
                        wait_snd_1()
        # SNXXX = Servo N (0 All, 1-6) XXX 0 to 180
        elif seg[0] == 'S':
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    s_arr[i].angle = v
            else:
                s_arr[num-1].angle = int(v)
        # BXXX = Brightness XXX 0 to 100
        elif seg[0] == 'B':
            br = int(seg[1:])
            led_low.brightness = float(br/100)
        # FXXX = Fade brightness in or out XXX 0 to 100
        elif seg[0] == 'F':
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    led_low.brightness = float(br/100)
                else:
                    br -= 1
                    led_low.brightness = float(br/100)
                await upd_vol_async(.1, vr)
        # VRFXXX = Volume ratio fade up or down XXX 0 to 100
        elif seg[:3] == 'VRF':
            v = int(seg[3:])
            while not vr == v:
                if vr < v:
                    vr += 2
                else:
                    vr -= 2
                await upd_vol_async(.03, vr)
        # VRXXX = Volume ratio set to XXX
        elif seg[:2] == 'VR':
            vr = int(seg[2:])
            upd_vol(0, vr)
        # AN_XXX = Animation XXX filename
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
        # C_SSS_XXX_BBB_AAA_RRR = Move car SS speed 0 to 100, XXX Position in decimal cm,
        # BBB target band in decimal cm, AAA acceleration decimal cm/sec, RRR = Ramp sound (True, False)
        elif seg[:2] == 'C_' or seg[:2] == 'CE' or seg[:2] == 'CH':
            MIN_SPEED = 0.2
            global encoder, home_car_pos
            seg_split = seg.split("_")

            spd = int(seg_split[1]) / 100
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
            give_up = abs(car_pos - target_pos)
            srt_t = time.monotonic()

            while True:
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

                t_past = time.monotonic() - srt_t
                if t_past > give_up:
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
        # lights LNR_SSS_EEE_R_G_B = Neo pixel lights SSS start (1 to 999), EEE end (1 to 999), RGB 0 to 255
        elif seg[:3] == 'LNR':
            seg_split = seg.split("_")
            start = int(seg_split[1]) - 1
            end = int(seg_split[2]) - 1
            r = int(seg_split[3])
            g = int(seg_split[4])
            b = int(seg_split[5])
            set_neo_range(start, end, r, g, b)
        # lights LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1 to 999) RGB 0 to 255
        elif seg[:2] == 'LN':
            seg_split = seg.split("_")
            light_n = int(seg_split[0][2:])-1
            r = int(seg_split[1])
            g = int(seg_split[2])
            b = int(seg_split[3])
            set_neo_to(light_n, r, g, b)
        # QXXXX = Add command XXXX any command ie AN_filename to add new animation
        elif seg[0] == 'Q':
            add_cmd(seg[1:])

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
        ply_a_1("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, is_running_an, exit_set_hdw_async
        if not is_running_an:
            sw = utilities.switch_state(
                l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
            if sw == "left_held":
                if cont_run:
                    cont_run = False
                    stp_all_cmds()
                    ply_a_1("/sd/mvc/continuous_mode_deactivated.wav")
                else:
                    cont_run = True
                    ply_a_1("/sd/mvc/continuous_mode_activated.wav")
            elif sw == "left" or cont_run:
                if not is_running_an:
                    add_cmd("AN_" + cfg["option_selected"])
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
        ply_a_1("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_1("/sd/mvc/" + main_m[self.i] + ".wav")
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
                ply_a_1("/sd/mvc/all_changes_complete.wav")
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
        ply_a_1("/sd/mvc/sound_selection_menu.wav")
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
                    open("/sd/mvc/option_selected.wav", "rb"))
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
        ply_a_1("/sd/mvc/add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_1(
                "/sd/mvc/" + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_1("/sd/mvc/create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_1("/sd/mvc/timestamp_mode_on.wav")
                ply_a_1("/sd/mvc/timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_1("/sd/mvc/timestamp_mode_off.wav")
            else:
                ply_a_1("/sd/mvc/all_changes_complete.wav")
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
        ply_a_1("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and not s.vol_adj_mode:
            ply_a_1("/sd/mvc/" + vol_set[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(vol_set)-1:
                s.i = 0
        if vol_set[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw == "right":
                s.vol_adj_mode = True
                ply_a_1("/sd/mvc/volume_adjustment_menu.wav")
        elif sw == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw == "right_held" and s.vol_adj_mode:
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_1("/sd/mvc/all_changes_complete.wav")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1, vr)
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_1("/sd/mvc/all_changes_complete.wav")
            mch.go_to('base_state')
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_1("/sd/mvc/all_changes_complete.wav")
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
            ply_a_1("/sd/mvc/" + web_m[self.i] + ".wav")
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
                ply_a_1("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_1("/sd/mvc/all_changes_complete.wav")
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
    while True:
        st_mch.upd()
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

