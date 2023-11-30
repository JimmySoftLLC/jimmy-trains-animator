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

# Setup the servo, this animation has two the feller and tree
# also get the programmed values for position which is stored on the sdCard
feller_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
tree_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

feller_servo = servo.Servo(feller_pwm)
tree_servo = servo.Servo(tree_pwm)

tree_last_pos = 120
tree_min = 60
tree_max = 180

tree_servo.angle = tree_last_pos

def moveTreeServo (servo_pos):
    if servo_pos < tree_min: servo_pos = tree_min
    if servo_pos > tree_max: servo_pos = tree_max
    tree_servo.angle = servo_pos
    global tree_last_pos
    tree_last_pos = servo_pos

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
            
        try:
            print("Fetching text from %s" % test_url_fast)
            response = requests.post(test_url_fast)
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
# Tmcc, legacy and UART communications

uart = busio.UART(board.GP0, board.GP1, baudrate=9600, bits=8, parity=None)

def getCommandObject(binary_word2,binary_word3):
    command = binary_word2[0:2]
    response = {}
    if command == "01": #switch command
        response["module"] = "switch"
        response["address"] = whatAddress(binary_word2,binary_word3,7)
    elif command == "00": #engine command
        response["module"] = "engine"
        response["address"] = whatAddress(binary_word2,binary_word3,7)
    elif command == "10": #accessory command
        response["module"] = "accessory"
        response["address"] = whatAddress(binary_word2,binary_word3,7)
    elif command == "11": #other command
        response["address"] = response["module"] = "other"
    response["command"] = whatCommand(binary_word3)
    response["data"] = whatData(binary_word3)
    return response
             
def whatAddress(binary_word2,binary_word3,number_bits):
    whole_word = binary_word2 + binary_word3
    start = 9-number_bits
    end = start + number_bits
    binary_number = whole_word[start:end]
    decimal_number = int(binary_number, 2)
    return decimal_number
    
def whatCommand(binary_word3):
    command = binary_word3[1:3]
    if command == "00": #action command
        return "action"
    elif command == "01": #extended command
        return "extended"
    elif command == "10": #speed command
        return "relative"
    elif command == "11": #speed command
        return "absolute"
    
def whatData(binary_word3):
    data = binary_word3[3:8]
    return data

def scale_number(num, exponent):
    if num < 0:
        return int(-(-num) ** exponent)
    else:
        return int(num ** exponent)

def processCommand(response):
    if response["module"] == "accessory":
        if response["command"] == "extended" and response["data"] =="01011":
            play_audio_0("/sd/mvc/accessory.wav")
            play_audio_0("/sd/mvc/set_to_id.wav")
            speak_this_string(str(response["address"]),False)
        elif response["command"] == "relative":
            binary_number = response["data"][1:5]
            decimal_number = scale_number(5-int(binary_number, 2),2)
            print(decimal_number)
            moveTreeServo (tree_last_pos+decimal_number)
            #play_audio_0("/sd/mvc/accessory.wav")
            #speak_this_string(str(response["address"]),False) 
            #play_audio_0("/sd/mvc/trottle_up.wav")
            #moveTreeServo (tree_last_pos+1)
            #play_audio_0("/sd/mvc/accessory.wav")
            #speak_this_string(str(response["address"]),False) 
            #play_audio_0("/sd/mvc/trottle_down.wav")
        elif response["command"] == "action" and response["data"][0:1] =="1":
            play_audio_0("/sd/mvc/accessory.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/numeric_button.wav")
            binary_number = response["data"][1:5]
            decimal_number = int(binary_number, 2)
            speak_this_string(str(decimal_number),False)
    if response["module"] == "engine":
        if response["command"] == "extended" and response["data"] =="01011":
            play_audio_0("/sd/mvc/engine.wav")
            play_audio_0("/sd/mvc/set_to_id.wav")
            speak_this_string(str(response["address"]),False)
        elif response["command"] == "relative" and response["data"] =="00110":
            play_audio_0("/sd/mvc/engine.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_up.wav")
        elif response["command"] == "relative" and response["data"] =="00100":
            play_audio_0("/sd/mvc/engine.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_down.wav")
        elif response["command"] == "action" and response["data"][0:1] =="1":
            play_audio_0("/sd/mvc/engine.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/numeric_button.wav")
            binary_number = response["data"][1:5]
            decimal_number = int(binary_number, 2)      
            speak_this_string(str(decimal_number),False) 
    if response["module"] == "switch":
        if response["command"] == "extended" and response["data"] =="01011":
            play_audio_0("/sd/mvc/switch.wav")
            play_audio_0("/sd/mvc/set_to_id.wav")
            speak_this_string(str(response["address"]),False)
        elif response["command"] == "relative" and response["data"] =="00110":
            play_audio_0("/sd/mvc/switch.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_up.wav")
        elif response["command"] == "relative" and response["data"] =="00100":
            play_audio_0("/sd/mvc/switch.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_down.wav")
        elif response["command"] == "action" and response["data"][0:1] =="1":
            play_audio_0("/sd/mvc/switch.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/numeric_button.wav")
            binary_number = response["data"][1:5]
            decimal_number = int(binary_number, 2)      
            speak_this_string(str(decimal_number),False)          
        
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

# the following is to help decode the lionel tmcc commands
while True:
    if (serve_webpage):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
    if uart.in_waiting >= 3:  # Check if at least 3 bytes are available to read
        received_data = uart.read(3)
        if len(received_data) == 3:
            word1, word2, word3 = received_data[0], received_data[1], received_data[2]
            
            # Convert words to binary strings
            binary_word1 = f'{word1:0>8b}'
            binary_word2 = f'{word2:0>8b}'
            binary_word3 = f'{word3:0>8b}'
            
            #print("Received command: " + str(received_data))
            #print("Received 0: " + str(received_data[0]))
            #print("Received 1: " + str(received_data[1]))
            #print("Received 2: " + str(received_data[2]))
            #print(f"Word 1: {binary_word1}")
            #print(f"Word 2: {binary_word2}")
            #print(f"Word 3: {binary_word3}\n")
            response = getCommandObject(binary_word2,binary_word3)
            processCommand(response)
            #print(response["module"],response["address"],response["command"],response["data"])
            uart.read(uart.in_waiting)
            
            # Reconstruct the command bytes
            #reconstructed_word1 = int(binary_word1, 2).to_bytes(1, 'big')
            #reconstructed_word2 = int(binary_word2, 2).to_bytes(1, 'big')
            #reconstructed_word3 = int(binary_word3, 2).to_bytes(1, 'big')
            
            # Construct the command to send back
            #reconstructed_command = reconstructed_word1 + reconstructed_word2 + reconstructed_word3
            #print("Reconstructed command: " + str(reconstructed_command))
            # Echo back the received command
            # uart.write(reconstructed_command)  # Echo back the received command
        else:
            # Invalid command format, discard the data
            uart.read(uart.in_waiting)
