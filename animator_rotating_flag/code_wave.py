import board
import pwmio
import time
import random
import math
import neopixel

# Single servo pin for Raspberry Pi Pico
SERVO_PINS = [board.GP2]

# Global list to hold PWM objects
servo_arr = []

# Initialize NeoPixel
led_up = neopixel.NeoPixel(board.GP13, 3)
led_up.auto_write = False
led_up.fill((255, 255, 255))
led_up.show()

def initialize_servos(pins):
    """
    Initialize PWM for servo(s).
    
    Args:
    pins (list): List of pin objects (e.g., [board.GP2]).
    
    Returns:
    list: List of PWMOut objects for the servos.
    """
    global servo_arr
    servo_arr = []
    for pin in pins:
        pwm = pwmio.PWMOut(pin, duty_cycle=2**15, frequency=50)
        servo_arr.append(pwm)
    return servo_arr

# Function to set servo angle (0 to 180 degrees) - indexed by servo_id
def set_servo_angle(servo_id, angle):
    """
    Set angle for a specific servo with extended pulse range.
    
    Args:
    servo_id (int): Index of the servo (0 to len(servos)-1).
    angle (float): Angle in degrees (0-180).
    """
    if servo_id >= len(servo_arr):
        raise ValueError(f"Servo ID {servo_id} out of range. Max: {len(servo_arr)-1}")
    
    # Clamp angle to valid range
    angle = max(0, min(180, angle))
    
    # Extended map: 0.5ms (0°) to 2.5ms (180°) pulse width
    pulse_ms = 0.5 + (angle / 180) * 2.0  # 0.5ms to 2.5ms
    duty_cycle = int((pulse_ms / 20) * 65535)  # 20ms period
    servo_arr[servo_id].duty_cycle = duty_cycle

def update_leds(wind_speed, angle_deg, offset_shift_factor):
    """
    Dynamically update NeoPixel LEDs based on simulation state for dramatic effect.
    
    Args:
    wind_speed (float): Current wind speed (for intensity/brightness).
    angle_deg (float): Current servo angle (for hue/warmth).
    offset_shift_factor (float): How much the center is shifting (0-1, for flicker/color shifts).
    """
    # Base brightness scales with wind speed (clamp to 0-255)
    base_brightness = int(min(255, max(100, wind_speed * 20)))  # Stronger wind = brighter
    

    r, g, b = 255, 255, 255  # Cool blue
    
    # Modulate with shift: During rapid center changes, add flicker/strobe
    # if offset_shift_factor > 0.5:
    #     # Flicker: Random dim during shifts
    #     flicker = random.randint(50, 255)
    #     r = int(r * (flicker / 255.0))
    #     g = int(g * (flicker / 255.0))
    #     b = int(b * (flicker / 255.0))
    
    # Apply brightness scaling
    r = int(r * (base_brightness / 255.0))
    g = int(g * (base_brightness / 255.0))
    b = int(b * (base_brightness / 255.0))
    
    # Set all 3 LEDs (or pattern if desired)
    led_up.fill((r, g, b))
    led_up.show()

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
        self.dt = 0.02  # Timestep in seconds (~50Hz update for smooth animation)
        
        # State: angle (radians) and angular velocity (scalar for single servo)
        self.angle = 0.0  # Initial rest position (radians)
        self.ang_vel = 0.0
        
        # Wind state: base wind speed (m/s) and direction (radians from vertical)
        self.base_wind_speed = 5.0  # Steady breeze
        self.wind_dir = math.pi / 2  # Start horizontal; will vary randomly
        
        # Enhanced turbulence: More frequencies and random phases for chaotic gusts
        self.turb_frequencies = [0.05, 0.2, 0.5, 1.0, 2.0]  # Broader spectrum for randomness
        self.turb_amplitudes = [3.0, 2.0, 1.5, 0.8, 0.4]  # Higher amps for stronger random variations
        self.turb_phases = [random.uniform(0, 2*math.pi) for _ in self.turb_frequencies]  # Random starts
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
        speed_var = random.uniform(0.7, 1.3)  # ±30% variation per update for gustiness
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
        self.wind_dir = (self.wind_dir * 0.9 + (math.pi / 2 + dir_var + noise) * 0.1)  # Low-pass filter for smooth shifts
        # Clamp to plausible range (e.g., avoid full backward)
        self.wind_dir = max(0, min(math.pi, self.wind_dir))
        
        # Wind vector (x-component for horizontal push; y for vertical if needed)
        self.wind_x = wind_speed * math.sin(self.wind_dir)
        self.wind_y = -wind_speed * math.cos(self.wind_dir)  # Negative y for downward component
        
    def compute_torque(self):
        """Compute drag torque based on wind and angle (single servo)."""
        # Relative wind angle: wind_dir - angle
        rel_angle = self.wind_dir - self.angle
        
        # Projected area factor: sin(rel_angle) for drag
        drag_factor = math.sin(rel_angle)
        
        # Torque magnitude (scaled empirically for servo response)
        area = self.segment_length ** 2
        torque = 0.5 * self.air_density * (self.wind_x ** 2) * self.drag_coeff * area * self.segment_length * abs(drag_factor)
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

