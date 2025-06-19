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
from adafruit_motor import  motor
import pwmio
import microcontroller
import rtc
import random
import board
import digitalio
import audiomp3
import audiomixer
import audiobusio
import time
import gc
import files
import os


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
# Setup hardware

# Setup pin for v
a_in = AnalogIn(board.A0)

# setup pin for audio enable 21 on 5v aud board
aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP2)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP3)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)


# setup i2s audio
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
aud_en.value = True

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

aud_en.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Setup motor controller
p_frq = 10000  # Custom PWM frequency in Hz; PWMOut min/max 1Hz/50kHz, default is 500Hz
d_mde = motor.SLOW_DECAY  # Set controller to Slow Decay (braking) mode

# DC motor setup; Set pins to custom PWM frequency
pwm_a = pwmio.PWMOut(board.GP10, frequency=p_frq)
pwm_b = pwmio.PWMOut(board.GP11, frequency=p_frq)
train = motor.DCMotor(pwm_a, pwm_b)
train.decay_mode = d_mde
train.throttle = 0
current_throttle = 0


################################################################################
# Flash data and globals

animations_folder = "/snds/"

cfg = files.read_json_file("cfg.json")

snd_opt = []
menu_snd_opt = []
ts_jsons = []

def upd_media():
    global snd_opt, menu_snd_opt, ts_jsons

    snd_opt = files.return_directory("", "/snds", ".json")

    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all']
    menu_snd_opt.extend(rnd_opt)

    ts_jsons = files.return_directory(
        "", "/t_s_def", ".json")

upd_media()

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("main_menu.json")
main_m = cfg_main["main_menu"]

cfg_vol = files.read_json_file("volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_web = files.read_json_file("web_menu.json")
web_m = cfg_web["web_menu"]

cfg_add_song = files.read_json_file(
    "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = cfg["cont_mode"]

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

gc_col("config setup")

ts_mode = False

flsh_i = 0
flsh_t = []

t_s = []
t_elsp = 0.0

################################################################################
# Setup neo pixels

n_px = 9

led = neopixel.NeoPixel(board.GP22, n_px)

gc_col("Neopixels setup")

################################################################################
# Setup wifi and web server

if (web):
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    gc_col("config wifi imports")

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = files.read_json_file("env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except:
        print("Using default ssid and password")

    for i in range(3):
        web = True
        led[0] = (0, 0, 255)
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
            def base(req: HTTPRequest):
                return FileResponse(req, "index.html", "/")

            @server.route("/mui.min.css")
            def base(req: HTTPRequest):
                return FileResponse(req, "mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(req: HTTPRequest):
                return FileResponse(req, "mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(request: Request):
                rq_d = request.json()
                cfg["option_selected"] = rq_d["an"]
                add_cmd("AN_" + cfg["option_selected"])
                if not mix.voice[0].playing:
                    files.write_json_file("/cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")
            
            @server.route("/defaults", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "reset_animation_timing_to_defaults":
                    for ts_fn in ts_jsons:
                        ts = files.read_json_file(
                            "/t_s_def/" + ts_fn + ".json")
                        files.write_json_file(
                            "/snds/"+ts_fn+".json", ts)
                    ply_a_0("/mvc/all_changes_complete.mp3")
                elif rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("/cfg.json", cfg)
                    ply_a_0("/mvc/all_changes_complete.mp3")
                    st_mch.go_to('base_state')
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/mode", [POST])
            def btn(request: Request):
                global cont_run, ts_mode
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
                    ply_a_0("/mvc/continuous_mode_activated.mp3")
                    cfg["cont_mode"] = cont_run
                    files.write_json_file("/cfg.json", cfg)
                elif rq_d["an"] == "cont_mode_off":
                    stop_all_cmds()
                    ply_a_0("/mvc/continuous_mode_deactivated.mp3")
                    cfg["cont_mode"] = cont_run
                    files.write_json_file("/cfg.json", cfg)
                elif rq_d["an"] == "timestamp_mode_on":
                    stop_all_cmds()
                    ts_mode = True
                    ply_a_0("/mvc/timestamp_mode_on.mp3")
                    ply_a_0("/mvc/timestamp_instructions.mp3")
                elif rq_d["an"] == "timestamp_mode_off":
                    ts_mode = False
                    ply_a_0("/mvc/timestamp_mode_off.mp3")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/speaker", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_0("/mvc/left_speaker_right_speaker.mp3")
                elif rq_d["an"] == "volume_pot_off":
                    cfg["volume_pot"] = False
                    files.write_json_file("/cfg.json", cfg)
                    ply_a_0("/mvc/all_changes_complete.mp3")
                elif rq_d["an"] == "volume_pot_on":
                    cfg["volume_pot"] = True
                    files.write_json_file("/cfg.json", cfg)
                    ply_a_0("/mvc/all_changes_complete.mp3")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/lights", [POST])
            def btn(request: Request):
                rq_d = request.json()
                command = rq_d["an"]
                add_command_to_ts(command)
                set_hdw(command)
                return Response(request, "Utility: " + "Utility: set lights")
            
            @server.route("/set-item-lights", [POST])
            def btn(request: Request):
                rq_d = request.json()
                command = "LN0_" + str(rq_d["r"]) + "_" + \
                str(rq_d["g"]) + "_" + str(rq_d["b"])
                add_command_to_ts(command)
                set_hdw(command)
                return Response(request, "Utility: " + "Utility: set lights")
            
            @server.route("/update-host-name", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                cfg["HOST_NAME"] = rq_d["an"]
                files.write_json_file("/cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                spk_web()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def btn(request: Request):
                stop_all_cmds()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                stop_all_cmds()
                return Response(req, local_ip)

            @server.route("/update-volume", [POST])
            def btn(request: Request):
                rq_d = request.json()
                ch_vol(rq_d["action"])
                files.write_json_file("/cfg.json", cfg)
                return Response(request, cfg["volume"])

            @server.route("/get-volume", [POST])
            def btn(request: Request):
                return Response(request, cfg["volume"])
            
            @server.route("/get-throttle", [POST])
            def btn(request: Request):
                cur_throttle_str = str(current_throttle)
                print("sending current throttle: ", cur_throttle_str)
                return Response(request, cur_throttle_str)

            @server.route("/get-animations", [POST])
            def btn(request: Request):
                stop_all_cmds()
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
                stop_all_cmds()
                rq_d = request.json()
                snd_f = rq_d["an"]
                if (f_exists("/snds/" + snd_f + ".json") == True):
                    f_n = "/snds/" + snd_f + ".json"
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
                        f_n = "/snds/" + \
                            rq_d[3] + ".json"
                        files.write_json_file(f_n, data)
                        data = []
                    upd_media()
                except Exception as e:
                    files.log_item(e)
                    data = []
                    return Response(request, "out of memory")
                return Response(request, "success")
            break
        except Exception as e:
            web = False
            files.log_item(e)
            led[0] = (0, 0, 75)
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
        command = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", command)
        # Process each command as an async operation
        await set_hdw_async(command)
        await asyncio.sleep(0)  # Yield control to the event loop


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_cmds():
    global exit_set_hdw_async,cont_run
    cont_run = False
    clr_cmd_queue()
    exit_set_hdw_async = True
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


def rst_def():
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-trolley"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods


def upd_vol(s):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        mix.voice[1].level = volume
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
        mix.voice[1].level = v
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
        v = 1
    cfg["volume"] = str(v)
    cfg["volume_pot"] = False
    if not mix.voice[0].playing:
        files.write_json_file("/cfg.json", cfg)
        ply_a_0("/mvc/volume.mp3")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1)
    w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        exit_early()


def wait_snd():
    while mix.voice[0].playing:
        exit_early()
        pass

def stp_a_0():
    mix.voice[0].stop()
    wait_snd()


def exit_early():
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
            ply_a_0("/mvc/" + character + ".mp3")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0("/mvc/dot.mp3")
        ply_a_0("/mvc/local.mp3")


def l_r_but():
    ply_a_0("/mvc/press_left_button_right_button.mp3")


def sel_web():
    ply_a_0("/mvc/web_menu.mp3")
    l_r_but()


def opt_sel():
    ply_a_0("/mvc/option_selected.mp3")


def spk_sng_num(song_number):
    ply_a_0("/mvc/song.mp3")
    spk_str(song_number, False)


async def no_trk():
    ply_a_0("/mvc/no_user_soundtrack_found.mp3")
    while True:
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        l_sw.update()
        r_sw.update()
        if sw == "left":
            break
        if sw == "right":
            ply_a_0("/mvc/create_sound_track_files.mp3")
            break
        await asyncio.sleep(.1)
        

def spk_web():
    ply_a_0("/mvc/animator_available_on_network.mp3")
    ply_a_0("/mvc/to_access_type.mp3")
    if cfg["HOST_NAME"] == "animator-ride-on-train":
        ply_a_0("/mvc/animator_ride_on_train.mp3")
        ply_a_0("/mvc/dot.mp3")
        ply_a_0("/mvc/local.mp3")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/mvc/in_your_browser.mp3")

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
    global cont_run, flsh_i, flsh_t

    stp_a_0()

    flsh_t = []

    if (f_exists("/snds/" + f_nm + ".json") == True):
        flsh_t = files.read_json_file(
            "/snds/" + f_nm + ".json")

    flsh_i = 0

    if flsh_i < len(flsh_t)-1:
        ft1 = flsh_t[flsh_i].split("|")
        result = await set_hdw_async(ft1[1])
        print("Result is: ", result)
        if result:
            w0_exists = f_exists("/snds/" + result + ".mp3")
            if w0_exists:
                w0 = audiomp3.MP3Decoder(
                    open("/snds/" + result + ".mp3", "rb"))
                mix.voice[0].play(w0, loop=False) 
            else:
                return
            srt_t = time.monotonic()

            ft1 = []
            ft2 = []
        else:
            return
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
                result = await set_hdw_async("")
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            else:
                result = await set_hdw_async(ft1[1])
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            flsh_i += 1
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and cfg["can_cancel"]:
            mix.voice[0].stop()
            flsh_i = len(flsh_t) - 1
        if sw == "left_held":
            mix.voice[0].stop()
            flsh_i = len(flsh_t) - 1
            if cont_run:
                cont_run = False
                stop_all_cmds()
                ply_a_0("/mvc/continuous_mode_deactivated.mp3")
        if (not mix.voice[0].playing and w0_exists) or not flsh_i < len(flsh_t)-1:
            mix.voice[0].stop()
            add_cmd("TA_0_2")
            return
        await upd_vol_async(.1)

def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)

async def an_ts(f_nm):
    print("time stamp mode")
    global t_s, t_elsp, ts_mode, ovrde_sw_st

    t_s = []

    try:
        w0 = audiomp3.MP3Decoder(
        open("/snds/" + f_nm + ".mp3", "rb"))
    except:
        if (f_exists("/snds/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "/snds/" + f_nm + ".json")
            ft1 = flsh_t[flsh_i].split("|")
            w0_nm = await set_hdw_async(ft1[1])
            print("Result is: ", w0_nm)
            w0 = audiomp3.MP3Decoder(
                open("/snds/" + w0_nm + ".mp3", "rb"))
        
    mix.voice[0].play(w0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell or ovrde_sw_st["switch_value"]:
            add_command_to_ts("")
            ovrde_sw_st["switch_value"] = ""
        if not mix.voice[0].playing:
            add_command_to_ts("")
            led.fill((0, 0, 0))
            led.show()
            files.write_json_file(
                "/snds/" + f_nm + ".json", t_s)
            break
        await asyncio.sleep(.1)

    ts_mode = False

    ply_a_0("/mvc/timestamp_saved.mp3")
    ply_a_0("/mvc/timestamp_mode_off.mp3")
    ply_a_0("/mvc/animations_are_now_active.mp3")



##############################
# animation effects
br = 0


def set_hdw(input_string):
    global sp, br, current_throttle
    # Split the input string into segments
    segs = input_string.split(",")
    # Process each segment
    for seg in segs:
        # TA_XXX_AAA = Train XXX throttle -100 to 100 AAA acceleration increments 1 to 100
        if seg[:2] == 'TA':
            try:
                seg_split = seg.split("_")
                v_str = seg_split[1]         
                target_throttle = int(v_str)
                a_str = seg_split[2]
                acceleration = int(a_str)
                diff = target_throttle - current_throttle
                while diff != 0:
                    if diff > 0:
                        new_throttle = min(current_throttle + acceleration, target_throttle)  # Increase throttle
                    else:
                        new_throttle = max(current_throttle - acceleration, target_throttle)  # Decrease throttle
                    v = new_throttle / 100
                    train.throttle = v
                    current_throttle = new_throttle
                    diff = target_throttle - current_throttle
                    time.sleep(.02)
            except Exception as e:
                print(e)
        # TXXX_AAA = Train XXX throttle -100 to 100
        elif seg[:1] == 'T':
            try:   
                v_str = seg[1:]         
                target_throttle = int(v_str)
                new_throttle = target_throttle
                v = new_throttle / 100
                train.throttle = v
                current_throttle = new_throttle
            except Exception as e:
                print(e)
        # MBXXX = Play background file, XXX (file name)  
        elif seg[:2] == 'MB': # play file
            file_nm = seg[2:]
            return file_nm
        # MALXXX = Play file, A (P play music, W play music wait, S stop music), L = file location (S sound tracks, M mvc folder, T stops) XXX (file name, if RAND random selection of folder)  
        elif seg[0] == 'M': # play file
                if seg[1] == "S":
                    stp_a_0()
                elif seg[1] == "W" or seg[1] == "P":
                    #stp_a_0()
                    if seg[2] == "S":
                        w0 = audiomp3.MP3Decoder(open("/snds/" + seg[3:] + ".mp3", "rb"))
                    elif seg[2] == "M":
                        w0 = audiomp3.MP3Decoder(open("/mvc/" + seg[3:] + ".mp3", "rb"))
                    elif seg[2] == "T":
                        print("this segment is: ", seg[3:])
                        if seg[3:] == "RAND":
                            dude = get_random_media_file("/stops")
                            print("the result is: ", dude)
                            w0 = audiomp3.MP3Decoder(open("/stops/" + dude + ".mp3", "rb"))
                        else:
                            w0 = audiomp3.MP3Decoder(open("/stops/" + seg[3:] + ".mp3", "rb"))
                    if seg[1] == "W" or seg[1] == "P":
                        mix.voice[1].play(w0, loop=False)
                    if seg[1] == "W":
                        wait_snd()
        # WA = Blow horn or whistle, A (H Horn, B Bell)
        elif seg[0] == 'W': # play file
            stp_a_0()
            if seg[1] == "B":
                fn=get_snds("/mvc","bell")
                w0 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[0].play(w0, loop=False)
            elif seg[1] == "H":
                fn=get_snds("/mvc","horn")
                w0 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[0].play(w0, loop=False)
        # lights LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1 to 999) RGB 0 to 255
        elif seg[:2] == 'LN':
                seg_split = seg.split("_")
                light_n = int(seg_split[0][2:])-1
                r = int(seg_split[1])
                g = int(seg_split[2])
                b = int(seg_split[3])
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
                upd_vol(.01)


async def set_hdw_async(input_string):
    global sp, br, current_throttle
    # Split the input string into segments
    segs = input_string.split(",")
    # Process each segment
    for seg in segs:
        # TA_XXX_AAA = Train XXX throttle -100 to 100 AAA acceleration increments 1 to 100
        if seg[:2] == 'TA':
            try:
                seg_split = seg.split("_")
                v_str = seg_split[1]         
                target_throttle = int(v_str)
                a_str = seg_split[2]
                acceleration = int(a_str)
                diff = target_throttle - current_throttle
                while diff != 0:
                    if diff > 0:
                        new_throttle = min(current_throttle + acceleration, target_throttle)  # Increase throttle
                    else:
                        new_throttle = max(current_throttle - acceleration, target_throttle)  # Decrease throttle
                    v = new_throttle / 100
                    train.throttle = v
                    current_throttle = new_throttle
                    diff = target_throttle - current_throttle
                    await asyncio.sleep(.02)
            except Exception as e:
                print(e)
        # TXXX_AAA = Train XXX throttle -100 to 100
        elif seg[:1] == 'T':
            try:   
                v_str = seg[1:]         
                target_throttle = int(v_str)
                new_throttle = target_throttle
                v = new_throttle / 100
                train.throttle = v
                current_throttle = new_throttle
            except Exception as e:
                print(e)
        # MBXXX = Play background file, XXX (file name)  
        elif seg[:2] == 'MB': # play file
            file_nm = seg[2:]
            return file_nm
        # MALXXX = Play file, A (P play music, W play music wait, S stop music), L = file location (S sound tracks, M mvc folder, T stops) XXX (file name, if RAND random selection of folder)  
        elif seg[0] == 'M': # play file
                if seg[1] == "S":
                    stp_a_0()
                elif seg[1] == "W" or seg[1] == "P":
                    #stp_a_0()
                    if seg[2] == "S":
                        w0 = audiomp3.MP3Decoder(open("/snds/" + seg[3:] + ".mp3", "rb"))
                    elif seg[2] == "M":
                        w0 = audiomp3.MP3Decoder(open("/mvc/" + seg[3:] + ".mp3", "rb"))
                    elif seg[2] == "T":
                        print("this segment is: ", seg[3:])
                        if seg[3:] == "RAND":
                            dude = get_random_media_file("/stops")
                            print("the result is: ", dude)
                            w0 = audiomp3.MP3Decoder(open("/stops/" + dude + ".mp3", "rb"))
                        else:
                            w0 = audiomp3.MP3Decoder(open("/stops/" + seg[3:] + ".mp3", "rb"))
                    if seg[1] == "W" or seg[1] == "P":
                        mix.voice[1].play(w0, loop=False)
                    if seg[1] == "W":
                        wait_snd()
        # WA = Blow horn or whistle, A (H Horn, B Bell)
        elif seg[0] == 'W': # play file
            stp_a_0()
            if seg[1] == "B":
                fn=get_snds("/mvc","bell")
                w0 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[0].play(w0, loop=False)
            elif seg[1] == "H":
                fn=get_snds("/mvc","horn")
                w0 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[0].play(w0, loop=False)
        # lights LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1 to 999) RGB 0 to 255
        elif seg[:2] == 'LN':
                seg_split = seg.split("_")
                light_n = int(seg_split[0][2:])-1
                r = int(seg_split[1])
                g = int(seg_split[2])
                b = int(seg_split[3])
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
        # AN_XXX = Animation XXX filename
        elif seg[:2] == 'AN':
            seg_split = seg.split("_")
            # Process each command as an async operation
            if seg_split[1] == "customers":
                await an_async(seg_split[1]+"_"+seg_split[2]+"_"+seg_split[3]+"_"+seg_split[4])
            else:
                await an_async(seg_split[1])

def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):  # in range(n_px)
            led[i] = (r, g, b)
    else:
        led[light_n] = (r, g, b)
    led.show()

def get_random_media_file(folder_to_search):
    files = files.return_directory("", folder_to_search, ".mp3")
    return random.choice(files) if files else None
        
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
        ply_a_0("/mvc/animations_are_now_active.mp3")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left_held":
            if cont_run:
                cont_run = False
                stop_all_cmds()
                ply_a_0("/mvc/continuous_mode_deactivated.mp3")
            else:
                cont_run = True
                ply_a_0("/mvc/continuous_mode_activated.mp3")
        elif (sw == "left" or cont_run) and not mix.voice[0].playing:
            add_cmd("AN_" + cfg["option_selected"])
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
        ply_a_0("/mvc/main_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/mvc/" + main_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "volume_settings":
                mch.go_to('volume_settings')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            else:
                ply_a_0("/mvc/all_changes_complete.mp3")
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
        ply_a_0("/mvc/sound_selection_menu.mp3")
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
                        "/snd_opt/" + menu_snd_opt[self.i] + ".mp3", "rb"))
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
                files.write_json_file("/cfg.json", cfg)
                w0 = audiomp3.MP3Decoder(
                    open("/mvc/option_selected.mp3", "rb"))
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
        ply_a_0("/mvc/add_sounds_animate.mp3")
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
                "/mvc/" + add_snd[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_0("/mvc/create_sound_track_files.mp3")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_0("/mvc/timestamp_mode_on.mp3")
                ply_a_0("/mvc/timestamp_instructions.mp3")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_0("/mvc/timestamp_mode_off.mp3")
            else:
                ply_a_0("/mvc/all_changes_complete.mp3")
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
        ply_a_0("/mvc/volume_settings_menu.mp3")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and not s.vol_adj_mode:
            ply_a_0("/mvc/" + vol_set[s.i] + ".mp3")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(vol_set)-1:
                s.i = 0
        if vol_set[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw == "right":
                s.vol_adj_mode = True
                ply_a_0("/mvc/volume_adjustment_menu.mp3")
        elif sw == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw == "right_held" and s.vol_adj_mode:
            files.write_json_file("/cfg.json", cfg)
            ply_a_0("/mvc/all_changes_complete.mp3")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1)
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            files.write_json_file("/cfg.json", cfg)
            ply_a_0("/mvc/all_changes_complete.mp3")
            mch.go_to('base_state')
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            files.write_json_file("/cfg.json", cfg)
            ply_a_0("/mvc/all_changes_complete.mp3")
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
            ply_a_0("/mvc/" + web_m[self.i] + ".mp3")
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
                ply_a_0("/mvc/web_instruct.mp3")
                sel_web()
            else:
                files.write_json_file("/cfg.json", cfg)
                ply_a_0("/mvc/all_changes_complete.mp3")
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
        server.start(str(wifi.radio.ipv4_address), port=80)
        led[1] = (0, 255, 0)
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        spk_web()
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()
else:
    led[1] = (255, 0, 0)
    led.show()
    time.sleep(3)

# initialize items
upd_vol(.5)

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
            server.poll()
        except OSError as e:
            if e.errno == 116:
                files.log_item("Client timeout (Errno 116)")
            else:
                files.log_item(f"OSError: {e}")
        except Exception as e:
            files.log_item(f"Poll Exception: {e}")
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

