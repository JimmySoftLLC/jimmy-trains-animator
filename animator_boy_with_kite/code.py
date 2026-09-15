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
import gc
import array
import rp2pio
import adafruit_pioasm
import os


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item(
        "Point " + collection_point + " Available memory: {} bytes".format(start_mem)
    )


gc_col("Imports gc, files")



################################################################################
# config variables

cfg = files.read_json_file("cfg.json")

cfg_main = files.read_json_file("main_menu.json")
main_m = cfg_main["main_menu"]

cfg_vol = files.read_json_file("volume_settings.json")
v_set = cfg_vol["volume_settings"]

cfg_opt = files.read_json_file("options.json")
mnu_o = cfg_opt["options"]

################################################################################
# globals
lst_kite_rot_pos = 90
lst_kite_deploy_pos = cfg["kite_deploy_max"]
kite_min = 0
kite_max = 180
kill_process = False
async_running = False
rand_timer = 0
launch_dialog_played = False

################################################################################
# setup hardware

# Setup the switches
l_sw_io = digitalio.DigitalInOut(board.GP2)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)

r_sw = digitalio.DigitalInOut(board.GP3)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

t_sw = digitalio.DigitalInOut(board.GP1)
t_sw.direction = digitalio.Direction.INPUT
t_sw.pull = digitalio.Pull.UP
t_sw = Debouncer(t_sw)

################################################################################
# PIO stepper motor

STEPPER_PHASE_TIME = 0.005
STEPPER_FULL_STEP_TIME = STEPPER_PHASE_TIME * 4

stepper_program = adafruit_pioasm.assemble("""
.program stepper
start:
    pull block
    out x, 1
    out y, 31
    jmp !x down
up:
    set pins, 9 [24]
    set pins, 3 [24]
    set pins, 6 [24]
    set pins, 12 [24]
    jmp y-- up
    jmp finished
down:
    set pins, 12 [24]
    set pins, 6 [24]
    set pins, 3 [24]
    set pins, 9 [24]
    jmp y-- down
finished:
    set pins, 0
    set x, 1
    mov isr, x
    push block
    jmp start
""")

stepper_init = adafruit_pioasm.assemble("""
    set pins, 0
""")

stepper_coils_off = adafruit_pioasm.assemble("""
    set pins, 0
""")

stepper_sm = rp2pio.StateMachine(stepper_program, frequency=5000, init=stepper_init, first_set_pin=board.GP4, set_pin_count=4, initial_set_pin_state=0, initial_set_pin_direction=0x0F, out_shift_right=True, wait_for_txstall=False)
stepper_done = array.array("I", [0])

################################################################################
# Audio

# Setup pin for vol on 5v aud board
a_in = AnalogIn(board.A2)

# setup pin for audio enable 21 on 5v aud board
aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup the mixer to play mp3 files
mix = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=2,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=16384,
)

aud.play(mix)


def upd_vol(s):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
    else:
        try:
            v = int(cfg["volume"]) / 100
        except:
            v = 0.5
        if v < 0 or v > 1:
            v = 0.5
    mix.voice[0].level = v
    time.sleep(s)


upd_vol(0.01)

################################################################################
# Servos
kite_rot = pwmio.PWMOut(board.GP17, duty_cycle=2**15, frequency=50)
kite_rot = servo.Servo(kite_rot, min_pulse=500, max_pulse=2500)
kite_rot.angle = lst_kite_rot_pos


################################################################################
# Sound helpers

w0 = None
START_FAIL_CHANCE = 0.10
FLIGHT_FAIL_CHANCE = 0.05
FLIGHT_DIALOG_CHANCE = 0.40

def clear_w0():
    global w0
    if w0:
        try:
            w0.deinit()
        except:
            pass
        w0 = None
    gc_col("Clear w0")

def clear_finished_w0():
    if w0 and not mix.voice[0].playing:
        clear_w0()

def stop_dialog():
    if mix.voice[0].playing:
        mix.voice[0].stop()
    clear_w0()

def play_dialog_folder(folder, chance=1.0):
    global w0
    if mix.voice[0].playing:
        return False
    if random.random() > chance:
        return False
    clear_w0()
    path = folder
    try:
        sounds = os.listdir(path)
    except Exception as e:
        files.log_item("Dialog folder error " + folder + ": " + str(e))
        gc.collect()
        return False
    if len(sounds) == 0:
        sounds = None
        gc.collect()
        return False
    attempts = len(sounds)
    while attempts > 0:
        file_name = random.choice(sounds)
        if file_name.lower().endswith(".mp3"):
            break
        attempts -= 1
    else:
        sounds = None
        gc.collect()
        return False
    sounds = None
    gc.collect()
    print("Dialog: " + folder + "/" + file_name)
    try:
        w0 = audiomp3.MP3Decoder(open(path + "/" + file_name, "rb"))
        mix.voice[0].play(w0, loop=False)
    except Exception as e:
        files.log_item("Dialog play error: " + str(e))
        clear_w0()
        return False
    return True

def play_wind():
    global w0
    if mix.voice[0].playing:
        return False
    if not play_dialog_folder("wind"):
        return False
    while mix.voice[0].playing:
        if animation_stop():
            clear_w0()
            return False
        upd_vol(0.01)
    clear_w0()
    if kill_process:
        return False
    try:
        w0 = audiomp3.MP3Decoder(open("mp3/wind_effect.mp3", "rb"))
        mix.voice[0].play(w0, loop=False)
    except Exception as e:
        files.log_item("Wind play error: " + str(e))
        clear_w0()
        return False
    return True


