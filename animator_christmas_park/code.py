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


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")
################################################################################
# Setup hardware
a_in = AnalogIn(board.A0)

# setup pin for audio enable 22 on tiny 28 on large
au_en = digitalio.DigitalInOut(board.GP28)
au_en.direction = digitalio.Direction.OUTPUT
au_en.value = False

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
au_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=4096)
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

au_en.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

cfg = files.read_json_file("/sd/config_christmas_park.json")

snd_o = files.return_directory("", "/sd/christmas_park_sounds", ".wav")

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

ts_json = files.return_directory("", "/sd/time_stamp_defaults", ".json")

web = cfg["serve_webpage"]

c_m = files.read_json_file("/sd/mvc/main_menu.json")
m_mnu = c_m["main_menu"]

c_w = files.read_json_file("/sd/mvc/web_menu.json")
w_mnu = c_w["web_menu"]

c_l = files.read_json_file("/sd/mvc/light_string_menu.json")
l_mnu = c_l["light_string_menu"]

c_l_o = files.read_json_file("/sd/mvc/light_options.json")
l_opt = c_l_o["light_options"]

c_v = files.read_json_file("/sd/mvc/volume_settings.json")
v_set = c_v["volume_settings"]

a_s = files.read_json_file("/sd/mvc/add_sounds_animate.json")
add_s = a_s["add_sounds_animate"]

gc_col("config setup")

c_run = False
ts_mode = False

################################################################################
# Setup neo pixels

trees = []
canes = []
ornmnts = []
stars = []
brnchs = []
cane_s = []
cane_e = []

n_px = 0

# 15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP10, n_px)


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


def show_l():
    led.show()
    time.sleep(.3)
    led.fill((0, 0, 0))
    led.show()


def l_tst():
    global ornmnts, stars, brnchs, cane_s, cane_e
    ornmnts = bld_tree("ornaments")
    stars = bld_tree("star")
    brnchs = bld_tree("branches")
    cane_s = bld_cane("start")
    cane_e = bld_cane("end")

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


def upd_l_str():
    global trees, canes, n_px, led
    trees = []
    canes = []

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

    print("Number of pixels total: ", n_px)
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
    PASSWORD = ""

    try:
        env = files.read_json_file("/sd/env.json")
        SSID = env["WIFI_SSID"]
        PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid")
    except:
        print("Using default ssid")

    try:
        # connect to your SSID
        wifi.radio.connect(SSID, PASSWORD)
        gc_col("wifi connect")

        # setup mdns server
        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(service_type="_http", protocol="_tcp", port=80)

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
            return FileResponse(req, "/sd/mui.min.css", "/")

        @server.route("/mui.min.js")
        def base(req: HTTPRequest):
            return FileResponse(req, "/sd/mui.min.js", "/")

        @server.route("/animation", [POST])
        def btn(req: Request):
            global cfg, c_run, ts_mode
            raw_text = req.raw_request.decode("utf8")
            if "customers_owned_music_" in raw_text:
                for sound_file in cus_o:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        an(cfg["option_selected"])
                        break
            else:  # built in animations
                for sound_file in mnu_o:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        an(cfg["option_selected"])
                        break
            files.write_json_file("/sd/config_christmas_park.json", cfg)
            return Response(req, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def btn(req: Request):
            global cfg
            command_sent = ""
            raw_text = req.raw_request.decode("utf8")
            if "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in ts_json:
                    time_stamps = files.read_json_file(
                        "/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file(
                        "/sd/christmas_park_sounds/"+time_stamp_file+".json", time_stamps)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to('base_state')
            return Response(req, "Utility: " + command_sent)

        @server.route("/mode", [POST])
        def btn(req: Request):
            global cfg, c_run, ts_mode
            command_sent = ""
            raw_text = req.raw_request.decode("utf8")
            if "cont_mode_on" in raw_text:
                c_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text:
                c_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif "timestamp_mode_on" in raw_text:
                ts_mode = True
                ply_a_0("/sd/mvc/timestamp_mode_on.wav")
                ply_a_0("/sd/mvc/timestamp_instructions.wav")
            elif "timestamp_mode_off" in raw_text:
                ts_mode = False
                ply_a_0("/sd/mvc/timestamp_mode_off.wav")
            return Response(req, "Utility: " + command_sent)

        @server.route("/speaker", [POST])
        def btn(req: Request):
            global cfg
            command_sent = ""
            raw_text = req.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                command_sent = "speaker_test"
                ply_a_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                command_sent = "volume_pot_off"
                cfg["volume_pot"] = False
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(req, "Utility: " + command_sent)

        @server.route("/lights", [POST])
        def btn(req: Request):
            global cfg
            command_sent = ""
            raw_text = req.raw_request.decode("utf8")
            if "set_to_red" in raw_text:
                led.fill((255, 0, 0))
                led.show()
            elif "set_to_green" in raw_text:
                led.fill((0, 255, 0))
                led.show()
            elif "set_to_blue" in raw_text:
                led.fill((0, 0, 255))
                led.show()
            elif "set_to_white" in raw_text:
                led.fill((255, 255, 255))
                led.show()
            elif "set_to_0" in raw_text:
                led.brightness = 0.0
                led.show()
            elif "set_to_20" in raw_text:
                led.brightness = 0.2
                led.show()
            elif "set_to_40" in raw_text:
                led.brightness = 0.4
                led.show()
            elif "set_to_60" in raw_text:
                led.brightness = 0.6
                led.show()
            elif "set_to_80" in raw_text:
                led.brightness = 0.8
                led.show()
            elif "set_to_100" in raw_text:
                led.brightness = 1.0
                led.show()
            return Response(req, "Utility: " + "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def btn(req: Request):
            global cfg
            data_object = req.json()
            cfg["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/config_christmas_park.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            spk_web()
            return Response(req, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def btn(req: Request):
            return Response(req, cfg["HOST_NAME"])

        @server.route("/update-volume", [POST])
        def btn(req: Request):
            global cfg
            data_object = req.json()
            ch_vol(data_object["action"])
            return Response(req, cfg["volume"])

        @server.route("/get-volume", [POST])
        def btn(req: Request):
            return Response(req, cfg["volume"])

        @server.route("/update-light-string", [POST])
        def btn(req: Request):
            global cfg
            data_object = req.json()
            if data_object["action"] == "save" or data_object["action"] == "clear" or data_object["action"] == "defaults":
                cfg["light_string"] = data_object["text"]
                print("action: " +
                      data_object["action"] + " data: " + cfg["light_string"])
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                upd_l_str()
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                return Response(req, cfg["light_string"])
            if cfg["light_string"] == "":
                cfg["light_string"] = data_object["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + \
                    "," + data_object["text"]
            print("action: " + data_object["action"] +
                  " data: " + cfg["light_string"])
            files.write_json_file("/sd/config_christmas_park.json", cfg)
            upd_l_str()
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(req, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def btn(req: Request):
            return Response(req, cfg["light_string"])

        @server.route("/get-customers-sound-tracks", [POST])
        def btn(req: Request):
            my_string = files.json_stringify(cus_o)
            return Response(req, my_string)

        @server.route("/get-built-in-sound-tracks", [POST])
        def btn(req: Request):
            sounds = []
            sounds.extend(snd_o)
            my_string = files.json_stringify(sounds)
            return Response(req, my_string)

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")


gc_col("utilities")

################################################################################
# Global Methods


def reset_lights_to_defaults():
    global cfg
    cfg["light_string"] = "cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21"


def reset_to_defaults():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-christmas-park"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"
    cfg["can_cancel"] = True
    reset_lights_to_defaults()


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
    if cfg["HOST_NAME"] == "animator-christmas-park":
        ply_a_0("/sd/mvc/animator_dash_christmas_dash_park.wav")
        ply_a_0("/sd/mvc/dot.wav")
        ply_a_0("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0("/sd/mvc/in_your_browser.wav")

################################################################################
# animations


def an(fn):
    global cfg
    print("Filename: " + fn)
    cur = fn
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
            ts(cur)
        else:
            an_ls(cur)
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
    if fn == "silent night":
        il = 3
        ih = 3
    if fn == "away in a manger":
        il = 3
        ih = 3

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
            "/sd/christmas_park_sounds/" + fn + ".json")
    ft = fls_t["flashTime"]

    ftl = len(ft)
    fti = 0

    if cf:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/christmas_park_sounds/" + fn + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    startTime = time.monotonic()
    i = 0

    mlt_c(.01)
    while True:
        pi = 0
        te = time.monotonic()-startTime
        if fti < len(ft)-2:
            d = ft[fti+1] - \
                ft[fti]-0.25
        else:
            d = 0.25
        if d < 0:
            d = 0
        if te > ft[fti] - 0.25:
            print("time elasped: " + str(te) +
                  " Timestamp: " + str(ft[fti]))
            fti += 1
            i = random.randint(il, ih)
            while i == pi:
                print("regenerating random selection")
                i = random.randint(il, ih)
            if i == 1:
                rainbow(.005, d)
            elif i == 2:
                mlt_c(.01)
                upd_vol(d)
            elif i == 3:
                fire(d)
            elif i == 4:
                c_fire(d)
            elif i == 5:
                mlt_c(d)
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
    print("time stamp mode")
    global ts_mode

    cf = "customers_owned_music_" in fn

    ts = files.read_json_file(
        "/sd/time_stamp_defaults/timestamp_mode.json")
    ts["flashTime"] = []

    fn = fn.replace("customers_owned_music_", "")

    if cf:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + fn + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/christmas_park_sounds/" + fn + ".wav", "rb"))
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
                    "/sd/christmas_park_sounds/" + fn + ".json", ts)
            break

    ts_mode = False
    ply_a_0("/sd/mvc/timestamp_saved.wav")
    ply_a_0("/sd/mvc/timestamp_mode_off.wav")
    ply_a_0("/sd/mvc/animations_are_now_active.wav")

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


def fire(dur):
    st = time.monotonic()
    led.brightness = 1.0

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

    print(len(firei))

    # Flicker, based on our initial RGB values
    while True:
        # for i in range (0, num_pixels):
        for i in firei:
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


def c_fire(dur):
    st = time.monotonic()
    led.brightness = 1.0

    # Flicker, based on our initial RGB values
    while True:
        for i in range(0, n_px):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            whichColor = random.randint(0, 1)
            if whichColor == 0:
                r1 = r
                g1 = 0
                b1 = 0
            elif whichColor == 1:
                r1 = 0
                g1 = g
                b1 = 0
            elif whichColor == 2:
                r1 = 0
                g1 = 0
                b1 = b
            led[i] = (r1, g1, b1)
            led.show()
        upd_vol(random.uniform(.2, 0.3))
        te = time.monotonic()-st
        if te > dur:
            return


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


def mlt_c(dur):
    st = time.monotonic()
    led.brightness = 1.0

    # Flicker, based on our initial RGB values
    while True:
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
        upd_vol(random.uniform(.2, 0.3))
        te = time.monotonic()-st
        if te > dur:
            return

################################################################################
# State Machine


class StMch(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add(self, state):
        self.states[state.name] = state

    def go_to(self, nm):
        if self.state:
            self.state.exit(self)
        self.state = self.states[nm]
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
        ply_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global c_run
        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
        if sw == "left_held":
            if c_run:
                c_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                c_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif sw == "left" or c_run:
            an(cfg["option_selected"])
        elif sw == "right":
            mch.go_to('main_menu')


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_1 = 0

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
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + m_mnu[self.i] + ".wav")
            self.sel_1 = self.i
            self.i += 1
            if self.i > len(m_mnu)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = m_mnu[self.sel_1]
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
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Snds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        ply_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, machine)

    def exit(self, machine):
        Ste.exit(self, machine)

    def upd(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    w0 = audiocore.WaveFile(open(
                        "/sd/christmas_park_options_voice_commands/option_" + mnu_o[self.i] + ".wav", "rb"))
                    mix.voice[0].play(w0, loop=False)
                except:
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(mnu_o)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = mnu_o[self.sel_i]
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                w0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass
            machine.go_to('base_state')


class AddSnds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'add_sounds_animate'

    def enter(self, mch):
        files.log_item('Add sounds animate')
        ply_a_0("/sd/mvc/add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + add_s[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_s)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = add_s[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_0("/sd/mvc/create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_0("/sd/mvc/timestamp_mode_on.wav")
                ply_a_0("/sd/mvc/timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_0("/sd/mvc/timestamp_mode_off.wav")

            else:
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class VolSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, machine):
        files.log_item('Set Web Options')
        ply_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        Ste.enter(self, machine)

    def exit(self, machine):
        Ste.exit(self, machine)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + v_set[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(v_set)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = v_set[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                ply_a_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    sw = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if sw == "left":
                        ch_vol("lower")
                    elif sw == "right":
                        ch_vol("raise")
                    elif sw == "right_held":
                        files.write_json_file(
                            "/sd/config_christmas_park.json", cfg)
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
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
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + w_mnu[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(w_mnu)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = w_mnu[self.sel_i]
            if sel_mnu == "web_on":
                cfg["serve_webpage"] = True
                opt_sel()
                sel_web()
            elif sel_mnu == "web_off":
                cfg["serve_webpage"] = False
                opt_sel()
                sel_web()
            elif sel_mnu == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            elif sel_mnu == "hear_instr_web":
                ply_a_0("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Light(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0
        self.li = 0
        self.sel_li = 0

    @property
    def name(self):
        return 'light_string_setup_menu'

    def enter(self, mch):
        files.log_item('Set Web Options')
        ply_a_0("/sd/mvc/light_string_setup_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + l_mnu[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(l_mnu)-1:
                self.i = 0
        if r_sw.fell:
            sel_i = l_mnu[self.sel_i]
            if sel_i == "hear_light_setup_instructions":
                ply_a_0("/sd/mvc/park_string_instructions.wav")
            elif sel_i == "reset_lights_defaults":
                reset_lights_to_defaults()
                ply_a_0("/sd/mvc/lights_reset_to.wav")
                spk_lght(False)
            elif sel_i == "hear_current_light_settings":
                spk_lght(True)
            elif sel_i == "clear_light_string":
                cfg["light_string"] = ""
                ply_a_0("/sd/mvc/lights_cleared.wav")
            elif sel_i == "add_lights":
                ply_a_0("/sd/mvc/add_light_menu.wav")
                a = True
                while a:
                    sw = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if sw == "left":
                        self.li -= 1
                        if self.li < 0:
                            self.li = len(l_opt)-1
                        self.sel_li = self.li
                        ply_a_0("/sd/mvc/" + l_opt[self.li] + ".wav")
                    elif sw == "right":
                        self.li += 1
                        if self.li > len(l_opt)-1:
                            self.li = 0
                        self.sel_li = self.li
                        ply_a_0("/sd/mvc/" + l_opt[self.li] + ".wav")
                    elif sw == "right_held":
                        if cfg["light_string"] == "":
                            cfg["light_string"] = l_opt[self.sel_li]
                        else:
                            cfg["light_string"] = cfg["light_string"] + \
                                "," + l_opt[self.sel_li]
                        ply_a_0("/sd/mvc/" +
                                l_opt[self.sel_li] + ".wav")
                        ply_a_0("/sd/mvc/added.wav")
                    elif sw == "left_held":
                        files.write_json_file(
                            "/sd/config_christmas_park.json", cfg)
                        upd_l_str()
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        a = False
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                upd_l_str()
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
st_mch.add(Light())

au_en.value = True

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

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.upd()
    upd_vol(.02)
    if (web):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue

