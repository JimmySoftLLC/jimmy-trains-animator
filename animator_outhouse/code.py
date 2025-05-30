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


import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import digitalio
import board
import microcontroller
import pwmio
from analogio import AnalogIn
from adafruit_debouncer import Debouncer
from adafruit_motor import servo
import utilities
import neopixel
import random
import gc
import files
import rtc
import asyncio


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
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
aud_en.value = True

sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050,
                       channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

mix.voice[0].level = .2

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
                    open("/sd/mvc/micro_sd_card_success.wav", "rb"))
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

# Setup the servo
d_s = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
g_s = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
r_s = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)

d_s = servo.Servo(d_s, min_pulse=500, max_pulse=2500)
g_s = servo.Servo(g_s, min_pulse=500, max_pulse=2500)
r_s = servo.Servo(r_s, min_pulse=500, max_pulse=2500)

d_lst_p = 90
d_min = 0
d_max = 180

g_lst_p = 90
g_min = 0
g_max = 180

r_lst_p = 90
r_min = 0
r_max = 180

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

cfg = files.read_json_file("/sd/cfg.json")

cfg_dlg = files.read_json_file("/sd/mvc/dialog_menu.json")
dlg_opt = cfg_dlg["dialog_options"]

cfg_mov_r_d = files.read_json_file("/sd/mvc/move_roof_door.json")
mov_r_d = cfg_mov_r_d["move_roof_door"]

cfg_adj_r_d = files.read_json_file("/sd/mvc/adjust_roof_door.json")
adj_r_d = cfg_adj_r_d["adjust_roof_door"]

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfd_vol = files.read_json_file("/sd/mvc/volume_settings.json")
v_set = cfd_vol["volume_settings"]

cfg_inst_m = files.read_json_file("/sd/mvc/install_menu.json")
inst_m = cfg_inst_m["install_menu"]

cont_run = False
instal_fig = False
reset_roof = True

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

gc_col("config setup")

################################################################################
# Get sound files in folder


def get_snds(dir, p_type):
    snd_ret = []
    snds = files.return_directory("", dir, ".wav")
    for element in snds:
        parts = element.split('_')
        if parts[0] == p_type:
            snd_ret.append(element)
    return snd_ret

################################################################################
# Setup neo pixels


num_px = 6

