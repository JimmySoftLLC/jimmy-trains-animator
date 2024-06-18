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

# Setup and analog pin to be used for volume control
# the the volume control is digital by setting mixer voice levels
analog_in = AnalogIn(board.A0)

def get_voltage(pin, wait_for):
    my_increment = wait_for/10
    pin_value = 0
    for _ in range(10):
        time.sleep(my_increment)
        pin_value += 1
        pin_value = pin_value / 10
    return (pin.value) / 65536

audio_enable = digitalio.DigitalInOut(board.GP22)
audio_enable.direction = digitalio.Direction.OUTPUT
audio_enable.value = False

# Setup the switches, there are two the Left and Right or Black and Red
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

# setup audio on the i2s bus, the animator uses the MAX98357A
# the animator can have one or two MAX98357As. one for mono two for stereo
# both MAX98357As share the same bus
# for mono the MAX98357A defaults to combine channels
# for stereo the MAX98357A SD pin is connected to VCC for right and a resistor to VCC for left
# the audio mixer is used so that volume can be control digitally it is set to stereo
# the sample_rate of the audio mixer is set to 22050 hz.  This is the max the raspberry pi pico can handle
# all files with be in the wave format instead of mp3.  This eliminates the need for decoding
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
# the sdCard holds all the media and calibration files
# if the card is missing a voice command is spoken
# the user inserts the card a presses the left button to move forward
audio_enable.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer it can play higher quality audio wav using larger wave files
# wave files are less cpu intensive since they are not compressed
num_voices = 2
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
audio.play(mixer)

volume = .2
mixer.voice[0].level = volume
mixer.voice[1].level = volume

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

config = files.read_json_file("/sd/config_christmas_park.json")

sound_options = files.return_directory("", "/sd/christmas_park_sounds", ".wav")

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

garbage_collect("config setup")

continuous_run = False
time_stamp_mode = False

################################################################################
# Setup neo pixels

grand_trees = []
canes = []
tree_ornaments = []
tree_stars = []
tree_branches  = []
cane_starts  = []
cane_ends  = []

num_pixels = 0

ledStripLeft = neopixel.NeoPixel(board.GP15, num_pixels)
ledStripMiddle = neopixel.NeoPixel(board.GP10, num_pixels)
ledStripRight = neopixel.NeoPixel(board.GP16, num_pixels)

def return_tree_parts(part):
    my_indexes = []
    for grand_tree in grand_trees:
        for led_index in grand_tree:
            start_index=led_index
            break
        if part == "ornaments":
            for led_index in range(0,7):
                my_indexes.append(led_index+start_index)
        if part == "star":
            for led_index in range(7,14):
                my_indexes.append(led_index+start_index)
        if part == "branches":        
            for led_index in range(14,21):
                my_indexes.append(led_index+start_index)
    return my_indexes

def return_cane_parts(part):
    my_indexes = []
    for cane in canes:
        for led_index in cane:
            start_index=led_index
            break
        if part == "end":
            for led_index in range(0,2):
                my_indexes.append(led_index+start_index)
        if part == "start":
            for led_index in range(2,4):
                my_indexes.append(led_index+start_index)
    return my_indexes

def show_Lights():
    ledStripMiddle.show()
    time.sleep(.3)
    ledStripMiddle.fill((0, 0, 0))
    ledStripMiddle.show()

