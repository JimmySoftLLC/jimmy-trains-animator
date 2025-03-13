# MIT License
#
# Copyright (c) 2024 JimmySoftLLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Breakout PWM Frequency Example
# for Adafruit motor controller breakout boards and H-bridge drivers
# TB6612 (#2448), DRV8833 (#3297), DRV8871 (#3190), L9110 (#4489), L293D (#807)

import time
import board
import pwmio
from adafruit_motor import motor
import adafruit_vl53l4cd
import busio

i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)

vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200

print("VL53L4CD Simple Test.")
print("--------------------")
model_id, module_type = vl53.model_info
print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

vl53.start_ranging()

while not vl53.data_ready:
    print("data not ready")
    time.sleep(.2) 

PWM_PIN_A = board.GP16  # Pick two PWM pins on their own channels
PWM_PIN_B = board.GP17
PWM_FREQ = 50  # Custom PWM frequency in Hz; PWMOut min/max 1Hz/50kHz, default is 500Hz
DECAY_MODE = motor.SLOW_DECAY  # Set controller to Slow Decay (braking) mode
THROTTLE_HOLD = 1  # Hold the throttle (seconds)

# DC motor setup; Set pins to custom PWM frequency
pwm_a = pwmio.PWMOut(PWM_PIN_A, frequency=PWM_FREQ)
pwm_b = pwmio.PWMOut(PWM_PIN_B, frequency=PWM_FREQ)
motor1 = motor.DCMotor(pwm_a, pwm_b)
motor1.decay_mode = DECAY_MODE

motor1.throttle = 0  # Stop motor1
print(0)  # Plot/print current throttle value

# Sweep up through 50 duty cycle values

throttle = 50 / 100  # Convert to throttle value (0 to 1.0)
motor1.throttle = throttle
while True:
        vl53.clear_interrupt()
        cur_dist = vl53.distance
        throttle = cur_dist
        if cur_dist > 20: throttle = 50
        if cur_dist < 34 : throttle = 5
        if cur_dist < 10: throttle = 5
        print(cur_dist)
        throttle = throttle / 100  # Convert to throttle value (0 to 1.0)
        motor1.throttle = throttle
        time.sleep(.1)  # Hold at current throttle value

