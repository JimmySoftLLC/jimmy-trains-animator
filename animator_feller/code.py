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
import audiomp3
from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_debouncer import Debouncer
from analogio import AnalogIn
import files
import animate_feller

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

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
# the sdCard holds all the media and calibration files
# if the card is missing a voice command is spoken
# the user inserts the card a presses the left button to move forward
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)
try:
  sdcard = sdcardio.SDCard(spi, cs)
  vfs = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")
except:
  wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
  audio.play(wave0)
  while audio.playing:
    pass
  cardInserted = False
  while not cardInserted:
    left_switch.update()
    if left_switch.fell:
        try:
            sdcard = sdcardio.SDCard(spi, cs)
            vfs = storage.VfsFat(sdcard)
            storage.mount(vfs, "/sd")
            cardInserted = True
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_success.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass
        except:
            wave0 = audiomp3.MP3Decoder(open("wav/micro_sd_card_not_inserted.mp3", "rb"))
            audio.play(wave0)
            while audio.playing:
                pass

# Setup the mixer it can play higher quality audio wav using larger wave files
# wave files are less cpu intensive since they are not compressed
num_voices = 2
mixer = audiomixer.Mixer(voice_count=num_voices, sample_rate=22050, channel_count=2,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer)

################################################################################
# Global Variables

# get the calibration settings from various json files which are stored on the sdCard
config = files.read_json_file("/sd/config_feller.json")
tree_down_pos = config["tree_down_pos"]
tree_up_pos = config["tree_up_pos"]
feller_rest_pos = config["feller_rest_pos"]
feller_chop_pos = config["feller_chop_pos"]

if tree_down_pos < 0: tree_down_pos = 0
if tree_up_pos > 170: tree_up_pos = 170
if feller_rest_pos < 0: feller_rest_pos = 0
if feller_chop_pos > 170: feller_chop_pos = 170

config_main_menu = files.read_json_file("/sd/feller_menu/main_menu.json")
main_menu = config_main_menu["main_menu"]

config_choose_sounds = files.read_json_file("/sd/feller_menu/choose_sounds.json")
feller_sound_options = config_choose_sounds["choose_sounds"]

config_feller_dialog = files.read_json_file("/sd/feller_dialog/feller_dialog.json")

feller_dialog_positive = config_feller_dialog["feller_dialog_positive"]
feller_dialog_negative = config_feller_dialog["feller_dialog_negative"]

config_adjust_feller_and_tree = files.read_json_file("/sd/feller_menu/adjust_feller_and_tree.json")
adjust_feller_and_tree = config_adjust_feller_and_tree["adjust_feller_and_tree"]

# set servos to starting position
feller_servo.angle = 0
tree_servo.angle = tree_up_pos

################################################################################
# Global Methods

def reset_to_defaults():
    tree_up_pos = 167
    tree_down_pos = 60
    feller_rest_pos = 0
    feller_chop_pos = 180

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

class BaseState(State):

    def __init__(self):      
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, machine):
        sleepAndUpdateVolume(.1)
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/animations_are_now_active.wav", "rb"))
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
            animate_feller.animation_one(
                sleepAndUpdateVolume, 
                audiocore, 
                mixer, 
                feller_servo, 
                tree_servo, 
                tree_up_pos, 
                tree_down_pos, 
                config["option_selected"], 
                feller_sound_options,
                feller_rest_pos,
                feller_chop_pos,
                feller_dialog_positive,
                feller_dialog_negative)
        if right_switch.fell:
            print('Just pressed 1')
            machine.go_to_state('main_menu')
            
class AdjustFellerAndTree(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'adjust_feller_and_tree'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/adjust_feller_and_tree_menu.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
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
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/" + adjust_feller_and_tree[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(adjust_feller_and_tree)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    pass
        if right_switch.fell:
                selected_menu_item = adjust_feller_and_tree[self.selectedMenuIndex]
                if selected_menu_item == "move_feller_to_chop_position":
                    feller_servo.angle = feller_chop_pos   
                elif selected_menu_item == "move_feller_to_rest_position":
                    feller_servo.angle = feller_rest_pos
                elif selected_menu_item == "move_tree_to_upright_position":
                    tree_servo.angle = tree_up_pos   
                elif selected_menu_item == "move_tree_to_fallen_position":
                    tree_servo.angle = 43 + tree_down_pos
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
                    machine.go_to_state('base_state')

class ChooseSounds(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        print('Select a program option')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/sound_selection_menu.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
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
                if self.menuIndex == len(feller_sound_options)-1:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/exit_this_menu.wav" , "rb"))
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/option_" + feller_sound_options[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(feller_sound_options)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    pass
        if right_switch.fell:
            if self.selectedMenuIndex == len(feller_sound_options)-1:
                if mixer.voice[0].playing:
                    mixer.voice[0].stop()
                    while mixer.voice[0].playing:
                        pass
                machine.go_to_state('main_menu')
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                config["option_selected"] = feller_sound_options[self.selectedMenuIndex]
                files.write_json_file("/sd/config_feller.json",config)
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/option_selected.wav", "rb"))
                mixer.voice[0].play( wave0, loop=False )
                while mixer.voice[0].playing:
                    pass
            machine.go_to_state('base_state')

class MainMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, machine):
        print('Select main menu')
        if mixer.voice[0].playing:
            mixer.voice[0].stop()
            while mixer.voice[0].playing:
                pass
        else:
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/main_menu.wav", "rb"))
            mixer.voice[0].play( wave0, loop=False )
            while mixer.voice[0].playing:
                pass
            wave0 = audiocore.WaveFile(open("/sd/feller_menu/press_left_button_right_button.wav", "rb"))
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
                wave0 = audiocore.WaveFile(open("/sd/feller_menu/" + main_menu[self.menuIndex] + ".wav" , "rb"))
                mixer.voice[0].play( wave0, loop=False )
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex +=1
                if self.menuIndex > len(main_menu)-1:
                    self.menuIndex = 0
                while mixer.voice[0].playing:
                    pass
        if right_switch.fell:
            if mixer.voice[0].playing:
                mixer.voice[0].stop()
                while mixer.voice[0].playing:
                    pass
            else:
                selected_menu_item = main_menu[self.selectedMenuIndex]
                if selected_menu_item == "choose_sounds":
                    machine.go_to_state('choose_sounds')
                elif selected_menu_item == "adjust_feller_and_tree":
                    machine.go_to_state('adjust_feller_and_tree')
                elif selected_menu_item == "exit_menu":
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
                    machine.go_to_state('base_state')
                else:
                    wave0 = audiocore.WaveFile(open("/sd/feller_menu/all_changes_complete.wav", "rb"))
                    mixer.voice[0].play( wave0, loop=False )
                    while mixer.voice[0].playing:
                        pass
                    machine.go_to_state('base_state')
                
# StateTemplate copy and add functionality
class StateTemplate(State):

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
pretty_state_machine.add_state(BaseState())
pretty_state_machine.add_state(MainMenu())
pretty_state_machine.add_state(ChooseSounds())
pretty_state_machine.add_state(AdjustFellerAndTree())

print("animator has started")

pretty_state_machine.go_to_state('base_state')

while True:
    pretty_state_machine.update()
    sleepAndUpdateVolume(.1)
