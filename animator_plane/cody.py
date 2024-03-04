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
from rainbowio import colorwheel
ledStrip = neopixel.NeoPixel(board.GP15, 7)

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

audio_enable = digitalio.DigitalInOut(board.GP22)
audio_enable.direction = digitalio.Direction.OUTPUT
audio_enable.value = False

# Setup the servo
# also get the programmed values for position which is stored on the sdCard
plane_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
plane_rotaton_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

plane_servo = servo.Servo(plane_pwm, min_pulse=500, max_pulse=2500)
plane_rotation_servo = servo.ContinuousServo(plane_rotaton_pwm, min_pulse=500, max_pulse=2500)

zero_val = 0

plane_last_pos = 0
plane_min = 0
plane_max = 180

plane_servo.angle = 20

# Setup the switches
SWITCH_1_PIN = board.GP6 #S1 on animator board
SWITCH_2_PIN = board.GP7 #S2 on animator board
SWITCH_3_PIN = board.GP8 #S2 on animator board

switch_io_1 = digitalio.DigitalInOut(SWITCH_1_PIN)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP
left_switch = Debouncer(switch_io_1)

switch_io_2 = digitalio.DigitalInOut(SWITCH_2_PIN)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP
right_switch = Debouncer(switch_io_2)

switch_io_3 = digitalio.DigitalInOut(SWITCH_3_PIN)
switch_io_3.direction = digitalio.Direction.INPUT
switch_io_3.pull = digitalio.Pull.UP
home_switch = Debouncer(switch_io_3)

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
num_voices = 3
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,bits_per_sample=16, samples_signed=True, buffer_size=16384)
audio.play(mixer)

volume = .2
mixer.voice[0].level = volume
mixer.voice[1].level = volume
mixer.voice[2].level = volume

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

config = files.read_json_file("/sd/config_plane.json")
serve_webpage = config["serve_webpage"]

serve_webpage=False

################################################################################
# Dialog and sound play methods

def sleepAndUpdateVolume(seconds):
    if config["volume_pot"]:
        volume = get_voltage(analog_in, seconds)
        mixer.voice[0].level = volume
        mixer.voice[1].level = volume
        mixer.voice[2].level = volume
    else:
        try:
            volume = int(config["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mixer.voice[0].level = volume
        mixer.voice[1].level = volume
        mixer.voice[2].level = volume
        time.sleep(seconds)

def play_audio_0(file_name):
    if mixer.voice[0].playing:
        mixer.voice[0].stop()
        while mixer.voice[0].playing:
            sleepAndUpdateVolume(0.02)
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        shortCircuitDialog()

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
    if config["HOST_NAME"]== "animator-plane":
        play_audio_0("/sd/mvc/animator_dash_plane.wav")
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")
    else:
        speak_this_string(config["HOST_NAME"], True)
    play_audio_0("/sd/mvc/in_your_browser.wav") 
        
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
        
        ################################################################################
        # Setup routes

        @server.route("/")
        def base(request: HTTPRequest):
            garbage_collect("Home page.")
            return FileResponse(request, "index.html", "/")
        
        @server.route("/mui.min.css")
        def base(request: HTTPRequest):
            return FileResponse(request, "/sd/webpage/mui.min.css", "/")
        
        @server.route("/mui.min.js")
        def base(request: HTTPRequest):
            return FileResponse(request, "/sd/webpage/mui.min.js", "/")
            
    except Exception as e:
        serve_webpage = False
        files.log_item(e)
 
garbage_collect("web server")

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
    
def movePlaneServo (servo_pos):
    if servo_pos < plane_min: servo_pos = plane_min
    if servo_pos > plane_max: servo_pos = plane_max
    plane_servo.angle = servo_pos
    global plane_last_pos
    plane_last_pos = servo_pos

def movePlaneToPositionGently (new_position, speed):
    global plane_last_pos
    sign = 1
    if plane_last_pos > new_position: sign = - 1
    for plane_angle in range( plane_last_pos, new_position, sign):
        movePlaneServo (plane_angle)
        sleepAndUpdateVolume(speed)
    movePlaneServo (new_position)
    
throttle_max = -.11 #1563
throttle_min = -.11 #06
global throttle_range
throttle_range = throttle_max-throttle_min
global speed
speed = 0
global direction
direction = 1      

while False:
    sleepAndUpdateVolume(.02)
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
        
wave0 = audiocore.WaveFile(open("/sd/plane_sounds/plane.wav", "rb"))
wave1 = audiocore.WaveFile(open("wav/missle.wav", "rb"))
mixer.voice[0].play( wave0, loop=True )
sleepAndUpdateVolume(.1)
              
plane_up = False
number_rotations = 0

while True:
    if speed > 1: direction = -1
    if speed < 0: direction = 1
    speed = speed + direction *.02
    current_throttle = throttle_min + throttle_range * speed
    #print (current_throttle)
    plane_rotation_servo.throttle = current_throttle
    #print (speed)
    if switch_io_3.value == False:
        if mixer.voice[1].playing == False and plane_up == True:
            garbage_collect("Grabage collect sounds")
            mixer.voice[1].play( wave1, loop=False )
            ledStrip.fill((255, 255, 255))
            ledStrip.show()
            sleepAndUpdateVolume(.5)
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            number_rotations +=1
        if plane_up == False:
            plane_pos = 20
            movePlaneToPositionGently(plane_pos, .01)
            plane_up = True   
        elif number_rotations > 3:
            plane_pos = 180
            movePlaneToPositionGently(plane_pos, .01)
            plane_up = False
            number_rotations = 0
            