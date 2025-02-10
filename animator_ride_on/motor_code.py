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

PWM_PIN_A = board.GP16  # Pick two PWM pins on their own channels
PWM_PIN_B = board.GP17
PWM_FREQ = 25  # Custom PWM frequency in Hz; PWMOut min/max 1Hz/50kHz, default is 500Hz
DECAY_MODE = motor.SLOW_DECAY  # Set controller to Slow Decay (braking) mode
THROTTLE_HOLD = 1  # Hold the throttle (seconds)

# DC motor setup; Set pins to custom PWM frequency
pwm_a = pwmio.PWMOut(PWM_PIN_A, frequency=PWM_FREQ)
pwm_b = pwmio.PWMOut(PWM_PIN_B, frequency=PWM_FREQ)
motor1 = motor.DCMotor(pwm_a, pwm_b)
motor1.decay_mode = DECAY_MODE

motor1.throttle = 0  # Stop motor1
print((0,))  # Plot/print current throttle value

# Sweep up through 50 duty cycle values
for duty_cycle in range(0, 101, 2):
    throttle = duty_cycle / 100  # Convert to throttle value (0 to 1.0)
    motor1.throttle = throttle
    print((throttle,))  # Plot/print current throttle value
    time.sleep(1)  # Hold at current throttle value

motor1.throttle = 0  # Stop motor1
print((0,))  # Plot/print current throttle value