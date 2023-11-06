import gc
import files

def garbage_collect(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item( "Point " + collection_point + " Available memory: {} bytes".format(start_mem) )
    
garbage_collect("Imports gc, files")

import sdcardio
import storage

import audiocore
import audiomixer
import audiobusio
import time

import board
import microcontroller
import busio
import pwmio
import digitalio

import random

from analogio import AnalogIn
from adafruit_motor import servo
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

# Setup the servo, this animation has two the feller and tree
# also get the programmed values for position which is stored on the sdCard
feller_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
tree_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

feller_servo = servo.Servo(feller_pwm)
tree_servo = servo.Servo(tree_pwm)

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
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,bits_per_sample=16, samples_signed=True, buffer_size=4096)
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

################################################################################
# Global Variables

def returnMinChops(min_chops, max_chops):
    if min_chops < 1 :
        min_chops = 1
    if min_chops > 20 :
        min_chops = 20
    if min_chops > max_chops :
        min_chops = max_chops
    return str(min_chops)

def returnMaxChops(min_chops, max_chops):
    if max_chops < 1 :
        max_chops = 1
    if max_chops > 20 :
        max_chops = 20
    if max_chops < min_chops :
        max_chops = min_chops
    return str(max_chops)

# get the calibration settings from various json files which are stored on the sdCard
config = files.read_json_file("/sd/config_feller.json")

tree_last_pos = config["tree_up_pos"]
tree_min = 60
tree_max = 180
if config["tree_down_pos"] < tree_min or config["tree_down_pos"] > tree_max: config["tree_down_pos"] = tree_min
if config["tree_up_pos"] < tree_min or config["tree_up_pos"] > tree_max: config["tree_up_pos"] = tree_max

feller_last_pos = config["feller_rest_pos"]
feller_min = 0
feller_max = 170
if config["feller_rest_pos"] < feller_min or config["feller_rest_pos"] > feller_max: config["feller_rest_pos"] = feller_min
if config["feller_chop_pos"] > feller_max or config["feller_chop_pos"] < feller_min: config["feller_chop_pos"] = feller_max

