import random
import time
import files

def feller_talking_movement(mixer,config, feller_servo, sleepAndUpdateVolume, left_switch):
    speak_rotation = 7
    speak_cadence = 0.2
    while mixer.voice[0].playing:
        feller_servo.angle = speak_rotation + config["feller_rest_pos"]
        sleepAndUpdateVolume(speak_cadence)
        feller_servo.angle = config["feller_rest_pos"]
        sleepAndUpdateVolume(speak_cadence)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        
def tree_talking_movement(mixer,config, tree_servo, sleepAndUpdateVolume, left_switch):
    speak_rotation = 2
    speak_cadence = 0.2
    while mixer.voice[0].playing:
        tree_servo.angle = speak_rotation + config["tree_up_pos"]
        sleepAndUpdateVolume(speak_cadence)
        tree_servo.angle = config["tree_up_pos"] - speak_rotation
        sleepAndUpdateVolume(speak_cadence)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        
def play_sound(sound_files, audiocore, mixer, sleepAndUpdateVolume, left_switch, folder, garbage_collect):
    highest_index = len(sound_files) - 1
    sound_number = random.randint(0, highest_index)
    files.log_item(folder + ": " + str(sound_number))
    wave0 = audiocore.WaveFile(open("/sd/" + folder + "/" + sound_files[sound_number] + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing :
        sleepAndUpdateVolume(0.1)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
    wave0.deinit()
    garbage_collect("deinit wave0")
    
def animation_one(
        sleepAndUpdateVolume, 
        audiocore, 
        mixer, 
        feller_servo, 
        tree_servo, 
        config,
        feller_sound_options, 
        feller_dialog,
        feller_wife,
        feller_poem,
        feller_buddy,
        feller_girlfriend,
        moveFellerServo,
        moveTreeServo,
        moveFellerToPositionGently,
        moveTreeToPositionGently,
        left_switch,
        garbage_collect):
    sleepAndUpdateVolume(0.05)
    
    if config["opening_dialog"]:
        which_sound = random.randint(0,3)
        if which_sound == 0:
            play_sound(feller_wife, audiocore, mixer, sleepAndUpdateVolume, left_switch, "feller_wife",garbage_collect)
        if which_sound == 1:
            play_sound(feller_buddy, audiocore, mixer, sleepAndUpdateVolume, left_switch, "feller_buddy",garbage_collect)
        if which_sound == 2:
            play_sound(feller_poem, audiocore, mixer, sleepAndUpdateVolume, left_switch, "feller_poem",garbage_collect)
        if which_sound == 3:
            play_sound(feller_girlfriend, audiocore, mixer, sleepAndUpdateVolume, left_switch, "feller_girlfriend",garbage_collect)    
        
    chopNum = 1
    chopNumber = random.randint(2, 7)
    highest_index = len(feller_dialog) - 1
    what_to_speak = random.randint(0, highest_index)
    when_to_speak = random.randint(2, chopNumber)
          
    files.log_item("Chop total: " + str(chopNumber) + " what to speak: " + str(what_to_speak) + " when to speak: " + str(when_to_speak))
    spoken = False
    tree_chop_pos = config["tree_up_pos"] - 3
    if config["option_selected"] == "random":
        highest_index = len(feller_sound_options) - 2 #subtract -2 to avoid choosing "random" for a file
        sound_number = random.randint(0, highest_index)
        soundFile = "/sd/feller_sounds/sounds_" + feller_sound_options[sound_number] + ".wav"
        print("Random sound file: " + feller_sound_options[sound_number])
    else:
        soundFile = "/sd/feller_sounds/sounds_" + config["option_selected"] + ".wav"
        print("Sound file: " + config["option_selected"])
    wave1 = audiocore.WaveFile(open(soundFile, "rb"))
    while chopNum <= chopNumber:
        if when_to_speak == chopNum and not spoken and config["feller_advice"]:
            spoken = True    
            soundFile = "/sd/feller_dialog/" + feller_dialog[what_to_speak] + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            feller_talking_movement(mixer,config, feller_servo, sleepAndUpdateVolume, left_switch)
            wave0.deinit()
            garbage_collect("deinit wave0")
            
        grunt_number = random.randint(1, 4)
        wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
        chopNum += 1
        
        for feller_angle in range(config["feller_rest_pos"], config["feller_chop_pos"] + 5, 10):  # 0 - 180 degrees, 10 degrees at a time.
            moveFellerServo(feller_angle)                                
            if feller_angle >= (config["feller_chop_pos"] - 10):
                mixer.voice[0].play( wave0, loop=False )
                shake = 2
                sleepAndUpdateVolume(0.2)
                for _ in range(shake):
                    moveTreeServo(tree_chop_pos)
                    sleepAndUpdateVolume(0.1)
                    moveTreeServo(config["tree_up_pos"])
                    sleepAndUpdateVolume(0.1)
                break
        if chopNum <= chopNumber: 
            for feller_angle in range(config["feller_chop_pos"], config["feller_rest_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
                moveFellerServo( feller_angle )
                sleepAndUpdateVolume(0.02)
    while mixer.voice[0].playing:
        pass     
    mixer.voice[0].play( wave1, loop=False )
    for tree_angle in range(config["tree_up_pos"], config["tree_down_pos"], -5): # 180 - 0 degrees, 5 degrees at a time.
        moveTreeServo(tree_angle)
        sleepAndUpdateVolume(0.06)
    shake = 8
    for _ in range(shake):
        moveTreeServo(config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
        moveTreeServo(7 + config["tree_down_pos"])
        sleepAndUpdateVolume(0.1)
    if config["option_selected"] == "alien":
        print("Alien sequence starting....")
        sleepAndUpdateVolume(2)
        moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
        moveTreeToPositionGently(config["tree_up_pos"], 0.01)
        left_pos = config["tree_up_pos"] - 4
        right_pos = config["tree_up_pos"] + 4
        while mixer.voice[0].playing :
            moveTreeToPositionGently(left_pos, 0.01)
            moveTreeToPositionGently(right_pos, 0.01)
        moveTreeToPositionGently(config["tree_up_pos"], 0.01)
        for alien_num in range(7):
            soundFile = "/sd/feller_alien/human_" + str(alien_num+1) + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            feller_talking_movement(mixer,config, feller_servo, sleepAndUpdateVolume, left_switch)
            soundFile = "/sd/feller_alien/alien_" + str(alien_num+1) + ".wav"
            wave0 = audiocore.WaveFile(open(soundFile, "rb"))
            mixer.voice[0].play( wave0, loop=False )
            tree_talking_movement(mixer,config, tree_servo, sleepAndUpdateVolume, left_switch)
    else:
        while mixer.voice[0].playing :
            sleepAndUpdateVolume(0.1)
            left_switch.update()
            if left_switch.fell:
                mixer.voice[0].stop()
    wave0.deinit()
    wave1.deinit()
    garbage_collect("deinit wave0 wave1")
    moveFellerToPositionGently(config["feller_rest_pos"], 0.01)
    sleepAndUpdateVolume(0.02)
    moveTreeToPositionGently(config["tree_up_pos"], 0.01)
