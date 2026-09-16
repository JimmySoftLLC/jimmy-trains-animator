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
# Config variables

cfg = files.read_json_file("cfg.json")

cfg_main = files.read_json_file("main_menu.json")
main_m = cfg_main["main_menu"]

cfg_vol = files.read_json_file("volume_settings.json")
v_set = cfg_vol["volume_settings"]

cfg_opt = files.read_json_file("options.json")
mnu_o = cfg_opt["options"]

cfg_muse_set = files.read_json_file("museum_settings.json")
muse_set = cfg_muse_set["museum_settings"]

################################################################################
# Globals

flag_deploy_max = 1100
lst_deploy_pos = flag_deploy_max
half_mast_pos = flag_deploy_max // 2
flag_up_extra = 50
wave_motor_steps = 1000
flag_rot_min = 0
flag_rot_max = 180
lst_rot_pos = flag_rot_max
flag_ext = 3

kill_process = False
async_running = False
rand_timer = 0
button_press_start = None
museum_long_press_stop = False

################################################################################
# Switch hardware

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
# Audio hardware

# setup pin for vol on 5v aud board
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

# setup the mixer to play mp3 files
mix = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=2,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=8192,
)

aud.play(mix)


def upd_vol(s):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        time.sleep(s)
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

rot = pwmio.PWMOut(board.GP16, duty_cycle=2**15, frequency=50)
rot = servo.Servo(rot, min_pulse=500, max_pulse=2500)

################################################################################
# Led

digitalio.DigitalInOut
led = pwmio.PWMOut(board.GP8, frequency=5000, duty_cycle=0)

################################################################################
# Sound helpers

w0 = None

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
    global wind_playing
    if mix.voice[0].playing:
        mix.voice[0].stop()
    clear_w0()
    wind_playing = False

def play_dialog_folder(folder, chance=1.0):
    global w0
    if not cfg["dialog"]:
        return False
    if mix.voice[0].playing:
        return False
    if random.random() >= chance:
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
        upd_vol(0.01)
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
        or str_to_speak == "sound"
        or str_to_speak == "otaps"
        or str_to_speak == "oretreat"
        or str_to_speak == "oreveille"
        or str_to_speak == "only"
        or str_to_speak == "wave"
        or str_to_speak == "lrdiseng"
        or str_to_speak == "wind"
        or str_to_speak == "dialog"
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
# Misc

def exit_early():
    global kill_process
    if not cfg["museum_mode"] and not l_sw_io.value:
        kill_process = True
        if mix.voice[0].playing:
            mix.voice[0].stop()
        coils_off()
        rot.angle = 180
        return True
    return False

def animation_stop():
    global kill_process, button_press_start, museum_long_press_stop
    if kill_process:
        return True
    if cfg["museum_mode"]:
        if not l_sw_io.value:
            if button_press_start is None:
                button_press_start = time.monotonic()
            elif time.monotonic() - button_press_start > 1.0:
                kill_process = True
                museum_long_press_stop = True
                button_press_start = None
                if mix.voice[0].playing:
                    mix.voice[0].stop()
                stop_stepper()
                time.sleep(2)
                return True
        else:
            button_press_start = None
    elif not l_sw_io.value:
        kill_process = True
        if mix.voice[0].playing:
            mix.voice[0].stop()
        stop_stepper()
        return True
    return False


def reset_motors():
    global kill_process
    kill_process = False
    rot.angle = 180
    asyncio.run(home_flag())
    coils_off()
    led.duty_cycle = 0
    
def flash_led():
    for _ in range(3):
        led.duty_cycle = 65000
        time.sleep(.75)
        led.duty_cycle = 0
        time.sleep(.75)

def rnd_prob(c):
    y = random.random()
    if y < c:
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

################################################################################
# servo motor

def servo_m(servo_pos):
    global lst_rot_pos
    if servo_pos < flag_rot_min:
        servo_pos = flag_rot_min
    if servo_pos > flag_rot_max:
        servo_pos = flag_rot_max
    rot.angle = servo_pos
    lst_rot_pos = servo_pos


def ch_servo(action):
    global kill_process
    s = int(cfg["servo"])
    if "servo" in action:
        s = action.split("servo")
        s = int(s[1])
    if action == "lower":
        s -= 1
    elif action == "raise":
        s += 1
    if s > 180:
        s = 100
    if s < 0:
        s = 0
    cfg["servo"] = str(s)
    ply_a_0("wave")
    spk_word(cfg["servo"])
    kill_process = False
    asyncio.run( rn_an(100, "up", False))  # Flag wave


################################################################################
# async methods

loop = asyncio.get_event_loop()


def rotate_spd():
    if mix.voice[0].playing:
        return 0.005
    else:
        return random.uniform(0.03, 0.03)
    

