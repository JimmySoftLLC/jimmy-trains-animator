import time
import board
import digitalio
from adafruit_motor import servo
import pwmio
import audiobusio
import audiomixer
import audiomp3
from analogio import AnalogIn

# Define the pins connected to the stepper motor driver
coil_A_1 = digitalio.DigitalInOut(board.GP7)
coil_A_2 = digitalio.DigitalInOut(board.GP6)
coil_B_1 = digitalio.DigitalInOut(board.GP5)
coil_B_2 = digitalio.DigitalInOut(board.GP4)

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

# Function to move the motor a given number of steps


def move_motor(steps, direction, shk, min_sk, max_sk, delay=0.005):
    call_interval = 10
    max_min = 0
    if direction == 'down':
        seq = step_down
    elif direction == 'up':
        seq = step_up
    else:
        raise ValueError("Direction must be 'down' or 'up'")
    for i in range(steps):
        if i % call_interval == 0:
            if max_min == 0:
                fl_shk.angle = max_sk
                max_min = 1
            else:
                fl_shk.angle = min_sk
                max_min = 0
        for step in seq:
            set_step(step)
            time.sleep(delay)
            
def upd_vol(seconds):
    volume = a_in.value / 65536
    mix.voice[0].level = volume
    time.sleep(seconds)
            
################################################################################
# Setup hardware

# Setup pin for vol on 5v aud board
a_in = AnalogIn(board.A2)

# setup pin for audio enable 21 on 5v aud board
aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)

aud.play(mix)

upd_vol(.1)

def play_taps():
    w0 = audiomp3.MP3Decoder(open("mp3/taps.mp3", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        upd_vol(.1)
        pass

# Setup the servos
fl_shk = pwmio.PWMOut(board.GP16, duty_cycle=2 ** 15, frequency=50)
fl_shk = servo.Servo(fl_shk, min_pulse=500, max_pulse=2500)

# Set up the led
digitalio.DigitalInOut
led = pwmio.PWMOut(board.GP8, frequency=5000, duty_cycle=0)

#play_taps()

# Main loop to raise flag up and down and wave it at the top
while True:
    move_motor(500, 'down', False, 180, 180)  # Flag down
    led.duty_cycle = 0
    move_motor(500, 'down', False, 180, 180)  # Flag down
    time.sleep(1)
    move_motor(500, 'up', False, 180, 180)  # Flag up
    led.duty_cycle = 65000
    move_motor(500, 'up', False, 180, 180)  # Flag up
    move_motor(1000, 'up', True, 118, 112)  # Flag wave
    fl_shk.angle = 180
    move_motor(100, 'up', False, 180, 180)  # Flag up to orient it before going down
    time.sleep(1)
