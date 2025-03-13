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

from rainbowio import colorwheel
import neopixel
import asyncio
import microcontroller
import random
import board
import time
import gc
import files
import os
import gc
from analogio import AnalogIn
import audiomp3
import audiomixer
import audiobusio
import digitalio
from adafruit_debouncer import Debouncer

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
# Sd card config variables

animators_folder = "/animations/"

cfg = files.read_json_file("cfg.json")

ts_jsons = files.return_directory(
    "", "t_s_def", ".json")

web = cfg["serve_webpage"]

exit_set_hdw_async = False

gc_col("config setup")

def upd_media():
    global animations

    animations = files.return_directory("", "animations", ".json")

upd_media()

################################################################################
# Setup hardware

# Setup pin for v
a_in = AnalogIn(board.A0)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

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
    voice_count=1,
    sample_rate=22050,
    channel_count=2,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=16384,
)
aud.play(mix)

mix.voice[0].level = .2

aud_en.value = False


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

#15 on demo 17 tiny 10 on large, GP11 on clhv-6, GP15 on clhv-6 and clmhv-6
neo_pixel_pin = board.GP15

led = neopixel.NeoPixel(neo_pixel_pin, n_px)

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
    time.sleep(.05)
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
    led.deinit()
    led = neopixel.NeoPixel(neo_pixel_pin, n_px)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()


