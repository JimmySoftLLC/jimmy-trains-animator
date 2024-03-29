import gc
import files

def garbage_collect(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item( "Point " + collection_point + " Available memory: {} bytes".format(start_mem) )
    
garbage_collect("Imports gc, files")

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

def reset_pico():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
    
garbage_collect("imports")
################################################################################
# Setup hardware

analog_in = AnalogIn(board.A0)

def get_voltage(pin, wait_for):
    my_increment = wait_for/10
    pin_value = 0
    for _ in range(10):
        time.sleep(my_increment)
        pin_value += 1
        pin_value = pin_value / 10
    return (pin.value) / 65536

audio_enable = digitalio.DigitalInOut(board.GP28) #22 animator tiny, #28 standard size
audio_enable.direction = digitalio.Direction.OUTPUT
audio_enable.value = False

# Setup the switches
SWITCH_1_PIN = board.GP6 #S1 on animator board
SWITCH_2_PIN = board.GP7 #S2 on animator board

switch_io_1 = digitalio.DigitalInOut(SWITCH_1_PIN)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP
left_switch = Debouncer(switch_io_1)

switch_io_2 = digitalio.DigitalInOut(SWITCH_2_PIN)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP
right_switch = Debouncer(switch_io_2)

# setup audio on the i2s bus
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
audio_enable.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer
num_voices = 1
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,bits_per_sample=16, samples_signed=True, buffer_size=4096)
audio.play(mixer)

volume = .2
mixer.voice[0].level = volume

try:
  sdcard = sdcardio.SDCard(spi, cs)
  vfs = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")
