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

gc_col("Imports gc, files")

def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()

gc_col("imports")
################################################################################
# Setup hardware

# Setup pin for vol
analog_in = AnalogIn(board.A0)

def g_volt(pin, wait_for):
    i = wait_for/10
    pin_v = 0
    for _ in range(10):
        time.sleep(i)
        pin_v += 1
        pin_v = pin_v / 10
    return (pin.value) / 65536

# setup pin for audio enable
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

aud = audiobusio.I2SOut(
    bit_clock=bclk, word_select=lrc, data=din)

# Setup sdCard
aud_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050,
                         channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

vol = .2
mix.voice[0].level = vol

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
s_2 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
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

s_array = [s_1, s_2, s_3, s_4, s_5, s_6]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card config variables

cfg = files.read_json_file("/sd/config_christmas_park.json")

snd_opt = files.return_directory("", "/sd/christmas_park_sounds", ".wav")

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
main_menu = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_menu = cfg_web["web_menu"]

cfg_light = files.read_json_file(
    "/sd/mvc/light_string_menu.json")
light_menu = cfg_light["light_string_menu"]

cfg_light_opt = files.read_json_file("/sd/mvc/light_options.json")
light_opt = cfg_light_opt["light_options"]

cfd_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfd_vol["volume_settings"]

cfg_add_snd = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
add_snd = cfg_add_snd["add_sounds_animate"]

gc_col("config setup")

cont_run = False
ts_mode = False

################################################################################
# Setup neo pixels
num_px = 2