def runLightTest():
    global tree_ornaments,tree_stars,tree_branches,cane_starts,cane_ends
    tree_ornaments = return_tree_parts("ornaments")
    tree_stars = return_tree_parts("star")
    tree_branches = return_tree_parts("branches")
    cane_starts = return_cane_parts("start")
    cane_ends = return_cane_parts("end")

    # cane test
    count = 0
    for led_index in cane_starts:
        ledStripMiddle[led_index]=(50, 50, 50)
        count+=1
        if count > 1:
            show_Lights()
            count = 0
    for led_index in cane_ends:
        ledStripMiddle[led_index]=(50, 50, 50)
        count+=1
        if count > 1:
            show_Lights()
            count = 0

    #tree test
    count = 0
    for led_index in tree_ornaments:
        ledStripMiddle[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0
    for led_index in tree_stars:
        ledStripMiddle[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0
    for led_index in tree_branches:
        ledStripMiddle[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0

def updateLightString():
    global grand_trees, canes, num_pixels, ledStripLeft, ledStripMiddle, ledStripRight, num_pixels
    grand_trees = []
    canes = []

    num_pixels = 0
    
    elements = config["light_string"].split(',')

    for element in elements:
        parts = element.split('-')

        if len(parts) == 2:
            christmas_park_type, quantity = parts
            quantity = int(quantity)

            if christmas_park_type == 'grandtree':
                grand_tree_sequence = list(range(num_pixels, num_pixels + quantity))
                grand_trees.append(grand_tree_sequence)
                num_pixels += quantity
            elif christmas_park_type == 'cane':
                cane_sequence = list(range(num_pixels, num_pixels + quantity))
                canes.append(cane_sequence)
                num_pixels += quantity

    print ("Number of pixels total: ", num_pixels)
    ledStripLeft.deinit()
    ledStripMiddle.deinit()
    ledStripRight.deinit()
    garbage_collect("Deinit ledStrip")
    ledStripLeft = neopixel.NeoPixel(board.GP15, num_pixels)
    ledStripLeft.auto_write = False
    ledStripLeft.brightness = 1.0
    ledStripMiddle = neopixel.NeoPixel(board.GP10, num_pixels)
    ledStripMiddle.auto_write = False
    ledStripMiddle.brightness = 1.0
    ledStripRight = neopixel.NeoPixel(board.GP16, num_pixels)
    ledStripRight.auto_write = False
    ledStripRight.brightness = 1.0
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
            files.write_json_file("/sd/config_christmas_park.json",config)
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        @server.route("/defaults", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in time_stamp_jsons:
                    time_stamps = files.read_json_file("/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file("/sd/christmas_park_sounds/"+time_stamp_file+".json",time_stamps)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()      
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')
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
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                config["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/lights", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "set_to_red" in raw_text:
                ledStripLeft.fill((255, 0, 0))
                ledStripLeft.show()
                ledStripMiddle.fill((255, 0, 0))
                ledStripMiddle.show()
                ledStripRight.fill((255, 0, 0))
                ledStripRight.show()
            elif "set_to_green" in raw_text:
                ledStripLeft.fill((0, 255, 0))
                ledStripLeft.show()
                ledStripMiddle.fill((0, 255, 0))
                ledStripMiddle.show()
                ledStripRight.fill((0, 255, 0))
                ledStripRight.show()
            elif "set_to_blue" in raw_text:
                ledStripLeft.fill((0, 0, 255))
                ledStripLeft.show()
                ledStripMiddle.fill((0, 0, 255))
                ledStripMiddle.show()
                ledStripRight.fill((0, 0, 255))
                ledStripRight.show()
            elif "set_to_white" in raw_text:
                ledStripLeft.fill((255, 255, 255))
                ledStripLeft.show()
                ledStripMiddle.fill((255, 255, 255))
                ledStripMiddle.show()
                ledStripRight.fill((255, 255, 255))
                ledStripRight.show()
            elif "set_to_0" in raw_text:
                ledStripMiddle.brightness = 0.0
                ledStripMiddle.show()
            elif "set_to_20" in raw_text:
                ledStripMiddle.brightness = 0.2
                ledStripMiddle.show()
            elif "set_to_40" in raw_text:
                ledStripMiddle.brightness = 0.4
                ledStripMiddle.show()
            elif "set_to_60" in raw_text:
                ledStripMiddle.brightness = 0.6
                ledStripMiddle.show()
            elif "set_to_80" in raw_text:
                ledStripMiddle.brightness = 0.8
                ledStripMiddle.show()
            elif "set_to_100" in raw_text:
                ledStripMiddle.brightness = 1.0
                ledStripMiddle.show()
            return Response(request, "Utility: " + "Utility: set lights")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            config["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/config_christmas_park.json",config)       
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
                files.write_json_file("/sd/config_christmas_park.json",config)
                updateLightString()
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                return Response(request, config["light_string"])
            if config["light_string"] =="":
                config["light_string"] = data_object["text"]
            else:
                config["light_string"] = config["light_string"] + "," + data_object["text"]
            print("action: " + data_object["action"]+ " data: " + config["light_string"])
            files.write_json_file("/sd/config_christmas_park.json",config)
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
        mixer.voice[1].level = volume
        time.sleep(seconds)

def reset_lights_to_defaults():
    global config
    config["light_string"] = "cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21"

def reset_to_defaults():
    global config
    config["volume_pot"] = True
    config["HOST_NAME"] = "animator-christmas-park"
    config["option_selected"] = "random all"
    config["volume"] = "20"
    config["can_cancel"] = True
    reset_lights_to_defaults()
    
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
    files.write_json_file("/sd/config_christmas_park.json",config)
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
    if config["HOST_NAME"]== "animator-christmas-park":
        play_audio_0("/sd/mvc/animator_dash_christmas_dash_park.wav")
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
            animation_light_show(current_option_selected)
    except:
        no_user_soundtrack_found()
        config["option_selected"] = "random built in"
        return
    garbage_collect("Animation complete.")
         
def animation_light_show(file_name):
    global time_stamp_mode
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
        flash_time_dictionary = files.read_json_file("/sd/christmas_park_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    if customers_file:
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
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
                sleepAndUpdateVolume(duration)
            elif my_index == 3:
                fire(duration)
            elif my_index == 4:   
                christmas_fire(duration)
            elif my_index == 5:
                multicolor(duration)
            previous_index = my_index
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        #if timeElasped > 2: mixer.voice[0].stop()
        if left_switch.fell and config["can_cancel"]:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStripMiddle.fill((0, 0, 0))
            ledStripMiddle.show()
            break
        sleepAndUpdateVolume(.001)
         
def animation_timestamp(file_name):
    print("time stamp mode")
    global time_stamp_mode
 
    customers_file = "customers_owned_music_" in file_name
    
    my_time_stamps = files.read_json_file("/sd/time_stamp_defaults/timestamp_mode.json")
    my_time_stamps["flashTime"]=[]
    
    file_name = file_name.replace("customers_owned_music_","")

    if customers_file :
        wave0 = audiocore.WaveFile(open("/sd/customers_owned_music/" + file_name + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(open("/sd/christmas_park_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    
    startTime = time.monotonic()
    sleepAndUpdateVolume(.1)

    while True:
        time_elasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            my_time_stamps["flashTime"].append(time_elasped) 
            print(time_elasped)
        if not mixer.voice[0].playing:
            ledStripMiddle.fill((0, 0, 0))
            ledStripMiddle.show()
            my_time_stamps["flashTime"].append(5000)
            if customers_file:
                files.write_json_file("/sd/customers_owned_music/" + file_name + ".json",my_time_stamps)
            else:   
                files.write_json_file("/sd/christmas_park_sounds/" + file_name + ".json",my_time_stamps)
            break

    time_stamp_mode = False
    play_audio_0("/sd/mvc/timestamp_saved.wav")
    play_audio_0("/sd/mvc/timestamp_mode_off.wav")
    play_audio_0("/sd/mvc/animations_are_now_active.wav")

##############################
# Led color effects
        
def change_color():
    ledStripMiddle.brightness = 1.0
    color_r = random.randint(0, 255)
    color_g = random.randint(0, 255)
    color_b = random.randint(0, 255)     
    ledStripMiddle.fill((color_r, color_g, color_b))
    ledStripMiddle.show()

def rainbow(speed,duration):
    startTime = time.monotonic()
    for j in range(0,255,1):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStripLeft[i] = colorwheel(pixel_index & 255)
            ledStripMiddle[i] = colorwheel(pixel_index & 255)
            ledStripRight[i] = colorwheel(pixel_index & 255)
        ledStripLeft.show()
        ledStripMiddle.show()
        ledStripRight.show()
        sleepAndUpdateVolume(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStripLeft[i] = colorwheel(pixel_index & 255)
            ledStripMiddle[i] = colorwheel(pixel_index & 255)
            ledStripRight[i] = colorwheel(pixel_index & 255)
        ledStripLeft.show()
        ledStripMiddle.show()
        ledStripRight.show()
        sleepAndUpdateVolume(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return

def fire(duration):
    startTime = time.monotonic()
    ledStripMiddle.brightness = 1.0

    fire_indexes = []
    
    fire_indexes.extend(tree_ornaments)
    fire_indexes.extend(cane_starts)
    fire_indexes.extend(cane_ends)
    
    star_indexes = []
    star_indexes.extend(tree_stars)
    
    for i in star_indexes:
        ledStripMiddle[i] = (255,255,255)
        
    branches_indexes = []
    branches_indexes.extend((tree_branches))
    
    for i in branches_indexes:
        ledStripMiddle[i] = (50,50,50)
    
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
            ledStripMiddle[i] = (r1,g1,b1)
            ledStripMiddle.show()
        sleepAndUpdateVolume(random.uniform(0.05,0.1))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
               
def christmas_fire(duration):
    startTime=time.monotonic()
    ledStripMiddle.brightness = 1.0

    #Flicker, based on our initial RGB values
    while True:
        for i in range (0, num_pixels):
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
            ledStripMiddle[i] = (r1,g1,b1)
            ledStripMiddle.show()
        sleepAndUpdateVolume(random.uniform(.2,0.3))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
         
def bounds(my_color, lower, upper):
    if (my_color < lower): my_color = lower
    if (my_color > upper): my_color = upper
    return my_color

def multicolor(duration):
    startTime=time.monotonic()
    ledStripMiddle.brightness = 1.0

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
            ledStripMiddle[i] = (r1,g1,b1)
            ledStripMiddle.show()
        sleepAndUpdateVolume(random.uniform(.2,0.3))
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
        files.log_item('Main menu')
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                try:
                    wave0 = audiocore.WaveFile(open("/sd/christmas_park_options_voice_commands/option_" + menu_sound_options[self.optionIndex] + ".wav" , "rb"))
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
                files.write_json_file("/sd/config_christmas_park.json",config)
                wave0 = audiocore.WaveFile(open("/sd/mvc/option_selected.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
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
        global time_stamp_mode
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + add_sounds_animate[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(add_sounds_animate)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = add_sounds_animate[self.selectedMenuIndex]
            if selected_menu_item == "hear_instructions":
                play_audio_0("/sd/mvc/create_sound_track_files.wav")
            elif selected_menu_item == "timestamp_mode_on":
                time_stamp_mode = True
                play_audio_0("/sd/mvc/timestamp_mode_on.wav")
                play_audio_0("/sd/mvc/timestamp_instructions.wav")
                machine.go_to_state('base_state') 
            elif selected_menu_item == "timestamp_mode_off":
                time_stamp_mode = False
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
                            files.write_json_file("/sd/config_christmas_park.json",config)
                            play_audio_0("/sd/mvc/all_changes_complete.wav")
                            done = True
                            machine.go_to_state('base_state')
                        sleepAndUpdateVolume(0.1)
                        pass
                elif selected_menu_item == "volume_pot_off":
                    config["volume_pot"] = False
                    if config["volume"] == 0:
                        config["volume"] = 10
                    files.write_json_file("/sd/config_christmas_park.json",config)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state') 
                elif selected_menu_item == "volume_pot_on":
                    config["volume_pot"] = True
                    files.write_json_file("/sd/config_christmas_park.json",config)
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
                files.write_json_file("/sd/config_christmas_park.json",config)
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
                play_audio_0("/sd/mvc/park_string_instructions.wav")
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
                        self.lightIndex -=1
                        if self.lightIndex < 0:
                            self.lightIndex = len(light_options)-1
                        self.selectedLightIndex = self.lightIndex   
                        play_audio_0("/sd/mvc/" + light_options[self.lightIndex] + ".wav") 
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
                        files.write_json_file("/sd/config_christmas_park.json",config)   
                        updateLightString()
                        play_audio_0("/sd/mvc/all_changes_complete.wav")
                        adding = False
                        machine.go_to_state('base_state')  
                    sleepAndUpdateVolume(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_christmas_park.json",config)
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

audio_enable.value = True

sleepAndUpdateVolume(.5)

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
   
