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
# this code requires the following installs

# blinka is a lib that allows you to use circuit python libraries for servos, light etc. search adafruit blinka for instructions

# control lifx lights using lifxlan 1.2.7 and confirm its version
# pip install lifxlan==1.2.7
# pip show lifxlan

# to use lifx lan you must use the bytestring 3.1.9 library and confirm its version
# pip install bitstring==3.1.9
# pip show bitstring

# on screen keyboard, onboard
# sudo apt install onboard

# text to speech using gtts 2.5.3 and confirm its version
# pip install gtts
# pip show gtts

# Units with a touchscreen use a html page and material UI for styling
# Midori, a lightweight browser, is used so it can run on any pi
# install midori and confirm its version
# sudo apt install midori==7.0
# midori --version

# Scripts can be modified via a webpage that the drivein will serve to your location network.
# It might be easier to use a spreadsheet program.  So install libra office on the pi so
# customers can use it to modify scripts too.
# Install with
# sudo apt update
# sudo apt install libreoffice

# The user will want to modify audio files locally so install audocity using
# sudo apt install audacity. Recommend to limit wav music to -10db and wav menu files to -12, mp4 -10


# for touch screen products the display on vnc will default to the touch screen
# resolution which is very low.  During dev you might want to use these three commands
# to set it higher, note these will reset at reboot.  Do not make these permanent.
# xrandr --newmode "1920x1080_60.00"  173.00  1920 2048 2248 2576  1080 1083 1088 1120 -hsync +vsync
# xrandr --addmode HDMI-1 "1920x1080_60.00"
# xrandr --output HDMI-1 --mode "1920x1080_60.00"

# i2s audio is setup on pi itself using an overlay, there is no hardware that needs to be set up in python
# the i2s amps are on the JimmyTrains ANPISBC HAT which provides the audio.  The amps have an audio enable
# feature that is controlled via pin 26.  It is enabled by this program just before it announces the animations are active
# The volume is also controlled by this program.  So the volume control on the pi has no effect.
# The amp circuits are set to the highest possible gain so audio tracks and movies should be normalized to -10.0dB to avoid
# clipping.

#######################################################
# prod files are located in the code folder on the user machine
# debug the code.py, files.py and utilities.py in the home directory
# Delete code.py, files.py and utilities.py in the home directory after release

############################################################
# Units will automatically startup up after reboot.   This can happen in a terminal window or in the backgournd.
# To kill the backgournd process enter pkill -f code.py in the terminal

###########################################################
# sudo apt-get install pulseaudio

############################################################
# This code will automatically create wav files for folder names to make this work you need
# gtts and pydub install these as follows
# pip install gtts
# sudo apt install ffmpeg
# pip install pydub


import re
from adafruit_servokit import ServoKit
from lifxlan import LifxLAN
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
from http import server
import socket
import socketserver
import threading
from zeroconf import ServiceInfo, Zeroconf
import json
import os
import gc
import vlc
import board
import digitalio
from adafruit_debouncer import Debouncer
import neopixel_spi
from rainbowio import colorwheel
import pygame
import gc
import files
import utilities
import psutil
import random
from gtts import gTTS
import requests
from lifxlan import BLUE, CYAN, GREEN, LifxLAN, ORANGE, PINK, PURPLE, RED, YELLOW
import subprocess
import time
import netifaces
from collections import OrderedDict, deque
import signal
import copy
from pydub import AudioSegment
import sys
import asyncio
import websockets
import pyautogui
import io
from typing import Dict, Any


# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.D26)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False


def get_home_path(subpath=""):
    # Get the current user's home directory
    home_dir = os.path.expanduser("~")
    # Return the full path by appending the optional subpath
    return os.path.join(home_dir, subpath)

################################################################################
# Globals


code_folder = get_home_path() + "code/"
media_folder = get_home_path() + "media/"
mvc_folder = code_folder + "mvc/"
animations_folder = get_home_path() + "media/animations/"
buttons_folder = get_home_path() + "media/buttons/"
snd_opt_folder = code_folder + "snd_opt/"
current_media_playing = ""
current_scene = ""
current_neo = ""
is_midori_running = False
override_switch_state = {}
override_switch_state["switch_value"] = ""
group_index = 1
is_button_mode = False

elves_folder = media_folder + "elves/"
elves_folder = media_folder + "elves/"
bells_folder = media_folder + "bells/"
horns_folder = media_folder + "horns/"
stops_folder = media_folder + "stops/"
santa_folder = media_folder + "santa/"
story_folder = media_folder + "story/"
cut_folder = media_folder + "cut/"
recording_folder = media_folder + "recording/"
shutter_folder = media_folder + "shutter/"
quotes_folder = media_folder + "quotes/"

FOLDER_MAP = {
    'E': elves_folder,
    'B': bells_folder,
    'H': horns_folder,
    'T': stops_folder,
    'S': santa_folder,
    'Z': story_folder,
    'C': cut_folder,
    'R': recording_folder,
    'X': shutter_folder,
    'Q': quotes_folder,
    'M': animations_folder
}

media_index = {'E': 0, 'B': 0, 'H': 0, 'T': 0,
               'S': 0, 'Z': 0, 'C': 0, 'R': 0, 'X': 0, 'Q': 0, 'M': 0}

################################################################################
# Loading image as wallpaper on pi


def replace_extension_to_jpg(image_path):
    # Create the new image path with .jpg extension
    new_image_path = os.path.splitext(image_path)[0] + '.jpg'

    # Check if the original file exists
    if os.path.exists(new_image_path):
        return new_image_path
    else:
        print(f"File not found: {new_image_path}")
        return None


wallpaper_lock = threading.Lock()


def change_wallpaper(image_path):
    # Attempt to acquire the lock using a context manager
    with wallpaper_lock:  # This ensures the lock is released properly
        try:
            new_image_path = replace_extension_to_jpg(image_path)

            if new_image_path:
                # Output will be 'path/to/your/image.jpg'
                print(new_image_path)
            else:
                new_image_path = media_folder + 'pictures/black.jpg'

            # Update the wallpaper in the desktop-items-0.conf file
            config_path = get_home_path() + '.config/pcmanfm/LXDE-pi/desktop-items-0.conf'

            # Read the config file
            with open(config_path, 'r') as file:
                config = file.readlines()

            # Modify the wallpaper path
            with open(config_path, 'w') as file:
                for line in config:
                    if line.startswith('wallpaper='):
                        file.write(f'wallpaper={new_image_path}\n')
                    else:
                        file.write(line)

            # Refresh the desktop, os.system will only return when finished
            os.system('pcmanfm --reconfigure')
            print("Wallpaper updated.")

            # Temporarily disable the fail-safe for this operation
            pyautogui.FAILSAFE = False

            # Move the mouse off-screen (e.g., to the right and bottom)
            pyautogui.moveTo(1920, 1080)

            # After moving the mouse, re-enable the fail-safe
            pyautogui.FAILSAFE = True

        except Exception as e:
            print(f"Image load error: {e}")


change_wallpaper(media_folder + 'pictures/black.jpg')


def f_exists(filename):
    try:
        status = os.stat(filename)
        f_exists = True
    except OSError:
        f_exists = False
    return f_exists


def gc_col(collection_point):
    gc.collect()
    start_mem = psutil.virtual_memory()[1]
    print("Point " + collection_point +
          " Available memory: {} bytes".format(start_mem))

################################################################################
# reset pi setup
# to make this work you must add permission to the visudo file
# sudo visudo
# cameratrain ALL=(ALL) NOPASSWD: /sbin/reboot


def restart_pi():
    os.system('sudo reboot')


def restart_pi_timer():
    play_mix_media(mvc_folder + "mvc/restarting_animator_kiosk.wav")
    delay = 2
    timer = threading.Timer(delay, restart_pi)
    timer.start()


gc_col("Imports gc, files")

################################################################################
# ssid and password setup
# to make this work you must add permission to the visudo file
# sudo visudo
# cameratrain ALL=(ALL) NOPASSWD: /usr/bin/nmcli

# Function to mount the USB drive (assumes automatic mounting to /media/pi)


def get_usb_path():
    media_path = "/media/cameratrain/"
    usb_path = None
    for root, dirs, files in os.walk(media_path):
        if 'env.txt' in files:
            usb_path = os.path.join(root, 'env.txt')
            break
    return usb_path

# Function to read the SSID and PASSWORD from the file


def read_wifi_credentials(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ssid = None
    password = None
    for line in lines:
        if line.startswith('SSID='):
            ssid = line.strip().split('=')[1]
        elif line.startswith('PASSWORD='):
            password = line.strip().split('=')[1]
        elif line.startswith('PRIORITY='):
            priority = line.strip().split('=')[1]
    return ssid, password, priority


def connect_wifi(ssid, password, priority):
    """
    Adds (or updates) a Wi-Fi connection with maximum priority (99)
    so it is ALWAYS chosen over any old/existing networks.
    """

    # Remove any existing connection with the same name first (clean slate for this SSID)
    subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                   capture_output=True)

    # Add the new connection with priority 99
    cmd = [
        'sudo', 'nmcli', 'connection', 'add',
        'type',             'wifi',
        'con-name',         ssid,           # name = SSID, looks clean
        'ifname',           'wlan0',
        'ssid',             ssid,
        'wifi-sec.key-mgmt', 'wpa-psk',
        'wifi-sec.psk',     password,
        'connection.autoconnect',         'yes',        # auto-connect enabled
        'connection.autoconnect-priority', priority           # ← THIS IS THE MAGIC
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Failed to add connection:")
        print(result.stderr)
        return False

    return True

# Update ssid password using usb drive


def update_ssid_password_from_usb():
    print("Looking for USB with Wi-Fi configuration...")
    while True:
        usb_path = get_usb_path()
        if usb_path:
            print(f"Found USB with Wi-Fi config at: {usb_path}")
            ssid, password, priority = read_wifi_credentials(usb_path)
            print("Using SSID: " + ssid + " and password: " + password)
            if ssid:
                print(f"Setting up Wi-Fi connection with SSID: {ssid}")
                connect_wifi(ssid, password, priority)
                break
        else:
            print("Waiting for USB to be inserted...")
            time.sleep(5)  # Check every 5 seconds for the USB


################################################################################
# config variables

cfg = files.read_json_file(code_folder + "cfg.json")
default_cfg = files.read_json_file(code_folder + "default_cfg.json")

button_groups = {}


def parse_button_list(items):
    list_output = {}
    if not isinstance(items, list):
        raise ValueError(f"Expected list, got {type(items).__name__}")

    for row in items:
        if not isinstance(row, str) or "|" not in row:
            # skip unexpected rows
            continue
        key, val = row.split("|", 1)
        key = key.strip()
        val = val.strip()
        if key:
            list_output[str(key)] = val
    return list_output


def upd_media():
    global snd_opt, menu_snd_opt, button_opt, button_groups

    snd_opt = files.return_directory("", animations_folder, ".json")
    button_opt = files.return_directory("", buttons_folder, ".json")

    button_groups = {}

    for base_name in button_opt:
        filename = base_name + ".json"
        try:
            raw = files.read_json_file(buttons_folder + filename)

            # raw is like ["1|...", "2|..."]
            button_groups[str(base_name)] = parse_button_list(raw)

        except Exception as e:
            print(f"Failed on {filename}: {e}")

    print("Sound options are:", json.dumps(
        snd_opt, indent=2, ensure_ascii=False))
    print("Button groups are:", json.dumps(
        button_groups, indent=2, ensure_ascii=False))

    menu_snd_opt = list(snd_opt)
    menu_snd_opt.append("random all")


def get_button_value(group_idx, button_idx, default=None):
    group_key = str(group_idx)
    button_key = str(button_idx)

    group = button_groups.get(group_key)
    if group is None:
        return default

    return group.get(button_key, default)


upd_media()

web = True

cfg_main = files.read_json_file(mvc_folder + "main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(mvc_folder + "web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file(mvc_folder + "volume_settings.json")
vol_set = cfg_vol["volume_settings"]

cfg_add_song = files.read_json_file(
    mvc_folder + "add_sounds_animate.json")
add_snd = cfg_add_song["add_sounds_animate"]

cont_run = False
ts_mode = False
lst_opt = ''
running_mode = ""
is_gtts_reachable = False
mix_is_paused = False
exit_set_hdw = False
local_ip = ""
t_s = []
t_elsp = 0.0


################################################################################
# Setup io hardware


switch_io_1 = digitalio.DigitalInOut(board.D17)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP

switch_io_2 = digitalio.DigitalInOut(board.D27)

switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP

switch_io_3 = digitalio.DigitalInOut(board.D22)
switch_io_3.direction = digitalio.Direction.INPUT
switch_io_3.pull = digitalio.Pull.UP

switch_io_4 = digitalio.DigitalInOut(board.D5)
switch_io_4.direction = digitalio.Direction.INPUT
switch_io_4.pull = digitalio.Pull.UP

switch_io_5 = digitalio.DigitalInOut(board.D6)
switch_io_5.direction = digitalio.Direction.INPUT
switch_io_5.pull = digitalio.Pull.UP

l_sw = Debouncer(switch_io_1)
r_sw = Debouncer(switch_io_2)
three_sw = Debouncer(switch_io_3)
four_sw = Debouncer(switch_io_4)
five_sw = Debouncer(switch_io_5)

################################################################################
# Setup sound

mix = None
mix_media = None

# Setup the mixer to play wav files


def pygame_mixer_init():
    global mix, mix_media
    if not mix:
        try:
            pygame.mixer.init()
            mix = pygame.mixer.Channel(0)
            mix_media = pygame.mixer.Channel(1)
        except Exception as e:
            print(f"Error while setting up audio: {e}")
            mix = None
            mix_media = None


def pygame_mixer_quit():
    global mix, mix_media
    if mix:
        mix.stop()
    if mix_media:
        mix_media.stop()
    mix = None
    mix_media = None
    pygame.mixer.quit()


pygame_mixer_init()

################################################################################
# Setup video hardware

# create vlc media player object for playing video, music etc
vlc_instance = vlc.Instance()
media_player = vlc.MediaPlayer(vlc_instance)


def play_movie_file(movie_filename):
    # Load media
    media = vlc_instance.media_new(movie_filename)
    media_player.set_media(media)

    media_player.set_fullscreen(True)

    # Play the video
    media_player.play()

    while not media_player.is_playing():
        time.sleep(.05)


def pause_movie():
    media_player.pause()


def play_movie():
    media_player.play()


def media_player_state():
    state = media_player.get_state()
    if state == vlc.State.Playing:
        return "Playing"
    elif state == vlc.State.Paused:
        return "Paused"
    elif state == vlc.State.Stopped:
        return "Stopped"
    elif state == vlc.State.Ended:
        return "Ended"
    else:
        return "Other state"

################################################################################


kit = ServoKit(channels=16)

# Setup servo hardware, new hat has 8 motor output pads, only 4 are used for camera car
# For a 180-degree servo, the typical pulse width range is 1ms to 2ms, with 1ms
# often being one end (0 degrees) and 2ms the other (180 degrees), though some
# servos use a wider range like 500µs (0.5ms) to 2500µs (2.5ms) for the full
# 180-degree sweep, with 1500µs at the center; always check the specific servo's
# datasheet as ranges can vary. Prototype used a 300-2700 pulse width range,
# but new boards use the standard range of 500 to 2500.
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)
kit.servo[2].set_pulse_width_range(500, 2500)
kit.servo[3].set_pulse_width_range(500, 2500)

s_1 = kit.servo[0]
s_2 = kit.servo[1]
s_3 = kit.servo[2]
s_4 = kit.servo[3]

p_arr = [90, 90, 90, 90]

s_arr = [s_1, s_2, s_3, s_4]


def m_servo(n, p):
    global p_arr

    # Clamp input to 0-180
    if p < 0:
        p = 0
    if p > 180:
        p = 180

    p_arr[n] = p

    # List of servos that are mounted "backwards"
    inverted_servos = {3}

    if n in inverted_servos:
        p = 180 - p

    s_arr[n].angle = p


def m_servo_s(n, n_pos, spd=0.01):
    global p_arr
    sign = 1
    if p_arr[n] > n_pos:
        sign = - 1
    for p in range(p_arr[n], n_pos, sign):
        m_servo(n, p)
        time.sleep(spd)
    m_servo(n, p)


################################################################################
# Create an ordered dictionary to preserve the order of insertion
neo_changes = OrderedDict(cfg["neo_changes"])

# Get the ordered list of keys
ordered_neo_changes_keys = list(neo_changes.keys())

trees = []
canes = []
ornmnts = []
stars = []
brnchs = []
cane_s = []
cane_e = []

bars = []
bolts = []
noods = []
neos = []

bar_arr = []
bolt_arr = []
neo_arr = []

n_px = 0
led = neopixel_spi.NeoPixel_SPI(
    board.SPI(), n_px, brightness=1.0, auto_write=False)


def bld_tree(p):
    i = []
    for t in trees:
        for ledi in t:
            si = ledi
            break
        if p == "ornaments":
            for ledi in range(0, 7):
                i.append(ledi+si)
        if p == "star":
            for ledi in range(7, 14):
                i.append(ledi+si)
        if p == "branches":
            for ledi in range(14, 21):
                i.append(ledi+si)
    return i


def bld_cane(p):
    i = []
    for c in canes:
        for led_i in c:
            si = led_i
            break
        if p == "end":
            for led_i in range(0, 2):
                i.append(led_i+si)
        if p == "start":
            for led_i in range(2, 4):
                i.append(led_i+si)
    return i


def bld_bar():
    i = []
    for b in bars:
        for l in b:
            si = l
            break
        for l in range(0, 10):
            i.append(l+si)
    return i


def bld_bolt():
    i = []
    for b in bolts:
        for l in b:
            si = l
            break
        if len(b) == 4:
            for l in range(0, 4):
                i.append(l+si)
        if len(b) == 1:
            for l in range(0, 1):
                i.append(l+si)
    return i


def bld_neo():
    i = []
    for n in neos:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l+si)
    return i


def show_l():
    led.show()
    time.sleep(.05)
    led.fill((0, 0, 0))
    led.show()


def l_tst():
    global ornmnts, stars, brnchs, cane_s, cane_e, bar_arr, bolt_arr, neo_arr

    # Christmas items
    ornmnts = bld_tree("ornaments")
    stars = bld_tree("star")
    brnchs = bld_tree("branches")
    cane_s = bld_cane("start")
    cane_e = bld_cane("end")

    # Lightning items
    bar_arr = bld_bar()
    bolt_arr = bld_bolt()

    # Neo items
    neo_arr = bld_neo()

    # cane test
    cnt = 0
    for i in cane_s:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0
    for i in cane_e:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0

    # tree test
    cnt = 0
    for i in ornmnts:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in stars:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in brnchs:
        led[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0

    # bar test
    for b in bars:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # bolt test
    for b in bolts:
        for l in b:
            led[l] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # nood test
    for n in noods:
        led[n[0]] = (50, 50, 50)
        led.show()
        time.sleep(.3)
        led.fill((0, 0, 0))
        led.show()

    # neo test
    for n in neos:
        for i in n:
            led[i] = (0, 50, 0)
            time.sleep(.3)
            led.show()
            led[i] = (50, 0, 0)
            time.sleep(.3)
            led.show()
            led[i] = (0, 0, 50)
            time.sleep(.3)
            led.show()
            time.sleep(.3)
            led.fill((0, 0, 0))
            led.show()


def upd_l_str():
    global trees, canes, bars, bolts, noods, neos, n_px, led
    trees = []
    canes = []
    bars = []
    bolts = []
    noods = []
    neos = []

    n_px = 0

    els = cfg["light_string"].split(',')

    for el in els:
        p = el.split('-')
        if len(p) == 2:
            typ, qty = p
            qty = int(qty)
            if typ == 'grandtree':
                s = list(range(n_px, n_px + qty))
                trees.append(s)
                n_px += qty
            elif typ == 'cane':
                s = list(range(n_px, n_px + qty))
                canes.append(s)
                n_px += qty
            if typ == 'bar':
                s = list(range(n_px, n_px + qty))
                bars.append(s)
                n_px += qty
            elif typ == 'bolt' and qty < 4:
                s = [n_px, qty]
                noods.append(s)
                n_px += 1
            elif typ == 'bolt' and qty == 4:
                s = list(range(n_px, n_px + qty))
                bolts.append(s)
                n_px += qty
            if typ == 'neo':
                if qty == 6:
                    neoqty = 2
                if qty == 12:
                    neoqty = 4
                s = list(range(n_px, n_px + neoqty))
                neos.append(s)
                n_px += neoqty

    print("Number of pixels total: ", n_px)
    led = None
    led = neopixel_spi.NeoPixel_SPI(
        board.SPI(), n_px, brightness=1.0, auto_write=False)
    led.auto_write = False
    led.brightness = 1.0
    l_tst()


upd_l_str()

# Neo pixel / neo 6 module methods

br = 0


def is_neo(number, nested_array):
    return any(number in sublist for sublist in nested_array)


def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):  # in range(n_px)
            if is_neo(i, neos):
                led[i] = (g, r, b)
            else:
                led[i] = (r, g, b)
    else:
        if is_neo(light_n, neos):
            led[light_n] = (g, r, b)
        else:
            led[light_n] = (r, g, b)
    led.show()


def get_neo_ids():
    matches = []
    for num in range(n_px + 1):
        if any(num == sublist[0] for sublist in neos):
            matches.append(num)
    return matches


def set_neo_module_to(mod_n, ind, v):
    cur = []
    neo_ids = get_neo_ids()
    print(mod_n, ind, v, neo_ids)
    if mod_n == 0:
        for i in neo_ids:
            led[i] = (v, v, v)
            led[i+1] = (v, v, v)
    elif ind == 0:
        led[neo_ids[mod_n-1]] = (v, v, v)
        led[neo_ids[mod_n-1]+1] = (v, v, v)
    elif ind < 4:
        ind -= 1
        if ind == 0:
            ind = 1
        elif ind == 1:
            ind = 0
        cur = list(led[neo_ids[mod_n-1]])
        cur[ind] = v
        led[neo_ids[mod_n-1]] = (cur[0], cur[1], cur[2])
        print(led[neo_ids[mod_n-1]])
    else:
        ind -= 1
        if ind == 3:
            ind = 4
        elif ind == 4:
            ind = 3
        cur = list(led[neo_ids[mod_n-1]+1])
        cur[ind-3] = v
        led[neo_ids[mod_n-1]+1] = (cur[0], cur[1], cur[2])
    led.show()


gc_col("Neopixels setup")


################################################################################
# Setup lifx lights

# Create an ordered dictionary to preserve the order of insertion
scene_changes = OrderedDict(cfg["scene_changes"])

# Get the ordered list of keys
ordered_scene_changes_keys = list(scene_changes.keys())

devices = []
lifx = {}


def discover_lights():
    if web == False:
        return False
    if cfg["lifx_enabled"] == False:
        return
    global devices, lifx
    play_mix_media(mvc_folder + "" + "discovering_lifx_lights" + ".wav")
    lifx = LifxLAN()

    # Discover LIFX devices on the local network
    devices = lifx.get_devices()

    # Report the count of discovered devices
    device_count = len(devices)
    spk_str(str(device_count), False)
    play_mix_media(mvc_folder + "" + "lifx_lights_found" + ".wav")

    print(f"Discovered {device_count} device(s).")

    # lifx.set_power_all_lights("on")

    # Iterate over each discovered device and control it
    # for device in devices:
    #     try:
    #         # print(f"Found device: {device.get_label()}")
    #         device.set_color(rgb_to_hsbk(50, 50, 50), 0, True))  # Set initial color
    #         device.set_power("on")
    #     except Exception as e:
    #         print(f"Error setting color for {device.get_label()}: {e}")


def set_light_color_threaded(device, r, g, b):
    """Function to set the light color, executed in a thread."""
    try:
        # Set color instantly
        device.set_color(rgb_to_hsbk(r, g, b), 0, True)
        print(f"Setting color for {device.get_label()} to RGB({r}, {g}, {b})")
    except Exception as e:
        print(f"Error setting color for {device.get_label()}: {e}")


def set_all_lights_parallel(r, g, b):
    """Set color for all lights in parallel using threads."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(
            set_light_color_threaded, device, r, g, b) for device in devices]
        for future in futures:
            future.result()  # Wait for all threads to complete


def set_light_color(light_n, r, g, b):
    if cfg["lifx_enabled"] == "false":
        return
    """Set color for a specific light or all lights."""
    if light_n == -1:
        lifx.set_color_all_lights(rgb_to_hsbk(r, g, b), 0, True)
        # set_all_lights_parallel(r, g, b)
    else:
        # Set color for a specific light
        devices[light_n].set_color(rgb_to_hsbk(r, g, b), 0, True)


def set_light_power(light_n, off_on):
    if light_n == -1:
        if off_on == "ON":
            lifx.set_power_all_lights("on", 0, True)
        else:
            lifx.set_power_all_lights("off", 0, True)
    else:
        if off_on == "ON":
            devices[light_n].set_power("on", 0, True)
        else:
            devices[light_n].set_power("off", 0, True)


################################################################################
# Color helpers


def scene_change(type, start, end, time=5, increments=100):
    """Handle a scene change by interpolating between two times and cycling RGB values."""
    rgb_cycle = interpolate(type, start, end)
    cycle_rgb_values(type, rgb_cycle, time, increments)


def interpolate_color(start_color, end_color, steps):
    """Gradually interpolate between two RGB colors."""
    r_step = (end_color[0] - start_color[0]) / steps
    g_step = (end_color[1] - start_color[1]) / steps
    b_step = (end_color[2] - start_color[2]) / steps

    interpolated_colors = []

    for step in range(steps + 1):
        r = int(start_color[0] + r_step * step)
        g = int(start_color[1] + g_step * step)
        b = int(start_color[2] + b_step * step)
        interpolated_colors.append((r, g, b))

    return interpolated_colors


def interpolate(type, start_key: str, end_key: str):
    """Interpolate between the start and end keys in the scene_changes dictionary."""
    try:
        if type == "lifx":
            start_index = ordered_scene_changes_keys.index(start_key)
            end_index = ordered_scene_changes_keys.index(end_key)
        elif type == "neo":
            start_index = ordered_neo_changes_keys.index(start_key)
            end_index = ordered_neo_changes_keys.index(end_key)

    except ValueError:
        raise ValueError("Invalid key provided.")

    if start_index > end_index:
        # Reverse interpolation
        if type == "lifx":
            interpolated_values = [cfg["scene_changes"][key]
                                   # end_index is exclusive
                                   for key in ordered_scene_changes_keys[start_index:end_index:-1]]
            # Ensure inclusion of end_index
            interpolated_values.append(
                cfg["scene_changes"][ordered_scene_changes_keys[end_index]])
        elif type == "neo":
            interpolated_values = [cfg["neo_changes"][key]
                                   # end_index is exclusive
                                   for key in ordered_neo_changes_keys[start_index:end_index:-1]]
            # Ensure inclusion of end_index
            interpolated_values.append(
                cfg["neo_changes"][ordered_neo_changes_keys[end_index]])
    else:
        # Forward interpolation
        if type == "lifx":
            interpolated_values = [cfg["scene_changes"][key]
                                   # end_index is inclusive
                                   for key in ordered_scene_changes_keys[start_index:end_index + 1]]
        elif type == "neo":
            interpolated_values = [cfg["neo_changes"][key]
                                   # end_index is inclusive
                                   for key in ordered_neo_changes_keys[start_index:end_index + 1]]

    return interpolated_values


def rgb_to_hsbk(r, g, b, brightness_multiplier=1.0):
    import colorsys

    # Normalize RGB values to the range 0-1
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Convert RGB to HSB (Hue, Saturation, Brightness)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Scale brightness with multiplier
    v = max(0, min(1, v * brightness_multiplier))  # Clamp between 0 and 1

    # Convert HSB to LIFX HSBK
    hue = int(h * 65535)          # Hue in range 0-65535
    saturation = int(s * 65535)    # Saturation in range 0-65535
    brightness = int(v * 65535)    # Brightness in range 0-65535

    # Fixed Kelvin value (can adjust for white balance)
    kelvin = 3500

    return [hue, saturation, brightness, kelvin]


def cycle_rgb_values(type, rgb_values, transition_time=2, steps=100):
    """Cycles through a list of RGB tuples, transitioning between each in order."""
    for i in range(len(rgb_values) - 1):
        start_color = rgb_values[i]
        end_color = rgb_values[i + 1]
        color_transition = interpolate_color(start_color, end_color, steps)

        for color in color_transition:
            # Use threading to set color for all lights at once
            if type == "lifx":
                set_light_color(-1, color[0], color[1], color[2])
            elif type == "neo":
                set_neo_to(-1, color[0], color[1], color[2])
            print(f"Setting color to {color}")
            # Adjust sleep time for smooth transitions
            time.sleep(transition_time / steps)

################################################################################
# Requests


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        """Perform a GET request."""
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        return self.handle_response(response)

    def post(self, endpoint, data=None):
        """Perform a POST request."""
        response = requests.post(
            f"{self.base_url}/{endpoint}", json=data, timeout=5)
        return self.handle_response(response)

    def put(self, endpoint, data=None):
        """Perform a PUT request."""
        response = requests.put(f"{self.base_url}/{endpoint}", json=data)
        return self.handle_response(response)

    def delete(self, endpoint):
        """Perform a DELETE request."""
        response = requests.delete(f"{self.base_url}/{endpoint}")
        return self.handle_response(response)

    def handle_response(self, response):
        """Handle the HTTP response."""
        if response.status_code == 200:
            try:
                # Try to parse the response as JSON
                return response.json()
            except ValueError:
                # If JSON parsing fails, treat it as plain text
                return response.text
        else:
            response.raise_for_status()  # Raise an error for bad responses


def send_animator_post(url, endpoint, new_data):
    try:
        new_url = "http://" + url
        new_data_loads = json.loads(new_data)
        api_client = ApiClient(new_url)
        created_data = api_client.post(endpoint, data=new_data_loads)
        print("POST response:", created_data)
        return created_data
    except Exception as e:
        print(f"Comms issue: {e}")


################################################################################
# Setup wifi and web server
number_tries = 0


def get_default_gateway():
    gateways = netifaces.gateways()
    default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
    if default_gateway:
        return default_gateway[0]
    return None


def wait_for_network():
    global number_tries
    while number_tries <= 10:
        try:
            gateway_ip = get_default_gateway()
            if gateway_ip is None:
                raise OSError("No default gateway found")

            # Ping the default gateway
            response = os.system(f"ping -c 1 {gateway_ip}")
            if response == 0:
                print("Wi-Fi is connected to the LAN!")
                return True
            else:
                raise OSError("No response from gateway")
        except OSError as e:
            print(f"Error: {e}")
            print("Waiting for Wi-Fi connection to LAN...")
            time.sleep(1)
            number_tries += 1

    print("Network not available after multiple tries.")
    return False


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def close_midori():
    global is_midori_running
    try:
        subprocess.run(['pkill', 'midori'], check=True)
        is_midori_running = False
        print("Midori closed successfully.")
    except subprocess.CalledProcessError:
        print("Midori was not running.")
    # if cfg["show_webpage"] == False:
    #     return


def open_midori(midori_url):
    global is_midori_running
    # if cfg["show_webpage"] == False or is_midori_running:
    #     return
    try:
        # midori_url = "http://" + local_ip + ":" + str(PORT) + "/stream.html"
        command = "midori -e Fullscreen " + midori_url
        subprocess.Popen(command, shell=True)
        is_midori_running = True
        print("Midori launched.")
    except Exception as e:
        print(f"Failed to start Midori: {e}")

################################################################################
# Setup routes
# Camera streaming globals removed

class MyHttpRequestHandler(server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            print(self.path)
            self.handle_serve_file("/code/index.html")
        elif self.path.endswith(".css"):
            print(self.path)
            self.handle_serve_file("/code" + self.path, "text/css")
        elif self.path.endswith(".js"):
            print(self.path)
            self.handle_serve_file("/code" + self.path,
                                   "application/javascript")

        elif self.path == "/stream.html":
            print(self.path)
            self.handle_serve_file("/code/stream.html")
        else:
            self.handle_serve_file(self.path)

    def do_POST(self):
        if self.path == "/upload":
            self.handle_file_upload()
        else:
            self.handle_generic_post(self.path)

    def handle_serve_file(self, path, content_type="text/html"):
        file_path = path.lstrip("/")
        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def handle_serve_file_name(self, f_n, content_type="text/html"):
        try:
            with open(f_n, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

    def handle_file_upload(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']

        if 'multipart/form-data' in content_type:
            boundary = content_type.split("boundary=")[1].encode()
            body = self.rfile.read(content_length)
            parts = body.split(b'--' + boundary)

            for part in parts:
                gc.collect()
                if part:
                    try:
                        headers, content = part.split(b'\r\n\r\n', 1)
                    except ValueError:
                        continue
                    content = content.rstrip(b'\r\n--')
                    header_lines = headers.decode().split('\r\n')
                    headers_dict = {}
                    for line in header_lines:
                        if ': ' in line:
                            key, value = line.split(': ', 1)
                            headers_dict[key] = value

                    if 'Content-Disposition' in headers_dict:
                        disposition = headers_dict['Content-Disposition']
                        if 'filename=' in disposition:
                            file_name = disposition.split(
                                'filename=')[1].strip('"')
                            # Ensure the uploads directory exists
                            os.makedirs("uploads", exist_ok=True)
                            file_path = os.path.join("uploads", file_name)

                            with open(file_path, "wb") as f:
                                f.write(content)

                            self.send_response(200)
                            self.send_header(
                                "Content-type", "application/json")
                            self.end_headers()
                            response = {"status": "success",
                                        "message": "File uploaded successfully"}
                            self.wfile.write(json.dumps(
                                response).encode('utf-8'))
                            return

            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "No file part"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()

    def handle_generic_post(self, path):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received POST data: {post_data.decode('utf-8')}")
        # Decode the byte string to a regular string
        post_data_obj = {}
        post_data_str = post_data.decode('utf-8')
        if post_data_str != '':
            post_data_obj = json.loads(post_data_str)
        if self.path == "/animation":
            self.animation_post(post_data_obj)
        elif self.path == "/mode":
            self.mode_post(post_data_obj)
        elif self.path == "/defaults":
            self.defaults_post(post_data_obj)
        elif self.path == "/get-animations":
            self.get_animations_post(post_data_obj)
        elif self.path == "/get-buttons":
            self.get_buttons_post(post_data_obj)
        elif self.path == "/speaker":
            self.speaker_post(post_data_obj)
        elif self.path == "/get-light-string":
            self.get_light_string_post(post_data_obj)
        elif self.path == "/get-scene-changes":
            self.get_scene_changes_post(post_data_obj)
        elif self.path == "/get-neo-changes":
            self.get_neo_changes_post(post_data_obj)
        elif self.path == "/update-host-name":
            self.update_host_name_post(post_data_obj)
        elif self.path == "/update-light-string":
            self.update_light_string_post(post_data_obj)
        elif self.path == "/lights":
            self.lights_lifx_post(post_data_obj)
        elif self.path == "/lights-scene":
            self.lights_scene_post(post_data_obj)
        elif self.path == "/lights-neo":
            self.lights_neo_post(post_data_obj)
        elif self.path == "/set-item-lights":
            self.set_item_lights(post_data_obj)
        elif self.path == "/update-host-name":
            self.update_host_name_post(post_data_obj)
        elif self.path == "/get-host-name":
            self.get_host_name_post(post_data_obj)
        elif self.path == "/update-volume":
            self.update_volume_post(post_data_obj)
        elif self.path == "/set-lifx-enabled":
            self.set_lifx_enabled(post_data_obj)
        elif self.path == "/get-volume":
            self.get_volume_post(post_data_obj)
        elif self.path == "/get-lifx-enabled":
            self.get_lifx_enabled(post_data_obj)
        elif self.path == "/create-animation":
            self.create_animation_post(post_data_obj, animations_folder)
        elif self.path == "/create-animation-button":
            self.create_animation_post(post_data_obj, buttons_folder)
        elif self.path == "/get-animation":
            self.get_animation_post(post_data_obj)
        elif self.path == "/get-button":
            self.get_button_post(post_data_obj)
        elif self.path == "/delete-animation":
            self.delete_animation_post(post_data_obj, animations_folder)
        elif self.path == "/delete-animation-button":
            self.delete_animation_post(post_data_obj, buttons_folder)
        elif self.path == "/save-data":
            self.save_data_post(post_data_obj, animations_folder)
        elif self.path == "/save-data-button":
            self.save_data_post(post_data_obj, buttons_folder)
        elif self.path == "/rename-animation":
            self.rename_animation_post(post_data_obj, animations_folder)
        elif self.path == "/rename-animation-button":
            self.rename_animation_post(post_data_obj, buttons_folder)
        elif self.path == "/stop":
            self.stop_post(post_data_obj)
        elif self.path == "/test-animation":
            self.test_animation_post(post_data_obj)
        elif self.path == "/get-local-ip":
            self.get_local_ip(post_data_obj)

    def test_animation_post(self, rq_d):
        global exit_set_hdw
        exit_set_hdw = False
        response = set_hdw(rq_d["an"], 3)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_local_ip(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = local_ip
        self.wfile.write(response.encode('utf-8'))

    def stop_post(self, rq_d):
        rst_an()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "rst an"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    def rename_animation_post(self, rq_d, folder_location):
        global data
        snd = rq_d["fo"].replace("animations", "")
        fo = folder_location + snd + ".json"
        fn = folder_location + rq_d["fn"] + ".json"
        os.rename(fo, fn)
        play_mix_media(mvc_folder + "all_changes_complete.wav")
        upd_media()
        update_folder_name_wavs()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "your response message"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    data = []

    def save_data_post(self, rq_d, folder_location):
        global data
        try:
            if rq_d[0] == 0:
                data = []
            data.extend(rq_d[2])
            if rq_d[0] == rq_d[1]:
                f_n = folder_location + \
                    rq_d[3] + ".json"
                files.write_json_file(f_n, data)
                data = []
            upd_media()
        except Exception as e:
            files.log_item(e)
            data = []
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            response = "out of memory"
            self.wfile.write(response.encode('utf-8'))
            print("Response sent:", response)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "success"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    def delete_animation_post(self, rq_d, folder_location):
        snd_f = rq_d["fn"]
        f_n = folder_location + snd_f + ".json"
        os.remove(f_n)
        play_mix_media(mvc_folder + "all_changes_complete.wav")
        upd_media()
        update_folder_name_wavs()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["fn"] + " animation file deleted"
        self.wfile.write(response.encode('utf-8'))

    def get_animation_post(self, rq_d):
        global cfg, cont_run, ts_mode
        snd_f = rq_d["an"]
        if (f_exists(animations_folder + snd_f + ".json") == True):
            f_n = animations_folder + snd_f + ".json"
            self.handle_serve_file_name(f_n)
            return

    def get_button_post(self, rq_d):
        global cfg, cont_run, ts_mode
        snd_f = rq_d["an"]
        if (f_exists(buttons_folder + snd_f + ".json") == True):
            f_n = buttons_folder + snd_f + ".json"
            self.handle_serve_file_name(f_n)
            return

    def create_animation_post(self, rq_d, folder_location):
        global data
        f_n = folder_location + rq_d["fn"] + ".json"
        if folder_location == buttons_folder:
            files.write_json_file(
                f_n, ["1|QAN_filename", "2|QAN_filename", "3|QAN_filename", "4|QAN_filename"])
        else:
            files.write_json_file(
                f_n, ["0.0|MB0name of your track.wav", "1.0|"])
        play_mix_media(mvc_folder + "all_changes_complete.wav")
        upd_media()
        update_folder_name_wavs()
        gc_col("created animation ")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "created " + rq_d["fn"] + " animation"
        self.wfile.write(response.encode('utf-8'))

    def update_light_string_post(self, rq_d):
        global cfg
        if rq_d["action"] == "save" or rq_d["action"] == "clear" or rq_d["action"] == "defaults":
            cfg["light_string"] = rq_d["text"]
            print("action: " +
                  rq_d["action"] + " data: " + cfg["light_string"])
            files.write_json_file(code_folder + "cfg.json", cfg)
            upd_l_str()
            play_mix_media(mvc_folder + "all_changes_complete.wav")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            response = cfg["light_string"]
            self.wfile.write(response.encode('utf-8'))
            return
        if cfg["light_string"] == "":
            cfg["light_string"] = rq_d["text"]
        else:
            cfg["light_string"] = cfg["light_string"] + \
                "," + rq_d["text"]
        print("action: " + rq_d["action"] +
              " data: " + cfg["light_string"])
        files.write_json_file(code_folder + "cfg.json", cfg)
        upd_l_str()
        play_mix_media(mvc_folder + "all_changes_complete.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["light_string"]
        self.wfile.write(response.encode('utf-8'))

    def mode_post(self, rq_d):
        print(rq_d)
        global cfg, cont_run, ts_mode
        if rq_d["an"] == "cont_mode_on":
            play_mix_media(mvc_folder + "continuous_mode_activated.wav")
            cont_run = True
        elif rq_d["an"] == "cont_mode_off":
            play_mix_media(mvc_folder + "continuous_mode_deactivated.wav")
            cont_run = False
        elif rq_d["an"] == "timestamp_mode_on":
            play_mix_media(mvc_folder + "timestamp_mode_on.wav")
            play_mix_media(mvc_folder + "timestamp_instructions.wav")
            ts_mode = True
        elif rq_d["an"] == "timestamp_mode_off":
            play_mix_media(mvc_folder + "timestamp_mode_off.wav")
            ts_mode = False
        if rq_d["an"] == "left":
            override_switch_state["switch_value"] = "left"
        elif rq_d["an"] == "left_held":
            override_switch_state["switch_value"] = "left_held"
        elif rq_d["an"] == "right":
            override_switch_state["switch_value"] = "right"
        elif rq_d["an"] == "right_held":
            override_switch_state["switch_value"] = "right_held"
        elif rq_d["an"] == "three":
            override_switch_state["switch_value"] = "three"
        elif rq_d["an"] == "three_held":
            override_switch_state["switch_value"] = "three_held"
        elif rq_d["an"] == "four":
            override_switch_state["switch_value"] = "four"
        elif rq_d["an"] == "four_held":
            override_switch_state["switch_value"] = "four_held"
        elif rq_d["an"] == "five":
            override_switch_state["switch_value"] = "five"
        elif rq_d["an"] == "five_held":
            override_switch_state["switch_value"] = "five_held"
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"mode processed": rq_d["an"]}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def animation_post(self, rq_d):
        global cfg, cont_run, ts_mode
        cfg["option_selected"] = rq_d["an"]
        add_command("AN_" + cfg["option_selected"])
        files.write_json_file(code_folder + "cfg.json", cfg)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"Animation added to queue: ": cfg["option_selected"]}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def defaults_post(self, rq_d):
        global cfg
        if rq_d["an"] == "reset_to_defaults":
            rst_def()
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix_media(mvc_folder + "all_changes_complete.wav")
            st_mch.go_to('base_state')
        elif rq_d["an"] == "reset_scene_to_defaults":
            cfg["scene_changes"] = copy.deepcopy(default_cfg["scene_changes"])
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix_media(mvc_folder + "all_changes_complete.wav")
            st_mch.go_to('base_state')
        elif rq_d["an"] == "reset_neo_to_defaults":
            cfg["neo_changes"] = copy.deepcopy(default_cfg["neo_changes"])
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix_media(mvc_folder + "all_changes_complete.wav")
            st_mch.go_to('base_state')
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def speaker_post(self, rq_d):
        global cfg
        if rq_d["an"] == "speaker_test":
            play_mix_media(mvc_folder + "left_speaker_right_speaker.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def get_light_string_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["light_string"]
        self.wfile.write(response.encode('utf-8'))

    def get_scene_changes_post(self, rq_d):
        response = cfg["scene_changes"]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_neo_changes_post(self, rq_d):
        response = cfg["neo_changes"]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def update_host_name_post(self, rq_d):
        global cfg
        cfg["HOST_NAME"] = rq_d["text"]
        files.write_json_file(code_folder + "cfg.json", cfg)
        spk_web()
        restart_pi_timer()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["HOST_NAME"]
        self.wfile.write(response.encode('utf-8'))

    def get_host_name_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["HOST_NAME"]
        self.wfile.write(response.encode('utf-8'))

    def update_volume_post(self, rq_d):
        global cfg
        ch_vol(rq_d["action"])
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["volume"]
        self.wfile.write(response.encode('utf-8'))

    def set_lifx_enabled(self, rq_d):
        global cfg
        cfg["lifx_enabled"] = rq_d["enabled"]
        if cfg["lifx_enabled"] == True:
            discover_lights()
        files.write_json_file(code_folder + "cfg.json", cfg)
        response = cfg["lifx_enabled"]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_volume_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = cfg["volume"]
        self.wfile.write(response.encode('utf-8'))

    def get_lifx_enabled(self, rq_d):
        response = cfg["lifx_enabled"]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_animations_post(self, rq_d):
        upd_media()
        response = snd_opt
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def get_buttons_post(self, rq_d):
        upd_media()
        response = button_opt
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def lights_lifx_post(self, rq_d):
        global exit_set_hdw
        exit_set_hdw = False
        add_command_to_ts(rq_d["an"])
        set_hdw(rq_d["an"], 1)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def lights_neo_post(self, rq_d):
        global current_neo, exit_set_hdw
        current_neo = rq_d["an"]
        rgb_value = cfg["neo_changes"][current_neo]
        exit_set_hdw = False
        command = "LN0_" + str(rgb_value[0]) + "_" + \
            str(rgb_value[1]) + "_" + str(rgb_value[2])
        add_command_to_ts(command)
        set_hdw(command, 0)
        response = rgb_value
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def lights_scene_post(self, rq_d):
        global current_scene, exit_set_hdw
        current_scene = rq_d["an"]
        rgb_value = cfg["scene_changes"][current_scene]
        exit_set_hdw = False
        command = "LX0_" + str(rgb_value[0]) + "_" + \
            str(rgb_value[1]) + "_" + str(rgb_value[2])
        add_command_to_ts(command)
        set_hdw(command, 0)
        response = rgb_value
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def set_item_lights(self, rq_d):
        global current_neo, current_scene, exit_set_hdw
        exit_set_hdw = False
        if rq_d["item"] == "lifx":
            command = "LX0_" + str(rq_d["r"]) + "_" + \
                str(rq_d["g"]) + "_" + str(rq_d["b"])
            add_command_to_ts(command)
            set_hdw(command, 0)
            if current_scene != "":
                cfg["scene_changes"][current_scene] = [
                    rq_d["r"], rq_d["g"], rq_d["b"]]
        elif rq_d["item"] == "neo":
            command = "LN0_" + str(rq_d["r"]) + "_" + \
                str(rq_d["g"]) + "_" + str(rq_d["b"])
            add_command_to_ts(command)
            set_hdw(command, 0)
            if current_neo != "":
                cfg["neo_changes"][current_neo] = [
                    rq_d["r"], rq_d["g"], rq_d["b"]]
        files.write_json_file(code_folder + "cfg.json", cfg)
        response = rq_d
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)


if web:
    if wait_for_network():
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")

        QUEUE_PORT = 8001
        PORT = 8083

        httpd = None

        def start_http_server():
            global httpd
            handler = MyHttpRequestHandler
            httpd = socketserver.ThreadingTCPServer((local_ip, PORT), handler)
            httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(f"Serving on {local_ip}:{PORT}")
            httpd.serve_forever()

        def get_mdns_info():
            name_str = cfg["HOST_NAME"] + "._http._tcp.local."
            server_str = cfg["HOST_NAME"] + ".local."
            desc = {'path': '/'}
            mdns_info = ServiceInfo(
                "_http._tcp.local.",
                name_str,
                addresses=[socket.inet_aton(local_ip)],
                port=PORT,
                properties=desc,
                server=server_str
            )
            return mdns_info

        mdns_info = get_mdns_info()

        async def command_queue_handler(websocket, path):
            global current_media_playing
            print("WebSocket connection established")
            try:
                while True:
                    if command_queue:
                        commands = list(command_queue)
                        response = {
                            'commands': commands,
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))
                    else:
                        response = {
                            'commands': [],
                            'current_media_playing': current_media_playing
                        }
                        await websocket.send(json.dumps(response))
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in command_queue_handler: {e}")
            finally:
                print("WebSocket connection closed")

        async def websocket_server():
            async with websockets.serve(command_queue_handler, "0.0.0.0", QUEUE_PORT):
                print(f"WebSocket server running on port {QUEUE_PORT}")
                await asyncio.Future()  # Run forever
    else:
        web = False

gc_col("web server")


################################################################################
# Command queue

command_queue = deque()


def add_command(command, to_start=False):
    """Add a command to the queue. If to_start is True, add to the front."""
    if to_start:
        command_queue.appendleft(command)  # Add to the front
        print(f"Command added to the start: {command}")
    else:
        command_queue.append(command)  # Add to the end
        print(f"Command added to the end: {command}")


def process_commands():
    """Process commands in a FIFO order from the front."""
    while command_queue:
        command = command_queue.popleft()  # Retrieve from the front
        print(f"Processing command: {command}")
        if command[:2] == 'AN':  # AN_XXX = Animation XXX filename
            cmd_split = command.split("_")
            an(cmd_split[1])
        else:
            set_hdw(command)


def clear_command_queue():
    """Clear all commands from the queue."""
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_commands():
    """Stop all commands and clear the queue."""
    global running_mode, cont_run, exit_set_hdw
    clear_command_queue()
    running_mode = ""
    exit_set_hdw = True
    if mix:
        mix.stop()
    if mix_media:
        mix_media.stop()
    media_player.stop()
    cont_run = False
    rst_an()
    print("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg = copy.deepcopy(default_cfg)

################################################################################
# Dialog and sound play methods


# Manually defined logarithmic values for lookup table (approximate)
linear_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# Logarithmic values approximated between 0 and 1
log_values = [
    0,        # log(0) is undefined, but we set it to 0 for this table
    0.001,    # log(0.1)
    0.01,     # log(0.2)
    0.1,      # log(0.3)
    0.2,      # log(0.4)
    0.3,      # log(0.5)
    0.4,      # log(0.6)
    0.5,      # log(0.7)
    0.6,      # log(0.8)
    0.7,      # log(0.9)
    1.0       # log(1) is 0, but here we set it to 1 for the table
]

# Print out the tables as arrays
print("Linear values:", linear_values)
print("Log values:", log_values)


def interpolate(x, x_values, y_values):
    # Ensure x is within the valid range of x_values
    if x <= x_values[0]:
        return y_values[0]
    elif x >= x_values[-1]:
        return y_values[-1]

    # Find the interval [x1, x2]
    for i in range(1, len(x_values)):
        if x_values[i] >= x:
            x1, x2 = x_values[i-1], x_values[i]
            y1, y2 = y_values[i-1], y_values[i]
            # Interpolate
            return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


# Example: Interpolate for linear input of 0.75
linear_input = 0.75
log_output = interpolate(linear_input, linear_values, log_values)
print(f"Linear input: {linear_input}, Interpolated Log output: {log_output}")


def upd_vol(seconds):
    volume = int(cfg["volume"])
    volume_0_1 = volume/100
    log_to_linear = int(interpolate(volume_0_1, log_values, linear_values)*100)
    if mix:
        mix.set_volume(volume_0_1*0.7)
    if mix_media:
        mix_media.set_volume(volume_0_1*0.7)
    media_player.audio_set_volume(log_to_linear)
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
    upd_vol(.05)
    files.write_json_file(code_folder + "cfg.json", cfg)
    play_mix_media(mvc_folder + "volume.wav")
    spk_str(cfg["volume"], False)


def play_mix(file_name, wait_until_done=True, allow_exit=True):
    print("playing " + file_name)
    if mix and mix.get_busy():
        mix.stop()
        while mix and mix.get_busy():
            pass
    if mix:
        mix_sound = pygame.mixer.Sound(file_name)
        upd_vol(.05)
        mix.play(mix_sound, loops=0)
    while mix and mix.get_busy() and wait_until_done:
        if allow_exit:
            exit_early()
    print("done playing")


def play_mix_media(file_name, wait_until_done=True, repeat=0, allow_exit=True):
    print("playing " + file_name)
    if mix_media and mix_media.get_busy():
        mix_media.stop()
        while mix and mix.get_busy():
            pass
    if mix_media:
        mix_media_sound = pygame.mixer.Sound(file_name)
        upd_vol(.05)
        mix_media.play(mix_media_sound, loops=repeat)
        while mix_media.get_busy() and wait_until_done:
            if allow_exit:
                exit_early()
    print("done playing")


def wait_snd():
    while (mix_media and mix_media.get_busy()) or media_player.is_playing():
        exit_early()
    print("done playing")


def stop_all_media():
    if mix:
        mix.stop()
    if mix_media:
        mix_media.stop()
    media_player.stop()
    close_midori()

    while (mix and mix.get_busy()) or (mix_media and mix_media.get_busy()) or media_player.is_playing():
        pass


def exit_early():
    switch_state = utilities.switch_state(
        l_sw, r_sw, time.sleep, 3.0, override_switch_state)
    if switch_state == "left":
        stop_all_media()
    time.sleep(0.05)


def spk_str(str_to_speak, addLocal, addIpAddressIs=False):
    if addIpAddressIs:
        play_mix_media(mvc_folder + "ip_address_is.wav")
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_mix_media(mvc_folder + "" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        play_mix_media(mvc_folder + "dot_local_colon_8083.wav")


def l_r_but():
    play_mix_media(mvc_folder + "press_left_button_right_button.wav")


def sel_web():
    play_mix_media(mvc_folder + "web_menu.wav")
    l_r_but()


def opt_sel():
    play_mix_media(mvc_folder + "option_selected.wav")


def spk_sng_num(song_number):
    play_mix_media(mvc_folder + "song.wav")
    spk_str(song_number, False)


def no_trk():
    play_mix_media(mvc_folder + "no_user_soundtrack_found.wav")
    while True:
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            break
        if switch_state == "right":
            play_mix_media(mvc_folder + "create_sound_track_files.wav")
            break


def spk_web():
    play_mix(code_folder + "mvc/animator_available_on_network.wav")
    play_mix(code_folder + "mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-kiosk":
        play_mix(code_folder + "mvc/animator_dash_kiosk.wav")
        play_mix(code_folder + "mvc/dot_local_colon_8083.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_mix(code_folder + "mvc/in_your_browser.wav")


def get_snds(dir, typ):
    sds = []
    s = files.return_directory("", dir, ".wav")
    for el in s:
        p = el.split('_')
        if p[0] == typ:
            sds.append(el)
    mx = len(sds) - 1
    i = random.randint(0, mx)
    fn = dir + "/" + sds[i] + ".wav"
    return fn


def get_random_joke():
    url = "https://official-joke-api.appspot.com/jokes/random"
    response = requests.get(url)

    if response.status_code == 200:
        joke = response.json()
        print(f"{joke['setup']} - {joke['punchline']}")
    else:
        print("Failed to retrieve a joke.")

    text_to_wav_file(joke['setup'], "myjoke.wav", 2)
    text_to_wav_file(joke['punchline'], "myjoke.wav", 2)

###############################################################################
# Text to speech


def check_gtts_status():
    if web == False:
        return False
    try:
        # gTTS API endpoint
        url = "https://translate.google.com"

        # Send a simple GET request
        response = requests.get(url, timeout=5)

        # Check the status code
        if response.status_code == 200:
            print("gTTS service is reachable.")
            return True
        else:
            print("gTTS service returned an unexpected status code: " +
                  response.status_code)
            return False

    except requests.ConnectionError:
        print("Failed to connect to gTTS service.")
        return False
    except requests.Timeout:
        print("The request to gTTS service timed out.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Custom exception for timeout
class TimeoutException(Exception):
    pass


# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutException("The operation timed out!")


# Set up a signal to call the handler after a timeout
signal.signal(signal.SIGALRM, timeout_handler)


def text_to_wav_file(text, file_name, timeout_duration):
    global is_gtts_reachable
    if is_gtts_reachable == False:
        return
    try:
        # Set the timeout (in seconds)
        signal.alarm(timeout_duration)

        # Convert text to mp3 file
        # text = files.strip_path_and_extension(f_nm)
        tts = gTTS(text=text, lang='en')
        tts.save(code_folder + "temp.mp3")

        # Cancel the alarm if operation completes before timeout
        signal.alarm(0)

        # Load the audio file with pydub
        audio = AudioSegment.from_file(code_folder + "temp.mp3")

        # Adjust the volume
        volume_change = -5  # Decrease volume by 5db
        adjusted_audio = audio + volume_change

        # Save the adjusted audio
        adjusted_audio.export(file_name, format="wav")
        print(f"Wav for {file_name} generated and volume adjusted.")

        play_mix_media(file_name)

    except TimeoutException:
        print("TTS operation timed out.")
        is_gtts_reachable = False
    except Exception as e:
        print(f"An error occurred: {e}")
        is_gtts_reachable = False


def generate_wav_from_filename(file_name):
    if is_gtts_reachable == False:
        return
    text_to_speak = file_name.replace("_", " ")
    text_to_speak = text_to_speak.replace(".json", "")

    wav_file = os.path.join(
        snd_opt_folder, f"{os.path.splitext(file_name)[0]}.wav")

    # If wav file already exists, skip
    if os.path.exists(wav_file):
        print(f"Wav for {file_name} already exists. Skipping...")
        return

    # Generate speech from text
    tts = gTTS(text=text_to_speak, lang='en')
    tts.save(code_folder + "temp.mp3")

    # Load the audio file with pydub
    audio = AudioSegment.from_file(code_folder + "temp.mp3")

    # Adjust the volume
    volume_change = -5  # Decrease volume by 5db
    adjusted_audio = audio + volume_change

    print(f"Wav filename to save: {wav_file}")
    # Save the adjusted audio
    adjusted_audio.export(wav_file, format="wav")
    print(f"Wav for {file_name} generated and volume adjusted.")


def update_folder_name_wavs():
    if not web or not is_gtts_reachable:
        return

    # Generate wavs for valid menu options
    for name in menu_snd_opt:
        generate_wav_from_filename(name)

    # Get all wav files in the folder
    for file in os.listdir(snd_opt_folder):
        if not file.lower().endswith(".wav"):
            continue

        base_name = os.path.splitext(file)[0]

        # Delete orphaned wav files
        if base_name not in menu_snd_opt:
            os.remove(os.path.join(snd_opt_folder, file))
            print(f"Deleted orphaned wav: {file}")


################################################################################
# Animation methods

def logo_when_idle():
    time_counter = 0

    while True:
        if not running_mode:
            time_counter += 1
            if time_counter == 2:
                # open_midori("http://" + local_ip + ":" + str(PORT) + "/")
                change_wallpaper(media_folder + 'pictures/black.jpg')
        else:
            time_counter = 0
        time.sleep(1)


def check_switches(stop_event):
    global cont_run, running_mode, mix_is_paused, exit_set_hdw
    while not stop_event.is_set():  # Check the stop event
        switch_state = utilities.switch_state_four_switches(
            l_sw, r_sw, three_sw, four_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left" and cfg["can_cancel"]:
            stop_event.set()  # Signal to stop the thread
            rst_an()
        elif switch_state == "left_held" and cfg["can_cancel"]:
            stop_event.set()  # Signal to stop the thread
            clear_command_queue()
            rst_an()
            if cont_run:
                cont_run = False
                pygame_mixer_init()
                play_mix(code_folder + "mvc/continuous_mode_deactivated.wav")
        elif switch_state == "right" and cfg["can_cancel"]:
            if running_mode == "media_player":
                if media_player.is_playing():
                    media_player.pause()
                else:
                    media_player.play()
            elif running_mode == "mix":
                if mix_is_paused:
                    if mix_media:
                        mix_media.unpause()
                    mix_is_paused = False
                else:
                    if mix_media:
                        mix_media.pause()
                    mix_is_paused = True
        elif switch_state == "three":
            print("sw three fell")
            ch_vol("lower")
        elif switch_state == "four":
            print("sw four fell")
            ch_vol("raise")
        upd_vol(0.05)


def run_check_switches_thread():
    stop_event = threading.Event()  # Create a stop event
    check_thread = threading.Thread(target=check_switches, args=(stop_event,))
    check_thread.start()
    return check_thread, stop_event


def rst_an(file_name=media_folder + 'pictures/black.jpg'):
    global current_media_playing, exit_set_hdw
    print("resetting animations")
    exit_set_hdw = True
    stop_all_media()
    led.brightness = 1.0
    led.fill((0, 0, 0))
    led.show()
    change_wallpaper(file_name)
    time.sleep(0.5)
    l_sw.update()
    r_sw.update()
    three_sw.update()
    four_sw.update()
    five_sw.update()
    current_media_playing = ""


def an(f_nm):
    global cfg, lst_opt, running_mode
    print("Filename: " + f_nm)
    try:
        cur_opt = return_file_to_use(f_nm)
        if ts_mode:
            an_ts(cur_opt)
            gc_col("animation cleanup")
        else:
            result = an_light(cur_opt)
            if not mix:
                pygame_mixer_init()
            gc_col("animation cleanup")
            return result
    except Exception as e:
        files.log_item(e)
        no_trk()
        cfg["option_selected"] = "random all"
        return
    gc_col("Animation complete.")


def return_file_to_use(f_nm):
    global cfg, lst_opt, running_mode
    cur_opt = f_nm
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
    return cur_opt


def an_light(f_nm):
    global ts_mode, running_mode, terminal_process, current_media_playing, mix_is_paused, exit_set_hdw
    exit_set_hdw = False
    current_media_playing = f_nm

    flsh_t = []

    if (f_exists(animations_folder + f_nm + ".json") == True):
        flsh_t = files.read_json_file(
            animations_folder + f_nm + ".json")

    check_thread, stop_event = run_check_switches_thread()

    flsh_i = 0

    media0_exists = False

    if flsh_i < len(flsh_t)-1:
        try:
            ft1 = flsh_t[flsh_i].split("|")
            result = set_hdw(ft1[1])
            try:
                result = result.split("_")
            except:
                result = None
            if result and len(result) > 1:
                media0 = animations_folder + result[1]
                media0_exists = f_exists(media0)
                if media0_exists:
                    if ".mp4" in media0:
                        pygame_mixer_quit()
                        running_mode = "media_player"
                        print("Running mode: ", running_mode)
                        play_movie_file(media0)
                    elif ".wav" in media0:
                        media0_basename = media0.replace(".wav", "")
                        running_mode = "mix"
                        print("Running mode: ", running_mode)
                        change_wallpaper(media0_basename + ".jpg")
                        mix_is_paused = False
                        if result[0] == "1":
                            repeat = -1
                        else:
                            repeat = 0
                        play_mix_media(media0, False, repeat, True)

            ft1 = []
            ft2 = []

            # add end command to time stamps so all table values can be used
            ft_last = flsh_t[len(flsh_t)-1].split("|")
            tm_last = float(ft_last[0]) + .1
            flsh_t.append(str(tm_last) + "|")
        except Exception as e:
            files.log_item(e)
            stop_event.set()  # Signal the thread to stop
            check_thread.join()  # Wait for the thread to finish
            result = an_done_reset("DONE")
            return result
        flsh_i += 1
    else:
        stop_event.set()  # Signal the thread to stop
        check_thread.join()  # Wait for the thread to finish
        result = an_done_reset("DONE")
        return result

    srt_t = time.monotonic()

    while True:
        t_past = time.monotonic()-srt_t
        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i+1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0
        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            t_elaspsed = "{:.3f}".format(t_past)
            duration = "{:.3f}".format(dur)
            log_this = "TE: " + \
                str(t_elaspsed) + " TS: " + \
                ft1[0] + " Dur: " + str(duration) + " Cmd: " + ft1[1]
            files.log_item(log_this)
            resp = set_hdw(ft1[1], dur)
            if resp == "STOP":
                result = an_done_reset(resp)
                return result
            flsh_i += 1

        media_player_state_now = media_player_state()

        if media0_exists and (not (mix_media and mix_media.get_busy()) and media_player_state_now != "Playing" and media_player_state_now != "Paused"):
            print("media ended")
            stop_event.set()  # Signal the thread to stop
            check_thread.join()  # Wait for the thread to finish
            result = an_done_reset("DONE")
            return result
        if flsh_i >= len(flsh_t)-1:
            print("all time stamps done")
            stop_event.set()  # Signal the thread to stop
            check_thread.join()  # Wait for the thread to finish
            result = an_done_reset("DONE")
            return result
        if exit_set_hdw:
            print("exit early pressed")
            stop_event.set()  # Signal the thread to stop
            check_thread.join()  # Wait for the thread to finish
            result = an_done_reset("DONE")
            return result
        time.sleep(.05)


def an_done_reset(return_value):
    global running_mode
    rst_an()
    time.sleep(0.05)
    running_mode = ""
    return return_value


def add_command_to_ts(command):
    global ts_mode, t_s, t_elsp
    if not ts_mode:
        return
    t_elsp_formatted = "{:.3f}".format(t_elsp)
    t_s.append(t_elsp_formatted + "|" + command)
    files.log_item(t_elsp_formatted + "|" + command)


def an_ts(f_nm):
    global t_s, t_elsp, terminal_process, ts_mode, running_mode
    print("time stamp mode")
    running_mode == "time_stamp_mode"

    is_video = ".mp4" in f_nm
    json_fn = f_nm.replace(".mp4", "")
    json_fn = json_fn.replace(".wav", "")

    t_s = []

    t_s.append("0.0|")

    media0 = media_folder + f_nm

    if is_video:
        play_movie_file(media0)
    else:
        play_mix_media(media0)

    startTime = time.perf_counter()
    time.sleep(.1)

    while True:
        t_elsp = time.perf_counter()-startTime
        r_sw.update()
        if r_sw.fell:
            add_command_to_ts("")
        if not (mix_media and mix_media.get_busy()) and not media_player.is_playing():
            add_command_to_ts("")
            led.fill((0, 0, 0))
            led.show()
            files.write_json_file(
                media_folder + json_fn + ".json", t_s)
            break

    ts_mode = False
    rst_an()
    play_mix(code_folder + "mvc/timestamp_saved.wav")
    play_mix(code_folder + "mvc/timestamp_mode_off.wav")
    play_mix(code_folder + "mvc/animations_are_now_active.wav")
    running_mode = ""


###############
# Animation helpers

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


def set_hdw(cmd, dur=3):
    global sp, br, running_mode, exit_set_hdw

    if cmd == "":
        return "NOCMDS"

    segs = cmd.split(",")

    try:
        for seg in segs:
            if exit_set_hdw:
                return "STOP"
            f_nm = ""
            if seg[0] == 'E':  # end an
                return "STOP"
            # SW_XXXX = Switch XXXX (left,right,three,four,five, left_held, ...)
            elif seg[:2] == 'SW':
                segs_split = seg.split("_")
                if len(segs_split) == 2:
                    override_switch_state["switch_value"] = segs_split[1]
                elif len(segs_split) == 3:
                    override_switch_state["switch_value"] = segs_split[1] + \
                        "_" + segs_split[2]
                else:
                    override_switch_state["switch_value"] = "none"
            # MBRXXX = Music background, R repeat (0 no, 1 yes), XXX (file name) must be in first row all others ignored
            elif seg[:2] == 'MB':  # play file
                repeat = seg[2]
                file_nm = seg[3:]
                return repeat + "_" + file_nm
            # MALXXX = Play file, A (P play media, W play media wait, S stop media), L = file location (M movies, E elves, B bells, H horns, T stops, S santa, Z christmas story, C cut, R recording, X shutter, Q quotes) XXX (file name, if RAND random selection of folder, SEQN play next in sequence, SEQF play first in sequence)
            elif seg[0] == 'M':  # play file
                if seg[1] == "S":
                    stop_all_media()
                elif seg[1] == "W" or seg[1] == "P":
                    if seg[2] in FOLDER_MAP:
                        folder = FOLDER_MAP[seg[2]]
                        code = seg[3:]
                        if seg[2] == "M":
                            pygame_mixer_quit()
                            file_type = ".mp4"
                        else:
                            pygame_mixer_init()
                            file_type = ".wav"
                        if code == "SEQN":
                            filename, media_index[seg[2]] = get_indexed_media_file(
                                folder, file_type, media_index[seg[2]])
                        elif code == "SEQF":
                            filename, media_index[seg[2]] = get_indexed_media_file(
                                folder, file_type, 0)
                        elif code == "RAND":
                            filename = get_random_media_file(folder, file_type)
                        else:
                            filename = code
                        w1 = folder + filename + file_type
                    if (seg[1] == "W" or seg[1] == "P"):
                        if seg[2] == "M":
                            play_movie_file(w1)
                        else:
                            play_mix_media(w1, False, 0, False)
                    if seg[1] == "W":
                        wait_snd()
            # HA = Blow horn or bell, A (H Horn, B Bell)
            elif seg[0] == 'H':  # play file
                stop_all_media()
                if seg[1] == "B":
                    w1 = get_snds(bells_folder, "bell")
                    play_mix_media(w1, False, 0, False)
                elif seg[1] == "H":
                    w1 = get_snds(horns_folder, "horn")
                    play_mix_media(w1, False, 0, False)
            # LNZZZ_R_G_B = Neopixel lights/Neo 6 modules ZZZ (0 All, 1 to 999) RGB 0 to 255
            elif seg[:2] == 'LN':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_neo_to(light_n, r, g, b)
            # LXZZZ_R_G_B = Lifx lights ZZZ (0 All, 1 to 999) RGB 0 to 255
            elif seg[:2] == 'LX':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_light_color(light_n, r, g, b)
            # LPZZZ_YYY = Lifx lights ZZZ (0 All, 1 to 999) YYY power ON or OFF
            elif seg[:2] == 'LP':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                power = segs_split[1]
                set_light_power(light_n, power)
            # NMZZZ_I_XXX = Neo 6 modules only ZZZ (0 All, 1 to 999) I index (0 All, 1 to 6) XXX 0 to 255</div>
            elif seg[0] == 'N':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0][1:])
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_module_to(mod_n, index, v)
            # BNYYY = Brightness (Neopixel lights/Neo 6 modules) YYY 000 to 100
            elif seg[0:2] == 'BN':
                br = int(seg[2:])
                led.brightness = float(br/100)
                led.show()
            # FXXX_TTT = Fade brightness in or out XXX 0 to 100, TTT time between transitions in decimal seconds
            elif seg[0] == 'F':
                segs_split = seg.split("_")
                v = int(segs_split[0][1:])
                s = float(segs_split[1])
                while not br == v:
                    if br < v:
                        br += 1
                        led.brightness = float(br/100)
                    else:
                        br -= 1
                        led.brightness = float(br/100)
                    led.show()
                    time.sleep(s)
            # ZRAND = Random rainbow, fire, or color change
            elif seg[0:] == 'ZRAND':
                random_effect(1, 3, dur)
            # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                rbow(v, dur)
            # ZFIRE = Fire
            elif seg[0:] == 'ZFIRE':
                random_effect(3, 3, dur)
            # ZCOLCH = Color change
            elif seg[0:] == 'ZCOLCH':
                random_effect(2, 2, dur)
            # ZL_S_E_T_I = Scene change S start E end using (daylight,afternoon,....), time, increments
            elif seg[:2] == 'ZL':
                segs_split = seg[3:].split("_")
                scene_change("lifx", segs_split[0], segs_split[1],
                             float(segs_split[2]), int(segs_split[3]))
            # ZN_S_E_T_I = Scene change S start E end using (red,green,....), time, increments
            elif seg[:2] == 'ZN':
                segs_split = seg[3:].split("_")
                scene_change("neo", segs_split[0], segs_split[1],
                             float(segs_split[2]), int(segs_split[3]))
            # ZJ = Joke
            elif seg[:2] == 'ZJ':
                get_random_joke()
            # IXXX/XXX XXX/XXXX(folder/filename)
            elif seg[0] == 'I':
                f_nm = media_folder + seg[1:]
                change_wallpaper(f_nm)
            # SNXXX = Servo N (0 All, 1-6) XXX 0 to 180
            if seg[0] == 'S':  # servos S
                num = int(seg[1])
                v = int(seg[2:])
                if num == 0:
                    for i in range(6):
                        m_servo_s(i, v)
                else:
                    m_servo_s(num-1, v)
            # QXXX/XXX = Add media to queue XXX/XXX (folder/filename)
            if seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)
            # API_UUU_EEE_DDD = Api POST call UUU base url, EEE endpoint, DDD data object i.e. {"an": data_object}
            if seg[:3] == 'API':
                seg_split = split_string(seg)
                print(seg_split)
                if len(seg_split) == 3:
                    print("three params")
                    response = send_animator_post(
                        url, seg_split[1], seg_split[2])
                    return response
                elif len(seg_split) == 4:
                    print("four params")
                    response = send_animator_post(
                        seg_split[1], seg_split[2], seg_split[3])
                    return response
                return ""
            # WOPEN_xxxx = Open webpage, XXX web url
            if seg[:5] == 'WOPEN':
                seg_split = seg.split("_")
                print("Segment 1 is: ", seg_split[1])
                open_midori(seg_split[1])
            # WCLOSE = Close webpage, XXX web url
            if seg[:6] == 'WCLOSE':
                close_midori()
    except Exception as e:
        files.log_item(e)


def split_string(seg):
    # Find the object (everything inside curly braces)
    match = re.search(r'(_\{.*\})', seg)

    if match:
        # Remove the last underscore and the object part from the string
        object_part = match.group(0)
        seg = seg.replace(object_part, '')
    else:
        object_part = ''  # If no object is found, set it to empty

    # Now split the remaining part by underscores
    parts = seg.split('_')

    # Add the object back as the last part
    # Remove leading underscore from object
    parts.append(object_part.strip('_'))

    return parts


def get_random_media_file(folder_to_search, file_type):
    myfiles = files.return_directory("", folder_to_search, file_type)
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

##############################
# Led color effects


def random_effect(il, ih, d):
    i = random.randint(il, ih)
    if i == 1:
        rbow(.005, d)
    elif i == 2:
        multi_color()
        time.sleep(d)
    elif i == 3:
        fire(d)


def rbow(spd, dur):
    global exit_set_hdw
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw:
                return
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
        for j in reversed(range(0, 255, 1)):
            if exit_set_hdw:
                return
            for i in range(n_px):
                pixel_index = (i * 256 // n_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return


def fire(dur):
    global exit_set_hdw
    st = time.monotonic()
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        for i in range(n_px):
            # if exit_set_hdw:
            #     return
            f = random.randint(0, 110)
            r1 = bnd(r-f, 0, 255)
            g1 = bnd(g-f, 0, 255)
            b1 = bnd(b-f, 0, 255)
            led[i] = (r1, g1, b1)
        led.show()
        time.sleep(random.uniform(0.05, 0.1))
        te = time.monotonic()-st
        if te > dur:
            return


def multi_color():
    global exit_set_hdw
    for i in range(0, n_px):
        # if exit_set_hdw:
        #         return
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


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c

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
        play_mix_media(mvc_folder + "animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global cont_run, running_mode, override_switch_state, is_button_mode, group_index
        if running_mode != "time_stamp_mode":
            process_commands()
            switch_state = utilities.switch_state_five_switches(
                l_sw, r_sw, three_sw, four_sw, five_sw, time.sleep, 3.0, override_switch_state)
            if is_button_mode:
                if switch_state == "left":
                    add_command(get_button_value(group_index, 1))
                    time.sleep(.5)
                elif switch_state == "right":
                    add_command(get_button_value(group_index, 2))
                    time.sleep(.5)
                elif switch_state == "three":
                    add_command(get_button_value(group_index, 3))
                    time.sleep(.5)
                elif switch_state == "four":
                    add_command(get_button_value(group_index, 4))
                    time.sleep(.5)
                elif switch_state == "five":
                    group_index += 1
                    if group_index > len(button_groups):
                        group_index = 1
                    print("Group_index: ", group_index)
                    play_mix_media(mvc_folder + "button_group.wav")
                    play_mix_media(mvc_folder + str(group_index) + ".wav")
                    time.sleep(.5)
                elif switch_state == "five_held":
                    print("switch out of button mode")
                    cfg["option_selected"] = "random all"
                    is_button_mode = False
                    play_mix_media(mvc_folder + "button_mode_off.wav")
                    time.sleep(.5)
            else:
                if switch_state == "left_held" and not is_button_mode:
                    if cont_run:
                        cont_run = False
                        play_mix_media(
                            mvc_folder + "continuous_mode_deactivated.wav")
                    else:
                        cont_run = True
                        play_mix_media(
                            mvc_folder + "continuous_mode_activated.wav")
                    time.sleep(.5)
                elif switch_state == "left" or cont_run:
                    add_command("AN_" + cfg["option_selected"])
                    time.sleep(.5)
                elif switch_state == "right":
                    mch.go_to('main_menu')
                    time.sleep(.5)
                elif switch_state == "three":
                    print("sw three fell")
                    ch_vol("lower")
                    time.sleep(.5)
                elif switch_state == "four":
                    print("sw four fell")
                    ch_vol("raise")
                    time.sleep(.5)
                elif switch_state == "five_held":
                    print("switch into button mode")
                    is_button_mode = True
                    play_mix_media(mvc_folder + "button_mode_on.wav")
        time.sleep(0.05)


class Main(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, mch):
        files.log_item('Main menu')
        play_mix_media(mvc_folder + "main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global override_switch_state
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            play_mix_media(mvc_folder + "" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if switch_state == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "choose_sounds":
                mch.go_to('choose_sounds')
            elif sel_mnu == "add_sounds_animate":
                mch.go_to('add_sounds_animate')
            elif sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "volume_level_adjustment":
                mch.go_to('volume_level_adjustment')
            else:
                play_mix_media(mvc_folder + "all_changes_complete.wav")
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
        play_mix_media(mvc_folder + "sound_selection_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global override_switch_state
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            try:
                play_mix_media(snd_opt_folder + menu_snd_opt[self.i] + ".wav")
            except Exception as e:
                files.log_item(e)
                spk_sng_num(str(self.i+1))
            self.sel_i = self.i
            self.i += 1
            if self.i > len(menu_snd_opt)-1:
                self.i = 0
        if switch_state == "right":
            cfg["option_selected"] = menu_snd_opt[self.sel_i]
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix_media(mvc_folder + "option_selected.wav")
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
        play_mix_media(mvc_folder + "add_sounds_animate.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global ts_mode, override_switch_state
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            play_mix_media(
                mvc_folder + "" + add_snd[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(add_snd)-1:
                self.i = 0
        if switch_state == "right":
            sel_mnu = add_snd[self.sel_i]
            if sel_mnu == "hear_instructions":
                play_mix_media(mvc_folder + "drive_in_media_instructions.wav")
            elif sel_mnu == "timestamp_mode_on":
                ts_mode = True
                play_mix_media(mvc_folder + "timestamp_mode_on.wav")
                play_mix_media(mvc_folder + "timestamp_instructions.wav")
                mch.go_to('base_state')
            elif sel_mnu == "timestamp_mode_off":
                ts_mode = False
                play_mix_media(mvc_folder + "timestamp_mode_off.wav")
            else:
                play_mix_media(mvc_folder + "all_changes_complete.wav")
                mch.go_to('base_state')


class VolumeLevelAdjustment(Ste):

    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return 'volume_level_adjustment'

    def enter(self, mch):
        files.log_item('Set Web Options')
        play_mix_media(mvc_folder + "volume_adjustment_menu.wav")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global override_switch_state
        done = False
        while not done:
            switch_state = utilities.switch_state(
                l_sw, r_sw, time.sleep, 3.0, override_switch_state)
            if switch_state == "left":
                ch_vol("lower")
            elif switch_state == "right":
                ch_vol("raise")
            elif switch_state == "right_held":
                files.write_json_file(
                    code_folder + "cfg.json", cfg)
                play_mix_media(mvc_folder + "all_changes_complete.wav")
                done = True
                mch.go_to('base_state')
            time.sleep(0.05)
            pass


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
        global cfg, override_switch_state
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            play_mix_media(mvc_folder + "" + web_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if switch_state == "right":
            selected_menu_item = web_m[self.sel_i]
            if selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            elif selected_menu_item == "hear_ip_address":
                local_ip
                spk_str(local_ip, False, True)
                sel_web()
            elif selected_menu_item == "update_ssid_password_from_usb":
                play_mix_media(
                    mvc_folder + "update_ssid_password_from_usb.wav")
                update_ssid_password_from_usb()
                restart_pi_timer()
            else:
                mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(Snds())
st_mch.add(AddSnds())
st_mch.add(VolumeLevelAdjustment())
st_mch.add(WebOpt())

time.sleep(0.05)
aud_en.value = True
upd_vol(0.05)

if web:
    files.log_item("starting server...")
    try:
        zeroconf = Zeroconf()
        print("Registering mDNS service...")
        zeroconf.register_service(mdns_info)
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
    except OSError:
        web = False
        files.log_item("server did not start...")

discover_lights()

is_gtts_reachable = check_gtts_status()

update_folder_name_wavs()

if web:
    # Start the WebSocket server in a separate thread
    websocket_thread = threading.Thread(
        target=lambda: asyncio.run(websocket_server()), daemon=True)
    websocket_thread.start()
    spk_web()

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")


def run_state_machine():
    while True:
        st_mch.upd()
        time.sleep(0.05)


# Start the state machine in a separate thread
state_machine_thread = threading.Thread(target=run_state_machine)
state_machine_thread.daemon = True
state_machine_thread.start()


def stop_program():
    stop_all_commands()
    if web:
        print("Unregistering mDNS service...")
        zeroconf.unregister_service(mdns_info)
        zeroconf.close()
        httpd.shutdown()
    rst_an()
    quit()


while True:
    try:
        input("Press enter to exit...\n\n")
    finally:
        stop_program()


# type: ignore