led = neopixel.NeoPixel(board.GP15, num_px)

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
        def buttonpress(request: Request):
            global cfg, cont_run, ts_mode
            raw_text = request.raw_request.decode("utf8")
            if "customers_owned_music_" in raw_text:
                for sound_file in cust_snd_opt:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        animation(cfg["option_selected"])
                        break
            else:  # built in animations
                for sound_file in menu_snd_opt:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        animation(cfg["option_selected"])
                        break
            files.write_json_file("/sd/config_christmas_park.json", cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def buttonpress(request: Request):
            global cfg
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in ts_jsons:
                    time_stamps = files.read_json_file(
                        "/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file(
                        "/sd/christmas_park_sounds/"+time_stamp_file+".json", time_stamps)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                st_mch.go_to('base_state')
            return Response(request, "Utility: " + command_sent)

        @server.route("/mode", [POST])
        def buttonpress(request: Request):
            global cfg, cont_run, ts_mode
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "cont_mode_on" in raw_text:
                cont_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text:
                cont_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif "timestamp_mode_on" in raw_text:
                ts_mode = True
                play_audio_0("/sd/mvc/timestamp_mode_on.wav")
                play_audio_0("/sd/mvc/timestamp_instructions.wav")
            elif "timestamp_mode_off" in raw_text:
                ts_mode = False
                play_audio_0("/sd/mvc/timestamp_mode_off.wav")
            return Response(request, "Utility: " + command_sent)

        @server.route("/speaker", [POST])
        def buttonpress(request: Request):
            global cfg
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                command_sent = "speaker_test"
                play_audio_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                command_sent = "volume_pot_off"
                cfg["volume_pot"] = False
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, "Utility: " + command_sent)

        @server.route("/lights", [POST])
        def buttonpress(request: Request):
            global cfg
            command_sent = ""
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
            return Response(request, "Utility: " + "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            cfg["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/config_christmas_park.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            speak_webpage()
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/update-volume", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            changeVolume(data_object["action"])
            return Response(request, cfg["volume"])

        @server.route("/get-volume", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["volume"])

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

        @server.route("/test-animation", [POST])
        def buttonpress(request: Request):
            data_object = request.json()
            print(data_object["text"])
            gc_col("Save Data.")
            update_animation(data_object["text"])
            return Response(request, "success")

        @server.route("/get-animation", [POST])
        def buttonpress(request: Request):
            global cfg, cont_run, ts_mode
            raw_text = request.raw_request.decode("utf8")
            if "customers_owned_music_" in raw_text:
                for sound_file in cust_snd_opt:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        sound_file = sound_file.replace(
                            "customers_owned_music_", "")
                        myData = files.read_json_file(
                            "/sd/customers_owned_music/" + sound_file + ".json")
                        for i in range(int(len(myData["flashTime"]))):
                            myData["flashTime"][i] = str(
                                round(myData["flashTime"][i], 1))
                        break
            else:  # built in animations
                for sound_file in menu_snd_opt:
                    if sound_file in raw_text:
                        if (f_exists("/sd/christmas_park_sounds/" + sound_file + "_an.json") == True):
                            file_name = "/sd/christmas_park_sounds/" + sound_file + "_an.json"
                            return FileResponse(request, file_name, "/")
                        else:
                            cfg["option_selected"] = sound_file
                            myData = files.read_json_file(
                                "/sd/christmas_park_sounds/" + sound_file + ".json")
                            for i in range(int(len(myData["flashTime"]))):
                                myData["flashTime"][i] = str(
                                    round(myData["flashTime"][i], 1))
                            return JSONResponse(request, myData)
                            
        @server.route("/delete-file", [POST])
        def buttonpress(request: Request):
            data_object = request.json()
            file_name = "/sd/christmas_park_sounds/" + data_object["text"] + "_an.json"
            os.remove(file_name)
            gc_col("get data")
            return JSONResponse(request, "file deleted")

        data_stuff = []

        @server.route("/save-data", [POST])
        def buttonpress(request: Request):
            global data_stuff
            data_object = request.json()
            try:
                if data_object[0] == 0:
                    data_stuff = []
                data_stuff.extend(data_object[2])
                if data_object[0] == data_object[1]:
                    file_name = "/sd/christmas_park_sounds/" + data_object[3] + "_an.json"
                    files.write_json_file(file_name, data_stuff)
                    data_stuff = []
                    gc_col("get data")
            except:
                data_stuff = []
                gc_col("get data")
                return Response(request, "out of memory")
            return Response(request, "success")

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")


gc_col("utilities")

################################################################################
# Global Methods


def upd_vol(seconds):
    if cfg["volume_pot"]:
        volume = g_volt(analog_in, seconds)
        mix.voice[0].level = volume
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
        time.sleep(seconds)


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


def changeVolume(action):
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
    files.write_json_file("/sd/config_christmas_park.json", cfg)
    play_audio_0("/sd/mvc/volume.wav")
    speak_this_string(cfg["volume"], False)

################################################################################
# Dialog and sound play methods


def play_audio_0(file_name):
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


def speak_this_string(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_audio_0("/sd/mvc/" + character + ".wav")
        except:
            print("Invalid character in string to speak")
    if addLocal:
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")


def left_right_mouse_button():
    play_audio_0("/sd/mvc/press_left_button_right_button.wav")


def selectWebOptionsAnnouncement():
    play_audio_0("/sd/mvc/web_menu.wav")
    left_right_mouse_button()


def option_selected_announcement():
    play_audio_0("/sd/mvc/option_selected.wav")


def speak_song_number(song_number):
    play_audio_0("/sd/mvc/song.wav")
    speak_this_string(song_number, False)


def speak_light_string(play_intro):
    try:
        elements = cfg["light_string"].split(',')
        if play_intro:
            play_audio_0("/sd/mvc/current_light_settings_are.wav")
        for index, element in enumerate(elements):
            play_audio_0("/sd/mvc/position.wav")
            play_audio_0("/sd/mvc/" + str(index+1) + ".wav")
            play_audio_0("/sd/mvc/is.wav")
            play_audio_0("/sd/mvc/" + element + ".wav")
    except:
        play_audio_0("/sd/mvc/no_lights_in_light_string.wav")
        return


def no_user_soundtrack_found():
    play_audio_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            play_audio_0("/sd/mvc/create_sound_track_files.wav")
            break


def speak_webpage():
    play_audio_0("/sd/mvc/animator_available_on_network.wav")
    play_audio_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-christmas-park":
        play_audio_0("/sd/mvc/animator_dash_christmas_dash_park.wav")
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")
    else:
        speak_this_string(cfg["HOST_NAME"], True)
    play_audio_0("/sd/mvc/in_your_browser.wav")

################################################################################
# animations


last_option = ""


def animation(file_name):
    global cfg, last_option
    print("Filename: " + file_name)
    current_option_selected = file_name
    #try:
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
        animation_timestamp(current_option_selected)
    else:
        animation_light_show(current_option_selected)
    #except:
    #    no_user_soundtrack_found()
    #    config["option_selected"] = "random built in"
    #    return
    gc_col("Animation complete.")

def animation_light_show(file_name):
    global ts_mode
    rand_index_low = 1
    rand_index_high = 3

    customers_file = "customers_owned_music_" in file_name

    flashTime = []

    if customers_file:
        file_name = file_name.replace("customers_owned_music_", "")
        try:
            flash_time_dictionary = files.read_json_file(
                "/sd/customers_owned_music/" + file_name + ".json")
        except:
            play_audio_0("/sd/mvc/no_timestamp_file_found.wav")
            while True:
                l_sw.update()
                r_sw.update()
                if l_sw.fell:
                    ts_mode = False
                    return
                if r_sw.fell:
                    ts_mode = True
                    play_audio_0("/sd/mvc/timestamp_instructions.wav")
                    return
    else:
        if (f_exists("/sd/christmas_park_sounds/" + file_name + "_an.json") == True):
            flashTime=files.read_json_file(
            "/sd/christmas_park_sounds/" + file_name + "_an.json")
        else:
            flash_time_dictionary = files.read_json_file(
            "/sd/christmas_park_sounds/" + file_name + ".json")
            flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0

    if customers_file:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)
    startTime = time.monotonic()

    my_index = 0
    ft1=[]
    ft2=[]

    while True:
        timeElapsed = time.monotonic()-startTime
        if flashTimeIndex < len(flashTime)-2:
            ft1=flashTime[flashTimeIndex].split("|")
            ft2=flashTime[flashTimeIndex+1].split("|")
            duration = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            duration = 0.25
        if duration < 0:
            duration = 0
        if timeElapsed > float(ft1[0]) - 0.25 and flashTimeIndex < len(flashTime)-2:
            print("time elapsed: " + str(timeElapsed) +
                  " Timestamp: " + ft1[0])
            flashTimeIndex += 1
            if (len(ft1)==1 or ft1[1]==""):
                my_index = random.randint(rand_index_low, rand_index_high)
                if my_index == 1:
                    update_animation("L0100,S0180")
                if my_index == 2:
                    update_animation("L0255,S090")
                if my_index == 3:
                    update_animation("L010,S00")
            else:
                update_animation(ft1[1])
        l_sw.update()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            return
        upd_vol(.001)


def animation_timestamp(file_name):
    print("time stamp mode")
    global ts_mode

    customers_file = "customers_owned_music_" in file_name

    my_time_stamps = files.read_json_file(
        "/sd/time_stamp_defaults/timestamp_mode.json")
    my_time_stamps["flashTime"] = []

    file_name = file_name.replace("customers_owned_music_", "")

    if customers_file:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        time_elasped = time.monotonic()-startTime
        r_sw.update()
        if r_sw.fell:
            my_time_stamps["flashTime"].append(time_elasped)
            print(time_elasped)
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            my_time_stamps["flashTime"].append(5000)
            if customers_file:
                files.write_json_file(
                    "/sd/customers_owned_music/" + file_name + ".json", my_time_stamps)
            else:
                files.write_json_file(
                    "/sd/christmas_park_sounds/" + file_name + ".json", my_time_stamps)
            break

    ts_mode = False
    play_audio_0("/sd/mvc/timestamp_saved.wav")
    play_audio_0("/sd/mvc/timestamp_mode_off.wav")
    play_audio_0("/sd/mvc/animations_are_now_active.wav")

##############################
# animation effects

spot = [0, 0, 0, 0, 0, 0]

def update_animation(input_string):
    global spot
    # Split the input string into segments
    segs = input_string.split(",")

    # Process each segment
    for seg in segs:
        if seg[0] == 'L':  # lights
            # Extract the spotlight number, value
            num = int(seg[1])
            value = int(seg[2:])

            # Set the spotlight value
            if num == 0:
                # Set all spotlights to the specified value
                for i in range(6):
                    spot[i] = value
            else:
                # Set on spot light
                spot[num-1] = int(value)
        if seg[0] == 'S':  # servos
            # Extract the spotlight number, value
            num = int(seg[1])
            value = int(seg[2:])

            # Set the spotlight value
            if num == 0:
                # Set all spotlights to the specified value
                for i in range(6):
                    s_array[i].angle = value
            else:
                # Set on spot light
                s_array[num].angle = int(value)

    led[0] = (spot[1], spot[0], spot[2])
    led[1] = (spot[4], spot[3], spot[5])
    led.show()

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

class BseSt(State):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, machine):
        play_audio_0("/sd/mvc/animations_are_now_active.wav")
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
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
            animation(cfg["option_selected"])
        elif switch_state == "right":
            machine.go_to('main_menu')

