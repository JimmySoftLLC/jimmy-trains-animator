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
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


gc_col("Imports gc, files")

################################################################################
# globals
kite_deploy_max = 1700
lst_kite_rot_pos = 90
lst_kite_deploy_pos = 0
kite_min = 0
kite_max = 180
kill_process = False
async_running = False
cont_run = False

################################################################################
# config variables

cfg = files.read_json_file("/cfg.json")

cfg_main = files.read_json_file("main_menu.json")
main_m = cfg_main["main_menu"]

cfg_vol = files.read_json_file("volume_settings.json")
v_set = cfg_vol["volume_settings"]

cfg_opt = files.read_json_file("options.json")
mnu_o = cfg_opt["options"]

print(cfg)

cfg["volume_pot"] = False
cfg["volume"] = 50


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
coil_A_1 = digitalio.DigitalInOut(board.GP4)
coil_A_2 = digitalio.DigitalInOut(board.GP5)
coil_B_1 = digitalio.DigitalInOut(board.GP6)
coil_B_2 = digitalio.DigitalInOut(board.GP7)

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

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup the mixer to play mp3 files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=16384)

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
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        time.sleep(s)


upd_vol(.1)

# Setup the servos
kite_rot = pwmio.PWMOut(board.GP17, duty_cycle=2 ** 15, frequency=50)
kite_rot = servo.Servo(kite_rot, min_pulse=500, max_pulse=2500)
kite_rot.angle = lst_kite_rot_pos


################################################################################
# sound