def ply_a_0(file_name):
    global w0
    upd_vol(0.01)
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.01)
    print("playing " + file_name)
    w0 = audiomp3.MP3Decoder(open("mp3/" + file_name + ".mp3", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        exit_early()
    clear_w0()


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
    ply_a_0("volume")
    spk_word(cfg["volume"])


def spk_sentence(snd):
    print(snd)
    try:
        ply_a_0(snd)
    except:
        snd_split = snd.split("_")
        for snd in snd_split:
            spk_word(snd)


def spk_word(str_to_speak):
    print(str_to_speak)
    if (
        str_to_speak == "minute"
        or str_to_speak == "minutes"
        or str_to_speak == "timer"
        or str_to_speak == "lower"
        or str_to_speak == "raise"
        or str_to_speak == "no"
        or str_to_speak == "continuous"
        or str_to_speak == "options"
        or str_to_speak == "this"
        or str_to_speak == "exit"
        or str_to_speak == "settings"
        or str_to_speak == "main"
        or str_to_speak == "menu"
        or str_to_speak == "adjustment"
        or str_to_speak == "volume"
        or str_to_speak == "pot"
        or str_to_speak == "off"
        or str_to_speak == "on"
        or str_to_speak == "random"
        or str_to_speak == "to"
        or str_to_speak == "lowerraisesavevol"
        or str_to_speak == "mode"
        or str_to_speak == "centerfig"
        or str_to_speak == "alignlrsave"
        or str_to_speak == "wind"
    ):
        ply_a_0(str_to_speak)
        return
    for character in str_to_speak:
        try:
            ply_a_0(character)
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")


################################################################################
# misc


def exit_early():
    global kill_process
    l_sw.update()
    if l_sw.fell:
        kill_process = True
        if mix.voice[0].playing: mix.voice[0].stop()
        coils_off()
        return True
    return False

def animation_stop():
    global kill_process
    if not l_sw_io.value:
        kill_process = True
        if mix.voice[0].playing:
            mix.voice[0].stop()
        stop_stepper()
        return True
    return False


################################################################################
# stepper motor

def clear_stepper_done():
    while stepper_sm.in_waiting:
        stepper_sm.readinto(stepper_done)

def coils_off():
    stepper_sm.run(stepper_coils_off)

def stop_stepper():
    stepper_sm.stop()
    stepper_sm.restart()
    clear_stepper_done()

################################################################################
# servo motor

def servo_m(servo_pos):
    global lst_kite_rot_pos
    if servo_pos < kite_min:
        servo_pos = kite_min
    if servo_pos > kite_max:
        servo_pos = kite_max
    kite_rot.angle = servo_pos
    lst_kite_rot_pos = servo_pos


def ch_servo(action):
    s = int(cfg["servo"])
    if "servo" in action:
        s = action.split("servo")
        s = int(s[1])
    if action == "left":
        s -= 1
    elif action == "right":
        s += 1
    if s > 180:
        s = 180
    if s < 0:
        s = 0
    cfg["servo"] = str(s)
    servo_m(int(cfg["servo"]))
    spk_word(cfg["servo"])


################################################################################
# async methods


loop = asyncio.get_event_loop()


def rotate_spd():
    if mix.voice[0].playing:
        return 0.005
    else:
        return 0.02


async def rotate_kite_async():
    global lst_kite_rot_pos, async_running
    while async_running:
        center_servo_pos = int(cfg["servo"])
        rand_pos_1 = random.randint(center_servo_pos - 70, center_servo_pos - 70)
        rand_pos_2 = random.randint(center_servo_pos + 70, center_servo_pos + 70)
        sign = 1
        if lst_kite_rot_pos > rand_pos_1:
            sign = -1
        total_steps = abs(rand_pos_1 - lst_kite_rot_pos)
        animation_stop()
        if not async_running or kill_process:
            break
        for _ in range(total_steps + 1):
            if animation_stop():
                async_running = False
                return
            spd = rotate_spd()
            kite_ang = lst_kite_rot_pos + 1 * sign
            servo_m(kite_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)
        sign = 1
        if lst_kite_rot_pos > rand_pos_2:
            sign = -1
        total_steps = abs(rand_pos_2 - lst_kite_rot_pos)
        animation_stop()
        if not async_running or kill_process:
            break
        for _ in range(total_steps + 1):
            if animation_stop():
                async_running = False
                return
            spd = rotate_spd()
            kite_ang = lst_kite_rot_pos + 1 * sign
            servo_m(kite_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)


async def deploy_kite(steps, direction, spd=0.005):
    global async_running, lst_kite_deploy_pos, launch_dialog_played
    if steps <= 0:
        async_running = False
        return
    if direction != "up" and direction != "down":
        raise ValueError("Direction must be 'down' or 'up'")
    clear_stepper_done()
    direction_bit = 1 if direction == "up" else 0
    command = ((steps - 1) << 1) | direction_bit
    command_data = array.array("I", [command])
    start_pos = lst_kite_deploy_pos
    start_time = time.monotonic()
    launch_position = int(cfg["kite_deploy_max"] * 0.15)
    stepper_sm.write(command_data)
    while not stepper_sm.in_waiting:
        elapsed = time.monotonic() - start_time
        completed_steps = int(elapsed / STEPPER_FULL_STEP_TIME)
        if completed_steps > steps:
            completed_steps = steps
        if direction == "up":
            lst_kite_deploy_pos = start_pos + completed_steps
        else:
            lst_kite_deploy_pos = start_pos - completed_steps
        if direction == "up" and not launch_dialog_played and lst_kite_deploy_pos >= launch_position:
            clear_finished_w0()
            if play_dialog_folder("launch"):
                launch_dialog_played = True
        if animation_stop():
            async_running = False
            return
        await asyncio.sleep(0)
    stepper_sm.readinto(stepper_done)
    if direction == "up":
        lst_kite_deploy_pos = start_pos + steps
    else:
        lst_kite_deploy_pos = start_pos - steps
    async_running = False


async def rn_an(steps, direction):
    global async_running
    async_running = True
    rot_k = asyncio.create_task(rotate_kite_async())
    deploy_g = asyncio.create_task(deploy_kite(steps, direction))
    await asyncio.gather(deploy_g, rot_k)


async def rn_home(steps, direction):
    global async_running
    async_running = True
    deploy_g = asyncio.create_task(deploy_kite(steps, direction))
    await asyncio.gather(deploy_g)


################################################################################
# Animations


def rnd_prob(c):
    y = random.random()
    if y < c:
        return True
    return False


def an():
    global kill_process, launch_dialog_played
    kill_process = False
    launch_dialog_played = False
    clear_finished_w0()
    if rnd_prob(START_FAIL_CHANCE):
        play_dialog_folder("start_fail")
        return
    play_dialog_folder("start_pass")
    cycles = 8
    if cfg["random"] == False:
        cycles = 4
    for _ in range(cycles):
        clear_finished_w0()
        if kill_process:
            stop_dialog()
            coils_off()
            return
        if rnd_prob(0.2) and not mix.voice[0].playing and cfg["wind"] == True:
            play_wind()
            if kill_process:
                stop_dialog()
                coils_off()
                return
        if cfg["random"] == True:
            rand_deploy_pos = random.randint(0, cfg["kite_deploy_max"])
            files.log_item("Random deploy pos: " + str(rand_deploy_pos))
            direction = "up"
            if lst_kite_deploy_pos > rand_deploy_pos:
                direction = "down"
            if rnd_prob(FLIGHT_FAIL_CHANCE):
                clear_finished_w0()
                play_dialog_folder("flight_fail")
                total_steps = abs(0 - lst_kite_deploy_pos)
                asyncio.run(rn_an(total_steps, "down"))
                if mix.voice[0].playing:
                    mix.voice[0].stop()
                clear_w0()
                coils_off()
                return
            clear_finished_w0()
            if direction == "up" and launch_dialog_played:
                play_dialog_folder("flight_up", FLIGHT_DIALOG_CHANCE)
            elif direction == "down":
                play_dialog_folder("flight_down", FLIGHT_DIALOG_CHANCE)
            total_steps = abs(rand_deploy_pos - lst_kite_deploy_pos)
            asyncio.run(rn_an(total_steps, direction))
            if kill_process:
                stop_dialog()
                coils_off()
                return
        else:
            if rnd_prob(FLIGHT_FAIL_CHANCE):
                clear_finished_w0()
                play_dialog_folder("flight_fail")
                total_steps = abs(0 - lst_kite_deploy_pos)
                asyncio.run(rn_an(total_steps, "down"))
                if mix.voice[0].playing:
                    mix.voice[0].stop()
                clear_w0()
                coils_off()
                return
            clear_finished_w0()
            play_dialog_folder("flight_down", FLIGHT_DIALOG_CHANCE)
            total_steps = abs(0 - lst_kite_deploy_pos)
            asyncio.run(rn_an(total_steps, "down"))
            if kill_process:
                stop_dialog()
                coils_off()
                return
            clear_finished_w0()
            if launch_dialog_played:
                play_dialog_folder("flight_up", FLIGHT_DIALOG_CHANCE)
            total_steps = abs(cfg["kite_deploy_max"] - lst_kite_deploy_pos)
            asyncio.run(rn_an(total_steps, "up"))
            if kill_process:
                stop_dialog()
                coils_off()
                return
    if mix.voice[0].playing:
        mix.voice[0].stop()
    clear_w0()
    gc_col("An done clean up sound")
    if kill_process:
        coils_off()
        return
    play_dialog_folder("flight_down", FLIGHT_DIALOG_CHANCE)
    total_steps = abs(0 - lst_kite_deploy_pos)
    asyncio.run(rn_an(total_steps, "down"))
    coils_off()
    clear_finished_w0()
    if kill_process:
        stop_dialog()
        return
    play_dialog_folder("end")


def home_motors():
    direction = "up"
    kite_ang = int(cfg["servo"] )
    servo_m(kite_ang)
    if lst_kite_deploy_pos > 0:
        direction = "down"
    ply_a_0("homming")
    total_steps = abs(0 - lst_kite_deploy_pos)
    asyncio.run(rn_home(total_steps, direction))


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
        # set servos to starting position
        ply_a_0("active")
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer
        sw = utilities.switch_state_trigger(l_sw, r_sw, t_sw, upd_vol, 3.0)
        if sw == "left_held":
            if cfg["timer"] == True:
                cfg["timer"] = False
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                spk_sentence("timer_mode_off")
                return
            else:
                cfg["timer"] = True
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                spk_sentence("timer_mode_on")
                return
        elif cfg["timer"] == True:
            if rand_timer <= 0:
                an()
                time.sleep(0.25)
                coils_off()
                rand_timer = int(cfg["timer_val"]) * 60
                print("an done")
            else:
                upd_vol(1)
                rand_timer -= 1
        elif sw == "left" or sw == "trigger":
            an()
            time.sleep(0.25)
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
        spk_sentence("main_menu")
        spk_sentence("r_l_but")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            spk_sentence(main_m[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m) - 1:
                self.i = 0
        if r_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "options":
                mch.go_to("options")
            elif sel_i == "volume_settings":
                mch.go_to("volume_settings")
            elif sel_i == "centerfig":
                mch.go_to("servo_settings")
            else:
                ply_a_0("all_changes_complete")
                mch.go_to("base_state")


class VolSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "volume_settings"

    def enter(self, mch):
        files.log_item("Set Web Options")
        spk_sentence("volume_settings_menu")
        spk_sentence("r_l_but")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            spk_sentence(v_set[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(v_set) - 1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = v_set[self.sel_i]
            if sel_mnu == "volume_adjustment":
                spk_sentence("volume_adjustment_menu_lowerraisesavevol")
                done = False
                while not done:
                    sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
                    if sw == "left":
                        ch_vol("lower")
                    elif sw == "right":
                        ch_vol("raise")
                    elif sw == "right_held":
                        aud_en.value = False
                        files.write_json_file("cfg.json", cfg)
                        aud_en.value = True
                        ply_a_0("all_changes_complete")
                        done = True
                        mch.go_to("base_state")
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                ply_a_0("all_changes_complete")
                mch.go_to("base_state")
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                ply_a_0("all_changes_complete")
                mch.go_to("base_state")


class Opt(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "options"

    def enter(self, mch):
        files.log_item("Choose sounds menu")
        spk_sentence("options_menu")
        spk_sentence("r_l_but")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global rand_timer
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            spk_sentence(mnu_o[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(mnu_o) - 1:
                self.i = 0
        if r_sw.fell:
            options = mnu_o[self.sel_i].split("_")
            if options[0] == "timer":
                cfg["timer"] = True
                cfg["timer_val"] = str(options[1])
                rand_timer = 0
            elif mnu_o[self.sel_i] == "wind":
                cfg["wind"] = True
            elif mnu_o[self.sel_i] == "no_wind":
                cfg["wind"] = False
            elif mnu_o[self.sel_i] == "random_raise_lower":
                cfg["random"] = True
            elif mnu_o[self.sel_i] == "raise_lower":
                cfg["random"] = False
            elif mnu_o[self.sel_i] == "exit_this_menu":
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                ply_a_0("all_changes_complete")
                mch.go_to("base_state")
                return
            ply_a_0("option_set")


class ServoSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "servo_settings"

    def enter(self, mch):
        global kill_process
        files.log_item("Set Web Options")
        spk_sentence("centerfig_menu")
        spk_sentence("alignlrsave")
        cfg["servo"] = 90
        kill_process = False
        servo_m(int(cfg["servo"]))
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        done = False
        while not done:
            sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
            if sw == "left":
                ch_servo("left")
            elif sw == "right":
                ch_servo("right")
            elif sw == "right_held":
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                ply_a_0("all_changes_complete")
                done = True
                mch.go_to("base_state")
            pass


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(VolSet())
st_mch.add(Opt())
st_mch.add(ServoSet())

aud_en.value = True

upd_vol(0.01)
home_motors()
st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")

while True:
    st_mch.upd()
    upd_vol(0.01)

