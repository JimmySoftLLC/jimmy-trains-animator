import storage
import board
import digitalio

top_sw = board.GP6
bot_sw = board.GP7

top_sw = digitalio.DigitalInOut(top_sw)
top_sw.direction = digitalio.Direction.INPUT
top_sw.pull = digitalio.Pull.UP

bot_sw = digitalio.DigitalInOut(bot_sw)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP

# Hold either switch while plugging in / resetting to make CIRCUITPY writable by USB
if not top_sw.value or not bot_sw.value:
    storage.remount("/", readonly=True)    # computer can write
else:
    storage.remount("/", readonly=False)   # code can write cfg.json
