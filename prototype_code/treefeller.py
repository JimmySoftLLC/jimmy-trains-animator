# audiomixer_demo_i2s.py -- show how to fade up and down playing loops
# Code based on that of https://github.com/todbot/circuitpython-tricks/blob/main/larger-tricks/audiomixer_demo.py
# where you can also find the WAV files used
# 30 Nov 2022 - @todbot / Tod Kurt
# 15 Dec 2022 - @jeremyscook

import time
import board
import audiomp3
import audiomixer
import audiobusio
import time
import pwmio
import digitalio
import random

from adafruit_motor import servo

# create a PWMOut object on Pin .
pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
pwm2 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
upPos = 167
upPosChop = upPos - 3
downPos = 60
my_servo = servo.Servo(pwm)
my_servo.angle=0
my_servo2 = servo.Servo(pwm2)
my_servo2.angle=upPos

audio = audiobusio.I2SOut(board.GP18, board.GP19, board.GP20)
tree = audiomp3.MP3Decoder(open("falling.mp3", "rb"))

btn = digitalio.DigitalInOut(board.GP6)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

play = False

while True:
    time.sleep(0.05)
    if btn.value == False: play = True
    if play == True:
        play = False
        chopNum = 1
        chopNumber = random.randint(2, 7)
        while chopNum < chopNumber:
            chop = audiomp3.MP3Decoder(open("chop" + str(chopNum) + ".mp3", "rb"))
            chopNum += 1
            chopActive = True
            for angle in range(0, upPos+5, 10):  # 0 - 180 degrees, 5 degrees at a time.
                my_servo.angle = angle                                 
                if angle >= (upPos-10) and chopActive:
                    audio.play(chop)
                    chopActive = False
                if angle >= upPos:
                    chopActive = True
                    newAngle = random.randint(upPosChop, upPos)
                    my_servo2.angle = upPosChop
                    time.sleep(0.1)
                    my_servo2.angle = upPos
                    time.sleep(0.1)
                    newAngle = random.randint(upPosChop, upPos)
                    my_servo2.angle = upPosChop
                    time.sleep(0.1)
                    my_servo2.angle = upPos
                    time.sleep(0.1)
                time.sleep(0.02)
            if chopNum < chopNumber: 
                for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                    my_servo.angle = angle
                    time.sleep(0.02)
            pass
        audio.play(tree)
        for angle in range(upPos, 50 + downPos, -5): # 180 - 0 degrees, 5 degrees at a time.
            my_servo2.angle = angle
            time.sleep(0.06)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        time.sleep(0.1)
        my_servo2.angle = 50 + downPos
        time.sleep(0.1)
        my_servo2.angle = 43 + downPos
        while audio.playing:
            time.sleep(0.02)
            pass
        for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
            my_servo.angle = angle
            time.sleep(0.02)
        for angle in range( 43 + downPos, upPos, 1): # 180 - 0 degrees, 5 degrees at a time.
            my_servo2.angle = angle
            time.sleep(0.01)
        my_servo2.angle = upPos
        time.sleep(0.02)
        my_servo2.angle = upPos
    pass
