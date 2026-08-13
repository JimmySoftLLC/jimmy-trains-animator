import storage
import board
import digitalio

# Setup the switches
bot_sw_pin = board.GP7

bot_sw = digitalio.DigitalInOut(bot_sw_pin)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP

# Hold switch while plugging in / resetting to make CIRCUITPY writable by USB
if not bot_sw.value:
    storage.remount("/", readonly=True)    # computer can write
else:
    storage.remount("/", readonly=False)   # code can write cfg.json