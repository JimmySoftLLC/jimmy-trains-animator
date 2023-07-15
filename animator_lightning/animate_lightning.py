import random
import time
import files
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.sequence import AnimationSequence
from rainbowio import colorwheel
import digitalio
import board
import asyncio
import audiocore
import audiomixer
from adafruit_motor import servo
import pwmio

# Setup the servo, this animation has two the feller and tree
# also get the programmed values for position which is stored on the sdCard
donald_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
pluto_pwm = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)
mickey_pwm = pwmio.PWMOut(board.GP13, duty_cycle=2 ** 15, frequency=50)
minie_pwm = pwmio.PWMOut(board.GP14, duty_cycle=2 ** 15, frequency=50)
goofy_pwm = pwmio.PWMOut(board.GP15, duty_cycle=2 ** 15, frequency=50)


donald_servo = servo.Servo(donald_pwm)
pluto_servo = servo.Servo(pluto_pwm)
mickey_servo = servo.Servo(mickey_pwm)
minie_servo = servo.Servo(minie_pwm)
goofy_servo = servo.Servo(goofy_pwm)

donald__last_pos = 90
pluto__last_pos = 90
mickey_last_pos = 90
minie__last_pos = 90
goofy__last_pos = 90

donald_servo.angle = donald__last_pos
pluto_servo.angle = pluto__last_pos
mickey_servo.angle = mickey_last_pos
minie_servo.angle = minie__last_pos
goofy_servo.angle = goofy__last_pos

flashTimeIndex = 0

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
        