# 15 on demo 17 tiny 10 on large
led_B = neopixel.NeoPixel(board.GP15, num_px)
led_F = neopixel.NeoPixel(board.GP16, 1)

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
        def base(req: HTTPRequest):
            stop_a_0()
            gc_col("Home page.")
            return FileResponse(req, "index.html", "/")

        @server.route("/mui.min.css")
        def base(req: HTTPRequest):
            stop_a_0()
            return FileResponse(req, "/sd/mui.min.css", "/")

        @server.route("/mui.min.js")
        def base(req: HTTPRequest):
            stop_a_0()
            return FileResponse(req, "/sd/mui.min.js", "/")

        def set_cfg(type, value):
            cfg[type] = value
            wrt_cal()

        @server.route("/animation", [POST])
        def buttonpress(req: Request):
            req_d = req.json()
            if "RUN" == req_d["an"]:
                add_cmd("RUN")
            elif "RUNG" == req_d["an"]:
                add_cmd("RUNG")
            elif "RUNPG" == req_d["an"]:
                add_cmd("RUNPG")
            elif "RUNC" == req_d["an"]:
                add_cmd("RUNC")
            elif "G" == req_d["an"]:
                set_cfg("rating", "g")
            elif "PG" == req_d["an"]:
                set_cfg("rating", "pg")
            elif "C" == req_d["an"]:
                set_cfg("rating", "c")
            elif "EXP0" == req_d["an"]:
                set_cfg("explosions_freq", 0)
            elif "EXP1" == req_d["an"]:
                set_cfg("explosions_freq", 1)
            elif "EXP2" == req_d["an"]:
                set_cfg("explosions_freq", 2)
            elif "EXP3" == req_d["an"]:
                set_cfg("explosions_freq", 3)
            return Response(req, "Success")

        @server.route("/utilities", [POST])
        def buttonpress(req: Request):
            global cfg
            stop_a_0()
            req_d = req.json()
            if "speaker_test" == req_d["an"]:
                ply_a_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" == req_d["an"]:
                cfg["volume_pot"] = False
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" == req_d["an"]:
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" == req_d["an"]:
                rst_def()
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to('base_state')
            return Response(req, "Dialog option cal saved.")

        @server.route("/update-host-name", [POST])
        def buttonpress(req: Request):
            global cfg
            stop_a_0()
            req_d = req.json()
            cfg["HOST_NAME"] = req_d["text"]
            files.write_json_file("/sd/cfg.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            spk_web()
            return Response(req, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def buttonpress(req: Request):
            return Response(req, cfg["HOST_NAME"])

        @server.route("/get-local-ip", [POST])
        def buttonpress(req: Request):
            stop_a_0()
            return Response(req, local_ip)

        @server.route("/update-volume", [POST])
        def buttonpress(req: Request):
            global cfg
            req_d = req.json()
            ch_vol(req_d["action"])
            return Response(req, cfg["volume"])

        @server.route("/get-volume", [POST])
        def buttonpress(req: Request):
            return Response(req, cfg["volume"])

        @server.route("/mode", [POST])
        def buttonpress(req: Request):
            global cfg, cont_run
            req_d = req.json()
            if req_d["an"] == "left":
                ovrde_sw_st["switch_value"] = "left"
            elif req_d["an"] == "right":
                ovrde_sw_st["switch_value"] = "right"
            elif req_d["an"] == "right_held":
                ovrde_sw_st["switch_value"] = "right_held"
            elif req_d["an"] == "three":
                ovrde_sw_st["switch_value"] = "three"
            elif req_d["an"] == "four":
                ovrde_sw_st["switch_value"] = "four"
            elif "cont_mode_on" == req_d["an"]:
                cont_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" == req_d["an"]:
                cont_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            return Response(req, "Mode set")

        @server.route("/roof", [POST])
        def buttonpress(req: Request):
            global cfg
            global mov_type
            req_d = req.json()
            if "roof_open_pos" == req_d["an"]:
                mov_type = "roof_open_position"
                mov_r_s(cfg[mov_type], 0.01)
                return Response(req, "Moved to roof open position.")
            elif "roof_closed_pos" == req_d["an"]:
                mov_type = "roof_closed_position"
                mov_r_s(cfg[mov_type], 0.01)
                return Response(req, "Moved to roof closed position.")
            elif "roof_open_more" == req_d["an"]:
                cal_l_but(
                    r_s, mov_type, -1, 0, 180)
                return Response(req, "Moved door open more.")
            elif "roof_close_more" == req_d["an"]:
                cal_r_but(
                    r_s, mov_type, -1, 0, 180)
                return Response(req, "Moved door close more.")
            elif "roof_cal_saved" == req_d["an"]:
                wrt_cal()
                st_mch.go_to('base_state')
                return Response(req, "cal saved.")

        @server.route("/door", [POST])
        def buttonpress(req: Request):
            global cfg
            global door_movement_type
            req_d = req.json()
            if "door_open_pos" == req_d["an"]:
                door_movement_type = "door_open_position"
                mov_d_s(cfg[door_movement_type], 0.01)
                return Response(req, "Moved to door open position.")
            elif "door_closed_pos" == req_d["an"]:
                door_movement_type = "door_closed_position"
                mov_d_s(cfg[door_movement_type], 0.01)
                return Response(req, "Moved to door closed position.")
            elif "door_open_more" == req_d["an"]:
                cal_l_but(
                    d_s, door_movement_type, 1, 0, 180)
                return Response(req, "Moved door open more.")
            elif "door_close_more" == req_d["an"]:
                cal_r_but(
                    d_s, door_movement_type, 1, 0, 180)
                return Response(req, "Moved door close more.")
            elif "door_cal_saved" == req_d["an"]:
                wrt_cal()
                st_mch.go_to('base_state')
                return Response(req, "Tree " + door_movement_type + " cal saved.")

        @server.route("/install-figure", [POST])
        def buttonpress(req: Request):
            global cfg, instal_fig
            req_d = req.json()
            ins_f(req_d["action"])
            return Response(req, cfg["figure"])

    except Exception as e:
        web = False
        files.log_item(e)

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
        if command == "RUNG":
            cfg["rating"] = "g"
        elif command == "RUNPG":
            cfg["rating"] = "pg"
        elif command == "RUNC":
            cfg["rating"] = "c"

        await an()
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
# Misc Methods


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-outhouse"
    cfg["volume"] = "20"
    cfg["roof_open_position"] = 100
    cfg["guy_up_position"] = 0
    cfg["door_open_position"] = 24
    cfg["guy_down_position"] = 180
    cfg["roof_closed_position"] = 31
    cfg["door_closed_position"] = 122
    cfg["figure"] = "man"
    cfg["explosions_freq"] = 2
    cfg["serve_webpage"] = True
    cfg["rating"] = "g"

################################################################################
# Dialog and sound play methods


def upd_vol(seconds):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        time.sleep(seconds)
    else:
        try:
            v = int(cfg["volume"]) / 100
        except Exception as e:
            files.log_item(e)
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        time.sleep(seconds)


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
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_0("/sd/mvc/volume.wav")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.02)
    print("playing" + file_name)
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        exit_early()
    print("done playing")


def sw_stp_m():
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def stop_a_0():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass


def exit_early():
    upd_vol(0.02)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()

async def exit_early_async():
    await upd_vol_async(0.02)
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
            ply_a_0("/sd/mvc/" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")


def l_r_but():
    ply_a_0("/sd/mvc/press_left_button_right_button.wav")


def opt_sel():
    ply_a_0("/sd/mvc/option_selected.wav")


def d_cal():
    ply_a_0("/sd/mvc/adjust_the_door_position_instruct.wav")
    ply_a_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")


def r_cal():
    ply_a_0("/sd/mvc/adjust_the_roof_position_instruct.wav")
    ply_a_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")


def sel_web():
    ply_a_0("/sd/mvc/web_menu.wav")
    l_r_but()


def spk_web():
    ply_a_0("/sd/mvc/animator_available_on_network.wav")
    ply_a_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-outhouse":
        ply_a_0("/sd/mvc/animator_dash_outhouse.wav")
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/sd/mvc/in_your_browser.wav")


def chk_lmt(min, max, pos):
    if pos < min:
        ply_a_0("/sd/mvc/limit_reached.wav")
        return False
    if pos > max:
        ply_a_0("/sd/mvc/limit_reached.wav")
        return False
    return True


def no_user_track():
    ply_a_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            ply_a_0("/sd/mvc/my_track_inst.wav")
            break

################################################################################
# Servo helpers

def mov_d_s(n_pos, speed):
    global d_lst_p
    sign = 1
    if d_lst_p > n_pos:
        sign = - 1
    for door_angle in range(d_lst_p, n_pos, sign):
        mov_d(door_angle)
        time.sleep(speed)
    mov_d(n_pos)


def mov_r_s(n_pos, spd):
    global r_lst_p
    sign = 1
    if r_lst_p > n_pos:
        sign = - 1
    for roof_angle in range(r_lst_p, n_pos, sign):
        mov_r(roof_angle)
        time.sleep(spd)
    mov_r(n_pos)

def mov_g_s(n_pos, speed, led):
    global g_lst_p
    tot_d = abs(g_lst_p - n_pos)
    sign = 1
    lst_i = -1
    if g_lst_p > n_pos:
        sign = - 1
    for guy_angle in range(g_lst_p, n_pos, sign):
        if led == True:
            i = int(abs(abs(n_pos-g_lst_p)/tot_d*5-5))
            if i != lst_i:
                led_B[i] = (0, 0, 255)
                led_B.show()
                lst_i = i
        mov_g(guy_angle)
        time.sleep(speed)
    mov_g(n_pos)


def mov_d(pos):
    if pos < d_min:
        pos = d_min
    if pos > d_max:
        pos = d_max
    d_s.angle = pos
    global d_lst_p
    d_lst_p = pos


def mov_g(pos):
    if pos < g_min:
        pos = g_min
    if pos > g_max:
        pos = g_max
    g_s.angle = pos
    global g_lst_p
    g_lst_p = pos


def mov_r(pos):
    if pos < r_min:
        pos = r_min
    if pos > r_max:
        pos = r_max
    r_s.angle = pos
    global r_lst_p
    r_lst_p = pos


def cal_l_but(s, mov_typ, sign, min, max):
    global cfg
    cfg[mov_typ] -= 1 * sign
    if chk_lmt(min, max, cfg[mov_typ]):
        s.angle = cfg[mov_typ]
    else:
        cfg[mov_typ] += 1 * sign


def cal_r_but(s, mov_typ, sign, min, max):
    global cfg
    cfg[mov_typ] += 1 * sign
    if chk_lmt(min, max, cfg[mov_typ]):
        s.angle = cfg[mov_typ]
    else:
        cfg[mov_typ] -= 1 * sign


def wrt_cal():
    global cfg
    if not mix.voice[0].playing:
        ply_a_0("/sd/mvc/all_changes_complete.wav")
        files.write_json_file("/sd/cfg.json", cfg)


def cal_pos(s, mov_typ):
    if mov_typ == "door_closed_position" or mov_typ == "door_open_position":
        min = 0
        max = 180
        sign = 1
    else:
        min = 0
        max = 180
        sign = -1
    done = False
    while not done:
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            cal_l_but(s, mov_typ, sign, min, max)
        elif sw == "right":
            cal_r_but(s, mov_typ, sign, min, max)
        elif sw == "right_held":
            wrt_cal()
            done = True
    if mov_typ == "door_close_position" or mov_typ == "door_open_position":
        global d_lst_p
        d_lst_p = cfg[mov_typ]
    else:
        global r_lst_p
        r_lst_p = cfg[mov_typ]


################################################################################
# Animations


async def fr_asy(r_on, g_on, b_on, spd):
    led_B.brightness = 1.0

    r = random.randint(150, 255)
    g = random.randint(150, 255)
    b = random.randint(150, 255)

    # Flicker, based on our initial RGB values

    for i in range(0, num_px):
        flicker = random.randint(0, 175)
        r1 = bnds(r-flicker, g-flicker, b-flicker)
        g1 = bnds(r-flicker, g-flicker, b-flicker)
        b1 = bnds(r-flicker, g-flicker, b-flicker)
        led_B[i] = (r1 * r_on, g1 * g_on, b1 * b_on)
    led_B.show()
    exit_early()


async def alien_tlk():
    led_B.brightness = 1.0

    r = random.randint(0, 0)
    g = random.randint(150, 255)
    b = random.randint(0, 0)

    # Flicker, based on our initial RGB values
    while mix.voice[0].playing:
        for i in range(0, 3):
            flicker = random.randint(0, 175)
            r1 = bnds(r-flicker, 0, 255)
            g1 = bnds(g-flicker, 0, 255)
            b1 = bnds(b-flicker, 0, 255)
            led_B[i] = (r1, g1, b1)
            led_B.show()
            await upd_vol_async(random.uniform(0.05, 0.1))
        for i in range(0, 3):
            led_B[i] = (0, 0, 0)
        led_B.show()


async def cyc_g_asy(spd, pos_up, pos_down, r, g, b):
    global g_lst_p
    while mix.voice[0].playing:
        exit_early()
        n_pos = pos_up
        sign = 1
        if g_lst_p > n_pos:
            sign = - 1
        for ang in range(g_lst_p, n_pos, sign*3):
            mov_g(ang)
            await fr_asy(r, g, b, spd)
        n_pos = pos_down
        sign = 1
        if g_lst_p > n_pos:
            sign = - 1
        for ang in range(g_lst_p, n_pos, sign*3):
            mov_g(ang)
            await fr_asy(r, g, b, spd)


async def cyc_r_asy(spd, pos_up, pos_down, r, g, b):
    global r_lst_p
    while mix.voice[0].playing:
        exit_early()
        n_pos = pos_up
        sign = 1
        if r_lst_p > n_pos:
            sign = - 1
        for ang in range(r_lst_p, n_pos, sign):
            mov_r(ang)
            await fr_asy(r, g, b, spd)
        n_pos = pos_down
        sign = 1
        if r_lst_p > n_pos:
            sign = - 1
        for ang in range(r_lst_p, n_pos, sign):
            mov_r(ang)
            await fr_asy(r, g, b, spd)


async def cyc_d_asy(spd, pos_up, pos_down, r, g, b):
    global d_lst_p
    while mix.voice[0].playing:
        exit_early()
        n_pos = pos_up
        sign = 3
        if d_lst_p > n_pos:
            sign = - 3
        for ang in range(d_lst_p, n_pos, sign):
            mov_d(ang)
            await fr_asy(r, g, b, spd)
        n_pos = pos_down
        sign = 3
        if d_lst_p > n_pos:
            sign = - 3
        for ang in range(d_lst_p, n_pos, sign):
            mov_d(ang)
            await fr_asy(r, g, b, spd)


async def rn_exp(r, g, b):
    await cyc_g_asy(0.01, cfg["guy_up_position"]+20, cfg["guy_up_position"], r, g, b)
    while mix.voice[0].playing:
        exit_early()


async def rn_music(r, g, b):
    led_F[0] = (0, 0, 0)
    led_F.show()
    await cyc_d_asy(0.01, cfg["door_closed_position"]-20,
              cfg["door_closed_position"], r, g, b)
    while mix.voice[0].playing:
        exit_early()

async def ply_mtch(fn, srt, end, wait):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            await upd_vol_async(0.02)
    print("playing" + fn)
    w0 = audiocore.WaveFile(open(fn, "rb"))
    mix.voice[0].play(w0, loop=False)
    if srt > 0 and end > 0:
        await asyncio.sleep(srt)
        led_B[0] = ((255, 0, 0))
        led_B.show()
        await asyncio.sleep(end)
        led_B[0] = ((0, 0, 0))
        led_B.show()
    while mix.voice[0].playing and wait:
        exit_early()
    print("done playing")


async def d_snd(pos):
    await rnd_snd("/sd/sqk", "sqk", 0, 0, False)
    mov_d_s(pos, .03)
    while mix.voice[0].playing:
        pass


async def sit_d():
    print("sitting down")
    mov_g_s(cfg["guy_down_position"]-10, 0.05, False)
    led_F[0] = ((255, 147, 41))
    led_F.show()
    if cfg["figure"] == "alien":
        await d_snd(cfg["door_open_position"])
        await rnd_snd("/sd/" + cfg["rating"], "alienent", 0, 0, False)
        await alien_tlk()
        await rnd_snd("/sd/" + cfg["rating"], "alienseat", 0, 0, False)
        await alien_tlk()
        mov_g_s(cfg["guy_down_position"], 0.05, False)
        await d_snd(cfg["door_closed_position"])
        await rnd_snd("/sd/" + cfg["rating"], "alienstr", 0, 0, False)
        await alien_tlk()
    elif cfg["figure"] == "music":
        await d_snd(cfg["door_open_position"])
        mov_g_s(cfg["guy_down_position"], 0.05, False)
        await d_snd(cfg["door_closed_position"])
    else:
        await d_snd(cfg["door_open_position"])
        await mtch()


async def mtch():
    mov_g_s(cfg["guy_down_position"], 0.05, False)
    await d_snd(cfg["door_closed_position"])
    led_F[0] = ((0, 0, 0))
    await rnd_snd("/sd/" + cfg["rating"], cfg["figure"], 0, 0, True)
    await rnd_snd("/sd/match", "fail", .1, .1, True)
    await rnd_snd("/sd/match", "fail", .1, .1, True)
    await rnd_snd("/sd/match", "fail", .1, .1, True)
    await rnd_snd("/sd/match", "lit", .4, .4, True)


async def rnd_snd(dir, p_typ, srt, end, wait):
    snds = get_snds(dir, p_typ)
    max_i = len(snds) - 1
    i = random.randint(0, max_i)
    await ply_mtch(dir + "/" + snds[i] + ".wav", srt, end, wait)


async def exp():
    global reset_roof
    print("explosion")
    await rnd_snd("/sd/" + cfg["rating"] + "_exp", cfg["figure"], 0, 0, False)
    await asyncio.sleep(.1)
    led_F[0] = (80, 80, 80)
    if cfg["figure"] != "music":
        mov_r(cfg["roof_open_position"])
    if cfg["figure"] == "alien":
        led_F[0] = (0, 255, 0)
    led_F.show()
    if cfg["figure"] == "alien":
        mov_g_s(cfg["guy_up_position"], .05, True)
        await rn_exp(0, 0, 1)
    elif cfg["figure"] == "music":
        reset_roof = False
        await rn_music(0, 1, 1)
    else:
        mov_g(cfg["guy_up_position"])
        mov_d(cfg["door_open_position"])
        for i in range(0, 6):
            led_B[i] = (255, 0, 0)
            led_B.show()
            await asyncio.sleep(.05)
        await rn_exp(1, 0, 0)


async def no_exp():
    global reset_roof
    reset_roof = False
    print("no explosion")
    await asyncio.sleep(.1)
    led_F[0] = ((255, 147, 41))
    led_F.show()
    if cfg["figure"] == "music":
        await rnd_snd("/sd/" + cfg["rating"] + "_noexp", cfg["figure"], 0, 0, False)
        await rn_music(0, 1, 1)
    elif cfg["figure"] == "alien":
        await d_snd(cfg["door_open_position"])
        mov_g_s(cfg["guy_down_position"]-20, 0.001, False)
        await rnd_snd("/sd/" + cfg["rating"] + "_noexp", cfg["figure"], 0, 0, False)
        await alien_tlk()
        led_F[0] = ((0, 0, 0))
        led_F.show()
        await d_snd(cfg["door_closed_position"])
    else:
        await d_snd(cfg["door_open_position"])
        mov_g_s(cfg["guy_down_position"]-20, 0.001, False)
        await rnd_snd("/sd/" + cfg["rating"] + "_noexp", cfg["figure"], 0, 0, True)
        led_F[0] = ((0, 0, 0))
        led_F.show()
        await d_snd(cfg["door_closed_position"])


async def rst_an(rest_roof):
    print("reset")
    led_F.fill((0, 0, 0))
    led_F.show()
    led_B.fill((0, 0, 0))
    led_B.show()
    mov_d(cfg["door_closed_position"])
    mov_g_s(cfg["guy_down_position"]-10, 0.001, False)
    await asyncio.sleep(.2)
    if rest_roof:
        mov_r_s(cfg["roof_closed_position"]+20, .001)
        mov_r_s(cfg["roof_closed_position"], .05)


async def an():
    global reset_roof
    reset_roof = True

    await sit_d()
    run_exp = rnd_prob(cfg["explosions_freq"])
    if cfg["figure"] == "alien":
        run_exp = True
    if run_exp:
        await exp()
    else:
        await no_exp()
    await rst_an(reset_roof)

################################################################################
# animation helpers

def rnd_prob(v):
    print(v)
    if v == 0:
        return False
    elif v == 1:
        y = random.random()
        if y < 0.33:
            return True
    elif v == 2:
        y = random.random()
        if y < 0.66:
            return True
    elif v == 3:
        return True
    return False

def bnds(my_color, lower, upper):
    if (my_color < lower):
        my_color = lower
    if (my_color > upper):
        my_color = upper
    return my_color


def ins_f(fig_type):
    global instal_fig
    mov_r_s(cfg["roof_open_position"], 0.01)
    mov_d_s(cfg["door_open_position"], 0.01)
    mov_g_s(0, 0.01, False)
    ply_a_0("/sd/mvc/install_figure_instructions.wav")
    cfg["figure"] = fig_type
    instal_fig = True

################################################################################
# State Machine


class StMch(object):

    def __init__(s):
        s.ste = None
        s.stes = {}
        s.paused_state = None

    def add(s, ste):
        s.stes[ste.name] = ste

    def go_to(s, ste):
        if s.ste:
            s.ste.exit(s)
        s.ste = s.stes[ste]
        s.ste.enter(s)

    def upd(s):
        if s.ste:
            s.ste.upd(s)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(s):
        pass

    @property
    def name(s):
        return ''

    def enter(s, mch):
        pass

    def exit(s, mch):
        pass

    def upd(s, mch):
        pass


class BseSt(Ste):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, mch):
        if not instal_fig:
            # set servos to starting position
            mov_g_s(cfg["guy_down_position"], 0.01, False)
            mov_d_s(cfg["door_closed_position"], 0.01)
            mov_r_s(cfg["roof_closed_position"], 0.01)
            ply_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, instal_fig
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left_held" and not instal_fig:
            if cont_run:
                cont_run = False
                stp_all_cmds()
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif (sw == "left" or cont_run) and not instal_fig:
            add_cmd("RUN")
        elif sw == "right" and not instal_fig:
            mch.go_to('main_menu')
        elif sw == "right" and instal_fig:
            instal_fig = False
            mov_g_s(cfg["guy_down_position"], 0.01, False)
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            st_mch.go_to('base_state')


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        ply_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/sd/mvc/" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw == "right":
            sel_i = main_m[self.sel_i]
            if sel_i == "dialog_options":
                mch.go_to('dialog_options')
            elif sel_i == "adjust_roof_door":
                mch.go_to('adjust_roof_door')
            elif sel_i == "move_roof_door":
                mch.go_to('move_roof_door')
            elif sel_i == "set_dialog_options":
                mch.go_to('set_dialog_options')
            elif sel_i == "web_options":
                mch.go_to('web_options')
            elif sel_i == "volume_settings":
                mch.go_to('volume_settings')
            elif sel_i == "install_figure":
                mch.go_to('install_figure')
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class MoveRD(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0

    @property
    def name(self):
        return 'move_roof_door'

    def enter(s, mch):
        files.log_item('Move roof or door menu')
        ply_a_0("/sd/mvc/move_roof_or_door_menu.wav")
        l_r_but()
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0("/sd/mvc/" + mov_r_d[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(mov_r_d)-1:
                s.i = 0
        if sw == "right":
            sel_i = mov_r_d[s.sel_i]
            if sel_i == "move_door_open_position":
                mov_d_s(cfg["door_open_position"], 0.01)
            elif sel_i == "move_door_closed_position":
                mov_d_s(cfg["door_closed_position"], 0.01)
            elif sel_i == "move_roof_open_position":
                mov_r_s(cfg["roof_open_position"], 0.01)
            elif sel_i == "move_roof_closed_position":
                mov_r_s(cfg["roof_closed_position"], 0.01)
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class AdjRD(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0

    @property
    def name(s):
        return 'adjust_roof_door'

    def enter(s, mch):
        files.log_item('Adjust roof or door menu')
        ply_a_0("/sd/mvc/adjust_roof_or_door_menu.wav")
        l_r_but()
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(
                "/sd/mvc/" + adj_r_d[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(adj_r_d)-1:
                s.i = 0
        if sw == "right":
            sel_i = adj_r_d[s.sel_i]
            if sel_i == "adjust_door_open_position":
                mov_d_s(cfg["door_open_position"], 0.01)
                d_cal()
                cal_pos(d_s, "door_open_position")
                mch.go_to('base_state')
            elif sel_i == "adjust_door_closed_position":
                mov_d_s(cfg["door_closed_position"], 0.01)
                d_cal()
                cal_pos(d_s, "door_closed_position")
                mch.go_to('base_state')
            elif sel_i == "adjust_roof_open_position":
                mov_r_s(cfg["roof_open_position"], 0.01)
                r_cal()
                cal_pos(r_s, "roof_open_position")
                mch.go_to('base_state')
            elif sel_i == "adjust_roof_closed_position":
                mov_r_s(cfg["roof_closed_position"], 0.01)
                r_cal()
                cal_pos(r_s, "roof_closed_position")
                mch.go_to('base_state')
            else:
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
        files.log_item('Set Web Options')
        ply_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" and not s.vol_adj_mode:
            ply_a_0("/sd/mvc/" + v_set[s.i] + ".wav")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(v_set)-1:
                s.i = 0
        if v_set[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw == "right":
                s.vol_adj_mode = True
                ply_a_0("/sd/mvc/volume_adjustment_menu.wav")
        elif sw == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw == "right_held" and s.vol_adj_mode:
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1)
        if sw == "right" and v_set[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            mch.go_to('base_state')
        if sw == "right" and v_set[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            files.write_json_file("/sd/cfg.json", cfg)
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            mch.go_to('base_state')


class WebOpt(Ste):
    global cfg

    def __init__(s):
        s.i = 0
        s.sel_i = 0

    @property
    def name(s):
        return 'web_options'

    def enter(s, mch):
        files.log_item('Set Web Options')
        sel_web()
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                ply_a_0("/sd/mvc/" + web_m[s.i] + ".wav")
                s.sel_i = s.i
                s.i += 1
                if s.i > len(web_m)-1:
                    s.i = 0
        if sw == "right":
            sel_i = web_m[s.sel_i]
            if sel_i == "web_on":
                cfg["serve_webpage"] = True
                opt_sel()
                sel_web()
            elif sel_i == "web_off":
                cfg["serve_webpage"] = False
                opt_sel()
                sel_web()
            elif sel_i == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            elif sel_i == "hear_instr_web":
                ply_a_0("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Dlg_Opt(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0

    @property
    def name(s):
        return 'dialog_options'

    def enter(s, mch):
        files.log_item('Choose sounds menu')
        ply_a_0("/sd/mvc/dialog_options_menu.wav")
        l_r_but()
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                ply_a_0("/sd/mvc/" +
                        dlg_opt[s.i] + ".wav")
                s.sel_i = s.i
                s.i += 1
                if s.i > len(dlg_opt)-1:
                    s.i = 0
        if sw == "right":
            opts = dlg_opt[s.sel_i].split(" ")
            if opts[0] == "exit_this_menu":
                print("choose exit this menu")
            elif opts[0] == "exp":
                cfg["explosions_freq"] = int(opts[1])
            else:
                cfg["rating"] = opts[1]
            files.log_item(
                "Exp freq: " + str(cfg["explosions_freq"]) + " Rating: " + cfg["rating"])
            files.write_json_file("/sd/cfg.json", cfg)
            opt_sel()
            mch.go_to('base_state')


class InsFig(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0

    @property
    def name(self):
        return 'install_figure'

    def enter(self, mch):
        files.log_item('Choose sounds menu')
        ply_a_0("/sd/mvc/install_figure_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(
                "/sd/mvc/" + inst_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(inst_m)-1:
                self.i = 0
        if sw == "right":
            ins_f(inst_m[self.sel_i])
            mch.go_to('base_state')


gc_col("Ste mch")

###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Dlg_Opt())
st_mch.add(AdjRD())
st_mch.add(MoveRD())
st_mch.add(WebOpt())
st_mch.add(VolSet())
st_mch.add(InsFig())

upd_vol(.1)
aud_en.value = True

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        spk_web()
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")

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
