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
import gc
import files
import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import digitalio
import board
import random
import rtc
import microcontroller
from analogio import AnalogIn
import neopixel
from rainbowio import colorwheel
from adafruit_debouncer import Debouncer
import asyncio
import os


def gc_col(c_p):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + c_p +
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

# Setup pin for v
a_in = AnalogIn(board.A0)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_mute = digitalio.DigitalInOut(board.GP22)
aud_mute.direction = digitalio.Direction.OUTPUT
aud_mute.value = True

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
aud_mute.value = False
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer
mix = audiomixer.Mixer(voice_count=2, sample_rate=22050,
                       channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

try:
    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
except Exception as e:
    files.log_item(e)
    w1 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[1].play(w1, loop=False)
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
                w1 = audiocore.WaveFile(
                    open("/sd/mvc/micro_sd_card_success.wav", "rb"))
                mix.voice[1].play(w1, loop=False)
                while mix.voice[1].playing:
                    pass
            except Exception as e:
                files.log_item(e)
                w1 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[1].play(w1, loop=False)
                while mix.voice[1].playing:
                    pass

aud_mute.value = True

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

cfg = files.read_json_file("/sd/cfg.json")

cfg_backup = files.read_json_file("/sd/cfg.json")

snd_o = files.return_directory("", "/sd/snds", ".wav")

cus_o = files.return_directory(
    "customers_owned_music_", "/sd/customers_owned_music", ".wav")

all_o = []
all_o.extend(snd_o)
all_o.extend(cus_o)

mnu_o = []
mnu_o.extend(snd_o)
rnd_o = ['random all', 'random built in', 'random my']
mnu_o.extend(rnd_o)
mnu_o.extend(cus_o)

ts_json = files.return_directory(
    "", "/sd/t_s_def", ".json")

web = cfg["serve_webpage"]

c_m = files.read_json_file("/sd/mvc/main_menu.json")
m_mnu = c_m["main_menu"]

c_w = files.read_json_file("/sd/mvc/web_menu.json")
web_m = c_w["web_menu"]

c_l = files.read_json_file(
    "/sd/mvc/light_string_menu.json")
l_mnu = c_l["light_string_menu"]

c_l_o = files.read_json_file("/sd/mvc/light_options.json")
l_opt = c_l_o["light_options"]

c_v = files.read_json_file("/sd/mvc/volume_settings.json")
v_s = c_v["volume_settings"]

c_a_s = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
add_snd = c_a_s["add_sounds_animate"]

cont_run = False
ts_mode = False
t_s = []
t_elsp = 0.0

local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

exit_set_hdw_async = False
is_running_an = False

gc_col("config setup")

################################################################################
# Setup neo pixels

bars = []
bolts = []
noods = []
nbolts = []
witches = []
saucers = []
ghosts = []
jets = []
stars = []

bar_arr = []
bolt_arr = []
nbolt_arr = []
witch_arr = []
saucer_arr = []
ghost_arr = []
jet_arr = []
star_arr = []

n_px = 2
neo_pin = board.GP10
led = neopixel.NeoPixel(neo_pin, n_px)


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


def bld_nbolt():
    i = []
    for b in nbolts:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def bld_witch():
    i = []
    for b in witches:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def bld_saucer():
    i = []
    for b in saucers:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def bld_ghost():
    i = []
    for b in ghosts:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def bld_jet():
    i = []
    for b in jets:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def bld_star():
    i = []
    for b in stars:
        for l in b:
            si = l
            break
        for l in range(0, len(b)):
            i.append(l+si)
    return i


def l_tst():
    global bar_arr, bolt_arr, nbolt_arr, witch_arr, saucer_arr, ghost_arr, jet_arr, star_arr
    bar_arr = bld_bar()
    bolt_arr = bld_bolt()
    nbolt_arr = bld_nbolt()
    witch_arr = bld_witch()
    saucer_arr = bld_saucer()
    ghost_arr = bld_ghost()
    jet_arr = bld_jet()
    star_arr = bld_saucer()

    for b in bars:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in bolts:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for n in noods:
        led[n[0]] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in nbolts:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in witches:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in saucers:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in ghosts:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in jets:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for b in stars:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()


def upd_l_str():
    global n_px, led, bars, bolts, noods, nbolts, witches, saucers, ghosts, jets, stars
    bars = []
    bolts = []
    noods = []
    nbolts = []
    witches = []
    saucers = []
    ghosts = []
    jets = []
    stars = []

    n_px = 0

    els = cfg["light_string"].split(',')

    for el in els:
        p = el.split('-')
        if len(p) == 2:
            typ, qty = p
            qty = int(qty)
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
            elif typ == 'nbolt':
                s = list(range(n_px, n_px + qty))
                nbolts.append(s)
                n_px += qty
            elif typ == 'witch':
                s = list(range(n_px, n_px + qty))
                witches.append(s)
                n_px += qty
            elif typ == 'saucer':
                s = list(range(n_px, n_px + qty))
                saucers.append(s)
                n_px += qty
            elif typ == 'ghost':
                s = list(range(n_px, n_px + qty))
                ghosts.append(s)
                n_px += qty
            elif typ == 'jet':
                s = list(range(n_px, n_px + qty))
                jets.append(s)
                n_px += qty
            elif typ == 'star':
                s = list(range(n_px, n_px + qty))
                stars.append(s)
                n_px += qty

    led.deinit()
    gc_col("Deinit ledStrip")
    led = neopixel.NeoPixel(neo_pin, n_px)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()


gc_col("Neopixels setup")

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

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid")
    except Exception as e:
        files.log_item(e)
        print("Using default ssid")

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

            # files.log_items IP address to REPL
            local_ip = str(wifi.radio.ipv4_address)
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
                stp_a_1()
                gc_col("Home page.")
                return FileResponse(req, "index.html", "/")

            @server.route("/mui.min.css")
            def base(req: HTTPRequest):
                stp_a_1()
                return FileResponse(req, "/sd/mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(req: HTTPRequest):
                stp_a_1()
                return FileResponse(req, "/sd/mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(req: Request):
                global cfg, cont_run, ts_mode
                rq_d = req.json()
                cfg["option_selected"] = rq_d["an"]
                add_cmd("AN_" + cfg["option_selected"])
                if not mix.voice[0].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                return Response(req, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(req: Request):
                global cfg
                stp_a_1()
                rq_d = req.json()
                if rq_d["an"] == "reset_animation_timing_to_defaults":
                    for ts_fn in ts_json:
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
                elif rq_d["an"] == "reset_incandescent_colors":
                    rst_def_col()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
                    s = files.json_stringify(
                        {"bars": cfg["bars"], "bolts": cfg["bolts"], "v": cfg["v"]})
                    st_mch.go_to('base_state')
                    return Response(req, s)
                elif rq_d["an"] == "reset_white_colors":
                    rst_wht_col()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
                    s = files.json_stringify(
                        {"bars": cfg["bars"], "bolts": cfg["bolts"], "v": cfg["v"]})
                    st_mch.go_to('base_state')
                    return Response(req, s)
                return Response(req, "Utility: " + rq_d["an"])

            @server.route("/mode", [POST])
            def btn(req: Request):
                global cfg, cont_run, ts_mode
                rq_d = req.json()
                if rq_d["an"] == "left":
                    ovrde_sw_st["switch_value"] = "left"
                elif rq_d["an"] == "left_held":
                    ovrde_sw_st["switch_value"] = "left_held"
                elif rq_d["an"] == "right":
                    ovrde_sw_st["switch_value"] = "right"
                elif rq_d["an"] == "right_held":
                    ovrde_sw_st["switch_value"] = "right_held"
                elif rq_d["an"] == "cont_mode_on":
                    cont_run = True
                    ply_a_1("/sd/mvc/continuous_mode_activated.wav")
                elif rq_d["an"] == "cont_mode_off":
                    cont_run = False
                    stp_all_cmds()
                    ply_a_1("/sd/mvc/continuous_mode_deactivated.wav")
                elif rq_d["an"] == "timestamp_mode_on":
                    ts_mode = True
                    ply_a_1("/sd/mvc/timestamp_mode_on.wav")
                    ply_a_1("/sd/mvc/timestamp_instructions.wav")
                elif rq_d["an"] == "timestamp_mode_off":
                    ts_mode = False
                    ply_a_1("/sd/mvc/timestamp_mode_off.wav")
                return Response(req, "Utility: " + rq_d["an"])

            @server.route("/speaker", [POST])
            def btn(req: Request):
                global cfg
                stp_a_1()
                rq_d = req.json()
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
                return Response(req, "Utility: " + rq_d["an"])

            @server.route("/lights", [POST])
            def btn(req: Request):
                stp_a_1()
                rq_d = req.json()
                v = rq_d["an"].split(",")
                led.fill((float(v[0]), float(v[1]), float(v[2])))
                led.show()
                return Response(req, "OK")

            @server.route("/bolt", [POST])
            def btn(req: Request):
                stp_a_1()
                led.fill((int(cfg["bolts"]["r"]), int(
                    cfg["bolts"]["g"]), int(cfg["bolts"]["b"])))
                led.show()
                return Response(req, "OK")

            @server.route("/bar", [POST])
            def btn(req: Request):
                stp_a_1()
                led.fill((int(cfg["bars"]["r"]), int(
                    cfg["bars"]["g"]), int(cfg["bars"]["b"])))
                led.show()
                return Response(req, "OK")

            @server.route("/bright", [POST])
            def btn(req: Request):
                rq_d = req.json()
                stp_a_1()
                led.brightness = float(rq_d["an"])
                led.show()
                return Response(req, "OK")

            @server.route("/update-host-name", [POST])
            def btn(req: Request):
                global cfg
                stp_a_1()
                rq_d = req.json()
                cfg["HOST_NAME"] = rq_d["text"]
                files.write_json_file("/sd/cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                spk_web()
                return Response(req, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def btn(req: Request):
                return Response(req, cfg["HOST_NAME"])

            @server.route("/update-volume", [POST])
            def btn(req: Request):
                global cfg
                rq_d = req.json()
                ch_vol(rq_d["action"])
                return Response(req, rq_d["action"])

            @server.route("/get-volume", [POST])
            def btn(req: Request):
                return Response(req, cfg["volume"])

            @server.route("/update-light-string", [POST])
            def btn(req: Request):
                global cfg
                rq_d = req.json()
                if rq_d["action"] == "save" or rq_d["action"] == "clear" or rq_d["action"] == "defaults":
                    cfg["light_string"] = rq_d["text"]
                    print("action: " +
                          rq_d["action"] + " data: " + cfg["light_string"])
                    files.write_json_file("/sd/cfg.json", cfg)
                    upd_l_str()
                    ply_a_1("/sd/mvc/all_changes_complete.wav")
                    return Response(req, cfg["light_string"])
                if cfg["light_string"] == "":
                    cfg["light_string"] = rq_d["text"]
                else:
                    cfg["light_string"] = cfg["light_string"] + \
                        "," + rq_d["text"]
                print("action: " + rq_d["action"] +
                      " data: " + cfg["light_string"])
                files.write_json_file("/sd/cfg.json", cfg)
                upd_l_str()
                ply_a_1("/sd/mvc/all_changes_complete.wav")
                return Response(req, cfg["light_string"])

            @server.route("/get-light-string", [POST])
            def btn(req: Request):
                return Response(req, cfg["light_string"])

            @server.route("/get-customers-sound-tracks", [POST])
            def btn(req: Request):
                s = files.json_stringify(cus_o)
                return Response(req, s)

            @server.route("/get-built-in-sound-tracks", [POST])
            def btn(req: Request):
                s = []
                s.extend(snd_o)
                s = files.json_stringify(s)
                return Response(req, s)

            @server.route("/test-animation", [POST])
            def btn(request: Request):
                stp_a_0()
                rq_d = request.json()
                print(rq_d["an"])
                gc_col("Save Data.")
                add_cmd(rq_d["an"])
                return Response(request, "success")

            @server.route("/get-animation", [POST])
            def btn(request: Request):
                global cfg, cont_run, ts_mode
                stp_a_0()
                rq_d = request.json()
                snd_f = rq_d["an"]
                if "customers_owned_music_" in snd_f:
                    snd_f = snd_f.replace("customers_owned_music_", "")
                    if (f_exists("/sd/customers_owned_music/" + snd_f + ".json") == True):
                        f_n = "/sd/customers_owned_music/" + snd_f + ".json"
                        print(f_n)
                        return FileResponse(request, f_n, "/")
                    else:
                        f_n = "/sd/t_s_def/timestamp mode.json"
                        return FileResponse(request, f_n, "/")
                else:
                    if (f_exists("/sd/snds/" + snd_f + ".json") == True):
                        f_n = "/sd/snds/" + snd_f + ".json"
                        return FileResponse(request, f_n, "/")
                    else:
                        f_n = "/sd/t_s_def/timestamp mode.json"
                        return FileResponse(request, f_n, "/")

            @server.route("/get-bar-colors", [POST])
            def btn(req: Request):
                s = files.json_stringify(cfg["bars"])
                return Response(req, s)

            @server.route("/get-bolt-colors", [POST])
            def btn(req: Request):
                s = files.json_stringify(cfg["bolts"])
                return Response(req, s)

            @server.route("/get-color-variation", [POST])
            def btn(req: Request):
                s = files.json_stringify(cfg["v"])
                return Response(req, s)

            @server.route("/set-lights", [POST])
            def btn(req: Request):
                global cfg
                rq_d = req.json()
                if rq_d["item"] == "bars":
                    cfg["bars"] = {"r": rq_d["r"],
                                   "g": rq_d["g"], "b": rq_d["b"]}
                    bi = []
                    bi.extend(bar_arr)
                    for i in bi:
                        led[i] = (rq_d["r"],
                                  rq_d["g"], rq_d["b"])
                    led.show()
                elif rq_d["item"] == "bolts":
                    cfg["bolts"] = {"r": rq_d["r"],
                                    "g": rq_d["g"], "b": rq_d["b"]}
                    bi = []
                    bi.extend(bolt_arr)
                    bi.extend(nbolt_arr)
                    for i in bi:
                        led[i] = (rq_d["r"],
                                  rq_d["g"], rq_d["b"])
                    led.show()
                elif rq_d["item"] == "variationBolt":
                    print(rq_d)
                    cfg["v"] = {"r1": rq_d["r"], "g1": rq_d["g"], "b1": rq_d["b"],
                                "r2": cfg["v"]["r2"], "g2": cfg["v"]["g2"], "b2": cfg["v"]["b2"]}
                elif rq_d["item"] == "variationBar":
                    cfg["v"] = {"r1": cfg["v"]["r1"], "g1": cfg["v"]["g1"], "b1": cfg["v"]
                                ["b1"], "r2": rq_d["r"], "g2": rq_d["g"], "b2": rq_d["b"]}
                files.write_json_file("/sd/cfg.json", cfg)
                return Response(req, "OK")

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                stp_a_1()
                return Response(req, local_ip)

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
                        f_n = ""
                        if "customers_owned_music_" in rq_d[3]:
                            snd_f = rq_d[3].replace(
                                "customers_owned_music_", "")
                            f_n = "/sd/customers_owned_music/" + \
                                snd_f + ".json"
                        else:
                            f_n = "/sd/snds/" + \
                                rq_d[3] + ".json"
                        files.write_json_file(f_n, data)
                        data = []
                        gc_col("get data")
                except Exception as e:
                    files.log_item(e)
                    data = []
                    gc_col("get data")
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


def stp_all_cmds():
    global exit_set_hdw_async
    clr_cmd_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")

################################################################################
# Global Methods


def rst_l_def():
    global cfg
    cfg["light_string"] = "nbolt-1,bar-10,bar-10,nbolt-2,bar-10,nbolt-3,bar-10,nbolt-2,bar-10,nbolt-1,bar-10"


def rst_def_col():
    global cfg
    cfg["bars"] = {"r": 255, "g": 136, "b": 26}
    cfg["bolts"] = {"r": 255, "g": 136, "b": 26}
    cfg["v"] = {"r1": 20, "g1": 8, "b1": 5, "r2": 20, "g2": 8, "b2": 5}


def rst_wht_col():
    global cfg
    cfg["bars"] = {"r": 255, "g": 255, "b": 255}
    cfg["bolts"] = {"r": 255, "g": 255, "b": 255}
    cfg["v"] = {"r1": 0, "g1": 0, "b1": 0, "r2": 0, "g2": 0, "b2": 0}


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-lightning"
    cfg["option_selected"] = "thunder birds rain"
    cfg["volume"] = "20"
    cfg["can_cancel"] = True
    rst_l_def()
    rst_def_col()


################################################################################
# Dialog and sound play methods


def upd_vol(s):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        mix.voice[1].level = v
        time.sleep(s)
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
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_1("/sd/mvc/volume.wav")
        spk_str(cfg["volume"], False)


def ply_a_1(file_name):
    if mix.voice[1].playing:
        mix.voice[1].stop()
        while mix.voice[1].playing:
            upd_vol(0.02)
    w1 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[1].play(w1, loop=False)
    while mix.voice[1].playing:
        exit_early()
        upd_vol(0.02)


def stp_a_1():
    mix.voice[1].stop()
    while mix.voice[1].playing:
        pass


def stp_a_0():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass


def exit_early(wait_time=3.0):
    global cont_run, ovrde_sw_st, is_running_an, exit_set_hdw_async
    sw = utilities.switch_state(
        l_sw, r_sw, time.sleep, wait_time, ovrde_sw_st)
    if sw == "left" and cfg["can_cancel"]:
        exit_set_hdw_async = True
        mix.voice[0].stop()
        l_sw.update()
        r_sw.update()
    if sw == "left_held":
        exit_set_hdw_async = True
        mix.voice[0].stop()
        cont_run = False
        stp_all_cmds()
        ply_a_1("/sd/mvc/continuous_mode_deactivated.wav")


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


def spk_lght(play_intro):
    try:
        elements = cfg["light_string"].split(',')
        if play_intro:
            ply_a_1("/sd/mvc/current_light_settings_are.wav")
        for index, element in enumerate(elements):
            ply_a_1("/sd/mvc/position.wav")
            play_number(index+1)
            ply_a_1("/sd/mvc/is.wav")
            ply_a_1("/sd/mvc/" + element + ".wav")
    except Exception as e:
        files.log_item(e)
        ply_a_1("/sd/mvc/no_lights_in_light_string.wav")
        return
    
def play_number(number):
    # Convert number to string to process each digit
    digits = str(number)
    for digit in digits:
        # Construct path for single-digit WAV file
        wav_path = f"/sd/mvc/{digit}.wav"
        ply_a_1(wav_path)


async def no_trk():
    global ovrde_sw_st
    ply_a_1("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        sw = utilities.switch_state(l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left" or cont_run:
            break
        elif sw == "right":
            ply_a_1("/sd/mvc/create_sound_track_files.wav")
            break
        await upd_vol_async(.1)


def spk_web():
    ply_a_1("/sd/mvc/animator_available_on_network.wav")
    ply_a_1("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-lightning":
        ply_a_1("/sd/mvc/animator_dash_lightning.wav")
        ply_a_1("/sd/mvc/dot.wav")
        ply_a_1("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_1("/sd/mvc/in_your_browser.wav")

################################################################################
# animations


def convert_to_new_format(my_object, my_type):
    flash_times = my_object.get("flashTime", [])
    return [f"{time}|{my_type}" for time in flash_times]


async def an_async(fn):
    global is_running_an, cfg
    print("Filename: " + fn)
    cur = fn
    is_running_an = True
    try:
        if fn == "random built in":
            hi = len(snd_o) - 1
            cur = snd_o[random.randint(0, hi)]
        elif fn == "random my":
            hi = len(cus_o) - 1
            cur = cus_o[random.randint(0, hi)]
        elif fn == "random all":
            hi = len(all_o) - 1
            cur = all_o[random.randint(0, hi)]
        if ts_mode:
            an_ts(cur)
        else:
            if "customers_owned_music_" in cur:
                await an_ls(cur, "ZRAND")
            elif cur == "alien lightshow":
                await an_ls(cur, "ZRAND")
            elif cur == "inspiring cinematic ambient lightshow":
                await an_ls(cur, "ZRAND")
            elif cur == "fireworks":
                await an_ls(cur, "FRWK")
            else:
                if ts_mode == True:
                    await an_lightning(cur)
                else:
                    await an_ls(cur, "LIGHT")
    except Exception as e:
        files.log_item(e)
        await no_trk()
        cfg["option_selected"] = "random built in"
        return
    is_running_an = False
    cfg = files.read_json_file("/sd/cfg.json")
    gc_col("Animation complete.")


async def an_ls(fn, my_type):
    global ts_mode, cont_run, ovrde_sw_st

    cust_f = "customers_owned_music_" in fn

    if cust_f:
        fn = fn.replace("customers_owned_music_", "")
        try:
            flsh_t = files.read_json_file(
                "/sd/customers_owned_music/" + fn + ".json")
        except Exception as e:
            files.log_item(e)
            ply_a_1("/sd/mvc/no_timestamp_file_found.wav")
            while True:
                l_sw.update()
                r_sw.update()
                if l_sw.fell:
                    ts_mode = False
                    return
                if r_sw.fell:
                    ts_mode = True
                    ply_a_1("/sd/mvc/timestamp_instructions.wav")
                    return
    else:
        flsh_t = files.read_json_file(
            "/sd/snds/" + fn + ".json")
        
    ft_last = flsh_t[len(flsh_t)-1].split("|")
    tm_last = float(ft_last[0]) + 1
    flsh_t.append(str(tm_last) + "|")

    if cust_f:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/snds/" + fn + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)

    srt_t = time.monotonic()

    flsh_i = 0

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
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                result = await set_hdw_async("L0" + str(lgt) + ",S0" + str(pos))
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            flsh_i += 1
        exit_early()
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            return
        await upd_vol_async(.1)

def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)

def an_ts(fn):
    print("Time stamp mode:")
    global t_s, t_elsp, ts_mode

    cf = "customers_owned_music_" in fn

    t_s= []

    fn = fn.replace("customers_owned_music_", "")

    if cf:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/snds/" + fn + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)

    st = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = time.monotonic()-st
        r_sw.update()
        if r_sw.fell:
            add_command_to_ts("")
        if not mix.voice[0].playing:
            add_command_to_ts("")
            led.fill((0, 0, 0))
            led.show()
            if cf:
                files.write_json_file(
                    "/sd/customers_owned_music/" + fn + ".json", t_s)
            else:
                files.write_json_file(
                    "/sd/snds/" + fn + ".json", t_s)
            break

    ts_mode = False
    ply_a_1("/sd/mvc/timestamp_saved.wav")
    ply_a_1("/sd/mvc/timestamp_mode_off.wav")
    ply_a_1("/sd/mvc/animations_are_now_active.wav")


async def an_lightning(file_name):
    global cont_run

    ftd = files.read_json_file(
        "/sd/snds/" + file_name + ".json")

    ft = ftd["flashTime"]

    ftl = len(ft)
    fti = 0

    w0 = audiocore.WaveFile(
        open("/sd/snds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    st = time.monotonic()

    while True:
        upd_vol(.1)
        await asyncio.sleep(0)
        te = time.monotonic()-st
        # amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
        rt = ft[fti] - random.uniform(.5, 1)
        if te > rt:
            exit_early()
            print("TE: " + str(te) + " TS: " +
                  str(rt) + " Dif: " + str(te-rt))
            fti += 1
            ltng()
        if ftl == fti:
            fti = 0
        exit_early()
        if not mix.voice[0].playing:
            break


async def set_hdw_async(input_string, dur=0):
    global exit_set_hdw_async, cfg, cfg_backup
    segs = input_string.split(",")
    # Process each segment
    for seg in segs:
        if exit_set_hdw_async:
            return
        # ZRAND = Random rainbow, fire, or color change
        if seg[0:] == 'ZRAND':
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
        # LIGHT = Lightning  
        elif seg[0:] == 'LIGHT':
            ltng()
        # FRWK = Fireworks
        elif seg[0:] == 'FRWK':
            await frwk(dur)
        # BOLT_R_G_B = Bolt color, R = red, G = green, B = blue
        elif seg[:4] == 'BOLT':
            seg_split = seg.split("_")
            cfg["bolts"]["r"] = int(seg_split[1])
            cfg["bolts"]["g"] = int(seg_split[2])
            cfg["bolts"]["b"] = int(seg_split[3])
        # BAR_R_G_B = Bolt color, R = red, G = green, B = blue
        elif seg[:3] == 'BAR':
            seg_split = seg.split("_")
            cfg["bars"]["r"] = int(seg_split[1])
            cfg["bars"]["g"] = int(seg_split[2])
            cfg["bars"]["b"] = int(seg_split[3])
        # RESET_COLORS = Reset colors to config file
        elif seg[:12] == 'RESET_COLORS':
            cfg["bolts"]["r"] = cfg_backup["bolts"]["r"]
            cfg["bolts"]["g"] = cfg_backup["bolts"]["g"]
            cfg["bolts"]["b"] = cfg_backup["bolts"]["b"]
            cfg["bars"]["r"] = cfg_backup["bars"]["r"]
            cfg["bars"]["g"] = cfg_backup["bars"]["g"]
            cfg["bars"]["b"] = cfg_backup["bars"]["b"]
        # AN_XXX = Animation XXX filename
        elif seg[:2] == 'AN':
            seg_split = seg.split("_")
            # Process each command as an async operation
            if seg_split[1] == "customers":
                await an_async(seg_split[1]+"_"+seg_split[2]+"_"+seg_split[3]+"_"+seg_split[4])
            else:
                await an_async(seg_split[1])

##############################
# animation effects


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


async def fire(dur):
    global exit_set_hdw_async
    st = time.monotonic()
    led.brightness = 1.0

    bari = []
    bari.extend(bar_arr)
    bari.extend(nbolt_arr)

    bolti = []
    bolti.extend(bolt_arr)

    nbolti = []
    nbolti.extend(nbolt_arr)

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    for i in bolti:
        led[i] = (r, g, b)

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        for i in bari:
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


def fwrk_sprd(arr):
    c = len(arr) // 2
    for i in range(c):
        l_i = c - 1 - i
        r_i = c + i
        yield (arr[l_i], arr[r_i])


def rst_bar():
    for b in bars:
        for i in b:
            led[i] = (0, 0, 0)


def r_w_b():
    i = random.randint(0, 2)
    if i == 0:  # white
        r = 255
        g = 255
        b = 255
    if i == 1:  # red
        r = 255
        g = 0
        b = 0
    if i == 2:  # blue
        r = 0
        g = 0
        b = 255
    return r, g, b


async def frwk(duration):
    global exit_set_hdw_async
    st = time.monotonic()
    led.brightness = 1.0

    
    bar_f = []

    if len(bars) > 0:
        # choose which bar or more to fire
        for i, arr in enumerate(bars):
            if i == random.randint(0, (len(bars)-1)):
                bar_f.append(i)
        # always fire at least one bar
        if len(bar_f) == 0:
            i == random.randint(0, (len(bars)-1))
            bar_f.append(i)

    for bolt in bolts:
        r, g, b = r_w_b()
        for bolt_index in bolt:
            led[bolt_index] = (r, g, b)

    for nbolt in nbolts:
        for nbolt_index in nbolt:
            r, g, b = r_w_b()
            led[nbolt_index] = (r, g, b)

    # Burst from center
    ext = False
    while not ext:
        for i in bar_f:
            r, g, b = r_w_b()
            fs = fwrk_sprd(bars[i])
            for left, right in fs:
                rst_bar()
                led[left] = (r, g, b)
                led[right] = (r, g, b)
                led.show()
                upd_vol(0.1)
                te = time.monotonic()-st
                if te > duration:
                    rst_bar()
                    led.show()
                    break
            led.show()
            te = time.monotonic()-st
            if te > duration:
                rst_bar()
                led.show()
                break
        te = time.monotonic()-st
        if exit_set_hdw_async:
            return
        if te > duration:
            rst_bar()
            led.show()
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


def col_it(col, var):
    col = int(col)
    var = int(var)
    l = int(bnd(col-var/100*col, 0, 255))
    h = int(bnd(col+var/100*col, 0, 255))
    return random.randint(l, h)


def ltng():
    global exit_set_hdw_async
    # choose which bolt or no bolt to fire
    bolt = []
    b_i = random.randint(-1, (len(bolts)-1))
    if b_i != -1:
        for i, arr in enumerate(bolts):
            if i == b_i:
                bolt.extend(arr)

    # choose which nbolt or no bolt to fire
    nbolt = []
    b_i = random.randint(-1, (len(nbolts)-1))
    if b_i != -1:
        for i, arr in enumerate(nbolts):
            if i == b_i:
                nbolt.extend(arr)

    # choose which bar one to all to fire
    bar = []
    for i, arr in enumerate(bars):
        if i == random.randint(0, (len(bars)-1)):
            bar.extend(arr)

    # choose which nood or no nood to fire
    nood = []
    nood_i = random.randint(-1, (len(noods)-1))
    if nood_i != -1:
        for i, arr in enumerate(noods):
            if i == nood_i:
                nood.extend(arr)

    if len(nood) > 0 and len(bolt) > 0:
        b_i = random.randint(0, 1)
        if b_i == 0:
            bolt = []
        else:
            nood = []

    # number of flashes
    f_num = random.randint(5, 10)

    if len(nood) > 0:
        if nood[1] == 1:
            l1 = 1
            l2 = 0
            l3 = 0
        if nood[1] == 2:
            l1 = random.randint(0, 1)
            l2 = 0
            l3 = random.randint(0, 1)
        if nood[1] == 3:
            l1 = random.randint(0, 1)
            l2 = random.randint(0, 1)
            l3 = random.randint(0, 1)

    for i in range(0, f_num):
        if exit_set_hdw_async:
            return
        # set bolt base color
        bolt_r = col_it(cfg["bolts"]["r"], cfg["v"]["r1"])
        bolt_g = col_it(cfg["bolts"]["g"], cfg["v"]["g1"])
        bolt_b = col_it(cfg["bolts"]["b"], cfg["v"]["b1"])

        # set bar base color
        bar_r = col_it(cfg["bars"]["r"], cfg["v"]["r2"])
        bar_g = col_it(cfg["bars"]["g"], cfg["v"]["g2"])
        bar_b = col_it(cfg["bars"]["b"], cfg["v"]["b2"])

        led.brightness = random.randint(150, 255) / 255
        for _ in range(4):
            if exit_set_hdw_async:
                return
            if len(nood) > 0:
                led[nood[0]] = (
                    (255)*l2, (255)*l1, (255)*l3)
            for j in bolt:
                led[j] = (
                    bolt_r, bolt_g, bolt_b)
            for j in nbolt:
                led[j] = (
                    bolt_r, bolt_g, bolt_b)
            for j in bar:
                led[j] = (
                    bar_r, bar_g, bar_b)
            led.show()
            dly = random.randint(0, 75)  # flash offset range - ms
            dly = dly/1000
            time.sleep(dly)
            led.fill((0, 0, 0))
            led.show()

        dly = random.randint(1, 50)  # time to next flash range - ms
        dly = dly/1000
        time.sleep(dly)
        led.fill((0, 0, 0))
        led.show()


def bnd(cd, l, u):
    if (cd < l):
        cd = l
    if (cd > u):
        cd = u
    return cd

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
        global cont_run, is_running_an
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
        ply_a_1("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_1("/sd/mvc/" + m_mnu[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(m_mnu)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = m_mnu[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "light_string_setup_menu":
                mch.go_to('light_string_setup_menu')
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
                    w1 = audiocore.WaveFile(open(
                        "/sd/snd_opt/option_" + mnu_o[self.i] + ".wav", "rb"))
                    mix.voice[1].play(w1, loop=False)
                except Exception as e:
                    files.log_item(e)
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(mnu_o)-1:
                    self.i = 0
                while mix.voice[1].playing:
                    pass
        if sw == "right":
            if mix.voice[1].playing:
                mix.voice[1].stop()
                while mix.voice[1].playing:
                    pass
            else:
                cfg["option_selected"] = mnu_o[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                w1 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[1].play(w1, loop=False)
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

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, mch):
        files.log_item('Set Web Options')
        ply_a_1("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_1("/sd/mvc/" + v_s[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(v_s)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = v_s[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                ply_a_1("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    sw = utilities.switch_state(
                        l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
                    if sw == "left":
                        ch_vol("lower")
                    elif sw == "right":
                        ch_vol("raise")
                    elif sw == "right_held":
                        files.write_json_file(
                            "/sd/cfg.json", cfg)
                        ply_a_1("/sd/mvc/all_changes_complete.wav")
                        done = True
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_1("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_1("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Light(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0
        self.li = 0
        self.sel_li = 0
        self.a = False

    @property
    def name(self):
        return 'light_string_setup_menu'

    def enter(self, mch):
        files.log_item('Light string menu')
        ply_a_1("/sd/mvc/light_string_setup_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if self.a:
            if sw == "left":
                self.li -= 1
                if self.li < 0:
                    self.li = len(l_opt)-1
                self.sel_li = self.li
                ply_a_1("/sd/mvc/" + l_opt[self.li] + ".wav")
            elif sw == "right":
                self.li += 1
                if self.li > len(l_opt)-1:
                    self.li = 0
                self.sel_li = self.li
                ply_a_1("/sd/mvc/" + l_opt[self.li] + ".wav")
            elif sw == "left_held":
                files.write_json_file("/sd/cfg.json", cfg)
                upd_l_str()
                ply_a_1("/sd/mvc/all_changes_complete.wav")
                self.a = False
                mch.go_to('base_state')
            elif sw == "right_held":
                if cfg["light_string"] == "":
                    cfg["light_string"] = l_opt[self.sel_li]
                else:
                    cfg["light_string"] = cfg["light_string"] + \
                        "," + l_opt[self.sel_li]
                ply_a_1("/sd/mvc/" +
                        l_opt[self.sel_li] + ".wav")
                ply_a_1("/sd/mvc/added.wav")
            upd_vol(0.1)
        elif sw == "left":
            ply_a_1("/sd/mvc/" + l_mnu[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(l_mnu)-1:
                self.i = 0
        elif sw == "right":
            sel_mnu = l_mnu[self.sel_i]
            if sel_mnu == "hear_light_setup_instructions":
                ply_a_1("/sd/mvc/string_instructions.wav")
            elif sel_mnu == "reset_lights_defaults":
                rst_l_def()
                ply_a_1("/sd/mvc/lights_reset_to.wav")
                spk_lght(False)
            elif sel_mnu == "hear_current_light_settings":
                spk_lght(True)
            elif sel_mnu == "clear_light_string":
                cfg["light_string"] = ""
                ply_a_1("/sd/mvc/lights_cleared.wav")
            elif sel_mnu == "add_lights":
                ply_a_1("/sd/mvc/add_light_menu.wav")
                self.a = True
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_1("/sd/mvc/all_changes_complete.wav")
                upd_l_str()
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
st_mch.add(Light())
st_mch.add(WebOpt())

aud_mute.value = False

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        led[1] = (0, 255, 0)
        led.show()
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        spk_web()
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()
else:
    led[1] = (0, 255, 0)
    led.show()
    time.sleep(1.5)

upd_l_str()

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
