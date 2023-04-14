import random

def chooseSound(index):
    if index == 1:
        return "/sd/feller_sounds/sounds_birds_dogs.wav"
    elif index == 2:
        return "/sd/feller_sounds/sounds_just_birds.wav"
    elif index == 3:
        return "/sd/feller_sounds/sounds_machines.wav"
    elif index == 4:
        return "/sd/feller_sounds/sounds_no_sounds.wav"
    elif index == 5:
        return "/sd/feller_sounds/sounds_owl.wav"
    elif index == 6:
        return "/sd/feller_sounds/sounds_halloween.wav"

def animation_one(sleepAndUpdateVolume, audiocore, mixer, feller_servo, tree_servo, treeUpPos, treeChopPos, treeDownPos, fellerStartPos, fellerChopPos):
    sleepAndUpdateVolume(0.05)
    chopNum = 1
    chopNumber = random.randint(2, 7)
    while chopNum < chopNumber:
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        chopActive = True
        for fellerAngle in range(0, fellerChopPos+5, 10):  # 0 - 180 degrees, 5 degrees at a time.
            feller_servo.angle = fellerAngle                                 
            if fellerAngle >= (fellerChopPos-10) and chopActive:
                mixer.voice[0].play( wave0, loop=False )
                chopActive = False
            if fellerAngle >= fellerChopPos:
                chopActive = True
                tree_servo.angle = treeChopPos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = treeUpPos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = treeChopPos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = treeUpPos
                sleepAndUpdateVolume(0.1)
            sleepAndUpdateVolume(0.02)
        if chopNum < chopNumber: 
            for treeAngle in range(treeUpPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                feller_servo.angle = treeAngle
                sleepAndUpdateVolume(0.02)
        pass
    soundNumber = random.randint(1, 6)
    soundFile = chooseSound(soundNumber)
    wave0 = audiocore.WaveFile(open(soundFile, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    treeShake = 7
    for fellerAngle in range(treeUpPos, treeShake + treeDownPos, -5): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = fellerAngle
        sleepAndUpdateVolume(0.06)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos + treeShake
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = treeDownPos
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.02)
    for fellerAngle in range(treeUpPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
        feller_servo.angle = fellerAngle
        sleepAndUpdateVolume(0.02)
    for fellerAngle in range( 43 + treeDownPos, treeUpPos, 1): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = fellerAngle
        sleepAndUpdateVolume(0.01)
    tree_servo.angle = treeUpPos
    sleepAndUpdateVolume(0.02)
    tree_servo.angle = treeUpPos

