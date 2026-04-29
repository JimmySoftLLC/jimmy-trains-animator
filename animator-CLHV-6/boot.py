import storage
import board
import digitalio

# Setup the switch
bot_sw = board.GP20

bot_sw = digitalio.DigitalInOut(bot_sw)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP

# Hold bottom button while plugging in / resetting to make CIRCUITPY writable by USB
if not bot_sw.value:
    storage.remount("/", readonly=True)    # computer can write
else:
    storage.remount("/", readonly=False)   # code can write cfg.json