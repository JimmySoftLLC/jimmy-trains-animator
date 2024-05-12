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


def gc_col(c_p):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + c_p +
                   " Available memory: {} bytes".format(start_mem))


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")

################################################################################
# Setup hardware

# Setup pin for v
a_in = AnalogIn(board.A0)

# setup pin for audio enable
# 22 animator tiny, #28 standard size
aud_en = digitalio.DigitalInOut(board.GP28)
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
except:
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
            except:
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass

aud_en.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

cfg = files.read_json_file("/sd/cfg.json")

s_o = files.return_directory("", "/sd/snd", ".wav")

c_s_o = files.return_directory(
    "customers_owned_music_", "/sd/customers_owned_music", ".wav")

a_s_o = []
a_s_o.extend(s_o)
a_s_o.extend(c_s_o)

m_s_o = []
m_s_o.extend(s_o)
rnd_opt = ['random all', 'random built in', 'random my']
m_s_o.extend(rnd_opt)
m_s_o.extend(c_s_o)

t_s_j = files.return_directory(
    "", "/sd/t_s_def", ".json")

web = cfg["serve_webpage"]

c_m = files.read_json_file("/sd/mvc/main_menu.json")
m_mu = c_m["main_menu"]

c_w = files.read_json_file("/sd/mvc/web_menu.json")
w_mu = c_w["web_menu"]

c_l = files.read_json_file(
    "/sd/mvc/light_string_menu.json")
l_mu = c_l["light_string_menu"]

c_l_o = files.read_json_file("/sd/mvc/light_options.json")
l_o = c_l_o["light_options"]

c_v = files.read_json_file("/sd/mvc/volume_settings.json")
v_s = c_v["volume_settings"]

c_a_s = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
a_s = c_a_s["add_sounds_animate"]

c_run = False
ts_mode = False

gc_col("config setup")

################################################################################
# Setup neo pixels
bars = []
bolts = []
nood = []

bar_arr = []
bolt_arr = []

n_px = 0

# 15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP10, n_px)


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


def l_tst():
    global bar_arr, bolt_arr
    bar_arr = bld_bar()
    bolt_arr = bld_bolt()
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
    for n in nood:
        led[n[0]] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()


