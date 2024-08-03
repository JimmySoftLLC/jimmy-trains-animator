import utilities
from adafruit_debouncer import Debouncer
import time
import board
import digitalio
from adafruit_motor import servo
import pwmio
import random
import audiobusio
import audiomixer
import audiomp3
import asyncio
from analogio import AnalogIn
import files

def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))
    
gc_col("Imports gc, files")

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP2)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP3)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

# Define the pins connected to the stepper motor driver
coil_A_1 = digitalio.DigitalInOut(board.GP4)
coil_A_2 = digitalio.DigitalInOut(board.GP5)
coil_B_1 = digitalio.DigitalInOut(board.GP6)
coil_B_2 = digitalio.DigitalInOut(board.GP7)

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
            
def upd_vol(seconds):
    volume = a_in.value / 65536
    mix.voice[0].level = volume
    time.sleep(seconds)

# Setup the servos
kite_rot = pwmio.PWMOut(board.GP17, duty_cycle=2 ** 15, frequency=50)
kite_rot = servo.Servo(kite_rot, min_pulse=500, max_pulse=2500)

lst_kite_pos = 90
lst_kite_deploy_pos = 1200
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
    
    for _ in range(total_steps + 1):
        kite_ang = lst_kite_pos + 1 * sign
        move_kite(kite_ang)
        time.sleep(spd)       

def move_kite (servo_pos):
    global lst_kite_pos
    if servo_pos < kite_min: servo_pos = kite_min
    if servo_pos > kite_max: servo_pos = kite_max
    kite_rot.angle = servo_pos
    lst_kite_pos = servo_pos
    
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

w0 = audiomp3.MP3Decoder(open("wav/kids_playing.mp3", "rb"))

#mix.voice[0].play(w0, loop=False)

def rotate_kite():
    for _ in range(10):
        dist = random.randint(75, 75)
        kite_move (90 + dist, .02)
        time.sleep(1)
        kite_move (90 - dist, .02)
        time.sleep(1)

################################################################################
# async methods

# Create an event loop
loop = asyncio.get_event_loop()

async_running = False

async def upd_vol_async(sec):
        v = a_in.value / 65536
        mix.voice[0].level = v
        await asyncio.sleep(sec)

async def kite_move_async():
    global lst_kite_pos, async_running
    spd = .02
    while async_running:
        rand_pos_1 = random.randint(15, 40) 
        rand_pos_2 = random.randint(110, 165)  
        sign = 1
        if lst_kite_pos > rand_pos_1:
            sign = -1
        total_steps = abs(rand_pos_1 - lst_kite_pos)
        for _ in range(total_steps + 1):
            kite_ang = lst_kite_pos + 1 * sign
            move_kite(kite_ang)
            if not async_running:
                break
            await asyncio.sleep(spd)
        await asyncio.sleep(2*spd)    
        sign = 1
        if lst_kite_pos > rand_pos_2:
            sign = -1
        total_steps = abs(rand_pos_2 - lst_kite_pos)
        for _ in range(total_steps + 1):
            kite_ang = lst_kite_pos + 1 * sign
            move_kite(kite_ang)
            if not async_running:
                break
            await asyncio.sleep(spd)
        await asyncio.sleep(2*spd)    
        
async def move_motor_async(steps, direction, spd=0.005):
    global async_running
    if direction == 'down':
        seq = step_down
    elif direction == 'up':
        seq = step_up
    else:
        raise ValueError("Direction must be 'down' or 'up'")
    for i in range(steps):
        for step in seq:
            set_step(step)
            await asyncio.sleep(spd)
    async_running = False

async def rn_exp(steps, direction):
    global async_running
    async_running = True
    cyc_k = asyncio.create_task(kite_move_async())
    cyc_g = asyncio.create_task(move_motor_async(steps, direction))
    await asyncio.gather(cyc_g, cyc_k)


while True:
    rand_deploy_pos = random.randint(0, 1200)
    direction = "up"
    if lst_kite_deploy_pos > rand_deploy_pos:
        direction = "down"
    total_steps = abs(rand_deploy_pos - lst_kite_deploy_pos)
    asyncio.run(rn_exp(total_steps, direction))
    lst_kite_deploy_pos = rand_deploy_pos
    print(rand_deploy_pos)
    