async def wave_flag_async(rand):
    global lst_rot_pos, async_running
    center_servo_pos = int(cfg["servo"])
    while async_running:
        if rand:
            pos_1 = random.randint(center_servo_pos - flag_ext, center_servo_pos)
            pos_2 = random.randint(center_servo_pos, center_servo_pos + flag_ext)
        else:
            pos_1 = center_servo_pos - flag_ext
            pos_2 = center_servo_pos + flag_ext
        sign = 1
        if lst_rot_pos > pos_1:
            sign = -1
        total_steps = abs(pos_1 - lst_rot_pos)
        exit_early()
        if not async_running or kill_process:
            break
        spd = rotate_spd()
        for _ in range(total_steps + 1):
            flag_ang = lst_rot_pos + 1 * sign
            servo_m(flag_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)
        sign = 1
        if lst_rot_pos > pos_2:
            sign = -1
        total_steps = abs(pos_2 - lst_rot_pos)
        exit_early()
        if not async_running or kill_process:
            break
        for _ in range(total_steps + 1):
            spd = rotate_spd()
            flag_ang = lst_rot_pos + 1 * sign
            servo_m(flag_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)


async def deploy_flag(steps, direction, keep_track=True):
    global async_running, lst_deploy_pos
    steps = int(steps)
    if steps <= 0:
        return
    if direction != "up" and direction != "down":
        print("Direction must be 'down' or 'up'")
        return
    stepper_sm.restart()
    clear_stepper_done()
    direction_bit = 0 if direction == "up" else 1
    command = ((steps - 1) << 1) | direction_bit
    command_data = array.array("I", [command])
    start_pos = lst_deploy_pos
    start_time = time.monotonic()
    stepper_sm.write(command_data)
    while not stepper_sm.in_waiting:
        if keep_track:
            elapsed = time.monotonic() - start_time
            completed_steps = int(elapsed / STEPPER_FULL_STEP_TIME)
            if completed_steps > steps:
                completed_steps = steps
            if direction == "up":
                lst_deploy_pos = start_pos + completed_steps
            else:
                lst_deploy_pos = start_pos - completed_steps
        if animation_stop():
            async_running = False
            stop_stepper()
            coils_off()
            return
        await asyncio.sleep(0)
    stepper_sm.readinto(stepper_done)
    if keep_track:
        if direction == "up":
            lst_deploy_pos = start_pos + steps
        else:
            lst_deploy_pos = start_pos - steps


async def move_flag_to(pos):
    pos = int(pos)
    steps = abs(pos - lst_deploy_pos)
    if steps == 0:
        return
    direction = "up" if pos > lst_deploy_pos else "down"
    await deploy_flag(steps, direction, True)


async def rn_an(steps, direction, rand, keep_track=True):
    global async_running
    async_running = True
    rot_f = asyncio.create_task(wave_flag_async(rand))
    deploy_f = asyncio.create_task(deploy_flag(steps, direction, keep_track))
    await deploy_f
    async_running = False
    await rot_f


async def home_flag():
    global lst_deploy_pos, kill_process
    kill_process = False
    await deploy_flag(flag_deploy_max + flag_up_extra, "down", False)
    lst_deploy_pos = 0
    coils_off()


################################################################################
# Animations

