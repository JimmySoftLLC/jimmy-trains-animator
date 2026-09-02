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

#######################################################

from trolley_controller import TrolleyController
import utilities
from adafruit_debouncer import Debouncer
import neopixel
from rainbowio import colorwheel
from analogio import AnalogIn
import asyncio
from adafruit_motor import motor
import pwmio
import microcontroller
import rtc
import random
import board
import digitalio
import busio
import audiomp3
import audiomixer
import audiobusio
import time
import gc
import files
import os
import audiocore
import sdcardio
import storage


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def f_exists(filename):
    try:
        status = os.stat(filename)
        f_exists = True
    except OSError:
        f_exists = False
    return f_exists


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")

################################################################################
# Globals

animations_folder = "/sd/snds/"
mvc_folder = "/sd/mvc/"

elves_folder = "elves/"
bells_folder = "bells/"
horns_folder = "horns/"
stops_folder = "stops/"
santa_folder = "santa/"
story_folder = "story/"

FOLDER_MAP = {
    'E': elves_folder,
    'B': bells_folder,
    'H': horns_folder,
    'T': stops_folder,
    'S': santa_folder,
    'C': story_folder
}

media_index = {'E': 0, 'B': 0, 'H': 0, 'T': 0, 'S': 0, 'C': 0}

################################################################################
# Setup hardware

# Setup pin for v
a_in = AnalogIn(board.A0)

track_a_in = AnalogIn(board.A2)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

# Setup the switches
l_sw_io = digitalio.DigitalInOut(board.GP6)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(lambda: not l_sw_io.value)

r_sw_io = digitalio.DigitalInOut(board.GP7)
r_sw_io.direction = digitalio.Direction.INPUT
r_sw_io.pull = digitalio.Pull.UP
r_sw = Debouncer(lambda: not r_sw_io.value)


# setup i2s audio
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

aud_en.value = True

# Setup the mixer to play mp3 files
mix = audiomixer.Mixer(
    voice_count=2,
    sample_rate=22050,
    channel_count=2,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=16384,
)
aud.play(mix)

mix.voice[0].level = .2
mix.voice[1].level = .2

aud_en.value = True
try:
    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
except Exception as e:
    files.log_item(e)
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[1].play(w0, loop=False)
    while mix.voice[1].playing:
        pass
    card_in = False
    while not card_in:
        l_sw.update()
        if l_sw.fell:
            try:
                sd = sdcardio.SDCard(spi, cs)
                vfs = storage.VfsFat(sd)
                storage.mount(vfs, "/sd")
                card_in = True
                w0 = audiocore.WaveFile(
                    open(mvc_folder + "micro_sd_card_success.wav", "rb"))
                mix.voice[1].play(w0, loop=False)
                while mix.voice[1].playing:
                    pass
            except Exception as e:
                files.log_item(e)
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[1].play(w0, loop=False)
                while mix.voice[1].playing:
                    pass

aud_en.value = False

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Flash data

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = []
menu_snd_opt = []
ts_jsons = []


def upd_media():
    global snd_opt, menu_snd_opt, ts_jsons

    snd_opt = files.return_directory("", animations_folder, ".json")

    menu_snd_opt = []
    menu_snd_opt.extend(snd_opt)
    rnd_opt = ['random all']
    menu_snd_opt.extend(rnd_opt)

    ts_jsons = files.return_directory("", "/sd/t_s_def", ".json")


upd_media()

web = cfg["serve_webpage"]

