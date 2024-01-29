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
import microcontroller
import pwmio
from analogio import AnalogIn
from adafruit_debouncer import Debouncer
from adafruit_motor import servo
import utilities
import neopixel
import random
import asyncio

num_pixels = 7

ledStrip = neopixel.NeoPixel(board.GP13, num_pixels)

def reset_pico():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
    
garbage_collect("imports")

################################################################################
# Setup hardware

analog_in = AnalogIn(board.A0)


audio_enable = digitalio.DigitalInOut(board.GP22)
audio_enable.direction = digitalio.Direction.OUTPUT
audio_enable.value = False

# Setup the servo
# also get the programmed values for position which is stored on the sdCard
door_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
guy_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
roof_pwm = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)

door_servo = servo.Servo(door_pwm, min_pulse=500, max_pulse=2500)
guy_servo = servo.Servo(guy_pwm, min_pulse=500, max_pulse=2500)
roof_servo = servo.Servo(roof_pwm, min_pulse=500, max_pulse=2500)

zero_val = 0

door_last_pos = 90
door_min = 0
door_max = 180

guy_last_pos = 90
guy_min = 0
guy_max = 180

roof_last_pos = 90
roof_min = 0
roof_max = 180

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

volume = .1
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

################################################################################
# Sd card data Variables

config = files.read_json_file("/sd/config_outhouse.json")

serve_webpage = config["serve_webpage"]

#config_dialog_selection_menu = files.read_json_file("/sd/mvc/dialog_selection_menu.json")
dialog_selection_menu = [] #config_dialog_selection_menu["dialog_selection_menu"]

config_move_roof_door = files.read_json_file("/sd/mvc/move_roof_door.json")
move_roof_door = config_move_roof_door["move_roof_door"]

config_adjust_roof_door = files.read_json_file("/sd/mvc/adjust_roof_door.json")
adjust_roof_door = config_adjust_roof_door["adjust_roof_door"]

config_web_menu = files.read_json_file("/sd/mvc/web_menu.json")
web_menu = config_web_menu["web_menu"]

config_main_menu = files.read_json_file("/sd/mvc/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_choose_sounds = files.read_json_file("/sd/mvc/choose_sounds.json")
outhouse_sound_options = config_choose_sounds["choose_sounds"]

volume_settings_options = files.read_json_file("/sd/mvc/volume_settings.json")
volume_settings = volume_settings_options["volume_settings"]

continuous_run = False

################################################################################
# Dialog and sound play methods

def sleepAndUpdateVolume(seconds):
    if config["volume_pot"]:
        volume = analog_in.value / 65536
        mixer.voice[0].level = volume
        time.sleep(seconds)
    else:
        try:
            volume = int(config["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mixer.voice[0].level = volume
        time.sleep(seconds)
        
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
    files.write_json_file("/sd/config_outhouse.json",config)
    play_audio_0("/sd/mvc/volume.wav")
    speak_this_string(config["volume"], False)

def play_audio_0(file_name):
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            sleepAndUpdateVolume(0.02)
    print("playing"+ file_name) 
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        shortCircuitDialog()
    print("done playing") 

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

def left_right_mouse_button():
    play_audio_0("/sd/mvc/press_left_button_right_button.wav")

def option_selected_announcement():
    play_audio_0("/sd/mvc/option_selected.wav")

def selectDialogOptionsAnnouncement():
    play_audio_0("/sd/mvc/dialog_selection_menu.wav")
    left_right_mouse_button()

def doorCalAnnouncement():
    play_audio_0("/sd/mvc/now_we_can_adjust_the_feller_position.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")

def roofCalAnnouncement():
    play_audio_0("/sd/mvc/now_we_can_adjust_the_tree_position.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")

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
        
################################################################################
# Setup wifi and web server

if (serve_webpage):
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
    import adafruit_requests
    import ssl
    import ipaddress
    garbage_collect("config wifi imports")

    files.log_item("Connecting to WiFi")

    #default for manufacturing and shows
    WIFI_SSID="jimmytrainsguest"
    WIFI_PASSWORD=""

    try:
        env = files.read_json_file("/sd/env.json")
        #WIFI_SSID = env["WIFI_SSID"]
        #WIFI_PASSWORD = env["WIFI_PASSWORD"]
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
        files.log_item("My IP address is " + ip_address)
        files.log_item("Connected to WiFi")
        
        # set up server
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        server = Server(pool, "/static", debug=True)
        
        garbage_collect("wifi server")
        
        # jimmytrains animator URL
        
        test_url_fast = "http://192.168.1.200/get-volume"
        test_url = "http://tablet.local/get-volume"   
        try:
            print("Fetching text from %s" % test_url)
            response = requests.post(test_url)
            print("-" * 40)
            print("Text Response: ", response.text)
            print("-" * 40)
            response.close()
        except Exception as e:
            print("Error:\n", str(e))

        garbage_collect("requests")
        
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
            
    except Exception as e:
        serve_webpage = False
        files.log_item(e)
 
garbage_collect("web server")

################################################################################
# Servo helpers

def moveDoorServo (servo_pos):
    if servo_pos < door_min: servo_pos = door_min
    if servo_pos > door_max: servo_pos = door_max
    door_servo.angle = servo_pos
    global door_last_pos
    door_last_pos = servo_pos

def moveDoorToPositionGently (new_position, speed):
    global door_last_pos
    sign = 1
    if door_last_pos > new_position: sign = - 1
    for door_angle in range( door_last_pos, new_position, sign):
        moveDoorServo (door_angle)
        time.sleep(speed)
    moveDoorServo (new_position)

def moveGuyServo (servo_pos):
    if servo_pos < guy_min: servo_pos = guy_min
    if servo_pos > guy_max: servo_pos = guy_max
    guy_servo.angle = servo_pos
    global guy_last_pos
    guy_last_pos = servo_pos

def moveGuyToPositionGently (new_position, speed):
    global guy_last_pos
    sign = 1
    if guy_last_pos > new_position: sign = - 1
    for guy_angle in range( guy_last_pos, new_position, sign):
        moveGuyServo (guy_angle)
        time.sleep(speed)
    moveGuyServo (new_position)

def moveRoofServo (servo_pos):
    if servo_pos < roof_min: servo_pos = roof_min
    if servo_pos > roof_max: servo_pos = roof_max
    roof_servo.angle = servo_pos
    global roof_last_pos
    roof_last_pos = servo_pos

def moveRoofToPositionGently (new_position, speed):
    global roof_last_pos
    sign = 1
    if roof_last_pos > new_position: sign = - 1
    for roof_angle in range( roof_last_pos, new_position, sign):
        moveRoofServo (roof_angle)
        time.sleep(speed)
    moveRoofServo (new_position)

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
    files.write_json_file("/sd/config_outhouse.json",config)

def calibratePosition(servo, movement_type):  
    if movement_type == "feller_rest_pos" or movement_type == "feller_chop_pos" :
        min_servo_pos = guy_min
        max_servo_pos = guy_max
        sign = 1
    else:
        min_servo_pos = roof_min
        max_servo_pos = roof_max
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

################################################################################
# async methods

# Create an event loop
loop = asyncio.get_event_loop()

async def sleepAndUpdateVolumeAsync(seconds):
    if config["volume_pot"]: 
        volume = analog_in.value / 65536
        mixer.voice[0].level = volume
        await asyncio.sleep(seconds)
    else:
        try:
            volume = int(config["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mixer.voice[0].level = volume
        await asyncio.sleep(seconds)

async def fireAsync():
    startTime = time.monotonic()
    ledStrip.brightness = 1.0
 
    r = random.randint(150,255)
    g = 0 #random.randint(0,255)
    b = 0 #random.randint(0,255)

    #Flicker, based on our initial RGB values
    while mixer.voice[0].playing:
        for i in range (0, num_pixels):
            flicker = random.randint(0,175)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 50)
            b1 = bounds(b-flicker, 0, 50)
            ledStrip[i] = (r1,g1,b1)
        ledStrip.show()
        await sleepAndUpdateVolumeAsync(random.uniform(0.05,0.1))
        
async def cycleGuyAsync(speed, pos_up, pos_down): 
    global guy_last_pos
    while mixer.voice[0].playing:
        new_position = pos_up
        sign = 1
        if guy_last_pos > new_position: sign = - 1
        for guy_angle in range( guy_last_pos, new_position, sign):
            moveGuyServo (guy_angle)
            await asyncio.sleep(speed)
        new_position = pos_down
        sign = 1
        if guy_last_pos > new_position: sign = - 1
        for guy_angle in range( guy_last_pos, new_position, sign):
            moveGuyServo (guy_angle)
            await asyncio.sleep(speed)

async def runExplosion ():
    cycle_guy = asyncio.create_task(cycleGuyAsync(0.01,config["guy_up_position"]+20,config["guy_up_position"]))
    cycle_lights = asyncio.create_task(fireAsync())
    await asyncio.gather(cycle_guy, cycle_lights)
    while mixer.voice[0].playing:
        shortCircuitDialog()

################################################################################
# Animations
    
def animate_outhouse():
    print("sitting down")
    moveGuyToPositionGently(config["guy_down_position"]-10,0.05)
    ledStrip[0]=((255, 147, 41))
    ledStrip.show()
    ledStrip[0]=((255, 147, 41))
    ledStrip.show()
    moveDoorToPositionGently(config["door_open_position"], .05)
    moveGuyToPositionGently(config["guy_down_position"],0.05)
    moveDoorToPositionGently(config["door_closed_position"], .05)
    ledStrip[0]=((0, 0, 0))
    ledStrip.show()
    play_audio_0("/sd/occ_statements/roses_light_a_match.wav")
    play_audio_0("/sd/match_fails/fail1.wav")
    play_audio_0("/sd/match_fails/fail2.wav")
    play_audio_0("/sd/match_fails/fail1.wav")
    play_audio_0("/sd/match_lit/lit3.wav")
    time.sleep(.5)
    
    print("explosion")
    wave0 = audiocore.WaveFile(open("/sd/outhouse_sounds/sounds_birds_dogs_short_version.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    time.sleep(.1)
    moveRoofServo(130)
    moveGuyServo(0)
    moveDoorServo(20)
    delay_time = .05
    for i in range(1, 6):
        ledStrip[i]=(255, 0, 0)
        ledStrip.show()
        time.sleep(delay_time)
    asyncio.run(runExplosion())

    print("reset")
    ledStrip.fill((0,0,0))
    ledStrip.show()
    moveDoorServo(config["door_closed_position"])
    moveGuyToPositionGently(config["guy_down_position"]-10,0.001)
    time.sleep(.2)
    moveRoofToPositionGently(config["roof_closed_position"]+30, .001)
    moveRoofToPositionGently(config["roof_closed_position"], .05)
    time.sleep(2)
        
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
        # set servos to starting position
        moveGuyToPositionGently(200, 0.01)
        moveDoorToPositionGently(config["door_closed_position"], 0.01)
        moveRoofToPositionGently(config["roof_closed_position"], 0.01)
        
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
            animate_outhouse()
        elif switch_state == "right":
            machine.go_to_state('main_menu')

class MoveRoofDoor(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'move_roof_door'

    def enter(self, machine):
        files.log_item('Move roof and door menu')
        play_audio_0("/sd/mvc/move_roof_door.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + move_roof_door[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(move_roof_door)-1:
                self.menuIndex = 0
        if right_switch.fell:
            selected_menu_item = move_roof_door[self.selectedMenuIndex]
            if selected_menu_item == "move_door_open_position":
                moveDoorToPositionGently(config["door_open_position"], 0.01)
            elif selected_menu_item == "move_door_closed_position":
                moveDoorToPositionGently(config["door_closed_position"], 0.01)
            elif selected_menu_item == "move_roof_open_position":
                moveGuyToPositionGently(config["roof_open_position"], 0.01)
            elif selected_menu_item == "move_roof_closed_position":
                moveGuyToPositionGently(config["roof_closed_position"], 0.01)
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
                     
class AdjustRoofDoor(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'adjust_roof_door'

    def enter(self, machine):
        files.log_item('Adjust roof door menu')
        play_audio_0("/sd/mvc/adjust_roof_door.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            play_audio_0("/sd/mvc/" + adjust_roof_door[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex +=1
            if self.menuIndex > len(adjust_roof_door)-1:
                self.menuIndex = 0
        if right_switch.fell:
                selected_menu_item = adjust_roof_door[self.selectedMenuIndex]
                if selected_menu_item == "move_door_open_position":
                    moveDoorToPositionGently(config["adjust_door_open_position"], 0.01)
                    doorCalAnnouncement()
                    calibratePosition(guy_servo, "door_open_position")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "adjust_door_closed_position":
                    moveDoorToPositionGently(config["door_closed_position"], 0.01)
                    doorCalAnnouncement()
                    calibratePosition(guy_servo, "door_closed_position")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "adjust_roof_open_position":
                    moveRoofToPositionGently(config["roof_open_position"], 0.01)
                    roofCalAnnouncement()
                    calibratePosition(door_servo, "roof_open_position")
                    machine.go_to_state('base_state')
                elif selected_menu_item == "adjust_roof_closed_position":
                    moveRoofToPositionGently(config["roof_closed_position"], 0.01)
                    roofCalAnnouncement()
                    calibratePosition(door_servo, "roof_closed_position")
                    machine.go_to_state('base_state')
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
                            files.write_json_file("/sd/config_outhouse.json",config)
                            play_audio_0("/sd/mvc/all_changes_complete.wav")
                            done = True
                            machine.go_to_state('base_state')
                        sleepAndUpdateVolume(0.1)
                        pass
                elif selected_menu_item == "volume_pot_off":
                    config["volume_pot"] = False
                    if config["volume"] == 0:
                        config["volume"] = 10
                    files.write_json_file("/sd/config_outhouse.json",config)
                    play_audio_0("/sd/mvc/all_changes_complete.wav")
                    machine.go_to_state('base_state') 
                elif selected_menu_item == "volume_pot_on":
                    config["volume_pot"] = True
                    files.write_json_file("/sd/config_outhouse.json",config)
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
                    files.write_json_file("/sd/config_outhouse.json",config)
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
                play_audio_0("/sd/mvc/option_" + outhouse_sound_options[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(outhouse_sound_options)-1:
                    self.menuIndex = 0
        if right_switch.fell:
            config["option_selected"] = outhouse_sound_options[self.selectedMenuIndex]
            files.log_item ("Selected index: " + str(self.selectedMenuIndex) + " Saved option: " + config["option_selected"])
            files.write_json_file("/sd/config_outhouse.json",config)
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
            elif selected_menu_item == "adjust_roof_door":
                machine.go_to_state('adjust_roof_door')
            elif selected_menu_item == "move_roof_door":
                machine.go_to_state('move_roof_door')
            elif selected_menu_item == "set_dialog_options":
                machine.go_to_state('set_dialog_options')
            elif selected_menu_item == "web_options":
                machine.go_to_state('web_options')
            elif selected_menu_item == "volume_settings":
                machine.go_to_state('volume_settings')
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
state_machine.add_state(AdjustRoofDoor())
state_machine.add_state(MoveRoofDoor())
state_machine.add_state(WebOptions())
state_machine.add_state(VolumeSettings())

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
        reset_pico
    
state_machine.go_to_state('base_state')   
files.log_item("animator has started...")
garbage_collect("animations started.")

while True:
    loop.run_forever()
    state_machine.update()
    sleepAndUpdateVolume(.1)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
