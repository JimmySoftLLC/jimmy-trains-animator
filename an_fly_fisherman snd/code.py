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
import asyncio
import audiobusio
import audiomixer
import audiocore
import audiomp3

from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_debouncer import Debouncer


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item(
        "Point " + collection_point +
        " Available memory: {} bytes".format(start_mem)
    )

################################################################################
# config variables

mvc_folder = "mvc/"

cfg = files.read_json_file("/cfg.json")

main_m = cfg["main_menu"]
vol_set_m = cfg["volume_settings"]
timer_m = cfg["timer_settings"]

rand_timer = 0
srt_t = time.monotonic()

################################################################################
# pin setups

servo_1_pin = board.GP10
servo_2_pin = board.GP11

top_sw_pin = board.GP6
bot_sw_pin = board.GP7
trig_sw_pin = board.GP12

bclk = board.GP18  # BCLK on MAX98357A i2s audio
lrc = board.GP19  # LRC on MAX98357A i2s audio
din = board.GP20  # DIN on MAX98357A i2s audio

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

a_in_pin = board.A0
aud_en_pin = board.GP22

################################################################################
# Setup hardware


# Setup the servo this animation can have up to two servos
# also get the programmed values for position which is stored on the pico itself
servo_1 = pwmio.PWMOut(servo_1_pin, duty_cycle=2 ** 15,
                       frequency=50)  # first prototype used GP10
servo_2 = pwmio.PWMOut(servo_2_pin, duty_cycle=2 ** 15, frequency=50)

servo_1 = servo.Servo(servo_1, min_pulse=500, max_pulse=2500)
servo_2 = servo.Servo(servo_2, min_pulse=500, max_pulse=2500)

prev_pos_arr = [180, 180]

servo_arr = [servo_1, servo_2]

# Setup the switches
top_sw = digitalio.DigitalInOut(top_sw_pin)
top_sw.direction = digitalio.Direction.INPUT
top_sw.pull = digitalio.Pull.UP
top_sw = Debouncer(top_sw)

bot_sw = digitalio.DigitalInOut(bot_sw_pin)
bot_sw.direction = digitalio.Direction.INPUT
bot_sw.pull = digitalio.Pull.UP
bot_sw = Debouncer(bot_sw)

trig_sw = digitalio.DigitalInOut(trig_sw_pin)
trig_sw.direction = digitalio.Direction.INPUT
trig_sw.pull = digitalio.Pull.UP
trig_sw = Debouncer(trig_sw)

# Setup for vol
a_in = AnalogIn(a_in_pin)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(aud_en_pin)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

# Setup the mixer to play mp3 files
mix = audiomixer.Mixer(voice_count=2, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

################################################################################
# misc methods

def rnd_prob(random_value):
    
    if random_value == 0:
        return False
    elif random_value == 1:
        return True
    else:
        y = random.random()
        if y < random_value:
            print("True Random value: " + str(y) + " < Random limit: " + str(random_value))
            return True
    print("False Random value: " + str(y) + " < Random limit: " + str(random_value))
    return False

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
    servo_arr[n].angle = p
    prev_pos_arr[n] = p

################################################################################
# Dialog and sound play methods


def upd_vol(s):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        time.sleep(s)
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except Exception as e:
            files.log_item(e)
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
        mix.voice[1].level = volume
        time.sleep(s)


async def upd_vol_async(s):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        mix.voice[1].level = v
        await asyncio.sleep(s)
    else:
        try:
            v = int(cfg["volume"]) / 100
        except Exception as e:
            files.log_item(e)
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        mix.voice[1].level = v
        await asyncio.sleep(s)


def ch_vol(action):
    v = int(cfg["volume"])
    if "volume" in action:
        v = action.split("volume")
        v = int(v[1])
    if action == "lower1":
        v -= 1
    elif action == "raise1":
        v += 1
    elif action == "lower":
        if v <= 10:
            v -= 1
        else:
            v -= 10
    elif action == "raise":
        if v < 10:
            v += 1
        else:
            v += 10
    if v > 100:
        v = 100
    if v < 1:
        v = 1
    cfg["volume"] = str(v)
    cfg["volume_pot"] = False
    if not mix.voice[0].playing:
        files.write_json_file("cfg.json", cfg)
        ply_a_0(mvc_folder + "volume.mp3")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name, wait=True, repeat=False):
    upd_vol(0)
    if not cfg["use_sd_card"] and "/sd/" in file_name:
        return

    # Stop if voice is currently playing
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1)

    # Choose decoder based on file extension
    if file_name.lower().endswith(".mp3"):
        w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w0 = audiocore.waveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)

    # Play the selected file
    mix.voice[0].play(w0, loop=repeat)

    # Wait until playback completes
    if wait:
        while mix.voice[0].playing:
            upd_vol(0.1)
            pass


