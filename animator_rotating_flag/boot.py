import storage
import board
import digitalio
import time

bot_sw = digitalio.DigitalInOut(board.GP11)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP

USB_HOLD_MAX = 4.0

if not bot_sw.value:
    start_time = time.monotonic()
    while not bot_sw.value and time.monotonic() - start_time < USB_HOLD_MAX:
        time.sleep(0.05)

    if bot_sw.value:
        # Released before 8 seconds = USB programming mode
        storage.remount("/", readonly=True)
    else:
        # Still held after 8 seconds = normal filesystem;
        # main program will see the continued hold and change the light
        storage.remount("/", readonly=False)
else:
    storage.remount("/", readonly=False)
