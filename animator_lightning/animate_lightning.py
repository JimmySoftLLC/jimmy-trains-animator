import random
import time

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

def animation_one(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch):
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
    
    wave0 = audiocore.WaveFile(open("/sd/wav/thunderstorm.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()

    while True:
        sleepAndUpdateVolume(.1)
        timeElasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            print(timeElasped)
        if timeElasped > flashTime[flashTimeIndex] - random.randint(0, 2):
            flashTimeIndex += 1
            lightning(ledStrip)
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            break