def upd_l_str():
    global bars, bolts, nood, n_px, led
    bars = []
    bolts = []
    nood = []

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
                nood.append(s)
                n_px += 1
            elif typ == 'bolt' and qty == 4:
                s = list(range(n_px, n_px + qty))
                bolts.append(s)
                n_px += qty

    led.deinit()
    gc_col("Deinit ledStrip")
    # 15 on demo 17 tiny 10 on large
    led = neopixel.NeoPixel(board.GP10, n_px)
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
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
    gc_col("config wifi imports")

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    SSID = "jimmytrainsguest"
    PASS = ""

    try:
        env = files.read_json_file("/sd/env.json")
        SSID = env["WIFI_SSID"]
        PASS = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid")
    except:
        print("Using default ssid")

    try:
        # connect to your SSID
        wifi.radio.connect(SSID, PASS)
        gc_col("wifi connect")

        # setup mdns server
        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(
            service_type="_http", protocol="_tcp", port=80)

        # files.log_items IP address to REPL
        files.log_item("IP is" + str(wifi.radio.ipv4_address))
        files.log_item("Connected")

        # set up server
        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)

        gc_col("wifi server")

        ################################################################################
        # Setup routes

        @server.route("/")
        def base(req: HTTPRequest):
            gc_col("Home page.")
            return FileResponse(req, "index.html", "/")

        @server.route("/mui.min.css")
        def base(req: HTTPRequest):
            return FileResponse(req, "mui.min.css", "/")

        @server.route("/mui.min.js")
        def base(req: HTTPRequest):
            return FileResponse(req, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def btn(req: Request):
            global cfg, c_run, ts_mode
            rq_d = req.json()
            cfg["option_selected"] = rq_d["an"]
            an(cfg["option_selected"])
            files.write_json_file("/sd/cfg.json", cfg)
            return Response(req, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def btn(req: Request):
            global cfg
            rq_d = req.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for ts_fn in t_s_j:
                    ts = files.read_json_file(
                        "/sd/t_s_def/" + ts_fn + ".json")
                    files.write_json_file(
                        "/sd/snd/"+ts_fn+".json", ts)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif rq_d["an"] == "reset_to_defaults":
                rst_def()
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to_state('base_state')
            elif rq_d["an"] == "reset_incandescent_colors":
                rst_def_col()
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                s = files.json_stringify(
                    {"bars": cfg["bars"], "bolts": cfg["bolts"], "v": cfg["v"]})
                st_mch.go_to_state('base_state')
                return Response(req, s)
            elif rq_d["an"] == "reset_white_colors":
                rst_wht_col()
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                s = files.json_stringify(
                    {"bars": cfg["bars"], "bolts": cfg["bolts"], "v": cfg["v"]})
                st_mch.go_to_state('base_state')
                return Response(req, s)
            return Response(req, "Utility: " + rq_d["an"])

        @server.route("/mode", [POST])
        def btn(req: Request):
            global cfg, c_run, ts_mode
            rq_d = req.json()
            if rq_d["an"] == "cont_mode_on":
                c_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
            elif rq_d["an"] == "cont_mode_off":
                c_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif rq_d["an"] == "timestamp_mode_on":
                ts_mode = True
                ply_a_0("/sd/mvc/timestamp_mode_on.wav")
                ply_a_0("/sd/mvc/timestamp_instructions.wav")
            elif rq_d["an"] == "timestamp_mode_off":
                ts_mode = False
                ply_a_0("/sd/mvc/timestamp_mode_off.wav")
            return Response(req, "Utility: " + rq_d["an"])

        @server.route("/speaker", [POST])
        def btn(req: Request):
            global cfg
            rq_d = req.json()
            if rq_d["an"] == "speaker_test":
                ply_a_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif rq_d["an"] == "volume_pot_off":
                cfg["volume_pot"] = False
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif rq_d["an"] == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(req, "Utility: " +  rq_d["an"])

        @server.route("/lights", [POST])
        def btn(req: Request):
            rq_d = req.json()
            v = rq_d["an"].split(",")
            led.fill((float(v[0]), float(v[1]), float(v[2])))
            led.show()
            return Response(req, "OK")
        
        @server.route("/bolt", [POST])
        def btn(req: Request):
            led.fill((int(cfg["bolts"]["r"]), int(cfg["bolts"]["g"]), int(cfg["bolts"]["b"])))
            led.show()
            return Response(req, "OK")
        
        @server.route("/bar", [POST])
        def btn(req: Request):
            led.fill((int(cfg["bars"]["r"]), int(cfg["bars"]["g"]), int(cfg["bars"]["b"])))
            led.show()
            return Response(req, "OK")
        
        @server.route("/bright", [POST])
        def btn(req: Request):
            rq_d = req.json()
            led.brightness = float(rq_d["an"])
            led.show()
            return Response(req, "OK")

        @server.route("/update-host-name", [POST])
        def btn(req: Request):
            global cfg
            rq_d = req.json()
            cfg["HOST_NAME"] = rq_d["text"]
            files.write_json_file("/sd/cfg.json", cfg)
            mdns_server.hostname = cfg["HOST_NAME"]
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
            return Response(req, cfg["volume"])

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
                ply_a_0("/sd/mvc/all_changes_complete.wav")
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
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(req, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def btn(req: Request):
            return Response(req, cfg["light_string"])

        @server.route("/get-customers-sound-tracks", [POST])
        def btn(req: Request):
            s = files.json_stringify(c_s_o)
            return Response(req, s)

        @server.route("/get-built-in-sound-tracks", [POST])
        def btn(req: Request):
            s = []
            s.extend(s_o)
            s = files.json_stringify(s)
            return Response(req, s)

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

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")

################################################################################
# Global Methods


def rst_l_def():
    global cfg
    cfg["light_string"] = "bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4"


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
        time.sleep(s)
    else:
        try:
            v = int(cfg["volume"]) / 100
        except:
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        time.sleep(s)


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
    files.write_json_file("/sd/cfg.json", cfg)
    ply_a_0("/sd/mvc/volume.wav")
    spk_str(cfg["volume"], False)


def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.02)
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(wave0, loop=False)
    while mix.voice[0].playing:
        exit_early()


def stp_a_0():
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
            ply_a_0("/sd/mvc/" + character + ".wav")
        except:
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")


def l_r_but():
    ply_a_0("/sd/mvc/press_left_button_right_button.wav")


def sel_web():
    ply_a_0("/sd/mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    ply_a_0("/sd/mvc/option_selected.wav")


def spk_sng_num(song_number):
    ply_a_0("/sd/mvc/song.wav")
    spk_str(song_number, False)


def spk_lght(play_intro):
    try:
        elements = cfg["light_string"].split(',')
        if play_intro:
            ply_a_0("/sd/mvc/current_light_settings_are.wav")
        for index, element in enumerate(elements):
            ply_a_0("/sd/mvc/position.wav")
            ply_a_0("/sd/mvc/" + str(index+1) + ".wav")
            ply_a_0("/sd/mvc/is.wav")
            ply_a_0("/sd/mvc/" + element + ".wav")
    except:
        ply_a_0("/sd/mvc/no_lights_in_light_string.wav")
        return


def no_trk():
    ply_a_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            ply_a_0("/sd/mvc/create_sound_track_files.wav")
            break


def spk_web():
    ply_a_0("/sd/mvc/animator_available_on_network.wav")
    ply_a_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-lightning":
        ply_a_0("/sd/mvc/animator_dash_lightning.wav")
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/sd/mvc/in_your_browser.wav")

################################################################################
# animations


l_o = ""


def an(fn):
    global cfg, l_o
    print("Filename: " + fn)
    c_o = fn
    try:
        if fn == "random built in":
            hi = len(s_o) - 1
            c_o = s_o[random.randint(
                0, hi)]
            while l_o == c_o and len(s_o) > 1:
                c_o = s_o[random.randint(
                    0, hi)]
            l_o = c_o
        elif fn == "random my":
            hi = len(c_s_o) - 1
            c_o = c_s_o[random.randint(
                0, hi)]
            while l_o == c_o and len(c_s_o) > 1:
                c_o = c_s_o[random.randint(
                    0, hi)]
            l_o = c_o
        elif fn == "random all":
            hi = len(a_s_o) - 1
            c_o = a_s_o[random.randint(
                0, hi)]
            while l_o == c_o and len(a_s_o) > 1:
                c_o = a_s_o[random.randint(
                    0, hi)]
            l_o = c_o
        if ts_mode:
            ts(c_o)
        else:
            if "customers_owned_music_" in c_o:
                an_ls(c_o)
            elif c_o == "alien lightshow":
                an_ls(c_o)
            elif c_o == "inspiring cinematic ambient lightshow":
                an_ls(c_o)
            elif c_o == "fireworks":
                an_ls(c_o)
            else:
                t_l(c_o)
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")


def an_ls(fn):
    global ts_mode
    il = 1
    ih = 3

    if fn == "fireworks":
        il = 4
        ih = 4

    cf = "customers_owned_music_" in fn

    if cf:
        fn = fn.replace("customers_owned_music_", "")
        try:
            fls_t = files.read_json_file(
                "/sd/customers_owned_music/" + fn + ".json")
        except:
            ply_a_0("/sd/mvc/no_timestamp_file_found.wav")
            while True:
                l_sw.update()
                r_sw.update()
                if l_sw.fell:
                    ts_mode = False
                    return
                if r_sw.fell:
                    ts_mode = True
                    ply_a_0("/sd/mvc/timestamp_instructions.wav")
                    return
    else:
        fls_t = files.read_json_file(
            "/sd/snd/" + fn + ".json")
    ft = fls_t["flashTime"]

    ftl = len(ft)
    fti = 0

    if cf:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/snd/" + fn + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    st = time.monotonic()
    i = 0

    mlt_c(.01)
    while True:
        pi = 0
        te = time.monotonic()-st
        if fti < len(ft)-2:
            d = ft[fti+1] - \
                ft[fti]-0.25
        else:
            d = 0.25
        if d < 0:
            d = 0
        if te > ft[fti] - 0.25:
            print("Time elapsed: " + str(te) + " Timestamp: " +
                  str(ft[fti]) + " Dif: " + str(te-ft[fti]))
            fti += 1
            i = random.randint(il, ih)
            while i == pi:
                i = random.randint(il, ih)
            if i == 1:
                rainbow(.005, d)
            elif i == 2:
                mlt_c(.01)
                upd_vol(d)
            elif i == 3:
                candle(d)
            elif i == 4:
                fwrk(d)
            pi = i
        if ftl == fti:
            fti = 0
        l_sw.update()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            break
        upd_vol(.001)


def ts(fn):
    print("Time stamp mode:")
    global ts_mode

    cf = "customers_owned_music_" in fn

    ts = files.read_json_file(
        "/sd/t_s_def/timestamp mode.json")
    ts["flashTime"] = []

    fn = fn.replace("customers_owned_music_", "")

    if cf:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/snd/" + fn + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)

    st = time.monotonic()
    upd_vol(.1)

    while True:
        te = time.monotonic()-st
        r_sw.update()
        if r_sw.fell:
            ts["flashTime"].append(te)
            print(te)
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            ts["flashTime"].append(5000)
            if cf:
                files.write_json_file(
                    "/sd/customers_owned_music/" + fn + ".json", ts)
            else:
                files.write_json_file(
                    "/sd/snd/" + fn + ".json", ts)
            break

    ts_mode = False
    ply_a_0("/sd/mvc/timestamp_saved.wav")
    ply_a_0("/sd/mvc/timestamp_mode_off.wav")
    ply_a_0("/sd/mvc/animations_are_now_active.wav")


def t_l(file_name):

    ftd = files.read_json_file(
        "/sd/snd/" + file_name + ".json")

    ft = ftd["flashTime"]

    ftl = len(ft)
    fti = 0

    w0 = audiocore.WaveFile(
        open("/sd/snd/" + file_name + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    st = time.monotonic()

    while True:
        upd_vol(.1)
        te = time.monotonic()-st
        # amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
        rt = ft[fti] - random.uniform(.5, 1)
        if te > rt:
            print("Time elapsed: " + str(te) + " Timestamp: " +
                  str(rt) + " Dif: " + str(te-rt))
            fti += 1
            ltng()
        if ftl == fti:
            fti = 0
        l_sw.update()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            break

##############################
# Led color effects


def rainbow(spd, dur):
    startTime = time.monotonic()
    for j in range(0, 255, 1):
        for i in range(n_px):
            pi = (i * 256 // n_px) + j
            led[i] = colorwheel(pi & 255)
        led.show()
        upd_vol(spd)
        te = time.monotonic()-startTime
        if te > dur:
            return
    for j in reversed(range(0, 255, 1)):
        for i in range(n_px):
            pi = (i * 256 // n_px) + j
            led[i] = colorwheel(pi & 255)
        led.show()
        upd_vol(spd)
        te = time.monotonic()-startTime
        if te > dur:
            return


def candle(dur):
    st = time.monotonic()
    led.brightness = 1.0

    bari = []
    bari.extend(bar_arr)

    bolti = []
    bolti.extend(bolt_arr)

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
    center = len(arr) // 2
    for i in range(center):
        left_index = center - 1 - i
        right_index = center + i
        yield (arr[left_index], arr[right_index])


def rst_bar():
    for bar in bars:
        for i in bar:
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


def fwrk(duration):
    st = time.monotonic()
    led.brightness = 1.0

    # choose which bar none to all to fire
    bar_f = []
    for index, my_array in enumerate(bars):
        if index == random.randint(0, (len(bars)-1)):
            bar_f.append(index)

    if len(bar_f) == 0:
        index == random.randint(0, (len(bars)-1))
        bar_f.append(index)

    for bolt in bolts:
        r, g, b = r_w_b()
        for i in bolt:
            led[i] = (r, g, b)

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
        if te > duration:
            rst_bar()
            led.show()
            return


def mlt_c(duration):
    startTime = time.monotonic()
    led.brightness = 1.0

    # Flicker, based on our initial RGB values
    while True:
        for i in range(0, n_px):
            red = random.randint(128, 255)
            green = random.randint(128, 255)
            blue = random.randint(128, 255)
            whichColor = random.randint(0, 2)
            if whichColor == 0:
                r1 = red
                g1 = 0
                b1 = 0
            elif whichColor == 1:
                r1 = 0
                g1 = green
                b1 = 0
            elif whichColor == 2:
                r1 = 0
                g1 = 0
                b1 = blue
            led[i] = (r1, g1, b1)
            led.show()
        upd_vol(random.uniform(.2, 0.3))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return


def col_it(col, var):
    col = int(col)
    var = int(var)
    low = int(bnd(col-var/100*col,0,255))
    high = int(bnd(col+var/100*col,0,255))
    return random.randint(low, high)


def ltng():
    # choose which bolt or no bolt to fire
    bolt_indexes = []
    which_bolt = random.randint(-1, (len(bolts)-1))
    if which_bolt != -1:
        for index, my_array in enumerate(bolts):
            if index == which_bolt:
                bolt_indexes.extend(my_array)

    # choose which bar one to all to fire
    bar_indexes = []
    for index, my_array in enumerate(bars):
        if index == random.randint(0, (len(bars)-1)):
            bar_indexes.extend(my_array)

    # choose which nood or no nood to fire
    nood_indexes = []
    which_nood = random.randint(-1, (len(nood)-1))
    if which_nood != -1:
        for index, my_array in enumerate(nood):
            if index == which_nood:
                nood_indexes.extend(my_array)

    if len(nood_indexes) > 0 and len(bolt_indexes) > 0:
        which_bolt = random.randint(0, 1)
        if which_bolt == 0:
            bolt_indexes = []
        else:
            nood_indexes = []

    # number of flashes
    flashCount = random.randint(5, 10)

    if len(nood_indexes) > 0:
        if nood_indexes[1] == 1:
            l1 = 1
            l2 = 0
            l3 = 0
        if nood_indexes[1] == 2:
            l1 = random.randint(0, 1)
            l2 = 0
            l3 = random.randint(0, 1)
        if nood_indexes[1] == 3:
            l1 = random.randint(0, 1)
            l2 = random.randint(0, 1)
            l3 = random.randint(0, 1)

    for i in range(0, flashCount):
        # set bolt base color
        bolt_r = col_it(cfg["bolts"]["r"], cfg["v"]["r1"])
        bolt_g = col_it(cfg["bolts"]["g"], cfg["v"]["g1"])
        bolt_b = col_it(cfg["bolts"]["b"], cfg["v"]["b1"])

        # set bar base color
        bar_r = col_it(cfg["bars"]["r"], cfg["v"]["r2"])
        bar_g = col_it(cfg["bars"]["g"], cfg["v"]["g2"])
        bar_b = col_it(cfg["bars"]["b"], cfg["v"]["b2"])

        led.brightness = random.randint(150, 255) / 255
        for j in range(4):
            if len(nood_indexes) > 0:
                led[nood_indexes[0]] = (
                    (255)*l2, (255)*l1, (255)*l3)
            for led_index in bolt_indexes:
                led[led_index] = (
                    bolt_r, bolt_g, bolt_b)
            for led_index in bar_indexes:
                led[led_index] = (
                    bar_r, bar_g, bar_b)
            led.show()
            delay = random.randint(0, 75)  # flash offset range - ms
            delay = delay/1000
            time.sleep(delay)
            led.fill((0, 0, 0))
            led.show()

        delay = random.randint(1, 50)  # time to next flash range - ms
        delay = delay/1000
        time.sleep(delay)
        led.fill((0, 0, 0))
        led.show()


def bnd(my_color, lower, upper):
    if (my_color < lower):
        my_color = lower
    if (my_color > upper):
        my_color = upper
    return my_color

################################################################################
# State Machine


class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def update(self):
        if self.state:
            self.state.update(self)

    # When pausing, don't exit the state
    def pause(self):
        self.state = self.states['paused']
        self.state.enter(self)

    # When resuming, don't re-enter the state
    def resume_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]

    def reset(self):
        rst()

################################################################################
# States

# Abstract parent state class.


class State(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        pass


class BaseState(State):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, machine):
        ply_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global c_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if c_run:
                c_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                c_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or c_run:
            an(cfg["option_selected"])
        elif switch_state == "right":
            machine.go_to_state('main_menu')


class MainMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, machine):
        ply_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + m_mu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(m_mu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = m_mu[self.selectedMenuIndex]
            if selected_menu_item == "choose_sounds":
                machine.go_to_state('choose_sounds')
            elif selected_menu_item == "add_sounds_animate":
                machine.go_to_state('add_sounds_animate')
            elif selected_menu_item == "light_string_setup_menu":
                machine.go_to_state('light_string_setup_menu')
            elif selected_menu_item == "web_options":
                machine.go_to_state('web_options')
            elif selected_menu_item == "volume_settings":
                machine.go_to_state('volume_settings')
            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class ChooseSounds(State):

    def __init__(self):
        self.optionIndex = 0
        self.currentOption = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        ply_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    wave0 = audiocore.WaveFile(open(
                        "/sd/snd_opt/option_" + m_s_o[self.optionIndex] + ".wav", "rb"))
                    mix.voice[0].play(wave0, loop=False)
                except:
                    spk_sng_num(str(self.optionIndex+1))
                self.currentOption = self.optionIndex
                self.optionIndex += 1
                if self.optionIndex > len(m_s_o)-1:
                    self.optionIndex = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = m_s_o[self.currentOption]
                files.write_json_file("/sd/cfg.json", cfg)
                wave0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play(wave0, loop=False)
                while mix.voice[0].playing:
                    pass
            machine.go_to_state('base_state')

# class AddSoundsAnimate(State):

#     def __init__(self):
#         self.menuIndex = 0
#         self.selectedMenuIndex = 0

#     @property
#     def name(self):
#         return 'add_sounds_animate'

#     def enter(self, machine):
#         files.log_item('Add sounds animate')
#         play_audio_0("/sd/mvc/add_sounds_animate.wav")
#         left_right_mouse_button()
#         State.enter(self, machine)

#     def exit(self, machine):
#         State.exit(self, machine)

#     def update(self, machine):
#         global time_stamp_mode
#         l_sw.update()
#         right_switch.update()
#         if l_sw.fell:
#             play_audio_0("/sd/mvc/" + add_sounds_animate[self.menuIndex] + ".wav")
#             self.selectedMenuIndex = self.menuIndex
#             self.menuIndex +=1
#             if self.menuIndex > len(add_sounds_animate)-1:
#                 self.menuIndex = 0
#         if right_switch.fell:
#             if mixer.voice[0].playing:
#                 mixer.voice[0].stop()
#                 while mixer.voice[0].playing:
#                     pass
#             else:
#                 selected_menu_item = add_sounds_animate[self.selectedMenuIndex]
#                 if selected_menu_item == "hear_instructions":
#                     play_audio_0("/sd/mvc/create_sound_track_files.wav")
#                 elif selected_menu_item == "timestamp_mode_on":
#                     time_stamp_mode = True
#                     play_audio_0("/sd/mvc/timestamp_mode_on.wav")
#                     play_audio_0("/sd/mvc/timestamp_instructions.wav")
#                     machine.go_to_state('base_state')
#                 elif selected_menu_item == "timestamp_mode_off":
#                     time_stamp_mode = False
#                     play_audio_0("/sd/mvc/timestamp_mode_off.wav")

#                 else:
#                     play_audio_0("/sd/mvc/all_changes_complete.wav")
#                     machine.go_to_state('base_state')


class VolumeSettings(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, machine):
        files.log_item('Set Web Options')
        ply_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + v_s[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(v_s)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = v_s[self.selectedMenuIndex]
            if selected_menu_item == "volume_level_adjustment":
                ply_a_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        ch_vol("lower")
                    elif switch_state == "right":
                        ch_vol("raise")
                    elif switch_state == "right_held":
                        files.write_json_file("/sd/cfg.json", cfg)
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        machine.go_to_state('base_state')
                    upd_vol(0.1)
                    pass
            elif selected_menu_item == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
            elif selected_menu_item == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class WebOptions(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'web_options'

    def enter(self, machine):
        files.log_item('Set Web Options')
        sel_web()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + w_mu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(w_mu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = w_mu[self.selectedMenuIndex]
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
                ply_a_0("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class LightStringSetupMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'light_string_setup_menu'

    def enter(self, machine):
        files.log_item('Light string menu')
        ply_a_0("/sd/mvc/light_string_setup_menu.wav")
        l_r_but()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + l_mu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(l_mu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = l_mu[self.selectedMenuIndex]
            if selected_menu_item == "hear_light_setup_instructions":
                ply_a_0("/sd/mvc/string_instructions.wav")
            elif selected_menu_item == "reset_lights_defaults":
                rst_l_def()
                ply_a_0("/sd/mvc/lights_reset_to.wav")
                spk_lght(False)
            elif selected_menu_item == "hear_current_light_settings":
                spk_lght(True)
            elif selected_menu_item == "clear_light_string":
                cfg["light_string"] = ""
                ply_a_0("/sd/mvc/lights_cleared.wav")
            elif selected_menu_item == "add_lights":
                ply_a_0("/sd/mvc/add_light_menu.wav")
                adding = True
                while adding:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        self.menuIndex -= 1
                        if self.menuIndex < 0:
                            self.menuIndex = len(l_o)-1
                        self.selectedMenuIndex = self.menuIndex
                        ply_a_0("/sd/mvc/" +
                                l_o[self.menuIndex] + ".wav")
                    elif switch_state == "right":
                        self.menuIndex += 1
                        if self.menuIndex > len(l_o)-1:
                            self.menuIndex = 0
                        self.selectedMenuIndex = self.menuIndex
                        ply_a_0("/sd/mvc/" +
                                l_o[self.menuIndex] + ".wav")
                    elif switch_state == "right_held":
                        if cfg["light_string"] == "":
                            cfg["light_string"] = l_o[self.selectedMenuIndex]
                        else:
                            cfg["light_string"] = cfg["light_string"] + \
                                "," + l_o[self.selectedMenuIndex]
                        ply_a_0("/sd/mvc/" +
                                l_o[self.selectedMenuIndex] + ".wav")
                        ply_a_0("/sd/mvc/added.wav")
                    elif switch_state == "left_held":
                        files.write_json_file("/sd/cfg.json", cfg)
                        upd_l_str()
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        adding = False
                        machine.go_to_state('base_state')
                    upd_vol(0.1)
                    pass
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                upd_l_str()
                machine.go_to_state('base_state')

###############################################################################
# Create the state machine


st_mch = StateMachine()
st_mch.add_state(BaseState())
st_mch.add_state(MainMenu())
st_mch.add_state(ChooseSounds())
# state_machine.add_state(AddSoundsAnimate())
st_mch.add_state(VolumeSettings())
st_mch.add_state(WebOptions())
st_mch.add_state(LightStringSetupMenu())

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
        rst()

st_mch.go_to_state('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.update()
    upd_vol(.02)
    if (web):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue


