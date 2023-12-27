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
ledStrip = neopixel.NeoPixel(board.GP13, 7)

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

audio_enable = digitalio.DigitalInOut(board.GP28)
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

################################################################################
# Sd card data Variables

config = files.read_json_file("/sd/config_lightning.json")
serve_webpage = config["serve_webpage"]

################################################################################
# Dialog and sound play methods

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
    if config["HOST_NAME"]== "animator-lightning":
        play_audio_0("/sd/mvc/animator_dash_lightning.wav")
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
ledStrip = neopixel.NeoPixel(board.GP13, 7)

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

audio_enable = digitalio.DigitalInOut(board.GP28)
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

################################################################################
# Sd card data Variables

config = files.read_json_file("/sd/config_lightning.json")
serve_webpage = config["serve_webpage"]

################################################################################
# Dialog and sound play methods

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
    if config["HOST_NAME"]== "animator-lightning":
        play_audio_0("/sd/mvc/animator_dash_lightning.wav")
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

def explodeOuthouse():
    print("hanging out")
    ledStrip[0]=((255, 147, 41))
    ledStrip.show()
    moveDoorToPositionGently(20, .05)
    moveGuyToPositionGently(170,0.05)
    moveGuyToPositionGently(180,0.05)
    ledStrip[0]=((0, 0, 0))
    ledStrip.show()
    time.sleep(2)

    delay_time = .05
    print("explode")
    moveRoofServo(130)
    moveDoorServo(20)
    moveGuyToPositionGently(0,0.001)
    ledStrip[1]=(255, 0, 0)
    ledStrip.show()
    time.sleep(delay_time)
    ledStrip[2]=(255, 0, 0)
    ledStrip.show()
    time.sleep(delay_time)
    ledStrip[3]=(255, 0, 0)
    ledStrip.show()
    time.sleep(delay_time)
    ledStrip[4]=(255, 0, 0)
    ledStrip.show()
    time.sleep(delay_time)
    ledStrip[5]=(255, 0, 0)
    ledStrip.show()
    time.sleep(2)

    print("reset")
    ledStrip.fill((0,0,0))
    ledStrip.show()
    moveDoorServo(120)
    moveGuyToPositionGently(180,0.001)
    time.sleep(.2)
    moveRoofToPositionGently(70, .001)
    moveRoofToPositionGently(55, .05)
    time.sleep(2)
    
while True:
    explodeOuthouse()