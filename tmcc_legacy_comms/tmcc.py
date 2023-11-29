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
from analogio import AnalogIn
from adafruit_debouncer import Debouncer

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

from analogio import AnalogIn

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

def processCommand(response):
    if response["module"] == "accessory":
        if response["command"] == "extended" and response["data"] =="01011":
            play_audio_0("/sd/mvc/accessory.wav")
            play_audio_0("/sd/mvc/set_to_id.wav")
            speak_this_string(str(response["address"]),False)
        elif response["command"] == "relative" and response["data"] =="00110":
            play_audio_0("/sd/mvc/accessory.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_up.wav")
        elif response["command"] == "relative" and response["data"] =="00100":
            play_audio_0("/sd/mvc/accessory.wav")
            speak_this_string(str(response["address"]),False) 
            play_audio_0("/sd/mvc/trottle_down.wav")
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

# the following is to help decode the lionel tmcc commands
while True:
    if uart.in_waiting >= 3:  # Check if at least 3 bytes are available to read
        received_data = uart.read(3)
        if len(received_data) == 3:
            word1, word2, word3 = received_data[0], received_data[1], received_data[2]
            
            # Convert words to binary strings
            binary_word1 = f'{word1:0>8b}'
            binary_word2 = f'{word2:0>8b}'
            binary_word3 = f'{word3:0>8b}'
            
            print("Received command: " + str(received_data))
            #print("Received 0: " + str(received_data[0]))
            #print("Received 1: " + str(received_data[1]))
            #print("Received 2: " + str(received_data[2]))
            #print(f"Word 1: {binary_word1}")
            #print(f"Word 2: {binary_word2}")
            #print(f"Word 3: {binary_word3}\n")
            response = getCommandObject(binary_word2,binary_word3)
            processCommand(response)
            print(response["module"],response["address"],response["command"],response["data"])
            uart.read(uart.in_waiting)
            
            # Reconstruct the command bytes
            reconstructed_word1 = int(binary_word1, 2).to_bytes(1, 'big')
            reconstructed_word2 = int(binary_word2, 2).to_bytes(1, 'big')
            reconstructed_word3 = int(binary_word3, 2).to_bytes(1, 'big')
            
            # Construct the command to send back
            reconstructed_command = reconstructed_word1 + reconstructed_word2 + reconstructed_word3
            print("Reconstructed command: " + str(reconstructed_command))
            # Echo back the received command
            # uart.write(reconstructed_command)  # Echo back the received command
        else:
            # Invalid command format, discard the data
            uart.read(uart.in_waiting)