def ply_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.02)
    print("playing " + file_name)
    w0 = audiomp3.MP3Decoder(open("mp3/" + file_name + ".mp3", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        exit_early()
    print("done playing")


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
    spk_str(cfg["volume"], False)


def spk_str(str_to_speak):
    if (character == "minute" or
        character == "minutes" or
        character == "timer" or
        character == "lower" or
        character == "raise" or
        character == "no" or
            character == "wind"):
        ply_a_0(character)
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
    upd_vol(0.01)
    l_sw.update()
    if l_sw.fell:
        kill_process = True
        mix.voice[0].stop()

################################################################################
# motors


step_down = [
    [0, 0, 1, 1],  # Step 1
    [0, 1, 1, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [1, 0, 0, 1]   # Step 4
]

step_up = [
    [1, 0, 0, 1],  # Step 4
    [1, 1, 0, 0],  # Step 3
    [0, 1, 1, 0],  # Step 2
    [0, 0, 1, 1]   # Step 1
]


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


def servo_m(servo_pos):
    global lst_kite_rot_pos
    if servo_pos < kite_min:
        servo_pos = kite_min
    if servo_pos > kite_max:
        servo_pos = kite_max
    kite_rot.angle = servo_pos
    lst_kite_rot_pos = servo_pos

################################################################################
# async methods


loop = asyncio.get_event_loop()


def rotate_spd():
    if mix.voice[0].playing:
        return 0.002
    else:
        return 0.02


async def rotate_kite_async():
    global lst_kite_rot_pos, async_running
    while async_running:
        rand_pos_1 = random.randint(15, 40)
        rand_pos_2 = random.randint(110, 165)
        sign = 1
        if lst_kite_rot_pos > rand_pos_1:
            sign = -1
        total_steps = abs(rand_pos_1 - lst_kite_rot_pos)
        exit_early()
        for _ in range(total_steps + 1):
            if not async_running or kill_process:
                break
            spd = rotate_spd()
            kite_ang = lst_kite_rot_pos + 1 * sign
            servo_m(kite_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2*spd)
        sign = 1
        if lst_kite_rot_pos > rand_pos_2:
            sign = -1
        total_steps = abs(rand_pos_2 - lst_kite_rot_pos)
        exit_early()
        for _ in range(total_steps + 1):
            if not async_running or kill_process:
                break
            spd = rotate_spd()
            kite_ang = lst_kite_rot_pos + 1 * sign
            servo_m(kite_ang)
            await asyncio.sleep(spd)
        await asyncio.sleep(2*spd)


async def deploy_kite(steps, direction, spd=0.005):
    global async_running, lst_kite_deploy_pos
    if direction == 'down':
        seq = step_down
    elif direction == 'up':
        seq = step_up
    else:
        raise ValueError("Direction must be 'down' or 'up'")
    for i in range(steps):
        if kill_process:
            break
        if direction == 'down':
            lst_kite_deploy_pos -= 1
        elif direction == 'up':
            lst_kite_deploy_pos += 1
        for step in seq:
            set_step(step)
            await asyncio.sleep(spd)
    async_running = False


async def rn_an(steps, direction):
    global async_running
    async_running = True
    rot_k = asyncio.create_task(rotate_kite_async())
    deploy_g = asyncio.create_task(deploy_kite(steps, direction))
    await asyncio.gather(deploy_g, rot_k)

################################################################################
# Animations


def rnd_prob(c):
    y = random.random()
    if y < c:
        return True
    return False


def an():
    global kill_process
    kill_process = False
    w0 = audiomp3.MP3Decoder(open("mp3/wind.mp3", "rb"))
    for _ in range(9):
        if kill_process:
            return
        rand_deploy_pos = random.randint(0, kite_deploy_max)
        if rnd_prob(.2) and not mix.voice[0].playing:
            mix.voice[0].play(w0, loop=False)
        direction = "up"
        if lst_kite_deploy_pos > rand_deploy_pos:
            direction = "down"
        total_steps = abs(rand_deploy_pos - lst_kite_deploy_pos)
        asyncio.run(rn_an(total_steps, direction))
    w0.deinit()
    gc_col("Sound cleanup")
    total_steps = abs(0 - lst_kite_deploy_pos)
    asyncio.run(rn_an(total_steps, "down"))


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
        return ''

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
        return 'base_state'

    def enter(self, mch):
        # set servos to starting position
        ply_a_0("active")
        files.log_item("Entered base Ste")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, fig_web
        sw = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if sw == "left_held":
            if cont_run:
                cont_run = False
                ply_a_0("c_m_off")
            else:
                cont_run = True
                ply_a_0("c_m_on")
        elif sw == "left" or cont_run:
            an()
            print("an done")
        elif sw == "right":
            mch.go_to('main_menu')


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        ply_a_0("m_mnu")
        ply_a_0("l_r_but")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0(main_m[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if r_sw.fell:
            sel_i = main_m[self.sel_i]
            if sel_i == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_i == "volume_settings":
                mch.go_to('volume_settings')
            else:
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')


class VolSet(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, machine):
        files.log_item('Set Web Options')
        ply_a_0("volume_settings_menu")
        ply_a_0("l_r_but")
        Ste.enter(self, machine)

    def exit(self, machine):
        Ste.exit(self, machine)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0(v_set[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(v_set)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = v_set[self.sel_i]
            if sel_mnu == "volume_level_adjustment":
                ply_a_0("volume_adjustment_menu")
                done = False
                while not done:
                    sw = utilities.switch_state(
                        l_sw, r_sw, upd_vol, 3.0)
                    if sw == "left":
                        ch_vol("lower")
                    elif sw == "right":
                        ch_vol("raise")
                    elif sw == "right_held":
                        aud_en.value = False
                        files.write_json_file(
                            "cfg.json", cfg)
                        aud_en.value = True
                        ply_a_0("all_changes_complete")
                        done = True
                        mch.go_to('base_state')
                    upd_vol(0.1)
                    pass
            elif sel_mnu == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["volume"] == 0:
                    cfg["volume"] = 10
                files.write_json_file("cfg.json", cfg)
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')
            elif sel_mnu == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("cfg.json", cfg)
                ply_a_0("all_changes_complete")
                mch.go_to('base_state')


class Snds(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        ply_a_0("sound_selection_menu")
        ply_a_0("l_r_but")
        Ste.enter(self, machine)

    def exit(self, machine):
        Ste.exit(self, machine)

    def upd(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            ply_a_0(mnu_o[self.i])
            self.sel_i = self.i
            self.i += 1
            if self.i > len(mnu_o)-1:
                self.i = 0
        if r_sw.fell:
            cfg["option_selected"] = mnu_o[self.sel_i]
            files.write_json_file("cfg.json", cfg)
            ply_a_0(cfg["option_selected"])
            machine.go_to('base_state')


###############################################################################
# Create the Ste mch

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(VolSet())
st_mch.add(Snds())

aud_en.value = True

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.upd()
    upd_vol(.1)
