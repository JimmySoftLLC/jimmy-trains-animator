import storage
import board
import digitalio

# Setup the switches
right_sw_pin = board.GP15

right_sw = digitalio.DigitalInOut(right_sw_pin)
right_sw.direction = digitalio.Direction.INPUT
right_sw.pull = digitalio.Pull.UP

# Hold switch while plugging in / resetting to make CIRCUITPY writable by USB
if not right_sw.value:
    storage.remount("/", readonly=True)    # computer can write
else:
    storage.remount("/", readonly=False)   # code can write cfg.json