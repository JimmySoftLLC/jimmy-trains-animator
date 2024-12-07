

import files
import utilities
import time
import board
import microcontroller
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
servo_1 = pwmio.PWMOut(board.GP2, duty_cycle=2 ** 15, frequency=50)  # first prototype used GP10
servo_2 = pwmio.PWMOut(board.GP3, duty_cycle=2 ** 15, frequency=50)

servo_1 = servo.Servo(servo_1, min_pulse=500, max_pulse=2500)
servo_2 = servo.Servo(servo_2, min_pulse=500, max_pulse=2500)

prev_pos_arr = [180, 180]

servo_arr = [servo_1, servo_2]

# Setup the switches
l_sw = board.GP11
r_sw = board.GP20

l_sw = digitalio.DigitalInOut(l_sw)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(r_sw)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

################################################################################
# get the calibration settings from the picos flash memory
cfg = files.read_json_file("/cfg.json")

main_m = cfg["main_menu"]
mnu_o = cfg["options"]

################################################################################
# Servo methods

def random_wait(low, hi):
    # Generate a random delay between low and hi seconds
    delay = random.randint(low, hi)
    print(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)


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
def s_1_wiggle_movement(n, center_pt, cyc, spd):
    for _ in range(cyc):
        move_at_speed(n, center_pt-7, spd)
        move_at_speed(n, center_pt+7, spd)


def an():
    move_at_speed(0, cfg["wiggle_pos"], cfg["gentle_speed"])
    cyc = random.randint(cfg["wiggle_cycles_low"], cfg["wiggle_cycles_high"])
    s_1_wiggle_movement(0, cfg["wiggle_pos"], cyc, cfg["wiggle_speed"])
    time.sleep(.1)
    move_at_speed(0, cfg["cast_pos"], cfg["cast_speed"])
    # random_wait(cfg["time_between_casts_low"], cfg["time_between_casts_high"])


# Initialize all servos to 90 degree position upon startup
move_at_speed(0, cfg["wiggle_pos"], cfg["gentle_speed"])

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
    global rand_timer

    def __init__(self):
        pass

    @property
    def name(self):
        return "base_state"

    def enter(self, mch):
        # set servos to starting position
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, fig_web, rand_timer
        sw = utilities.switch_state(l_sw, r_sw, time.sleep, 3.0)
        if sw == "left_held":
            if cfg["timer"] == True:
                cfg["timer"] = False
                cont_run = False
                files.write_json_file("cfg.json", cfg)
                return
            if cont_run:
                cont_run = False
            elif cfg["timer"] == False:
                cont_run = True
        elif cfg["timer"] == True:
            if rand_timer <= 0:
                an()
                rand_timer = int(cfg["timer_val"]) * 60
                print("an done")
            else:
                rand_timer -= 1
        elif sw == "left" or cont_run:
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
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m) - 1:
                self.i = 0
        if r_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "options":
                mch.go_to("options")
            elif sel_i == "volume_settings":
                mch.go_to("volume_settings")
            elif sel_i == "centerfig":
                mch.go_to("servo_settings")
            else:
                mch.go_to("base_state")


class Opt(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "options"

    def enter(self, mch):
        files.log_item("Choose sounds menu")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(mnu_o) - 1:
                self.i = 0
        if r_sw.fell:
            options = mnu_o[self.sel_i].split("_")
            if options[0] == "timer":
                cfg["timer"] = True
                cfg["timer_val"] = str(options[1])
                rand_timer = 0
            elif mnu_o[self.sel_i] == "wind":
                cfg["wind"] = True
            elif mnu_o[self.sel_i] == "no_wind":
                cfg["wind"] = False
            elif mnu_o[self.sel_i] == "random_raise_lower":
                cfg["random"] = True
            elif mnu_o[self.sel_i] == "raise_lower":
                cfg["random"] = False
            elif mnu_o[self.sel_i] == "exit_this_menu":
                files.write_json_file("cfg.json", cfg)
                mch.go_to("base_state")
                return


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Opt())

time.sleep(5)

while True:
    st_mch.upd()
    time.sleep(0.01)


