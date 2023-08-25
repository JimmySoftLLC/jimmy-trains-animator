import gc
import files

def garbage_collect(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item( "Point " + collection_point + " Available memory: {} bytes".format(start_mem) )
    
garbage_collect("Imports gc, files")

import sdcardio
import storage

import audiomp3
import audiocore
import audiomixer
import audiobusio
import os
import time

import board
import microcontroller
import busio
import pwmio
import digitalio

import random
import rtc

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
try:
  sdcard = sdcardio.SDCard(spi, cs)
  vfs = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")
except:
  wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
  audio.play(wave0)
  while audio.playing:
    pass
  wave0.deinit()
  garbage_collect("deinit wave0")
  cardInserted = False
  while not cardInserted:
    left_switch.update()
    if left_switch.fell:
        try:
            sdcard = sdcardio.SDCard(spi, cs)
            vfs = storage.VfsFat(sdcard)
            storage.mount(vfs, "/sd")
            cardInserted = True
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_success.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass
            wave0.deinit()
            garbage_collect("deinit wave0")
        except:
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass
            wave0.deinit()
            garbage_collect("deinit wave0")
            
audio.deinit()
audio_enable.value = False

garbage_collect("deinit audio")

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup the mixer it can play higher quality audio wav using larger wave files
# wave files are less cpu intensive since they are not compressed
num_voices = 2
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True, buffer_size=16384)
audio.play(mixer)

garbage_collect("audio setup")
        
import animate_feller
import utilities

garbage_collect("animator_feller, utilities")

################################################################################
# Global Variables

# get the calibration settings from various json files which are stored on the sdCard
config = files.read_json_file("/sd/config_feller.json")

tree_last_pos = config["tree_up_pos"]
tree_min = 90
tree_max = 180
if config["tree_down_pos"] < tree_min or config["tree_down_pos"] > tree_max: config["tree_down_pos"] = tree_min
if config["tree_up_pos"] < tree_min or config["tree_up_pos"] > tree_max: config["tree_up_pos"] = tree_max

feller_last_pos = config["feller_rest_pos"]
feller_min = 0
feller_max = 170
if config["feller_rest_pos"] < feller_min or config["feller_rest_pos"] > feller_max: config["feller_rest_pos"] = feller_min
if config["feller_chop_pos"] > feller_max or config["feller_chop_pos"] < feller_min: config["feller_chop_pos"] = feller_max

