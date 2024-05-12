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
num_voices = 1
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

cfg = files.read_json_file("/sd/config_lightning.json")

snd_opt = files.return_directory("", "/sd/lightning_sounds", ".wav")

cust_snd_opt = files.return_directory(
    "customers_owned_music_", "/sd/customers_owned_music", ".wav")

all_snd_opt = []
all_snd_opt.extend(snd_opt)
all_snd_opt.extend(cust_snd_opt)

menu_snd_opt = []
menu_snd_opt.extend(snd_opt)
rnd_opt = ['random all', 'random built in', 'random my']
menu_snd_opt.extend(rnd_opt)
menu_snd_opt.extend(cust_snd_opt)

ts_jsons = files.return_directory(
    "", "/sd/time_stamp_defaults", ".json")

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfg_lght = files.read_json_file(
    "/sd/mvc/light_string_menu.json")
lght_m = cfg_lght["light_string_menu"]

cfg_l_opt = files.read_json_file("/sd/mvc/light_options.json")
l_opt = cfg_l_opt["light_options"]

cfg_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False

gc_col("config setup")

################################################################################
# Setup neo pixels
bars = []
bolts = []
nood = []

bar_arr = []
bolt_arr = []

num_px = 0

# 15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP10, num_px)


def bld_bar():
    my_indexes = []
    for bar in bars:
        for led_index in bar:
            start_index = led_index
            break
        for led_index in range(0, 10):
            my_indexes.append(led_index+start_index)
    return my_indexes


def bld_bolt():
    my_indexes = []
    for bolt in bolts:
        for led_index in bolt:
            start_index = led_index
            break
        if len(bolt) == 4:
            for led_index in range(0, 4):
                my_indexes.append(led_index+start_index)
        if len(bolt) == 1:
            for led_index in range(0, 1):
                my_indexes.append(led_index+start_index)
    return my_indexes


def l_tst():
    global bar_arr, bolt_arr
    bar_arr = bld_bar()
    bolt_arr = bld_bolt()
    for bar in bars:
        for led_index in bar:
            led[led_index] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()
    for bolt in bolts:
        for led_index in bolt:
            led[led_index] = (50, 50, 50)
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
    global bars, bolts, nood, num_px, led, num_px
    bars = []
    bolts = []
    nood = []

    num_px = 0

    els = cfg["light_string"].split(',')

    for el in els:
        p = el.split('-')
        if len(p) == 2:
            typ, qty = p
            qty = int(qty)
            if typ == 'bar':
                s = list(range(num_px, num_px + qty))
                bars.append(s)
                num_px += qty
            elif typ == 'bolt' and qty < 4:
                s = [num_px, qty]
                nood.append(s)
                num_px += 1
            elif typ == 'bolt' and qty == 4:
                s = list(range(num_px, num_px + qty))
                bolts.append(s)
                num_px += qty

    print("Number of pixels total: ", num_px)
    led.deinit()
    gc_col("Deinit ledStrip")
    # 15 on demo 17 tiny 10 on large
    led = neopixel.NeoPixel(board.GP15, num_px)
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
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except:
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
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            cfg["option_selected"] = rq_d["an"]
            an(cfg["option_selected"])
            files.write_json_file("/sd/cfg.json", cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def buttonpress(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for ts_fn in ts_jsons:
                    ts = files.read_json_file(
                        "/sd/time_stamp_defaults/" + ts_fn + ".json")
                    files.write_json_file(
                        "/sd/lightning_sounds/"+ts_fn+".json", ts)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif rq_d["an"] == "reset_to_defaults":
                rst_def()
                files.write_json_file("/sd/config_lightning.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to_state('base_state')
            elif rq_d["an"] == "reset_default_colors":
                rst_def_col()
                files.write_json_file("/sd/config_lightning.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                my_string = files.json_stringify(
                    {"bars": cfg["bars"], "bolts": cfg["bolts"], "variation": cfg["variation"]})
                st_mch.go_to_state('base_state')
                return Response(request, my_string)
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/mode", [POST])
        def buttonpress(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            if rq_d["an"] == "cont_mode_on":
                cont_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
            elif rq_d["an"] == "cont_mode_off":
                cont_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif rq_d["an"] == "timestamp_mode_on":
                ts_mode = True
                ply_a_0("/sd/mvc/timestamp_mode_on.wav")
                ply_a_0("/sd/mvc/timestamp_instructions.wav")
            elif rq_d["an"] == "timestamp_mode_off":
                ts_mode = False
                ply_a_0("/sd/mvc/timestamp_mode_off.wav")
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/speaker", [POST])
        def buttonpress(request: Request):
            global cfg
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                command_sent = "speaker_test"
                ply_a_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                command_sent = "volume_pot_off"
                cfg["volume_pot"] = False
                files.write_json_file("/sd/config_lightning.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_lightning.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, "Utility: " + command_sent)

        @server.route("/lights", [POST])
        def buttonpress(request: Request):
            raw_text = request.raw_request.decode("utf8")
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
            return Response(request, "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            cfg["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/config_lightning.json", cfg)
            mdns_server.hostname = cfg["HOST_NAME"]
            speak_webpage()
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/update-volume", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            ch_vol(data_object["action"])
            return Response(request, cfg["volume"])

        @server.route("/get-volume", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["volume"])

        @server.route("/update-light-string", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            if data_object["action"] == "save" or data_object["action"] == "clear" or data_object["action"] == "defaults":
                cfg["light_string"] = data_object["text"]
                print("action: " +
                      data_object["action"] + " data: " + cfg["light_string"])
                files.write_json_file("/sd/config_lightning.json", cfg)
                upd_l_str()
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                return Response(request, cfg["light_string"])
            if cfg["light_string"] == "":
                cfg["light_string"] = data_object["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + \
                    "," + data_object["text"]
            print("action: " + data_object["action"] +
                  " data: " + cfg["light_string"])
            files.write_json_file("/sd/config_lightning.json", cfg)
            upd_l_str()
            ply_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["light_string"])

        @server.route("/get-customers-sound-tracks", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(cust_snd_opt)
            return Response(request, my_string)

        @server.route("/get-built-in-sound-tracks", [POST])
        def buttonpress(request: Request):
            sounds = []
            sounds.extend(snd_opt)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/get-bar-colors", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(cfg["bars"])
            return Response(request, my_string)

        @server.route("/get-bolt-colors", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(cfg["bolts"])
            return Response(request, my_string)

        @server.route("/get-color-variation", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(cfg["variation"])
            return Response(request, my_string)

        @server.route("/set-lights", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            command_sent = "set-lights"
            if data_object["item"] == "bars":
                cfg["bars"] = {"r": data_object["r"],
                               "g": data_object["g"], "b": data_object["b"]}
                bar_indexes = []
                bar_indexes.extend(bar_arr)
                for i in bar_indexes:
                    led[i] = (data_object["r"],
                              data_object["g"], data_object["b"])
                    led.show()
            elif data_object["item"] == "bolts":
                cfg["bolts"] = {"r": data_object["r"],
                                "g": data_object["g"], "b": data_object["b"]}
                bolt_indexes = []
                bolt_indexes.extend(bolt_arr)
                for i in bolt_indexes:
                    led[i] = (data_object["r"],
                              data_object["g"], data_object["b"])
                    led.show()
            elif data_object["item"] == "variationBolt":
                print(data_object)
                cfg["variation"] = {"r1": data_object["r"], "g1": data_object["g"], "b1": data_object["b"],
                                    "r2": cfg["variation"]["r2"], "g2": cfg["variation"]["g2"], "b2": cfg["variation"]["b2"]}
            elif data_object["item"] == "variationBar":
                cfg["variation"] = {"r1": cfg["variation"]["r1"], "g1": cfg["variation"]["g1"], "b1": cfg["variation"]
                                    ["b1"], "r2": data_object["r"], "g2": data_object["g"], "b2": data_object["b"]}
            files.write_json_file("/sd/config_lightning.json", cfg)
            return Response(request, command_sent)

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")


gc_col("utilities")

################################################################################
# Global Methods


def rst_l_def():
    global cfg
    cfg["light_string"] = "bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4"


def rst_def_col():
    global cfg
    cfg["bars"] = {"r": 255, "g": 77, "b": 21}
    cfg["bolts"] = {"r": 255, "g": 77, "b": 21}
    cfg["variation"] = {"r1": 20, "g1": 8, "b1": 5, "r2": 20, "g2": 8, "b2": 5}


def rst_wht_col():
    global cfg
    cfg["bars"] = {"r": 255, "g": 255, "b": 255}
    cfg["bolts"] = {"r": 255, "g": 255, "b": 255}
    cfg["variation"] = {"r1": 0, "g1": 0, "b1": 0, "r2": 0, "g2": 0, "b2": 0}


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-lightning"
    cfg["option_selected"] = "thunder birds rain"
    cfg["volume"] = "20"
    cfg["can_cancel"] = True
    rst_l_def()
    rst_wht_col()


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
        shortCircuitDialog()


def stop_audio_0():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass


def shortCircuitDialog():
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


def left_right_mouse_button():
    ply_a_0("/sd/mvc/press_left_button_right_button.wav")


def selectWebOptionsAnnouncement():
    ply_a_0("/sd/mvc/web_menu.wav")
    left_right_mouse_button()


def option_selected_announcement():
    ply_a_0("/sd/mvc/option_selected.wav")


def speak_song_number(song_number):
    ply_a_0("/sd/mvc/song.wav")
    spk_str(song_number, False)


def speak_light_string(play_intro):
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


def no_user_soundtrack_found():
    ply_a_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            ply_a_0("/sd/mvc/create_sound_track_files.wav")
            break


def speak_webpage():
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


last_option = ""


def an(file_name):
    global cfg, last_option
    print("Filename: " + file_name)
    current_option_selected = file_name
    try:
        if file_name == "random built in":
            highest_index = len(snd_opt) - 1
            current_option_selected = snd_opt[random.randint(
                0, highest_index)]
            while last_option == current_option_selected and len(snd_opt) > 1:
                current_option_selected = snd_opt[random.randint(
                    0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random my":
            highest_index = len(cust_snd_opt) - 1
            current_option_selected = cust_snd_opt[random.randint(
                0, highest_index)]
            while last_option == current_option_selected and len(cust_snd_opt) > 1:
                current_option_selected = cust_snd_opt[random.randint(
                    0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random all":
            highest_index = len(all_snd_opt) - 1
            current_option_selected = all_snd_opt[random.randint(
                0, highest_index)]
            while last_option == current_option_selected and len(all_snd_opt) > 1:
                current_option_selected = all_snd_opt[random.randint(
                    0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        if ts_mode:
            ts(current_option_selected)
        else:
            if "customers_owned_music_" in current_option_selected:
                animation_light_show(current_option_selected)
            elif current_option_selected == "alien lightshow":
                animation_light_show(current_option_selected)
            elif current_option_selected == "inspiring cinematic ambient lightshow":
                animation_light_show(current_option_selected)
            elif current_option_selected == "fireworks":
                animation_light_show(current_option_selected)
            else:
                t_l(current_option_selected)
    except Exception as e:
        files.log_item(e)
        no_user_soundtrack_found()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")


def animation_light_show(file_name):
    global ts_mode
    rand_index_low = 1
    rand_index_high = 3

    if file_name == "fireworks":
        rand_index_low = 4
        rand_index_high = 4

    customers_file = "customers_owned_music_" in file_name

    if customers_file:
        file_name = file_name.replace("customers_owned_music_", "")
        try:
            flash_time_dictionary = files.read_json_file(
                "/sd/customers_owned_music/" + file_name + ".json")
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
        flash_time_dictionary = files.read_json_file(
            "/sd/lightning_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0

    if customers_file:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)
    startTime = time.monotonic()
    my_index = 0

    mlt_c(.01)
    while True:
        previous_index = 0
        timeElapsed = time.monotonic()-startTime
        if flashTimeIndex < len(flashTime)-2:
            duration = flashTime[flashTimeIndex+1] - \
                flashTime[flashTimeIndex]-0.25
        else:
            duration = 0.25
        if duration < 0:
            duration = 0
        if timeElapsed > flashTime[flashTimeIndex] - 0.25:
            print("Time elapsed: " + str(timeElapsed) + " Timestamp: " +
                  str(flashTime[flashTimeIndex]) + " Dif: " + str(timeElapsed-flashTime[flashTimeIndex]))
            flashTimeIndex += 1
            my_index = random.randint(rand_index_low, rand_index_high)
            while my_index == previous_index:
                my_index = random.randint(rand_index_low, rand_index_high)
            if my_index == 1:
                rainbow(.005, duration)
            elif my_index == 2:
                mlt_c(.01)
                upd_vol(duration)
            elif my_index == 3:
                candle(duration)
            elif my_index == 4:
                fwrk(duration)
            previous_index = my_index
        if flashTimeLen == flashTimeIndex:
            flashTimeIndex = 0
        l_sw.update()
        # if timeElasped > 2: mixer.voice[0].stop()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            break
        upd_vol(.001)


def ts(file_name):
    print("Time stamp mode:")
    global ts_mode

    customers_file = "customers_owned_music_" in file_name

    my_time_stamps = files.read_json_file(
        "/sd/time_stamp_defaults/timestamp mode.json")
    my_time_stamps["flashTime"] = []

    file_name = file_name.replace("customers_owned_music_", "")

    if customers_file:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        time_elapsed = time.monotonic()-startTime
        r_sw.update()
        if r_sw.fell:
            my_time_stamps["flashTime"].append(time_elapsed)
            print(time_elapsed)
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            my_time_stamps["flashTime"].append(5000)
            if customers_file:
                files.write_json_file(
                    "/sd/customers_owned_music/" + file_name + ".json", my_time_stamps)
            else:
                files.write_json_file(
                    "/sd/lightning_sounds/" + file_name + ".json", my_time_stamps)
            break

    ts_mode = False
    ply_a_0("/sd/mvc/timestamp_saved.wav")
    ply_a_0("/sd/mvc/timestamp_mode_off.wav")
    ply_a_0("/sd/mvc/animations_are_now_active.wav")


def t_l(file_name):

    flash_time_dictionary = files.read_json_file(
        "/sd/lightning_sounds/" + file_name + ".json")

    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0

    wave0 = audiocore.WaveFile(
        open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)
    startTime = time.monotonic()

    while True:
        upd_vol(.1)
        time_elapsed = time.monotonic()-startTime
        # amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
        rand_time = flashTime[flashTimeIndex] - random.uniform(.5, 1)
        if time_elapsed > rand_time:
            print("Time elapsed: " + str(time_elapsed) + " Timestamp: " +
                  str(rand_time) + " Dif: " + str(time_elapsed-rand_time))
            flashTimeIndex += 1
            ltng()
        if flashTimeLen == flashTimeIndex:
            flashTimeIndex = 0
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
        for i in range(num_px):
            pi = (i * 256 // num_px) + j
            led[i] = colorwheel(pi & 255)
        led.show()
        upd_vol(spd)
        te = time.monotonic()-startTime
        if te > dur:
            return
    for j in reversed(range(0, 255, 1)):
        for i in range(num_px):
            pi = (i * 256 // num_px) + j
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
        for i in range(0, num_px):
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
        bolt_r = col_it(cfg["bolts"]["r"], cfg["variation"]["r1"])
        bolt_g = col_it(cfg["bolts"]["g"], cfg["variation"]["g1"])
        bolt_b = col_it(cfg["bolts"]["b"], cfg["variation"]["b1"])

        # set bar base color
        bar_r = col_it(cfg["bars"]["r"], cfg["variation"]["r2"])
        bar_g = col_it(cfg["bars"]["g"], cfg["variation"]["g2"])
        bar_b = col_it(cfg["bars"]["b"], cfg["variation"]["b2"])

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
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
                ply_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                ply_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
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
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + main_m[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(main_m)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = main_m[self.selectedMenuIndex]
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
        left_right_mouse_button()
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
                        "/sd/lightning_options_voice_commands/option_" + menu_snd_opt[self.optionIndex] + ".wav", "rb"))
                    mix.voice[0].play(wave0, loop=False)
                except:
                    speak_song_number(str(self.optionIndex+1))
                self.currentOption = self.optionIndex
                self.optionIndex += 1
                if self.optionIndex > len(menu_snd_opt)-1:
                    self.optionIndex = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.currentOption]
                files.write_json_file("/sd/config_lightning.json", cfg)
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
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + vol_set[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(vol_set)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = vol_set[self.selectedMenuIndex]
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
                        files.write_json_file("/sd/config_lightning.json", cfg)
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        machine.go_to_state('base_state')
                    upd_vol(0.1)
                    pass
            elif selected_menu_item == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/config_lightning.json", cfg)
                ply_a_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
            elif selected_menu_item == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_lightning.json", cfg)
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
        selectWebOptionsAnnouncement()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + web_m[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(web_m)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = web_m[self.selectedMenuIndex]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_instr_web":
                ply_a_0("/sd/mvc/web_instruct.wav")
                selectWebOptionsAnnouncement()
            else:
                files.write_json_file("/sd/config_lightning.json", cfg)
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
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0("/sd/mvc/" + lght_m[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(lght_m)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = lght_m[self.selectedMenuIndex]
            if selected_menu_item == "hear_light_setup_instructions":
                ply_a_0("/sd/mvc/string_instructions.wav")
            elif selected_menu_item == "reset_lights_defaults":
                rst_l_def()
                ply_a_0("/sd/mvc/lights_reset_to.wav")
                speak_light_string(False)
            elif selected_menu_item == "hear_current_light_settings":
                speak_light_string(True)
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
                            self.menuIndex = len(l_opt)-1
                        self.selectedMenuIndex = self.menuIndex
                        ply_a_0("/sd/mvc/" +
                                l_opt[self.menuIndex] + ".wav")
                    elif switch_state == "right":
                        self.menuIndex += 1
                        if self.menuIndex > len(l_opt)-1:
                            self.menuIndex = 0
                        self.selectedMenuIndex = self.menuIndex
                        ply_a_0("/sd/mvc/" +
                                l_opt[self.menuIndex] + ".wav")
                    elif switch_state == "right_held":
                        if cfg["light_string"] == "":
                            cfg["light_string"] = l_opt[self.selectedMenuIndex]
                        else:
                            cfg["light_string"] = cfg["light_string"] + \
                                "," + l_opt[self.selectedMenuIndex]
                        ply_a_0("/sd/mvc/" +
                                l_opt[self.selectedMenuIndex] + ".wav")
                        ply_a_0("/sd/mvc/added.wav")
                    elif switch_state == "left_held":
                        files.write_json_file("/sd/config_lightning.json", cfg)
                        upd_l_str()
                        ply_a_0("/sd/mvc/all_changes_complete.wav")
                        adding = False
                        machine.go_to_state('base_state')
                    upd_vol(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_lightning.json", cfg)
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
        speak_webpage()
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