def ply_a_1(file_name, wait=True, repeat = False, figure_index = None):
    upd_vol(0)
    if not cfg["use_sd_card"] and "/sd/" in file_name:
        return

    if wait:
        while mix.voice[1].playing:
            upd_vol(0.1)
    else: # Stop if voice is currently playing
        if mix.voice[1].playing:
            mix.voice[1].stop()
            while mix.voice[1].playing:
                upd_vol(0.1)

    # Choose decoder based on file extension
    if file_name.lower().endswith(".mp3"):
        w1 = audiomp3.MP3Decoder(open(file_name, "rb"))
    elif file_name.lower().endswith(".wav"):
        w1 = audiocore.waveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)

    spk_rot = 7

    # Play the selected file
    mix.voice[1].play(w1, loop=repeat)

    # Wait until playback completes
    if wait:
        while mix.voice[1].playing:
            if figure_index != None:
                m_servo(figure_index, prev_pos_arr[figure_index] + spk_rot)
                m_servo(figure_index, prev_pos_arr[figure_index] - spk_rot)
            else:
                upd_vol(0.1)
            pass

def wait_snd():
    while mix.voice[0].playing:
        pass


def wait_snd_1():
    while mix.voice[1].playing:
        upd_vol(.1)
        pass


def stp_a_0():
    mix.voice[0].stop()
    wait_snd()
    gc_col("stp snd")


def stp_a_1():
    mix.voice[1].stop()
    wait_snd_1()


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            ply_a_0(mvc_folder + character + ".mp3")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0(mvc_folder + "dot.mp3")
        ply_a_0(mvc_folder + "local.mp3")


def l_r_but():
    ply_a_0(mvc_folder + "press_left_button_right_button.mp3")


def sel_web():
    ply_a_0(mvc_folder + "web_menu.mp3")
    l_r_but()


def opt_sel():
    ply_a_0(mvc_folder + "option_selected.mp3")


def spk_sng_num(song_number):
    ply_a_0(mvc_folder + "song.mp3")
    spk_str(song_number, False)


def spk_web():
    ply_a_0(mvc_folder + "animator_available_on_network.mp3")
    ply_a_0(mvc_folder + "to_access_type.mp3")
    try:
        if cfg["HOST_NAME"] == "neo-pico":
            ply_a_0(mvc_folder + "neo_dash_pico.mp3")
            ply_a_0(mvc_folder + "dot.mp3")
            ply_a_0(mvc_folder + "local.mp3")
        else:
            spk_str(cfg["HOST_NAME"], True)
        ply_a_0(mvc_folder + "in_your_browser.mp3")
    except Exception as e:
        files.log_item(e)


def get_random_media_file(folder_to_search, file_ext):
    if not file_ext.startswith("."):
        file_ext = "." + file_ext

    file_ext = file_ext.lower()

    myfiles = files.return_directory(
        "",
        folder_to_search,
        file_ext
    )

    if not myfiles:
        return None

    return random.choice(myfiles)


def get_indexed_media_file(folder_to_search, file_ext, index):
    if not file_ext.startswith("."):
        file_ext = "." + file_ext

    file_ext = file_ext.lower()

    myfiles = files.return_directory(
        "",
        folder_to_search,
        file_ext
    )

    if not myfiles:
        return None, 0

    index = index % len(myfiles)

    selected_file = myfiles[index]
    new_index = (index + 1) % len(myfiles)

    print(
        "playing:",
        selected_file,
        "(",
        index,
        "/",
        len(myfiles),
        ")"
    )

    return selected_file, new_index


