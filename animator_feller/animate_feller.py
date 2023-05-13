import random

def animation_one(
        sleepAndUpdateVolume, 
        audiocore, 
        mixer, 
        feller_servo, 
        tree_servo, 
        tree_up_pos, 
        tree_down_pos, 
        option_selected, 
        feller_sound_options, 
        feller_rest_pos,
        feller_chop_pos,
        feller_dialog_positive,
        feller_dialog_negative):
    sleepAndUpdateVolume(0.05)
    chopNum = 1
    chopNumber = random.randint(2, 7)
    when_to_speak = random.randint(1, chopNumber)
    print(when_to_speak)
    tree_chop_pos = tree_up_pos - 3
    while chopNum < chopNumber:  
        if when_to_speak == chopNum:
            if chopNum <= 2:
                highest_index = len(feller_dialog_positive) - 1
                soundNumber = random.randint(0, highest_index)
                soundFile = "/sd/feller_dialog/" + feller_dialog_positive[soundNumber] + ".wav"
                wave0 = audiocore.WaveFile(open(soundFile, "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    feller_servo.angle = 5 + feller_rest_pos
                    sleepAndUpdateVolume(0.1)
                    feller_servo.angle = feller_rest_pos
                    sleepAndUpdateVolume(0.1)
            if chopNum > 2:
                highest_index = len(feller_dialog_negative) - 1
                soundNumber = random.randint(0, highest_index)
                soundFile = "/sd/feller_dialog/" + feller_dialog_negative[soundNumber] + ".wav"
                wave0 = audiocore.WaveFile(open(soundFile, "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    feller_servo.angle = 5 + feller_rest_pos
                    sleepAndUpdateVolume(0.1)
                    feller_servo.angle = feller_rest_pos
                    sleepAndUpdateVolume(0.1)
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        chopActive = True
        for feller_angle in range(feller_rest_pos, feller_chop_pos + 5, 10):  # 0 - 180 degrees, 10 degrees at a time.
            feller_servo.angle = feller_angle                                 
            if feller_angle >= (feller_chop_pos - 10) and chopActive:
                mixer.voice[0].play( wave0, loop=False )
                chopActive = False
            if feller_angle >= feller_chop_pos:
                chopActive = True
                shake = 2
                for _ in range(shake):
                    tree_servo.angle = tree_chop_pos
                    sleepAndUpdateVolume(0.1)
                    tree_servo.angle = tree_up_pos
                    sleepAndUpdateVolume(0.1)
            sleepAndUpdateVolume(0.02)
        if chopNum < chopNumber: 
            for feller_angle in range(feller_chop_pos, feller_rest_pos, -5): # 180 - 0 degrees, 5 degrees at a time.
                feller_servo.angle = feller_angle
                sleepAndUpdateVolume(0.02)
        pass
    if option_selected == "random":
        feller_sound_options_highest_index = len(feller_sound_options) - 2 #subtract -2 to avoid choosing "random" for a file
        soundNumber = random.randint(0, feller_sound_options_highest_index)
        soundFile = "/sd/feller_sounds/sounds_" + feller_sound_options[soundNumber] + ".wav"
    else:
        soundFile = "/sd/feller_sounds/sounds_" + option_selected + ".wav"
    wave0 = audiocore.WaveFile(open(soundFile, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    for tree_angle in range(tree_up_pos, 50 + tree_down_pos, -5): # 180 - 0 degrees, 5 degrees at a time.
        tree_servo.angle = tree_angle
        sleepAndUpdateVolume(0.06)
    shake = 8
    for _ in range(shake):
        tree_servo.angle = tree_down_pos
        sleepAndUpdateVolume(0.1)
        tree_servo.angle = 7 + tree_down_pos
        sleepAndUpdateVolume(0.1)
    tree_servo.angle = tree_down_pos
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.02)
    for feller_angle in range(feller_chop_pos, feller_rest_pos, -5): # 180 - 0 degrees, 5 degrees at a time.
        feller_servo.angle = feller_angle
        sleepAndUpdateVolume(0.02)
    for tree_angle in range( tree_down_pos + 7, tree_up_pos, 1): # 180 - 0 degrees, 1 degrees at a time.
        tree_servo.angle = tree_angle
        sleepAndUpdateVolume(0.01)
    tree_servo.angle = tree_up_pos
    sleepAndUpdateVolume(0.02)
    tree_servo.angle = tree_up_pos
    