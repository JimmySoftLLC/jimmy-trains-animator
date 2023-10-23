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

audio_enable = digitalio.DigitalInOut(board.GP28)
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
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True, buffer_size=4096)
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
                wave0 = audiocore.WaveFile(open("/sd/menu_voice_commands/micro_sd_card_success.wav", "rb"))
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
# Global Variables

config = files.read_json_file("/sd/config_christmas_park.json")
sound_options = config["options"]

my_sound_options = files.return_directory("customers_owned_music_", "/sd/customers_owned_music", ".wav")

rand_sound_options = []

rand_sound_options.extend(sound_options)
rand_sound_options.extend(my_sound_options)
rand_sound_options.remove("random")

time_stamp_jsons = files.return_directory("", "/sd/time_stamp_defaults", ".json")

serve_webpage = config["serve_webpage"]

config_main_menu = files.read_json_file("/sd/menu_voice_commands/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_web_menu = files.read_json_file("/sd/menu_voice_commands/web_menu.json")
web_menu = config_web_menu["web_menu"]

config_light_string_menu = files.read_json_file("/sd/menu_voice_commands/light_string_menu.json")
light_string_menu = config_light_string_menu["light_string_menu"]

config_light_options = files.read_json_file("/sd/menu_voice_commands/light_options.json")
light_options = config_light_options["light_options"]

volume_settings_options = files.read_json_file("/sd/menu_voice_commands/volume_settings.json")
volume_settings = volume_settings_options["volume_settings"]

garbage_collect("config setup")

continuous_run = False
time_stamp_mode = False

################################################################################
# Setup neo pixels
import neopixel
from rainbowio import colorwheel

grand_trees = []
canes = []
tree_ornaments = []
tree_stars = []
tree_branches  = []
cane_starts  = []
cane_ends  = []

num_pixels = 0

ledStrip = neopixel.NeoPixel(board.GP10, num_pixels)

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
    ledStrip.show()
    time.sleep(.3)
    ledStrip.fill((0, 0, 0))
    ledStrip.show()

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
        ledStrip[led_index]=(50, 50, 50)
        count+=1
        if count > 1:
            show_Lights()
            count = 0
    for led_index in cane_ends:
        ledStrip[led_index]=(50, 50, 50)
        count+=1
        if count > 1:
            show_Lights()
            count = 0

    #tree test
    count = 0
    for led_index in tree_ornaments:
        ledStrip[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0
    for led_index in tree_stars:
        ledStrip[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0
    for led_index in tree_branches:
        ledStrip[led_index]=(50, 50, 50)
        count+=1
        if count > 6:
            show_Lights()
            count = 0

def updateLightString():
    global grand_trees, canes, num_pixels, ledStrip, num_pixels
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
    ledStrip.deinit()
    garbage_collect("Deinit ledStrip")
    ledStrip = neopixel.NeoPixel(board.GP10, num_pixels)
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
            global config
            global continuous_run
            global time_stamp_mode
            raw_text = request.raw_request.decode("utf8")
            if "random" in raw_text: 
                config["option_selected"] = "random"
                animation(config["option_selected"])
            elif "we_wish_you_a_merry_christmas" in raw_text: 
                config["option_selected"] = "we_wish_you_a_merry_christmas"
                animation(config["option_selected"])
            elif "angels_we_have_heard_on_high" in raw_text: 
                config["option_selected"] = "angels_we_have_heard_on_high"
                animation(config["option_selected"])
            elif "joyful_snowman" in raw_text: 
                config["option_selected"] = "joyful_snowman"
                animation(config["option_selected"])
            elif "carol_of_the_bells" in raw_text: 
                config["option_selected"] = "carol_of_the_bells"
                animation(config["option_selected"])
            elif "dance_of_the_sugar_plum_fairy" in raw_text: 
                config["option_selected"] = "dance_of_the_sugar_plum_fairy"
                animation(config["option_selected"])
            elif "deck_the_halls_jazzy_version" in raw_text: 
                config["option_selected"] = "deck_the_halls_jazzy_version"
                animation(config["option_selected"])
            elif "the_wassail_song" in raw_text: 
                config["option_selected"] = "the_wassail_song"
                animation(config["option_selected"])     
            elif "jingle_bells_orchestra" in raw_text: 
                config["option_selected"] = "jingle_bells_orchestra"
                animation(config["option_selected"])
            elif "away_in_a_manger" in raw_text: 
                config["option_selected"] = "away_in_a_manger"
                animation(config["option_selected"])
            elif "joy_to_the_world" in raw_text: 
                config["option_selected"] = "joy_to_the_world"
                animation(config["option_selected"])
            elif "silent_night" in raw_text: 
                config["option_selected"] = "silent_night"
                animation(config["option_selected"])
            elif "auld_lang_syne_jazzy_version" in raw_text: 
                config["option_selected"] = "auld_lang_syne_jazzy_version"
                animation(config["option_selected"])
            elif "customers_owned_music_" in raw_text:
                for my_sound_file in my_sound_options:
                    if my_sound_file  in raw_text:
                        config["option_selected"] = my_sound_file
                        animation(config["option_selected"])
                        break
            elif "cont_mode_on" in raw_text: 
                continuous_run = True
                play_audio_0("/sd/menu_voice_commands/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                continuous_run = False
                play_audio_0("/sd/menu_voice_commands/continuous_mode_deactivated.wav")
            elif "timestamp_mode_on" in raw_text: 
                time_stamp_mode = True
                play_audio_0("/sd/menu_voice_commands/timestamp_mode_on.wav")
                play_audio_0("/sd/menu_voice_commands/timestamp_instructions.wav")
            elif "timestamp_mode_off" in raw_text: 
                time_stamp_mode = False
                play_audio_0("/sd/menu_voice_commands/timestamp_mode_off.wav") 
            elif "reset_animation_timing_to_defaults" in raw_text:
                for time_stamp_file in time_stamp_jsons:
                    time_stamps = files.read_json_file("/sd/time_stamp_defaults/" + time_stamp_file + ".json")
                    files.write_json_file("/sd/christmas_park_sounds/"+time_stamp_file+".json",time_stamps)
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        @server.route("/utilities", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                command_sent = "speaker_test"
                play_audio_0("/sd/menu_voice_commands/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                command_sent = "volume_pot_off"
                config["volume_pot"] = False
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                command_sent = "volume_pot_on"
                config["volume_pot"] = True
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                command_sent = "reset_to_defaults"
                reset_to_defaults()      
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                pretty_state_machine.go_to_state('base_state')
            return Response(request, "Utility: " + command_sent)
        
        @server.route("/lights", [POST])
        def buttonpress(request: Request):
            global config
            command_sent = ""
            raw_text = request.raw_request.decode("utf8")
            if "set_to_red" in raw_text:
                command_sent = "set_to_red"
                ledStrip.fill((255, 0, 0))
                ledStrip.show()
            elif "set_to_green" in raw_text:
                command_sent = "set_to_green"
                ledStrip.fill((0, 255, 0))
                ledStrip.show()
            elif "set_to_blue" in raw_text:
                command_sent = "set_to_blue"
                ledStrip.fill((0, 0, 255))
                ledStrip.show()
            elif "set_to_white" in raw_text:
                command_sent = "set_to_white"
                ledStrip.fill((255, 255, 255))
                ledStrip.show()
            elif "set_to_0" in raw_text:
                command_sent = "set_to_0"
                ledStrip.brightness = 0.0
                ledStrip.show()
            elif "set_to_20" in raw_text:
                command_sent = "set_to_20"
                ledStrip.brightness = 0.2
                ledStrip.show()
            elif "set_to_40" in raw_text:
                command_sent = "set_to_40"
                ledStrip.brightness = 0.4
                ledStrip.show()
            elif "set_to_60" in raw_text:
                command_sent = "set_to_60"
                ledStrip.brightness = 0.6
                ledStrip.show()
            elif "set_to_80" in raw_text:
                command_sent = "set_to_80"
                ledStrip.brightness = 0.8
                ledStrip.show()
            elif "set_to_100" in raw_text:
                command_sent = "set_to_100"
                ledStrip.brightness = 1.0
                ledStrip.show()
            return Response(request, "Utility: " + command_sent)

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
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                return Response(request, config["light_string"])
            if config["light_string"] =="":
                config["light_string"] = data_object["text"]
            else:
                config["light_string"] = config["light_string"] + "," + data_object["text"]
            print("action: " + data_object["action"]+ " data: " + config["light_string"])
            files.write_json_file("/sd/config_christmas_park.json",config)
            updateLightString()
            play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
            return Response(request, config["light_string"])
        
        @server.route("/get-light-string", [POST])
        def buttonpress(request: Request):
            return Response(request, config["light_string"])
        
        @server.route("/get-customers-sound-tracks", [POST])
        def buttonpress(request: Request):
            my_string = files.json_stringify(my_sound_options)
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

def reset_to_defaults():
    global config
    config["volume_pot"] = True
    config["HOST_NAME"] = "animator-christmas-park"
    config["option_selected"] = "we_wish_you_a_merry_christmas"
    config["volume"] = 30
    
    reset_lights_to_defaults()
    
def reset_lights_to_defaults():
    global config
    config["light_string"] = "cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21"

def changeVolume(action):
    volume = int(config["volume"])
    if action == "lower1":
        volume -= 1
    if action == "lower10":
        volume -= 10
    if action == "raise10":
        volume += 10
    if action == "raise1":
        volume += 1
    if volume > 100:
        volume =100
    if volume < 1:
        volume = 1
    config["volume"] = str(volume)
    config["volume_pot"] = False
    files.write_json_file("/sd/config_christmas_park.json",config)
    play_audio_0("/sd/menu_voice_commands/volume.wav")
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
            play_audio_0("/sd/menu_voice_commands/" + character + ".wav")
        except:
            print("invalid character in string to speak")
    if addLocal:
        play_audio_0("/sd/menu_voice_commands/dot.wav")
        play_audio_0("/sd/menu_voice_commands/local.wav")

def selectSoundMenuAnnouncement():
    play_audio_0("/sd/menu_voice_commands/sound_selection_menu.wav")
    left_right_mouse_button()

def selectMySoundMenuAnnouncement():
    play_audio_0("/sd/menu_voice_commands/choose_my_sounds_menu.wav")
    left_right_mouse_button()
    
def left_right_mouse_button():
    play_audio_0("/sd/menu_voice_commands/press_left_button_right_button.wav")
    
def mainMenuAnnouncement():
    play_audio_0("/sd/menu_voice_commands/main_menu.wav")
    left_right_mouse_button()

def selectWebOptionsAnnouncement():
    play_audio_0("/sd/menu_voice_commands/web_menu.wav")
    left_right_mouse_button()

def volumeSettingsAnnouncement():
    play_audio_0("/sd/menu_voice_commands/volume_settings_menu.wav")
    left_right_mouse_button()

def lightStringSetupAnnouncement():
    play_audio_0("/sd/menu_voice_commands/light_string_setup_menu.wav")
    left_right_mouse_button()
    
def stringInstructions():
    play_audio_0("/sd/menu_voice_commands/string_instructions.wav")    
    
def option_selected_announcement():
    play_audio_0("/sd/menu_voice_commands/option_selected.wav")
    
def speak_light_string(play_intro):
    if play_intro :
        play_audio_0("/sd/menu_voice_commands/current_light_settings_are.wav")
    elements = config["light_string"].split(',')
    for index, element in enumerate(elements):
        play_audio_0("/sd/menu_voice_commands/position.wav")
        play_audio_0("/sd/menu_voice_commands/" + str(index+1) + ".wav")
        play_audio_0("/sd/menu_voice_commands/is.wav")
        play_audio_0("/sd/menu_voice_commands/" + element + ".wav")
        
def no_user_soundtrack_found():
    play_audio_0("/sd/menu_voice_commands/no_user_sountrack_found.wav")
    while True:
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            break
        if right_switch.fell:
            play_audio_0("/sd/menu_voice_commands/create_sound_track_files.wav")
            break

################################################################################
# animations
     
def animation(file_name):
    print(file_name)
    current_option_selected = file_name
    if file_name == "random":
        if file_name == "random":
            highest_index = len(rand_sound_options) - 1
            sound_number = random.randint(0, highest_index)
            current_option_selected = rand_sound_options[sound_number]
            print("Random sound file: " + rand_sound_options[sound_number])
            print("Sound file: " + current_option_selected)
    if time_stamp_mode:
        animation_timestamp(current_option_selected)
    else:
        animation_light_show(current_option_selected)
    garbage_collect("animation finished")
         
def animation_light_show(file_name):
    global time_stamp_mode
    rand_index_low = 1
    rand_index_high = 3
    if file_name == "silent_night":
        rand_index_low = 3
        rand_index_high = 3

    customers_file = "customers_owned_music_" in file_name
    
    if customers_file:
        file_name=file_name.replace("customers_owned_music_","")
        try:
            flash_time_dictionary = files.read_json_file("/sd/customers_owned_music/" + file_name + ".json")
        except:
            play_audio_0("/sd/menu_voice_commands/no_timestamp_file_found.wav")
            while True:
                left_switch.update()
                right_switch.update()
                if left_switch.fell:
                    time_stamp_mode = False
                    return
                if right_switch.fell:
                    time_stamp_mode = True
                    play_audio_0("/sd/menu_voice_commands/timestamp_instructions.wav")
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
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            #ledStrip.fill((0, 0, 0))
            #ledStrip.show()
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
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            my_time_stamps["flashTime"].append(5000)
            if customers_file:
                files.write_json_file("/sd/customers_owned_music/" + file_name + ".json",my_time_stamps)
            else:   
                files.write_json_file("/sd/christmas_park_sounds/" + file_name + ".json",my_time_stamps)
            break

    time_stamp_mode = False
    play_audio_0("/sd/menu_voice_commands/timestamp_saved.wav")
    play_audio_0("/sd/menu_voice_commands/timestamp_mode_off.wav")
    play_audio_0("/sd/menu_voice_commands/animations_are_now_active.wav")

##############################
# Led color effects
        
def change_color():
    ledStrip.brightness = 1.0
    color_r = random.randint(0, 255)
    color_g = random.randint(0, 255)
    color_b = random.randint(0, 255)     
    ledStrip.fill((color_r, color_g, color_b))
    ledStrip.show()

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

def fire(duration):
    startTime = time.monotonic()
    ledStrip.brightness = 1.0

    fire_indexes = []
    
    fire_indexes.extend(tree_ornaments)
    fire_indexes.extend(cane_starts)
    fire_indexes.extend(cane_ends)
    
    star_indexes = []
    star_indexes.extend(tree_stars)
    
    for i in star_indexes:
        ledStrip[i] = (255,255,255)
        
    branches_indexes = []
    branches_indexes.extend((tree_branches))
    
    for i in branches_indexes:
        ledStrip[i] = (50,50,50)
    
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
            ledStrip[i] = (r1,g1,b1)
            ledStrip.show()
        sleepAndUpdateVolume(random.uniform(0.05,0.1))
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
               
def christmas_fire(duration):
    startTime=time.monotonic()
    ledStrip.brightness = 1.0

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
            ledStrip[i] = (r1,g1,b1)
            ledStrip.show()
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
        """As indicated, reset"""
        self.firework_color = random_color()
        self.burst_count = 0
        self.shower_count = 0
        self.firework_step_time = time.monotonic() + 0.05

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
        if left_switch.fell:
            machine.paused_state = machine.state.name
            machine.pause()
            return False
        return True

class BaseState(State):

    def __init__(self):      
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, machine):
        play_audio_0("/sd/menu_voice_commands/animations_are_now_active.wav")
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
                play_audio_0("/sd/menu_voice_commands/continuous_mode_deactivated.wav")
            else:
                continuous_run = True
                play_audio_0("/sd/menu_voice_commands/continuous_mode_activated.wav")
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
        mainMenuAnnouncement()
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
                play_audio_0("/sd/menu_voice_commands/" + main_menu[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(main_menu)-1:
                    self.menuIndex = 0
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                selected_menu_item = main_menu[self.selectedMenuIndex]
                if selected_menu_item == "choose_sounds":
                    machine.go_to_state('choose_sounds')
                elif selected_menu_item == "choose_my_sounds":
                    machine.go_to_state('choose_my_sounds')
                elif selected_menu_item == "new_feature": #add this later
                    play_audio_0("/sd/menu_voice_commands/no_timestamp_file_found.wav")
                    while True:
                        left_switch.update()
                        right_switch.update()
                        if left_switch.fell:
                            time_stamp_mode = False
                            return
                        if right_switch.fell:
                            time_stamp_mode = True
                            play_audio_0("/sd/menu_voice_commands/timestamp_instructions.wav")
                            return
                elif selected_menu_item == "light_string_setup_menu":
                    machine.go_to_state('light_string_setup_menu')
                elif selected_menu_item == "web_options":
                    machine.go_to_state('web_options') 
                elif selected_menu_item == "volume_settings":
                    machine.go_to_state('volume_settings')                 
                else:
                    play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                    machine.go_to_state('base_state')

class ChooseSounds(State):

    def __init__(self):
        self.optionIndex = 0
        self.currentOption = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            files.log_item('Choose sounds menu')
            selectSoundMenuAnnouncement()
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
                wave0 = audiocore.WaveFile(open("/sd/christmas_park_options_voice_commands/option_" + sound_options[self.optionIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.currentOption = self.optionIndex
                self.optionIndex +=1
                if self.optionIndex > len(sound_options)-1:
                    self.optionIndex = 0
                while mixer.voice[0].playing:
                    pass
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                config["option_selected"] = sound_options[self.currentOption]
                files.write_json_file("/sd/config_christmas_park.json",config)
                wave0 = audiocore.WaveFile(open("/sd/menu_voice_commands/option_selected.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            machine.go_to_state('base_state')

class ChooseMySounds(State):

    def __init__(self):
        self.optionIndex = 0
        self.currentOption = 0

    @property
    def name(self):
        return 'choose_my_sounds'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            files.log_item('Choose sounds menu')
            selectMySoundMenuAnnouncement()
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
                    my_string = my_sound_options[self.optionIndex].replace("customers_owned_music_","")
                    speak_this_string(my_string,False)
                    self.currentOption = self.optionIndex
                    self.optionIndex +=1
                    if self.optionIndex > len(my_sound_options)-1:
                        self.optionIndex = 0
                    while mixer.voice[0].playing:
                        pass
                except:
                    no_user_soundtrack_found()
                    machine.go_to_state('base_state')
                    return
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                try:
                    config["option_selected"] = my_sound_options[self.currentOption]
                    files.write_json_file("/sd/config_christmas_park.json",config)
                    wave0 = audiocore.WaveFile(open("/sd/menu_voice_commands/option_selected.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
                except:
                    print("no sound track")
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
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                play_audio_0("/sd/menu_voice_commands/" + web_menu[self.menuIndex] + ".wav")
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
                    play_audio_0("/sd/menu_voice_commands/web_instruct.wav")
                    selectWebOptionsAnnouncement()
                else:
                    files.write_json_file("/sd/config_christmas_park.json",config)
                    play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                    machine.go_to_state('base_state')   

class LightStringSetupMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'light_string_setup_menu'

    def enter(self, machine):
        files.log_item('Set Web Options')
        lightStringSetupAnnouncement()
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
                play_audio_0("/sd/menu_voice_commands/" + light_string_menu[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(light_string_menu)-1:
                    self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = light_string_menu[self.selectedMenuIndex]
            if selected_menu_item == "hear_light_setup_instructions":
                stringInstructions()
            elif selected_menu_item == "reset_lights_defaults":
                reset_lights_to_defaults()
                play_audio_0("/sd/menu_voice_commands/lights_reset_to.wav")
                speak_light_string(False)
            elif selected_menu_item == "hear_current_light_settings": 
                speak_light_string(True)
            elif selected_menu_item == "clear_light_string":
                config["light_string"] = ""
                play_audio_0("/sd/menu_voice_commands/lights_cleared.wav") 
            elif selected_menu_item == "add_lights":
                play_audio_0("/sd/menu_voice_commands/add_light_menu.wav")
                while True:
                    switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 3.0)
                    if switch_state == "left":
                        if mixer.voice[0].playing:
                            mixer.voice[0].stop()
                            while mixer.voice[0].playing:
                                pass
                        else:
                            self.menuIndex -=1
                            if self.menuIndex < 0:
                                self.menuIndex = len(light_options)-1
                            self.selectedMenuIndex = self.menuIndex
                            play_audio_0("/sd/menu_voice_commands/" + light_options[self.menuIndex] + ".wav") 
                    elif switch_state == "right":
                        if mixer.voice[0].playing:
                            mixer.voice[0].stop()
                            while mixer.voice[0].playing:
                                pass
                        else:
                            self.menuIndex +=1
                            if self.menuIndex > len(light_options)-1:
                                self.menuIndex = 0
                            self.selectedMenuIndex = self.menuIndex
                            play_audio_0("/sd/menu_voice_commands/" + light_options[self.menuIndex] + ".wav") 
                    elif switch_state == "right_held":
                        if mixer.voice[0].playing:
                            mixer.voice[0].stop()
                            while mixer.voice[0].playing:
                                pass
                        else:
                            if config["light_string"] == "":
                                config["light_string"] = light_options[self.selectedMenuIndex]
                            else:
                                config["light_string"] = config["light_string"] + "," + light_options[self.selectedMenuIndex]
                            play_audio_0("/sd/menu_voice_commands/" + light_options[self.selectedMenuIndex] + ".wav")
                            play_audio_0("/sd/menu_voice_commands/added.wav")
                    elif switch_state == "left_held":
                        if mixer.voice[0].playing:
                            mixer.voice[0].stop()
                            while mixer.voice[0].playing:
                                pass
                        else:
                            files.write_json_file("/sd/config_christmas_park.json",config)
                            play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                            updateLightString()
                            machine.go_to_state('base_state')  
                    sleepAndUpdateVolume(0.1)
                    pass
            else:
                files.write_json_file("/sd/config_christmas_park.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                updateLightString()
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
        volumeSettingsAnnouncement()

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
                play_audio_0("/sd/menu_voice_commands/" + volume_settings[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(volume_settings)-1:
                    self.menuIndex = 0
        if right_switch.fell:
                selected_menu_item = volume_settings[self.selectedMenuIndex]
                if selected_menu_item == "volume_level_adjustment":
                    play_audio_0("/sd/menu_voice_commands/volume_adjustment_menu.wav")
                    while True: 
                        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 3.0)
                        if switch_state == "left":
                            changeVolume("lower")
                        elif switch_state == "right":
                            changeVolume("raise")
                        elif switch_state == "right_held":
                            files.write_json_file("/sd/config_christmas_park.json",config)
                            play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                            machine.go_to_state('base_state')
                            break 
                        sleepAndUpdateVolume(0.1)
                        pass
                elif selected_menu_item == "volume_pot_off":
                    config["volume_pot"] = False
                    if config["volume"] == 0:
                        config["volume"] = 10
                    files.write_json_file("/sd/config_christmas_park.json",config)
                    play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                    machine.go_to_state('base_state') 
                elif selected_menu_item == "volume_pot_on":
                    config["volume_pot"] = True
                    files.write_json_file("/sd/config_christmas_park.json",config)
                    play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                    machine.go_to_state('base_state') 

# StateTemplate copy and add functionality
class StateTemplate(State):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'example'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        State.update(self, machine)

###############################################################################
# Create the state machine

pretty_state_machine = StateMachine()
pretty_state_machine.add_state(BaseState())
pretty_state_machine.add_state(ChooseSounds())
pretty_state_machine.add_state(ChooseMySounds())
pretty_state_machine.add_state(MainMenu())
pretty_state_machine.add_state(WebOptions())
pretty_state_machine.add_state(LightStringSetupMenu())
pretty_state_machine.add_state(VolumeSettings())
       
audio_enable.value = True

sleepAndUpdateVolume(.5)

def speak_webpage():
    play_audio_0("/sd/menu_voice_commands/animator_available_on_network.wav")
    play_audio_0("/sd/menu_voice_commands/to_access_type.wav")
    if config["HOST_NAME"]== "animator-christmas-park":
        play_audio_0("/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav")
        play_audio_0("/sd/menu_voice_commands/dot.wav")
        play_audio_0("/sd/menu_voice_commands/local.wav")
    else:
        speak_this_string(config["HOST_NAME"], True)
    play_audio_0("/sd/menu_voice_commands/in_your_browser.wav")    

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

pretty_state_machine.go_to_state('base_state')   
files.log_item("animator has started...")
garbage_collect("animations started.")

while True:
    pretty_state_machine.update()
    sleepAndUpdateVolume(.02)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
