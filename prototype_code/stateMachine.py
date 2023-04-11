import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import pwmio
import digitalio
import os
import random
import rtc
import board
from analogio import AnalogIn
from rainbowio import colorwheel
from adafruit_motor import servo
from adafruit_debouncer import Debouncer
from analogio import AnalogIn
from adafruit_motor import servo

analog_in = AnalogIn(board.A0)

def get_voltage(pin):
    return (pin.value) / 65536

def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

# Pins
SWITCH_0_PIN = board.GP6
SWITCH_1_PIN = board.GP7

# create a PWMOut object on Pin .
pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
treeServo = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
upPos = 167
upPosChop = upPos - 3
downPos = 60
my_servo = servo.Servo(pwm)
my_servo.angle=0
my_servo2 = servo.Servo(treeServo)
my_servo2.angle=upPos

################################################################################
# Setup hardware
switch_io_0 = digitalio.DigitalInOut(SWITCH_0_PIN)
switch_io_0.direction = digitalio.Direction.INPUT
switch_io_0.pull = digitalio.Pull.UP
switch_0 = Debouncer(switch_io_0)
switch_io_1 = digitalio.DigitalInOut(SWITCH_1_PIN)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP
switch_1 = Debouncer(switch_io_1)

#setup sdCard
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

#setup audio
i2s_bclk = board.GP18   # BCK on PCM5102 I2S DAC (SCK pin to Gnd)
i2s_wsel = board.GP19  # LCLK on PCM5102
i2s_data = board.GP20  # DIN on PCM5102
num_voices = 2

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)

mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback

options = [
'choppingToMusic',
'choppingThunder',
'choppingRandom',
'choppingNoOtherSounds',
'choppingBirdsAndDogs'
]

print("machine has started")

def setVolume():
    volume = get_voltage(analog_in)
    mixer.voice[0].level = volume
    mixer.voice[1].level = volume
    
def sleepAndUpdateVolume(seconds):
    setVolume()
    time.sleep(seconds)

################################################################################
# Global Variables


################################################################################
# State Machine

class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def update(self):
        if self.state:
            self.state.update(self)

    # When pausing, don't exit the state
    def pause(self):
        self.state = self.states['paused']
        self.state.enter(self)

    # When resuming, don't re-enter the state
    def resume_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]

    def reset(self):
        """As indicated, reset"""
        self.firework_color = random_color()
        self.burst_count = 0
        self.shower_count = 0
        self.firework_step_time = time.monotonic() + 0.05

################################################################################
# States

# Abstract parent state class.

class State(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        if switch_0.fell:
            machine.paused_state = machine.state.name
            machine.pause()
            return False
        return True


# Wait for 10 seconds to midnight or the witch to be pressed,
# then drop the ball.

class WaitingState(State):

    def __init__(self):      
        pass

    @property
    def name(self):
        return 'waiting'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        switch_0.update()
        switch_1.update()
        if switch_0.fell:
            sleepAndUpdateVolume(0.05)
            #wave1 = audiocore.WaveFile(open("/sd/wav/birds3.wav", "rb"))
            sleepAndUpdateVolume(1)
            #mixer.voice[1].play( wave1, loop=False )
            chopNum = 1
            chopNumber = random.randint(2, 7)
            while chopNum < chopNumber:
                wave0 = audiocore.WaveFile(open("/sd/feller_chops/chop" + str(chopNum) + ".wav", "rb"))
                chopNum += 1
                chopActive = True
                for angle in range(0, upPos+5, 10):  # 0 - 180 degrees, 5 degrees at a time.
                    my_servo.angle = angle                                 
                    if angle >= (upPos-10) and chopActive:
                        mixer.voice[0].play( wave0, loop=False )
                        chopActive = False
                    if angle >= upPos:
                        chopActive = True
                        my_servo2.angle = upPosChop
                        sleepAndUpdateVolume(0.1)
                        my_servo2.angle = upPos
                        sleepAndUpdateVolume(0.1)
                        my_servo2.angle = upPosChop
                        sleepAndUpdateVolume(0.1)
                        my_servo2.angle = upPos
                        sleepAndUpdateVolume(0.1)
                    sleepAndUpdateVolume(0.02)
                    setVolume()
                if chopNum < chopNumber: 
                    for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                        my_servo.angle = angle
                        sleepAndUpdateVolume(0.02)
                        setVolume()
                pass
            wave0 = audiocore.WaveFile(open("/sd/feller_sound_options/option_birds_dogs.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            for angle in range(upPos, 50 + downPos, -5): # 180 - 0 degrees, 5 degrees at a time.
                my_servo2.angle = angle
                sleepAndUpdateVolume(0.06)
                setVolume()
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 50 + downPos
            sleepAndUpdateVolume(0.1)
            my_servo2.angle = 43 + downPos
            while mixer.voice[0].playing:
                setVolume()
            for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
                my_servo.angle = angle
                sleepAndUpdateVolume(0.02)
            for angle in range( 43 + downPos, upPos, 1): # 180 - 0 degrees, 5 degrees at a time.
                my_servo2.angle = angle
                sleepAndUpdateVolume(0.01)
            my_servo2.angle = upPos
            sleepAndUpdateVolume(0.02)
            my_servo2.angle = upPos

        if switch_1.fell:
            
            print("Files on filesystem:")
            print("====================")
            print_directory("/sd/wav")

            print('Just pressed 1')
            volume = get_voltage(analog_in)
            print(volume)
            machine.go_to_state('program')

class ProgramState(State):

    def __init__(self):
        self.optionIndex = 0

    @property
    def name(self):
        return 'program'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            wave0 = audiocore.WaveFile(open("/sd/wav/option mode.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        switch_0.update()
        switch_1.update()
        if switch_0.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                wave0 = audiocore.WaveFile(open("/sd/wav/" + options[self.optionIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.optionIndex +=1
                if self.optionIndex > 4:
                    self.optionIndex = 0
                while mixer.voice[0].playing:
                    pass
        if switch_1.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                wave0 = audiocore.WaveFile(open("/sd/wav/optionSelected.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            machine.go_to_state('waiting')

# Do nothing, wait to be reset

class ExampleState(State):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'example'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        State.update(self, machine)


################################################################################
# Create the state machine

pretty_state_machine = StateMachine()
pretty_state_machine.add_state(WaitingState())
pretty_state_machine.add_state(ProgramState())

pretty_state_machine.go_to_state('waiting')

while True:
    pretty_state_machine.update()
    setVolume()
    sleepAndUpdateVolume(.1)
    
    
