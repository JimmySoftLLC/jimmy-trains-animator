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


def f_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


################################################################################
# config variables

bigfoot_folder = "bigfoot/"
mvc_folder = "mvc/"
intro_folder = "intro/"
ending_folder = "ending/"

cfg = files.read_json_file("/cfg.json")

rand_timer = 0
srt_t = time.monotonic()
current_setting = "hidden"
async_running = False

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

prev_pos_arr = [cfg["hidden"], cfg["forward"]]

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

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=2, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

################################################################################
# misc methods


def rnd_prob(random_value):
    print("Using random value: " + str(random_value))
    if random_value == 0:
        return False
    elif random_value == 1:
        return True
    else:
        y = random.random()
        if y < random_value:
            return True
    return False


################################################################################
# Servo methods


def move_at_speed(n, new_position, speed, function_to_run = None):
    global prev_pos_arr
    if function_to_run:
        function_to_run
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
        ply_a_0(mvc_folder + "volume.wav")
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
        w0 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)

    # Play the selected file
    mix.voice[0].play(w0, loop=repeat)

    # Wait until playback completes
    if wait:
        while mix.voice[0].playing:
            upd_vol(0.1)
            pass


def ply_a_1(file_name, wait=True, repeat=False):
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
        w1 = audiocore.WaveFile(open(file_name, "rb"))
    else:
        raise ValueError("Unsupported audio format: " + file_name)

    # Play the selected file
    mix.voice[1].play(w1, loop=repeat)

    # Wait until playback completes
    if wait:
        while mix.voice[1].playing:
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
            ply_a_0(mvc_folder + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        ply_a_0(mvc_folder + "dot.wav")
        ply_a_0(mvc_folder + "local.wav")


def l_r_but():
    ply_a_0(mvc_folder + "press_left_button_right_button.wav")


def sel_web():
    ply_a_0(mvc_folder + "web_menu.wav")
    l_r_but()


def opt_sel():
    ply_a_0(mvc_folder + "option_selected.wav")


def spk_sng_num(song_number):
    ply_a_0(mvc_folder + "song.wav")
    spk_str(song_number, False)


def spk_web():
    ply_a_0(mvc_folder + "animator_available_on_network.wav")
    ply_a_0(mvc_folder + "to_access_type.wav")
    try:
        if cfg["HOST_NAME"] == "neo-pico":
            ply_a_0(mvc_folder + "neo_dash_pico.wav")
            ply_a_0(mvc_folder + "dot.wav")
            ply_a_0(mvc_folder + "local.wav")
        else:
            spk_str(cfg["HOST_NAME"], True)
        ply_a_0(mvc_folder + "in_your_browser.wav")
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


def play_random_file(folder_to_search, file_ext, wait):
    filename = get_random_media_file(folder_to_search, file_ext)
    if not filename:
        return
    filename = filename + "." + file_ext
    full_path = folder_to_search + filename

    print("Filename is:", full_path)
    ply_a_1(full_path, wait)


def bigfoot_sound(wait):
    play_random_file(bigfoot_folder, "mp3", wait)

def intro_sound(wait):
    play_random_file(intro_folder, "mp3", wait)

def ending_sound(wait):
    play_random_file(ending_folder, "mp3", wait)

################################################################################
# async methods


loop = asyncio.get_event_loop()


async def move_at_speed_async(n, new_position, speed):
    global prev_pos_arr, async_running
    sign = 1
    if prev_pos_arr[n] > new_position:
        sign = - 1
    for servo_pos in range(prev_pos_arr[n], new_position, sign):
        if not async_running:
            return
        m_servo(n, servo_pos)
        await asyncio.sleep(speed)
    m_servo(n, new_position)


async def walking_swagger(n, center_pt, spd, wiggle_amount):
    global async_running
    while async_running:
        await move_at_speed_async(n, center_pt-wiggle_amount, spd)
        if not async_running:
            return
        await move_at_speed_async(n, center_pt+wiggle_amount, spd)
        if not async_running:
            return


async def walking(n, destination, spd,):
    global async_running
    await move_at_speed_async(n, destination, spd)
    async_running = False


async def swagger_walk(figure_location, figure_rotation, function_to_run = False):
    global async_running, cfg
    if function_to_run:
        function_to_run
    async_running = True
    walk_swag_f = asyncio.create_task(walking_swagger(1, figure_rotation,
                                                      cfg["swagger_speed"], cfg["swagger"]))
    walk_f = asyncio.create_task(
        walking(0, figure_location, cfg["walking_speed"]))
    await asyncio.gather(walk_f, walk_swag_f)


def an():
    intro_sound(True)
    if rnd_prob(.6):  # come all the way out
        asyncio.run(swagger_walk(cfg["visible"], cfg["forward"], bigfoot_sound(False)))
        rand_timer = random.uniform(1.0, 5.0)
        time.sleep(rand_timer)
        move_at_speed(1, cfg["backward"], cfg["turning_speed"])
        if rnd_prob(.4):
            rand_timer = random.uniform(1.0, 5.0)
            time.sleep(rand_timer)
            move_at_speed(1, cfg["forward"], cfg["staring_speed"], bigfoot_sound(False))
            rand_timer = random.uniform(1.0, 5.0)
            time.sleep(rand_timer)
            move_at_speed(1, cfg["backward"], cfg["turning_speed"])
            asyncio.run(swagger_walk(cfg["hidden"], cfg["backward"]))
        else:
            asyncio.run(swagger_walk(cfg["hidden"], cfg["backward"],bigfoot_sound(False)))
        ending_sound(True)
        move_at_speed(1, cfg["forward"], cfg["turning_speed"])
    else:  # peek to see if someone is there
        peek_pos = int((cfg["visible"]-cfg["hidden"])
                       * cfg["peek"]+cfg["hidden"])
        asyncio.run(swagger_walk(peek_pos, cfg["peek_rotation"]))
        rand_timer = random.uniform(1.0, 5.0)
        time.sleep(rand_timer)
        move_at_speed(1, cfg["backward"], cfg["turning_speed"])
        asyncio.run(swagger_walk(cfg["hidden"], cfg["backward"]))
        move_at_speed(1, cfg["forward"], cfg["turning_speed"])


################################################################################
# animations

def show_mode(cycles, stay_at_middle=False):
    middle_point = int((cfg["visible"]+cfg["hidden"])/2)
    show_mode_point = int((middle_point+cfg["visible"])/2)
    show_mode_spd = 0.04
    move_at_speed(0, middle_point, show_mode_spd)
    time.sleep(1)
    for _ in range(cycles):
        move_at_speed(0, show_mode_point, show_mode_spd)
        move_at_speed(0, middle_point, show_mode_spd)
    if not stay_at_middle:
        time.sleep(1)
        move_at_speed(0, cfg["hidden"], cfg["walking_speed"])


def show_timer_mode():
    if cfg["timer"] == True:
        show_mode(2)
    else:
        show_mode(1)


def show_timer_program_option(cycles):
    middle_point = int((cfg["forward"]+cfg["backward"])/2)
    show_mode_point = int((middle_point+cfg["forward"])/2)
    move_at_speed(1, cfg["forward"], cfg["turning_speed"])
    for _ in range(cycles):
        move_at_speed(1, show_mode_point, cfg["turning_speed"])
        move_at_speed(1, cfg["forward"], cfg["turning_speed"])


def ch_servo(n, setting, action):
    s = cfg[setting]
    if action == "lower":
        s -= 1
    elif action == "raise":
        s += 1
    if s > 180:
        s = 100
    if s < 0:
        s = 0
    cfg[setting] = s
    print(s)
    move_at_speed(n, cfg[setting], cfg["turning_speed"])

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
        return "main_menu"

    def enter(self, mch):
        files.log_item("Main menu")
        show_mode(3, True)
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer, srt_t
        top_sw.update()
        bot_sw.update()
        if top_sw.fell:
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m) - 1:
                self.i = 0
            print(main_m[self.sel_i])
            show_timer_program_option(self.sel_i+1)
        if bot_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "exit_this_menu":
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


class ServoSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "servo_settings"

    def enter(self, mch):
        files.write_json_file("cfg.json", cfg)
        show_mode(4, True)
        if current_setting == "hidden":
            cfg[current_setting] = cfg["hidden_default"]
            move_at_speed(0, cfg["hidden"], cfg["walking_speed"])
        else:
            cfg[current_setting] = cfg["visible_default"]
            move_at_speed(0, cfg["visible"], cfg["walking_speed"])
        files.log_item("Set " + current_setting + " servo settings")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global current_setting
        top_sw.update()
        bot_sw.update()
        done = False
        while not done:
            sw = utilities.switch_state_trigger(
                top_sw, bot_sw, trig_sw, time.sleep, 3.0)
            if sw == "left":
                ch_servo(0, current_setting, "raise")
            elif sw == "right":
                ch_servo(0, current_setting, "lower")
            elif sw == "right_held" and current_setting == "hidden":
                files.write_json_file("cfg.json", cfg)
                move_at_speed(1, cfg["forward"], cfg["turning_speed"])
                move_at_speed(0, cfg["hidden"], cfg["walking_speed"])
                done = True
                current_setting = "visible"
                mch.go_to("servo_settings")
                pass
            elif sw == "right_held" and current_setting == "visible":
                files.write_json_file("cfg.json", cfg)
                move_at_speed(1, cfg["forward"], cfg["turning_speed"])
                move_at_speed(0, cfg["hidden"], cfg["walking_speed"])
                done = True
                mch.go_to("base_state")
            pass


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(ServoSet())


sw = utilities.switch_state(top_sw, bot_sw, time.sleep, 6.0)
if sw == "left_held":  # left switch visible settings
    current_setting = "hidden"
    st_mch.go_to("servo_settings")
else:  # initialize figures in correct position
    move_at_speed(1, cfg["forward"], cfg["turning_speed"])
    move_at_speed(0, cfg["hidden"], cfg["walking_speed"])
    st_mch.go_to("base_state")
    files.log_item("animator has started...")
    gc_col("animations started")
    aud_en.value = True
    ply_a_0(mvc_folder+"animations_are_now_active.mp3")

while True:
    st_mch.upd()
    time.sleep(0.01)