def play_random_file(folder_to_search, file_ext = "mp3", wait = True, figure_index = None):
    filename = get_random_media_file(folder_to_search, file_ext)
    if not filename:
        return
    filename = filename + "." + file_ext
    full_path = folder_to_search + filename

    print("Filename is:", full_path)
    ply_a_1(full_path, wait, False, figure_index)

################################################################################
# animations

def s_1_wiggle_movement(n, center_pt, cyc, spd, wiggle_amount=7):
    for _ in range(cyc):
        move_at_speed(n, center_pt-wiggle_amount, spd)
        move_at_speed(n, center_pt+wiggle_amount, spd)

fisherman_sequence = 0

def conversation_pause(short_pause=False):
    if short_pause:
        pause_time = random.uniform(0.2, 0.6)
    else:
        pause_time = random.uniform(0.5, 1.2)
    time.sleep(pause_time)

def son_casting_sequence():
    max_cast_attempts = 3
    cast_attempt = 0
    cast_successful = False

    play_random_file("dad/cast_instruction/", "mp3", True, 0)

    conversation_pause()

    while cast_attempt < max_cast_attempts and not cast_successful:
        cast_attempt += 1

        print("Son cast attempt:", cast_attempt)
        cast_result = random.choice([
            "success",
            "tree",
            "success",
            "missed",
            "success",
            "missed",
        ])
        cast_motion(1)
        play_random_file("son/cast_" + cast_result + "/", "mp3", True, 1)

        conversation_pause(short_pause=True)

        play_random_file("dad/respond_cast_" + cast_result + "/", "mp3", True, 0)

        conversation_pause()

        if cast_result == "success":
            cast_successful = True
            break

        if cast_attempt < max_cast_attempts:
            play_random_file("dad/try_again/", "mp3", True, 0)

            conversation_pause()

    if not cast_successful:
        play_random_file("dad/give_up_casting/", "mp3", True, 0)
        return False

    return True


def waiting_conversation():
    play_random_file("son/waiting/", "mp3", True, 1)
    conversation_pause(short_pause=True)
    play_random_file("dad/respond_waiting/", "mp3", True, 0)


def dad_casting_scene():
    play_random_file("dad/own_cast/", "mp3", True, 0)
    cast_motion(0)
    conversation_pause(short_pause=True)
    # Usually let the son comment on Dad's cast.
    if random.randint(1, 4) != 1:
        play_random_file("son/respond_dad_cast/", "mp3", True, 1)


def dad_fishing_scene():
    play_random_file("dad/own_got_bite/", "mp3", True, 0)
    conversation_pause(short_pause=True)
    play_random_file("son/happy/", "mp3", True, 1)

    conversation_pause()

    fish_result = random.choice([
        "caught",
        "lost"
    ])

    if fish_result == "caught":
        play_random_file("dad/own_caught_fish/", "mp3", True, 0)
        conversation_pause(short_pause=True)
        play_random_file("son/happy/", "mp3", True, 1)     

    else:
        play_random_file("dad/own_lost_fish/", "mp3", True, 0)
        conversation_pause(short_pause=True)
        play_random_file("son/sad/", "mp3", True, 1)
        
        
def son_gets_bite_scene():
    play_random_file("son/got_bite/", "mp3", True, 1)
    conversation_pause(short_pause=True)
    # play_random_file("dad/respond_got_bite/", "mp3", True, 0)
    conversation_pause()
    play_random_file("son/fish_on/", "mp3", True, 1)
    conversation_pause(short_pause=True)
    # play_random_file("dad/respond_fish_on/", "mp3", True, 0)


def son_fish_result_scene():
    fish_result = random.choice([
        "caught",
        "caught",
        "lost"
    ])

    if fish_result == "caught":
        play_random_file("son/caught_fish/", "mp3", True, 1)
        conversation_pause(short_pause=True)
        # play_random_file("dad/respond_caught_fish/", "mp3", True, 0)
    else:
        play_random_file("son/lost_fish/", "mp3", True, 1)
        conversation_pause(short_pause=True)
        # play_random_file("dad/respond_lost_fish/", "mp3", True, 0)


