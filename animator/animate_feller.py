import random

def animation_one(sleepAndUpdateVolume, audiocore, mixer, feller_servo, tree_servo, upPos, downPos, upPosChop):
    sleepAndUpdateVolume(0.05)
    chopNum = 1
    chopNumber = random.randint(2, 7)
    while chopNum < chopNumber:
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        chopActive = True
        for angle in range(0, upPos+5, 10):  # 0 - 180 degrees, 5 degrees at a time.
            feller_servo.angle = angle                                 
            if angle >= (upPos-10) and chopActive:
                mixer.voice[0].play( wave0, loop=False )
                chopActive = False
            if angle >= upPos:
                chopActive = True
                tree_servo.angle = upPosChop
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = upPos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = upPosChop
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = upPos
                sleepAndUpdateVolume(0.1)
            sleepAndUpdateVolume(0.02)
        if chopNum < chopNumber: 
            for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                feller_servo.angle = angle
                sleepAndUpdateVolume(0.02)
        pass
    wave0 = audiocore.WaveFile(open("/sd/feller_sounds/sounds_birds_dogs.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    for angle in range(upPos, 50 + downPos, -5): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = angle
        sleepAndUpdateVolume(0.06)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + downPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + downPos
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.02)
    for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
        feller_servo.angle = angle
        sleepAndUpdateVolume(0.02)
    for angle in range( 43 + downPos, upPos, 1): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = angle
        sleepAndUpdateVolume(0.01)
    tree_servo.angle = upPos
    sleepAndUpdateVolume(0.02)
    tree_servo.angle = upPos
