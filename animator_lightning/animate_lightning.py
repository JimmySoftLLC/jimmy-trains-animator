import random

def lightning(ledStrip):
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

def animation_one(sleepAndUpdateVolume, audiocore, mixer, ledStrip):
    lightning(ledStrip)
