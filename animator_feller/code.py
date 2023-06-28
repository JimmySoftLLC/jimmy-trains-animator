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

def get_voltage(pin):
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

serve_webpage = config["serve_webpage"]

feller_movement_type = "feller_rest_pos"
tree_movement_type = "tree_up_pos"

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
        mdns_server.hostname = env["HOST_NAME"]
        mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
        
        # files.log_items MAC address to REPL
        mystring = [hex(i) for i in wifi.radio.mac_address]
        files.log_item("My MAC addr:" + str(mystring))

        # files.log_items IP address to REPL
        files.log_item("My IP address is" + str(wifi.radio.ipv4_address))
        files.log_item("Connected to WiFi")
        
        # set up server
        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)
        garbage_collect("wifi server")
        
        def getTime(): 
            get_time_url = "https://worldtimeapi.org/api/timezone/America/New_York"
            requests = adafruit_requests.Session(pool, ssl.create_default_context())
            try:
                files.log_item("Fetching time from %s" % get_time_url)
                response = requests.get(get_time_url)  
                responseObject = files.json_parse(response.text)
                files.log_item(responseObject["timezone"])
                files.log_item(responseObject["datetime"])
                response.close()
                time.sleep(1)
                return responseObject["datetime"]
            except Exception as e:
                files.log_item("Error:\n", str(e))
        
        ################################################################################
        # Setup routes

        # serve webpage
        @server.route("/")
        def base(request: HTTPRequest):
            return FileResponse(request, "index.html", "/")
        
        @server.route("/feller-adjust")
        def base(request: HTTPRequest):
            return FileResponse(request, "feller-adjust.html", "/")
        
        @server.route("/tree-adjust")
        def base(request: HTTPRequest):
            return FileResponse(request, "tree-adjust.html", "/")

        # if a button is pressed on the site
        @server.route("/animation", [POST])
        def buttonpress(request: Request):
            global config
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
            elif "speaker_test" in raw_text: 
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/left_speaker_right_speaker.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        # if a button is pressed on the site
        @server.route("/feller", [POST])        
        def buttonpress(request: Request):
            global config
            global feller_movement_type
            raw_text = request.raw_request.decode("utf8")    
            if "feller_rest_pos" in raw_text:
                feller_movement_type = "feller_rest_pos"
                moveFellerToPositionGently(config[feller_movement_type])
                return Response(request, "Moved feller to rest position.")
            elif "feller_chop_pos" in raw_text:
                feller_movement_type = "feller_chop_pos"
                moveFellerToPositionGently(config[feller_movement_type])
                return Response(request, "Moved feller to chop position.")
            elif "feller_adjust" in raw_text:
                feller_movement_type = "feller_rest_pos"
                moveFellerToPositionGently(config[feller_movement_type])
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
                
        # if a button is pressed on the site
        @server.route("/tree", [POST])        
        def buttonpress(request: Request):
            global config
            global tree_movement_type
            raw_text = request.raw_request.decode("utf8")    
            if "tree_up_pos" in raw_text:
                tree_movement_type = "tree_up_pos"
                moveTreeToPositionGently(config[tree_movement_type])
                return Response(request, "Moved tree to up position.")
            elif "tree_down_pos" in raw_text:
                tree_movement_type = "tree_down_pos"
                moveTreeToPositionGently(config[tree_movement_type])
                return Response(request, "Moved tree to fallen position.")
            elif "tree_adjust" in raw_text:
                tree_movement_type = "tree_up_pos"
                moveTreeToPositionGently(config[tree_movement_type])
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

def setVolume():
    volume = get_voltage(analog_in)
    mixer.voice[0].level = volume
    mixer.voice[1].level = volume
    
def sleepAndUpdateVolume(seconds):
    setVolume()
    time.sleep(seconds)
    
garbage_collect("global variable and methods")

################################################################################
# Dialog
    
def fellerCalAnnouncement():
    global left_switch
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/now_we_can_adjust_the_feller_position.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/to_exit_press_and_hold_button_down.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    
def treeCalAnnouncement():
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/now_we_can_adjust_the_tree_position.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/to_exit_press_and_hold_button_down.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    
def mainMenuAnnouncement():
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            pass
    else:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/main_menu.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
    
def selectSoundMenuAnnouncement():
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            pass
    else:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/sound_selection_menu.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
    
def adjustFellerAndTreeMenuAnnouncement():
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            pass
    else:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/adjust_feller_and_tree_menu.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        
def moveFellerAndTreeMenuAnnouncement():
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            pass
    else:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/move_feller_and_tree_menu.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        
def checkLimits(min_servo_pos, max_servo_pos, servo_pos):
    if servo_pos < min_servo_pos:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/limit_reached.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass 
        return False
    if servo_pos > max_servo_pos:
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/limit_reached.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass 
        return False
    return True

