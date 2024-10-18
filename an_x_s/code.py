

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

servo_1 = servo.Servo(servo_1, min_pulse=500, max_pulse=2500)
servo_2 = servo.Servo(servo_2, min_pulse=500, max_pulse=2500)

s1_last_pos = 180
s2_last_pos = 180


# Setup the switches, not all units have these
sw_1 = board.GP6  # revaluate this when the AN1S is in final design
sw_2 = board.GP7  # revaluate this when the AN1S is in final design

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
# Servo methods

def random_wait(low, hi):
    # Generate a random delay between low and hi seconds
    delay = random.randint(low, hi)
    print(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)


def move_s1_at_speed(new_position, speed):
    global s1_last_pos
    sign = 1
    if s1_last_pos > new_position:
        sign = - 1
    for s_1 in range(s1_last_pos, new_position, sign):
        move_s_1(s_1)
        time.sleep(speed)
    move_s_1(new_position)


def move_s_1(servo_pos):
    global s1_last_pos
    if servo_pos < 0:
        servo_pos = 0
    if servo_pos > 180:
        servo_pos = 180
    servo_1.angle = servo_pos
    s1_last_pos = servo_pos


################################################################################
# animations
def s_1_wiggle_movement(center_pt, cyc, spd):
    for _ in range(cyc):
        move_s1_at_speed(center_pt-7, spd)
        move_s1_at_speed(center_pt+7, spd)


def animate():
    cyc = random.randint(1, 3)
    s_1_wiggle_movement(90, cyc, .05)
    time.sleep(.1)
    move_s1_at_speed(180, .002)
    random_wait(5, 20)
    move_s1_at_speed(90, .03)


# Initialize all servos to 90 degree position upon startup
move_s1_at_speed(90, .05)

time.sleep(5)

while True:
    animate()
    pass
