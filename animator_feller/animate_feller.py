import random

def animation_one(
        sleepAndUpdateVolume, 
        audiocore, 
        mixer, 
        feller_servo, 
        tree_servo, 
        config,
        feller_sound_options, 
        feller_dialog_positive,
        feller_dialog_negative,
        feller_dialog_advice,
        moveFellerServo,
        moveTreeServo,
        moveFellerToPositionGently,
        moveTreeToPositionGently,
        left_switch):
    sleepAndUpdateVolume(0.05)
    chopNum = 1
    chopNumber = random.randint(2, 7)
    what_to_speak = random.randint(1, 3)
    when_to_speak = random.randint(2, chopNumber)
    print("chop total: " + str(chopNumber) + " what to speak: " + str(what_to_speak) + " when to speak: " + str(when_to_speak))
    spoken = False
    tree_chop_pos = config["tree_up_pos"] - 3
    speak_rotation = 7
    speak_cadence = 0.2
    while chopNum <= chopNumber:
        if when_to_speak == chopNum and not spoken:
            spoken = True
            highest_index = len(feller_dialog) - 1
            soundNumber = random.randint(0, highest_index)
            soundFile = "/sd/feller_dialog/" + feller_dialog[soundNumber] + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                feller_servo.angle = speak_rotation + config["feller_rest_pos"]
                sleepAndUpdateVolume(speak_cadence)
                feller_servo.angle = config["feller_rest_pos"]
                sleepAndUpdateVolume(speak_cadence)
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        chopActive = True
        for feller_angle in range(config["feller_rest_pos"], config["feller_chop_pos"] + 5, 10):  # 0 - 180 degrees, 10 degrees at a time.
            moveFellerServo(feller_angle)                                
            if feller_angle >= (config["feller_chop_pos"] - 10) and chopActive:
                mixer.voice[0].play( wave0, loop=False )
                chopActive = False
            if feller_angle >= config["feller_chop_pos"]:
                chopActive = True
                shake = 2
                for _ in range(shake):
                    moveTreeServo(tree_chop_pos)
                    sleepAndUpdateVolume(0.1)
                    moveTreeServo(config["tree_up_pos"])
                    sleepAndUpdateVolume(0.1)
            sleepAndUpdateVolume(0.02)
        if chopNum <= chopNumber: 
            for feller_angle in range(config["feller_chop_pos"], config["feller_rest_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
                moveFellerServo( feller_angle )
                sleepAndUpdateVolume(0.02)
        pass
    sleepAndUpdateVolume(0.02)
    if config["option_selected"] == "random":
        feller_sound_options_highest_index = len(feller_sound_options) - 2 #subtract -2 to avoid choosing "random" for a file
        soundNumber = random.randint(0, feller_sound_options_highest_index)
        soundFile = "/sd/feller_sounds/sounds_" + feller_sound_options[soundNumber] + ".wav"
    else:
        soundFile = "/sd/feller_sounds/sounds_" + config["option_selected"] + ".wav"
    wave0 = audiocore.WaveFile(open(soundFile, "rb"))
    mixer.voice[0].play( wave0, loop=False )
    for tree_angle in range(config["tree_up_pos"], config["tree_down_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
        moveTreeServo(tree_angle)
        sleepAndUpdateVolume(0.06)
    shake = 8
    for _ in range(shake):
        moveTreeServo(config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
        moveTreeServo(7 + config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
    moveTreeServo(config["tree_down_pos"])
    #soundFile2 = "/sd/feller_dialog/i_am_exhausted.wav"
    #wave1 = audiocore.WaveFile(open(soundFile2, "rb"))
    #mixer.voice[1].play( wave1, loop=True )
    while mixer.voice[0].playing:
        sleepAndUpdateVolume(0.02)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
    moveFellerToPositionGently(config["feller_rest_pos"])
    sleepAndUpdateVolume(0.02)
    moveTreeToPositionGently(config["tree_up_pos"])