def shortCircuitDialog():
    sleepAndUpdateVolume(0.02)
    left_switch.update()
    if left_switch.fell:
        mixer.voice[0].stop()
        
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
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
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

def moveFellerToPositionGently (new_position):
    global feller_last_pos
    files.log_item("feller angle: " + str(tree_last_pos) + "  " + str(new_position))
    sign = 1
    if feller_last_pos > new_position: sign = - 1
    for feller_angle in range( feller_last_pos, new_position, sign):
        feller_servo.angle = feller_angle
        sleepAndUpdateVolume(0.01)
    feller_servo.angle = new_position 
    feller_last_pos = new_position
    
def moveTreeToPositionGently (new_position):
    global tree_last_pos
    files.log_item("tree angle: " + str(tree_last_pos) + "  " + str(new_position))
    sign = 1
    if tree_last_pos > new_position: sign = - 1
    for tree_angle in range( tree_last_pos, new_position, sign): 
        tree_servo.angle = tree_angle
        sleepAndUpdateVolume(0.01)
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
            moveFellerToPositionGently(config["feller_rest_pos"])
            sleepAndUpdateVolume(0.02)
            moveTreeToPositionGently(config["tree_up_pos"])
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/animations_are_now_active.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
        files.log_item("Entered base state")
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 30)
        if switch_state == "left_held":
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/continuous_mode_activated.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
            continuous_run = True
            while continuous_run:
                sleepAndUpdateVolume(0.5)
                switch_state = utilities.switch_state(left_switch, right_switch, sleepAndUpdateVolume, 30)
                if switch_state == "left_held":
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/continuous_mode_deactivated.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
                    continuous_run = False
                if continuous_run:
                    animateFeller()
        elif switch_state == "left":
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
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/" + move_feller_and_tree[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(move_feller_and_tree)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    shortCircuitDialog()
        if right_switch.fell:
                selected_menu_item = move_feller_and_tree[self.selectedMenuIndex]
                if selected_menu_item == "move_feller_to_rest_position":
                    moveFellerToPositionGently(config["feller_rest_pos"])
                elif selected_menu_item == "move_feller_to_chop_position":
                    moveFellerToPositionGently(config["feller_chop_pos"])
                elif selected_menu_item == "move_tree_to_upright_position":
                    moveTreeToPositionGently(config["tree_up_pos"])
                elif selected_menu_item == "move_tree_to_fallen_position":
                    moveTreeToPositionGently(config["tree_down_pos"])
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
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
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/" + adjust_feller_and_tree[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(adjust_feller_and_tree)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    shortCircuitDialog()
        if right_switch.fell:
                selected_menu_item = adjust_feller_and_tree[self.selectedMenuIndex]
                if selected_menu_item == "move_feller_to_rest_position":
                    moveFellerToPositionGently(config["feller_rest_pos"])
                    fellerCalAnnouncement()
                    calibratePosition(feller_servo, "feller_rest_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_feller_to_chop_position":
                    moveFellerToPositionGently(config["feller_chop_pos"])
                    fellerCalAnnouncement()
                    calibratePosition(feller_servo, "feller_chop_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_tree_to_upright_position":
                    moveTreeToPositionGently(config["tree_up_pos"])
                    treeCalAnnouncement()
                    calibratePosition(tree_servo, "tree_up_pos")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "move_tree_to_fallen_position":
                    moveTreeToPositionGently(config["tree_down_pos"])
                    treeCalAnnouncement()
                    calibratePosition(tree_servo, "tree_down_pos")
                    machine.go_to_state('base_state')
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
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
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/option_" + feller_sound_options[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(feller_sound_options)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    shortCircuitDialog()
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            config["option_selected"] = feller_sound_options[self.selectedMenuIndex]
            files.log_item ("Selected index: " + str(self.selectedMenuIndex) + " Saved option: " + config["option_selected"])
            files.write_json_file("/sd/config_feller.json",config)
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/option_selected.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
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
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/" + main_menu[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(main_menu)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    shortCircuitDialog()
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
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
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

audio_enable.value = True

sleepAndUpdateVolume(.1)

# speak each character in a string
def speak_this_string(str_to_speak):
    for character in str_to_speak:
        if character == "-":
            character = "dash"
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/"+ character + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/dot.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass
    wave0 = audiocore.WaveFile(open("/sd/feller_menu/local.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        pass

if (serve_webpage):
    files.log_item("starting server...")
    # startup the server
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/animator_available_on_network.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/to_access_type.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        if env["HOST_NAME"]== "animator-feller":
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/animator_feller_local.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
        else:
            speak_this_string(env["HOST_NAME"])
        wave0 = audiocore.WaveFile(open("/sd/feller_menu/in_your_browser.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
    # if the server fails to begin, restart the pico w
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        reset_pico()
        
pretty_state_machine.go_to_state('base_state')
    
files.log_item("animator has started...")

while True:
    pretty_state_machine.update()
    sleepAndUpdateVolume(.1)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