def fly_fisherman_dialog():
    global fisherman_sequence

    print("Fly Fisherman sequence:", fisherman_sequence)

    # =========================================================
    # SEQUENCE 0
    #
    # Dad teaches the son to cast.
    #
    # Son may miss, hit a tree, and try again.
    # Once successful, stop and wait for another button press.
    # =========================================================

    if fisherman_sequence == 0:
        cast_successful = son_casting_sequence()

        if cast_successful:
            fisherman_sequence = 1

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 1
    # #
    # # Father and son wait for the fish.
    # #
    # # Son asks or says something.
    # # Dad responds.
    # # =========================================================

    if fisherman_sequence == 1:
        waiting_conversation()

        fisherman_sequence = 2

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 2
    # #
    # # Dad does some fishing too.
    # #
    # # Dad casts and the son may comment.
    # # =========================================================

    if fisherman_sequence == 2:
        dad_casting_scene()

        fisherman_sequence = 3

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 3
    # #
    # # Something happens while fishing.
    # #
    # # Usually continue toward the son's fish.
    # # Occasionally Dad gets the bite instead.
    # # =========================================================

    if fisherman_sequence == 3:
        event = random.choice([
            "son",
            "son",
            "son",
            "dad"
        ])

        if event == "dad":
            dad_fishing_scene()

            # After Dad's event, return focus to the son.
            fisherman_sequence = 4

        else:
            # Son gets the bite.
            son_gets_bite_scene()

            fisherman_sequence = 5

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return



    # # =========================================================
    # # SEQUENCE 4
    # #
    # # Dad just had his fishing event.
    # #
    # # Son and Dad have another short waiting conversation.
    # # Then the next press moves toward the son's bite.
    # # =========================================================

    if fisherman_sequence == 4:
        waiting_conversation()

        fisherman_sequence = 6

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 5
    # #
    # # Son already has the fish on.
    # #
    # # Now find out whether he catches it or loses it.
    # # =========================================================

    if fisherman_sequence == 5:
        son_fish_result_scene()

        fisherman_sequence = 7

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 6
    # #
    # # After Dad's event, it is now definitely the son's turn
    # # to get a bite.
    # # =========================================================

    if fisherman_sequence == 6:
        son_gets_bite_scene()

        fisherman_sequence = 5

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SEQUENCE 7
    # #
    # # Son finished his fish event.
    # #
    # # Have one more casual fishing conversation before
    # # beginning another cycle.
    # # =========================================================

    if fisherman_sequence == 7:
        waiting_conversation()

        # Most of the time keep fishing without repeating
        # the teaching-to-cast section.
        #
        # Occasionally start the entire story over.

        restart = random.choice([
            False,
            False,
            False,
            True
        ])

        if restart:
            fisherman_sequence = 0
        else:
            fisherman_sequence = 2

        print("Fly Fisherman stopped at sequence:", fisherman_sequence)
        return


    # # =========================================================
    # # SAFETY
    # #
    # # If fisherman_sequence ever contains an invalid value,
    # # reset the story.
    # =========================================================


    fisherman_sequence = 0

    print("Invalid sequence - resetting Fly Fisherman")


def an():
    fly_fisherman_dialog()
    
def cast_motion(fisherman_index):
    print("fisherman: ",fisherman_index)
    move_at_speed(fisherman_index, cfg["wiggle_pos"], cfg["gentle_speed"])
    cyc = random.randint(cfg["wiggle_cycles_low"], cfg["wiggle_cycles_high"])
    s_1_wiggle_movement(fisherman_index, cfg["wiggle_pos"], cyc, cfg["wiggle_speed"])
    time.sleep(.1)
    move_at_speed(fisherman_index, cfg["cast_pos"], cfg["cast_speed"])

def show_mode(cycles):
    middle_point = int((cfg["wiggle_pos"]+cfg["cast_pos"])/2)
    show_mode_spd = 0.01
    move_at_speed(0, cfg["cast_pos"], cfg["wiggle_speed"])
    for _ in range(cycles):
        move_at_speed(0, middle_point, show_mode_spd)
        move_at_speed(0, cfg["cast_pos"], show_mode_spd)


def show_timer_mode():
    if cfg["timer"] == True:
        show_mode(2)
    else:
        show_mode(1)


