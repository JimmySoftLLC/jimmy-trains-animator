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
import neopixel
import random
import rtc
import microcontroller

import audiomp3
from analogio import AnalogIn
from rainbowio import colorwheel
from adafruit_debouncer import Debouncer

from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.sequence import AnimationSequence
import asyncio

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
try:
  sdcard = sdcardio.SDCard(spi, cs)
  vfs = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")
except:
  wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
  audio.play(wave0)
  while audio.playing:
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
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_success.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass
        except:
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass

# Setup the mixer it can play higher quality audio wav using larger wave files
# wave files are less cpu intensive since they are not compressed
num_voices = 1
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True, buffer_size=8192)
audio.play(mixer)

audio_enable.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

#setup neo pixels
num_pixels = 60
ledStrip = neopixel.NeoPixel(board.GP10, num_pixels)
ledStrip.auto_write = False
ledStrip.brightness = 1.0

################################################################################
# Global Variables

config = files.read_json_file("/sd/config_lightning.json")

sound_options = config["options"]

serve_webpage = config["serve_webpage"]

garbage_collect("config setup")

continuous_run = False

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
                animation(config["option_selected"])
            elif "thunder_birds_rain" in raw_text: 
                config["option_selected"] = "thunder_birds_rain"
                animation(config["option_selected"])
            elif "continuous_thunder" in raw_text: 
                config["option_selected"] = "continuous_thunder"
                animation(config["option_selected"])
            elif "dark_thunder" in raw_text: 
                config["option_selected"] = "dark_thunder"
                animation(config["option_selected"])
            elif "epic_thunder" in raw_text: 
                config["option_selected"] = "epic_thunder"
                animation(config["option_selected"])
            elif "halloween_thunder" in raw_text: 
                config["option_selected"] = "halloween_thunder"
                animation(config["option_selected"])
            elif "thunder_and_rain" in raw_text: 
                config["option_selected"] = "thunder_and_rain"
                animation(config["option_selected"])
            elif "thunder_distant" in raw_text: 
                config["option_selected"] = "thunder_distant"
                animation(config["option_selected"])
            elif "inspiring_cinematic_ambient_lightshow" in raw_text: 
                config["option_selected"] = "inspiring_cinematic_ambient_lightshow"
                animation(config["option_selected"])
            elif "alien_lightshow" in raw_text: 
                config["option_selected"] = "alien_lightshow"
                animation(config["option_selected"])
            elif "cont_mode_on" in raw_text: 
                continuous_run = True
                play_audio_0("/sd/menu_voice_commands/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text: 
                continuous_run = False
                play_audio_0("/sd/menu_voice_commands/continuous_mode_deactivated.wav")
            return Response(request, "Animation " + config["option_selected"] + " started.")
        
        @server.route("/utilities", [POST])
        def buttonpress(request: Request):
            global config
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text: 
                play_audio_0("/sd/menu_voice_commands/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                config["volume_pot"] = False
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                config["volume_pot"] = True
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                reset_to_defaults()      
                files.write_json_file("/sd/config_lightning.json",config)
                play_audio_0("/sd/menu_voice_commands/all_changes_complete.wav")
                pretty_state_machine.go_to_state('base_state')
            elif "set_to_red" in raw_text:
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
            return Response(request, "Dialog option cal saved.")

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
            config["volume"] = data_object["text"]
            config["volume_pot"] = False
            files.write_json_file("/sd/config_lightning.json",config)       
            speak_this_string(config["volume"], False)

            return Response(request, config["volume"])
        
        @server.route("/get-volume", [POST])
        def buttonpress(request: Request):
            return Response(request, config["volume"])
           
    except Exception as e:
        serve_webpage = False
        files.log_item(e)

    
garbage_collect("web server")

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
        if character == "-":
            character = "dash"
        if character == ".":
            character = "dot"
        play_audio_0("/sd/menu_voice_commands/" + character + ".wav")
    if addLocal:
        play_audio_0("/sd/menu_voice_commands/dot.wav")
        play_audio_0("/sd/menu_voice_commands/local.wav")

################################################################################
# animations

def lightning(ledStrip):
    r = random.randint(40, 80)
    g = random.randint(10, 25)
    b = random.randint(0, 10)

    # number of flashes
    flashCount = random.randint (5, 10)

    # flash white brightness range - 0-255
    flashBrightnessMin =  150
    flashBrightnessMax =  255
    flashBrightness = random.randint(flashBrightnessMin, flashBrightnessMax) / 255
    ledStrip.brightness = flashBrightness
    
    #print (str(time.monotonic()-startTime))

    # flash duration range - ms
    flashDurationMin = 5
    flashDurationMax = 75

    # flash off range - ms
    flashOffsetMin = 0
    flashOffsetMax = 75

    # time to next flash range - ms
    nextFlashDelayMin = 1
    nextFlashDelayMax = 50
    
    for i in range(0,flashCount):
        color = random.randint(0, 50)
        if color < 0: color = 0
        
        ledStrip.fill((r + color, g + color, b + color))
        ledStrip.show()
        delay = random.randint(flashOffsetMin, flashOffsetMax)
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
        
        ledStrip.fill((r + color, g + color, b + color))
        ledStrip.show()
        delay = random.randint(flashOffsetMin, flashOffsetMax)
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
        
        ledStrip.fill((r + color, g + color, b + color))
        ledStrip.show();
        delay = random.randint(flashOffsetMin, flashOffsetMax)
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
        
        ledStrip.fill((r + color, g + color, b + color))
        ledStrip.show()
        delay = random.randint(flashOffsetMin, flashOffsetMax)
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
        
        delay = random.randint(nextFlashDelayMin, nextFlashDelayMax)
        delay = delay/1000
        time.sleep(delay)
        ledStrip.fill((0, 0, 0))
        ledStrip.show()
        
def animation(file_name):
    print(file_name)
    if file_name == "alien_lightshow":
        animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "inspiring_cinematic_ambient_lightshow":
        animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
        #animation_lightshow_async(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "timestamp_mode":
        animation_timestamp(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "breakfast_at_diner":
        breakfast_at_diner(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "continuous_thunder":
        continuous_thunder(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    else:
        thunder_once_played(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
        
def continuous_thunder(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    
    while True:
        wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        startTime = time.monotonic()
        pressed_stop_button = False
        flashTimeIndex = 0
        while True:
            sleepAndUpdateVolume(.1)
            timeElasped = time.monotonic()-startTime
            right_switch.update()
            if right_switch.fell:
                print(timeElasped)
            if timeElasped > flashTime[flashTimeIndex] - random.uniform(.5, 2): #amount of time before you here thunder 0.5 is synched with the lightning
                flashTimeIndex += 1
                lightning(ledStrip)
            if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
            left_switch.update()
            if left_switch.fell:
                mixer.voice[0].stop()
                pressed_stop_button = True
            if not mixer.voice[0].playing:
                break
        if pressed_stop_button:
            break

def thunder_once_played(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()

    while True:
        sleepAndUpdateVolume(.1)
        timeElasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            print(timeElasped)
        if timeElasped > flashTime[flashTimeIndex] - random.uniform(.5, 2): #amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
            flashTimeIndex += 1
            lightning(ledStrip)
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            break
        
def change_color(ledStrip):
    ledStrip.brightness = 1.0
    color_r = random.randint(0, 255)
    color_g = random.randint(0, 255)
    color_b = random.randint(0, 255)     
    ledStrip.fill((color_r, color_g, color_b))
    ledStrip.show()
    
async def fire(ledStrip):
    while True:
        ledStrip.brightness = 1.0
        r = 226
        g = 121
        b = 35

        #Flicker, based on our initial RGB values
        for i in range (0, len(ledStrip)):
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            ledStrip[i] = (r1,g1,b1)
        ledStrip.show()
        await asyncio.sleep(random.randint(100,1000) / 3000)


def rainbow(ledStrip, speed, sleepAndUpdateVolume):
    num_pixels = len(ledStrip)
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
    for j in reversed(range(255)):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
        
async def play_music(file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch):
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while True:
        if not mixer.voice[0].playing:
            break
        sleepAndUpdateVolume(.1)
        await asyncio.sleep(1)
        
def fire_now(ledStrip, num_times, sleepAndUpdateVolume):
    ledStrip.brightness = 1.0
    r = 226
    g = 121
    b = 35

    #Flicker, based on our initial RGB values
    for _ in range(num_times):
        for i in range (1, 31):
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            ledStrip[i] = (r1,g1,b1)
        ledStrip.show()
        sleepAndUpdateVolume(random.uniform(0.05,0.1))
        
async def main(ledStrip, file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch):
    fire_task = asyncio.create_task(fire(ledStrip))
    play_music_task = asyncio.create_task(play_music(file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch))
    await asyncio.gather(fire_task)
    print("done")
        
def animation_lightshow_async(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    asyncio.run(main(ledStrip, file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch))
    
def animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    my_index = 0
    
    while True:
        timeElasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            print(timeElasped)
        if timeElasped > flashTime[flashTimeIndex] - 0.25:
            flashTimeIndex += 1
            my_index += 1 #random.randint(1, 3)
            if my_index == 1:
                change_color(ledStrip)
                sleepAndUpdateVolume(.3)
                rainbow(ledStrip, .001, sleepAndUpdateVolume)
            elif my_index == 2:
                change_color(ledStrip)
                sleepAndUpdateVolume(.3)
                fire_now(ledStrip, 18, sleepAndUpdateVolume)    
            if (my_index > 1): my_index = 0
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            break
        sleepAndUpdateVolume(.1)
         
def animation_timestamp(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    print("time stamp mode")

    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    
    my_time_stamps = {"flashTime":[0]}

    while True:
        time_elasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            my_time_stamps["flashTime"].append(time_elasped) 
            print(time_elasped)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            print(my_time_stamps)
            break
        sleepAndUpdateVolume(.05)
        
def breakfast_at_diner(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    print("time stamp mode")
    
    customer = [
        "I_am_so_hungry",
        "i_know_but_i_am_starving",
        "let_me_in_i_will_give_big_tip",
        "thank_you_for_letting_me_in",
        "i_would_like_some_bacon",
        "yes_please_some_black_coffee",
        "i_want_to_pay",
        "thank_for_everything"   
        ]
    
    employee = [
        "we_are_closed",
        "the_cook_not_here",
        "Ok_for_you",
        "can_i_take_order",
        "do_you_want_drink",
        "want_anything_else",
        "six_hundred_dollars",  
        ]
    
    ledStrip.fill((0, 0, 0))
    ledStrip.show()
    
    ledStrip[0] = (50,50,50)
    ledStrip.show()
    
    while True:
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[0] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        ledStrip[7] = (255,255,255)
        ledStrip.show()
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[0] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[1] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[1] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[2] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[2] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        ledStrip[6] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[8] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[5] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[9] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[4] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[10] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[3] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[11] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[3] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_1.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[3] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[4] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[4] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[5] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_2.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        walking_light = 50
        walking_time = .5
        ledStrip[9] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[8] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[7] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[6] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[5] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[4] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[3] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/bacon_cooking.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:  
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_1.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        walking_light = 255
        walking_time = .5
        ledStrip[3] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[4] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[5] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[6] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[7] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[8] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[9] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[5] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[6] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[6] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/cash_register.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[7] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            break
        sleepAndUpdateVolume(.05)
        
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            animation(config["option_selected"])
        if right_switch.fell:
            print('Just pressed option mode')
            machine.go_to_state('program')

class ProgramState(State):

    def __init__(self):
        self.optionIndex = 0
        self.currentOption = 0

    @property
    def name(self):
        return 'program'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            play_audio_0("/sd/menu_voice_commands/option_mode_entered_left_right.wav")
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
                wave0 = audiocore.WaveFile(open("/sd/lightning_options_voice_commands/option_" + sound_options[self.optionIndex] + ".wav" , "rb"))
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
                files.write_json_file("/sd/config_lightning.json",config)
                wave0 = audiocore.WaveFile(open("/sd/menu_voice_commands/option_selected.wav", "rb"))
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

###############################################################################
# Create the state machine

pretty_state_machine = StateMachine()
pretty_state_machine.add_state(BaseState())
pretty_state_machine.add_state(ProgramState())
        
audio_enable.value = True

def speak_webpage():
    play_audio_0("/sd/menu_voice_commands/animator_available_on_network.wav")
    play_audio_0("/sd/menu_voice_commands/to_access_type.wav")
    if config["HOST_NAME"]== "animator-lightning-old":
        play_audio_0("/sd/menu_voice_commands/animator_lightning_local.wav")
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
