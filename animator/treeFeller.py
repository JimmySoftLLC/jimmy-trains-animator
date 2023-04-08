import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import pwmio
import digitalio
import random
import rtc
import board
from analogio import AnalogIn
from rainbowio import colorwheel
from adafruit_motor import servo
from adafruit_debouncer import Debouncer
from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_motor import servo
import files
import animateFeller

################################################################################
# Setup hardware

# Setup and analog pin to be used for volume control
# the the volume control is digital by setting mixer voice levels
analog_in = AnalogIn(board.A0)

def get_voltage(pin):
    return (pin.value) / 65536

# Setup the servo, this animation has two the feller and tree
# also get the programmed values for position which is stored on the sdCard
feller_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
tree_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

feller_servo = servo.Servo(feller_pwm)
tree_servo = servo.Servo(tree_pwm)

# Setup the switches, there are two the Left and Right or Black and Red
SWITCH_1_PIN = board.GP6 #S1 on animator board
SWITCH_2_PIN = board.GP7 #S2 on animator board

switch_io_1 = digitalio.DigitalInOut(SWITCH_1_PIN)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP
left_switch = Debouncer(switch_io_1)

switch_io_2 = digitalio.DigitalInOut(SWITCH_2_PIN)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP
right_switch = Debouncer(switch_io_2)

# Setup sdCard
# the sdCard holds all the media and calibration files
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

files.print_directory(left_switch,"/sd/wav")

# setup audio on the i2s bus, the animator uses the MAX98357A
# the animator can have one or two MAX98357As. one for mono two for stereo
# both MAX98357As share the same bus
# for mono the MAX98357A defaults to combine channels
# for stereo the MAX98357A SD pin is connected to VCC for right and a resistor to VCC for left
# the audio mixer is used so that volume can be control digitally it is set to stereo
# the sample_rate of the audio mixer is set to 22050 hz.  This is the max the raspberry pi pico can handle
# all files with be in the wave format instead of mp3.  This eliminates the need for decoding
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A
num_voices = 2

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer)

################################################################################
# Global Variables

# get the calibration settings which are stored on the sdCard
upPos = 167
upPosChop = upPos - 3
downPos = 60

options = [
'choppingToMusic',
'choppingThunder',
'choppingRandom',
'choppingNoOtherSounds',
'choppingBirdsAndDogs'
]

feller_servo.angle = 0
tree_servo.angle = upPos

################################################################################
# Global Methods

def setVolume():
    volume = get_voltage(analog_in)
    mixer.voice[0].level = volume
    mixer.voice[1].level = volume
    
def sleepAndUpdateVolume(seconds):
    setVolume()
    time.sleep(seconds)

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
        if left_switch.fell:
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
            animateFeller.animationOne(sleepAndUpdateVolume,audiocore, upPos, downPos)
            # sleepAndUpdateVolume(0.05)
            # chopNum = 1
            # chopNumber = random.randint(2, 7)
            # while chopNum < chopNumber:
            #     wave0 = audiocore.WaveFile(open("/sd/wav/chop" + str(chopNum) + ".wav", "rb"))
            #     chopNum += 1
            #     chopActive = True
            #     for angle in range(0, upPos+5, 10):  # 0 - 180 degrees, 5 degrees at a time.
            #         feller_servo.angle = angle                                 
            #         if angle >= (upPos-10) and chopActive:
            #             mixer.voice[0].play( wave0, loop=False )
            #             chopActive = False
            #         if angle >= upPos:
            #             chopActive = True
            #             tree_servo.angle = upPosChop
            #             sleepAndUpdateVolume(0.1)
            #             tree_servo.angle = upPos
            #             sleepAndUpdateVolume(0.1)
            #             tree_servo.angle = upPosChop
            #             sleepAndUpdateVolume(0.1)
            #             tree_servo.angle = upPos
            #             sleepAndUpdateVolume(0.1)
            #         sleepAndUpdateVolume(0.02)
            #         setVolume()
            #     if chopNum < chopNumber: 
            #         for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
            #             feller_servo.angle = angle
            #             sleepAndUpdateVolume(0.02)
            #             setVolume()
            #     pass
            # wave0 = audiocore.WaveFile(open("/sd/wav/falling.wav", "rb"))
            # mixer.voice[0].play( wave0, loop=False )
            # for angle in range(upPos, 50 + downPos, -5): # 180 - 0 degrees, 5 degrees at a time.
            #     tree_servo.angle = angle
            #     sleepAndUpdateVolume(0.06)
            #     setVolume()
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 50 + downPos
            # sleepAndUpdateVolume(0.1)
            # tree_servo.angle = 43 + downPos
            # while mixer.voice[0].playing:
            #     setVolume()
            # for angle in range(upPos, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
            #     feller_servo.angle = angle
            #     sleepAndUpdateVolume(0.02)
            # for angle in range( 43 + downPos, upPos, 1): # 180 - 0 degrees, 5 degrees at a time.
            #     tree_servo.angle = angle
            #     sleepAndUpdateVolume(0.01)
            # tree_servo.angle = upPos
            # sleepAndUpdateVolume(0.02)
            # tree_servo.angle = upPos

        if right_switch.fell:
            print('Just pressed 1')
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
        left_switch.update()
        right_switch.update()
        if left_switch.fell:
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
        if right_switch.fell:
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

# exampleState copy and add functionality

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


###############################################################################
# Create the state machine

pretty_state_machine = StateMachine()
pretty_state_machine.add_state(WaitingState())
pretty_state_machine.add_state(ProgramState())

print("animator has started")

pretty_state_machine.go_to_state('waiting')

while True:
    pretty_state_machine.update()
    sleepAndUpdateVolume(.1)
    