config_main_menu = files.read_json_file("/sd/feller_menu/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_choose_sounds = files.read_json_file("/sd/feller_menu/choose_sounds.json")
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

config_adjust_feller_and_tree = files.read_json_file("/sd/feller_menu/adjust_feller_and_tree.json")
adjust_feller_and_tree = config_adjust_feller_and_tree["adjust_feller_and_tree"]

config_move_feller_and_tree = files.read_json_file("/sd/feller_menu/move_feller_and_tree.json")
move_feller_and_tree = config_move_feller_and_tree["move_feller_and_tree"]

config_dialog_selection_menu = files.read_json_file("/sd/feller_menu/dialog_selection_menu.json")
dialog_selection_menu = config_dialog_selection_menu["dialog_selection_menu"]

config_web_menu = files.read_json_file("/sd/feller_menu/web_menu.json")
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

    try:
        env = files.read_json_file("/sd/env.json")
        garbage_collect("wifi env")
        
        # connect to your SSID
        wifi.radio.connect(env["WIFI_SSID"], env["WIFI_PASSWORD"])
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
        
        @server.route("/feller-adjust")
        def base(request: HTTPRequest):
            garbage_collect("Feller adjust.")
            return FileResponse(request, "feller-adjust.html", "/")
        
        @server.route("/tree-adjust")
        def base(request: HTTPRequest):
            garbage_collect("Tree adjust.")
            return FileResponse(request, "tree-adjust.html", "/")
        
        @server.route("/table")
        def base(request: HTTPRequest):
            garbage_collect("Table.")
            return FileResponse(request, "index-table.html", "/")
        
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
                animateFeller()
            elif "forth_of_july" in raw_text: 
                config["option_selected"] = "forth_of_july"
                animateFeller()
            elif "christmas" in raw_text: 
                config["option_selected"] = "christmas"
                animateFeller()
            elif "halloween" in raw_text: 
                config["option_selected"] = "halloween"
                animateFeller()
            elif "train" in raw_text: 
                config["option_selected"] = "train"
                animateFeller()
            elif "alien" in raw_text: 
                config["option_selected"] = "alien"
                animateFeller()  
            elif "birds_dogs_short_version" in raw_text: 
                config["option_selected"] = "birds_dogs_short_version"
                animateFeller()
            elif "birds_dogs" in raw_text: 
                config["option_selected"] = "birds_dogs"
                animateFeller()
            elif "just_birds" in raw_text: 
                config["option_selected"] = "just_birds"
                animateFeller()
            elif "machines" in raw_text: 
                config["option_selected"] = "machines"
                animateFeller()
            elif "no_sounds" in raw_text: 
                config["option_selected"] = "no_sounds"
                animateFeller()
            elif "owl" in raw_text: 
                config["option_selected"] = "owl"
                animateFeller()
            elif "happy_birthday" in raw_text: 
                config["option_selected"] = "happy_birthday"
                animateFeller()
            elif "speaker_test" in raw_text: 
                play_audio_0("/sd/feller_menu/left_speaker_right_speaker.wav")
            elif "cont_mode_on" in raw_text: 
                continuous_run = True
                play_audio_0("/sd/feller_menu/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                continuous_run = False
                play_audio_0("/sd/feller_menu/continuous_mode_deactivated.wav")
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
                pretty_state_machine.go_to_state('base_state')
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
                pretty_state_machine.go_to_state('base_state')
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
            play_audio_0("/sd/feller_menu/all_changes_complete.wav")

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
        
        @server.route("/save-data", [POST])
        def buttonpress(request: Request):
            data_object = request.json()
            print(data_object[0])
            print(data_object[1])
            print(data_object[2])
            garbage_collect("Save Data.")
            return Response(request, "success")
        
        @server.route("/get-host-name", [POST])
        def buttonpress(request: Request):
            return Response(request, config["HOST_NAME"])
        
        @server.route("/upload-endpoint", [POST])
        def upload_file_chunk(request: Request):
            try:
                data_object = request.body
                print(str(data_object))
                # add code to append to file here, more posts will just build on that....
                return Response(request, "success")
            except Exception as e:
                return Response(request, str(e))
           
    except Exception as e:
        serve_webpage = False
        files.log_item(e)

    
garbage_collect("web server")

################################################################################
# Global Methods

def reset_to_defaults():
    global config
    config["tree_up_pos"] = 165
    config["tree_down_pos"] = 100
    config["feller_rest_pos"] = 0
    config["feller_chop_pos"] = 150

def sleepAndUpdateVolume(seconds):
    volume = get_voltage(analog_in, seconds)
    mixer.voice[0].level = volume
    mixer.voice[1].level = volume

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
    while True:
        sleepAndUpdateVolume(.05)
        left_switch.update()
        if left_switch.fell:
            stop_audio_0()
            return

def left_right_mouse_button():
    play_audio_0("/sd/feller_menu/press_left_button_right_button.wav")

def option_selected_announcement():
    play_audio_0("/sd/feller_menu/option_selected.wav")

def fellerCalAnnouncement():
    play_audio_0("/sd/feller_menu/now_we_can_adjust_the_feller_position.wav")
    play_audio_0("/sd/feller_menu/to_exit_press_and_hold_button_down.wav")
    
def treeCalAnnouncement():
    play_audio_0("/sd/feller_menu/now_we_can_adjust_the_tree_position.wav")
    play_audio_0("/sd/feller_menu/to_exit_press_and_hold_button_down.wav")
    
def mainMenuAnnouncement():
    play_audio_0("/sd/feller_menu/main_menu.wav")
    left_right_mouse_button()
 
def selectSoundMenuAnnouncement():
    play_audio_0("/sd/feller_menu/sound_selection_menu.wav")
    left_right_mouse_button()
    
def adjustFellerAndTreeMenuAnnouncement():
    play_audio_0("/sd/feller_menu/adjust_feller_and_tree_menu.wav")
    left_right_mouse_button()
        
def moveFellerAndTreeMenuAnnouncement():
    play_audio_0("/sd/feller_menu/move_feller_and_tree_menu.wav")
    left_right_mouse_button()

def selectDialogOptionsAnnouncement():
    play_audio_0("/sd/feller_menu/dialog_selection_menu.wav")
    left_right_mouse_button()
    
def selectWebOptionsAnnouncement():
    play_audio_0("/sd/feller_menu/web_menu.wav")
    left_right_mouse_button()
 
def checkLimits(min_servo_pos, max_servo_pos, servo_pos):
    if servo_pos < min_servo_pos:
        play_audio_0("/sd/feller_menu/limit_reached.wav")
        return False
    if servo_pos > max_servo_pos:
        play_audio_0("/sd/feller_menu/limit_reached.wav")
        return False
    return True

def shortCircuitDialog():
    sleepAndUpdateVolume(0.02)
    left_switch.update()
    if left_switch.fell:
        mixer.voice[0].stop()

def speak_this_string(str_to_speak, addLocal):
    for character in str_to_speak:
        if character == "-":
            character = "dash"
        if character == ".":
            character = "dot"
        play_audio_0("/sd/feller_menu/" + character + ".wav")
    if addLocal:
        play_audio_0("/sd/feller_menu/dot.wav")
        play_audio_0("/sd/feller_menu/local.wav")
        
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
    play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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
        feller_servo.angle = feller_angle
        sleepAndUpdateVolume(speed)
    feller_servo.angle = new_position 
    feller_last_pos = new_position
    
def moveTreeToPositionGently (new_position, speed):
    global tree_last_pos
    sign = 1
    if tree_last_pos > new_position: sign = - 1
    for tree_angle in range( tree_last_pos, new_position, sign): 
        tree_servo.angle = tree_angle
        sleepAndUpdateVolume(speed)
    tree_servo.angle = new_position
    tree_last_pos = new_position

def moveFellerServo (servo_pos):
    feller_servo.angle = servo_pos
    global feller_last_pos
    feller_last_pos = servo_pos

def moveTreeServo (servo_pos):
    tree_servo.angle = servo_pos
    global tree_last_pos
    tree_last_pos = servo_pos
    
def animateFeller ():
    animate_feller.animation_one(
        sleepAndUpdateVolume, 
        audiocore, 
        mixer, 
        feller_servo, 
        tree_servo, 
        config,
        feller_sound_options, 
        feller_dialog,
        feller_wife,
        feller_poem,
        feller_buddy,
        feller_girlfriend,
        moveFellerServo,
        moveTreeServo,
        moveFellerToPositionGently,
        moveTreeToPositionGently,
        left_switch,
        right_switch,
        garbage_collect)

garbage_collect("servo helpers")

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
        sleepAndUpdateVolume(.1)
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            # set servos to starting position
            moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
            moveTreeToPositionGently(config["tree_up_pos"], 0.01)
            play_audio_0("/sd/feller_menu/animations_are_now_active.wav")
        files.log_item("Entered base state")
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global continuous_run
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 30)
        if switch_state == "left_held":
            if continuous_run:
                continuous_run = False
                play_audio_0("/sd/feller_menu/continuous_mode_deactivated.wav")
            else:
                continuous_run = True
                play_audio_0("/sd/feller_menu/continuous_mode_activated.wav")
        elif switch_state == "left" or continuous_run:
            animateFeller()
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
        moveFellerAndTreeMenuAnnouncement()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/feller_menu/" + move_feller_and_tree[self.menuIndex] + ".wav")
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
                play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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
        adjustFellerAndTreeMenuAnnouncement()
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
                play_audio_0("/sd/feller_menu/" + adjust_feller_and_tree[self.menuIndex] + ".wav")
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
                    play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                play_audio_0("/sd/feller_menu/" + dialog_selection_menu[self.menuIndex] + ".wav")
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
                    play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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
                play_audio_0("/sd/feller_menu/" + web_menu[self.menuIndex] + ".wav")
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
                    play_audio_0("/sd/feller_menu/web_instruct.wav")
                    selectWebOptionsAnnouncement()
                else:
                    files.write_json_file("/sd/config_feller.json",config)
                    play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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
                play_audio_0("/sd/feller_menu/option_" + feller_sound_options[self.menuIndex] + ".wav")
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
                play_audio_0("/sd/feller_menu/" + main_menu[self.menuIndex] + ".wav")
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
                elif selected_menu_item == "adjust_feller_and_tree":
                    machine.go_to_state('adjust_feller_and_tree')
                elif selected_menu_item == "move_feller_and_tree":
                    machine.go_to_state('move_feller_and_tree')
                elif selected_menu_item == "set_dialog_options":
                    machine.go_to_state('set_dialog_options')
                elif selected_menu_item == "web_options":
                    machine.go_to_state('web_options')
                else:
                    play_audio_0("/sd/feller_menu/all_changes_complete.wav")
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

pretty_state_machine = StateMachine()
pretty_state_machine.add_state(BaseState())
pretty_state_machine.add_state(MainMenu())
pretty_state_machine.add_state(ChooseSounds())
pretty_state_machine.add_state(AdjustFellerAndTree())
pretty_state_machine.add_state(MoveFellerAndTree())
pretty_state_machine.add_state(SetDialogOptions())
pretty_state_machine.add_state(WebOptions())

audio_enable.value = True

def speak_webpage():
    play_audio_0("/sd/feller_menu/animator_available_on_network.wav")
    play_audio_0("/sd/feller_menu/to_access_type.wav")
    if config["HOST_NAME"]== "animator-feller":
        play_audio_0("/sd/feller_menu/animator_feller_local.wav")
    else:
        speak_this_string(config["HOST_NAME"], True)
    play_audio_0("/sd/feller_menu/in_your_browser.wav")    

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
    sleepAndUpdateVolume(.1)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
