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


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item(
        "Point " + collection_point + " Available memory: {} bytes".format(start_mem)
    )


gc_col("Imports gc, files")

################################################################################
# globals

kill_process = False
cont_run = False
rand_timer = 0
flag_deploy_max = 1100
lst_flag_deploy_pos = flag_deploy_max
half_mast_pos = flag_deploy_max / 2
flag_up_extra = 50

wave_motor_steps = 1000
flag_rot_min = 0
flag_rot_max = 180
lst_flag_rot_pos = flag_rot_max
flag_ext = 3

################################################################################
# config variables

cfg = files.read_json_file("cfg.json")

cfg_main = files.read_json_file("main_menu.json")
main_m = cfg_main["main_menu"]

cfg_vol = files.read_json_file("volume_settings.json")
v_set = cfg_vol["volume_settings"]

cfg_opt = files.read_json_file("options.json")
mnu_o = cfg_opt["options"]

print(cfg)

################################################################################
# setup hardware

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
coil_A_1 = digitalio.DigitalInOut(board.GP7)
coil_A_2 = digitalio.DigitalInOut(board.GP6)
coil_B_1 = digitalio.DigitalInOut(board.GP5)
coil_B_2 = digitalio.DigitalInOut(board.GP4)

# Set the pins as outputs
coil_A_1.direction = digitalio.Direction.OUTPUT
coil_A_2.direction = digitalio.Direction.OUTPUT
coil_B_1.direction = digitalio.Direction.OUTPUT
coil_B_2.direction = digitalio.Direction.OUTPUT

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

# Setup the mixer to play mp3 files
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

# Setup the servos
flag_rot = pwmio.PWMOut(board.GP16, duty_cycle=2**15, frequency=50)
flag_rot = servo.Servo(flag_rot, min_pulse=500, max_pulse=2500)

# Set up the led
digitalio.DigitalInOut
led = pwmio.PWMOut(board.GP8, frequency=5000, duty_cycle=0)

################################################################################
# sound


def ply_a_0(file_name):
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
    w0.deinit()
    gc_col("Clear w0")
    print("done playing")


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
        mix.voice[0].stop()
        coils_off()
        flag_rot.angle = 180


def reset_motors():
    global kill_process
    kill_process = False
    flag_rot.angle = 180
    move_motor(0)  # Flag down
    coils_off()
    led.duty_cycle = 0
    
def flash_led():
    for _ in range(3):
        led.duty_cycle = 65000
        time.sleep(.75)
        led.duty_cycle = 0
        time.sleep(.75)


################################################################################
# motors

step_down = [
    [0, 0, 1, 1],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [1, 0, 0, 1],  # Step 4
]

step_up = [
    [1, 0, 0, 1],  # Step 4
    [1, 1, 0, 0],  # Step 3
    [0, 1, 1, 0],  # Step 2
    [0, 0, 1, 1],  # Step 1
]


def coils_off():
    coil_A_1.value = 0
    coil_A_2.value = 0
    coil_B_1.value = 0
    coil_B_2.value = 0


def set_step(step):
    coil_A_1.value = step[0]
    coil_A_2.value = step[1]
    coil_B_1.value = step[2]
    coil_B_2.value = step[3]


def servo_m(servo_pos):
    global lst_flag_rot_pos
    if servo_pos < flag_rot_min:
        servo_pos = flag_rot_min
    if servo_pos > flag_rot_max:
        servo_pos = flag_rot_max
    flag_rot.angle = servo_pos
    lst_flag_rot_pos = servo_pos


def move_motor(pos, keep_track=True):
    global lst_flag_deploy_pos, async_running
    direction = "up"
    if lst_flag_deploy_pos > pos:
        direction = "down"
    total_steps = abs(pos - lst_flag_deploy_pos)
    delay = 0.005
    if direction == "down":
        seq = step_down
    elif direction == "up":
        seq = step_up
    for _ in range(total_steps):
        exit_early()
        if kill_process:
            return
        if direction == "down":
            if keep_track:
                lst_flag_deploy_pos -= 1
        elif direction == "up":
            if keep_track:
                lst_flag_deploy_pos += 1
        for step in seq:
            set_step(step)
            time.sleep(delay)
    print(lst_flag_deploy_pos)


################################################################################
# async methods

loop = asyncio.get_event_loop()


def rotate_spd():
    if mix.voice[0].playing:
        return 0.005
    else:
        return random.uniform(0.03, 0.03)


def rnd_prob(c):
    y = random.random()
    if y < c:
        return True
    return False


async def wave_flag(rand):
    global lst_flag_rot_pos, async_running
    center_servo_pos = int(cfg["servo"])
    while async_running:
        if rand:
            pos_1 = random.randint(center_servo_pos - flag_ext, center_servo_pos)
            pos_2 = random.randint(center_servo_pos, center_servo_pos + flag_ext)
        else:
            pos_1 = center_servo_pos - flag_ext
            pos_2 = center_servo_pos + flag_ext
        sign = 1
        if lst_flag_rot_pos > pos_1:
            sign = -1
        total_steps = abs(pos_1 - lst_flag_rot_pos)
        exit_early()
        if not async_running or kill_process:
            break
        spd = rotate_spd()
        for _ in range(total_steps + 1):
            flag_ang = lst_flag_rot_pos + 1 * sign
            servo_m(flag_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)
        sign = 1
        if lst_flag_rot_pos > pos_2:
            sign = -1
        total_steps = abs(pos_2 - lst_flag_rot_pos)
        exit_early()
        if not async_running or kill_process:
            break
        for _ in range(total_steps + 1):
            spd = rotate_spd()
            flag_ang = lst_flag_rot_pos + 1 * sign
            servo_m(flag_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2 * spd)


async def deploy_flag(steps, direction, spd=0.005):
    global async_running
    if direction == "down":
        seq = step_down
    elif direction == "up":
        seq = step_up
    else:
        raise ValueError("Direction must be 'down' or 'up'")
    for _ in range(steps):
        if kill_process:
            break
        for step in seq:
            set_step(step)
            await asyncio.sleep(spd)
    async_running = False


async def rn_an(steps, direction, rand):
    global async_running
    async_running = True
    rot_f = asyncio.create_task(wave_flag(rand))
    deploy_f = asyncio.create_task(deploy_flag(steps, direction))
    await asyncio.gather(deploy_f, rot_f)


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
        move_motor(half_mast_pos)  # Flag up
        if kill_process:
            return
        led.duty_cycle = 65000
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            ply_a_0("reveille")
        move_motor(flag_deploy_max)  # Flag up
        move_motor(flag_deploy_max + flag_up_extra, False)  # Flag up dont keep track
        if kill_process:
            return
        asyncio.run(rn_an(wave_motor_steps, "up", False))  # Flag wave
        if kill_process:
            return
        flag_rot.angle = 180
        move_motor(
            flag_deploy_max + flag_up_extra, False
        )  # Flag up dont keep track to orient it before going down
        if kill_process:
            return
        move_motor(half_mast_pos)  # Flag down
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            ply_a_0("retreat")
        if cfg_temp["sound"] == "sound_otaps":
            ply_a_0("taps")
        led.duty_cycle = 0
        move_motor(0)  # Flag down
        if kill_process:
            return
    elif cfg_temp["mode"] == "raise_lower":
        move_motor(half_mast_pos)  # Flag up
        if kill_process:
            return
        led.duty_cycle = 65000
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            ply_a_0("reveille")
        move_motor(flag_deploy_max + flag_up_extra)  # Flag up
        if kill_process:
            return
        wait_period = random.randint(5, 10)
        time_done = time.monotonic() + wait_period
        while time.monotonic() < time_done:
            time.sleep(0.05)
            exit_early()
            if kill_process:
                return
        move_motor(half_mast_pos)  # Flag down
        if cfg_temp["sound"] == "sound_oreveille_oretreat":
            ply_a_0("retreat")
        if cfg_temp["sound"] == "sound_otaps":
            ply_a_0("taps")
        led.duty_cycle = 0
        move_motor(0)  # Flag down
        if kill_process:
            return
    elif cfg_temp["mode"] == "raise_wave":
        move_motor(flag_deploy_max)  # Flag up
        move_motor(flag_deploy_max + flag_up_extra, False)  # Flag up dont keep track
        led.duty_cycle = 65000
        if kill_process:
            return
        while not kill_process:
            steps = random.randint(300, 600)
            asyncio.run(rn_an(steps, "up", False))  # Flag wave
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
        global cont_run, fig_web, rand_timer
        sw = utilities.switch_state(l_sw, r_sw, upd_vol, 3.0)
        if sw == "left_held":
            if cfg["timer"] == True:
                cfg["timer"] = False
                cont_run = False
                aud_en.value = False
                files.write_json_file("cfg.json", cfg)
                aud_en.value = True
                spk_sentence("timer_mode_off")
                return
            if cont_run:
                cont_run = False
                spk_sentence("continuous_mode_off")
            elif cfg["timer"] == False:
                cont_run = True
                spk_sentence("continuous_mode_on")
        elif cfg["timer"] == True:
            if rand_timer <= 0:
                an()
                reset_motors()
                rand_timer = int(cfg["timer_val"]) * 60
                print("an time done")
            else:
                upd_vol(1)
                rand_timer -= 1
        elif sw == "left" or cont_run:
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
        move_motor(flag_deploy_max)  # Flag up
        move_motor(flag_deploy_max + flag_up_extra, False)  # Flag up dont keep track
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
                flag_rot.angle = 180
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

reset_motors()

flash_led()

st_mch.go_to("base_state")
files.log_item("animator has started...")
gc_col("animations started")

while True:
    st_mch.upd()
    upd_vol(0.01)
