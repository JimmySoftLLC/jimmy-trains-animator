# MIT License
#
# Copyright (c) 2024 JimmySoftLLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import files
import utilities
import time
import board
import microcontroller
import pwmio
import digitalio
import random
import gc

from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_debouncer import Debouncer


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item(
        "Point " + collection_point +
        " Available memory: {} bytes".format(start_mem)
    )


def reset_pico():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


################################################################################
# get the calibration settings from the picos flash memory
cfg = files.read_json_file("/cfg.json")

main_m = cfg["main_menu"]

rand_timer = 0
srt_t = time.monotonic()    

################################################################################
# Setup hardware


# Setup the servo this animation can have up to two servos
# also get the programmed values for position which is stored on the pico itself
servo_1 = pwmio.PWMOut(board.GP2, duty_cycle=2 ** 15,
                       frequency=50)  # first prototype used GP10
servo_2 = pwmio.PWMOut(board.GP6, duty_cycle=2 ** 15, frequency=50)

servo_1 = servo.Servo(servo_1, min_pulse=500, max_pulse=2500)
servo_2 = servo.Servo(servo_2, min_pulse=500, max_pulse=2500)

prev_pos_arr = [cfg["forward"], cfg["hidden"]]

servo_arr = [servo_1, servo_2]

# Setup the switches
top_sw = board.GP20
bot_sw = board.GP11

top_sw = digitalio.DigitalInOut(top_sw)
top_sw.direction = digitalio.Direction.INPUT
top_sw.pull = digitalio.Pull.UP
top_sw = Debouncer(top_sw)

bot_sw = digitalio.DigitalInOut(bot_sw)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP
bot_sw = Debouncer(bot_sw)



################################################################################
# Servo methods


def move_at_speed(n, new_position, speed):
    global prev_pos_arr
    sign = 1
    if prev_pos_arr[n] > new_position:
        sign = - 1
    for servo_pos in range(prev_pos_arr[n], new_position, sign):
        m_servo(n, servo_pos)
        time.sleep(speed)
    m_servo(n, new_position)


def m_servo(n, p):
    global prev_pos_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    servo_arr[n].angle = p
    prev_pos_arr[n] = p


################################################################################
# animations
def swagger_movement(n, center_pt, cyc, spd, wiggle_amount):
    for _ in range(cyc):
        move_at_speed(n, center_pt-wiggle_amount, spd)
        move_at_speed(n, center_pt+wiggle_amount, spd)


def an():
    move_at_speed(1, cfg["visible"], cfg["walking_speed"])
    swagger_movement(0, cfg["forward"]-cfg["swagger"], 2, cfg["swagger_speed"], cfg["swagger"])
    move_at_speed(0, cfg["backward"], cfg["turning_speed"])
    move_at_speed(1, cfg["hidden"], cfg["walking_speed"])
    move_at_speed(0, cfg["forward"], cfg["turning_speed"])


def show_mode(cycles, stay_at_middle = False):
    middle_point = int((cfg["visible"]+cfg["hidden"])/2)
    show_mode_point = int((middle_point+cfg["visible"])/2)
    show_mode_spd = 0.04
    move_at_speed(1, middle_point, show_mode_spd)
    time.sleep(1)
    for _ in range(cycles):
        move_at_speed(1, show_mode_point, show_mode_spd)
        move_at_speed(1, middle_point, show_mode_spd)
    if not stay_at_middle:
        time.sleep(1)
        move_at_speed(1, cfg["hidden"], cfg["walking_speed"])


def show_timer_mode():
    if cfg["timer"] == True:
        show_mode(2)
    else:
        show_mode(1)


def show_timer_program_option(cycles):
    middle_point = int((cfg["visible"]+cfg["hidden"])/2)
    middle_point = int((middle_point+cfg["hidden"])/2)
    move_at_speed(1, cfg["hidden"], cfg["walking_speed"])
    for _ in range(cycles):
        move_at_speed(1, middle_point, cfg["walking_speed"])
        move_at_speed(1, cfg["hidden"], cfg["walking_speed"])

################################################################################
# State Machine


class StMch(object):

    def __init__(s):
        s.ste = None
        s.stes = {}
        s.paused_state = None

    def add(s, ste):
        s.stes[ste.name] = ste

    def go_to(s, ste):
        if s.ste:
            s.ste.exit(s)
        s.ste = s.stes[ste]
        s.ste.enter(s)

    def upd(s):
        if s.ste:
            s.ste.upd(s)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(s):
        pass

    @property
    def name(s):
        return ""

    def enter(s, mch):
        pass

    def exit(s, mch):
        pass

    def upd(s, mch):
        pass


class BseSt(Ste):
    def __init__(self):
        pass

    @property
    def name(self):
        return "base_state"

    def enter(self, mch):
        show_timer_mode()
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 3.0)
        if sw == "left_held":
            rand_timer = 0
            if cfg["timer"] == True:
                cfg["timer"] = False
                files.write_json_file("cfg.json", cfg)
            elif cfg["timer"] == False:
                cfg["timer"] = True
                files.write_json_file("cfg.json", cfg)
            show_timer_mode()
        elif cfg["timer"] == True:
            if rand_timer <= time.monotonic()-srt_t:
                an()
                timer_val_split = cfg["timer_val"].split("_")
                if timer_val_split[0] == "random":
                    rand_timer = random.uniform(
                        float(timer_val_split[1]), float(timer_val_split[2]))
                    next_time = "{:.1f}".format(rand_timer)
                    print("Next time : " + next_time)
                if timer_val_split[0] == "timer":
                    rand_timer = float(timer_val_split[1])
                    next_time = "{:.1f}".format(rand_timer)
                    print("Next time : " + next_time)
                srt_t = time.monotonic()
        elif sw == "left":
            an()
            print("an done")
        elif sw == "right":
            mch.go_to("main_menu")


class Main(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "main_menu"

    def enter(self, mch):
        files.log_item("Main menu")
        show_mode(3)
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        top_sw.update()
        bot_sw.update()
        if top_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m) - 1:
                self.i = 0
            print(main_m[self.sel_i])
            show_timer_program_option(self.sel_i+1)
        if bot_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "exit_this_menu":
                print(sel_i)
                cfg["timer"] = False
                rand_timer = 0
                files.write_json_file("cfg.json", cfg)
                mch.go_to("base_state")
            else:
                print(sel_i)
                cfg["timer"] = True
                cfg["timer_val"] = sel_i
                rand_timer = 0
                files.write_json_file("cfg.json", cfg)
                mch.go_to("base_state")


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())

sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 6.0)
if sw == "left_held":  # top switch counter clockwise
    cfg["hidden"] = 120
    files.write_json_file("cfg.json", cfg)
    show_mode(4)
elif sw == "right_held":  # top switch clockwise
    cfg["visible"] = 60
    files.write_json_file("cfg.json", cfg)
    show_mode(4)

#initialize figures in correct position
move_at_speed(0, cfg["forward"], cfg["turning_speed"])
move_at_speed(1, cfg["hidden"], cfg["walking_speed"])
time.sleep(5)

st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")

while True:
    st_mch.upd()
    time.sleep(0.01)
