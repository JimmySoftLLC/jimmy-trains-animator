import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import pwmio
import digitalio
import board
import neopixel
import random
import rtc

r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

#setup neo pixels
num_pixels = 30
ledStrip = neopixel.NeoPixel(board.GP10, num_pixels)
ledStrip.auto_write = False
ledStrip.brightness = 1.0

#setup sdCard
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

#setup audio
i2s_bclk = board.GP18   # BCK on PCM5102 I2S DAC (SCK pin to Gnd)
i2s_wsel = board.GP19  # LCLK on PCM5102
i2s_data = board.GP20  # DIN on PCM5102
num_voices = 3

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)

mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback

files.log_item("audio is now playing")

# set some initial levels
mixer.voice[0].level = 1.0
mixer.voice[1].level = 1.0
mixer.voice[2].level = 1.0

wave0 = audiocore.WaveFile(open("/sd/wav/thunderstorm.wav", "rb"))
startTime = time.monotonic()
mixer.voice[0].play( wave0, loop=True )

flashTime = [
2.26105,
23.251,
36.452,
42.3651,
64.137,
68.098,
70.5891,
81.928,
94.652,
102.151,
114.858,
149.075,
155.0,
176.599,
180.552,
182.82,
194.274,
207.053,
214.628,
227.533,
261.722,
267.595,
289.273,
293.577,
295.761,
306.983,
319.856,
327.354,
340.374,
374.584 ]

flashTimeLen = len(flashTime)
flashTimeIndex = 0

flashCount= 10

def lightning():
    r = random.randint(40, 80)
    g = random.randint(10, 25)
    b = random.randint(0, 10)

    # number of flashes
    flashCount = random.randint (5, 10)

    # flash white brightness range - 0-255
    flashBrightnessMin =  10
    flashBrightnessMax =  255
    flashBrightness = random.randint(flashBrightnessMin, flashBrightnessMax) / 255
    ledStrip.brightness = flashBrightness
    
    #files.log_item (str(time.monotonic()-startTime))

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
           
play = False

btn = digitalio.DigitalInOut(board.GP14)
btn.direction = digitalio.Direction.INPUT
 
while True:
    if time.monotonic()-startTime > flashTime[flashTimeIndex] - random.randint(0, 2):
        flashTimeIndex += 1
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        lightning()
    time.sleep(.2)
    
    #if btn.value == True: play = True
    #if play == True:
        #play = False
        #lightning()
        # delay = random.randint(2, 10)
        # time.sleep(delay)
        