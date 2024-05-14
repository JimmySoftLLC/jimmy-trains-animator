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
    files.log_item( "Point " + collection_point + " Available memory: {} bytes".format(start_mem) )


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
    
gc_col("Imports gc, files")
################################################################################
# Setup hardware
a_in = AnalogIn(board.A0)

# setup pin for audio enable 22 on tiny 28 on large
au_en = digitalio.DigitalInOut(board.GP22)
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
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

mix.voice[0].level = .2

try:
  sd = sdcardio.SDCard(spi, cs)
  vfs = storage.VfsFat(sd)
  storage.mount(vfs, "/sd")
except:
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[0].play( w0, loop=False )
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
                w0 = audiocore.WaveFile(open("/sd/mvc/micro_sd_card_success.wav", "rb"))
                mix.voice[0].play( w0, loop=False )
                while mix.voice[0].playing:
                    pass
            except:
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[0].play( w0, loop=False )
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

cus_o = files.return_directory("customers_owned_music_", "/sd/customers_owned_music", ".wav")

all_o = []
all_o.extend(snd_o)
all_o.extend(cus_o)

mnu_o = []
mnu_o.extend(snd_o)
rnd_o = ['random all','random built in','random my']
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
brnchs  = []
cane_s  = []
cane_e  = []

n_px = 0

#15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP15, n_px)

def bld_tree(p):
    i = []
    for t in trees:
        for ledi in t:
            si=ledi
            break
        if p == "ornaments":
            for ledi in range(0,7):
                i.append(ledi+si)
        if p == "star":
            for ledi in range(7,14):
                i.append(ledi+si)
        if p == "branches":        
            for ledi in range(14,21):
                i.append(ledi+si)
    return i

def bld_cane(p):
    i = []
    for c in canes:
        for led_i in c:
            si=led_i
            break
        if p == "end":
            for led_i in range(0,2):
                i.append(led_i+si)
        if p == "start":
            for led_i in range(2,4):
                i.append(led_i+si)
    return i

def show_l():
    led.show()
    time.sleep(.3)
    led.fill((0, 0, 0))
    led.show()

def l_tst():
    global ornmnts,stars,brnchs,cane_s,cane_e
    ornmnts = bld_tree("ornaments")
    stars = bld_tree("star")
    brnchs = bld_tree("branches")
    cane_s = bld_cane("start")
    cane_e = bld_cane("end")

    # cane test
    cnt = 0
    for i in cane_s:
        led[i]=(50, 50, 50)
        cnt+=1
        if cnt > 1:
            show_l()
            cnt = 0
    for i in cane_e:
        led[i]=(50, 50, 50)
        cnt+=1
        if cnt > 1:
            show_l()
            cnt = 0

    #tree test
    cnt = 0
    for i in ornmnts:
        led[i]=(50, 50, 50)
        cnt+=1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in stars:
        led[i]=(50, 50, 50)
        cnt+=1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in brnchs:
        led[i]=(50, 50, 50)
        cnt+=1
        if cnt > 6:
            show_l()
            cnt = 0

def updateLightString():
    global trees, canes, n_px, led, n_px
    trees = []
    canes = []

    n_px = 0
    
    elements = cfg["light_string"].split(',')

    for element in elements:
        parts = element.split('-')

        if len(parts) == 2:
            christmas_park_type, quantity = parts
            quantity = int(quantity)

            if christmas_park_type == 'grandtree':
                grand_tree_sequence = list(range(n_px, n_px + quantity))
                trees.append(grand_tree_sequence)
                n_px += quantity
            elif christmas_park_type == 'cane':
                cane_sequence = list(range(n_px, n_px + quantity))
                canes.append(cane_sequence)
                n_px += quantity

    print ("Number of pixels total: ", n_px)
    led.deinit()
    gc_col("Deinit ledStrip")
    #15 on demo 17 tiny 10 on large
    led = neopixel.NeoPixel(board.GP15, n_px)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()
    
