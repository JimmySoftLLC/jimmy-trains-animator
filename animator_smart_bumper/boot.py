import storage
import board
import digitalio

# -------------------------------------------------------------------
# Left button:
#   GP21 = input with pull-up
#   GP22 = output LOW (acts as ground)
# -------------------------------------------------------------------

left_gnd = digitalio.DigitalInOut(board.GP22)
left_gnd.direction = digitalio.Direction.OUTPUT
left_gnd.value = False

left_sw = digitalio.DigitalInOut(board.GP21)
left_sw.direction = digitalio.Direction.INPUT
left_sw.pull = digitalio.Pull.UP

# -------------------------------------------------------------------
# Right button:
#   GP8 = input with pull-up
#   GND = other side of switch
# -------------------------------------------------------------------

right_sw = digitalio.DigitalInOut(board.GP8)
right_sw.direction = digitalio.Direction.INPUT
right_sw.pull = digitalio.Pull.UP

# Hold either switch while plugging in / resetting
# to make CIRCUITPY writable by USB
if not left_sw.value or not right_sw.value:
    storage.remount("/", readonly=True)     # computer can write
else:
    storage.remount("/", readonly=False)    # code can write cfg.json