import time
import board
import digitalio
from adafruit_motor import servo
import pwmio

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
step_sequence1 = [
    [0, 0, 1, 1],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [1, 0, 0, 1]   # Step 4
]

# Define the step sequence for a unipolar stepper motor
step_sequence2 = [
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
    
# Function to move the motor a given number of steps
def move_motor(steps, direction, shk, min_sk, max_sk, delay=0.005):
    call_interval = 5
    which_one = 0
    if direction == 'forward':
        seq = step_sequence1
    elif direction == 'backward':
        seq = step_sequence2
    else:
        raise ValueError("Direction must be 'forward' or 'backward'")
    for i in range(steps):
        if i % call_interval == 0:
            if which_one == 0:
                fl_shk.angle = max_sk
                which_one = 1
            else:
                fl_shk.angle = min_sk
                which_one = 0
        for step in seq:
            set_step(step)
            time.sleep(delay)
        
  
# Setup the servos
fl_shk = pwmio.PWMOut(board.GP15, duty_cycle=2 ** 15, frequency=50)
fl_shk = servo.Servo(fl_shk, min_pulse=500, max_pulse=2500)


# Main loop to rotate the motor back and forth
while True:

    move_motor(1000, 'forward', False, 180, 180)  # Rotate forward
    time.sleep(1)
    move_motor(1000, 'backward', False, 180, 180)  # Rotate backward
    move_motor(500, 'backward', True, 100, 90)  # Rotate backward
    fl_shk.angle = 180
    move_motor(100, 'backward', False, 180, 180)  # Rotate backward
    time.sleep(1)
    

