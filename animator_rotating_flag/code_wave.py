import board
import pwmio
import time
import random
import math

# Example servo pins (adjust based on your board)
SERVO_PINS = [board.GP2]  # Up to 4 servos for a segmented flag

# Global list to hold PWM objects
servos = []

def initialize_servos(pins):
    """
    Initialize PWM for multiple servos.
    
    Args:
    pins (list): List of pin objects (e.g., [board.D9, board.D10]).
    
    Returns:
    list: List of PWMOut objects for the servos.
    """
    global servos
    servos = []
    for pin in pins:
        pwm = pwmio.PWMOut(pin, duty_cycle=2**15, frequency=50)
        servos.append(pwm)
    return servos

# Function to set servo angle (0 to 180 degrees) - indexed by servo_id
def set_servo_angle(servo_id, angle):
    """
    Set angle for a specific servo.
    
    Args:
    servo_id (int): Index of the servo (0 to len(servos)-1).
    angle (float): Angle in degrees (0-180).
    """
    if servo_id >= len(servos):
        raise ValueError(f"Servo ID {servo_id} out of range. Max: {len(servos)-1}")
    
    # Clamp angle to valid range
    angle = max(0, min(180, angle))
    
    # Map angle to duty cycle (1ms to 2ms pulse width)
    pulse_ms = 1 + (angle / 180) * 1  # 1ms (0°) to 2ms (180°)
    duty_cycle = int((pulse_ms / 20) * 65535)  # 20ms period
    servos[servo_id].duty_cycle = duty_cycle

class WindSimulator:
    """
    Enhanced physics-based wind simulator for flag rigging.
    Removes fixed centering; instead, uses wind-driven drift with random direction variations
    for more natural, unpredictable waving. Turbulence is amplified for randomness.
    """
    def __init__(self, num_segments, segment_length=0.2, air_density=1.2, drag_coeff=1.0):
        """
        Args:
        num_segments (int): Number of flag segments (matches num servos).
        segment_length (float): Length of each segment in meters (affects force scaling).
        air_density (float): Air density in kg/m³ (default sea level).
        drag_coeff (float): Drag coefficient for fabric (tune for realism, 0.5-2.0).
        """
        self.num_segments = num_segments
        self.segment_length = segment_length
        self.air_density = air_density
        self.drag_coeff = drag_coeff
        self.dt = 0.02  # Timestep in seconds (~50Hz update for smooth animation)
        
        # State: angles (radians) and angular velocities for each segment
        self.angles = [0.0] * num_segments  # Initial rest position (radians)
        self.ang_vels = [0.0] * num_segments
        
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
        
        # Random direction: Broader swings (±45° base, plus noise) for non-centered waving
        dir_var = random.uniform(-math.pi/4, math.pi/4)  # ±45°
        noise = random.uniform(-0.1, 0.1)  # Small jitter
        self.wind_dir = (self.wind_dir * 0.9 + (math.pi / 2 + dir_var + noise) * 0.1)  # Low-pass filter for smooth shifts
        # Clamp to plausible range (e.g., avoid full backward)
        self.wind_dir = max(0, min(math.pi, self.wind_dir))
        
        # Wind vector (x-component for horizontal push; y for vertical if needed)
        self.wind_x = wind_speed * math.sin(self.wind_dir)
        self.wind_y = -wind_speed * math.cos(self.wind_dir)  # Negative y for downward component
        
    def compute_torque(self, segment_idx):
        """Compute drag torque on a segment based on wind and angle.
        Torque = 0.5 * rho * v^2 * Cd * A * L * sin(theta)  (simplified for angular)
        Where A ~ segment_length^2, but scaled for torque.
        """
        # Relative wind angle: wind_dir - segment angle
        rel_angle = self.wind_dir - self.angles[segment_idx]
        
        # Projected area factor: sin(rel_angle) for drag
        drag_factor = math.sin(rel_angle)
        
        # Torque magnitude (scaled empirically for servo response)
        area = self.segment_length ** 2
        torque = 0.5 * self.air_density * (self.wind_x ** 2) * self.drag_coeff * area * self.segment_length * abs(drag_factor)
        torque *= math.copysign(1, drag_factor)  # Direction
        
        # Inter-segment coupling: previous segment influences this one (chain tension)
        if segment_idx > 0:
            tension_factor = 0.15  # Slightly weaker for more independent waving
            tension_torque = tension_factor * (self.angles[segment_idx-1] - self.angles[segment_idx])
            torque += tension_torque
        
        return torque
    
    def physics_step(self):
        """Euler integration: ang_vel += torque / inertia * dt; angle += ang_vel * dt"""
        self.update_wind()
        
        for i in range(self.num_segments):
            # Compute torque for this segment
            torque = self.compute_torque(i)
            
            # Simple rotational inertia (empirical, low for responsive flag)
            inertia = 0.01  # Tune: higher = slower response
            
            # Angular acceleration
            ang_acc = torque / inertia
            
            # Update velocity (with damping)
            self.ang_vels[i] += ang_acc * self.dt
            self.ang_vels[i] *= (1 - self.damping * self.dt)  # Exponential decay
            
            # Update angle
            self.angles[i] += self.ang_vels[i] * self.dt
        
        # Weak restoring torque relative to *current wind direction* (allows drift, not fixed center)
        for i in range(self.num_segments):
            rel_rest_angle = self.angles[i] - self.wind_dir  # Bias toward wind, not 0
            restoring_torque = -self.restoring_strength * math.sin(rel_rest_angle)
            gravity_inertia = 0.01
            self.ang_vels[i] += (restoring_torque / gravity_inertia) * self.dt

def physics_wind_motion(min_angles_deg, max_angles_deg, wind_sim):
    """
    Advanced wind simulation: Use physics to drive servo angles within soft limits.
    Enhanced for random, non-centered waving.
    Runs indefinitely until interrupted.
    
    Args:
    min_angles_deg (list): Min angles per segment in degrees.
    max_angles_deg (list): Max angles per segment in degrees.
    wind_sim (WindSimulator): Initialized simulator instance.
    """
    num_servos = len(servos)
    if wind_sim.num_segments != num_servos:
        raise ValueError("WindSimulator num_segments must match num_servos.")
    
    print(f"Starting random physics-based wind simulation on {num_servos} segments...")
    
    try:
        while True:
            # Physics update
            wind_sim.physics_step()
            
            # Convert to degrees and clamp softly (lerp towards limits if exceeded)
            for i in range(num_servos):
                angle_deg = math.degrees(wind_sim.angles[i])
                
                # Soft clamp: if outside limits, pull back gradually
                if angle_deg < min_angles_deg[i]:
                    angle_deg = min_angles_deg[i] + 0.1 * (angle_deg - min_angles_deg[i])
                elif angle_deg > max_angles_deg[i]:
                    angle_deg = max_angles_deg[i] + 0.1 * (angle_deg - max_angles_deg[i])
                
                set_servo_angle(i, angle_deg)
            
            time.sleep(wind_sim.dt)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        # Rest position on exit
         
        for i in range(num_servos):
            set_servo_angle(i, 90)

# Example usage:
# Initialize hardware
initialize_servos(SERVO_PINS[:3])  # 3 segments

# Create simulator (tune for more chaos)
wind_sim = WindSimulator(num_segments=1, segment_length=.6, drag_coeff=.5)

# Set per-segment limits (e.g., tighter at base, looser at tip)
min_angles = [0]  # Degrees
max_angles = [180]
physics_wind_motion(min_angles, max_angles, wind_sim)
