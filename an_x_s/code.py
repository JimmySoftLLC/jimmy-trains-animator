

import files
import time
import board
import microcontroller
import busio
import pwmio
import digitalio
import random

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
s_1 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
s_2 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)

p_arr = [180, 180]

s_arr = [s_1, s_2]

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


def move_at_speed(n, new_position, speed):
    global p_arr
    sign = 1
    if p_arr[n] > new_position:
        sign = - 1
    for servo_pos in range(p_arr[n], new_position, sign):
        m_servo(n, servo_pos)
        time.sleep(speed)
    m_servo(n, new_position)


def m_servo(n, p):
    global p_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    s_arr[n].angle = p
    p_arr[n] = p


################################################################################
# animations
def s_1_wiggle_movement(n, center_pt, cyc, spd):
    for _ in range(cyc):
        move_at_speed(n, center_pt-7, spd)
        move_at_speed(n, center_pt+7, spd)


def animate():
    cyc = random.randint(1, 3)
    s_1_wiggle_movement(0, 90, cyc, .05)
    time.sleep(.1)
    move_at_speed(0, 180, .002)
    random_wait(5, 20)
    move_at_speed(0, 90, .03)


# Initialize all servos to 90 degree position upon startup
move_at_speed(0, 90, .05)

time.sleep(5)

while True:
    animate()
    pass