upd_l_str()

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

    local_ip = ""

    try:
        env = files.read_json_file("env.json")
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
        server.port = 80  # Explicitly set port to 80

        gc_col("wifi server")

        ################################################################################
        # Setup routes

        @server.route("/")
        def base(request: HTTPRequest):
            gc_col("Home page.")
            return FileResponse(request, "index.html", "/")

        @server.route("/mui.min.css")
        def base(request: HTTPRequest):
            return FileResponse(request, "mui.min.css", "/")

        @server.route("/mui.min.js")
        def base(request: HTTPRequest):
            return FileResponse(request, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["option_selected"] = rq_d["an"]
            add_command(cfg["option_selected"])
            files.write_json_file("cfg.json", cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for ts_fn in ts_jsons:
                    ts = files.read_json_file(
                        "t_s_def/" + ts_fn + ".json")
                    files.write_json_file(
                        "animations/"+ts_fn+".json", ts)
            elif rq_d["an"] == "reset_to_defaults":
                rst_def()
                files.write_json_file("cfg.json", cfg)
            return Response(request, "Utility: " + rq_d["an"])
        
        @server.route("/stop", [POST])
        def btn(request: Request):
            stop_all_commands()
            return Response(request, "Stopped all commands")

        @server.route("/lights", [POST])
        def btn(request: Request):
            global exit_set_hdw_async
            exit_set_hdw_async = False
            """Handle lights route synchronously but process async operation in background."""
            try:
                rq_d = request.json()  # Parse the incoming JSON
                asyncio.create_task(set_hdw_async(rq_d["an"],0))  # Schedule the async task
                return Response(request, "Utility: set lights successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error setting lights.")
            
        @server.route("/create-animation", [POST])
        def btn(request: Request):
            try:
                global data, animators_folder
                rq_d = request.json()  # Parse the incoming JSON
                print(rq_d)
                f_n = animators_folder + rq_d["fn"] + ".json"
                print(f_n)
                an_data = ["0.0|BN100,LN0_255_0_0", "1.0|BN100,LN0_0_255_0", "2.0|BN100,LN0_0_0_255", "3.0|BN100,LN0_255_255_255"]
                files.write_json_file(f_n, an_data)
                upd_media()
                return Response(request, "Created animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error creating animation.")
        
        @server.route("/rename-animation", [POST])
        def btn(request: Request):
            try:
                global data, animators_folder
                rq_d = request.json()  # Parse the incoming JSON
                fo = animators_folder + rq_d["fo"] + ".json"
                fn = animators_folder + rq_d["fn"] + ".json"
                os.rename(fo, fn)
                upd_media()
                return Response(request, "Renamed animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error setting lights.")
            
        @server.route("/delete-animation", [POST])
        def btn(request: Request):
            try:
                global data, animators_folder
                rq_d = request.json()  # Parse the incoming JSON
                print(rq_d)
                f_n = animators_folder + rq_d["fn"] + ".json"
                print(f_n)
                os.remove(f_n)
                upd_media()
                return Response(request, "Delete animation successfully.")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error setting lights.")
            
        @server.route("/update-light-string", [POST])
        def btn(req: Request):
            global cfg
            rq_d = req.json()
            if rq_d["action"] == "save" or rq_d["action"] == "clear" or rq_d["action"] == "defaults":
                cfg["light_string"] = rq_d["text"]
                print("action: " +
                      rq_d["action"] + " data: " + cfg["light_string"])
                files.write_json_file("cfg.json", cfg)
                upd_l_str()
                return Response(req, cfg["light_string"])
            if cfg["light_string"] == "":
                cfg["light_string"] = rq_d["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + \
                    "," + rq_d["text"]
            print("action: " + rq_d["action"] +
                  " data: " + cfg["light_string"])
            files.write_json_file("cfg.json", cfg)
            upd_l_str()
            return Response(req, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def btn(req: Request):
            return Response(req, cfg["light_string"])
        
        @server.route("/update-host-name", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["HOST_NAME"] = rq_d["an"]
            files.write_json_file("cfg.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def btn(request: Request):
            return Response(request, cfg["HOST_NAME"])
        
        @server.route("/get-local-ip", [POST])
        def btn(request: Request):
            return Response(request, local_ip)

        @server.route("/get-animations", [POST])
        def btn(request: Request):
            sounds = []
            sounds.extend(animations)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/test-animation", [POST])
        def btn(request: Request):
            global exit_set_hdw_async
            exit_set_hdw_async = False
            try:
                rq_d = request.json()
                print(rq_d["an"])
                gc_col("Save Data.")
                asyncio.create_task(set_hdw_async(rq_d["an"], 3))  # Schedule the async task
                return Response(request, "Test animation successfully")
            except Exception as e:
                files.log_item(e)  # Log any errors
                return Response(request, "Error test animation.")

        @server.route("/get-animation", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            snd_f = rq_d["an"]
            if (f_exists("animations/" + snd_f + ".json") == True):
                f_n = "animations/" + snd_f + ".json"
                return FileResponse(request, f_n, "/")
            else:
                f_n = "t_s_def/timestamp mode.json"
                return FileResponse(request, f_n, "/")

        data = []

        @server.route("/save-data", [POST])
        def btn(request: Request):
            global data
            rq_d = request.json()
            try:
                if rq_d[0] == 0:
                    data = []
                data.extend(rq_d[2])
                if rq_d[0] == rq_d[1]:
                    f_n = "animations/" + rq_d[3] + ".json"
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

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")

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
        except:
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
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
    files.write_json_file("cfg.json", cfg)
    ply_a_0("/mvc/volume.mp3")
    spk_str(cfg["volume"], False)


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.02)
    print("playing" + file_name)
    w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
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
        except:
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0("/mvc/dot.mp3")
        ply_a_0("/mvc/local.mp3")


def l_r_but():
    ply_a_0("/mvc/press_left_button_right_button.mp3")


def opt_sel():
    ply_a_0("/mvc/option_selected.mp3")


def d_cal():
    ply_a_0("/mvc/adjust_the_door_position_instruct.mp3")
    ply_a_0("/mvc/to_exit_press_and_hold_button_down.mp3")


def r_cal():
    ply_a_0("/mvc/adjust_the_roof_position_instruct.mp3")
    ply_a_0("/mvc/to_exit_press_and_hold_button_down.mp3")


def sel_web():
    ply_a_0("/mvc/web_menu.mp3")
    l_r_but()


def spk_web():
    ply_a_0("/mvc/animator_available_on_network.mp3")
    ply_a_0("/mvc/to_access_type.mp3")
    if cfg["HOST_NAME"] == "animator-outhouse":
        ply_a_0("/mvc/animator_dash_outhouse.mp3")
        ply_a_0("/mvc/dot.mp3")
        ply_a_0("/mvc/local.mp3")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/mvc/in_your_browser.mp3")


def chk_lmt(min, max, pos):
    if pos < min:
        ply_a_0("/mvc/limit_reached.mp3")
        return False
    if pos > max:
        ply_a_0("/mvc/limit_reached.mp3")
        return False
    return True


def no_user_track():
    ply_a_0("/mvc/no_user_soundtrack_found.mp3")


################################################################################
# Command queue
command_queue = []

def add_command(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    """Add a command to the queue. If to_start is True, add to the front."""
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        print("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        print("Command added to the end:", command)

async def process_commands():
    """Asynchronous function to process commands in a FIFO order."""
    while command_queue:
        command = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", command)
        await an_async(command)  # Process each command as an async operation
        await asyncio.sleep(0)  # Yield control to the event loop

def clear_command_queue():
    """Clear all commands from the queue."""
    command_queue.clear()
    print("Command queue cleared.")

def stop_all_commands():
    """Stop all commands and clear the queue."""
    global exit_set_hdw_async
    clear_command_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-clmhv6"
    cfg["option_selected"] = "random all"


################################################################################
# animations


async def an_async(f_nm):
    """Run animation lighting as an async task."""
    print("Filename:", f_nm)
    try:
        await an_light_async(f_nm)
        gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    """Asynchronous animation lighting."""

    flsh_t = []
    if f_exists("animations/" + f_nm + ".json"):
        flsh_t = files.read_json_file("animations/" + f_nm + ".json")

    # add end command to time stamps to stop video when timestamps run out
    ft_last = flsh_t[len(flsh_t)-1].split("|")
    tm_last = float(ft_last[0]) + .1
    flsh_t.append(str(tm_last) + "|E")
    flsh_t.append(str(tm_last + .1) + "|E")

    flsh_i = 0
    srt_t = time.monotonic()

    while True:
        t_past = time.monotonic() - srt_t
        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i + 1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0

        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            files.log_item(f"time elapsed: {t_past} Timestamp: {ft1[0]}")
            if len(ft1) == 1 or ft1[1] == "":
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                result = await set_hdw_async(f"L0{lgt},S0{pos}",dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            else:
                result = await set_hdw_async(ft1[1],dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            flsh_i += 1
            
        # print (flsh_i)

        await asyncio.sleep(0)  # Yield control to other tasks

        # Exit condition for stopping animation
        if flsh_i >= len(flsh_t)-1:
            # led.fill((0, 0, 0))
            # led.show()
            break

##############################
# animation effects

async def random_effect(il, ih, d):
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
            await asyncio.sleep(spd)
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
            await asyncio.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
            
async def fire(dur):
    global exit_set_hdw_async
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

    # Flicker, based on our initial RGB values
    while True:
        for i in firei:
            if exit_set_hdw_async:
                return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led[i] = (r1, g1, b1)
            led.show()
        await asyncio.sleep(random.uniform(0.05, 0.1))
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


sp = [0, 0, 0, 0, 0, 0]
br = 0

async def set_hdw_async(input_string, dur):
    """Async hardware control for NeoPixel lights."""
    global sp, br, exit_set_hdw_async
    segs = input_string.split(",")

    try:
        for seg in segs:
            if exit_set_hdw_async:
                return "STOP"
            if seg[0] == 'E':  # end an
                return "STOP"
            elif seg[:2] == 'LN':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_neo_to(light_n, r, g, b)
            # modules NMZZZ_I_XXX = Neo 6 modules only ZZZ (0 All, 1 to 999) I index (0 All, 1 to 6) XXX 0 to 255</div>
            elif seg[:2] == 'NM':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0][2:])
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_module_to(mod_n, index, v)
            # brightness BXXX = Brightness XXX 000 to 100
            elif seg[0:2] == 'BN':
                br = int(seg[2:])
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
            # QXXX/XXX = Add media to queue XXX/XXX (folder/filename)
            if seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)
    except Exception as e:
            files.log_item(e)

def is_neo(number, nested_array):
    return any(number in sublist for sublist in nested_array)

def set_neo_to(light_n, r, g, b):
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

def set_neo_module_to(mod_n, ind, v):
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

upd_vol(.1)
aud_en.value = True

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)

        spk_web()
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")


files.log_item("animator has started...")
gc_col("animations started.")

# Main task handling
async def process_commands_task():
    """Task to continuously process commands."""
    while True:
        try:
            await process_commands()  # Async command processing
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks

async def server_poll_task(server):
    """Poll the web server."""
    while True:
        try:
            server.poll()  # Web server polling
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks

async def garbage_collection_task():
    while True:
        gc.collect()  # Collect garbage
        await asyncio.sleep(10)  # Run every 10 seconds (adjust as needed)

async def main():
    # Create asyncio tasks
    tasks = [
        process_commands_task(),
        garbage_collection_task(),
    ]

    if web:
        tasks.append(server_poll_task(server))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass



