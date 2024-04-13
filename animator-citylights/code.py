import utilities
from adafruit_debouncer import Debouncer
from rainbowio import colorwheel
import neopixel
from analogio import AnalogIn
import asyncio
from adafruit_motor import servo
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

# Setup pin for vol
a_in = AnalogIn(board.A0)

# setup pin for audio enable 22 on tiny 28 on large
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
aud_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)
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

# Setup the servos
s_1 = pwmio.PWMOut(board.GP9, duty_cycle=2 ** 15, frequency=50)
s_2 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50) #bandstand 10 city lights 15
s_3 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

s_4 = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)
s_5 = pwmio.PWMOut(board.GP13, duty_cycle=2 ** 15, frequency=50)
s_6 = pwmio.PWMOut(board.GP14, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

s_4 = servo.Servo(s_4, min_pulse=500, max_pulse=2500)
s_5 = servo.Servo(s_5, min_pulse=500, max_pulse=2500)
s_6 = servo.Servo(s_6, min_pulse=500, max_pulse=2500)

s_arr = [s_1, s_2, s_3, s_4, s_5, s_6]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card config variables

cfg = files.read_json_file("/sd/cfg.json")

def getAll():
    global snd_opt, plylst_opt, cust_snd_opt, all_snd_opt, menu_snd_opt
    snd_opt = files.return_directory("", "/sd/bltin", ".wav")

    plylst_opt = files.return_directory("plylst_", "/sd/plylst", ".json")

    cust_snd_opt = files.return_directory(
        "customers_owned_music_", "/sd/customers_owned_music", ".wav")

    all_snd_opt = []
    all_snd_opt.extend(snd_opt)
    all_snd_opt.extend(plylst_opt)
    all_snd_opt.extend(cust_snd_opt)

    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all', 'random built in', 'random my']
    menu_snd_opt.extend(rnd_opt)
    menu_snd_opt.extend(plylst_opt)
    menu_snd_opt.extend(cust_snd_opt)

getAll()

ts_jsons = files.return_directory(
    "", "/sd/t_s_def", ".json")

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfd_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfd_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False

gc_col("config setup")

################################################################################
# Setup neo pixels

num_px = 10

led = neopixel.NeoPixel(board.GP15, num_px) #15 on demo 17 tiny 10 on large
led.auto_write = False
led.brightness = 1.0
led.fill((50, 50, 50))
led.show()

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
        files.log_item("Using env ssid and password")
    except:
        files.log_item("Using default ssid and password")

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
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for time_stamp_file in ts_jsons:
                    time_stamps = files.read_json_file(
                        "/sd/t_s_def/" + time_stamp_file + ".json")
                    files.write_json_file(
                        "/sd/bltin/"+time_stamp_file+".json", time_stamps)
                play_a_0("/sd/mvc/all_changes_complete.wav")
            elif rq_d["an"] == "reset_to_defaults":
                cmd_snt = "reset_to_defaults"
                rst_def()
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to('base_state')
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/mode", [POST])
        def btn(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            if rq_d["an"] == "cont_mode_on":
                cont_run = True
                play_a_0("/sd/mvc/continuous_mode_activated.wav")
            elif rq_d["an"] == "cont_mode_off":
                cont_run = False
                play_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif rq_d["an"] == "timestamp_mode_on":
                ts_mode = True
                play_a_0("/sd/mvc/timestamp_mode_on.wav")
                play_a_0("/sd/mvc/timestamp_instructions.wav")
            elif rq_d["an"] == "timestamp_mode_off":
                ts_mode = False
                play_a_0("/sd/mvc/timestamp_mode_off.wav")
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/speaker", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "speaker_test":
                cmd_snt = "speaker_test"
                play_a_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif rq_d["an"] == "volume_pot_off":
                cmd_snt = "volume_pot_off"
                cfg["volume_pot"] = False
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
            elif rq_d["an"] == "volume_pot_on":
                cmd_snt = "volume_pot_on"
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/lights", [POST])
        def btn(request: Request):
            rq_d = request.json()
            set_hdw(rq_d["an"],1)
            return Response(request, "Utility: " + "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["HOST_NAME"] = rq_d["an"]
            files.write_json_file("/sd/cfg.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            spk_web()
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def btn(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/update-volume", [POST])
        def btn(request: Request):
            global cfg
            rq_d = request.json()
            ch_vol(rq_d["action"])
            return Response(request, cfg["volume"])

        @server.route("/get-volume", [POST])
        def btn(request: Request):
            return Response(request, cfg["volume"])
        
        @server.route("/get-scripts", [POST])
        def btn(request: Request):
            sounds = []
            sounds.extend(plylst_opt)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)
        
        @server.route("/get-built-in-sound-tracks", [POST])
        def btn(request: Request):
            sounds = []
            sounds.extend(snd_opt)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)
        
        @server.route("/get-customers-sound-tracks", [POST])
        def btn(request: Request):
            my_string = files.json_stringify(cust_snd_opt)
            return Response(request, my_string)

        @server.route("/test-animation", [POST])
        def btn(request: Request):
            rq_d = request.json()
            files.log_item(rq_d["an"])
            gc_col("Save Data.")
            set_hdw(rq_d["an"],3)
            return Response(request, "success")

        @server.route("/get-animation", [POST])
        def btn(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            snd_f = rq_d["an"]
            if "plylst_" in snd_f:
                snd_f = snd_f.replace("plylst_", "")
                if (f_exists("/sd/plylst/" + snd_f + ".json") == True):
                    f_n = "/sd/plylst/" + snd_f + ".json"
                    files.log_item(f_n)
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "/sd/t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")
            if "customers_owned_music_" in snd_f:
                snd_f = snd_f.replace("customers_owned_music_", "")
                if (f_exists("/sd/customers_owned_music/" + snd_f + ".json") == True):
                    f_n = "/sd/customers_owned_music/" + snd_f + ".json"
                    files.log_item(f_n)
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "/sd/t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")
            else:
                if (f_exists("/sd/bltin/" + snd_f + ".json") == True):
                    f_n = "/sd/bltin/" + snd_f + ".json"
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "/sd/t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")
                
        
        @server.route("/stop", [POST])
        def btn(request: Request):
            rq_d = request.json()
            rst_an()
            gc_col("rst an")
            return JSONResponse(request, "rst an")
        
        @server.route("/delete-playlist", [POST])
        def btn(request: Request):
            rq_d = request.json()
            snd_f = rq_d["fn"].replace("plylst_", "")
            f_n = "/sd/plylst/" + snd_f + ".json"
            os.remove(f_n)
            getAll()
            gc_col("get data")
            return JSONResponse(request, "file deleted")
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
                    f_n = ""
                    an = rq_d[3].split("_")
                    if "plylst" == an[0]:
                        snd_f = rq_d[3].replace("plylst_", "")
                        f_n = "/sd/plylst/" + \
                            snd_f + ".json"
                        files.log_item(f_n)
                    elif "customers" == an[0]:
                        snd_f = rq_d[3].replace("customers_owned_music_", "")
                        f_n = "/sd/customers_owned_music/" + \
                            snd_f + ".json" 
                    else:
                        f_n = "/sd/bltin/" + \
                            rq_d[3] + ".json"
                    print("saving to: " + f_n)
                    files.write_json_file(f_n, data)
                    getAll()
                    data = []
                    gc_col("get data")
                    
            except:
                data = []
                gc_col("get data")
                return Response(request, "out of memory")
            return Response(request, "success")
        
        @server.route("/create-playlist", [POST])
        def btn(request: Request):
            global data
            rq_d = request.json()
            f_n="/sd/plylst/" + rq_d["fn"] + ".json"
            files.write_json_file(f_n, ["0.0|", "1.0|"])
            getAll()
            gc_col("created playlist")
            return Response(request, "success")
        
        @server.route("/rename-playlist", [POST])
        def btn(request: Request):
            global data
            rq_d = request.json()
            snd = rq_d["fo"].replace("plylst_", "")
            fo="/sd/plylst/" + snd + ".json"
            fn="/sd/plylst/" + rq_d["fn"] + ".json"
            os.rename(fo,fn)
            getAll()
            gc_col("renamed playlist")
            return Response(request, "success")  

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")

################################################################################
# Global Methods


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods

def upd_vol(seconds):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        time.sleep(seconds)
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
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
    play_a_0("/sd/mvc/volume.wav")
    spk_str(cfg["volume"], False)


def stp_snd():
    mix.voice[0].stop()
    wait_snd()


def wait_snd():
    while mix.voice[0].playing:
        exit_early
        pass

def play_a_0(file_name):
    stp_snd()
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    wait_snd()
    

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
            play_a_0("/sd/mvc/" + character + ".wav")
        except:
            files.log_item("Invalid character in string to speak")
    if addLocal:
        play_a_0("/sd/mvc/dot.wav")
        play_a_0("/sd/mvc/local.wav")


def l_r_but():
    play_a_0("/sd/mvc/press_left_button_right_button.wav")


def sel_web():
    play_a_0("/sd/mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    play_a_0("/sd/mvc/option_selected.wav")


def spk_sng_num(song_number):
    play_a_0("/sd/mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    play_a_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            play_a_0("/sd/mvc/create_sound_track_files.wav")
            break


def spk_web():
    play_a_0("/sd/mvc/animator_available_on_network.wav")
    play_a_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-city-lights":
        play_a_0("/sd/mvc/animator_dash_city_dash_lights.wav")
        play_a_0("/sd/mvc/dot.wav")
        play_a_0("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_a_0("/sd/mvc/in_your_browser.wav")


p_arr = [90, 90, 90, 90, 90, 90]


async def cyc_servo(n, s, p_up, p_dwn):
    global p_arr
    while mix.voice[0].playing:
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
# animations


lst_opt = ""


def an(f_nm):
    global cfg, lst_opt
    files.log_item("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random built in":
            h_i = len(snd_opt) - 1
            cur_opt = snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(snd_opt) > 1:
                cur_opt = snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            files.log_item("Random sound option: " + f_nm)
            files.log_item("Sound file: " + cur_opt)
        elif f_nm == "random my":
            h_i = len(cust_snd_opt) - 1
            cur_opt = cust_snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(cust_snd_opt) > 1:
                cur_opt = cust_snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            files.log_item("Random sound option: " + f_nm)
            files.log_item("Sound file: " + cur_opt)
        elif f_nm == "random all":
            h_i = len(all_snd_opt) - 1
            cur_opt = all_snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(all_snd_opt) > 1:
                cur_opt = all_snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            files.log_item("Random sound option: " + f_nm)
            files.log_item("Sound file: " + cur_opt)
        if ts_mode:
            an_ts(cur_opt)
        else:
            files.log_item(cur_opt)
            an_light(cur_opt)
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")


def an_light(f_nm):
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm
    plylst_f = "plylst_" in f_nm

    flsh_t = []

    if cust_f:
        f_nm = f_nm.replace("customers_owned_music_", "")
        if (f_exists("/sd/customers_owned_music/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "/sd/customers_owned_music/" + f_nm + ".json")
        else:
            try:
                flsh_t = files.read_json_file(
                    "/sd/customers_owned_music/" + f_nm + ".json")
            except:
                play_a_0("/sd/mvc/no_timestamp_file_found.wav")
                while True:
                    l_sw.update()
                    r_sw.update()
                    if l_sw.fell:
                        ts_mode = False
                        return
                    if r_sw.fell:
                        ts_mode = True
                        play_a_0("/sd/mvc/timestamp_instructions.wav")
                        return
    elif plylst_f:
        f_nm = f_nm.replace("plylst_", "")
        flsh_t = files.read_json_file("/sd/plylst/" + f_nm + ".json")
    else:
        if (f_exists("/sd/bltin/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "/sd/bltin/" + f_nm + ".json")

    flsh_i = 0
    
    ft1 = []
    ft2 = []
    
    ft1 = flsh_t[len(flsh_t)-1].split("|")
    tm = float(ft1[0]) + 1
    flsh_t.append(str(tm) + "|E")
    flsh_t.append(str(tm + 1) + "|E")
    
    files.log_item(flsh_t)

    if not plylst_f:
        if cust_f:
            w0 = audiocore.WaveFile(
                open("/sd/customers_owned_music/" + f_nm + ".wav", "rb"))
        else:
            w0 = audiocore.WaveFile(
                open("/sd/bltin/" + f_nm + ".wav", "rb"))
        mix.voice[0].play(w0, loop=False)

    srt_t = time.monotonic()

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
                set_hdw("L000" + str(lgt) + ",S0" + str(pos),dur)
            else:
                resp = set_hdw(ft1[1], dur)
                if resp == "STOP":
                    rst_an()
                    return
            flsh_i += 1
        l_sw.update()
        if l_sw.fell and cfg["can_cancel"]:
            flsh_i = len(flsh_t)-1
            rst_an()
            return "STOP"
        if flsh_i == len(flsh_t)-1:
            rst_an()
            return "DONE"
        upd_vol(.001)

def rst_an():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass
    led.fill((0, 0, 0))
    led.show()

def an_ts(f_nm):
    files.log_item("time stamp mode")
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm

    t_s = []

    f_nm = f_nm.replace("customers_owned_music_", "")

    if cust_f:
        w0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + f_nm + ".wav", "rb"))
    else:
        w0 = audiocore.WaveFile(
            open("/sd/bltin/" + f_nm + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            files.log_item(t_elsp)
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            t_s.append(1)
            if cust_f:
                files.write_json_file(
                    "/sd/customers_owned_music/" + f_nm + ".json", t_s)
            else:
                files.write_json_file(
                    "/sd/bltin/" + f_nm + ".json", t_s)
            break

    ts_mode = False
    play_a_0("/sd/mvc/timestamp_saved.wav")
    play_a_0("/sd/mvc/timestamp_mode_off.wav")
    play_a_0("/sd/mvc/animations_are_now_active.wav")

##############################
# animation effects

br = 0

def set_hdw(cmd,dur): 
    global sp, br
    # Split the input string into segments
    segs = cmd.split(",")

    # Process each segment
    try:
        for seg in segs:
            f_nm = ""
            if seg[0] == 'E': # end an
                return "STOP"
            if seg[0] == 'M': # play file
                if seg[1] == "S":
                    stp_snd()
                elif seg[1] == "W" or seg[1] == "A" or seg[1] == "P":
                    stp_snd()
                    if seg[2] == "B":
                        w0 = audiocore.WaveFile(open("/sd/bltin/" + seg[3:] + ".wav", "rb"))
                        f_nm = seg[3:]
                    elif seg[2] == "C":
                        w0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + seg[3:] + ".wav", "rb"))
                        f_nm = "customers_owned_music_" + seg[3:]
                    elif seg[2] == "P":
                        f_nm = "plylst_" + seg[3:]
                    if seg[1] == "W" or seg[1] == "P":
                        mix.voice[0].play(w0, loop=False)
                    if seg[1] == "A":    
                        res = an(f_nm)
                        if res == "STOP": return "STOP"
                    if seg[1] == "W":
                        wait_snd()
            if seg[0] == 'L':  # lights
                px = int(seg[1])+int(seg[2])
                ind = int(seg[3])-1
                if ind == 0:
                    ind = 1
                elif ind == 1:
                    ind = 0
                v = int(seg[4:])
                if px == 0:
                    led.fill((v, v, v))
                else:
                    cur = list(led[px-1])
                    cur[ind] = v
                    if seg[3] == "0":
                        led[px-1]=(v,v,v)
                    else:
                        led[px-1]=(cur[0],cur[1],cur[2])
                led.show()
            if seg[0] == 'S':  # servos
                num = int(seg[1])
                v = int(seg[2:])
                if num == 0:
                    for i in range(6):
                        s_arr[i].angle = v
                else:
                    s_arr[num].angle = int(v)
            if seg[0] == 'B':  # brightness
                br = int(seg[1:])
                led.brightness = float(br/100)
                led.show()
            if seg[0] == 'F':  # fade in or out
                v = int(seg[1:])
                while not br == v:
                    if br < v:
                        br += 1
                        led.brightness = float(br/100)
                    else:
                        br -= 1
                        led.brightness = float(br/100)
                    led.show()
                    upd_vol(.01)
            if seg[0] == 'R':
                v = float(seg[1:])
                rbow(v,dur)
    except Exception as e:
        files.log_item(e)

def rbow(spd,dur):
    st = time.monotonic()
    for j in range(0,255,1):
        for i in range(num_px):
            pixel_index = (i * 256 // num_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        upd_vol(spd)
        te = time.monotonic()-st
        if te > dur:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_px):
            pixel_index = (i * 256 // num_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        upd_vol(spd)
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
        play_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
                play_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                play_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
            an(cfg["option_selected"])
        elif switch_state == "right":
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
        play_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0("/sd/mvc/" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if r_sw.fell:
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
                play_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')


class Bltin(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, mch):
        files.log_item('Choose sounds menu')
        play_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
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
                        "/sd/o_bltin/" + menu_snd_opt[self.i] + ".wav", "rb"))
                    mix.voice[0].play(w0, loop=False)
                except:
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                w0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
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
        play_a_0("/sd/mvc/add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0(
                "/sd/mvc/" + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                play_a_0("/sd/mvc/create_sound_track_files.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                play_a_0("/sd/mvc/timestamp_mode_on.wav")
                play_a_0("/sd/mvc/timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                play_a_0("/sd/mvc/timestamp_mode_off.wav")
            else:
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
        play_a_0("/sd/mvc/volume_settings_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0("/sd/mvc/" + vol_set[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(vol_set)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = vol_set[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                play_a_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        ch_vol("lower")
                    elif switch_state == "right":
                        ch_vol("raise")
                    elif switch_state == "right_held":
                        files.write_json_file(
                            "/sd/cfg.json", cfg)
                        play_a_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
            play_a_0("/sd/mvc/" + web_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if r_sw.fell:
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
                play_a_0("/sd/mvc/web_instruct.wav")
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                play_a_0("/sd/mvc/all_changes_complete.wav")
                mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Bltin())
st_mch.add(AddSnds())
st_mch.add(VolSet())
st_mch.add(WebOpt())

aud_en.value = True

upd_vol(.5)

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
            gc.collect()
        except Exception as e:
            files.log_item(e)
            continue
        