def physics_wind_motion(min_angle_deg, max_angle_deg, wind_sim):
    """
    Advanced wind simulation: Use physics to drive servo angle within soft limits.
    Enhanced for random, non-centered waving with periodic wind direction shifts.
    Shifts are smoothed with variable speed (abrupt or smooth).
    LEDs vary with motion for dramatic effect.
    Runs indefinitely until interrupted.
    
    Args:
        min_angle_deg (float): Min angle in degrees.
        max_angle_deg (float): Max angle in degrees.
        wind_sim (WindSimulator): Initialized simulator instance.
    """
    if len(servo_arr) != 1:
        raise ValueError("This simplified version is for a single servo only.")
    
    print("Starting random physics-based wind simulation on 1 servo with dynamic LEDs...")
    
    # Wind shift parameters
    current_offset = 0.0  # Current smooth offset
    target_offset = 0.0
    wave_count = 0
    updates_til_shift = random.randint(20, 100)  # Initial random hold time
    
    # Smoothing factor (0.01 very smooth/slow, 0.2 abrupt/fast)
    # Randomize per shift: lower = smoother, higher = more abrupt
    smooth_factor = 0.05  # Default medium; will randomize on shift
    
    try:
        while True:
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
                current_offset += smooth_factor * (target_offset - current_offset)
            
            # Count "waves" as updates
            wave_count += 1
            
            # Check if time to initiate new wind shift
            if wave_count >= updates_til_shift:
                target_offset = random.uniform(-60, 60)  # New random center offset
                
                # Randomize smoothing: 0.01-0.05 smooth, 0.06-0.20 abrupt
                smooth_factor = random.uniform(0.01, 0.20)
                
                # Reset for next shift
                wave_count = 0
                updates_til_shift = random.randint(20, 100)
            
            # LED dramatic effect: Sync with wind, angle, and shift
            # shift_factor = abs(current_offset - target_offset) / 60.0  # 0-1 normalized shift progress
            # update_leds(wind_sim.current_wind_speed, angle_deg, shift_factor)
            
            time.sleep(wind_sim.dt)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        # Rest position on exit and LEDs off
        set_servo_angle(0, 90)
        led_up.fill((0, 0, 0))
        led_up.show()

# Example usage (updated for single servo on GP2):
initialize_servos(SERVO_PINS)  # 1 servo on GP2

# Servo range test
set_servo_angle(0, 0)
time.sleep(2)

set_servo_angle(0, 180)
time.sleep(2)

set_servo_angle(0, 90)
time.sleep(2)

# Create simulator (tune for more chaos)
wind_sim = WindSimulator(segment_length=0.6, drag_coeff=0.5)

# Set limits (full range as specified)
min_angle = 0  # Degrees
max_angle = 180
physics_wind_motion(min_angle, max_angle, wind_sim)