class Main(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, machine):
        files.log_item('Main menu')
        play_audio_0("/sd/mvc/main_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + main_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(main_menu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = main_menu[self.selectedMenuIndex]
            if selected_menu_item == "choose_sounds":
                machine.go_to('choose_sounds')
            elif selected_menu_item == "add_sounds_animate":
                machine.go_to('add_sounds_animate')
            elif selected_menu_item == "web_options":
                machine.go_to('web_options')
            elif selected_menu_item == "volume_settings":
                machine.go_to('volume_settings')
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to('base_state')

class Sounds(State):

    def __init__(self):
        self.optionIndex = 0
        self.currentOption = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        play_audio_0("/sd/mvc/sound_selection_menu.wav")
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
                        "/sd/christmas_park_options_voice_commands/option_" + menu_snd_opt[self.optionIndex] + ".wav", "rb"))
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
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                wave0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play(wave0, loop=False)
                while mix.voice[0].playing:
                    pass
            machine.go_to('base_state')

class AddSounds(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'add_sounds_animate'

    def enter(self, machine):
        files.log_item('Add sounds animate')
        play_audio_0("/sd/mvc/add_sounds_animate.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global ts_mode
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0(
                "/sd/mvc/" + add_snd[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(add_snd)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = add_snd[self.selectedMenuIndex]
            if selected_menu_item == "hear_instructions":
                play_audio_0("/sd/mvc/create_sound_track_files.wav")
            elif selected_menu_item == "timestamp_mode_on":
                ts_mode = True
                play_audio_0("/sd/mvc/timestamp_mode_on.wav")
                play_audio_0("/sd/mvc/timestamp_instructions.wav")
                machine.go_to('base_state')
            elif selected_menu_item == "timestamp_mode_off":
                ts_mode = False
                play_audio_0("/sd/mvc/timestamp_mode_off.wav")

            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to('base_state')

class VolSet(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, machine):
        files.log_item('Set Web Options')
        play_audio_0("/sd/mvc/volume_settings_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + vol_set[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(vol_set)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = vol_set[self.selectedMenuIndex]
            if selected_menu_item == "volume_level_adjustment":
                play_audio_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        changeVolume("lower")
                    elif switch_state == "right":
                        changeVolume("raise")
                    elif switch_state == "right_held":
                        files.write_json_file(
                            "/sd/config_christmas_park.json", cfg)
                        play_audio_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        machine.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif selected_menu_item == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to('base_state')
            elif selected_menu_item == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to('base_state')

class WebOpt(State):
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
            play_audio_0("/sd/mvc/" + web_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(web_menu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = web_menu[self.selectedMenuIndex]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_url":
                speak_this_string(cfg["HOST_NAME"], True)
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_instr_web":
                play_audio_0("/sd/mvc/web_instruct.wav")
                selectWebOptionsAnnouncement()
            else:
                files.write_json_file("/sd/config_christmas_park.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to('base_state')

###############################################################################
# Create the state machine

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Sounds())
st_mch.add(AddSounds())
st_mch.add(VolSet())
st_mch.add(WebOpt())

aud_en.value = True

upd_vol(.5)

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

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.update()
    upd_vol(.02)
    if (web):
        try:
            server.poll()
            gc.collect()
        except Exception as e:
            files.log_item(e)
            continue
