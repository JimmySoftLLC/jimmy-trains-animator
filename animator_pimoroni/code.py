# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# This example demonstrates how to light keys when pressed.

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

import sdcardio
import storage
import board
import busio

import audiomp3
import audiocore
import audiomixer
import audiobusio
import math
import asyncio
import files
import time

from pmk import PMK, number_to_xy, hsv_to_rgb
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

file_path="/sd/lightning_sounds/inspiring_cinematic_ambient_lightshow.wav"

# Set up Keybow keyboard
keybow = PMK(Hardware())
keys = keybow.keys
keyBrightness = 0.25

# setup audio on the i2s bus, the animator uses the MAX98357A
# the animator can have one or two MAX98357As. one for mono two for stereo
# both MAX98357As share the same bus
# for mono the MAX98357A defaults to combine channels
# for stereo the MAX98357A SD pin is connected to VCC for right and a resistor to VCC for left
# the audio mixer is used so that volume can be control digitally it is set to stereo
# the sample_rate of the audio mixer is set to 22050 hz.  This is the max the raspberry pi pico can handle
# all files with be in the wave format instead of mp3.  This eliminates the need for decoding
i2s_bclk = board.GP6   # BCLK on MAX98357A
i2s_lrc = board.GP7  # LRC on MAX98357A
i2s_din = board.GP8  # DIN on MAX98357A

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
# the sdCard holds all the media and calibration files
# if the card is missing a voice command is spoken
# the user inserts the card a presses the left button to move forward
sck = board.GP10
si = board.GP11
so = board.GP12
cs = board.GP13
spi = busio.SPI(sck, si, so)
try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
except:
    print("no card")
    wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
    audio.play(wave0)
    while audio.playing:
        pass

# Setup the mixer it can play higher quality audio wav using larger wave files
# wave files are less cpu intensive since they are not compressed
num_voices = 2
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True, buffer_size=16384)
audio.play(mixer)

my_time_stamps = {"flashTime":[0]}

def append_time (r, g, b):
    global my_time_stamps
    time_elasped = time.monotonic()-startTime
    my_time_stamps["flashTime"].append({"timeElasped": time_elasped, "r": r,"g": g,"b": b})
    
key_3_state = False
key_7_state = False

# Attach handler functions to all of the keys
for key in keys:
    # A press handler that sends the keycode and turns on the LED
    @keybow.on_press(key)
    def press_handler(key):
        global my_time_stamps
        global key_3_state
        global key_7_state
        my_time_stamps
        hue = key.number/16
        r, g, b = hsv_to_rgb(hue, 1, 1)
        append_time(r, g, b)
        print(r, g, b)
        key.led_off()
        print(key.number)
        if (key.number == 3):
            key_3_state = True
        if (key.number == 7):
            key_7_state = True
            loop.create_task(pressed_button(7))
        if (key.number == 11):
            loop.create_task(pressed_button(11))
        if key_3_state and key_7_state:
            loop.create_task(stop_now())
        
    # A release handler that turns off the LED
    @keybow.on_release(key)
    def release_handler(key):
        global key_3_state
        global key_7_state
        hue = key.number/16
        r, g, b = hsv_to_rgb(hue, 1, keyBrightness)
        keys[key.number].set_led(r, g, b)
        if (key.number == 3):
            key_3_state = False
        if (key.number == 7):
            key_7_state = False

# Create an event loop
loop = asyncio.get_event_loop()

async def play_music(file_path): 
    global startTime
    wave0 = audiocore.WaveFile(open(file_path, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    mixer.voice[0].level = 0.1
    print("start music")
    
async def pressed_button(buttonNum): 
    while True:
        print("pressed button; " + str(buttonNum))
        await asyncio.sleep(2)
        
async def update_keys():         
    # Always remember to call keybow.update() on every iteration of your loop!
    while True:
        keybow.update()
        await asyncio.sleep(.001)

# turn all button lights on
for i in range(16):
    hue = i/16
    # Convert the hue to RGB values.
    r, g, b = hsv_to_rgb(hue, 1, keyBrightness)
    keys[i].set_led(r, g, b)
    
async def stop_now():
    mixer.voice[0].stop()
    for i in range(16):
        keys[i].led_off()
    files.log_item(my_time_stamps)
    loop.stop()
        
loop.create_task(play_music(file_path))
loop.create_task(update_keys())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except KeyboardInterrupt:
    # Perform any cleanup operations if needed
    for i in range(16):
        keys[i].led_off()   
    print("Exiting program")
    pass
