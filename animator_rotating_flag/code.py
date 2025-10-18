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

import files
import utilities
import time
import board
import microcontroller
import pwmio
import digitalio
import random
import gc
import neopixel
import math
from adafruit_motor import servo
from adafruit_debouncer import Debouncer


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item(
        "Point " + collection_point +
        " Available memory: {} bytes".format(start_mem)
    )


def reset_pico():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


################################################################################
# Setup hardware
# Single servo pin for Raspberry Pi Pico
SERVO_PINS = [board.GP2]

# Global list to hold PWM objects
servo_arr = []
prev_pos_arr = []

# Initialize NeoPixel
led = neopixel.NeoPixel(board.GP13, 3)
led.auto_write = False
led.fill((255, 255, 255))
led.show()


def initialize_servos(pins):
    """
    Initialize PWM for servo(s).

    Args:
    pins (list): List of pin objects (e.g., [board.GP2]).

    Returns:
    list: List of PWMOut objects for the servos.
    """
    global servo_arr, prev_pos_arr
    servo_arr = []
    prev_pos_arr = []
    for pin in pins:
        pwm = pwmio.PWMOut(pin, duty_cycle=2**15, frequency=50)
        servo_arr.append(pwm)
        prev_pos_arr.append(90)
    return servo_arr

# Function to set servo angle (0 to 180 degrees) - indexed by servo_id


def set_servo_angle(servo_id, angle):
    global prev_pos_arr
    """
    Set angle for a specific servo with extended pulse range.

    Args:
    servo_id (int): Index of the servo (0 to len(servos)-1).
    angle (float): Angle in degrees (0-180).
    """
    if servo_id >= len(servo_arr):
        raise ValueError(
            f"Servo ID {servo_id} out of range. Max: {len(servo_arr)-1}")

    # Clamp angle to valid range
    angle = max(0, min(180, angle))

    # Extended map: 0.5ms (0°) to 2.5ms (180°) pulse width
    pulse_ms = 0.5 + (angle / 180) * 2.0  # 0.5ms to 2.5ms
    duty_cycle = int((pulse_ms / 20) * 65535)  # 20ms period
    servo_arr[servo_id].duty_cycle = duty_cycle
    prev_pos_arr[servo_id] = int(angle)


class WindSimulator:
    """
    Enhanced physics-based wind simulator for single-servo flag rigging.
    Removes fixed centering; uses wind-driven drift with random direction variations
    for more natural, unpredictable waving. Turbulence is amplified for randomness.
    Simplified to single servo—no segments or coupling.
    """

    def __init__(self, segment_length=0.2, air_density=1.2, drag_coeff=1.0):
        """
        Args:
        segment_length (float): Length of the flag segment in meters (affects force scaling).
        air_density (float): Air density in kg/m³ (default sea level).
        drag_coeff (float): Drag coefficient for fabric (tune for realism, 0.5-2.0).
        """
        self.segment_length = segment_length
        self.air_density = air_density
        self.drag_coeff = drag_coeff
        # Timestep in seconds (~50Hz update for smooth animation)
        self.dt = 0.02

        # State: angle (radians) and angular velocity (scalar for single servo)
        self.angle = 0.0  # Initial rest position (radians)
        self.ang_vel = 0.0

        # Wind state: base wind speed (m/s) and direction (radians from vertical)
        self.base_wind_speed = 5.0  # Steady breeze
        self.wind_dir = math.pi / 2  # Start horizontal; will vary randomly

        # Enhanced turbulence: More frequencies and random phases for chaotic gusts
        # Broader spectrum for randomness
        self.turb_frequencies = [0.05, 0.2, 0.5, 1.0, 2.0]
        # Higher amps for stronger random variations
        self.turb_amplitudes = [3.0, 2.0, 1.5, 0.8, 0.4]
        self.turb_phases = [random.uniform(
            0, 2*math.pi) for _ in self.turb_frequencies]  # Random starts
        self.turb_time = 0.0

        # Weak, wind-relative restoring force (not fixed center)
        self.restoring_strength = 0.2  # Low to allow drift; 0.0 = pure random wind push

        # Damping for stability (friction-like)
        self.damping = 0.7  # Slightly lower for more persistent waves

        # For LED sync: Track current wind speed
        self.current_wind_speed = self.base_wind_speed

    def update_wind(self):
        """Generate highly variable wind with random direction shifts and amplified turbulence."""
        self.turb_time += self.dt

        # Base wind with random speed fluctuations
        # ±30% variation per update for gustiness
        speed_var = random.uniform(0.7, 1.3)
        wind_speed = self.base_wind_speed * speed_var

        # Turbulence: Sum sines with random phase updates for evolving chaos
        turb = 0.0
        for i, (freq, amp) in enumerate(zip(self.turb_frequencies, self.turb_amplitudes)):
            phase = self.turb_phases[i] + 2 * math.pi * freq * self.turb_time
            turb += amp * math.sin(phase)
            # Occasionally reseed phase for long-term randomness (every ~10s)
            if random.random() < 0.01:
                self.turb_phases[i] = random.uniform(0, 2*math.pi)

        wind_speed += turb * 0.4  # Higher turbulence scaling for more randomness
        self.current_wind_speed = wind_speed  # Store for LED

        # Random direction: Broader swings (±45° base, plus noise) for non-centered waving
        dir_var = random.uniform(-math.pi/4, math.pi/4)  # ±45°
        noise = random.uniform(-0.1, 0.1)  # Small jitter
        # Low-pass filter for smooth shifts
        self.wind_dir = (self.wind_dir * 0.9 +
                         (math.pi / 2 + dir_var + noise) * 0.1)
        # Clamp to plausible range (e.g., avoid full backward)
        self.wind_dir = max(0, min(math.pi, self.wind_dir))

        # Wind vector (x-component for horizontal push; y for vertical if needed)
        self.wind_x = wind_speed * math.sin(self.wind_dir)
        # Negative y for downward component
        self.wind_y = -wind_speed * math.cos(self.wind_dir)

    def compute_torque(self):
        """Compute drag torque based on wind and angle (single servo)."""
        # Relative wind angle: wind_dir - angle
        rel_angle = self.wind_dir - self.angle

        # Projected area factor: sin(rel_angle) for drag
        drag_factor = math.sin(rel_angle)

        # Torque magnitude (scaled empirically for servo response)
        area = self.segment_length ** 2
        torque = 0.5 * self.air_density * \
            (self.wind_x ** 2) * self.drag_coeff * \
             area * self.segment_length * abs(drag_factor)
        torque *= math.copysign(1, drag_factor)  # Direction

        return torque

    def physics_step(self):
        """Euler integration: ang_vel += torque / inertia * dt; angle += ang_vel * dt"""
        self.update_wind()

        # Compute torque for the single servo
        torque = self.compute_torque()

        # Simple rotational inertia (empirical, low for responsive flag)
        inertia = 0.01  # Tune: higher = slower response

        # Angular acceleration
        ang_acc = torque / inertia

        # Update velocity (with damping)
        self.ang_vel += ang_acc * self.dt
        self.ang_vel *= (1 - self.damping * self.dt)  # Exponential decay

        # Update angle
        self.angle += self.ang_vel * self.dt

        # Weak restoring torque relative to *current wind direction* (allows drift, not fixed center)
        rel_rest_angle = self.angle - self.wind_dir  # Bias toward wind, not 0
        restoring_torque = -self.restoring_strength * math.sin(rel_rest_angle)
        gravity_inertia = 0.01
        self.ang_vel += (restoring_torque / gravity_inertia) * self.dt


# Wind shift parameters
current_offset = 0.0  # Current smooth offset
target_offset = 0.0
wave_count = 0
updates_til_shift = random.randint(20, 100)  # Initial random hold time

# Smoothing factor (0.01 very smooth/slow, 0.2 abrupt/fast)
# Randomize per shift: lower = smoother, higher = more abrupt
smooth_factor = 0.05  # Default medium; will randomize on shift

