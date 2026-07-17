import storage
import board
import digitalio

# -------------------------------------------------------------------
# Left bumper:
#   GP21 = input with pull-up
#   GP22 = output LOW (acts as ground)
# -------------------------------------------------------------------

gnd_pin = digitalio.DigitalInOut(board.GP22)
gnd_pin.direction = digitalio.Direction.OUTPUT
gnd_pin.value = False

l_sw = digitalio.DigitalInOut(board.GP21)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP

# -------------------------------------------------------------------
# Right bumper:
#   GP8 = input with pull-up
#   GND = other side of switch
# -------------------------------------------------------------------

r_sw = digitalio.DigitalInOut(board.GP8)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP

# Hold either switch while plugging in / resetting
# to make CIRCUITPY writable by USB
if not l_sw.value or not r_sw.value:
    storage.remount("/", readonly=True)     # computer can write
else:
    storage.remount("/", readonly=False)    # code can write cfg.json