updateLightString()
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

    #default for manufacturing and shows
    WIFI_SSID="jimmytrainsguest"
    WIFI_PASSWORD=""

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
        mdns_server = mdns.Server(wifi.radio)
        mdns_server.hostname = cfg["HOST_NAME"]
        mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
        
        # files.log_items MAC address to REPL
        mystring = [hex(i) for i in wifi.radio.mac_address]
        files.log_item("My MAC addr:" + str(mystring))

        ip_address = str(wifi.radio.ipv4_address)

        # files.log_items IP address to REPL
        files.log_item("My IP address is" + ip_address)
        files.log_item("Connected to WiFi")
        
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
            return FileResponse(request, "/sd/mui.min.css", "/")
        
        @server.route("/mui.min.js")
        def base(request: HTTPRequest):
            return FileResponse(request, "/sd/mui.min.js", "/")
        
        @server.route("/animation", [POST])
        def buttonpress(request: Request):
            global cfg, c_run, ts_mode
            raw_text = request.raw_request.decode("utf8")
            if "customers_owned_music_" in raw_text:
                for sound_file in cus_o:
                    if sound_file in raw_text:
                        cfg["option_selected"] = sound_file
                        animation(cfg["option_selected"])
                        break
            else: # built in animations
                for sound_file in mnu_o:
                    if sound_file  in raw_text:
                        cfg["option_selected"] = sound_file
                        animation(cfg["option_selected"])
                        break
            files.write_json_file("/sd/config_christmas_park.json",cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")
        
        @server.route("/defaults", [POST])
        def buttonpress(request: Request):
            global cfg
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in ts_json:
                    time_stamps = files.read_json_file("/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file("/sd/christmas_park_sounds/"+time_stamp_file+".json",time_stamps)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()      
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/mode", [POST])
        def buttonpress(request: Request):
            global cfg, c_run, ts_mode
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "cont_mode_on" in raw_text: 
                c_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                c_run = False
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
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                cfg["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json",cfg)
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
            files.write_json_file("/sd/config_christmas_park.json",cfg)       
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
            changeVolume(data_object["action"])
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
                print("action: " + data_object["action"]+ " data: " + cfg["light_string"])
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                updateLightString()
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                return Response(request, cfg["light_string"])
            if cfg["light_string"] =="":
                cfg["light_string"] = data_object["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + "," + data_object["text"]
            print("action: " + data_object["action"]+ " data: " + cfg["light_string"])
            files.write_json_file("/sd/config_christmas_park.json",cfg)
            updateLightString()
            play_audio_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, cfg["light_string"])
        
        @server.route("/get-light-string", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["light_string"])
        
        @server.route("/get-customers-sound-tracks", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(cus_o)
            return Response(request, my_string)
        
        @server.route("/get-built-in-sound-tracks", [POST])
        def buttonpress(request: Request):
            sounds = []
            sounds.extend(snd_o)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)
           
    except Exception as e:
        web = False
        files.log_item(e)
 
gc_col("web server")

import utilities

gc_col("utilities")

################################################################################
# Global Methods
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
        volume =100
    if volume < 1:
        volume = 1
    cfg["volume"] = str(volume)
    cfg["volume_pot"] = False
    files.write_json_file("/sd/config_christmas_park.json",cfg)
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
    mix.voice[0].play( wave0, loop=False )
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
    speak_this_string(song_number,False)    
    
def speak_light_string(play_intro):
    try:
        elements = cfg["light_string"].split(',')
        if play_intro :
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
    if cfg["HOST_NAME"]== "animator-christmas-park":
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
    try:
        if file_name == "random built in":
            highest_index = len(snd_o) - 1
            current_option_selected = snd_o[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(snd_o)>1:
                current_option_selected = snd_o[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random my":
            highest_index = len(cus_o) - 1
            current_option_selected = cus_o[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(cus_o)>1:
                current_option_selected = cus_o[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random all":
            highest_index = len(all_o) - 1
            current_option_selected = all_o[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(all_o)>1:
                current_option_selected = all_o[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        if ts_mode:
            animation_timestamp(current_option_selected)
        else:
            animation_light_show(current_option_selected)
    except:
        no_user_soundtrack_found()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")
         
def animation_light_show(file_name):
    global ts_mode
    rand_index_low = 1
    rand_index_high = 3
    if file_name == "silent night":
        rand_index_low = 3
        rand_index_high = 3
    if file_name == "away in a manger":
        rand_index_low = 3
        rand_index_high = 3

    customers_file = "customers_owned_music_" in file_name
    
    if customers_file:
        file_name=file_name.replace("customers_owned_music_","")
        try:
            flash_time_dictionary = files.read_json_file("/sd/customers_owned_music/" + file_name + ".json")
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
        flash_time_dictionary = files.read_json_file("/sd/christmas_park_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    if customers_file:
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    my_index = 0
    
    multicolor(.01)
    while True:
        previous_index=0
        timeElasped = time.monotonic()-startTime
        if flashTimeIndex < len(flashTime)-2:
            duration = flashTime[flashTimeIndex+1]-flashTime[flashTimeIndex]-0.25
        else:
            duration =  0.25
        if duration < 0: duration = 0
        if timeElasped > flashTime[flashTimeIndex] - 0.25:
            print("time elasped: " + str(timeElasped) + " Timestamp: " + str(flashTime[flashTimeIndex]))
            flashTimeIndex += 1
            my_index = random.randint(rand_index_low, rand_index_high)
            while my_index == previous_index:
                print("regenerating random selection")
                my_index = random.randint(rand_index_low, rand_index_high)
            if my_index == 1:
                rainbow(.005,duration)
            elif my_index == 2:
                multicolor(.01)
                upd_vol(duration)
            elif my_index == 3:
                fire(duration)
            elif my_index == 4:   
                christmas_fire(duration)
            elif my_index == 5:
                multicolor(duration)
            previous_index = my_index
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        l_sw.update()
        #if timeElasped > 2: mixer.voice[0].stop()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            led.fill((0, 0, 0))
            led.show()
            break
        upd_vol(.001)
         
def animation_timestamp(file_name):
    print("time stamp mode")
    global ts_mode
 
    customers_file = "customers_owned_music_" in file_name
    
    my_time_stamps = files.read_json_file("/sd/time_stamp_defaults/timestamp_mode.json")
    my_time_stamps["flashTime"]=[]
    
    file_name = file_name.replace("customers_owned_music_","")

    if customers_file :
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mix.voice[0].play( wave0, loop=False )
    
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
                files.write_json_file("/sd/customers_owned_music/" + file_name + ".json",my_time_stamps)
            else:   
                files.write_json_file("/sd/christmas_park_sounds/" + file_name + ".json",my_time_stamps)
            break

    ts_mode = False
    play_audio_0("/sd/mvc/timestamp_saved.wav")
    play_audio_0("/sd/mvc/timestamp_mode_off.wav")
    play_audio_0("/sd/mvc/animations_are_now_active.wav")

##############################
# Led color effects
        
def change_color():
    led.brightness = 1.0
    color_r = random.randint(0, 255)
    color_g = random.randint(0, 255)
    color_b = random.randint(0, 255)     
    led.fill((color_r, color_g, color_b))
    led.show()

def rainbow(speed,duration):
    startTime = time.monotonic()
    for j in range(0,255,1):
        for i in range(n_px):
            pixel_index = (i * 256 // n_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        upd_vol(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(n_px):
            pixel_index = (i * 256 // n_px) + j
            led[i] = colorwheel(pixel_index & 255)
        led.show()
        upd_vol(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return

def fire(duration):
    startTime = time.monotonic()
    led.brightness = 1.0

    fire_indexes = []
    
    fire_indexes.extend(ornmnts)
    fire_indexes.extend(cane_s)
    fire_indexes.extend(cane_e)
    
    star_indexes = []
    star_indexes.extend(stars)
    
    for i in star_indexes:
        led[i] = (255,255,255)
        
    branches_indexes = []
    branches_indexes.extend((brnchs))
    
    for i in branches_indexes:
        led[i] = (50,50,50)
    
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    
    print (len(fire_indexes))

    #Flicker, based on our initial RGB values
    while True:
        #for i in range (0, num_pixels):
        for i in fire_indexes:
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            led[i] = (r1,g1,b1)
            led.show()
        upd_vol(random.uniform(0.05,0.1))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
               
def christmas_fire(duration):
    startTime=time.monotonic()
    led.brightness = 1.0

    #Flicker, based on our initial RGB values
    while True:
        for i in range (0, n_px):
            red = random.randint(0,255)
            green = random.randint(0,255)
            blue = random.randint(0,255)
            whichColor = random.randint(0,1)
            if whichColor == 0:
                r1=red
                g1=0
                b1=0
            elif whichColor == 1:
                r1=0
                g1=green
                b1=0
            elif whichColor == 2:
                r1=0
                g1=0
                b1=blue
            led[i] = (r1,g1,b1)
            led.show()
        upd_vol(random.uniform(.2,0.3))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
         
def bounds(my_color, lower, upper):
    if (my_color < lower): my_color = lower
    if (my_color > upper): my_color = upper
    return my_color

def multicolor(duration):
    startTime=time.monotonic()
    led.brightness = 1.0

    #Flicker, based on our initial RGB values
    while True:
        for i in range (0, n_px):
            red = random.randint(128,255)
            green = random.randint(128,255)
            blue = random.randint(128,255)
            whichColor = random.randint(0,2)
            if whichColor == 0:
                r1=red
                g1=0
                b1=0
            elif whichColor == 1:
                r1=0
                g1=green
                b1=0
            elif whichColor == 2:
                r1=0
                g1=0
                b1=blue
            led[i] = (r1,g1,b1)
            led.show()
        upd_vol(random.uniform(.2,0.3))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
 
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
        play_audio_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global c_run
        switch_state = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if c_run:
                c_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                c_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or c_run:
            animation(cfg["option_selected"])
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
            play_audio_0("/sd/mvc/" + m_mnu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(m_mnu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = m_mnu[self.selectedMenuIndex]
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
                play_audio_0("/sd/mvc/all_changes_complete.wav")
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
                    wave0 = audiocore.WaveFile(open("/sd/christmas_park_options_voice_commands/option_" + mnu_o[self.optionIndex] + ".wav" , "rb"))
                    mix.voice[0].play( wave0, loop=False )
                except:
                    speak_song_number(str(self.optionIndex+1))
                self.currentOption = self.optionIndex
                self.optionIndex +=1
                if self.optionIndex > len(mnu_o)-1:
                    self.optionIndex = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = mnu_o[self.currentOption]
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                wave0 = audiocore.WaveFile(open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play( wave0, loop=False )
                while mix.voice[0].playing:
                    pass
            machine.go_to_state('base_state')

class AddSoundsAnimate(State):

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
            play_audio_0("/sd/mvc/" + add_s[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(add_s)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = add_s[self.selectedMenuIndex]
            if selected_menu_item == "hear_instructions":
                play_audio_0("/sd/mvc/create_sound_track_files.wav")
            elif selected_menu_item == "timestamp_mode_on":
                ts_mode = True
                play_audio_0("/sd/mvc/timestamp_mode_on.wav")
                play_audio_0("/sd/mvc/timestamp_instructions.wav")
                machine.go_to_state('base_state') 
            elif selected_menu_item == "timestamp_mode_off":
                ts_mode = False
                play_audio_0("/sd/mvc/timestamp_mode_off.wav")
                        
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
                    
class VolumeSettings(State):

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
            play_audio_0("/sd/mvc/" + v_set[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(v_set)-1:
                self.menuIndex = 0
        if r_sw.fell:
                selected_menu_item = v_set[self.selectedMenuIndex]
                if selected_menu_item == "volume_level_adjustment":
                    play_audio_0("/sd/mvc/volume_adjustment_menu.wav")
                    done = False
                    while not done: 
                        switch_state = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
                        if switch_state == "left":
                            changeVolume("lower")
                        elif switch_state == "right":
                            changeVolume("raise")
                        elif switch_state == "right_held":
                            files.write_json_file("/sd/config_christmas_park.json",cfg)
                            play_audio_0("/sd/mvc/all_changes_complete.wav")
                            done = True
                            machine.go_to_state('base_state')
                        upd_vol(0.1)
                        pass
                elif selected_menu_item == "volume_pot_off":
                    cfg["volume_pot"] = False
                    if cfg["volume"] == 0:
                        cfg["volume"] = 10
                    files.write_json_file("/sd/config_christmas_park.json",cfg)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state') 
                elif selected_menu_item == "volume_pot_on":
                    cfg["volume_pot"] = True
                    files.write_json_file("/sd/config_christmas_park.json",cfg)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
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
            play_audio_0("/sd/mvc/" + w_mnu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(w_mnu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = w_mnu[self.selectedMenuIndex]
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
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')   

class LightStringSetupMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0
        self.lightIndex = 0
        self.selectedLightIndex = 0

    @property
    def name(self):
        return 'light_string_setup_menu'

    def enter(self, machine):
        files.log_item('Set Web Options')
        play_audio_0("/sd/mvc/light_string_setup_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + l_mnu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(l_mnu)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = l_mnu[self.selectedMenuIndex]
            if selected_menu_item == "hear_light_setup_instructions":
                play_audio_0("/sd/mvc/park_string_instructions.wav")
            elif selected_menu_item == "reset_lights_defaults":
                reset_lights_to_defaults()
                play_audio_0("/sd/mvc/lights_reset_to.wav")
                speak_light_string(False)
            elif selected_menu_item == "hear_current_light_settings": 
                speak_light_string(True)
            elif selected_menu_item == "clear_light_string":
                cfg["light_string"] = ""
                play_audio_0("/sd/mvc/lights_cleared.wav") 
            elif selected_menu_item == "add_lights":
                play_audio_0("/sd/mvc/add_light_menu.wav")
                adding = True
                while adding:
                    switch_state = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
                    if switch_state == "left":
                        self.lightIndex -=1
                        if self.lightIndex < 0:
                            self.lightIndex = len(l_opt)-1
                        self.selectedLightIndex = self.lightIndex   
                        play_audio_0("/sd/mvc/" + l_opt[self.lightIndex] + ".wav") 
                    elif switch_state == "right":
                        self.menuIndex +=1
                        if self.menuIndex > len(l_opt)-1:
                            self.menuIndex = 0
                        self.selectedMenuIndex = self.menuIndex
                        play_audio_0("/sd/mvc/" + l_opt[self.menuIndex] + ".wav") 
                    elif switch_state == "right_held":
                        if cfg["light_string"] == "":
                            cfg["light_string"] = l_opt[self.selectedMenuIndex]
                        else:
                            cfg["light_string"] = cfg["light_string"] + "," + l_opt[self.selectedMenuIndex]
                        play_audio_0("/sd/mvc/" + l_opt[self.selectedMenuIndex] + ".wav")
                        play_audio_0("/sd/mvc/added.wav")    
                    elif switch_state == "left_held":
                        files.write_json_file("/sd/config_christmas_park.json",cfg)   
                        updateLightString()
                        play_audio_0("/sd/mvc/all_changes_complete.wav")
                        adding = False
                        machine.go_to_state('base_state')  
                    upd_vol(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_christmas_park.json",cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                updateLightString()
                machine.go_to_state('base_state')  

###############################################################################
# Create the state machine

state_machine = StateMachine()
state_machine.add_state(BaseState())
state_machine.add_state(MainMenu())
state_machine.add_state(ChooseSounds())
state_machine.add_state(AddSoundsAnimate())
state_machine.add_state(VolumeSettings())
state_machine.add_state(WebOptions())
state_machine.add_state(LightStringSetupMenu())

au_en.value = True

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

state_machine.go_to_state('base_state')   
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    state_machine.update()
    upd_vol(.02)
    if (web):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
   