cfg_main = files.read_json_file(mvc_folder + "main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(mvc_folder + "web_menu.json")
web_m = cfg_web["web_menu"]

cfg_add_song = files.read_json_file(mvc_folder +
                                    "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cfg_bump_set = files.read_json_file(mvc_folder +
                                    "bumper_settings.json")
bump_set = cfg_bump_set["bumper_settings"]


local_ip = ""

ovrde_sw_st = {}
ovrde_sw_st["switch_value"] = ""

gc_col("config setup")

ts_mode = False

flsh_i = 0
flsh_t = []

t_s = []
t_elsp = 0.0

an_running = False
an_just_added = False

################################################################################
# Setup neo pixels

n_px = 13

# 16 on demo, 17 tiny, 10 on large, 13 on motor board motor4 pin
led = neopixel.NeoPixel(board.GP13, n_px)
led.auto_write = False
led.fill((20, 20, 20))
led.show()

gc_col("Neopixels setup")

################################################################################
# Dialog and sound play methods


def upd_vol(s, bckgrnd_ratio=None):
    global bckgrnd_vol

    if bckgrnd_ratio is not None:
        bckgrnd_vol = bckgrnd_ratio

    if bckgrnd_vol > 100:
        bckgrnd_vol = 100

    if bckgrnd_vol < 0:
        bckgrnd_vol = 0

    try:
        volume = int(cfg["volume"]) / 100
        bckgrnd_volume = volume * (bckgrnd_vol / 100)
    except Exception as e:
        files.log_item(e)
        volume = .5
        bckgrnd_volume = .5

    if volume < 0 or volume > 1:
        volume = .5

    if bckgrnd_volume < 0 or bckgrnd_volume > 1:
        bckgrnd_volume = .5

    mix.voice[0].level = bckgrnd_volume
    mix.voice[1].level = volume

    time.sleep(s)


async def upd_vol_async(s, bckgrnd_ratio=None):
    global bckgrnd_vol

    if bckgrnd_ratio is not None:
        bckgrnd_vol = bckgrnd_ratio

    if bckgrnd_vol > 100:
        bckgrnd_vol = 100

    if bckgrnd_vol < 0:
        bckgrnd_vol = 0

    try:
        volume = int(cfg["volume"]) / 100
        bckgrnd_volume = volume * (bckgrnd_vol / 100)
    except Exception as e:
        files.log_item(e)
        volume = .5
        bckgrnd_volume = .5

    if volume < 0 or volume > 1:
        volume = .5

    if bckgrnd_volume < 0 or bckgrnd_volume > 1:
        bckgrnd_volume = .5

    mix.voice[0].level = bckgrnd_volume
    mix.voice[1].level = volume

    await asyncio.sleep(s)


async def upd_bckgrnd_throttle_async(actual_throttle, requested_throttle):
    if not bckgrnd_track_throttle:
        return

    actual_throttle = abs(actual_throttle)
    requested_throttle = abs(requested_throttle)

    if requested_throttle <= 0:
        await upd_vol_async(0, 0)
        return

    bckgrnd_ratio = actual_throttle / requested_throttle * 100

    if bckgrnd_ratio > 100:
        bckgrnd_ratio = 100

    if bckgrnd_ratio < 0:
        bckgrnd_ratio = 0

    await upd_vol_async(0, bckgrnd_ratio)


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
    if not mix.voice[0].playing:
        files.write_json_file("/sd/cfg.json", cfg)
        ply_a_0(mvc_folder + "volume.mp3")
        spk_str(cfg["volume"], False)


def ply_a_0(file_name, wait=True, repeat=False):
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
            exit_early()
            pass


def wait_snd():
    while mix.voice[0].playing:
        pass


async def wait_snd_1():
    while mix.voice[1].playing:
        if an_running:
            if await animation_wait(.01):
                return True
        else:
            await asyncio.sleep(0)

    return False


def stp_a_0():
    mix.voice[0].stop()
    wait_snd()


async def stp_a_1():
    mix.voice[1].stop()
    await wait_snd_1()


def exit_early():
    upd_vol(0)

    if an_running:
        animation_wait(.1)
        return

    time.sleep(.1)

    l_sw.update()

    if l_sw.fell:
        mix.voice[0].stop()


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


def sel_bumper():
    ply_a_0(mvc_folder + "bumper_settings_menu.mp3")
    l_r_but()


def opt_sel():
    ply_a_0(mvc_folder + "option_selected.mp3")


def spk_sng_num(song_number):
    ply_a_0(mvc_folder + "song.mp3")
    spk_str(song_number, False)


async def no_trk():
    ply_a_0(mvc_folder + "no_user_soundtrack_found.mp3")
    while True:
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        l_sw.update()
        r_sw.update()
        if sw == "left":
            break
        if sw == "right":
            ply_a_0(mvc_folder + "create_sound_track_files.mp3")
            break
        await asyncio.sleep(.1)


def spk_web():
    ply_a_0(mvc_folder + "animator_available_on_network.mp3")
    ply_a_0(mvc_folder + "to_access_type.mp3")
    if cfg["HOST_NAME"] == "animator-trolley":
        ply_a_0(mvc_folder + "animator_trolley.mp3")
        ply_a_0(mvc_folder + "dot.mp3")
        ply_a_0(mvc_folder + "local.mp3")
    else:
        spk_str(cfg["HOST_NAME"], True)
    ply_a_0(mvc_folder + "in_your_browser.mp3")


def get_snds(dir, typ):
    sds = []
    s = files.return_directory("", dir, ".mp3")
    for el in s:
        p = el.split('_')
        if p[0] == typ:
            sds.append(el)
    mx = len(sds) - 1
    i = random.randint(0, mx)
    fn = dir + "/" + sds[i] + ".mp3"
    return fn


################################################################################
# Setup motor controller
p_frq = 10000  # Custom PWM frequency in Hz; PWMOut min/max 1Hz/50kHz, default is 500Hz
d_mde = motor.SLOW_DECAY  # Set controller to Slow Decay (braking) mode

# DC motor setup; Set pins to custom PWM frequency, 17 16 on incline, 0 1 on demo
pwm_a = pwmio.PWMOut(board.GP17, frequency=p_frq)
pwm_b = pwmio.PWMOut(board.GP16, frequency=p_frq)
train = motor.DCMotor(pwm_a, pwm_b)
train.decay_mode = d_mde
train.throttle = 0
current_throttle = 0


controller = TrolleyController(
    train,
    l_sw_io,
    r_sw_io,
    ramp_start_ratio=0.7,
    min_throttle=0.12,
    off_bumper_time=0.3,
    ramp_steps=3,
)

bumper_direction = 1
bumper_requested_throttle = 0.0
bumper_progress = 0.0
bumper_last_time = time.monotonic()
bumper_calibrated = False

bumper_target_position = None
bumper_positioning = False
bumper_position_success = False

BUMPER_BACKOFF_SPEED = 0.12
BUMPER_RELEASE_TIME = 0.15
BUMPER_BACKOFF_TIMEOUT = 2.0
POS_RAMP_DISTANCE = 0.12
POS_MIN_SPEED = 0.10

virtual_position = 50.0
VIRTUAL_FULL_TRAVEL_MIN = 8.0
VIRTUAL_FULL_TRAVEL_MAX = 12.0
VIRTUAL_REFERENCE_SPEED = 20.0
VIRTUAL_ACCELERATION = 2


def calibrate_bumper():
    global bumper_direction, bumper_requested_throttle, bumper_progress, bumper_last_time, bumper_calibrated
    global bumper_target_position, bumper_positioning, bumper_position_success

    bumper_direction = 1
    bumper_requested_throttle = 0.0
    bumper_progress = 0.0
    bumper_last_time = time.monotonic()
    bumper_calibrated = False

    bumper_target_position = None
    bumper_positioning = False
    bumper_position_success = False

    print("Calibrating...")

    ply_a_0(mvc_folder + "bumper_cal_starting.mp3")

    bumper_calibrated = controller.calibrate(speed=0.2, cycles=3)

    if bumper_calibrated:
        bumper_direction = 1

        if controller.time_forward:
            bumper_progress = controller.off_bumper_time / controller.time_forward
        else:
            bumper_progress = 0.0

        print("Bumper calibration complete")
        print("Forward time:", controller.time_forward)
        print("Reverse time:", controller.time_reverse)
        print("Starting position:", int(bumper_progress * 100), "%")

        ply_a_0(mvc_folder + "the_calibration_was_successful.mp3")

    else:
        print("Bumper calibration failed")


async def set_bumper_speed(target_throttle, acceleration=None):
    global bumper_requested_throttle

    target_throttle = abs(target_throttle)

    if target_throttle > 100:
        target_throttle = 100

    if acceleration is None or acceleration <= 0:
        bumper_requested_throttle = target_throttle / 100
        await asyncio.sleep(0)
        return False

    target = target_throttle / 100
    step = acceleration / 100

    while bumper_requested_throttle != target:
        if bumper_requested_throttle < target:
            bumper_requested_throttle = min(
                bumper_requested_throttle + step, target)
        else:
            bumper_requested_throttle = max(
                bumper_requested_throttle - step, target)

        if an_running:
            if await animation_wait(.02):
                return True
        else:
            await asyncio.sleep(.02)

    return False


async def back_off_bumper(hit_direction):
    global current_throttle

    backoff_speed = BUMPER_BACKOFF_SPEED

    if backoff_speed <= 0:
        backoff_speed = 0.12

    train.throttle = -hit_direction * backoff_speed
    current_throttle = int(train.throttle * 100)

    backoff_start = time.monotonic()
    clear_start = None

    while True:
        now = time.monotonic()

        if hit_direction > 0:
            bumper_active = r_sw_io.value
        else:
            bumper_active = l_sw_io.value

        if bumper_active:
            clear_start = None
        else:
            if clear_start is None:
                clear_start = now

            elif now - clear_start >= BUMPER_RELEASE_TIME:
                break

        if now - backoff_start >= BUMPER_BACKOFF_TIMEOUT:
            print("Bumper backoff timeout")
            break

        await asyncio.sleep(0)

    elapsed = time.monotonic() - backoff_start

    return elapsed, backoff_speed


async def position_trolley_virtual(speed, percentage):
    global virtual_position, current_throttle

    speed = abs(speed)

    if speed > 100:
        speed = 100

    if speed <= 0:
        print("Virtual POS speed must be greater than 0")
        return False

    if percentage < 0 or percentage > 100:
        print("Virtual POS position must be between 0 and 100")
        return False

    distance = abs(percentage - virtual_position)

    print("Virtual POS command")
    print("Speed:", speed)
    print("Virtual current position:", int(virtual_position))
    print("Virtual target position:", percentage)
    print("Virtual distance:", int(distance), "%")

    if distance <= 1:
        await set_hdw_async("TA_0_" + str(VIRTUAL_ACCELERATION), 0)
        virtual_position = float(percentage)
        print("Already at virtual position")
        return True

    if percentage > virtual_position:
        direction = 1
        print("Virtual POS traveling FORWARD")
    else:
        direction = -1
        print("Virtual POS traveling REVERSE")

    full_travel_time = random.uniform(VIRTUAL_FULL_TRAVEL_MIN, VIRTUAL_FULL_TRAVEL_MAX)

    speed_ratio = VIRTUAL_REFERENCE_SPEED / speed
    distance_ratio = distance / 100.0

    travel_time = full_travel_time * distance_ratio * speed_ratio

    if travel_time < 0.25:
        travel_time = 0.25

    print("Virtual full travel time:", full_travel_time)
    print("Virtual travel time:", travel_time)

    target_throttle = int(speed) * direction

    result = await set_hdw_async("TA_" + str(target_throttle) + "_" + str(VIRTUAL_ACCELERATION), 0)

    if result == "STOP":
        return False

    if an_running:
        if await animation_wait(travel_time):
            await set_hdw_async("TA_0_" + str(VIRTUAL_ACCELERATION), 0)
            return False
    else:
        await asyncio.sleep(travel_time)

    result = await set_hdw_async("TA_0_" + str(VIRTUAL_ACCELERATION), 0)

    if result == "STOP":
        return False

    virtual_position = float(percentage)

    print("Virtual POS complete:", percentage, "%")

    return True


async def position_trolley(speed, percentage):
    global bumper_direction, bumper_requested_throttle
    global bumper_target_position, bumper_positioning, bumper_position_success
    global current_throttle

    speed = abs(speed)

    if speed > 100:
        speed = 100

    if speed <= 0:
        print("POS speed must be greater than 0")
        return False

    if percentage < 0 or percentage > 100:
        print("POS position must be between 0 and 100")
        return False

    if not cfg["bumper_mode"] or not bumper_calibrated:
        return await position_trolley_virtual(speed, percentage)

    target = percentage / 100

    print("POS command")
    print("Speed:", speed)
    print("Current position:", int(bumper_progress * 100))
    print("Target position:", percentage)

    if percentage == 0:
        bumper_direction = -1
        bumper_target_position = 0.0
        bumper_positioning = True
        bumper_position_success = False
        bumper_requested_throttle = speed / 100
        print("POS homing LEFT")

    elif percentage == 100:
        bumper_direction = 1
        bumper_target_position = 1.0
        bumper_positioning = True
        bumper_position_success = False
        bumper_requested_throttle = speed / 100
        print("POS homing RIGHT")

    else:
        if abs(bumper_progress - target) <= 0.01:
            train.throttle = 0
            current_throttle = 0
            bumper_requested_throttle = 0.0
            print("Already at requested position")
            return True

        if target > bumper_progress:
            bumper_direction = 1
            print("POS traveling RIGHT")
        else:
            bumper_direction = -1
            print("POS traveling LEFT")

        bumper_target_position = target
        bumper_positioning = True
        bumper_position_success = False
        bumper_requested_throttle = speed / 100

    while bumper_positioning:
        if an_running:
            if await animation_wait(.01):
                bumper_target_position = None
                bumper_positioning = False
                bumper_position_success = False
                bumper_requested_throttle = 0.0

                train.throttle = 0
                current_throttle = 0

                return False

        else:
            await asyncio.sleep(0)

    if bumper_position_success:
        print("POS complete:", percentage, "%")
        return True

    print("POS did not reach destination")

    return False


################################################################################
# Setup wifi and web server

if (web):
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    gc_col("config wifi imports")

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except:
        print("Using default ssid and password")

    for i in range(3):
        web = True
        led[0] = (0, 0, 255)
        led.show()
        try:
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            gc_col("wifi connect")

            mdns = mdns.Server(wifi.radio)
            mdns.hostname = cfg["HOST_NAME"]
            mdns.advertise_service(
                service_type="_http", protocol="_tcp", port=80)

            local_ip = str(wifi.radio.ipv4_address)

            files.log_item("IP is " + local_ip)
            files.log_item("Connected")

            pool = socketpool.SocketPool(wifi.radio)
            server = Server(pool, "/static", debug=True)
            server.port = 80  # Explicitly set port to 80

            gc_col("wifi server")

            ################################################################################
            # Setup routes

            @server.route("/")
            def base(req: HTTPRequest):
                return FileResponse(req, "index.html", "/")

            @server.route("/mui.min.css")
            def base(req: HTTPRequest):
                return FileResponse(req, "mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(req: HTTPRequest):
                return FileResponse(req, "mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(request: Request):
                rq_d = request.json()
                cfg["option_selected"] = rq_d["an"]
                add_cmd("AN_" + cfg["option_selected"])
                if not mix.voice[0].playing:
                    files.write_json_file("/sd/cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("/sd/cfg.json", cfg)
                    ply_a_0(mvc_folder + "all_changes_complete.mp3")
                    st_mch.go_to('base_state')
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/mode", [POST])
            def btn(request: Request):
                global ts_mode
                rq_d = request.json()
                if rq_d["an"] == "left":
                    ovrde_sw_st["switch_value"] = "left"
                elif rq_d["an"] == "left_held":
                    ovrde_sw_st["switch_value"] = "left_held"
                elif rq_d["an"] == "right":
                    ovrde_sw_st["switch_value"] = "right"
                elif rq_d["an"] == "right_held":
                    ovrde_sw_st["switch_value"] = "right_held"
                elif rq_d["an"] == "three":
                    ovrde_sw_st["switch_value"] = "three"
                elif rq_d["an"] == "four":
                    ovrde_sw_st["switch_value"] = "four"
                elif rq_d["an"] == "cont_mode_on":
                    stop_all_cmds()
                    ply_a_0(mvc_folder + "continuous_mode_activated.mp3")
                    cfg["cont_mode"] = True
                    files.write_json_file("/sd/cfg.json", cfg)
                elif rq_d["an"] == "cont_mode_off":
                    stop_all_cmds()
                    ply_a_0(mvc_folder + "continuous_mode_deactivated.mp3")
                    cfg["cont_mode"] = False
                    files.write_json_file("/sd/cfg.json", cfg)
                elif rq_d["an"] == "timestamp_mode_on":
                    stop_all_cmds()
                    ts_mode = True
                    ply_a_0(mvc_folder + "timestamp_mode_on.mp3")
                    ply_a_0(mvc_folder + "timestamp_instructions.mp3")
                elif rq_d["an"] == "timestamp_mode_off":
                    stop_all_cmds()
                    ts_mode = False
                    ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/speaker", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                if rq_d["an"] == "speaker_test":
                    ply_a_0(mvc_folder + "left_speaker_right_speaker.mp3")
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/lights", [POST])
            def btn(request: Request):
                rq_d = request.json()
                command = rq_d["an"]
                add_command_to_ts(command)
                set_hdw_lights(command)
                return Response(request, "Utility: " + "Utility: set lights")

            @server.route("/set-item-lights", [POST])
            def btn(request: Request):
                rq_d = request.json()
                command = "LN0_" + str(rq_d["r"]) + "_" + \
                    str(rq_d["g"]) + "_" + str(rq_d["b"])
                add_command_to_ts(command)
                set_hdw_lights(command)
                return Response(request, "Utility: " + "Utility: set lights")

            @server.route("/get-wifi-signal", [POST])
            def get_local_ip(request: Request):
                avg_rssi = measure_signal_strength(WIFI_SSID, 10)
                return Response(request, str(avg_rssi))

            @server.route("/get-track-voltage", [POST])
            def btn(request: Request):
                track_voltage = get_track_voltage()
                return Response(request, str(track_voltage))

            @server.route("/update-host-name", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                cfg["HOST_NAME"] = rq_d["an"]
                files.write_json_file("/sd/cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                spk_web()
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def btn(request: Request):
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def buttonpress(req: Request):
                return Response(req, local_ip)

            @server.route("/update-volume", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                ch_vol(rq_d["action"])
                files.write_json_file("/sd/cfg.json", cfg)
                return Response(request, cfg["volume"])

            @server.route("/get-volume", [POST])
            def btn(request: Request):
                return Response(request, cfg["volume"])

            @server.route("/get-throttle", [POST])
            def btn(request: Request):
                cur_throttle_str = str(current_throttle)
                print("sending current throttle: ", cur_throttle_str)
                return Response(request, cur_throttle_str)

            @server.route("/get-animations", [POST])
            def btn(request: Request):
                stop_all_cmds()
                sounds = []
                sounds.extend(snd_opt)
                my_string = files.json_stringify(sounds)
                return Response(request, my_string)

            @server.route("/create-animation", [POST])
            def btn(request: Request):
                stop_all_cmds()
                try:
                    global data, animations_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    print(rq_d)
                    f_n = animations_folder + rq_d["fn"] + ".json"
                    print(f_n)
                    an_data = ["0.0|MB0name of your track.wav", "1.0|"]
                    files.write_json_file(f_n, an_data)
                    upd_media()
                    return Response(request, "Created animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error creating animation.")

            @server.route("/rename-animation", [POST])
            def btn(request: Request):
                stop_all_cmds()
                try:
                    global data, animations_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    fo = animations_folder + rq_d["fo"] + ".json"
                    fn = animations_folder + rq_d["fn"] + ".json"
                    os.rename(fo, fn)
                    upd_media()
                    return Response(request, "Renamed animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/delete-animation", [POST])
            def btn(request: Request):
                stop_all_cmds()
                try:
                    global data, animations_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    print(rq_d)
                    f_n = animations_folder + rq_d["fn"] + ".json"
                    print(f_n)
                    os.remove(f_n)
                    upd_media()
                    return Response(request, "Delete animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/test-animation", [POST])
            def btn(request: Request):
                try:
                    rq_d = request.json()
                    add_cmd(rq_d["an"])
                    return Response(request, "success")
                except Exception as e:
                    print(e)
                    return Response(request, "error")

            @server.route("/get-animation", [POST])
            def btn(request: Request):
                stop_all_cmds()
                rq_d = request.json()
                snd_f = rq_d["an"]
                if (f_exists(animations_folder + snd_f + ".json") == True):
                    f_n = animations_folder + snd_f + ".json"
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "/t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")

            data = []

            @server.route("/save-data", [POST])
            def btn(request: Request):
                global data
                stop_all_cmds()
                rq_d = request.json()
                try:
                    if rq_d[0] == 0:
                        data = []
                    data.extend(rq_d[2])
                    if rq_d[0] == rq_d[1]:
                        f_n = animations_folder + \
                            rq_d[3] + ".json"
                        files.write_json_file(f_n, data)
                        data = []
                    upd_media()
                except Exception as e:
                    files.log_item(e)
                    data = []
                    return Response(request, "out of memory")
                return Response(request, "success")
            break
        except Exception as e:
            web = False
            files.log_item(e)
            led[0] = (0, 0, 75)
            led.show()

gc_col("web server")


def measure_signal_strength(MY_SSID, cycles):
    if not web:
        return 0
    print("Monitoring signal for:", MY_SSID)
    print("Showing current RSSI + running average (simple sum + count)\n")

    total_sum = 0.0
    count = 0

    while True:
        current_rssi = None
        found = False

        try:
            for network in wifi.radio.start_scanning_networks():
                if network.ssid == MY_SSID:
                    current_rssi = network.rssi
                    print(
                        f"{time.monotonic():.1f}s | {MY_SSID} → RSSI = {current_rssi} dBm", end="")
                    found = True
                    break

            wifi.radio.stop_scanning_networks()

            if found and current_rssi is not None:
                total_sum += current_rssi
                count += 1

                if count > 0:
                    avg_rssi = total_sum / count
                    print(f"   |   Avg ({count} readings): {avg_rssi:.1f} dBm")
                else:
                    print("   |   Avg: waiting...")
            else:
                print(
                    "   |   Could not see your SSID (hidden, out of range, or scan miss)")

        except Exception as e:
            print(f"Scan error: {e}")
            wifi.radio.stop_scanning_networks()  # cleanup on error

        time.sleep(0.1)
        if count > cycles:
            return avg_rssi


cycles = 10
avg_rssi = measure_signal_strength(WIFI_SSID, cycles)
print(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")

################################################################################
# Command queue
command_queue = []


def add_cmd(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        print("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        print("Command added to the end:", command)


async def process_cmd():
    while command_queue:
        cmd = command_queue.pop(0)
        print("Processing command:", cmd)
        if cmd[:2] == 'AN':
            cmd_split = cmd.split("_")
            clr_cmd_queue()
            if cmd_split[1] == "customers":
                await an_async(cmd_split[1]+"_"+cmd_split[2]+"_"+cmd_split[3]+"_"+cmd_split[4])
            else:
                await an_async(cmd_split[1])
        else:
            await set_hdw_async(cmd)
        await asyncio.sleep(0)


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_cmds():
    global exit_set_hdw_async, flsh_i, flsh_t
    flsh_i = len(flsh_t)-1
    if cfg["cont_mode"] == True:
        result = True
        cfg["cont_mode"] = False
    else:
        result = False
    mix.voice[0].stop()
    mix.voice[1].stop()
    clr_cmd_queue()
    exit_set_hdw_async = True
    print("Processing stopped and command queue cleared.")
    return result


async def animation_wait(wait_time):
    global an_running, bumper_requested_throttle, current_throttle, flsh_i, t_elsp

    start_time = time.monotonic()

    while time.monotonic() - start_time < wait_time:
        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0, ovrde_sw_st, False)

        if t_elsp > 2:
            track_voltage = get_track_voltage()
            if track_voltage < 9.0:
                sw = "left_held"

        if sw == "left_held":
            print("LEFT HELD - STOP ANIMATION")

            bumper_requested_throttle = 0.0
            train.throttle = 0
            current_throttle = 0

            result = stop_all_cmds()

            if result == True:
                ply_a_0(mvc_folder + "continuous_mode_deactivated.mp3")
                files.write_json_file("/sd/cfg.json", cfg)
            else:
                ply_a_0(mvc_folder + "animation_canceled.mp3")

            an_running = False
            return True

        await asyncio.sleep(0)

    return False


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)

################################################################################
# Misc Methods

def get_track_voltage(samples = 20):
    total = 0.0

    for _ in range(samples):
        total += track_a_in.value / 65536 * 3.3 * 15.684
        time.sleep(.0017)

    return total / samples

def rst_def():
    cfg["option_selected"] = "random all"
    cfg["cont_mode"] = False
    cfg["volume"] = "50"
    cfg["HOST_NAME"] = "animator-trolley"
    cfg["serve_webpage"] = True


################################################################################
# Animations

lst_opt = ""

async def an_async(f_nm):
    global lst_opt, ts_mode
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random all":
            h_i = len(snd_opt) - 1
            cur_opt = snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(snd_opt) > 1:
                cur_opt = snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            await an_ts(cur_opt)
        else:
            await an_light_async(cur_opt)
    except Exception as e:
        files.log_item(e)
        await no_trk()
        cfg["option_selected"] = "random all"
        return
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    global flsh_i, flsh_t, an_running, exit_set_hdw_async, t_elsp

    an_running = True

    stp_a_0()

    flsh_t = []

    if f_exists(animations_folder + f_nm + ".json") == True:
        flsh_t = files.read_json_file(animations_folder + f_nm + ".json")

    flsh_i = 0

    if flsh_i < len(flsh_t)-1:
        ft1 = flsh_t[flsh_i].split("|")
        result = await set_hdw_async(ft1[1])
        print("Result is: ", result)

        if result == "STOP":
            an_running = False
            return

        result = result.split("_")

        if result and len(result) > 1:
            w0_exists = f_exists(animations_folder + result[1])

            if w0_exists:
                if result[0] == "1":
                    repeat = True
                else:
                    repeat = False

                ply_a_0(animations_folder + result[1], False, repeat)

            else:
                an_running = False
                return

            srt_t = time.monotonic()

            ft1 = []
            ft2 = []

            ft_last = flsh_t[len(flsh_t)-1].split("|")
            tm_last = float(ft_last[0]) + .1
            flsh_t.append(str(tm_last) + "|")

        else:
            an_running = False
            return

        flsh_i += 1

    else:
        an_running = False
        return

    while True:
        t_elsp = time.monotonic()-srt_t

        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25

        else:
            dur = 0.25

        if dur < 0:
            dur = 0

        if t_elsp > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            files.log_item("time elapsed: " + str(t_elsp) +
                           " Timestamp: " + ft1[0] + " Command: " + ft1[1])

            if len(ft1) == 1 or ft1[1] == "":
                result = await set_hdw_async("", dur)

                if result == "STOP":
                    an_running = False
                    return

            else:
                result = await set_hdw_async(ft1[1], dur)

                if result == "STOP":
                    an_running = False
                    return

            flsh_i += 1

        if (not mix.voice[0].playing and w0_exists) or not flsh_i < len(flsh_t)-1:
            mix.voice[0].stop()
            mix.voice[1].stop()
            result = await set_hdw_async("TA_0_2", 0)
            result = await set_hdw_async("VR100", 0)
            an_running = False
            return

        upd_vol(0)

        if await animation_wait(.1):
            result = await set_hdw_async("TA_0_2", 0)
            result = await set_hdw_async("VR100", 0)
            return


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)


async def an_ts(f_nm):
    print("time stamp mode")
    global t_s, t_elsp, ts_mode, ovrde_sw_st

    t_elsp = 0
    t_s = [""]

    if (f_exists(animations_folder + f_nm + ".json") == True):
        t_s_from_file = files.read_json_file(
            animations_folder + f_nm + ".json")
    else:
        return

    if len(t_s) > 0:
        t_s[0] = t_s_from_file[0]
        ft1 = t_s[0].split("|")
        result = await set_hdw_async(ft1[1])
        print("Result is: ", result)
        result = result.split("_")
        if result and len(result) > 1:
            w0_exists = f_exists(animations_folder + result[1])
            if w0_exists:
                if result[0] == "1":
                    repeat = True
                else:
                    repeat = False
            else:
                return
            if w0_exists:
                file_name = animations_folder + result[1]
                if file_name.lower().endswith(".mp3"):
                    w0 = audiomp3.MP3Decoder(open(file_name, "rb"))
                elif file_name.lower().endswith(".wav"):
                    w0 = audiocore.WaveFile(open(file_name, "rb"))
                else:
                    raise ValueError("Unsupported audio format: " + file_name)
                add_command_to_ts("B0,ZCOLCH,F100,TA_30_1")
                mix.voice[0].play(w0, loop=repeat)
            else:
                return
        else:
            return
    else:
        return

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell or ovrde_sw_st["switch_value"]:
            add_command_to_ts("ZRAND")
            ovrde_sw_st["switch_value"] = ""
        if not mix.voice[0].playing:
            add_command_to_ts("B100,TA_0_1,F0,LN0_0_0_0,B100")
            led.fill((0, 0, 0))
            led.show()
            files.write_json_file(
                animations_folder + f_nm + ".json", t_s)
            break
        await asyncio.sleep(.1)

    ts_mode = False

    ply_a_0(mvc_folder + "timestamp_saved.mp3")
    ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
    ply_a_0(mvc_folder + "animations_are_now_active.mp3")


##############################
# animation effects

brightness = 0
bckgrnd_vol = 100
bckgrnd_track_throttle = False

e_media_file_index = 0
t_media_file_index = 0
c_media_file_index = 0
s_media_file_index = 0
h_media_file_index = 0


def set_hdw_lights(seg):
    global brightness

    # lights LNZZZ_R_G_B = Neo pixel lights ZZZ (0 All, 1 to 999) RGB 0 to 255
    if seg[:2] == 'LN':
        seg_split = seg.split("_")
        light_n = int(seg_split[0][2:])-1
        r = int(seg_split[1])
        g = int(seg_split[2])
        b = int(seg_split[3])
        set_neo_to(light_n, r, g, b)

    # BXXX = Brightness XXX 0 to 100
    elif seg[0] == 'B':
        brightness = int(seg[1:])
        led.brightness = float(brightness / 100)


async def set_hdw_async(cmd, dur=3):
    global brightness, current_throttle, media_index, exit_set_hdw_async, bumper_requested_throttle
    global bckgrnd_vol, bckgrnd_track_throttle

    if cmd == "":
        return "NOCMDS"

    segs = cmd.split(",")

    for seg in segs:
        if exit_set_hdw_async:
            return "STOP"

        # TA_XXX_AAA = Train XXX throttle -100 to 100 AAA acceleration increments 1 to 100
        if seg[:2] == 'TA':
            try:
                seg_split = seg.split("_")
                target_throttle = int(seg_split[1])
                acceleration = int(seg_split[2])

                if cfg["bumper_mode"]:
                    if await set_bumper_speed(target_throttle, acceleration):
                        return "STOP"

                else:
                    starting_throttle = abs(current_throttle)
                    requested_throttle = abs(target_throttle)

                    if requested_throttle <= 0:
                        requested_throttle = starting_throttle

                    diff = target_throttle - current_throttle

                    while diff != 0:
                        if diff > 0:
                            new_throttle = min(current_throttle + acceleration, target_throttle)
                        else:
                            new_throttle = max(current_throttle - acceleration, target_throttle)

                        train.throttle = new_throttle / 100
                        current_throttle = new_throttle

                        await upd_bckgrnd_throttle_async(current_throttle, requested_throttle)

                        diff = target_throttle - current_throttle

                        if an_running:
                            if await animation_wait(.02):
                                return "STOP"
                        else:
                            await asyncio.sleep(.02)

            except Exception as e:
                print(e)

        # POS_SS_PP = Position SS throttle (0 to 100 0 home left, 100 home right) PP decimal percent
        elif seg[:3] == 'POS':
            try:
                seg_split = seg.split("_")

                if len(seg_split) != 3:
                    print("Invalid POS command:", seg)
                    continue

                speed = int(seg_split[1])
                percentage = int(seg_split[2])

                await position_trolley(speed, percentage)

            except Exception as e:
                print("POS error:", e)

        # ZRAND = Random rainbow, fire, or color change
        elif seg[0:] == 'ZRAND':
            await random_effect(1, 3, dur)

            if exit_set_hdw_async:
                return "STOP"

        # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
        elif seg[:2] == 'ZR':
            v = float(seg[2:])
            await rbow(v, dur)

            if exit_set_hdw_async:
                return "STOP"

        # ZFIRE = Fire
        elif seg[0:] == 'ZFIRE':
            await fire(dur)

            if exit_set_hdw_async:
                return "STOP"

        # ZCOLCH = Color change
        elif seg[0:] == 'ZCOLCH':
            if multi_color():
                return "STOP"

        # TXXX = Train throttle -100 to 100
        elif seg[:1] == 'T':
            try:
                target_throttle = int(seg[1:])
                if cfg["bumper_mode"]:
                    bumper_requested_throttle = abs(target_throttle) / 100
                else:
                    train.throttle = target_throttle / 100
                    current_throttle = target_throttle
                    if target_throttle == 0:
                        await upd_bckgrnd_throttle_async(0, 1)
                    else:
                        await upd_bckgrnd_throttle_async(target_throttle, target_throttle)
            except Exception as e:
                print(e)

        # VRT = Background volume automatically tracks trolley throttle
        elif seg == 'VRT':
            bckgrnd_track_throttle = True

        # VRFXXX = Fade background volume to XXX, 0 to 100, turns off volume tracking to throttle
        elif seg[:3] == 'VRF':
            try:
                bckgrnd_track_throttle = False
                target_vol = int(seg[3:])

                if target_vol > 100:
                    target_vol = 100

                if target_vol < 0:
                    target_vol = 0

                while bckgrnd_vol != target_vol:
                    if bckgrnd_vol < target_vol:
                        new_vol = min(bckgrnd_vol + 2, target_vol)
                    else:
                        new_vol = max(bckgrnd_vol - 2, target_vol)

                    await upd_vol_async(0, new_vol)

                    if an_running:
                        if await animation_wait(.03):
                            return "STOP"
                    else:
                        await asyncio.sleep(.03)

            except Exception as e:
                print("VRF error:", e)

        # VRXXX = Set background volume to XXX, 0 to 100, turns off volume tracking to throttle
        elif seg[:2] == 'VR':
            try:
                bckgrnd_track_throttle = False
                target_vol = int(seg[2:])

                if target_vol > 100:
                    target_vol = 100

                if target_vol < 0:
                    target_vol = 0

                await upd_vol_async(0, target_vol)

            except Exception as e:
                print("VR error:", e)

        # MBXfilename = Background media
        elif seg[:2] == 'MB':
            repeat = seg[2]
            file_nm = seg[3:]
            return repeat + "_" + file_nm

        # MBRXXX = Music background, R repeat (0 no, 1 yes), XXX file name
        elif seg[0] == 'M':
            if seg[1] == "S":
                stp_a_0()

            elif seg[1] == "W" or seg[1] == "P":
                if seg[2] in FOLDER_MAP:
                    folder = FOLDER_MAP[seg[2]]
                    code = seg[3:]

                    if code == "SEQN":
                        filename, media_index[seg[2]] = get_indexed_media_file(folder, "mp3", media_index[seg[2]])

                    elif code == "SEQF":
                        filename, media_index[seg[2]] = get_indexed_media_file(folder, "mp3", 0)

                    elif code == "RAND":
                        filename = get_random_media_file(folder)

                    else:
                        filename = code

                    w1 = audiomp3.MP3Decoder(open(folder + filename + ".mp3", "rb"))

                if seg[1] == "W" or seg[1] == "P":
                    await stp_a_1()
                    mix.voice[1].play(w1, loop=False)

                if seg[1] == "W":
                    if await wait_snd_1():
                        return "STOP"

        elif seg[0] == 'H':
            await stp_a_1()

            if seg[1] == "B":
                fn = get_snds("bells/", "bell")
                w1 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[1].play(w1, loop=False)

            elif seg[1] == "H":
                fn = get_snds("horns/", "horn")
                w1 = audiomp3.MP3Decoder(open(fn, "rb"))
                mix.voice[1].play(w1, loop=False)

        elif seg[:2] == 'LN' or seg[0] == 'B':
            set_hdw_lights(seg)

        # FXXX = Fade NeoPixel brightness to XXX
        elif seg[0] == 'F':
            target_brightness = int(seg[1:])

            while brightness != target_brightness:
                if brightness < target_brightness:
                    brightness += 1
                    led.brightness = float(brightness / 100)

                else:
                    brightness -= 1
                    led.brightness = float(brightness / 100)

                led.show()

                if an_running:
                    if await animation_wait(.01):
                        return "STOP"
                else:
                    time.sleep(.01)

        elif seg[0] == 'W':
            s = float(seg[1:])

            if an_running:
                if await animation_wait(s):
                    return "STOP"
            else:
                await asyncio.sleep(s)


def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):
            led[i] = (r, g, b)
    else:
        led[light_n] = (r, g, b)
    led.show()


async def random_effect(il, ih, d):
    if exit_set_hdw_async:
        return

    i = random.randint(il, ih)

    if i == 1:
        await rbow(0.012, d)

    elif i == 2:
        multi_color()

        if an_running:
            if await animation_wait(d):
                return
        else:
            await asyncio.sleep(d)

    elif i == 3:
        await fire(d)


async def rbow(spd, dur):
    st = time.monotonic()
    te = time.monotonic()-st

    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw_async:
                return
            
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)

            led.show()

            if an_running:
                if await animation_wait(spd):
                    return
            else:
                time.sleep(spd)

            te = time.monotonic()-st

            if te > dur:
                return


def multi_color():
    for i in range(n_px):
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        c = random.randint(0, 2)

        if c == 0:
            r1 = r
            g1 = 0
            b1 = 0

        elif c == 1:
            r1 = 0
            g1 = g
            b1 = 0

        elif c == 2:
            r1 = 0
            g1 = 0
            b1 = b

        led[i] = (r1, g1, b1)

    led.show()

    return False


async def fire(dur):
    st = time.monotonic()

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    while True:
        if exit_set_hdw_async:
            return

        for i in range(n_px):
            f = random.randint(0, 110)

            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)

            led[i] = (r1, g1, b1)

        led.show()

        upd_vol(0)

        if an_running:
            if await animation_wait(random.uniform(0.05, 0.1)):
                return
        else:
            time.sleep(random.uniform(0.05, 0.1))

        te = time.monotonic()-st

        if te > dur:
            return


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


def get_random_media_file(folder_to_search):
    myfiles = files.return_directory("", folder_to_search, ".mp3")
    return random.choice(myfiles) if myfiles else None


def get_indexed_media_file(folder_to_search, file_ext, index):
    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext
    file_ext = file_ext.lower()

    myfiles = files.return_directory("", folder_to_search, file_ext)

    if not myfiles:
        return None, 0

    index = index % len(myfiles)

    selected_file = myfiles[index]
    new_index = (index + 1) % len(myfiles)

    print(f"playing: {selected_file}  ({index}/{len(myfiles)})")

    return selected_file, new_index


################################################################################
# State Machine

class StMch(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add(self, state):
        self.states[state.name] = state

    def go_to(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def upd(self):
        if self.state:
            self.state.upd(self)

################################################################################
# States

# Abstract parent state class.


class Ste(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, mch):
        pass

    def exit(self, mch):
        pass

    def upd(self, mch):
        pass


class BseSt(Ste):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, mch):
        ply_a_0(mvc_folder + "animations_are_now_active.mp3")
        files.log_item("Entered base state")

        l_sw.update()
        r_sw.update()

        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global an_just_added

        if an_running:
            return

        if cfg["bumper_mode"] and bumper_calibrated and bumper_requested_throttle > 0:
            return

        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0, ovrde_sw_st, wait_at_end = False)

        track_voltage = get_track_voltage()

        if track_voltage < 9.0:
            sw = "left"

        if sw == "left":
            if not mix.voice[0].playing and not an_running and not an_just_added:
                add_cmd("AN_" + cfg["option_selected"])
                an_just_added = True

        elif sw == "left_held":
            if not cfg["cont_mode"]:
                cfg["cont_mode"] = True
                ply_a_0(mvc_folder + "continuous_mode_activated.mp3")
                files.write_json_file("/sd/cfg.json", cfg)

        elif sw == "right":
            if not mix.voice[0].playing:
                mch.go_to("main_menu")

        if cfg["cont_mode"] and not mix.voice[0].playing and not an_running and not an_just_added:
            add_cmd("AN_" + cfg["option_selected"])
            an_just_added = True

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
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + main_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "volume_level_adjustment":
                vol_adj_mode = True
                ply_a_0(mvc_folder + "volume_adjustment_menu.mp3")
                while vol_adj_mode:
                    sw = utilities.switch_state(
                        l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
                    if sw == "left" and vol_adj_mode:
                        ch_vol("lower")
                    elif sw == "right" and vol_adj_mode:
                        ch_vol("raise")
                    elif sw == "right_held" and vol_adj_mode:
                        files.write_json_file("/sd/cfg.json", cfg)
                        ply_a_0(mvc_folder + "all_changes_complete.mp3")
                        vol_adj_mode = False
                        mch.go_to('base_state')
                        upd_vol(0.1)
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "bumper_settings":
                mch.go_to('bumper_settings')
            else:
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')


class Snds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, mch):
        files.log_item('Choose sounds menu')
        ply_a_0(mvc_folder + "sound_selection_menu.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    w0 = audiomp3.MP3Decoder(open(
                        "/sd/snd_opt/" + menu_snd_opt[self.i] + ".mp3", "rb"))
                    mix.voice[0].play(w0, loop=False)
                except Exception as e:
                    files.log_item(e)
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if sw == "right":
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                w0 = audiomp3.MP3Decoder(
                    open(mvc_folder + "option_selected.mp3", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass
            mch.go_to('base_state')


class AddSnds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'add_sounds_animate'

    def enter(self, mch):
        files.log_item('Add sounds animate')
        ply_a_0(mvc_folder + "add_sounds_animate.mp3")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(
                mvc_folder + add_snd[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if sw == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                ply_a_0(mvc_folder + "create_sound_track_files.mp3")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                ply_a_0(mvc_folder + "timestamp_mode_on.mp3")
                ply_a_0(mvc_folder + "timestamp_instructions.mp3")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                ply_a_0(mvc_folder + "timestamp_mode_off.mp3")
            else:
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')


class WebOpt(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'web_options'

    def enter(self, mch):
        files.log_item('Set Web Options')
        sel_web()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)
        if sw == "left":
            ply_a_0(mvc_folder + web_m[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if sw == "right":
            selected_menu_item = web_m[self.sel_i]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                opt_sel()
                sel_web()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                opt_sel()
                sel_web()
            elif selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')


class BumperOpt(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'bumper_settings'

    def enter(self, mch):
        files.log_item('Set Bumper Options')
        sel_bumper()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global bumper_requested_throttle, bumper_target_position, bumper_positioning, bumper_position_success
        global current_throttle

        sw = utilities.switch_state(l_sw, r_sw, time.sleep, 3.0, ovrde_sw_st)

        if sw == "left":
            ply_a_0(mvc_folder + bump_set[self.i] + ".mp3")
            self.sel_i = self.i
            self.i += 1

            if self.i > len(bump_set)-1:
                self.i = 0

        if sw == "right":
            selected_menu_item = bump_set[self.sel_i]

            if selected_menu_item == "bumper_mode_on":
                cfg["bumper_mode"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "bumper_instructions.mp3")
                mch.go_to('base_state')

            elif selected_menu_item == "bumper_mode_off":
                cfg["bumper_mode"] = False

                bumper_requested_throttle = 0.0
                bumper_target_position = None
                bumper_positioning = False
                bumper_position_success = False

                train.throttle = 0
                current_throttle = 0

                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')

            else:
                files.write_json_file("/sd/cfg.json", cfg)
                ply_a_0(mvc_folder + "all_changes_complete.mp3")
                mch.go_to('base_state')

async def bumper_tsk():
    global bumper_direction
    global bumper_requested_throttle
    global bumper_progress
    global bumper_last_time
    global current_throttle
    global bumper_target_position
    global bumper_positioning
    global bumper_position_success
    global bckgrnd_track_throttle

    bumper_last_time = time.monotonic()

    while True:

        if not cfg["bumper_mode"]:
            bumper_last_time = time.monotonic()
            await asyncio.sleep(0)
            continue

        if not bumper_calibrated:
            bumper_last_time = time.monotonic()
            await asyncio.sleep(0)
            continue

        now = time.monotonic()
        dt = now - bumper_last_time
        bumper_last_time = now

        if bumper_requested_throttle <= 0:
            train.throttle = 0
            current_throttle = 0

            await asyncio.sleep(0)
            continue

        bumper_hit = False
        hit_direction = bumper_direction

        if bumper_direction > 0 and r_sw_io.value:
            print("RIGHT bumper")
            bumper_hit = True

        elif bumper_direction < 0 and l_sw_io.value:
            print("LEFT bumper")
            bumper_hit = True

        if bumper_hit:

            homing_to_bumper = False

            if bumper_positioning and bumper_target_position is not None:
                if hit_direction < 0 and bumper_target_position == 0.0:
                    homing_to_bumper = True

                elif hit_direction > 0 and bumper_target_position == 1.0:
                    homing_to_bumper = True

            backoff_time, backoff_speed = await back_off_bumper(hit_direction)

            bumper_direction = -hit_direction

            if hit_direction < 0:

                if controller.time_forward and controller.base_speed:
                    bumper_progress = backoff_time * (backoff_speed / controller.base_speed) / controller.time_forward
                else:
                    bumper_progress = 0.0

                if bumper_progress < 0.0:
                    bumper_progress = 0.0

                if bumper_progress > 1.0:
                    bumper_progress = 1.0

                print("Position reset from LEFT bumper:", int(bumper_progress * 100), "%")

            else:

                if controller.time_reverse and controller.base_speed:
                    bumper_progress = 1.0 - (backoff_time * (backoff_speed / controller.base_speed) / controller.time_reverse)
                else:
                    bumper_progress = 1.0

                if bumper_progress < 0.0:
                    bumper_progress = 0.0

                if bumper_progress > 1.0:
                    bumper_progress = 1.0

                print("Position reset from RIGHT bumper:", int(bumper_progress * 100), "%")

            if bumper_positioning:

                train.throttle = 0
                current_throttle = 0

                await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

                bumper_requested_throttle = 0.0
                bumper_target_position = None
                bumper_positioning = False

                if homing_to_bumper:
                    bumper_position_success = True
                    print("POS homing complete")

                else:
                    bumper_position_success = False
                    print("POS aborted - unexpected bumper reached")

                bumper_last_time = time.monotonic()

                await asyncio.sleep(0)
                continue

            if bumper_direction > 0:
                print("Now traveling RIGHT")

            else:
                print("Now traveling LEFT")

            bumper_last_time = time.monotonic()

            await asyncio.sleep(0)
            continue

        if bumper_direction > 0:
            est_time = controller.time_forward
        else:
            est_time = controller.time_reverse

        if est_time is None or est_time <= 0:
            train.throttle = 0
            current_throttle = 0

            await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

            await asyncio.sleep(0)
            continue

        requested_speed = abs(bumper_requested_throttle)

        commanded_speed = requested_speed

        if bumper_direction > 0:
            travel_progress = bumper_progress
        else:
            travel_progress = 1.0 - bumper_progress

        if bumper_positioning and bumper_target_position is not None:
            if bumper_target_position > 0.0 and bumper_target_position < 1.0:
                distance_remaining = abs(bumper_target_position - bumper_progress)

                if distance_remaining < POS_RAMP_DISTANCE:
                    ramp_ratio = distance_remaining / POS_RAMP_DISTANCE
                    min_speed = POS_MIN_SPEED

                    if commanded_speed < min_speed:
                        min_speed = commanded_speed

                    commanded_speed = min_speed + ((commanded_speed - min_speed) * ramp_ratio)

        ramped_throttle = controller._ramped_throttle(bumper_direction, commanded_speed, travel_progress)

        train.throttle = ramped_throttle
        current_throttle = int(ramped_throttle * 100)

        await upd_bckgrnd_throttle_async(ramped_throttle, requested_speed)

        base_speed = controller.base_speed

        if base_speed is None or base_speed <= 0:
            base_speed = commanded_speed

        actual_speed = abs(ramped_throttle)

        if base_speed > 0:
            position_change = dt * (actual_speed / base_speed) / est_time

            if bumper_direction > 0:
                bumper_progress += position_change
            else:
                bumper_progress -= position_change

        if bumper_progress > 1.0:
            bumper_progress = 1.0

        if bumper_progress < 0.0:
            bumper_progress = 0.0

        if bumper_positioning and bumper_target_position is not None:

            if bumper_target_position > 0.0 and bumper_target_position < 1.0:

                target_reached = False

                if bumper_direction > 0 and bumper_progress >= bumper_target_position:
                    target_reached = True

                elif bumper_direction < 0 and bumper_progress <= bumper_target_position:
                    target_reached = True

                if target_reached:
                    bumper_progress = bumper_target_position

                    train.throttle = 0
                    current_throttle = 0

                    # Trolley actually stopped, so tracked
                    # trolley sound goes to zero.
                    await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

                    bumper_requested_throttle = 0.0

                    print("POS destination reached:", int(bumper_progress * 100), "%")

                    bumper_target_position = None
                    bumper_positioning = False
                    bumper_position_success = True

        await asyncio.sleep(0)

###############################################################################
# Create the state machine

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())
st_mch.add(AddSnds())
st_mch.add(WebOpt())
st_mch.add(BumperOpt())

aud_en.value = True

upd_vol(.1)


if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        led[1] = (0, 255, 0)
        led.show()
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        dbm_string = str(-int(avg_rssi))+"dbm"
        spk_str(dbm_string, False)
        spk_web()
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()
else:
    led[1] = (255, 0, 0)
    led.show()
    time.sleep(3)

# initialize items
upd_vol(.5)

if cfg["bumper_mode"]:
    calibrate_bumper()

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

###############################################################################
# Main task handling

async def bumper_tsk():
    global bumper_direction
    global bumper_requested_throttle
    global bumper_progress
    global bumper_last_time
    global current_throttle
    global bumper_target_position
    global bumper_positioning
    global bumper_position_success
    global bckgrnd_track_throttle

    bumper_last_time = time.monotonic()

    while True:

        if not cfg["bumper_mode"]:
            bumper_last_time = time.monotonic()
            await asyncio.sleep(0)
            continue

        if not bumper_calibrated:
            bumper_last_time = time.monotonic()
            await asyncio.sleep(0)
            continue

        now = time.monotonic()
        dt = now - bumper_last_time
        bumper_last_time = now

        if bumper_requested_throttle <= 0:
            train.throttle = 0
            current_throttle = 0

            await asyncio.sleep(0)
            continue

        bumper_hit = False
        hit_direction = bumper_direction

        if bumper_direction > 0 and r_sw_io.value:
            print("RIGHT bumper")
            bumper_hit = True

        elif bumper_direction < 0 and l_sw_io.value:
            print("LEFT bumper")
            bumper_hit = True

        if bumper_hit:

            homing_to_bumper = False

            if bumper_positioning and bumper_target_position is not None:
                if hit_direction < 0 and bumper_target_position == 0.0:
                    homing_to_bumper = True

                elif hit_direction > 0 and bumper_target_position == 1.0:
                    homing_to_bumper = True

            backoff_time, backoff_speed = await back_off_bumper(hit_direction)

            bumper_direction = -hit_direction

            if hit_direction < 0:

                if controller.time_forward and controller.base_speed:
                    bumper_progress = backoff_time * (backoff_speed / controller.base_speed) / controller.time_forward
                else:
                    bumper_progress = 0.0

                if bumper_progress < 0.0:
                    bumper_progress = 0.0

                if bumper_progress > 1.0:
                    bumper_progress = 1.0

                print("Position reset from LEFT bumper:", int(bumper_progress * 100), "%")

            else:

                if controller.time_reverse and controller.base_speed:
                    bumper_progress = 1.0 - (backoff_time * (backoff_speed / controller.base_speed) / controller.time_reverse)
                else:
                    bumper_progress = 1.0

                if bumper_progress < 0.0:
                    bumper_progress = 0.0

                if bumper_progress > 1.0:
                    bumper_progress = 1.0

                print("Position reset from RIGHT bumper:", int(bumper_progress * 100), "%")

            if bumper_positioning:

                train.throttle = 0
                current_throttle = 0

                await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

                bumper_requested_throttle = 0.0
                bumper_target_position = None
                bumper_positioning = False

                if homing_to_bumper:
                    bumper_position_success = True
                    print("POS homing complete")

                else:
                    bumper_position_success = False
                    print("POS aborted - unexpected bumper reached")

                bumper_last_time = time.monotonic()

                await asyncio.sleep(0)
                continue

            if bumper_direction > 0:
                print("Now traveling RIGHT")

            else:
                print("Now traveling LEFT")

            bumper_last_time = time.monotonic()

            await asyncio.sleep(0)
            continue

        if bumper_direction > 0:
            est_time = controller.time_forward
        else:
            est_time = controller.time_reverse

        if est_time is None or est_time <= 0:
            train.throttle = 0
            current_throttle = 0

            await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

            await asyncio.sleep(0)
            continue

        requested_speed = abs(bumper_requested_throttle)

        commanded_speed = requested_speed

        if bumper_direction > 0:
            travel_progress = bumper_progress
        else:
            travel_progress = 1.0 - bumper_progress

        if bumper_positioning and bumper_target_position is not None:
            if bumper_target_position > 0.0 and bumper_target_position < 1.0:
                distance_remaining = abs(bumper_target_position - bumper_progress)

                if distance_remaining < POS_RAMP_DISTANCE:
                    ramp_ratio = distance_remaining / POS_RAMP_DISTANCE
                    min_speed = POS_MIN_SPEED

                    if commanded_speed < min_speed:
                        min_speed = commanded_speed

                    commanded_speed = min_speed + ((commanded_speed - min_speed) * ramp_ratio)

        ramped_throttle = controller._ramped_throttle(bumper_direction, commanded_speed, travel_progress)

        train.throttle = ramped_throttle
        current_throttle = int(ramped_throttle * 100)

        await upd_bckgrnd_throttle_async(ramped_throttle, requested_speed)

        base_speed = controller.base_speed

        if base_speed is None or base_speed <= 0:
            base_speed = commanded_speed

        actual_speed = abs(ramped_throttle)

        if base_speed > 0:
            position_change = dt * (actual_speed / base_speed) / est_time

            if bumper_direction > 0:
                bumper_progress += position_change
            else:
                bumper_progress -= position_change

        if bumper_progress > 1.0:
            bumper_progress = 1.0

        if bumper_progress < 0.0:
            bumper_progress = 0.0

        if bumper_positioning and bumper_target_position is not None:

            if bumper_target_position > 0.0 and bumper_target_position < 1.0:

                target_reached = False

                if bumper_direction > 0 and bumper_progress >= bumper_target_position:
                    target_reached = True

                elif bumper_direction < 0 and bumper_progress <= bumper_target_position:
                    target_reached = True

                if target_reached:
                    bumper_progress = bumper_target_position

                    train.throttle = 0
                    current_throttle = 0

                    await upd_bckgrnd_throttle_async(0, bumper_requested_throttle)

                    bumper_requested_throttle = 0.0

                    print("POS destination reached:", int(bumper_progress * 100), "%")

                    bumper_target_position = None
                    bumper_positioning = False
                    bumper_position_success = True

        await asyncio.sleep(0)
        

async def process_cmd_tsk():
    """Task to continuously process commands."""
    while True:
        try:
            await process_cmd()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)


async def server_poll_tsk(server):
    """Poll the web server."""
    while True:
        try:
            server.poll()
        except OSError as e:
            if e.errno == 116:
                files.log_item("Client timeout (Errno 116)")
            else:
                files.log_item(f"OSError: {e}")
        except Exception as e:
            files.log_item(f"Poll Exception: {e}")
        await asyncio.sleep(0)


async def state_mach_upd_task(st_mch):
    global an_just_added
    while True:
        st_mch.upd()
        if an_just_added:
            await asyncio.sleep(3)
            an_just_added = False
        else:
            await asyncio.sleep(0)


async def main():
    tasks = [
        process_cmd_tsk(),
        state_mach_upd_task(st_mch),
        bumper_tsk()
    ]

    if web:
        tasks.append(server_poll_tsk(server))

    await asyncio.gather(*tasks)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass