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

# ADDED (decoder)
import pulseio
import digitalio


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def f_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")

################################################################################
# Sd card config variables

animators_folder = "/animations/"

cfg = files.read_json_file("cfg.json")

ts_jsons = files.return_directory("", "t_s_def", ".json")

web = cfg["serve_webpage"]

exit_set_hdw_async = False

gc_col("config setup")

def upd_media():
    global animations
    animations = files.return_directory("", "animations", ".json")

upd_media()

################################################################################
# Setup neo pixels (main light string)

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

n_px = 1  # keep non-zero so NeoPixel init doesn't choke before we rebuild
neo_pixel_pin = board.GP6
led = neopixel.NeoPixel(neo_pixel_pin, n_px)
led.auto_write = False
led.fill((0, 0, 20))
led.show()

led_indicator = neopixel.NeoPixel(board.GP14, 1)
led_indicator.auto_write = False
led_indicator.fill((0, 0, 20))
led_indicator.show()


def bld_tree(p):
    i = []
    for t in trees:
        for ledi in t:
            si = ledi
            break
        if p == "ornaments":
            for ledi in range(0, 7):
                i.append(ledi + si)
        if p == "star":
            for ledi in range(7, 14):
                i.append(ledi + si)
        if p == "branches":
            for ledi in range(14, 21):
                i.append(ledi + si)
    return i


def bld_cane(p):
    i = []
    for c in canes:
        for led_i in c:
            si = led_i
            break
        if p == "end":
            for led_i in range(0, 2):
                i.append(led_i + si)
        if p == "start":
            for led_i in range(2, 4):
                i.append(led_i + si)
    return i


def bld_bar():
    i = []
    for b in bars:
        for l in b:
            si = l
            break
        for l in range(0, 10):
            i.append(l + si)
    return i


def bld_bolt():
    i = []
    for b in bolts:
        for l in b:
            si = l
            break
        if len(b) == 4:
            for l in range(0, 4):
                i.append(l + si)
        if len(b) == 1:
            for l in range(0, 1):
                i.append(l + si)
    return i


def bld_neo():
    i = []
    for n in neos:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l + si)
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
    try:
        led.deinit()
    except Exception:
        pass
    led = neopixel.NeoPixel(neo_pixel_pin, n_px)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()


upd_l_str()

gc_col("Neopixels setup")

################################################################################
# PWM RGB (base-4) decoder + mapping to queue
# (This is separate from your main light-string NeoPixels)

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789,_/.+-*"
assert len(ALPHABET) == 43

PINS = {"R": board.GP2, "G": board.GP3, "B": board.GP4}

IDLE_STATE = False
MAXLEN = 1200

CAPTURE_S = 0.02
MIN_DURS = 40

T01 = 0.2512
T12 = 0.3293
T23 = 0.4040

ALPHA = 0.20
WIN = 5
MIN_MAJ = 5

CONFIRM_COUNT = 3