def an():
    global kill_process
    kill_process = False
    cfg_temp = files.read_json_file("cfg.json")
    if cfg_temp["random"] == True:
        pick = random.randint(0, 2)
        print(pick)
        if pick == 0:
            cfg_temp["sound"] = "sound_off"
        elif pick == 1:
            cfg_temp["sound"] = "sound_otaps"
        elif pick == 2:
            cfg_temp["sound"] = "sound_oreveille_oretreat"
    if cfg_temp["mode"] == "raise_wave_lower":
        asyncio.run(move_flag_to(half_mast_pos))
        if kill_process:
            return
        led.duty_cycle = 65000
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            coils_off()
            ply_a_0("reveille")
        asyncio.run(move_flag_to(flag_deploy_max))
        asyncio.run(deploy_flag(flag_up_extra, "up", False))
        if kill_process:
            return
        asyncio.run(rn_an(wave_motor_steps, "up", False, False))
        if kill_process:
            return
        rot.angle = 180
        asyncio.run(deploy_flag(flag_up_extra, "up", False))
        if kill_process:
            return
        asyncio.run(move_flag_to(half_mast_pos))
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            coils_off()
            ply_a_0("retreat")
        if cfg_temp["sound"] == "sound_otaps":
            coils_off()
            ply_a_0("taps")
        led.duty_cycle = 0
        asyncio.run(move_flag_to(0))
        if kill_process:
            return
    elif cfg_temp["mode"] == "raise_lower":
        asyncio.run(move_flag_to(half_mast_pos))
        if kill_process:
            return
        led.duty_cycle = 65000
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            coils_off()
            ply_a_0("reveille")
        asyncio.run(move_flag_to(flag_deploy_max))
        asyncio.run(deploy_flag(flag_up_extra, "up", False))
        if kill_process:
            return
        wait_period = random.randint(5, 10)
        time_done = time.monotonic() + wait_period
        while time.monotonic() < time_done:
            time.sleep(0.05)
            exit_early()
            if kill_process:
                return
        asyncio.run(move_flag_to(half_mast_pos))
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            coils_off()
            ply_a_0("retreat")
        if cfg_temp["sound"] == "sound_otaps":
            coils_off()
            ply_a_0("taps")
        led.duty_cycle = 0
        asyncio.run(move_flag_to(0))
        if kill_process:
            return
    elif cfg_temp["mode"] == "raise_wave":
        asyncio.run(move_flag_to(flag_deploy_max))
        asyncio.run(deploy_flag(flag_up_extra, "up", False))
        led.duty_cycle = 65000
        if kill_process:
            return
        while not kill_process:
            steps = random.randint(300, 600)
            asyncio.run(rn_an(steps, "up", False, False))
            if kill_process:
                return
            coils_off()
            wait_period = random.randint(2, 7)
            time_done = time.monotonic() + wait_period
            while time.monotonic() < time_done:
                time.sleep(0.05)
                exit_early()
                if kill_process:
                    return


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
    global rand_timer

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
        global rand_timer, kill_process
        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
        if sw == "left_held":
            if cfg["timer"] == True:
                cfg["timer"] = False
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                spk_sentence("timer_mode_off")
                return
        elif cfg["timer"] == True:
            if rand_timer <= 0:
                an()
                reset_motors()
                rand_timer = int(cfg["timer_val"]) * 60
                print("an time done")
            else:
                upd_vol(1)
                rand_timer -= 1
        elif sw == "left":
            an()
            kill_process = False
            reset_motors()
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
            elif sel_i == "wave_settings":
                mch.go_to("wave_settings")
            elif sel_i == "museum_settings":
                mch.go_to('museum_settings')
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

class MuseumOpt(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'museum_settings'

    def enter(self, mch):
        files.log_item('Set museum Options')
        spk_sentence("museum_settings_menu")
        spk_sentence("r_l_but")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(l_sw, r_sw, time.sleep, 3.0)
        if sw == "left":
            spk_sentence(muse_set[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(muse_set) - 1:
                self.i = 0
        if sw == "right":
            selected_menu_item = muse_set[self.sel_i]
            if selected_menu_item == "museum_mode_on":
                cfg["museum_mode"] = True
                files.write_json_file("cfg.json", cfg)
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')
            elif selected_menu_item == "museum_mode_off":
                cfg["museum_mode"] = False
                files.write_json_file("cfg.json", cfg)
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')
            else:
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')
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
            if mnu_o[self.sel_i] != "timer_off" and options[0] == "timer":
                cfg["timer"] = True
                cfg["timer_val"] = str(options[1])
                rand_timer = 0
            elif mnu_o[self.sel_i] == "timer_off":
                cfg["timer"] = "timer_off"
                rand_timer = 0
            elif mnu_o[self.sel_i] == "sound_off":
                cfg["sound"] = "sound_off"
            elif mnu_o[self.sel_i] == "sound_otaps":
                cfg["sound"] = "sound_otaps"
            elif mnu_o[self.sel_i] == "sound_oreveille_oretreat":
                cfg["sound"] = "sound_oreveille_oretreat"
            elif mnu_o[self.sel_i] == "random_sound_off":
                cfg["random"] = False
            elif mnu_o[self.sel_i] == "random_sound_on":
                cfg["random"] = True
            elif mnu_o[self.sel_i] == "raise_lower":
                cfg["mode"] = "raise_lower"
            elif mnu_o[self.sel_i] == "raise_wave_lower":
                cfg["mode"] = "raise_wave_lower"
            elif mnu_o[self.sel_i] == "raise_wave":
                cfg["mode"] = "raise_wave"
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
        return "wave_settings"

    def enter(self, mch):
        global kill_process
        files.log_item("Set Web Options")
        spk_sentence("wave_settings_menu")
        spk_sentence("lrdiseng")
        cfg["servo"] = 120
        kill_process = False
        asyncio.run(move_flag_to(flag_deploy_max))
        asyncio.run(deploy_flag(flag_up_extra, "up", False))
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
                ch_servo("lower")
            elif sw == "right":
                ch_servo("raise")
            elif sw == "right_held":
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                rot.angle = 180
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
st_mch.add(MuseumOpt())

aud_en.value = True

upd_vol(0.01)

ply_a_0("homming")
reset_motors()

flash_led()

st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")

while True:
    st_mch.upd()
    upd_vol(0.01)

