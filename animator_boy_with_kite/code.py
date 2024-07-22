import time
import board
import digitalio
from adafruit_motor import servo
import pwmio
import random

# Define the pins connected to the stepper motor driver
coil_A_1 = digitalio.DigitalInOut(board.GP10)
coil_A_2 = digitalio.DigitalInOut(board.GP11)
coil_B_1 = digitalio.DigitalInOut(board.GP12)
coil_B_2 = digitalio.DigitalInOut(board.GP13)

# Set the pins as outputs
coil_A_1.direction = digitalio.Direction.OUTPUT
coil_A_2.direction = digitalio.Direction.OUTPUT
coil_B_1.direction = digitalio.Direction.OUTPUT
coil_B_2.direction = digitalio.Direction.OUTPUT

# Define the step sequence for a unipolar stepper motor
step_down = [
    [0, 0, 1, 1],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [1, 0, 0, 1]   # Step 4
]

# Define the step sequence for a unipolar stepper motor
step_up = [
    [1, 0, 0, 1],  # Step 4
    [1, 1, 0, 0],  # Step 3
    [0, 1, 1, 0],  # Step 2
    [0, 0, 1, 1]   # Step 1
]

# Function to set the coil states
def set_step(step):
    coil_A_1.value = step[0]
    coil_A_2.value = step[1]
    coil_B_1.value = step[2]
    coil_B_2.value = step[3]
    
def coils_off():
    coil_A_1.value = 0
    coil_A_2.value = 0
    coil_B_1.value = 0
    coil_B_2.value = 0

# Function to move the motor a given number of steps
def move_motor(steps, direction, delay=0.005):
    if direction == 'down':
        seq = step_down
    elif direction == 'up':
        seq = step_up
    else:
        raise ValueError("Direction must be 'down' or 'up'")
    for i in range(steps):
        for step in seq:
            set_step(step)
            time.sleep(delay)

# Setup the servos
kite_rot = pwmio.PWMOut(board.GP18, duty_cycle=2 ** 15, frequency=50)
kite_rot = servo.Servo(kite_rot, min_pulse=500, max_pulse=2500)

lst_kite_pos = 90
kite_rot.angle = lst_kite_pos
kite_min = 0
kite_max = 180

def kite_move_smooth(n_pos, spd, acceleration):
    global lst_kite_pos
    sign = 1
    if lst_kite_pos > n_pos:
        sign = -1

    total_steps = abs(n_pos - lst_kite_pos)
    
    for step in range(total_steps + 1):
        kite_ang = lst_kite_pos + step * sign
        move_kite(kite_ang)

        # Calculate a factor to adjust speed based on acceleration
        # Using a quadratic function for smooth acceleration and deceleration
        factor = ((step / total_steps) - 0.5) ** 2 * 4
        time.sleep(spd + acceleration * factor)
        
        lst_kite_pos = n_pos
        move_kite(n_pos)

def kite_move(n_pos, spd):
    global lst_kite_pos
    sign = 1
    if lst_kite_pos > n_pos:
        sign = -1

    total_steps = abs(n_pos - lst_kite_pos)
    
    for step in range(total_steps + 1):
        kite_ang = lst_kite_pos + 1 * sign
        move_kite(kite_ang)
        time.sleep(spd)       

def move_kite (servo_pos):
    if servo_pos < kite_min: servo_pos = kite_min
    if servo_pos > kite_max: servo_pos = kite_max
    kite_rot.angle = servo_pos
    global lst_kite_pos
    lst_kite_pos = servo_pos


# Main loop to raise flag up and down and wave it at the top
while True: 
    move_motor(1200, 'down')  # Kite down
    coils_off()
    for _ in range(10):
        dist = random.randint(75, 75)
        kite_move (90 + dist, .01)
        kite_move (90 - dist, .01)
    move_motor(400, 'up')  # Kite up
    coils_off()
    for _ in range(10):
        dist = random.randint(75, 75)
        kite_move (90 + dist, .01)
        kite_move (90 - dist, .01)
    move_motor(400, 'up')  # Kite up
    coils_off()
    for _ in range(10):
        dist = random.randint(75, 75)
        kite_move (90 + dist, .01)
        kite_move (90 - dist, .01)
    move_motor(400, 'up')  # Kite up
    coils_off()
    for _ in range(10):
        dist = random.randint(75, 75)
        kite_move (90 + dist, .01)
        kite_move (90 - dist, .01)