def physics_wind_motion(min_angle_deg, max_angle_deg, wind_sim, dur):
    global current_offset, target_offset, wave_count, updates_til_shift, smooth_factor
    """
    Advanced wind simulation: Use physics to drive servo angle within soft limits.
    Enhanced for random, non-centered waving with periodic wind direction shifts.
    Shifts are smoothed with variable speed (abrupt or smooth).
    LEDs vary with motion for dramatic effect.
    Runs for the specified duration in seconds.

    Args:
        min_angle_deg (float): Min angle in degrees.
        max_angle_deg (float): Max angle in degrees.
        wind_sim (WindSimulator): Initialized simulator instance.
        dur (float): Duration to run the simulation in seconds.
    """
    if len(servo_arr) != 1:
        raise ValueError("This simplified version is for a single servo only.")

    print(
        f"Starting random physics-based wind simulation on 1 servo with dynamic LEDs for {dur} seconds...")

    start_time = time.monotonic()

    if cfg["light"] == "auto":
            if cfg["timer_val"] != "timer_0_seconds" or cfg["timer"]==False:
                turn_on_led()
            else:
                led.brightness=1.0
                led.show()

    try:
        while True:
            current_time = time.monotonic()
            if current_time - start_time >= dur:
                print(f"\nSimulation completed after {dur} seconds.")
                if cfg["light"] == "auto":
                    if cfg["timer_val"] != "timer_0_seconds" or cfg["timer"]==False:
                        turn_off_led()
                break

            # Physics update
            wind_sim.physics_step()

            # Convert physics angle to degrees
            angle_deg = math.degrees(wind_sim.angle)

            # Soft clamp to physics limits (before offset)
            if angle_deg < min_angle_deg:
                angle_deg = min_angle_deg + 0.1 * (angle_deg - min_angle_deg)
            elif angle_deg > max_angle_deg:
                angle_deg = max_angle_deg + 0.1 * (angle_deg - max_angle_deg)

            # Add smoothed shifting offset
            angle_deg += current_offset

            # Final hard clamp to servo range (0-180)
            angle_deg = max(0, min(180, angle_deg))

            set_servo_angle(0, angle_deg)

            # Update smoothing: lerp current toward target
            if abs(current_offset - target_offset) > 0.1:  # If shifting
                current_offset += smooth_factor * \
                    (target_offset - current_offset)

            # Count "waves" as updates
            wave_count += 1

            # Check if time to initiate new wind shift
            if wave_count >= updates_til_shift:
                # New random center offset
                target_offset = random.uniform(-60, 60)

                # Randomize smoothing: 0.01-0.05 smooth, 0.06-0.20 abrupt
                smooth_factor = random.uniform(0.01, 0.20)

                # Reset for next shift
                wave_count = 0
                updates_til_shift = random.randint(20, 100)

            time.sleep(wind_sim.dt)
            if (top_sw_io.value == False):
                sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 3.0)
                if sw == "left_held":
                    cfg["timer"] = False
                    files.write_json_file("cfg.json", cfg)
                    show_timer_mode()
                    if cfg["light"] == "auto":
                        led.brightness = 0
                        led.show()
                    break

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")


def turn_on_led():
    for i in range(0,101):
        led.brightness = float(i/100)
        led.show()
        time.sleep(.01)

def turn_off_led():
    for i in reversed(range(101)):
        led.brightness = float(i/100)
        led.show()
        time.sleep(.01)


# Setup the switches
top_sw = board.GP20
bot_sw = board.GP11

top_sw_io = digitalio.DigitalInOut(top_sw)
top_sw_io.direction = digitalio.Direction.INPUT
top_sw_io.pull = digitalio.Pull.UP
top_sw = Debouncer(top_sw_io)

bot_sw_io = digitalio.DigitalInOut(bot_sw)
bot_sw_io.direction = digitalio.Direction.INPUT
bot_sw_io.pull = digitalio.Pull.UP
bot_sw = Debouncer(bot_sw_io)

################################################################################
# get the calibration settings from the picos flash memory
cfg = files.read_json_file("/cfg.json")

main_m = cfg["main_menu"]

rand_timer = 0
srt_t = time.monotonic()

################################################################################
# Servo methods


def move_at_speed(n, new_position, speed):
    global prev_pos_arr
    sign = 1
    if prev_pos_arr[n] > new_position:
        sign = - 1
    for servo_pos in range(prev_pos_arr[n], new_position, sign):
        m_servo(n, servo_pos)
        time.sleep(speed)
    m_servo(n, new_position)


def m_servo(n, p):
    global prev_pos_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    set_servo_angle(0, float(p))
    prev_pos_arr[n] = p


################################################################################
# animations
def s_1_wiggle_movement(n, center_pt, cyc, spd, wiggle_amount=7):
    for _ in range(cyc):
        move_at_speed(n, center_pt-wiggle_amount, spd)
        move_at_speed(n, center_pt+wiggle_amount, spd)


def an():
    # Set limits (full range as specified)
    min_angle = 0  # Degrees
    max_angle = 180
    wave_dur = random.randint(20, 60)
    physics_wind_motion(min_angle, max_angle, wind_sim, wave_dur)


