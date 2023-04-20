import random

def chooseSound(index):
    if index == 1:
        return "/sd/feller_sounds/sounds_birds_dogs.wav"
    elif index == 2:
        return "/sd/feller_sounds/sounds_halloween.wav"
    elif index == 3:
        return "/sd/feller_sounds/sounds_just_birds.wav"
    elif index == 4:
        return "/sd/feller_sounds/sounds_machines.wav"
    elif index == 5:
        return "/sd/feller_sounds/sounds_no_sounds.wav"
    elif index == 6:
        return "/sd/feller_sounds/sounds_owl.wav"
def animation_one(sleepAndUpdateVolume, audiocore, mixer, feller_servo, tree_servo, tree_up_pos, tree_down_pos, tree_chop_pos, option_selected):
    sleepAndUpdateVolume(0.05)
    chopNum = 1
    chopNumber = random.randint(2, 7)
    while chopNum < chopNumber:
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        chopActive = True
        for angle in range(0, tree_up_pos+5, 10):  # 0 - 180 degrees, 10 degrees at a time.
            feller_servo.angle = angle                                 
            if angle >= (tree_up_pos-10) and chopActive:
                mixer.voice[0].play( wave0, loop=False )
                chopActive = False
            if angle >= tree_up_pos:
                chopActive = True
                tree_servo.angle = tree_chop_pos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = tree_up_pos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = tree_chop_pos
                sleepAndUpdateVolume(0.1)
                tree_servo.angle = tree_up_pos
                sleepAndUpdateVolume(0.1)
            sleepAndUpdateVolume(0.02)
        if chopNum < chopNumber: 
            for angle in range(tree_up_pos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                feller_servo.angle = angle
                sleepAndUpdateVolume(0.02)
        pass
    if option_selected == "random":
        soundNumber = random.randint(1, 6)
        soundFile = chooseSound(soundNumber)
    else:
        soundFile = "/sd/feller_sounds/sounds_" + option_selected + ".wav"
    wave0 = audiocore.WaveFile(open(soundFile, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    for angle in range(tree_up_pos, 50 + tree_down_pos, -5): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = angle
        sleepAndUpdateVolume(0.06)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 50 + tree_down_pos
    sleepAndUpdateVolume(0.1)
    tree_servo.angle = 43 + tree_down_pos
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.02)
    for angle in range(tree_up_pos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
        feller_servo.angle = angle
        sleepAndUpdateVolume(0.02)
    for angle in range( 43 + tree_down_pos, tree_up_pos, 1): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = angle
        sleepAndUpdateVolume(0.01)
    tree_servo.angle = tree_up_pos
    sleepAndUpdateVolume(0.02)
    tree_servo.angle = tree_up_pos