except:
    wave0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    cardInserted = False
    while not cardInserted:
        left_switch.update()
        if left_switch.fell:
            try:
                sdcard = sdcardio.SDCard(spi, cs)
                vfs = storage.VfsFat(sdcard)
                storage.mount(vfs, "/sd")
                cardInserted = True
                wave0 = audiocore.WaveFile(open("/sd/mvc/micro_sd_card_success.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            except:
                wave0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            
audio_enable.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

config = files.read_json_file("/sd/config_lightning.json")

sound_options =  files.return_directory("", "/sd/lightning_sounds", ".wav")

my_sound_options = files.return_directory("customers_owned_music_", "/sd/customers_owned_music", ".wav")

all_sound_options = []
all_sound_options.extend(sound_options)
all_sound_options.extend(my_sound_options)

menu_sound_options = []
menu_sound_options.extend(sound_options)
rnd_options = ['random all','random built in','random my']
menu_sound_options.extend(rnd_options)
menu_sound_options.extend(my_sound_options)

time_stamp_jsons = files.return_directory("", "/sd/time_stamp_defaults", ".json")

serve_webpage = config["serve_webpage"]

config_main_menu = files.read_json_file("/sd/mvc/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_web_menu = files.read_json_file("/sd/mvc/web_menu.json")
web_menu = config_web_menu["web_menu"]

config_light_string_menu = files.read_json_file("/sd/mvc/light_string_menu.json")
light_string_menu = config_light_string_menu["light_string_menu"]

config_light_options = files.read_json_file("/sd/mvc/light_options.json")
light_options = config_light_options["light_options"]

volume_settings_options = files.read_json_file("/sd/mvc/volume_settings.json")
volume_settings = volume_settings_options["volume_settings"]

add_sounds_animate_options = files.read_json_file("/sd/mvc/add_sounds_animate.json")
add_sounds_animate = add_sounds_animate_options["add_sounds_animate"]

garbage_collect("sd card variables")

continuous_run = False
time_stamp_mode = False

################################################################################
# Setup neo pixels
bars = []
bolts = []
nood = []

bar_array = []
bolt_array = []

num_pixels = 0

ledStrip = neopixel.NeoPixel(board.GP10, num_pixels) #GP10 is M1, GP13 is M4, GP15 is M6

def return_bar_array():
    my_indexes = []
    for bar in bars:
        for led_index in bar:
            start_index=led_index
            break
        for led_index in range(0,10):
            my_indexes.append(led_index+start_index)
    return my_indexes

def return_bolt_array():
    my_indexes = []
    for bolt in bolts:
        for led_index in bolt:
            start_index=led_index
            break
        if len(bolt) == 4:
            for led_index in range(0,4):
                my_indexes.append(led_index+start_index)
        if len(bolt) == 1:
            for led_index in range(0,1):
                my_indexes.append(led_index+start_index)
    return my_indexes

def runLightTest():
    global bar_array, bolt_array
    bar_array = return_bar_array()
    bolt_array = return_bolt_array()
    for bar in bars:
        for led_index in bar:
            ledStrip[led_index]=(50, 50, 50)
        ledStrip.show()
        time.sleep(.3)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
    for bolt in bolts:
        for led_index in bolt:
            ledStrip[led_index]=(50, 50, 50)
        ledStrip.show()
        time.sleep(.3)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
    for n in nood:
        ledStrip[n[0]]=(50, 50, 50)
        ledStrip.show()
        time.sleep(.3)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
    
def updateLightString():
    global bars, bolts, nood, num_pixels, ledStrip, num_pixels
    bars = []
    bolts = []
    nood = []

    num_pixels = 0
    
    elements = config["light_string"].split(',')

    for element in elements:
        parts = element.split('-')
        if len(parts) == 2:
            lightning_type, quantity = parts
            quantity = int(quantity)
            if lightning_type == 'bar':
                sequence = list(range(num_pixels, num_pixels + quantity))
                bars.append(sequence)
                num_pixels += quantity
            elif lightning_type == 'bolt' and quantity < 4:
                sequence = [num_pixels,quantity]
                nood.append(sequence)
                num_pixels += 1
            elif lightning_type == 'bolt' and quantity==4:
                sequence = list(range(num_pixels, num_pixels + quantity))
                bolts.append(sequence)
                num_pixels += quantity

    print ("Number of pixels total: ", num_pixels)
    ledStrip.deinit()
    garbage_collect("Deinit ledStrip")
    ledStrip = neopixel.NeoPixel(board.GP10, num_pixels) #GP10 is M1, GP13 is M4, GP15 is M6
    ledStrip.auto_write = False
    ledStrip.brightness = 1.0
    runLightTest()
    
updateLightString()
garbage_collect("Neopixels setup")

################################################################################
# Setup wifi and web server

if (serve_webpage):
    import socketpool
    import mdns
    garbage_collect("config wifi imports")
    import wifi
    garbage_collect("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
    garbage_collect("config wifi imports")

    files.log_item("Connecting to WiFi")

    #default for manufacturing and shows
    WIFI_SSID="jimmytrainsguest"
    WIFI_PASSWORD=""

    try:
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        garbage_collect("wifi env")
        print("Using env ssid and password")
    except:
        print("Using default ssid and password")

    try:
        # connect to your SSID
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        garbage_collect("wifi connect")
        
        # setup mdns server
        mdns_server = mdns.Server(wifi.radio)
        mdns_server.hostname = config["HOST_NAME"]
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
        garbage_collect("wifi server")
        
        ################################################################################
        # Setup routes

        @server.route("/")
        def base(request: HTTPRequest):
            garbage_collect("Home page.")
            return FileResponse(request, "index.html", "/")
        
        @server.route("/mui.min.css")
        def base(request: HTTPRequest):
            return FileResponse(request, "mui.min.css", "/")
        
        @server.route("/mui.min.js")
        def base(request: HTTPRequest):
            return FileResponse(request, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def buttonpress(request: Request):
            global config, continuous_run, time_stamp_mode
            raw_text = request.raw_request.decode("utf8")
            if "customers_owned_music_" in raw_text:
                for sound_file in my_sound_options:
                    if sound_file in raw_text:
                        config["option_selected"] = sound_file
                        animation(config["option_selected"])
                        break
            else: # built in animations
                for sound_file in menu_sound_options:
                    if sound_file  in raw_text:
                        config["option_selected"] = sound_file
                        animation(config["option_selected"])
                        break
            files.write_json_file("/sd/config_lightning.json",config)
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        @server.route("/defaults", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in time_stamp_jsons:
                    time_stamps = files.read_json_file("/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file("/sd/lightning_sounds/"+time_stamp_file+".json",time_stamps)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()      
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')
            elif "reset_default_colors" in raw_text:
                command_sent = "reset_default_colors"
                reset_default_colors()    
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                my_string = files.json_stringify({"bars":config["bars"],"bolts":config["bolts"],"variation":config["variation"]})
                state_machine.go_to_state('base_state')
                return Response(request, my_string)
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/mode", [POST])
        def buttonpress(request: Request):
            global config, continuous_run, time_stamp_mode
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "cont_mode_on" in raw_text: 
                continuous_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                continuous_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            elif "timestamp_mode_on" in raw_text: 
                time_stamp_mode = True
                play_audio_0("/sd/mvc/timestamp_mode_on.wav")
                play_audio_0("/sd/mvc/timestamp_instructions.wav")
            elif "timestamp_mode_off" in raw_text: 
                time_stamp_mode = False
                play_audio_0("/sd/mvc/timestamp_mode_off.wav") 
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/speaker", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                command_sent = "speaker_test"
                play_audio_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                command_sent = "volume_pot_off"
                config["volume_pot"] = False
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                config["volume_pot"] = True
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/lights", [POST])
        def buttonpress(request: Request):
            raw_text = request.raw_request.decode("utf8")
            if "set_to_red" in raw_text:
                ledStrip.fill((255, 0, 0))
                ledStrip.show()
            elif "set_to_green" in raw_text:
                ledStrip.fill((0, 255, 0))
                ledStrip.show()
            elif "set_to_blue" in raw_text:
                ledStrip.fill((0, 0, 255))
                ledStrip.show()
            elif "set_to_white" in raw_text:
                ledStrip.fill((255, 255, 255))
                ledStrip.show()
            elif "set_to_0" in raw_text:
                ledStrip.brightness = 0.0
                ledStrip.show()
            elif "set_to_20" in raw_text:
                ledStrip.brightness = 0.2
                ledStrip.show()
            elif "set_to_40" in raw_text:
                ledStrip.brightness = 0.4
                ledStrip.show()
            elif "set_to_60" in raw_text:
                ledStrip.brightness = 0.6
                ledStrip.show()
            elif "set_to_80" in raw_text:
                ledStrip.brightness = 0.8
                ledStrip.show()
            elif "set_to_100" in raw_text:
                ledStrip.brightness = 1.0
                ledStrip.show()
            return Response(request, "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            config["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/config_lightning.json",config)       
            mdns_server.hostname = config["HOST_NAME"]
            speak_webpage()
            return Response(request, config["HOST_NAME"])
        
        @server.route("/get-host-name", [POST])
        def buttonpress(request: Request):
            return Response(request, config["HOST_NAME"])
        
        @server.route("/update-volume", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            changeVolume(data_object["action"])
            return Response(request, config["volume"])
        
        @server.route("/get-volume", [POST])
        def buttonpress(request: Request):
            return Response(request, config["volume"])
        
        @server.route("/update-light-string", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            if data_object["action"] == "save" or data_object["action"] == "clear" or data_object["action"] == "defaults":
                config["light_string"] = data_object["text"]
                print("action: " + data_object["action"]+ " data: " + config["light_string"])
                files.write_json_file("/sd/config_lightning.json",config)
                updateLightString()
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                return Response(request, config["light_string"])
            if config["light_string"] =="":
                config["light_string"] = data_object["text"]
            else:
                config["light_string"] = config["light_string"] + "," + data_object["text"]
            print("action: " + data_object["action"]+ " data: " + config["light_string"])
            files.write_json_file("/sd/config_lightning.json",config)
            updateLightString()
            play_audio_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, config["light_string"])
        
        @server.route("/get-light-string", [POST])
        def buttonpress(request: Request):
            return Response(request, config["light_string"])
        
        @server.route("/get-customers-sound-tracks", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(my_sound_options)
            return Response(request, my_string)
        
        @server.route("/get-built-in-sound-tracks", [POST])
        def buttonpress(request: Request):
            sounds = []
            sounds.extend(sound_options)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)
        
        @server.route("/get-bar-colors", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(config["bars"])
            return Response(request, my_string)
        
        @server.route("/get-bolt-colors", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(config["bolts"])
            return Response(request, my_string)
        
        @server.route("/get-color-variation", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(config["variation"])
            return Response(request, my_string)

        @server.route("/set-lights", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            command_sent = "set-lights"
            if data_object["item"] == "bars":
                config["bars"] = { "r": data_object["r"], "g": data_object["g"], "b": data_object["b"] }
                bar_indexes = []
                bar_indexes.extend(bar_array)
                for i in bar_indexes:
                    ledStrip[i] = (data_object["r"], data_object["g"], data_object["b"])
                    ledStrip.show()        
            elif data_object["item"] == "bolts":
                config["bolts"] = { "r": data_object["r"], "g": data_object["g"], "b": data_object["b"] }
                bolt_indexes = []
                bolt_indexes.extend(bolt_array)
                for i in bolt_indexes:
                    ledStrip[i] = (data_object["r"], data_object["g"], data_object["b"])
                    ledStrip.show()
            elif data_object["item"] == "variationBolt":
                print(data_object)
                config["variation"] = { "r1": data_object["r"], "g1": data_object["g"], "b1": data_object["b"], "r2": config["variation"]["r2"], "g2": config["variation"]["g2"], "b2": config["variation"]["b2"] }
            elif data_object["item"] == "variationBar":
                config["variation"] = { "r1": config["variation"]["r1"], "g1": config["variation"]["g1"], "b1": config["variation"]["b1"],"r2": data_object["r"], "g2": data_object["g"], "b2": data_object["b"] }
            files.write_json_file("/sd/config_lightning.json",config)
            return Response(request, command_sent)
           
    except Exception as e:
        serve_webpage = False
        files.log_item(e)
 
garbage_collect("web server")

import utilities

garbage_collect("utilities")

################################################################################
# Global Methods
def sleepAndUpdateVolume(seconds):
    if config["volume_pot"]:
        volume = get_voltage(analog_in, seconds)
        mixer.voice[0].level = volume
    else:
        try:
            volume = int(config["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mixer.voice[0].level = volume
        time.sleep(seconds)

def reset_lights_to_defaults():
    global config
    config["light_string"] = "bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4"
    

def reset_default_colors():
    global config
    config["bars"] = { "r": 60, "g": 18, "b": 5 }
    config["bolts"] = { "r": 60, "g": 18, "b": 5 }
    config["variation"] = { "r1": 20, "g1": 8, "b1": 5 , "r2": 20, "g2": 8, "b2": 5 }

def reset_to_defaults():
    global config
    config["volume_pot"] = True
    config["HOST_NAME"] = "animator-lightning"
    config["option_selected"] = "thunder birds rain"
    config["volume"] = "20"
    config["can_cancel"] = True
    reset_lights_to_defaults()
    reset_default_colors()
    
def changeVolume(action):
    volume = int(config["volume"])
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
    config["volume"] = str(volume)
    config["volume_pot"] = False
    files.write_json_file("/sd/config_lightning.json",config)
    play_audio_0("/sd/mvc/volume.wav")
    speak_this_string(config["volume"], False)

################################################################################
# Dialog and sound play methods

def play_audio_0(file_name):
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            sleepAndUpdateVolume(0.02)
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        shortCircuitDialog()

def stop_audio_0():
    mixer.voice[0].stop()
    while mixer.voice[0].playing:
        pass

def shortCircuitDialog():
    sleepAndUpdateVolume(0.02)
    left_switch.update()
    if left_switch.fell:
        mixer.voice[0].stop()
        
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
        elements = config["light_string"].split(',')
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            break
        if right_switch.fell:
            play_audio_0("/sd/mvc/create_sound_track_files.wav")
            break

def speak_webpage():
    play_audio_0("/sd/mvc/animator_available_on_network.wav")
    play_audio_0("/sd/mvc/to_access_type.wav")
    if config["HOST_NAME"]== "animator-lightning":
        play_audio_0("/sd/mvc/animator_dash_lightning.wav")
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")
    else:
        speak_this_string(config["HOST_NAME"], True)
    play_audio_0("/sd/mvc/in_your_browser.wav") 
        
################################################################################
# animations

last_option = ""
      
def animation(file_name):
    global config, last_option
    print("Filename: " + file_name)
    current_option_selected = file_name
    try:
        if file_name == "random built in":
            highest_index = len(sound_options) - 1
            current_option_selected = sound_options[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(sound_options)>1:
                current_option_selected = sound_options[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random my":
            highest_index = len(my_sound_options) - 1
            current_option_selected = my_sound_options[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(my_sound_options)>1:
                current_option_selected = my_sound_options[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        elif file_name == "random all":
            highest_index = len(all_sound_options) - 1
            current_option_selected = all_sound_options[random.randint(0, highest_index)]
            while last_option == current_option_selected and len(all_sound_options)>1:
                current_option_selected = all_sound_options[random.randint(0, highest_index)]
            last_option = current_option_selected
            print("Random sound option: " + file_name)
            print("Sound file: " + current_option_selected)
        if time_stamp_mode:
            animation_timestamp(current_option_selected)
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
                thunder_and_lightning(current_option_selected)
    except:
       no_user_soundtrack_found()
       config["option_selected"] = "random built in"
       return
    garbage_collect("Animation complete.")
         
def animation_light_show(file_name):
    global time_stamp_mode
    rand_index_low = 1
    rand_index_high = 3
    
    if file_name == "fireworks":
        rand_index_low = 4
        rand_index_high = 4

    customers_file = "customers_owned_music_" in file_name
    
    if customers_file:
        file_name=file_name.replace("customers_owned_music_","")
        try:
            flash_time_dictionary = files.read_json_file("/sd/customers_owned_music/" + file_name + ".json")
        except:
            play_audio_0("/sd/mvc/no_timestamp_file_found.wav")
            while True:
                left_switch.update()
                right_switch.update()
                if left_switch.fell:
                    time_stamp_mode = False
                    return
                if right_switch.fell:
                    time_stamp_mode = True
                    play_audio_0("/sd/mvc/timestamp_instructions.wav")
                    return
    else:
        flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    if customers_file:
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    my_index = 0
    
    multicolor(.01)
    while True:
        previous_index=0
        timeElapsed = time.monotonic()-startTime
        if flashTimeIndex < len(flashTime)-2:
            duration = flashTime[flashTimeIndex+1]-flashTime[flashTimeIndex]-0.25
        else:
            duration =  0.25
        if duration < 0: duration = 0
        if timeElapsed > flashTime[flashTimeIndex] - 0.25:
            print("Time elapsed: " + str(timeElapsed) + " Timestamp: " + str(flashTime[flashTimeIndex])+ " Dif: " + str(timeElapsed-flashTime[flashTimeIndex]))
            flashTimeIndex += 1
            my_index = random.randint(rand_index_low, rand_index_high)
            while my_index == previous_index:
                my_index = random.randint(rand_index_low, rand_index_high)
            if my_index == 1:
                rainbow(.005,duration)
            elif my_index == 2:
                multicolor(.01)
                sleepAndUpdateVolume(duration)
            elif my_index == 3:
                candle(duration)
            elif my_index == 4:
                firework(duration)
            previous_index = my_index
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        #if timeElasped > 2: mixer.voice[0].stop()
        if left_switch.fell and config["can_cancel"]:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            break
        sleepAndUpdateVolume(.001)
         
def animation_timestamp(file_name):
    print("Time stamp mode:")
    global time_stamp_mode
 
    customers_file = "customers_owned_music_" in file_name
    
    my_time_stamps = files.read_json_file("/sd/time_stamp_defaults/timestamp mode.json")
    my_time_stamps["flashTime"]=[]
    
    file_name = file_name.replace("customers_owned_music_","")

    if customers_file :
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    
    startTime = time.monotonic()
    sleepAndUpdateVolume(.1)

    while True:
        time_elapsed = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            my_time_stamps["flashTime"].append(time_elapsed) 
            print(time_elapsed)
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            my_time_stamps["flashTime"].append(5000)
            if customers_file:
                files.write_json_file("/sd/customers_owned_music/" + file_name + ".json",my_time_stamps)
            else:   
                files.write_json_file("/sd/lightning_sounds/" + file_name + ".json",my_time_stamps)
            break

    time_stamp_mode = False
    play_audio_0("/sd/mvc/timestamp_saved.wav")
    play_audio_0("/sd/mvc/timestamp_mode_off.wav")
    play_audio_0("/sd/mvc/animations_are_now_active.wav")

def thunder_and_lightning(file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()

    while True:
        sleepAndUpdateVolume(.1)
        time_elapsed = time.monotonic()-startTime
        rand_time = flashTime[flashTimeIndex] - random.uniform(.5, 1) #amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
        if time_elapsed > rand_time:
            print("Time elapsed: " + str(time_elapsed) + " Timestamp: " + str(rand_time)+ " Dif: " + str(time_elapsed-rand_time))
            flashTimeIndex += 1
            lightning()
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell and config["can_cancel"]:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            break

##############################
# Led color effects

def rainbow(speed,duration):
    startTime = time.monotonic()
    for j in range(0,255,1):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return

def candle(duration):
    startTime = time.monotonic()
    ledStrip.brightness = 1.0

    bar_indexes = []
    bar_indexes.extend(bar_array)
    
    bolt_indexes = []
    bolt_indexes.extend(bolt_array)

    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    
    for i in bolt_indexes:
        ledStrip[i] = (r,g,b)

    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)

    #Flicker, based on our initial RGB values
    while True:
        for i in bar_indexes:
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            ledStrip[i] = (r1,g1,b1)
            ledStrip.show()
        sleepAndUpdateVolume(random.uniform(0.05,0.1))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
        
def simulate_firework_spread(arr):
    center = len(arr) // 2
    for i in range(center):
        left_index = center - 1 - i
        right_index = center + i
        yield (arr[left_index], arr[right_index])
        
def reset_bars():
    for bar in bars:
        for i in bar:
            ledStrip[i] = (0,0,0)
            
def red_white_blue():
    i = random.randint(0,2)
    if i == 0: #white
        r = 255
        g = 255
        b = 255
    if i == 1: #red
        r = 255
        g = 0
        b = 0
    if i == 2: #blue
        r = 0
        g = 0
        b = 255
    return r, g, b
        
def firework(duration):
    startTime = time.monotonic()
    ledStrip.brightness = 1.0

    # choose which bar none to all to fire
    barToFire = []
    for index, my_array in enumerate(bars):
        if index == random.randint(0,(len(bars)-1)):
            barToFire.append(index)
            
    if len(barToFire)== 0:
        index == random.randint(0,(len(bars)-1))
        barToFire.append(index)
    
    for bolt in bolts:
        r , g, b =red_white_blue()
        for i in bolt:
            ledStrip[i] = (r,g,b)
    
    #Burst from center
    exit_loops = False
    while not exit_loops:
        for barIndex in barToFire:
            r , g, b =red_white_blue()
            firework_spread = simulate_firework_spread(bars[barIndex])
            for left, right in firework_spread:
                reset_bars()
                ledStrip[left] = (r,g,b)
                ledStrip[right] = (r,g,b)
                ledStrip.show()
                sleepAndUpdateVolume(0.1)
                timeElasped = time.monotonic()-startTime
                if timeElasped > duration:
                    reset_bars()
                    ledStrip.show()
                    break
            ledStrip.show()
            timeElasped = time.monotonic()-startTime
            if timeElasped > duration:
                reset_bars()
                ledStrip.show()
                break
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            reset_bars()
            ledStrip.show()
            return

def multicolor(duration):
    startTime=time.monotonic()
    ledStrip.brightness = 1.0

    #Flicker, based on our initial RGB values
    while True:
        for i in range (0, num_pixels):
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
            ledStrip[i] = (r1,g1,b1)
            ledStrip.show()
        sleepAndUpdateVolume(random.uniform(.2,0.3))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
        
def color_it(item, colorKey, addSub):
    return config[item][colorKey] + addSub

def lightning():
    # choose which bolt or no bolt to fire    
    bolt_indexes = []
    which_bolt = random.randint(-1,(len(bolts)-1))
    if which_bolt!= -1:
        for index, my_array in enumerate(bolts):
            if index == which_bolt:
                bolt_indexes.extend(my_array)
    
    # choose which bar one to all to fire
    bar_indexes = []
    for index, my_array in enumerate(bars):
        if index == random.randint(0,(len(bars)-1)):
            bar_indexes.extend(my_array)
            
    # choose which nood or no nood to fire    
    nood_indexes = []
    which_nood = random.randint(-1,(len(nood)-1))
    if which_nood!= -1:
        for index, my_array in enumerate(nood):
            if index == which_nood:
                nood_indexes.extend(my_array)
            
    if len(nood_indexes) > 0 and len(bolt_indexes) > 0 :
        which_bolt = random.randint(0,1)
        if which_bolt == 0:
            bolt_indexes = []
        else:
            nood_indexes = []
            
    # set bolt base color
    r = int(config["variation"]["r1"])
    g = int(config["variation"]["r1"])
    b = int(config["variation"]["r1"])
    bolt_r = random.randint(color_it("bolts","r",-r), color_it("bolts","r",r)) # r 40 80 60 +- 20
    bolt_g = random.randint(color_it("bolts","g",-g), color_it("bolts","g",g)) # g 10 26 18 +- 8
    bolt_b = random.randint(color_it("bolts","b",-b), color_it("bolts","b",b)) # b 0 10 5 +- 5
    
    # set bar base color
    r = int(config["variation"]["r2"])
    g = int(config["variation"]["r2"])
    b = int(config["variation"]["r2"])
    bar_r = random.randint(color_it("bolts","r",-r), color_it("bolts","r",r)) # r 40 80 60 +- 20
    bar_g = random.randint(color_it("bolts","g",-g), color_it("bolts","g",g)) # g 10 26 18 +- 8
    bar_b = random.randint(color_it("bolts","b",-b), color_it("bolts","b",b)) # b 0 10 5 +- 5

    # number of flashes
    flashCount = random.randint (5, 10)

    # flash white brightness range - 0-255
    ledStrip.brightness = random.randint(255, 255) / 255 #150 255, changed to full brightness
    
    if len(nood_indexes) > 0:
        if nood_indexes[1] == 1:
            l1=1
            l2=0
            l3=0
        if nood_indexes[1] == 2:
            l1=random.randint(0, 1)
            l2=0
            l3=random.randint(0, 1)
        if nood_indexes[1] == 3:
            l1=random.randint(0, 1)
            l2=random.randint(0, 1)
            l3=random.randint(0, 1)  
    
    for i in range(0,flashCount):
        color = random.randint(0, 100) # 0 50
        if color < 0: color = 0
        for j in range(4):
            if len(nood_indexes) > 0: ledStrip[nood_indexes[0]]=((155 + color)*l2, (155+ color)*l1, (155 + color)*l3)
            for led_index in bolt_indexes:
                ledStrip[led_index]=(bolt_r + color, bolt_g + color, bolt_b + color)
            for led_index in bar_indexes:
                ledStrip[led_index]=(bar_r + color, bar_g + color, bar_b + color)
            ledStrip.show()
            delay = random.randint(0, 75) # flash offset range - ms
            delay = delay/1000
            time.sleep(delay)
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
        
        delay = random.randint(1, 50) # time to next flash range - ms
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
         
def bounds(my_color, lower, upper):
    if (my_color < lower): my_color = lower
    if (my_color > upper): my_color = upper
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
        reset_pico()

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
        global continuous_run
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 3.0)
        if switch_state == "left_held":
            if continuous_run:
                continuous_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                continuous_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or continuous_run:
            animation(config["option_selected"])
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
        play_audio_0("/sd/mvc/main_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + main_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(main_menu)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = main_menu[self.selectedMenuIndex]
            if selected_menu_item == "choose_sounds": machine.go_to_state('choose_sounds')
            elif selected_menu_item == "add_sounds_animate": machine.go_to_state('add_sounds_animate')  
            elif selected_menu_item == "light_string_setup_menu": machine.go_to_state('light_string_setup_menu')
            elif selected_menu_item == "web_options": machine.go_to_state('web_options') 
            elif selected_menu_item == "volume_settings": machine.go_to_state('volume_settings')                 
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                try:
                    wave0 = audiocore.WaveFile(open("/sd/lightning_options_voice_commands/option_" + menu_sound_options[self.optionIndex] + ".wav" , "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                except:
                    speak_song_number(str(self.optionIndex+1))
                self.currentOption = self.optionIndex
                self.optionIndex +=1
                if self.optionIndex > len(menu_sound_options)-1:
                    self.optionIndex = 0
                while mixer.voice[0].playing:
                    pass
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                config["option_selected"] = menu_sound_options[self.currentOption]
                files.write_json_file("/sd/config_lightning.json",config)
                wave0 = audiocore.WaveFile(open("/sd/mvc/option_selected.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
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
#         left_switch.update()
#         right_switch.update()
#         if left_switch.fell:
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
        play_audio_0("/sd/mvc/volume_settings_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + volume_settings[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(volume_settings)-1:
                self.menuIndex = 0
        if right_switch.fell:
                selected_menu_item = volume_settings[self.selectedMenuIndex]
                if selected_menu_item == "volume_level_adjustment":
                    play_audio_0("/sd/mvc/volume_adjustment_menu.wav")
                    done = False
                    while not done: 
                        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 3.0)
                        if switch_state == "left":
                            changeVolume("lower")
                        elif switch_state == "right":
                            changeVolume("raise")
                        elif switch_state == "right_held":
                            files.write_json_file("/sd/config_lightning.json",config)
                            play_audio_0("/sd/mvc/all_changes_complete.wav")
                            done = True
                            machine.go_to_state('base_state')
                        sleepAndUpdateVolume(0.1)
                        pass
                elif selected_menu_item == "volume_pot_off":
                    config["volume_pot"] = False
                    if config["volume"] == 0:
                        config["volume"] = 10
                    files.write_json_file("/sd/config_lightning.json",config)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state') 
                elif selected_menu_item == "volume_pot_on":
                    config["volume_pot"] = True
                    files.write_json_file("/sd/config_lightning.json",config)
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + web_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(web_menu)-1:
                self.menuIndex = 0
        if right_switch.fell:
                selected_menu_item = web_menu[self.selectedMenuIndex]
                if selected_menu_item == "web_on":
                    config["serve_webpage"] = True
                    option_selected_announcement()
                    selectWebOptionsAnnouncement()
                elif selected_menu_item == "web_off":
                    config["serve_webpage"] = False
                    option_selected_announcement()
                    selectWebOptionsAnnouncement()
                elif selected_menu_item == "hear_url":
                    speak_this_string(config["HOST_NAME"], True)
                    selectWebOptionsAnnouncement()
                elif selected_menu_item == "hear_instr_web":
                    play_audio_0("/sd/mvc/web_instruct.wav")
                    selectWebOptionsAnnouncement()
                else:
                    files.write_json_file("/sd/config_lightning.json",config)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
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
        play_audio_0("/sd/mvc/light_string_setup_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + light_string_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(light_string_menu)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = light_string_menu[self.selectedMenuIndex]
            if selected_menu_item == "hear_light_setup_instructions":
                play_audio_0("/sd/mvc/string_instructions.wav")  
            elif selected_menu_item == "reset_lights_defaults":
                reset_lights_to_defaults()
                play_audio_0("/sd/mvc/lights_reset_to.wav")
                speak_light_string(False)
            elif selected_menu_item == "hear_current_light_settings": 
                speak_light_string(True)
            elif selected_menu_item == "clear_light_string":
                config["light_string"] = ""
                play_audio_0("/sd/mvc/lights_cleared.wav") 
            elif selected_menu_item == "add_lights":
                play_audio_0("/sd/mvc/add_light_menu.wav")
                adding = True
                while adding:
                    switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 3.0)
                    if switch_state == "left":
                        self.menuIndex -=1
                        if self.menuIndex < 0:
                            self.menuIndex = len(light_options)-1
                        self.selectedMenuIndex = self.menuIndex
                        play_audio_0("/sd/mvc/" + light_options[self.menuIndex] + ".wav") 
                    elif switch_state == "right":
                        self.menuIndex +=1
                        if self.menuIndex > len(light_options)-1:
                            self.menuIndex = 0
                        self.selectedMenuIndex = self.menuIndex
                        play_audio_0("/sd/mvc/" + light_options[self.menuIndex] + ".wav") 
                    elif switch_state == "right_held":
                        if config["light_string"] == "":
                            config["light_string"] = light_options[self.selectedMenuIndex]
                        else:
                            config["light_string"] = config["light_string"] + "," + light_options[self.selectedMenuIndex]
                        play_audio_0("/sd/mvc/" + light_options[self.selectedMenuIndex] + ".wav")
                        play_audio_0("/sd/mvc/added.wav")    
                    elif switch_state == "left_held":
                        files.write_json_file("/sd/config_lightning.json",config)   
                        updateLightString()
                        play_audio_0("/sd/mvc/all_changes_complete.wav")
                        adding = False
                        machine.go_to_state('base_state')  
                    sleepAndUpdateVolume(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                updateLightString()
                machine.go_to_state('base_state') 

###############################################################################
# Create the state machine

state_machine = StateMachine()
state_machine.add_state(BaseState())
state_machine.add_state(MainMenu())
state_machine.add_state(ChooseSounds())
#state_machine.add_state(AddSoundsAnimate())
state_machine.add_state(VolumeSettings())
state_machine.add_state(WebOptions())
state_machine.add_state(LightStringSetupMenu())

audio_enable.value = True   

if (serve_webpage):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        speak_webpage()
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        reset_pico()

state_machine.go_to_state('base_state')   
files.log_item("animator has started...")
garbage_collect("animations started.")

while True:
    state_machine.update()
    sleepAndUpdateVolume(.02)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue