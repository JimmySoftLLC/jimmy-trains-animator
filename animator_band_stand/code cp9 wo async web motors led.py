import utilities
from adafruit_debouncer import Debouncer
from analogio import AnalogIn
import microcontroller
import rtc
import random
import board
import digitalio
import busio
import storage
import sdcardio
import audiobusio
import audiomixer
import audiocore
import time
import gc
import files
import os


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
# Setup hardware

# Setup pin for vol
a_in = AnalogIn(board.A0)

# setup pin for audio enable 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP6)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP7)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup sdCard
aud_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)
aud.play(mix)

mix.voice[0].level = .2

try:
    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
except:
    w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
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
                    open("/sd/mvc/micro_sd_card_success.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass
            except:
                w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
                mix.voice[0].play(w0, loop=False)
                while mix.voice[0].playing:
                    pass

aud_en.value = False

# Setup the servos

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card config variables

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = files.return_directory("", "/sd/snds", ".wav")

cust_snd_opt = files.return_directory(
    "customers_owned_music_", "/sd/customers_owned_music", ".wav")

all_snd_opt = []
all_snd_opt.extend(snd_opt)
all_snd_opt.extend(cust_snd_opt)

menu_snd_opt = []
menu_snd_opt.extend(snd_opt)
rnd_opt = ['random all', 'random built in', 'random my']
menu_snd_opt.extend(rnd_opt)
menu_snd_opt.extend(cust_snd_opt)

ts_jsons = files.return_directory(
    "", "/sd/t_s_def", ".json")

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfd_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfd_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    "/sd/mvc/add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False

gc_col("config setup")

################################################################################
# Setup neo pixels

num_px = 2

# 15 on demo 17 tiny 10 on large
# led = neopixel.NeoPixel(board.GP17, num_px)

gc_col("Neopixels setup")

################################################################################
# Setup wifi and web server

# gc_col("web server")

################################################################################
# Global Methods


def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"

################################################################################
# Dialog and sound play methods


def upd_vol(seconds):
    if cfg["volume_pot"]:
        volume = a_in.value / 65536
        mix.voice[0].level = volume
        time.sleep(seconds)
    else:
        try:
            volume = int(cfg["volume"]) / 100
        except:
            volume = .5
        if volume < 0 or volume > 1:
            volume = .5
        mix.voice[0].level = volume
        time.sleep(seconds)


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
    files.write_json_file("/sd/cfg.json", cfg)
    play_a_0("/sd/mvc/volume.wav")
    spk_str(cfg["volume"], False)


def play_a_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            upd_vol(0.1)
    wave0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(wave0, loop=False)
    while mix.voice[0].playing:
        exit_early()


def stop_a_0():
    mix.voice[0].stop()
    while mix.voice[0].playing:
        pass


def exit_early():
    upd_vol(0.1)
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
            play_a_0("/sd/mvc/" + character + ".wav")
        except:
            print("Invalid character in string to speak")
    if addLocal:
        play_a_0("/sd/mvc/dot.wav")
        play_a_0("/sd/mvc/local.wav")


def l_r_but():
    play_a_0("/sd/mvc/press_left_button_right_button.wav")


def sel_web():
    play_a_0("/sd/mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    play_a_0("/sd/mvc/option_selected.wav")


def spk_sng_num(song_number):
    play_a_0("/sd/mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    play_a_0("/sd/mvc/no_user_soundtrack_found.wav")
    while True:
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            break
        if r_sw.fell:
            play_a_0("/sd/mvc/create_sound_track_files.wav")
            break


def spk_web():
    play_a_0("/sd/mvc/animator_available_on_network.wav")
    play_a_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-bandstand":
        play_a_0("/sd/mvc/animator_dash_bandstand.wav")
        play_a_0("/sd/mvc/dot.wav")
        play_a_0("/sd/mvc/local.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_a_0("/sd/mvc/in_your_browser.wav")


p_arr = [90, 90, 90, 90, 90, 90]


def cyc_servo(n, s, p_up, p_dwn):
    global p_arr
    while mix.voice[0].playing:
        n_p = p_up
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            time.sleep(s)
        n_p = p_dwn
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            time.sleep(s)


def m_servo(n, p):
    global p_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    #s_arr[n].angle = p
    p_arr[n][n] = p

################################################################################
# animations


lst_opt = ""


def an(f_nm):
    global cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        if f_nm == "random built in":
            h_i = len(snd_opt) - 1
            cur_opt = snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(snd_opt) > 1:
                cur_opt = snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        elif f_nm == "random my":
            h_i = len(cust_snd_opt) - 1
            cur_opt = cust_snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(cust_snd_opt) > 1:
                cur_opt = cust_snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        elif f_nm == "random all":
            h_i = len(all_snd_opt) - 1
            cur_opt = all_snd_opt[random.randint(
                0, h_i)]
            while lst_opt == cur_opt and len(all_snd_opt) > 1:
                cur_opt = all_snd_opt[random.randint(
                    0, h_i)]
            lst_opt = cur_opt
            print("Random sound option: " + f_nm)
            print("Sound file: " + cur_opt)
        if ts_mode:
            an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            an_light(cur_opt)
            gc_col("animation cleanup")
    except:
        no_trk()
        cfg["option_selected"] = "random built in"
        return
    gc_col("Animation complete.")


def an_light(f_nm):
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm

    flsh_t = []

    if cust_f:
        f_nm = f_nm.replace("customers_owned_music_", "")
        if (f_exists("/sd/customers_owned_music/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "/sd/customers_owned_music/" + f_nm + ".json")
        else:
            try:
                flsh_t = files.read_json_file(
                    "/sd/customers_owned_music/" + f_nm + ".json")
            except:
                play_a_0("/sd/mvc/no_timestamp_file_found.wav")
                while True:
                    l_sw.update()
                    r_sw.update()
                    if l_sw.fell:
                        ts_mode = False
                        return
                    if r_sw.fell:
                        ts_mode = True
                        play_a_0("/sd/mvc/timestamp_instructions.wav")
                        return
    else:
        if (f_exists("/sd/snds/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "/sd/snds/" + f_nm + ".json")

    flsh_i = 0

    if cust_f:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + f_nm + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/snds/" + f_nm + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)
    srt_t = time.monotonic()

    ft1 = []
    ft2 = []

    while True:
        t_past = time.monotonic()-srt_t
        if flsh_i < len(flsh_t)-2:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0
        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-2:
            print("time elapsed: " + str(t_past) +
                  " Timestamp: " + ft1[0])
            flsh_i += 1
            if (len(ft1) == 1 or ft1[1] == ""):
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                set_hdw("L0" + str(lgt) + ",S0" + str(pos))
            else:
                set_hdw(ft1[1])
        l_sw.update()
        if l_sw.fell and cfg["can_cancel"]:
            mix.voice[0].stop()
        if not mix.voice[0].playing:
            # led.fill((0, 0, 0))
            # led.show()
            return
        upd_vol(.1)


def an_ts(f_nm):
    print("time stamp mode")
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm

    t_s = []

    f_nm = f_nm.replace("customers_owned_music_", "")

    if cust_f:
        wave0 = audiocore.WaveFile(
            open("/sd/customers_owned_music/" + f_nm + ".wav", "rb"))
    else:
        wave0 = audiocore.WaveFile(
            open("/sd/snds/" + f_nm + ".wav", "rb"))
    mix.voice[0].play(wave0, loop=False)

    startTime = time.monotonic()
    upd_vol(.1)

    while True:
        t_elsp = round(time.monotonic()-startTime, 1)
        r_sw.update()
        if r_sw.fell:
            t_s.append(str(t_elsp) + "|")
            print(t_elsp)
        if not mix.voice[0].playing:
            # led.fill((0, 0, 0))
            # led.show()
            t_s.append(5000)
            if cust_f:
                files.write_json_file(
                    "/sd/customers_owned_music/" + f_nm + ".json", t_s)
            else:
                files.write_json_file(
                    "/sd/snds/" + f_nm + ".json", t_s)
            break

    ts_mode = False
    play_a_0("/sd/mvc/timestamp_saved.wav")
    play_a_0("/sd/mvc/timestamp_mode_off.wav")
    play_a_0("/sd/mvc/animations_are_now_active.wav")

##############################
# animation effects


sp = [0, 0, 0, 0, 0, 0]
br = 0


def set_hdw(input_string):
    global sp, br
    # Split the input string into segments
    segs = input_string.split(",")

    # Process each segment
    for seg in segs:
        if seg[0] == 'L':  # lights
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    sp[i] = v
            else:
                sp[num-1] = int(v)
            # led[0] = (sp[1], sp[0], sp[2])
            # led[1] = (sp[4], sp[3], sp[5])
            # led.show()
        if seg[0] == 'S':  # servos
            num = int(seg[1])
            v = int(seg[2:])
            # if num == 0:
            #     for i in range(6):
            #         s_arr[i].angle = v
            # else:
            #     s_arr[num-1].angle = int(v)
        if seg[0] == 'B':  # brightness
            br = int(seg[1:])
            # led.brightness = float(br/100)
        if seg[0] == 'F':  # fade in or out
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    # led.brightness = float(br/100)
                else:
                    br -= 1
                    # led.brightness = float(br/100)
                upd_vol(.1)

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
        play_a_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, upd_vol, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
                play_a_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                play_a_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
            an(cfg["option_selected"])
        elif switch_state == "right":
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
        play_a_0("/sd/mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_a_0("/sd/mvc/" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if r_sw.fell:
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "volume_settings":
                mch.go_to('volume_settings')
            else:
                play_a_0("/sd/mvc/all_changes_complete.wav")
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
        play_a_0("/sd/mvc/sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                try:
                    wave0 = audiocore.WaveFile(open(
                        "/sd/o_snds/" + menu_snd_opt[self.i] + ".wav", "rb"))
                    mix.voice[0].play(wave0, loop=False)
                except:
                    spk_sng_num(str(self.i+1))
                self.sel_i = self.i
                self.i += 1
                if self.i > len(menu_snd_opt)-1:
                    self.i = 0
                while mix.voice[0].playing:
                    pass
        if r_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                cfg["option_selected"] = menu_snd_opt[self.sel_i]
                files.write_json_file("/sd/cfg.json", cfg)
                wave0 = audiocore.WaveFile(
                    open("/sd/mvc/option_selected.wav", "rb"))
                mix.voice[0].play(wave0, loop=False)
                while mix.voice[0].playing:
                    pass
            mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())

aud_en.value = True

upd_vol(.1)

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    st_mch.upd()
    upd_vol(.1)

