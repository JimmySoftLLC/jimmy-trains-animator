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

from adafruit_debouncer import Debouncer
from adafruit_motor import servo
from analogio import AnalogIn
import random
import digitalio
import pwmio
import busio
import microcontroller
import board
import time
import audiobusio
import audiomixer
import audiocore
import storage
import sdcardio
import gc
import asyncio
import os
import json


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    print("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))

gc_col("Imports gc, files")

def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()

gc_col("imports")

################################################################################
# Setup audio

aud = audiobusio.I2SOut(
    bit_clock=board.GP18,
    word_select=board.GP19,
    data=board.GP20)

mix = audiomixer.Mixer(
    voice_count=1, sample_rate=22050, channel_count=2,
    bits_per_sample=16, samples_signed=True, buffer_size=4096)

aud.play(mix)
mix.voice[0].level = .2

gc_col("audio setup")

################################################################################
# Setup audio pot and enable pin

a_in = AnalogIn(board.A0)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

################################################################################
# Setup the switches

l_sw_io = digitalio.DigitalInOut(board.GP6)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)

r_sw = digitalio.DigitalInOut(board.GP7)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

t_sw = digitalio.DigitalInOut(board.GP8)
t_sw.direction = digitalio.Direction.INPUT
t_sw.pull = digitalio.Pull.UP
t_sw = Debouncer(t_sw)

def switch_state(l_sw, r_sw, upd_vol, h_down_sec, override_switch_state=None, t_sw=None, wait_at_end=True):
    if override_switch_state and override_switch_state["switch_value"]:
        sw = override_switch_state["switch_value"]
        override_switch_state["switch_value"] = ""
        return sw
    l_sw.update()
    r_sw.update()
    if t_sw:
        t_sw.update()
    if l_sw.fell:
        cyc = 0
        while True:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec * 10:
                return "left_held"
            if l_sw.rose:
                return "left"
    if r_sw.fell:
        cyc = 0
        while True:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec * 10:
                return "right_held"
            if r_sw.rose:
                return "right"
    if t_sw and t_sw.fell:
        while True:
            upd_vol(.1)
            t_sw.update()
            if t_sw.rose:
                return "trigger"
    if not l_sw.value:
        cyc = 0
        while True:
            upd_vol(.1)
            l_sw.update()
            cyc += 1
            if cyc > h_down_sec * 10:
                return "left_held"
            if l_sw.rose:
                return "none"
    if not r_sw.value:
        cyc = 0
        while True:
            upd_vol(.1)
            r_sw.update()
            cyc += 1
            if cyc > h_down_sec * 10:
                return "right_held"
            if r_sw.rose:
                return "none"
    if wait_at_end:
        upd_vol(.1)
    return "none"

################################################################################
# Setup sdCard

aud_en.value = True

sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
except Exception as e:
    print(e)
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        pass
    cardInserted = False
    while not cardInserted:
        l_sw.update()
        if l_sw.fell:
            try:
                sdcard = sdcardio.SDCard(spi, cs)
                vfs = storage.VfsFat(sdcard)
                storage.mount(vfs, "/sd")
                cardInserted = True
                w0 = audiocore.WaveFile(
                    open("/sd/mvc/micro_sd_card_success.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass
            except Exception as e:
                print(e)
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass

aud_en.value = False

# Setup the servo
f_s = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
t_s = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
f_s = servo.Servo(f_s)
t_s = servo.Servo(t_s)

################################################################################
# Config and globals

def read_json_file(file_name):
    with open(file_name, "r") as f:
        return json.loads(f.read())

def write_json_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(json.dumps(data))

try:
    cfg = read_json_file("/sd/cfg.json")
except Exception as e:
    print("config file corrupt writing out default deep copy")
    cfg = read_json_file("/sd/cfg_default.json")
    write_json_file("/sd/cfg.json", cfg)

cfg["cont_mode"] = False

cfg_vol = read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

t_lst_p = cfg["tree_up_pos"]
t_min = 60
t_max = 180
if cfg["tree_down_pos"] < t_min or cfg["tree_down_pos"] > t_max:
    cfg["tree_down_pos"] = t_min
if cfg["tree_up_pos"] < t_min or cfg["tree_up_pos"] > t_max:
    cfg["tree_up_pos"] = t_max

f_lst_p = cfg["feller_rest_pos"]
f_min = 0
f_max = 170
if cfg["feller_rest_pos"] < f_min or cfg["feller_rest_pos"] > f_max:
    cfg["feller_rest_pos"] = f_min
if cfg["feller_chop_pos"] > f_max or cfg["feller_chop_pos"] < f_min:
    cfg["feller_chop_pos"] = f_max

cfg_main = read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_snds = read_json_file("/sd/mvc/choose_sounds.json")
snd_opts = cfg_snds["choose_sounds"]

cfg_adj_f_t = read_json_file(
    "/sd/mvc/adjust_feller_and_tree.json")
adj_f_t = cfg_adj_f_t["adjust_feller_and_tree"]

cfg_mov_f_t = read_json_file(
    "/sd/mvc/move_feller_and_tree.json")
mov_f_t = cfg_mov_f_t["move_feller_and_tree"]

cfg_dlg = read_json_file(
    "/sd/mvc/set_options.json")
dlg_m = cfg_dlg["set_options"]

web = cfg["serve_webpage"]

f_mov_typ = "feller_rest_pos"
t_mov_typ = "tree_up_pos"

button_press_start = None
an_running = False
an_just_added = False

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

gc_col("config setup")

################################################################################
# Setup wifi and web server

if (web):
    import socketpool
    import mdns
    gc_col("config wifi imports")
    import wifi
    gc_col("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
    gc_col("config wifi imports")

    print("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except Exception as e:
        print(e)
        print("Using default ssid and password")

    try:
        for i in range(3):
            web = True

            # connect to your SSID
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            gc_col("wifi connect")

            # setup mdns server
            mdns_server = mdns.Server(wifi.radio)
            mdns_server.hostname = cfg["HOST_NAME"]
            mdns_server.advertise_service(
                service_type="_http", protocol="_tcp", port=80)

            # prints MAC address to REPL
            mystring = [hex(i) for i in wifi.radio.mac_address]
            print("My MAC addr:" + str(mystring))

            local_ip = str(wifi.radio.ipv4_address)

            # prints IP address to REPL
            print("My IP address is" + local_ip)
            print("Connected to WiFi")

            # set up server
            pool = socketpool.SocketPool(wifi.radio)
            server = Server(pool, "/static", debug=True)
            gc_col("wifi server")

            ################################################################################
            # Setup routes

            @server.route("/")
            def base(request: HTTPRequest):
                gc_col("Home page.")
                stp_all_cmds()
                return FileResponse(request, "index.html", "/")

            @server.route("/mui.min.css")
            def base(request: HTTPRequest):
                stp_all_cmds()
                return FileResponse(request, "mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(request: HTTPRequest):
                stp_all_cmds()
                return FileResponse(request, "mui.min.js", "/")

            @server.route("/animation", [POST])
            def buttonpress(request: Request):
                rq_d = request.json()
                add_cmd(rq_d["an"])
                return Response(request, "Animation " + rq_d["an"] + " started.")

            @server.route("/feller", [POST])
            def buttonpress(request: Request):
                global cfg
                global f_mov_typ
                stp_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "feller_rest_pos":
                    f_mov_typ = "feller_rest_pos"
                    m_f_spd(cfg[f_mov_typ], 0.01)
                    return Response(request, "Moved feller to rest position.")
                elif rq_d["an"] == "feller_chop_pos":
                    f_mov_typ = "feller_chop_pos"
                    m_f_spd(cfg[f_mov_typ], 0.01)
                    return Response(request, "Moved feller to chop position.")
                elif rq_d["an"] == "feller_adjust":
                    f_mov_typ = "feller_rest_pos"
                    m_f_spd(cfg[f_mov_typ], 0.01)
                    return Response(request, "Redirected to feller-adjust page.")
                elif rq_d["an"] == "feller_home":
                    return Response(request, "Redirected to home page.")
                elif rq_d["an"] == "feller_clockwise":
                    cal_l_but(
                        f_s, f_mov_typ, 1, f_min, f_max)
                    return Response(request, "Moved feller clockwise.")
                elif rq_d["an"] == "feller_counter_clockwise":
                    cal_r_but(
                        f_s, f_mov_typ, 1, f_min, f_max)
                    return Response(request, "Moved feller counter clockwise.")
                elif rq_d["an"] == "feller_cal_saved":
                    wrt_cal()
                    st_mch.go_to('base_state')
                    return Response(request, "Feller " + f_mov_typ + " cal saved.")

            @server.route("/tree", [POST])
            def buttonpress(request: Request):
                global cfg
                global t_mov_typ
                stp_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "tree_up_pos":
                    t_mov_typ = "tree_up_pos"
                    m_t_spd(cfg[t_mov_typ], 0.01)
                    return Response(request, "Moved tree to up position.")
                elif rq_d["an"] == "tree_down_pos":
                    t_mov_typ = "tree_down_pos"
                    m_t_spd(cfg[t_mov_typ], 0.01)
                    return Response(request, "Moved tree to fallen position.")
                elif rq_d["an"] == "tree_adjust":
                    t_mov_typ = "tree_up_pos"
                    m_t_spd(cfg[t_mov_typ], 0.01)
                    return Response(request, "Redirected to tree-adjust page.")
                elif rq_d["an"] == "tree_home":
                    return Response(request, "Redirected to home page.")
                elif rq_d["an"] == "tree_up":
                    cal_l_but(
                        t_s, t_mov_typ, -1, t_min, t_max)
                    return Response(request, "Moved tree up.")
                elif rq_d["an"] == "tree_down":
                    cal_r_but(
                        t_s, t_mov_typ, -1, t_min, t_max)
                    return Response(request, "Moved tree down.")
                elif rq_d["an"] == "tree_cal_saved":
                    wrt_cal()
                    st_mch.go_to('base_state')
                    return Response(request, "Tree " + t_mov_typ + " cal saved.")

            @server.route("/settings", [POST])
            def buttonpress(request: Request):
                global cfg
                rq_d = request.json()
                if rq_d["an"] == "opening_dialog_on":
                    cfg["opening_dialog"] = True
                elif rq_d["an"] == "opening_dialog_off":
                    cfg["opening_dialog"] = False
                elif rq_d["an"] == "feller_advice_on":
                    cfg["feller_advice"] = True
                elif rq_d["an"] == "feller_advice_off":
                    cfg["feller_advice"] = False
                elif "cont_mode_on" == rq_d["an"]:
                    cfg["cont_mode"] = True
                elif "cont_mode_off" == rq_d["an"]:
                    cfg["cont_mode"] = False
                elif rq_d["an"] == "museum_mode_on":
                    cfg["museum_mode"] = True
                elif rq_d["an"] == "museum_mode_off":
                    cfg["museum_mode"] = False
                write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                return Response(request, "Dialog option cal saved.")

            @server.route("/utilities", [POST])
            def buttonpress(request: Request):
                global cfg
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_0("/sd/mvc/left_speaker_right_speaker.wav")
                elif rq_d["an"] == "volume_pot_off":
                    cfg["volume_pot"] = False
                    write_json_file("/sd/cfg.json", cfg)
                    ply_a_0("/sd/mvc/all_changes_complete.wav")
                elif rq_d["an"] == "volume_pot_on":
                    cfg["volume_pot"] = True
                    write_json_file("/sd/cfg.json", cfg)
                    ply_a_0("/sd/mvc/all_changes_complete.wav")
                elif rq_d["an"] == "reset_to_defaults":
                    reset_to_defaults()
                    write_json_file("/sd/cfg.json", cfg)
                    ply_a_0("/sd/mvc/all_changes_complete.wav")
                    st_mch.go_to('base_state')

                return Response(request, "Dialog option cal saved.")

            @server.route("/update-host-name", [POST])
            def buttonpress(request: Request):
                global cfg
                stp_all_cmds()
                data_object = request.json()
                cfg["HOST_NAME"] = data_object["text"]
                write_json_file("/sd/cfg.json", cfg)
                mdns_server.hostname = cfg["HOST_NAME"]
                speak_webpage()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def buttonpress(request: Request):
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                return Response(req, local_ip)

            @server.route("/update-volume", [POST])
            def buttonpress(request: Request):
                global cfg
                data_object = request.json()
                ch_vol(data_object["action"])
                return Response(request, cfg["volume"])

            @server.route("/get-volume", [POST])
            def buttonpress(request: Request):
                return Response(request, cfg["volume"])

            @server.route("/mode", [POST])
            def buttonpress(req: Request):
                global cfg
                rq_d = req.json()
                stp_all_cmds()
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
                return Response(req, "Mode set")

            @server.route("/update-min-chops", [POST])
            def buttonpress(request: Request):
                global cfg
                data_object = request.json()
                min_chops = min(max(int(data_object["text"]), 1), 20)
                cfg["min_chops"] = str(min(min_chops, int(cfg["max_chops"])))
                write_json_file("/sd/cfg.json", cfg)
                spk_str(cfg["min_chops"], False)
                return Response(request, cfg["min_chops"])

            @server.route("/get-min-chops", [POST])
            def buttonpress(request: Request):
                print(cfg["min_chops"])
                return Response(request, cfg["min_chops"])

            @server.route("/update-max-chops", [POST])
            def buttonpress(request: Request):
                global cfg
                data_object = request.json()
                max_chops = min(max(int(data_object["text"]), 1), 20)
                cfg["max_chops"] = str(max(max_chops, int(cfg["min_chops"])))
                write_json_file("/sd/cfg.json", cfg)
                spk_str(cfg["max_chops"], False)
                return Response(request, cfg["max_chops"])

            @server.route("/get-max-chops", [POST])
            def buttonpress(request: Request):
                print(cfg["max_chops"])
                return Response(request, cfg["max_chops"])
            break

    except Exception as e:
        web = False
        print(e)


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
        await an(command)
        await asyncio.sleep(0)  # Yield control to the event loop


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stp_all_cmds():
    global exit_set_hdw_async
    clr_cmd_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")

################################################################################
# Global Methods


def reset_to_defaults():
    global cfg
    cfg["tree_up_pos"] = 165
    cfg["tree_down_pos"] = 100
    cfg["feller_rest_pos"] = 0
    cfg["feller_chop_pos"] = 150
    cfg["opening_dialog"] = False
    cfg["feller_advice"] = False
    cfg["HOST_NAME"] = "animator-feller"
    cfg["volume_pot"] = True
    cfg["min_chops"] = "2"
    cfg["max_chops"] = "7"
    cfg["volume"] = "20"
    cfg["can_cancel"] = True
    cfg["option_selected"] = "birds_dogs_short_version"
    cfg["museum_mode"] = False


def ch_vol(action):
    volume = int(cfg["volume"])
    if "volume" in action:
        vol = action.split("volume")
        volume = int(vol[1])
    if action == "lower1":
        volume -= 1
    elif action == "raise1":
        volume += 1
    elif action == "lower":
        if volume <= 10:
            volume -= 1
        else:
            volume -= 10
    elif action == "raise":
        if volume < 10:
            volume += 1
        else:
            volume += 10
    if volume > 100:
        volume = 100
    if volume < 1:
        volume = 1
    cfg["volume"] = str(volume)
    cfg["volume_pot"] = False
    if not mix.voice[0].playing:
        write_json_file("/sd/cfg.json", cfg)
        ply_a_0("/sd/mvc/volume.wav")
        spk_str(cfg["volume"], False)


def upd_vol(s):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        time.sleep(s)
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except Exception as e:
            print(e)
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
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
            print(e)
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        await asyncio.sleep(s)


gc_col("global variable and methods")

################################################################################
# Dialog and sound play methods


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.02)
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        exit_early()


def stop_audio_0():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass


def exit_early():
    upd_vol(0.02)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def animation_stop():
    global button_press_start, exit_set_hdw_async
    if exit_set_hdw_async:
        return True
    if cfg["museum_mode"] or cfg["cont_mode"]:
        if not l_sw_io.value:
            if button_press_start is None:
                button_press_start = time.monotonic()
            elif time.monotonic() - button_press_start > 1:
                exit_set_hdw_async = True
        else:
            button_press_start = None
    elif not l_sw_io.value:
        exit_set_hdw_async = True
    return exit_set_hdw_async


def l_r_but():
    ply_a_0("/sd/mvc/press_left_button_right_button.wav")


def snd_choosen():
    ply_a_0("/sd/mvc/option_selected.wav")

def option_set():
    ply_a_0("/sd/mvc/option_selected.wav")
    set_options_menu()


def f_cal():
    ply_a_0("/sd/mvc/now_we_can_adjust_the_feller_position.wav")
    ply_a_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")

def t_cal():
    ply_a_0("/sd/mvc/now_we_can_adjust_the_tree_position.wav")
    ply_a_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")

def set_options_menu():
    ply_a_0("/sd/mvc/set_options_menu.wav")
    l_r_but()

def chk_lmt(min_servo_pos, max_servo_pos, servo_pos):
    if servo_pos < min_servo_pos:
        ply_a_0("/sd/mvc/limit_reached.wav")
        return False
    if servo_pos > max_servo_pos:
        ply_a_0("/sd/mvc/limit_reached.wav")
        return False
    return True

def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            ply_a_0("/sd/mvc/" + character + ".wav")
        except:
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")


gc_col("dialog methods")

#############################################################################################
# Servo helpers


def cal_l_but(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global cfg
    cfg[movement_type] -= 1 * sign
    if chk_lmt(min_servo_pos, max_servo_pos, cfg[movement_type]):
        servo.angle = cfg[movement_type]
    else:
        cfg[movement_type] += 1 * sign


def cal_r_but(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global cfg
    cfg[movement_type] += 1 * sign
    if chk_lmt(min_servo_pos, max_servo_pos, cfg[movement_type]):
        servo.angle = cfg[movement_type]
    else:
        cfg[movement_type] -= 1 * sign


def wrt_cal():
    ply_a_0("/sd/mvc/all_changes_complete.wav")
    global cfg
    write_json_file("/sd/cfg.json", cfg)


def m_f_spd(n_pos, spd):
    global f_lst_p
    sign = 1
    if f_lst_p > n_pos:
        sign = - 1
    for feller_angle in range(f_lst_p, n_pos, sign):
        mov_f(feller_angle)
        upd_vol(spd)
    mov_f(n_pos)


def m_t_spd(n_pos, spd):
    global t_lst_p
    sign = 1
    if t_lst_p > n_pos:
        sign = - 1
    for tree_angle in range(t_lst_p, n_pos, sign):
        mov_t(tree_angle)
        upd_vol(spd)
    mov_t(n_pos)


def mov_f(n_pos):
    if n_pos < f_min:
        n_pos = f_min
    if n_pos > f_max:
        n_pos = f_max
    f_s.angle = n_pos
    global f_lst_p
    f_lst_p = n_pos


def mov_t(n_pos):
    if n_pos < t_min:
        n_pos = t_min
    if n_pos > t_max:
        n_pos = t_max
    t_s.angle = n_pos
    global t_lst_p
    t_lst_p = n_pos


gc_col("servo helpers")

################################################################################
# animate feller


def f_tlk_mov():
    spk_rot = 7
    spk_cad = 0.2
    while mix.voice[0].playing:
        if animation_stop():
            mix.voice[0].stop()
            return
        f_s.angle = spk_rot + cfg["feller_rest_pos"]
        upd_vol(spk_cad)
        f_s.angle = cfg["feller_rest_pos"]
        upd_vol(spk_cad)


def t_tlk_mov():
    spk_rot = 2
    spk_cad = 0.2
    while mix.voice[0].playing:
        if animation_stop():
            mix.voice[0].stop()
            return
        t_s.angle = cfg["tree_up_pos"]
        upd_vol(spk_cad)
        t_s.angle = cfg["tree_up_pos"] - spk_rot
        upd_vol(spk_cad)


def ply_snd(folder):
    path = "/sd/" + folder
    sounds = [f for f in os.listdir(path) if not f.startswith(".")]
    file_name = random.choice(sounds)
    sounds = None
    print(folder + ": " + file_name)
    w0 = audiocore.WaveFile(open(path + "/" + file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        upd_vol(0.1)
        if animation_stop():
            mix.voice[0].stop()
            break
    w0.deinit()
    gc_col("deinit w0")


async def an(command):
    global an_running
    an_running = True
    cfg["option_selected"] = command
    write_json_file("/sd/cfg.json", cfg)
    await upd_vol_async(0.05)
    w0 = None
    w1 = None
    try:
        if cfg["opening_dialog"]:
            s_i = random.randint(0, 3)
            if s_i == 0:
                ply_snd("feller_wife")
            elif s_i == 1:
                ply_snd("feller_buddy")
            elif s_i == 2:
                ply_snd("feller_poem")
            else:
                ply_snd("feller_girlfriend")
            if animation_stop():
                return

        chop_i = 1
        chop_n = random.randint(int(cfg["min_chops"]), int(cfg["max_chops"]))
        when_spk = random.randint(1, chop_n)
        print("Chop total:", chop_n, "when to speak:", when_spk)
        spoken = False
        t_chop_p = cfg["tree_up_pos"] - 3
        cur_opt = cfg["option_selected"]

        if cur_opt == "random":
            s_n = random.randint(0, len(snd_opts) - 2)
            cur_opt = snd_opts[s_n]
            print("Random sound file:", cur_opt)

        # Open the final sound before chopping.
        if cur_opt == "happy_birthday":
            s_n = random.randint(0, 6)
            w1 = audiocore.WaveFile(open("/sd/feller_sounds/sounds_" + cur_opt + str(s_n) + ".wav", "rb"))
        else:
            w1 = audiocore.WaveFile(open("/sd/feller_sounds/sounds_" + cur_opt + ".wav", "rb"))

        while chop_i <= chop_n:
            await upd_vol_async(0)
            if animation_stop():
                return

            if when_spk == chop_i and not spoken and cfg["feller_advice"]:
                spoken = True
                sounds = [f for f in os.listdir("/sd/feller_dialog") if not f.startswith(".")]
                snd_f = "/sd/feller_dialog/" + random.choice(sounds)
                sounds = None
                print("Feller dialog:", snd_f)
                w0 = audiocore.WaveFile(open(snd_f, "rb"))
                mix.voice[0].play(w0, loop=False)
                f_tlk_mov()
                w0.deinit()
                w0 = None
                gc_col("deinit w0")
                if animation_stop():
                    return

            chop_s = random.randint(1, 7)
            print("Chop track:", chop_s)
            w0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chop_s) + ".wav", "rb"))
            chop_i += 1

            for f_pos in range(cfg["feller_rest_pos"], cfg["feller_chop_pos"] + 5, 10):
                if animation_stop():
                    mix.voice[0].stop()
                    break
                mov_f(f_pos)
                if f_pos >= cfg["feller_chop_pos"] - 10:
                    mix.voice[0].play(w0, loop=False)
                    upd_vol(0.2)
                    for _ in range(2):
                        mov_t(t_chop_p)
                        upd_vol(0.1)
                        mov_t(cfg["tree_up_pos"])
                        upd_vol(0.1)
                    break

            if animation_stop():
                return

            if chop_i <= chop_n:
                for f_pos in range(cfg["feller_chop_pos"], cfg["feller_rest_pos"], -5):
                    if animation_stop():
                        break
                    mov_f(f_pos)
                    upd_vol(0.02)

            if animation_stop():
                return

            while mix.voice[0].playing:
                await upd_vol_async(0.01)
                if animation_stop():
                    mix.voice[0].stop()
                    return

            w0.deinit()
            w0 = None

        # Chopping completed, so now play the already-open final sound.
        mix.voice[0].play(w1, loop=False)

        for t_pos in range(cfg["tree_up_pos"], cfg["tree_down_pos"], -5):
            mov_t(t_pos)
            upd_vol(0.06)

        for _ in range(8):
            mov_t(cfg["tree_down_pos"])
            upd_vol(0.1)
            mov_t(7 + cfg["tree_down_pos"])
            upd_vol(0.1)

        if cur_opt == "alien":
            print("Alien sequence starting....")
            upd_vol(2)
            m_f_spd(cfg["feller_rest_pos"], 0.01)
            m_t_spd(cfg["tree_up_pos"], 0.01)
            l_pos = cfg["tree_up_pos"]
            r_pos = cfg["tree_up_pos"] - 8

            while mix.voice[0].playing:
                await upd_vol_async(0)
                if animation_stop():
                    mix.voice[0].stop()
                    return
                m_t_spd(l_pos, 0.1)
                m_t_spd(r_pos, 0.1)

            w1.deinit()
            w1 = None
            m_t_spd(cfg["tree_up_pos"], 0.04)

            for alien_n in range(7):
                if animation_stop():
                    return

                snd_f = "/sd/feller_alien/human_" + str(alien_n + 1) + ".wav"
                w0 = audiocore.WaveFile(open(snd_f, "rb"))
                mix.voice[0].play(w0, loop=False)
                f_tlk_mov()
                w0.deinit()
                w0 = None

                if animation_stop():
                    return

                snd_f = "/sd/feller_alien/alien_" + str(alien_n + 1) + ".wav"
                w0 = audiocore.WaveFile(open(snd_f, "rb"))
                mix.voice[0].play(w0, loop=False)
                t_tlk_mov()
                w0.deinit()
                w0 = None

                if animation_stop():
                    return
        else:
            while mix.voice[0].playing:
                await upd_vol_async(0)
                if animation_stop():
                    mix.voice[0].stop()
                    return

            w1.deinit()
            w1 = None

    finally:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            await asyncio.sleep(0)
        if w0 is not None:
            w0.deinit()
            w0 = None
        if w1 is not None:
            w1.deinit()
            w1 = None
        gc_col("deinit audio")
        m_f_spd(cfg["feller_rest_pos"], 0.01)
        m_t_spd(cfg["tree_up_pos"], 0.01)
        await upd_vol_async(0.2)
        f_s.fraction = None
        t_s.fraction = None
        an_running = False

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
        m_f_spd(cfg["feller_rest_pos"], 0.01)
        m_t_spd(cfg["tree_up_pos"], 0.01)
        time.sleep(0.2)
        f_s.fraction = None
        t_s.fraction = None
        ply_a_0("/sd/mvc/animations_are_now_active.wav")
        print("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global an_just_added
        sw = switch_state(l_sw, r_sw, time.sleep, 1.0, ovrde_sw_st, t_sw)
        if sw == "left_held" and not cfg["museum_mode"]:
            if cfg["cont_mode"]:
                cfg["cont_mode"] = False
                write_json_file("/sd/cfg.json", cfg)
                clr_cmd_queue()
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cfg["cont_mode"] = True
                write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
            return
        if an_running:
            return
        if cfg["museum_mode"]:
            if sw == "left":
                add_cmd(cfg["option_selected"])
                an_just_added = True
            elif sw == "right":
                mch.go_to('main_menu')
            return
        if sw == "left" or cfg["cont_mode"]:
            add_cmd(cfg["option_selected"])
            an_just_added = True
        elif sw == "trigger":
            add_cmd(cfg["option_selected"])
            an_just_added = True
        elif sw == "right":
            mch.go_to('main_menu')

class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        print('Main menu')
        ply_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/sd/mvc/" + main_m[self.i] + ".wav")
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
            elif sel_mnu == "adjust_feller_and_tree":
                mch.go_to('adjust_feller_and_tree')
            elif sel_mnu == "move_feller_and_tree":
                mch.go_to('move_feller_and_tree')
            elif sel_mnu == "set_options":
                mch.go_to('set_options')
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Snds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, mch):
        print('Choose sounds menu')
        ply_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                ply_a_0("/sd/mvc/option_" +
                        snd_opts[self.i] + ".wav")
                self.sel_i = self.i
                self.i += 1
                if self.i > len(snd_opts)-1:
                    self.i = 0
        if sw == "right":
            cfg["option_selected"] = snd_opts[self.sel_i]
            print("Selected index: " + str(self.sel_i) +
                           " Saved option: " + cfg["option_selected"])
            write_json_file("/sd/cfg.json", cfg)
            snd_choosen()
            mch.go_to('base_state')


class MovFellTree(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'move_feller_and_tree'

    def enter(self, mch):
        print('Move feller and tree menu')
        ply_a_0("/sd/mvc/move_feller_and_tree_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/sd/mvc/" + mov_f_t[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(mov_f_t)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = mov_f_t[self.sel_i]
            if sel_mnu == "move_feller_to_rest_position":
                m_f_spd(cfg["feller_rest_pos"], 0.01)
            elif sel_mnu == "move_feller_to_chop_position":
                m_f_spd(cfg["feller_chop_pos"], 0.01)
            elif sel_mnu == "move_tree_to_upright_position":
                m_t_spd(cfg["tree_up_pos"], 0.01)
            elif sel_mnu == "move_tree_to_fallen_position":
                m_t_spd(cfg["tree_down_pos"], 0.01)
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class AdjFellTree(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0
        self.cal_active = False
        self.mov_type = ""
        self.servo = {}

    @property
    def name(self):
        return 'adjust_feller_and_tree'

    def enter(self, mch):
        print('Adjust feller and tree menu')
        ply_a_0("/sd/mvc/adjust_feller_and_tree_menu.wav")
        l_r_but()
        self.cal_active = False
        self.mov_type = ""
        self.servo = {}
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global f_lst_p, t_lst_p
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and not self.cal_active:
            ply_a_0("/sd/mvc/" +
                    adj_f_t[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(adj_f_t)-1:
                self.i = 0
        elif sw == "right" and not self.cal_active:
            selected_menu_item = adj_f_t[self.sel_i]
            if selected_menu_item == "move_feller_to_rest_position":
                m_f_spd(cfg["feller_rest_pos"], 0.01)
                f_cal()
                self.servo = f_s
                self.mov_type = "feller_rest_pos"
                self.cal_active = True
            elif selected_menu_item == "move_feller_to_chop_position":
                m_f_spd(cfg["feller_chop_pos"], 0.01)
                f_cal()
                self.servo = f_s
                self.mov_type = "feller_chop_pos"
                self.cal_active = True
            elif selected_menu_item == "move_tree_to_upright_position":
                m_t_spd(cfg["tree_up_pos"], 0.01)
                t_cal()
                self.servo = t_s
                self.mov_type = "tree_up_pos"
                self.cal_active = True
            elif selected_menu_item == "move_tree_to_fallen_position":
                m_t_spd(cfg["tree_down_pos"], 0.01)
                t_cal()
                self.servo = t_s
                self.mov_type = "tree_down_pos"
                self.cal_active = True
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
        elif self.cal_active:
            if self.mov_type == "feller_rest_pos" or self.mov_type == "feller_chop_pos":
                min_pos = f_min
                max_pos = f_max
                sign = 1
            else:
                min_pos = t_min
                max_pos = t_max
                sign = -1
            self.servo.angle = cfg[self.mov_type]
            if sw == "left":
                cal_l_but(
                    self.servo, self.mov_type, sign, min_pos, max_pos)
            if sw == "right":
                cal_r_but(
                    self.servo, self.mov_type, sign, min_pos, max_pos)
            if self.mov_type == "feller_rest_pos" or self.mov_type == "feller_chop_pos":
                f_lst_p = cfg[self.mov_type]
            else:
                t_lst_p = cfg[self.mov_type]
            if sw == "right_held":
                wrt_cal()
                mch.go_to('base_state')


class SetOpt(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'set_options'

    def enter(self, mch):
        print('Set Options')
        set_options_menu()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/sd/mvc/" +
                    dlg_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(dlg_m)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = dlg_m[self.sel_i]
            if sel_mnu == "opening_dialog_on":
                cfg["opening_dialog"] = True
                option_set()
            elif sel_mnu == "opening_dialog_off":
                cfg["opening_dialog"] = False
                option_set()
            elif sel_mnu == "lumberjack_advice_on":
                cfg["feller_advice"] = True
                option_set()
            elif sel_mnu == "lumberjack_advice_off":
                cfg["feller_advice"] = False
                option_set()
            elif sel_mnu == "museum_mode_on":
                cfg["museum_mode"] = True
                option_set()
            elif sel_mnu == "museum_mode_off":
                cfg["serve_webpage"] = False
                option_set()
            elif sel_mnu == "web_on":
                cfg["serve_webpage"] = True
                option_set()
            elif sel_mnu == "web_off":
                cfg["serve_webpage"] = False
                option_set()
            elif sel_mnu == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                set_options_menu()
            elif sel_mnu == "hear_instr_web":
                ply_a_0("/sd/mvc/web_instruct.wav")
                set_options_menu()
            else:
                write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
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
        print('Set Web Options')
        ply_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and not s.vol_adj_mode:
            ply_a_0("/sd/mvc/" + vol_set[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(vol_set)-1:
                s.i = 0
        if vol_set[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw == "right":
                s.vol_adj_mode = True
                ply_a_0("/sd/mvc/volume_adjustment_menu.wav")
        elif sw == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw == "right_held" and s.vol_adj_mode:
            write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1)
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            mch.go_to('base_state')
        if sw == "right" and vol_set[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            mch.go_to('base_state')

gc_col("state mch")

###############################################################################
# Create the state machine

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())
st_mch.add(AdjFellTree())
st_mch.add(MovFellTree())
st_mch.add(SetOpt())
st_mch.add(VolSet())

aud_en.value = True


def speak_webpage():
    ply_a_0("/sd/mvc/animator_available_on_network.wav")
    ply_a_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-feller":
        ply_a_0("/sd/mvc/animator_feller_local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/sd/mvc/in_your_browser.wav")


if (web):
    print("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        print("Listening on http://%s:80" % wifi.radio.ipv4_address)
        speak_webpage()
    except OSError:
        time.sleep(5)
        print("restarting...")
        rst()

st_mch.go_to('base_state')
print("animator has started...")
gc_col("animations started.")

# Main task handling


async def process_cmd_tsk():
    """Task to continuously process commands."""
    while True:
        try:
            await process_cmd()  # Async command processing
        except Exception as e:
            print(e)
        await asyncio.sleep(0)  # Yield control to other tasks


async def server_poll_tsk(server):
    """Poll the web server."""
    while True:
        try:
            server.poll()  # Web server polling
        except Exception as e:
            print(e)
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