def animation(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name, num_pixels):
    print(file_name)
    chips_birthday(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    return
    if file_name == "alien_lightshow":
        animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "inspiring_cinematic_ambient_lightshow":
        animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
        #animation_lightshow_async(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "timestamp_mode":
        animation_timestamp(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "breakfast_at_diner":
        breakfast_at_diner(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    elif file_name == "continuous_thunder":
        continuous_thunder(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
    else:
        thunder_once_played(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name)
        
def continuous_thunder(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    
    while True:
        wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        startTime = time.monotonic()
        pressed_stop_button = False
        flashTimeIndex = 0
        while True:
            sleepAndUpdateVolume(.1)
            timeElasped = time.monotonic()-startTime
            right_switch.update()
            if right_switch.fell:
                print(timeElasped)
            if timeElasped > flashTime[flashTimeIndex] - random.uniform(.5, 2): #amount of time before you here thunder 0.5 is synched with the lightning
                flashTimeIndex += 1
                lightning(ledStrip)
            if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
            left_switch.update()
            if left_switch.fell:
                mixer.voice[0].stop()
                pressed_stop_button = True
            if not mixer.voice[0].playing:
                break
        if pressed_stop_button:
            break

def thunder_once_played(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()

    while True:
        sleepAndUpdateVolume(.1)
        timeElasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            print(timeElasped)
        if timeElasped > flashTime[flashTimeIndex] - random.uniform(.5, 2): #amount of time before you here thunder 0.5 is synched with the lightning 2 is 1.5 seconds later
            flashTimeIndex += 1
            lightning(ledStrip)
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            break
        
def change_color(ledStrip):
    ledStrip.brightness = 1.0
    color_r = random.randint(0, 255)
    color_g = random.randint(0, 255)
    color_b = random.randint(0, 255)     
    ledStrip.fill((color_r, color_g, color_b))
    ledStrip.show()
    
async def fire(ledStrip):
    while True:
        ledStrip.brightness = 1.0
        r = 226
        g = 121
        b = 35

        #Flicker, based on our initial RGB values
        for i in range (0, len(ledStrip)):
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            ledStrip[i] = (r1,g1,b1)
        ledStrip.show()
        await asyncio.sleep(random.randint(100,1000) / 3000)


def rainbow(ledStrip, speed, num_pixels, sleepAndUpdateVolume):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
    for j in reversed(range(255)):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            ledStrip[i] = colorwheel(pixel_index & 255)
        ledStrip.show()
        sleepAndUpdateVolume(speed)
        
async def play_music(file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch):
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while True:
        if not mixer.voice[0].playing:
            break
        sleepAndUpdateVolume(.1)
        await asyncio.sleep(1)
        
def fire_now(ledStrip, num_times, sleepAndUpdateVolume):
    ledStrip.brightness = 1.0
    r = 226
    g = 121
    b = 35

    #Flicker, based on our initial RGB values
    for _ in range(num_times):
        for i in range (1, 20):
            flicker = random.randint(0,110)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            ledStrip[i] = (r1,g1,b1)
        ledStrip.show()
        sleepAndUpdateVolume(random.uniform(0.05,0.3))
        
async def main(ledStrip, file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch):
    fire_task = asyncio.create_task(fire(ledStrip))
    play_music_task = asyncio.create_task(play_music(file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch))
    await asyncio.gather(fire_task)
    print("done")
        
def animation_lightshow_async(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    asyncio.run(main(ledStrip, file_name, audiocore, mixer, sleepAndUpdateVolume, left_switch))
    
def animation_lightshow(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/" + file_name + ".json")
    flashTime = flash_time_dictionary["flashTime"]

    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    my_index = 0
    
    while True:
        timeElasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            print(timeElasped)
        if timeElasped > flashTime[flashTimeIndex] - 0.25:
            flashTimeIndex += 1
            my_index += 1 #random.randint(1, 3)
            if my_index == 1:
                change_color(ledStrip)
                sleepAndUpdateVolume(.3)
                rainbow(ledStrip, .006, 8, sleepAndUpdateVolume)
            elif my_index == 2:
                change_color(ledStrip)
                sleepAndUpdateVolume(.3)
                fire_now(ledStrip, 8, sleepAndUpdateVolume)    
            if (my_index > 1): my_index = 0
        if flashTimeLen == flashTimeIndex: flashTimeIndex = 0
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            break
        sleepAndUpdateVolume(.1)
         
def animation_timestamp(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    print("time stamp mode")

    print_timestamp = False
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/" + file_name + ".wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    
    my_time_stamps = {"flashTime":[0]}

    while True:
        time_elasped = time.monotonic()-startTime
        right_switch.update()
        if right_switch.fell:
            my_time_stamps["flashTime"].append(time_elasped) 
            print(time_elasped)
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            print(my_time_stamps)
            break
        sleepAndUpdateVolume(.05)
        
def breakfast_at_diner(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    print("time stamp mode")

    print_timestamp = False
    
    customer = [
        "I_am_so_hungry",
        "i_know_but_i_am_starving",
        "let_me_in_i_will_give_big_tip",
        "thank_you_for_letting_me_in",
        "i_would_like_some_bacon",
        "yes_please_some_black_coffee",
        "i_want_to_pay",
        "thank_for_everything"   
        ]
    
    employee = [
        "we_are_closed",
        "the_cook_not_here",
        "Ok_for_you",
        "can_i_take_order",
        "do_you_want_drink",
        "want_anything_else",
        "six_hundred_dollars",  
        ]
    
    ledStrip.fill((0, 0, 0))
    ledStrip.show()
    
    ledStrip[0] = (50,50,50)
    ledStrip.show()
    
    while True:
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[0] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        ledStrip[7] = (255,255,255)
        ledStrip.show()
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[0] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[1] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[1] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[2] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[2] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        ledStrip[6] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[8] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[5] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[9] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[4] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[10] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[3] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        ledStrip[11] = (255,255,255)
        ledStrip.show()
        sleepAndUpdateVolume(.2)
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[3] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_1.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[3] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[4] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[4] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[5] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_2.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        walking_light = 50
        walking_time = .5
        ledStrip[9] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[8] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[7] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[6] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[5] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[4] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[3] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/bacon_cooking.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:  
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/footsteps_1.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        walking_light = 255
        walking_time = .5
        ledStrip[3] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[4] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[5] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[6] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[7] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[8] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        ledStrip[9] = (walking_light,walking_light,walking_light)
        ledStrip.show()
        sleepAndUpdateVolume(walking_time)
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[5] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[6] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + employee[6] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/cash_register.wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        wave0 = audiocore.WaveFile(open("/sd/diner/" + customer[7] + ".wav", "rb"))
        mixer.voice[0].play( wave0, loop=False )
        while mixer.voice[0].playing:
            pass
        left_switch.update()
        if left_switch.fell:
            mixer.voice[0].stop()
        if not mixer.voice[0].playing:
            ledStrip.fill((0, 0, 0))
            ledStrip.show()
            break
        sleepAndUpdateVolume(.05)
               
def moveToPositionGently (new_position, speed, sleepAndUpdateVolume, ledStrip, startTime, flashTime):
    global donald__last_pos
    global pluto__last_pos
    global mickey_last_pos
    global minie__last_pos
    global goofy__last_pos
    global flashTimeIndex
    sign = 1
    if donald__last_pos > new_position: sign = - 1
    for feller_angle in range( donald__last_pos, new_position, sign):
        timeElasped = time.monotonic()-startTime
        if timeElasped > flashTime[flashTimeIndex] - 0.25:
            print (flashTime[flashTimeIndex])
            if 11.5117 == flashTime[flashTimeIndex]:
                rainbow(ledStrip, .001, 40, sleepAndUpdateVolume)
            elif 60.8691 == flashTime[flashTimeIndex]:
                fire_now(ledStrip, 10, sleepAndUpdateVolume)    
            else:
                change_color(ledStrip)
            flashTimeIndex+=1
        donald_servo.angle = feller_angle  
        sleepAndUpdateVolume(.001)
        pluto_servo.angle = feller_angle
        sleepAndUpdateVolume(.001)
        mickey_servo.angle = feller_angle
        sleepAndUpdateVolume(.001)
        minie_servo.angle = feller_angle
        sleepAndUpdateVolume(.001)
        goofy_servo.angle = feller_angle
        sleepAndUpdateVolume(speed)
    donald__last_pos = new_position

      
def chips_birthday(sleepAndUpdateVolume, audiocore, mixer, ledStrip, left_switch, right_switch, file_name):
    global flashTimeIndex
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/mickey_birthday_song.json")
    flashTime = flash_time_dictionary["flashTime"]
    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/mickey_birthday_song.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    while mixer.voice[0].playing:
        moveToPositionGently (30,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        moveToPositionGently (150,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        pass
    
    flash_time_dictionary = files.read_json_file("/sd/lightning_sounds/you_got_a_friend_in_me.json")
    flashTime = flash_time_dictionary["flashTime"]
    flashTimeLen = len(flashTime)
    flashTimeIndex = 0
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/you_got_a_friend_in_me.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    while mixer.voice[0].playing:
        moveToPositionGently (30,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        moveToPositionGently (150,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        pass
    
    return

    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/happy_birthday_in_the_park.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    while mixer.voice[0].playing:
        moveToPositionGently (30,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        moveToPositionGently (150,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        pass
    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/beauty_and_the_beast.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    while mixer.voice[0].playing:
        moveToPositionGently (30,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        moveToPositionGently (150,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        pass
    

    
    wave0 = audiocore.WaveFile(open("/sd/lightning_sounds/when_you_wish_upon_a_star.wav", "rb"))
    mixer.voice[0].play( wave0, loop=False )
    startTime = time.monotonic()
    while mixer.voice[0].playing:
        moveToPositionGently (30,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        moveToPositionGently (150,.02,sleepAndUpdateVolume, ledStrip, startTime, flashTime)
        pass
    
    
    #play_audio_0("/sd/music/beegie_when_you_wish.wav")
           
def bounds(my_color, lower, upper):
    if (my_color < lower): my_color = lower
    if (my_color > upper): my_color = upper
    return my_color
 
