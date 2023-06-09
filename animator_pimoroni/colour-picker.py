# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# This example demonstrates the use of a modifier key to pick the colour of the
# keys' LEDs, as well as the LED sleep functionality.

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

from pmk import PMK, hsv_to_rgb
#from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

MODIFIER_KEY = 0

# Set up Keybow
keybow = PMK(Hardware())
keys = keybow.keys

# Enable LED sleep and set a time of 5 seconds before the LEDs turn off.
# They'll turn back on with a tap of any key!
keybow.led_sleep_enabled = True
keybow.led_sleep_time = 5

# Set up the modifier key. It's 0, or the bottom left key.
modifier_key = keys[MODIFIER_KEY]
modifier_key.modifier = True

# The starting colour (black/off)
rgb = (0, 0, 0)

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # If the modifier key and any other key are pressed, then set all the
    # keys to the selected colour. The second key pressed picks the colour.
    if modifier_key.held and keybow.any_pressed:
        if len(keybow.get_pressed()) > 1:
            hue = max(keybow.get_pressed()) / 15.0
            rgb = hsv_to_rgb(hue, 1.0, 1.0)

    keybow.set_all(*rgb)
