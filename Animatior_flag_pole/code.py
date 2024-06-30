import time
import board
import digitalio
from adafruit_motor import servo # type: ignore
import pwmio
from adafruit_debouncer import Debouncer # type: ignore
import utilities
import files
import gc

def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP6)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP7)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

# Define the pins connected to the stepper motor driver
coil_A_1 = digitalio.DigitalInOut(board.GP10)
coil_A_2 = digitalio.DigitalInOut(board.GP11)
coil_B_1 = digitalio.DigitalInOut(board.GP12)
coil_B_2 = digitalio.DigitalInOut(board.GP13)

# Set the pins as outputs
coil_A_1.direction = digitalio.Direction.OUTPUT
coil_A_2.direction = digitalio.Direction.OUTPUT
coil_B_1.direction = digitalio.Direction.OUTPUT
coil_B_2.direction = digitalio.Direction.OUTPUT

# Define the step sequence for a unipolar stepper motor
step_seq_fwd = [
    [0, 0, 1, 1],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [1, 0, 0, 1]   # Step 4
]

# Define the step sequence for a unipolar stepper motor
step_seq_rev = [
    [1, 0, 0, 1],  # Step 4
    [1, 1, 0, 0],  # Step 3
    [0, 1, 1, 0],  # Step 2
    [0, 0, 1, 1]   # Step 1   
]

# Function to set the coil states
def set_step(step):
    coil_A_1.value = step[0]
    coil_A_2.value = step[1]
    coil_B_1.value = step[2]
    coil_B_2.value = step[3]
    
# Function to move the motor a given number of steps
def move_motor(steps, direction, shk, min_sk, max_sk, delay=0.005):
    call_interval = 5
    which_one = 0
    if direction == 'forward':
        seq = step_seq_fwd
    elif direction == 'backward':
        seq = step_seq_rev
    else:
        raise ValueError("Direction must be 'forward' or 'backward'")
    for i in range(steps):
        if i % call_interval == 0:
            if which_one == 0:
                fl_shk.angle = max_sk
                which_one = 1
            else:
                fl_shk.angle = min_sk
                which_one = 0
        for step in seq:
            set_step(step)
            time.sleep(delay)
        
  
# Setup the servos
fl_shk = pwmio.PWMOut(board.GP15, duty_cycle=2 ** 15, frequency=50)
fl_shk = servo.Servo(fl_shk, min_pulse=500, max_pulse=2500)


################################################################################
# State Machine


class StMch(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add(self, state):
        self.states[state.name] = state

    def go_to(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def upd(self):
        if self.state:
            self.state.upd(self)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, mch):
        pass

    def exit(self, mch):
        pass

    def upd(self, mch):
        pass


class BseSt(Ste):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, mch):
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
            else:
                cont_run = True
        elif switch_state == "left" or cont_run:
            an(cfg["option_selected"])
        elif switch_state == "right":
            mch.go_to('main_menu')


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "volume_settings":
                mch.go_to('volume_settings')
            else:
                mch.go_to('base_state')


###############################################################################
# Create the state machine

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")


while True:
    st_mch.upd()
    move_motor(1000, 'forward', False, 180, 180)  # Rotate forward
    time.sleep(1)
    move_motor(1000, 'backward', False, 180, 180)  # Rotate backward
    move_motor(500, 'backward', True, 100, 90)  # Rotate backward
    fl_shk.angle = 180
    move_motor(100, 'backward', False, 180, 180)  # Rotate backward
    time.sleep(1)