def _enable_pullup(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    d.deinit()

def _duty_raw_from_pulsein(pulses: pulseio.PulseIn):
    n = len(pulses)
    if n < MIN_DURS:
        return None

    data = [pulses[i] for i in range(n)]
    if len(data) % 2:
        data = data[1:]

    even_sum = 0
    odd_sum = 0
    total_sum = 0
    for i in range(0, len(data), 2):
        a = data[i]
        b = data[i + 1]
        even_sum += a
        odd_sum += b
        total_sum += (a + b)

    if total_sum == 0:
        return None

    duty_even = even_sum / total_sum
    duty_odd  = odd_sum  / total_sum
    return duty_even if duty_even <= duty_odd else duty_odd

def _duty_to_digit(d):
    if d < T01: return 0
    if d < T12: return 1
    if d < T23: return 2
    return 3

def _rgb_digits_to_char(r, g, b):
    idx = r * 16 + g * 4 + b
    if idx >= len(ALPHABET):
        return None
    return ALPHABET[idx]

def _majority_tuple(buf):
    counts = {}
    for t in buf:
        counts[t] = counts.get(t, 0) + 1
    best_t = None
    best_n = 0
    for t, n in counts.items():
        if n > best_n:
            best_t, best_n = t, n
    return best_t, best_n

comm_latest = {"char": None, "digits": None, "votes": 0, "lat_ms": 0}
comm_new_char_event = asyncio.Event()

# Map decoded characters to *hardware command strings* (enqueued)
# Change these to whatever you want.
CHAR_TO_HDW = {
    "a": "LN1_255_0_0",   # example
    "b": "LN1_0_255_0",   # example
    "c": "LN1_0_0_255",   # example
}

async def decoder_task():
    for pin in PINS.values():
        _enable_pullup(pin)

    pulseins = {}
    for k, pin in PINS.items():
        pi = pulseio.PulseIn(pin, maxlen=MAXLEN, idle_state=IDLE_STATE)
        pi.pause()
        pulseins[k] = pi

    filt = {"R": None, "G": None, "B": None}
    hist = []
    last_char = None

    candidate = None
    candidate_n = 0
    candidate_start_t = None

    while True:
        # parallel capture
        for ch in ("R", "G", "B"):
            pulseins[ch].clear()
            pulseins[ch].resume()

        await asyncio.sleep(CAPTURE_S)

        for ch in ("R", "G", "B"):
            pulseins[ch].pause()

        digits = {}

        for ch in ("R", "G", "B"):
            d = _duty_raw_from_pulsein(pulseins[ch])
            if d is None:
                digits = None
                break

            if filt[ch] is None:
                filt[ch] = d
            else:
                filt[ch] = ALPHA * d + (1.0 - ALPHA) * filt[ch]

            digits[ch] = _duty_to_digit(filt[ch])

        if digits is None:
            await asyncio.sleep(0)
            continue

        t = (digits["R"], digits["G"], digits["B"])

        hist.append(t)
        if len(hist) > WIN:
            hist.pop(0)

        best_t, best_n = _majority_tuple(hist)

        if best_n < MIN_MAJ:
            await asyncio.sleep(0)
            continue

        ch_out = _rgb_digits_to_char(*best_t)
        if ch_out is None:
            candidate = None
            candidate_n = 0
            candidate_start_t = None
            await asyncio.sleep(0)
            continue

        if best_t != candidate:
            candidate = best_t
            candidate_n = 1
            candidate_start_t = time.monotonic()
        else:
            candidate_n += 1

        if candidate_n < CONFIRM_COUNT:
            await asyncio.sleep(0)
            continue

        if ch_out != last_char:
            now = time.monotonic()
            lat_ms = int((now - candidate_start_t) * 1000) if candidate_start_t is not None else 0

            last_char = ch_out
            comm_latest["char"] = ch_out
            comm_latest["digits"] = best_t
            comm_latest["votes"] = best_n
            comm_latest["lat_ms"] = lat_ms
            comm_new_char_event.set()

            candidate_start_t = None

        await asyncio.sleep(0)

################################################################################
# Setup wifi and web server

if web:
    import socketpool
    import mdns
    gc_col("config wifi imports")
    import wifi
    gc_col("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
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
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        gc_col("wifi connect")

        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(service_type="_http", protocol="_tcp", port=80)

        local_ip = str(wifi.radio.ipv4_address)
        files.log_item("IP is" + local_ip)
        files.log_item("Connected")

        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)

        gc_col("wifi server")

        ################################################################################
        # Setup routes

        @server.route("/")
        def base(request: Request):
            gc_col("Home page.")
            return FileResponse(request, "index.html", "/")

        @server.route("/mui.min.css")
        def mui_css(request: Request):
            return FileResponse(request, "mui.min.css", "/")

        @server.route("/mui.min.js")
        def mui_js(request: Request):
            return FileResponse(request, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def animation_btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["option_selected"] = rq_d["an"]
            add_command(cfg["option_selected"])
            files.write_json_file("cfg.json", cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def defaults_btn(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for ts_fn in ts_jsons:
                    ts = files.read_json_file("t_s_def/" + ts_fn + ".json")
                    files.write_json_file("animations/" + ts_fn + ".json", ts)
            elif rq_d["an"] == "reset_to_defaults":
                rst_def()
                files.write_json_file("cfg.json", cfg)
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/stop", [POST])
        def stop_btn(request: Request):
            stop_all_commands()
            return Response(request, "Stopped all commands")

        @server.route("/lights", [POST])
        def lights_btn(request: Request):
            global exit_set_hdw_async
            exit_set_hdw_async = False
            try:
                rq_d = request.json()
                asyncio.create_task(set_hdw_async(rq_d["an"], 0))
                return Response(request, "Utility: set lights successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error setting lights.")

        @server.route("/create-animation", [POST])
        def create_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                f_n = animators_folder + rq_d["fn"] + ".json"
                an_data = [
                    "0.0|BN100,LN0_255_0_0",
                    "1.0|BN100,LN0_0_255_0",
                    "2.0|BN100,LN0_0_0_255",
                    "3.0|BN100,LN0_255_255_255"
                ]
                files.write_json_file(f_n, an_data)
                upd_media()
                return Response(request, "Created animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error creating animation.")

        @server.route("/rename-animation", [POST])
        def rename_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                fo = animators_folder + rq_d["fo"] + ".json"
                fn = animators_folder + rq_d["fn"] + ".json"
                os.rename(fo, fn)
                upd_media()
                return Response(request, "Renamed animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error renaming animation.")

        @server.route("/delete-animation", [POST])
        def delete_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                f_n = animators_folder + rq_d["fn"] + ".json"
                os.remove(f_n)
                upd_media()
                return Response(request, "Delete animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error deleting animation.")

        @server.route("/update-light-string", [POST])
        def update_light_string(req: Request):
            global cfg
            rq_d = req.json()
            if rq_d["action"] in ("save", "clear", "defaults"):
                cfg["light_string"] = rq_d["text"]
                files.write_json_file("cfg.json", cfg)
                upd_l_str()
                return Response(req, cfg["light_string"])

            if cfg["light_string"] == "":
                cfg["light_string"] = rq_d["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + "," + rq_d["text"]

            files.write_json_file("cfg.json", cfg)
            upd_l_str()
            return Response(req, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def get_light_string(req: Request):
            return Response(req, cfg["light_string"])

        @server.route("/update-host-name", [POST])
        def update_host_name(request: Request):
            global cfg
            rq_d = request.json()
            cfg["HOST_NAME"] = rq_d["an"]
            files.write_json_file("cfg.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def get_host_name(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-local-ip", [POST])
        def get_local_ip(request: Request):
            return Response(request, local_ip)

        @server.route("/get-animations", [POST])
        def get_animations(request: Request):
            sounds = []
            sounds.extend(animations)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/test-animation", [POST])
        def test_animation(request: Request):
            global exit_set_hdw_async
            exit_set_hdw_async = False
            try:
                rq_d = request.json()
                asyncio.create_task(set_hdw_async(rq_d["an"], 3))
                return Response(request, "Test animation successfully")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error test animation.")

        @server.route("/get-animation", [POST])
        def get_animation(request: Request):
            rq_d = request.json()
            snd_f = rq_d["an"]
            if f_exists("animations/" + snd_f + ".json"):
                f_n = "animations/" + snd_f + ".json"
                return FileResponse(request, f_n, "/")
            else:
                f_n = "t_s_def/timestamp mode.json"
                return FileResponse(request, f_n, "/")

        data = []

        @server.route("/save-data", [POST])
        def save_data(request: Request):
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
# Command queue
command_queue = []

def add_command(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    if to_start:
        command_queue.insert(0, command)
        print("Command added to the start:", command)
    else:
        command_queue.append(command)
        print("Command added to the end:", command)

async def process_commands():
    while command_queue:
        command = command_queue.pop(0)
        print("Processing command:", command)
        await an_async(command)
        await asyncio.sleep(0)

def clear_command_queue():
    command_queue.clear()
    print("Command queue cleared.")

def stop_all_commands():
    global exit_set_hdw_async
    clear_command_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"


################################################################################
# animations

async def an_async(f_nm):
    print("Filename:", f_nm)
    try:
        await an_light_async(f_nm)
        gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
    gc_col("Animation complete.")

async def an_light_async(f_nm):
    flsh_t = []
    if f_exists("animations/" + f_nm + ".json"):
        flsh_t = files.read_json_file("animations/" + f_nm + ".json")
    else:
        # If it's not an animation file, treat it as a direct hardware command string
        # so queued decoder commands like "LN1_..." work immediately.
        result = await set_hdw_async(f_nm, 0)
        await asyncio.sleep(0)
        return result

    ft_last = flsh_t[len(flsh_t) - 1].split("|")
    tm_last = float(ft_last[0]) + .1
    flsh_t.append(str(tm_last) + "|E")
    flsh_t.append(str(tm_last + .1) + "|E")

    flsh_i = 0
    srt_t = time.monotonic()

    while True:
        t_past = time.monotonic() - srt_t
        if flsh_i < len(flsh_t) - 1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i + 1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0

        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t) - 1:
            files.log_item(f"time elapsed: {t_past} Timestamp: {ft1[0]}")
            if len(ft1) == 1 or ft1[1] == "":
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                result = await set_hdw_async(f"L0{lgt},S0{pos}", dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            flsh_i += 1

        await asyncio.sleep(0)

        if flsh_i >= len(flsh_t) - 1:
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
    te = time.monotonic() - st
    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw_async:
                return
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            await asyncio.sleep(spd)
            te = time.monotonic() - st
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
            te = time.monotonic() - st
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
    brnchsi.extend(brnchs)

    for i in brnchsi:
        led[i] = (50, 50, 50)

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    while True:
        for i in firei:
            if exit_set_hdw_async:
                return
            f = random.randint(0, 110)
            r1 = bnd(r - f, 0, 255)
            g1 = bnd(g - f, 0, 255)
            b1 = bnd(b - f, 0, 255)
            led[i] = (r1, g1, b1)
            led.show()
        await asyncio.sleep(random.uniform(0.05, 0.1))
        te = time.monotonic() - st
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
        else:
            r1 = 0
            g1 = 0
            b1 = b
        led[i] = (r1, g1, b1)

    for i in stars:
        led[i] = (255, 255, 255)

    for i in brnchs:
        led[i] = (7, 163, 30)

    for i in cane_e:
        led[i] = (255, 255, 255)

    led.show()

def bnd(c, l, u):
    if c < l:
        c = l
    if c > u:
        c = u
    return c


sp = [0, 0, 0, 0, 0, 0]
br = 0

async def set_hdw_async(input_string, dur):
    global sp, br, exit_set_hdw_async
    segs = input_string.split(",")

    try:
        for seg in segs:
            if exit_set_hdw_async:
                return "STOP"
            if seg[0] == 'E':
                return "STOP"
            elif seg[:2] == 'LN':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:]) - 1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_neo_to(light_n, r, g, b)
            elif seg[:2] == 'NM':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0][2:])
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_module_to(mod_n, index, v)
            elif seg[0:2] == 'BN':
                br = int(seg[2:])
                led.brightness = float(br / 100)
                led.show()
            elif seg[0] == 'F':
                segs_split = seg.split("_")
                v = int(segs_split[0][1:])
                s = float(segs_split[1])
                while not br == v:
                    if br < v:
                        br += 1
                    else:
                        br -= 1
                    led.brightness = float(br / 100)
                    led.show()
                    await asyncio.sleep(s)
            elif seg[0:] == 'ZRAND':
                await random_effect(1, 3, dur)
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                await rbow(v, dur)
            elif seg[0:] == 'ZFIRE':
                await fire(dur)
            elif seg[0:] == 'ZCOLCH':
                multi_color()
                await asyncio.sleep(dur)
            if seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)
    except Exception as e:
        files.log_item(e)

def is_neo(number, nested_array):
    return any(number in sublist for sublist in nested_array)

def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):
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
            led[i + 1] = (v, v, v)
    elif ind == 0:
        led[neo_ids[mod_n - 1]] = (v, v, v)
        led[neo_ids[mod_n - 1] + 1] = (v, v, v)
    elif ind < 4:
        ind -= 1
        if ind == 0:
            ind = 1
        elif ind == 1:
            ind = 0
        cur = list(led[neo_ids[mod_n - 1]])
        cur[ind] = v
        led[neo_ids[mod_n - 1]] = (cur[0], cur[1], cur[2])
        print(led[neo_ids[mod_n - 1]])
    else:
        ind -= 1
        if ind == 3:
            ind = 4
        elif ind == 4:
            ind = 3
        cur = list(led[neo_ids[mod_n - 1] + 1])
        cur[ind - 3] = v
        led[neo_ids[mod_n - 1] + 1] = (cur[0], cur[1], cur[2])
    led.show()


################################################################################
# Decoder consumer: map a/b/c -> hardware command string, then enqueue

async def consumer_task():
    while True:
        await comm_new_char_event.wait()
        comm_new_char_event.clear()

        ch = comm_latest["char"]
        if ch is None:
            await asyncio.sleep(0)
            continue

        # Debug (keep or remove)
        print("CHAR:", ch,
              "| digits:", comm_latest["digits"],
              "| votes:", comm_latest["votes"],
              "| latency_ms:", comm_latest["lat_ms"])

        if ch in CHAR_TO_HDW:
            add_command(CHAR_TO_HDW[ch])
            print("Enqueued mapped HW:", CHAR_TO_HDW[ch])
        else:
            # If you want *all* chars enqueued too, keep this line.
            # Otherwise delete it.
            add_command(ch)

        await asyncio.sleep(0)


################################################################################
# Start server

if web:
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        rst()

files.log_item("animator has started...")
gc_col("animations started.")

################################################################################
# Main task handling

async def process_commands_task():
    while True:
        try:
            await process_commands()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)

async def server_poll_task(server):
    while True:
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)

async def garbage_collection_task():
    while True:
        gc.collect()
        await asyncio.sleep(10)

async def main():
    tasks = [
        process_commands_task(),
        garbage_collection_task(),
        decoder_task(),
        consumer_task(),
    ]

    if web:
        tasks.append(server_poll_task(server))

    await asyncio.gather(*tasks)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