def show_timer_program_option(cycles):
    middle_point = int((cfg["wiggle_pos"]+cfg["cast_pos"])/2)
    middle_point = int((middle_point+cfg["cast_pos"])/2)
    move_at_speed(0, cfg["cast_pos"], cfg["wiggle_speed"])
    for _ in range(cycles):
        move_at_speed(0, middle_point, cfg["wiggle_speed"])
        move_at_speed(0, cfg["cast_pos"], cfg["wiggle_speed"])

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
        ply_a_0(mvc_folder+"animations_are_now_active.mp3")
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        sw = utilities.switch_state_trigger(
            top_sw, bot_sw, trig_sw, time.sleep, 3.0)
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
            if sw == "trigger":
                an()
                print("an done")
        elif sw == "left":
            an()
            print("an done")
        elif sw == "trigger":
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
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        ply_a_0(mvc_folder + "main_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw_st = utilities.switch_state_trigger(
            top_sw, bot_sw, trig_sw, time.sleep, 3.0)
        if sw_st == "left":
            ply_a_0(mvc_folder + "" + main_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw_st == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "timer_settings":
                mch.go_to('timer_settings')
            elif sel_mnu == "volume_settings":
                mch.go_to('volume_settings')
            else:
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')

class TimerSet(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "timer_settings"

    def enter(self, mch):
        files.log_item("timer_settings_menu")
        ply_a_0(mvc_folder + "timer_settings_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        sw_st = utilities.switch_state_trigger(
            top_sw, bot_sw, trig_sw, time.sleep, 3.0)
        if sw_st == "left":
            ply_a_0(mvc_folder + "" + timer_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(timer_m)-1:
                self.i = 0
        if sw_st == "right":
            sel_i = timer_m[self.sel_i]
            if sel_i == "timer_off":
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

class VolSet(Ste):

    def __init__(s):
        s.i = 0
        s.sel_i = 0
        s.vol_adj_mode = False

    @property
    def name(s):
        return 'volume_settings'

    def enter(s, mch):
        files.log_item('Set Web Options')
        ply_a_0(mvc_folder + "volume_settings_menu.mp3")
        l_r_but()
        s.vol_adj_mode = False
        Ste.enter(s, mch)

    def exit(s, mch):
        Ste.exit(s, mch)

    def upd(s, mch):
        sw_st = utilities.switch_state_trigger(
            top_sw, bot_sw, trig_sw, time.sleep, 3.0)
        if sw_st == "left" and not s.vol_adj_mode:
            ply_a_0(mvc_folder + "" + vol_set_m[s.i] + ".mp3")
            s.sel_i = s.i
            s.i += 1
            if s.i > len(vol_set_m)-1:
                s.i = 0
        if vol_set_m[s.sel_i] == "volume_level_adjustment" and not s.vol_adj_mode:
            if sw_st == "right":
                s.vol_adj_mode = True
                ply_a_0(mvc_folder + "volume_adjustment_menu.mp3")
        elif sw_st == "left" and s.vol_adj_mode:
            ch_vol("lower")
        elif sw_st == "right" and s.vol_adj_mode:
            ch_vol("raise")
        elif sw_st == "right_held" and s.vol_adj_mode:
            files.write_json_file("cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.mp3")
            s.vol_adj_mode = False
            mch.go_to('base_state')
            upd_vol(0.1)
        if sw_st == "right" and vol_set_m[s.sel_i] == "volume_pot_off":
            cfg["volume_pot"] = False
            if cfg["volume"] == 0:
                cfg["volume"] = 10
            files.write_json_file("cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.mp3")
            mch.go_to('base_state')
        if sw_st == "right" and vol_set_m[s.sel_i] == "volume_pot_on":
            cfg["volume_pot"] = True
            files.write_json_file("cfg.json", cfg)
            ply_a_0(mvc_folder + "all_changes_complete.mp3")
            mch.go_to('base_state')


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(TimerSet())
st_mch.add(VolSet())

sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 6.0)
if sw == "left_held":  # top switch counter clockwise
    cfg["cast_pos"] = 0
    files.write_json_file("cfg.json", cfg)
    show_mode(4)
elif sw == "right_held":  # top switch clockwise
    cfg["cast_pos"] = 180
    files.write_json_file("cfg.json", cfg)
    show_mode(4)
else:
    aud_en.value = True
    move_at_speed(0, cfg["wiggle_pos"], cfg["gentle_speed"])
    time.sleep(5)

st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")


while True:
    st_mch.upd()
    time.sleep(0.01)