def show_mode(cycles):
    middle_point = int((cfg["mode_indicate_pos"]+cfg["mode_pos"])/2)
    show_mode_spd = 0.01
    move_at_speed(0, cfg["mode_pos"], cfg["mode_speed"])
    for _ in range(cycles):
        move_at_speed(0, middle_point, show_mode_spd)
        move_at_speed(0, cfg["mode_pos"], show_mode_spd)


def show_timer_mode():
    if cfg["timer"] == True:
        show_mode(2)
    else:
        show_mode(1)


def show_timer_program_option(cycles):
    middle_point = int((cfg["mode_indicate_pos"]+cfg["mode_pos"])/2)
    middle_point = int((middle_point+cfg["mode_pos"])/2)
    move_at_speed(0, cfg["mode_pos"], cfg["mode_speed"])
    for _ in range(cycles):
        move_at_speed(0, middle_point, cfg["mode_speed"])
        move_at_speed(0, cfg["mode_pos"], cfg["mode_speed"])

################################################################################
# State Machine


class StMch(object):

    def __init__(s):
        s.ste = None
        s.stes = {}
        s.paused_state = None

    def add(s, ste):
        s.stes[ste.name] = ste

    def go_to(s, ste):
        if s.ste:
            s.ste.exit(s)
        s.ste = s.stes[ste]
        s.ste.enter(s)

    def upd(s):
        if s.ste:
            s.ste.upd(s)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(s):
        pass

    @property
    def name(s):
        return ""

    def enter(s, mch):
        pass

    def exit(s, mch):
        pass

    def upd(s, mch):
        pass


class BseSt(Ste):
    def __init__(self):
        pass

    @property
    def name(self):
        return "base_state"

    def enter(self, mch):
        show_timer_mode()
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 3.0)
        if sw == "left_held":
            rand_timer = 0
            if cfg["timer"] == True:
                cfg["timer"] = False
                files.write_json_file("cfg.json", cfg)
            elif cfg["timer"] == False:
                cfg["timer"] = True
                files.write_json_file("cfg.json", cfg)
            show_timer_mode()
        elif cfg["timer"] == True:
            if rand_timer <= time.monotonic()-srt_t:
                an()
                timer_val_split = cfg["timer_val"].split("_")
                if timer_val_split[0] == "random":
                    rand_timer = random.uniform(
                        float(timer_val_split[1]), float(timer_val_split[2]))
                    next_time = "{:.1f}".format(rand_timer)
                    print("Next time : " + next_time)
                if timer_val_split[0] == "timer":
                    rand_timer = float(timer_val_split[1])
                    next_time = "{:.1f}".format(rand_timer)
                    print("Next time : " + next_time)
                srt_t = time.monotonic()
        elif sw == "left":
            an()
            print("an done")
        elif sw == "right":
            mch.go_to("main_menu")


class Main(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "main_menu"

    def enter(self, mch):
        files.log_item("Main menu")
        show_mode(3)
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        top_sw.update()
        bot_sw.update()
        if top_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m) - 1:
                self.i = 0
            print(main_m[self.sel_i])
            show_timer_program_option(self.sel_i+1)
        if bot_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "exit_this_menu":
                print(sel_i)
                cfg["timer"] = False
                rand_timer = 0
                files.write_json_file("cfg.json", cfg)
                mch.go_to("base_state")
            else:
                print(sel_i)
                cfg["timer"] = True
                cfg["timer_val"] = sel_i
                rand_timer = 0
                files.write_json_file("cfg.json", cfg)
                mch.go_to("base_state")


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())

# Example usage (updated for single servo on GP2):
initialize_servos(SERVO_PINS)  # 1 servo on GP2

# Servo range test
set_servo_angle(0, 90)

# Create simulator (tune for more chaos)
wind_sim=WindSimulator(segment_length=0.6, drag_coeff=0.5)

sw=utilities.switch_state(top_sw, bot_sw, time.sleep, 3.0)

if sw == "left_held":  # top switch counter clockwise
    cfg["light"] = "auto"
    files.write_json_file("cfg.json", cfg)
    show_mode(4)
elif sw == "right_held":  # top switch clockwise
    cfg["light"] = "on"
    files.write_json_file("cfg.json", cfg)
    show_mode(4)
else:
    move_at_speed(0, cfg["mode_indicate_pos"], cfg["mode_speed"])
    time.sleep(5)

if cfg["light"] == "auto":
    turn_off_led()

st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")

while True:
    st_mch.upd()
    time.sleep(0.01)