config_main_menu = files.read_json_file("/sd/mvc/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_choose_sounds = files.read_json_file("/sd/mvc/choose_sounds.json")
feller_sound_options = config_choose_sounds["choose_sounds"]

config_feller_dialog = files.read_json_file("/sd/feller_dialog/feller_dialog.json")
feller_dialog = config_feller_dialog["feller_dialog"]

config_feller_wife = files.read_json_file("/sd/feller_wife/feller_wife.json")
feller_wife = config_feller_wife["feller_wife"]

config_feller_poem = files.read_json_file("/sd/feller_poem/feller_poem.json")
feller_poem = config_feller_poem["feller_poem"]

config_feller_buddy = files.read_json_file("/sd/feller_buddy/feller_buddy.json")
feller_buddy = config_feller_buddy["feller_buddy"]

config_feller_girlfriend = files.read_json_file("/sd/feller_girlfriend/feller_girlfriend.json")
feller_girlfriend = config_feller_girlfriend["feller_girlfriend"]

config_adjust_feller_and_tree = files.read_json_file("/sd/mvc/adjust_feller_and_tree.json")
adjust_feller_and_tree = config_adjust_feller_and_tree["adjust_feller_and_tree"]

config_move_feller_and_tree = files.read_json_file("/sd/mvc/move_feller_and_tree.json")
move_feller_and_tree = config_move_feller_and_tree["move_feller_and_tree"]

config_dialog_selection_menu = files.read_json_file("/sd/mvc/dialog_selection_menu.json")
dialog_selection_menu = config_dialog_selection_menu["dialog_selection_menu"]

config_web_menu = files.read_json_file("/sd/mvc/web_menu.json")
web_menu = config_web_menu["web_menu"]

serve_webpage = config["serve_webpage"]

feller_movement_type = "feller_rest_pos"
tree_movement_type = "tree_up_pos"

continuous_run = False

garbage_collect("config setup")

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
            raw_text = request.raw_request.decode("utf8")
            if "random" in raw_text: 
                config["option_selected"] = "random"
                animate_feller()
            elif "forth_of_july" in raw_text: 
                config["option_selected"] = "forth_of_july"
                animate_feller()
            elif "christmas" in raw_text: 
                config["option_selected"] = "christmas"
                animate_feller()
            elif "halloween" in raw_text: 
                config["option_selected"] = "halloween"
                animate_feller()
            elif "train" in raw_text: 
                config["option_selected"] = "train"
                animate_feller()
            elif "alien" in raw_text: 
                config["option_selected"] = "alien"
                animate_feller()  
            elif "birds_dogs_short_version" in raw_text: 
                config["option_selected"] = "birds_dogs_short_version"
                animate_feller()
            elif "birds_dogs" in raw_text: 
                config["option_selected"] = "birds_dogs"
                animate_feller()
            elif "just_birds" in raw_text: 
                config["option_selected"] = "just_birds"
                animate_feller()
            elif "machines" in raw_text: 
                config["option_selected"] = "machines"
                animate_feller()
            elif "no_sounds" in raw_text: 
                config["option_selected"] = "no_sounds"
                animate_feller()
            elif "owl" in raw_text: 
                config["option_selected"] = "owl"
                animate_feller()
            elif "happy_birthday" in raw_text: 
                config["option_selected"] = "happy_birthday"
                animate_feller()
            elif "cont_mode_on" in raw_text: 
                continuous_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                continuous_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        @server.route("/feller", [POST])        
        def buttonpress(request: Request):
            global config
            global feller_movement_type
            raw_text = request.raw_request.decode("utf8")    
            if "feller_rest_pos" in raw_text:
                feller_movement_type = "feller_rest_pos"
                moveFellerToPositionGently(config[feller_movement_type], 0.01)
                return Response(request, "Moved feller to rest position.")
            elif "feller_chop_pos" in raw_text:
                feller_movement_type = "feller_chop_pos"
                moveFellerToPositionGently(config[feller_movement_type], 0.01)
                return Response(request, "Moved feller to chop position.")
            elif "feller_adjust" in raw_text:
                feller_movement_type = "feller_rest_pos"
                moveFellerToPositionGently(config[feller_movement_type],0.01)
                return Response(request, "Redirected to feller-adjust page.")
            elif "feller_home" in raw_text:
                return Response(request, "Redirected to home page.")
            elif "feller_clockwise" in raw_text:
                calibrationLeftButtonPressed(feller_servo, feller_movement_type, 1, feller_min, feller_max)
                return Response(request, "Moved feller clockwise.")
            elif "feller_counter_clockwise" in raw_text:
                calibrationRightButtonPressed(feller_servo, feller_movement_type, 1, feller_min, feller_max)
                return Response(request, "Moved feller counter clockwise.")
            elif "feller_cal_saved" in raw_text:
                write_calibrations_to_config_file()
                state_machine.go_to_state('base_state')
                return Response(request, "Feller " + feller_movement_type + " cal saved.")
                
        @server.route("/tree", [POST])        
        def buttonpress(request: Request):
            global config
            global tree_movement_type
            raw_text = request.raw_request.decode("utf8")    
            if "tree_up_pos" in raw_text:
                tree_movement_type = "tree_up_pos"
                moveTreeToPositionGently(config[tree_movement_type], 0.01)
                return Response(request, "Moved tree to up position.")
            elif "tree_down_pos" in raw_text:
                tree_movement_type = "tree_down_pos"
                moveTreeToPositionGently(config[tree_movement_type], 0.01)
                return Response(request, "Moved tree to fallen position.")
            elif "tree_adjust" in raw_text:
                tree_movement_type = "tree_up_pos"
                moveTreeToPositionGently(config[tree_movement_type], 0.01)
                return Response(request, "Redirected to tree-adjust page.")
            elif "tree_home" in raw_text:
                return Response(request, "Redirected to home page.")
            elif "tree_up" in raw_text:
                calibrationLeftButtonPressed(tree_servo, tree_movement_type, -1, tree_min, tree_max)
                return Response(request, "Moved tree up.")
            elif "tree_down" in raw_text:
                calibrationRightButtonPressed(tree_servo, tree_movement_type, -1, tree_min, tree_max)
                return Response(request, "Moved tree down.")
            elif "tree_cal_saved" in raw_text:
                write_calibrations_to_config_file()
                state_machine.go_to_state('base_state')
                return Response(request, "Tree " + tree_movement_type + " cal saved.")
            
        @server.route("/dialog", [POST])
        def buttonpress(request: Request):
            global config
            raw_text = request.raw_request.decode("utf8")
            if "opening_dialog_on" in raw_text: 
                config["opening_dialog"] = True

            elif "opening_dialog_off" in raw_text: 
                config["opening_dialog"] = False

            elif "feller_advice_on" in raw_text: 
                config["feller_advice"] = True
                
            elif "feller_advice_off" in raw_text: 
                config["feller_advice"] = False
                
            files.write_json_file("/sd/config_feller.json",config)
            play_audio_0("/sd/mvc/all_changes_complete.wav")

            return Response(request, "Dialog option cal saved.")
        
        @server.route("/utilities", [POST])
        def buttonpress(request: Request):
            global config
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text: 
                play_audio_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                config["volume_pot"] = False
                files.write_json_file("/sd/config_feller.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                config["volume_pot"] = True
                files.write_json_file("/sd/config_feller.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                reset_to_defaults()      
                files.write_json_file("/sd/config_feller.json",config)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')

            return Response(request, "Dialog option cal saved.")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            config["HOST_NAME"] = data_object["text"]  
            files.write_json_file("/sd/config_feller.json",config)       
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
        
        @server.route("/update-min-chops", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            config["min_chops"] = returnMinChops(int(data_object["text"]),int(config["max_chops"]))
            files.write_json_file("/sd/config_feller.json",config)
            speak_this_string(config["min_chops"], False)
            return Response(request, config["min_chops"])
        
        @server.route("/get-min-chops", [POST])
        def buttonpress(request: Request):
            print(config["min_chops"])
            return Response(request, config["min_chops"])

        @server.route("/update-max-chops", [POST])
        def buttonpress(request: Request):
            global config
            data_object = request.json()
            config["max_chops"] = returnMaxChops(int(config["min_chops"]),int(data_object["text"]))
            files.write_json_file("/sd/config_feller.json",config)
            speak_this_string(config["max_chops"], False)
            return Response(request, config["max_chops"])
        
        @server.route("/get-max-chops", [POST])
        def buttonpress(request: Request):
            print(config["max_chops"])
            return Response(request, config["max_chops"])
           
    except Exception as e:
        serve_webpage = False
        files.log_item(e)

    
garbage_collect("web server")

import utilities

garbage_collect("utilities")

################################################################################
# Global Methods

def reset_to_defaults():
    global config
    config["tree_up_pos"] = 165
    config["tree_down_pos"] = 100
    config["feller_rest_pos"] = 0
    config["feller_chop_pos"] = 150
    config["opening_dialog"] = False
    config["feller_advice"] = True
    config["HOST_NAME"] = "animator-feller"
    config["volume_pot"] = True
    config["min_chops"] = "2"
    config["max_chops"] = "7"
    config["volume"] = "20"
    config["can_cancel"] = True

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
    files.write_json_file("/sd/config_feller.json",config)
    play_audio_0("/sd/mvc/volume.wav")
    speak_this_string(config["volume"], False)

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

garbage_collect("global variable and methods")

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

def left_right_mouse_button():
    play_audio_0("/sd/mvc/press_left_button_right_button.wav")

def option_selected_announcement():
    play_audio_0("/sd/mvc/option_selected.wav")

def fellerCalAnnouncement():
    play_audio_0("/sd/mvc/now_we_can_adjust_the_feller_position.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")
    
def treeCalAnnouncement():
    play_audio_0("/sd/mvc/now_we_can_adjust_the_tree_position.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")

def selectDialogOptionsAnnouncement():
    play_audio_0("/sd/mvc/dialog_selection_menu.wav")
    left_right_mouse_button()
    
def selectWebOptionsAnnouncement():
    play_audio_0("/sd/mvc/web_menu.wav")
    left_right_mouse_button()
 
def checkLimits(min_servo_pos, max_servo_pos, servo_pos):
    if servo_pos < min_servo_pos:
        play_audio_0("/sd/mvc/limit_reached.wav")
        return False
    if servo_pos > max_servo_pos:
        play_audio_0("/sd/mvc/limit_reached.wav")
        return False
    return True

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
        
garbage_collect("dialog methods")

#############################################################################################
# Servo helpers

def calibrationLeftButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global config
    config[movement_type] -= 1 * sign
    if checkLimits(min_servo_pos, max_servo_pos, config[movement_type]):
        servo.angle = config[movement_type]
    else:
        config[movement_type] += 1 * sign

def calibrationRightButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global config
    config[movement_type] += 1 * sign
    if checkLimits(min_servo_pos, max_servo_pos, config[movement_type]):
        servo.angle = config[movement_type]
    else:
        config[movement_type] -= 1 * sign
        
def write_calibrations_to_config_file():
    play_audio_0("/sd/mvc/all_changes_complete.wav")
    global config
    files.write_json_file("/sd/config_feller.json",config)
    
def calibratePosition(servo, movement_type):  
    if movement_type == "feller_rest_pos" or movement_type == "feller_chop_pos" :
        min_servo_pos = feller_min
        max_servo_pos = feller_max
        sign = 1
    else:
        min_servo_pos = tree_min
        max_servo_pos = tree_max
        sign = -1
    calibrations_complete = False
    while not calibrations_complete:
        servo.angle = config[movement_type]
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            calibrationLeftButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos)
        if right_switch.fell:
            button_check = True
            number_cycles = 0  
            while button_check:
                sleepAndUpdateVolume(.1)
                right_switch.update()
                number_cycles += 1
                if number_cycles > 30:
                    write_calibrations_to_config_file()
                    button_check = False
                    calibrations_complete = True 
                if right_switch.rose:
                    button_check = False           
            if not calibrations_complete:
                calibrationRightButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos)
    if movement_type == "feller_rest_pos" or movement_type == "feller_chop_pos" :
        global feller_last_pos
        feller_last_pos = config[movement_type]
    else:
        global tree_last_pos
        tree_last_pos = config[movement_type]

def moveFellerToPositionGently (new_position, speed):
    global feller_last_pos
    sign = 1
    if feller_last_pos > new_position: sign = - 1
    for feller_angle in range( feller_last_pos, new_position, sign):
        moveFellerServo (feller_angle)
        sleepAndUpdateVolume(speed)
    moveFellerServo (new_position)
    
def moveTreeToPositionGently (new_position, speed):
    global tree_last_pos
    sign = 1
    if tree_last_pos > new_position: sign = - 1
    for tree_angle in range( tree_last_pos, new_position, sign): 
        moveTreeServo(tree_angle)
        sleepAndUpdateVolume(speed)
    moveTreeServo(new_position)

def moveFellerServo (servo_pos):
    if servo_pos < feller_min: servo_pos = feller_min
    if servo_pos > feller_max: servo_pos = feller_max
    feller_servo.angle = servo_pos
    global feller_last_pos
    feller_last_pos = servo_pos

def moveTreeServo (servo_pos):
    if servo_pos < tree_min: servo_pos = tree_min
    if servo_pos > tree_max: servo_pos = tree_max
    tree_servo.angle = servo_pos
    global tree_last_pos
    tree_last_pos = servo_pos

garbage_collect("servo helpers")

################################################################################
# animate feller

def feller_talking_movement():
    speak_rotation = 7
    speak_cadence = 0.2
    while mixer.voice[0].playing:
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
        if switch_state == "left_held":
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
            return
        feller_servo.angle = speak_rotation + config["feller_rest_pos"]
        sleepAndUpdateVolume(speak_cadence)
        feller_servo.angle = config["feller_rest_pos"]
        sleepAndUpdateVolume(speak_cadence)

def tree_talking_movement():
    speak_rotation = 2
    speak_cadence = 0.2
    while mixer.voice[0].playing:
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
        if switch_state == "left_held":
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
            return
        tree_servo.angle = config["tree_up_pos"]
        sleepAndUpdateVolume(speak_cadence)
        tree_servo.angle = config["tree_up_pos"] - speak_rotation
        sleepAndUpdateVolume(speak_cadence)

def play_sound(sound_files, folder):
    highest_index = len(sound_files) - 1
    sound_number = random.randint(0, highest_index)
    files.log_item(folder + ": " + str(sound_number))
    wave0 = audiocore.WaveFile(open("/sd/" + folder + "/" + sound_files[sound_number] + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing :
        sleepAndUpdateVolume(0.1)
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
        if switch_state == "left_held":
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
    wave0.deinit()
    garbage_collect("deinit wave0")
    
def animate_feller():
    
    sleepAndUpdateVolume(0.05)
    
    if config["opening_dialog"]:
        which_sound = random.randint(0,3)
        if which_sound == 0:
            play_sound(feller_wife, "feller_wife")
        if which_sound == 1:
            play_sound(feller_buddy, "feller_buddy")
        if which_sound == 2:
            play_sound(feller_poem, "feller_poem")
        if which_sound == 3:
            play_sound(feller_girlfriend, "feller_girlfriend")      
    chopNum = 1
    chopNumber = random.randint(int(config["min_chops"]), int(config["max_chops"]))
    highest_index = len(feller_dialog) - 1
    what_to_speak = random.randint(0, highest_index)
    when_to_speak = random.randint(1, chopNumber)
          
    files.log_item("Chop total: " + str(chopNumber) + " what to speak: " + str(what_to_speak) + " when to speak: " + str(when_to_speak))
    spoken = False
    tree_chop_pos = config["tree_up_pos"] - 3
    
    current_option_selected = config["option_selected"]
    if current_option_selected == "random":
        highest_index = len(feller_sound_options) - 2 #subtract -2 to avoid choosing "random" for a file 
        sound_number = random.randint(0, highest_index)
        current_option_selected = feller_sound_options[sound_number]
        print("Random sound file: " + feller_sound_options[sound_number])
    if current_option_selected == "happy_birthday":
        sound_number = random.randint(0, 6)
        soundFile = "/sd/feller_sounds/sounds_" + current_option_selected + str(sound_number) + ".wav"
        print("Sound file: " + current_option_selected + str(sound_number))
    else:
        soundFile = "/sd/feller_sounds/sounds_" + current_option_selected + ".wav"
        print("Sound file: " + current_option_selected)
      
    wave1 = audiocore.WaveFile(open(soundFile, "rb"))
    while chopNum <= chopNumber:
        if when_to_speak == chopNum and not spoken and config["feller_advice"]:
            spoken = True    
            soundFile = "/sd/feller_dialog/" + feller_dialog[what_to_speak] + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            feller_talking_movement()
            wave0.deinit()
            garbage_collect("deinit wave0")
            
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        
        for feller_angle in range(config["feller_rest_pos"], config["feller_chop_pos"] + 5, 10):  # 0 - 180 degrees, 10 degrees at a time.
            moveFellerServo(feller_angle)                                
            if feller_angle >= (config["feller_chop_pos"] - 10):
                mixer.voice[0].play( wave0, loop=False )
                shake = 2
                sleepAndUpdateVolume(0.2)
                for _ in range(shake):
                    moveTreeServo(tree_chop_pos)
                    sleepAndUpdateVolume(0.1)
                    moveTreeServo(config["tree_up_pos"])
                    sleepAndUpdateVolume(0.1)
                break
        if chopNum <= chopNumber: 
            for feller_angle in range(config["feller_chop_pos"], config["feller_rest_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
                moveFellerServo( feller_angle )
                sleepAndUpdateVolume(0.02)
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.1)     
    mixer.voice[0].play( wave1, loop=False )
    for tree_angle in range(config["tree_up_pos"], config["tree_down_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
        moveTreeServo(tree_angle)
        sleepAndUpdateVolume(0.06)
    shake = 8
    for _ in range(shake):
        moveTreeServo(config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
        moveTreeServo(7 + config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
    if current_option_selected == "alien":
        print("Alien sequence starting....")
        sleepAndUpdateVolume(2)
        moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
        moveTreeToPositionGently(config["tree_up_pos"], 0.01)
        left_pos = config["tree_up_pos"]
        right_pos = config["tree_up_pos"] - 8
        while mixer.voice[0].playing :
            switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
            if switch_state == "left_held":
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
                soundFile = "/sd/mvc/animation_canceled.wav"
                wave0 = audiocore.WaveFile(open(soundFile, "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
                break
            moveTreeToPositionGently(left_pos, 0.1)
            moveTreeToPositionGently(right_pos, 0.1)
        moveTreeToPositionGently(config["tree_up_pos"], 0.04)
        for alien_num in range(7):
            soundFile = "/sd/feller_alien/human_" + str(alien_num+1) + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            feller_talking_movement()
            soundFile = "/sd/feller_alien/alien_" + str(alien_num+1) + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            tree_talking_movement()
            switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
            if switch_state == "left_held":
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
                soundFile = "/sd/mvc/animation_canceled.wav"
                wave0 = audiocore.WaveFile(open(soundFile, "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
                break
    else:
        while mixer.voice[0].playing:
            switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 0.5)
            if switch_state == "left_held":
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
                soundFile = "/sd/mvc/animation_canceled.wav"
                wave0 = audiocore.WaveFile(open(soundFile, "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
                break
    wave0.deinit()
    wave1.deinit()
    garbage_collect("deinit wave0 wave1")
    moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
    sleepAndUpdateVolume(0.02)
    moveTreeToPositionGently(config["tree_up_pos"], 0.01)

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
        # set servos to starting position
        moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
        moveTreeToPositionGently(config["tree_up_pos"], 0.01)
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
            animate_feller()
        elif switch_state == "right":
            machine.go_to_state('main_menu')
class MoveFellerAndTree(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'move_feller_and_tree'

    def enter(self, machine):
        files.log_item('Move feller and tree menu')
        play_audio_0("/sd/mvc/move_feller_and_tree_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + move_feller_and_tree[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(move_feller_and_tree)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = move_feller_and_tree[self.selectedMenuIndex]
            if selected_menu_item == "move_feller_to_rest_position":
                moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
            elif selected_menu_item == "move_feller_to_chop_position":
                moveFellerToPositionGently(config["feller_chop_pos"], 0.01)
            elif selected_menu_item == "move_tree_to_upright_position":
                moveTreeToPositionGently(config["tree_up_pos"], 0.01)
            elif selected_menu_item == "move_tree_to_fallen_position":
                moveTreeToPositionGently(config["tree_down_pos"], 0.01)
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
                     
class AdjustFellerAndTree(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'adjust_feller_and_tree'

    def enter(self, machine):
        files.log_item('Adjust feller and tree menu')
        play_audio_0("/sd/mvc/adjust_feller_and_tree_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + adjust_feller_and_tree[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(adjust_feller_and_tree)-1:
                self.menuIndex = 0
        if right_switch.fell:
                selected_menu_item = adjust_feller_and_tree[self.selectedMenuIndex]
                if selected_menu_item == "move_feller_to_rest_position":
                    moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
                    fellerCalAnnouncement()
                    calibratePosition(feller_servo, "feller_rest_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_feller_to_chop_position":
                    moveFellerToPositionGently(config["feller_chop_pos"], 0.01)
                    fellerCalAnnouncement()
                    calibratePosition(feller_servo, "feller_chop_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_tree_to_upright_position":
                    moveTreeToPositionGently(config["tree_up_pos"], 0.01)
                    treeCalAnnouncement()
                    calibratePosition(tree_servo, "tree_up_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_tree_to_fallen_position":
                    moveTreeToPositionGently(config["tree_down_pos"], 0.01)
                    treeCalAnnouncement()
                    calibratePosition(tree_servo, "tree_down_pos")
                    machine.go_to_state('base_state')
                else:
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state')

class SetDialogOptions(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'set_dialog_options'

    def enter(self, machine):
        files.log_item('Set Dialog Options')
        selectDialogOptionsAnnouncement()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + dialog_selection_menu[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(dialog_selection_menu)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = dialog_selection_menu[self.selectedMenuIndex]
            if selected_menu_item == "opening_dialog_on":
                config["opening_dialog"] = True
                option_selected_announcement()
                selectDialogOptionsAnnouncement()
            elif selected_menu_item == "opening_dialog_off":
                config["opening_dialog"] = False
                option_selected_announcement()
                selectDialogOptionsAnnouncement()
            elif selected_menu_item == "lumberjack_advice_on":
                config["feller_advice"] = True
                option_selected_announcement()
                selectDialogOptionsAnnouncement()
            elif selected_menu_item == "lumberjack_advice_off":
                config["feller_advice"] = False
                option_selected_announcement()
                selectDialogOptionsAnnouncement()
            else:
                files.write_json_file("/sd/config_feller.json",config)
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
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
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
                    files.write_json_file("/sd/config_feller.json",config)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state')   
                                     
class ChooseSounds(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

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
                play_audio_0("/sd/mvc/option_" + feller_sound_options[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(feller_sound_options)-1:
                    self.menuIndex = 0
        if right_switch.fell:
            config["option_selected"] = feller_sound_options[self.selectedMenuIndex]
            files.log_item ("Selected index: " + str(self.selectedMenuIndex) + " Saved option: " + config["option_selected"])
            files.write_json_file("/sd/config_feller.json",config)
            option_selected_announcement()
            machine.go_to_state('base_state')

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
            elif selected_menu_item == "adjust_feller_and_tree":
                machine.go_to_state('adjust_feller_and_tree')
            elif selected_menu_item == "move_feller_and_tree":
                machine.go_to_state('move_feller_and_tree')
            elif selected_menu_item == "set_dialog_options":
                machine.go_to_state('set_dialog_options')
            elif selected_menu_item == "web_options":
                machine.go_to_state('web_options')
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
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
        
garbage_collect("state machine")

###############################################################################
# Create the state machine

state_machine = StateMachine()
state_machine.add_state(BaseState())
state_machine.add_state(MainMenu())
state_machine.add_state(ChooseSounds())
state_machine.add_state(AdjustFellerAndTree())
state_machine.add_state(MoveFellerAndTree())
state_machine.add_state(SetDialogOptions())
state_machine.add_state(WebOptions())

audio_enable.value = True

def speak_webpage():
    play_audio_0("/sd/mvc/animator_available_on_network.wav")
    play_audio_0("/sd/mvc/to_access_type.wav")
    if config["HOST_NAME"]== "animator-feller":
        play_audio_0("/sd/mvc/animator_feller_local.wav")
    else:
        speak_this_string(config["HOST_NAME"], True)
    play_audio_0("/sd/mvc/in_your_browser.wav")    

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
    sleepAndUpdateVolume(.1)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue

