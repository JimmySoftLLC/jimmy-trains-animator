

import files
import time
import board
import microcontroller
import busio
import pwmio
import digitalio
import random
import utilities

from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_debouncer import Debouncer

def reset_pico():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()

################################################################################
# Setup hardware

# Setup the servo this animation can have up to two servos
# also get the programmed values for position which is stored on the pico itself
servo_1 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
servo_2 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

servo_1 = servo.Servo(servo_1)
servo_2 = servo.Servo(servo_2)

# Initialize all servos to 90 degree position upon startup
servo_1.angle = 90
servo_2.angle = 90

# Setup the switches, not all units have these
sw_1 = board.GP6 # revaluate this when the AN1S is in final design
sw_2 = board.GP7 # revaluate this when the AN1S is in final design

sw_1 = digitalio.DigitalInOut(sw_1)
sw_1.direction = digitalio.Direction.INPUT
sw_1.pull = digitalio.Pull.UP
sw_1 = Debouncer(sw_1)

sw_2 = digitalio.DigitalInOut(sw_2)
sw_2.direction = digitalio.Direction.INPUT
sw_2.pull = digitalio.Pull.UP
sw_2 = Debouncer(sw_2)

################################################################################
# get the calibration settings from the picos flash memory
config = files.read_json_file("/cfg.json")

################################################################################
# Shared methods

# Note this is the passed in method for the utilities module if used
def time_sleep(dur):
    time.sleep(dur)

################################################################################
# Servo methods

def move_s1_at_speed (new_position, speed):
    global s1_last_pos
    sign = 1
    if s1_last_pos > new_position: sign = - 1
    for s_1 in range( s1_last_pos, new_position, sign):
        move_s_1 (s_1)
        time.sleep(speed)
    move_s_1 (new_position)
    
def move_s_1 (servo_pos):
    if servo_pos < 0: servo_pos = 0
    if servo_pos > 180: servo_pos = 180
    servo_1.angle = servo_pos
    global s1_last_pos
    s1_last_pos = servo_pos

################################################################################
# animations

def s_1_wiggle_movement(dur):
    rotation = 7
    cycle_time = 0.2
    st = time.monotonic
    while time.monotonic - st < dur:
        switch_state = utilities.switch_state(sw_1, sw_2, time_sleep, 0.5)
        if switch_state == "left_held":
            return
        servo_1.angle = rotation + config["wiggle_pos"]
        time_sleep(cycle_time)
        servo_1.angle = config["wiggle_pos"]
        time_sleep(cycle_time)

def animate():
    print("dude")

while True:
    time_sleep(.1)
