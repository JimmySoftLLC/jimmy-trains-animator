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
# feature that is contorlled via pin 26.  It is enabled by this program just before it announces the animations are active
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

from lifxlan import LifxLAN
from concurrent.futures import ThreadPoolExecutor
import http.server
import socket
import socketserver
import threading
from zeroconf import ServiceInfo, Zeroconf
import json
import os
import gc
import board
import digitalio
from adafruit_debouncer import Debouncer
import pygame
import gc
import files
import utilities
import psutil
import random
from gtts import gTTS
import requests
from lifxlan import LifxLAN
import subprocess
import time
import netifaces
from collections import OrderedDict, deque
import signal
import copy
from pydub import AudioSegment
import pyautogui
import serial
import serial.tools.list_ports


# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.D26)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = False


def get_home_path(subpath=""):
    # Get the current user's home directory
    home_dir = os.path.expanduser("~")
    # Return the full path by appending the optional subpath
    return os.path.join(home_dir, subpath)


code_folder = get_home_path() + "code/"
media_folder = get_home_path() + "media/"
animators_folder = get_home_path() + "media/animator/animators/"
current_scene = ""
connect_to_base_3 = True
tmp_wav_file_name = code_folder + "tmp.wav"
override_switch_state = {}
override_switch_state["switch_value"] = ""

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
                new_image_path = media_folder + 'pictures/logo.jpg'

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


change_wallpaper(media_folder + 'pictures/logo.jpg')


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

# to make this work you must add permission to the visudo file
# sudo visudo
# base3 ALL=(ALL) NOPASSWD: /sbin/reboot


def restart_pi():
    os.system('sudo reboot')


def restart_pi_timer():
    play_mix(code_folder + "mvc/restarting_animator_base3.wav")
    delay = 2
    timer = threading.Timer(delay, restart_pi)
    timer.start()


gc_col("Imports gc, files")

################################################################################
# ssid and password setup

# Function to mount the USB drive (assumes automatic mounting to /media/pi)


def get_usb_path():
    media_path = "/media/base3/"
    usb_path = None
    for root, dirs, files in os.walk(media_path):
        if 'wifi_config.txt' in files:
            usb_path = os.path.join(root, 'wifi_config.txt')
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
    return ssid, password


def connect_wifi(ssid, password):
    # Run nmcli added a connection to the connection manager list,
    # this public connection can be edited by the user later if needed.
    subprocess.call(['sudo', 'nmcli', 'connection', 'add', 'type', 'wifi',
                     'con-name', ssid, 'ifname', 'wlan0', 'ssid', ssid,
                     'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', password])

# Update ssid password using usb drive


def update_ssid_password_from_usb():
    print("Looking for USB with Wi-Fi configuration...")
    while True:
        usb_path = get_usb_path()
        if usb_path:
            print(f"Found USB with Wi-Fi config at: {usb_path}")
            ssid, password = read_wifi_credentials(usb_path)
            print("Using SSID: " + ssid + " and password: " + password)
            if ssid:
                print(f"Setting up Wi-Fi connection with SSID: {ssid}")
                connect_wifi(ssid, password)
                break
        else:
            print("Waiting for USB to be inserted...")
            time.sleep(5)  # Check every 5 seconds for the USB


################################################################################
# config variables

cfg = files.read_json_file(code_folder + "cfg.json")
default_cfg = files.read_json_file(code_folder + "default_cfg.json")
animator_configs = []


def get_media_files(folder_to_search, extensions):
    media_dict = {}

    # Normalize extensions (e.g., ensure they all start with a dot)
    extensions = [ext if ext.startswith(
        '.') else f'.{ext}' for ext in extensions]

    # Loop through each folder (topic) in the folder_to_search directory
    for topic in os.listdir(folder_to_search):
        topic_path = os.path.join(folder_to_search, topic)

        # Ensure it's a directory before proceeding
        if os.path.isdir(topic_path):
            # Get all files that match the specified extensions
            files = [f for f in os.listdir(topic_path)
                     if os.path.isfile(os.path.join(topic_path, f)) and f.lower().endswith(tuple(extensions))]
            media_dict[topic] = files

    return media_dict


def upd_media():
    global animator_files, animator_configs

    extensions = ['.json']  # List of extensions to filter by
    animator_files = get_media_files(media_folder + "animator/", extensions)
    # print("Animators: " + str(animator_files))

    animator_configs = []
    for animator_file in animator_files["animators"]:
        cfg_animator = files.read_json_file(animators_folder + animator_file)
        animator_configs.append(cfg_animator)


upd_media()

# This device only works if it is connected to the wifi network so no config setting for this.
web = True

cfg_main = files.read_json_file(code_folder + "mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file(code_folder + "mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfg_vol = files.read_json_file(code_folder + "mvc/volume_settings.json")
vol_set = cfg_vol["volume_settings"]

is_gtts_reachable = False

exit_set_hdw = False
local_ip = ""
mdns_to_ip = {}

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

l_sw = Debouncer(switch_io_1)
r_sw = Debouncer(switch_io_2)
three_sw = Debouncer(switch_io_3)
four_sw = Debouncer(switch_io_4)

################################################################################
# Setup sound

# Setup the mixer to play wav files
pygame.mixer.init()
mix = pygame.mixer.Channel(0)
mix_media = pygame.mixer.Channel(1)

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
    play_mix(code_folder + "mvc/" + "discovering_lifx_lights" + ".wav")
    lifx = LifxLAN()

    # Discover LIFX devices on the local network
    devices = lifx.get_devices()

    # Report the count of discovered devices
    device_count = len(devices)
    spk_str(str(device_count), False)
    play_mix(code_folder + "mvc/" + "lifx_lights_found" + ".wav")

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
    else:
        # Forward interpolation
        if type == "lifx":
            interpolated_values = [cfg["scene_changes"][key]
                                   # end_index is inclusive
                                   for key in ordered_scene_changes_keys[start_index:end_index + 1]]

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


def send_animator_post(url, endpoint, new_data=None):
    try:
        new_url = "http://" + url
        api_client = ApiClient(new_url)
        
        if new_data is not None:
            new_data_loads = json.loads(new_data)
            created_data = api_client.post(endpoint, data=new_data_loads)
        else:
            created_data = api_client.post(endpoint)
        
        print("POST response:", created_data)
        return created_data
    except Exception as e:
        print(f"Comms issue: {e}")
        return None  # Optionally return None or raise the exception, depending on your needs


################################################################################
# Setup serial communication

global ser


def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    available_ports = [port.device for port in ports]
    return available_ports


def open_serial_connection(port, baud_rate=115200):
    ser = serial.Serial(port, baud_rate, timeout=1)
    return ser


def get_usb_ports():
    ports = list_serial_ports()
    print("Available serial ports:", ports)
    text_to_wav_file("Available serial ports are", tmp_wav_file_name, 2)
    for port in ports:
        text_to_wav_file(port, tmp_wav_file_name, 2)

################################################################################
# Read and write serial commands connected to base3

def read_command():
    global exit_set_hdw
    while True:
        try:
            if ser.in_waiting >= 3:  # Check if at least 3 bytes are available to read
                received_data = ser.read(3)
                if len(received_data) == 3:
                    word1, word2, word3 = received_data[0], received_data[1], received_data[2]

                    # Convert words to binary strings
                    binary_word1 = f'{word1:0>8b}'
                    binary_word2 = f'{word2:0>8b}'
                    binary_word3 = f'{word3:0>8b}'
                    print(f"Word 1: {binary_word1}")
                    print(f"Word 2: {binary_word2}")
                    print(f"Word 3: {binary_word3}\n")

                    command_object = get_command_object(
                        binary_word1, binary_word2, binary_word3)

                    print(command_object["system"], command_object["device"],
                          command_object["address"], command_object["command"], command_object["data"], command_object["button"], command_object["value"])

                    binary_word1, binary_word2, binary_word3 = get_command_binary_words(command_object["system"], command_object["device"], command_object["address"], command_object["button"], command_object["value"])   
                    print(f"Word cmd 1: {binary_word1}")
                    print(f"Word cmd 2: {binary_word2}")
                    print(f"Word cmd 3: {binary_word3}\n")

                    matched_commands = animator_command_matches(command_object)

                    # Check if there are any matches
                    if matched_commands:
                        for matched_command, animator_command_rows in matched_commands:
                            # Print each matched command and animators command rows
                            # print(matched_command, command_object)
                            if matched_command:
                                exit_set_hdw = False
                                set_hdw(matched_command[1], 1,
                                        animator_command_rows["animatorIpAddress"])
                    else:
                        print("No matches found")

                    time.sleep(1)
                    ser.read(ser.in_waiting)
                else:
                    # Invalid command format, discard the data
                    ser.read(ser.in_waiting)
        except Exception as e:
            print(f"Comms issue: {e}")

def send_command(system, device, address, button, value):
    word1, word2, word3 = get_command_binary_words(system, device, address, button, value)

    byte1 = int(word1, 2).to_bytes(1, 'big')
    byte2 = int(word2, 2).to_bytes(1, 'big')
    byte3 = int(word3, 2).to_bytes(1, 'big')

    command = byte1 + byte2 + byte3

    try:
        ser.write(command)
        print(f"Sent command: {word1} {word2} {word3}")
        return True
    except Exception as e:
        print(f"Error sending command: {e}")
        return False

################################################################################
# Command decoding

def get_command_object(binary_word1, binary_word2, binary_word3):
    command_object = {}
    command_object["system"] = get_system(binary_word1)
    if binary_word1 == "11111110" and binary_word2 == "11111111" and binary_word3 == "11111111":
        command_object["system"] = "halt"
        command_object["device"] = "halt"
        command_object["address"] = "0000"
        command_object["button"] = "HALT"
        command_object["command"] = "absolute"
        command_object["value"] = "11"
        command_object["data"] = "11111"
        return command_object
    elif command_object["system"] == "tmcc":
        command = binary_word2[0:2]
        if command == "01":  # Switch command
            command_object["device"] = "switch"
            command_object["address"] = str(
                get_address(binary_word2, binary_word3, 7))
        elif command == "00":  # Engine command
            command_object["device"] = "engine"
            command_object["address"] = str(
                get_address(binary_word2, binary_word3, 7))
        elif command == "10":  # Accessory command
            command_object["device"] = "accessory"
            command_object["address"] = str(
                get_address(binary_word2, binary_word3, 7))
        elif command == "11":  # Route, train or group command
            command = binary_word2[0:4]
            if command == "1101":  # Route command
                command_object["device"] = "route"
            else:
                command = binary_word2[0:5]
                if command == "11001":  # Train command
                    command_object["device"] = "train"
                elif command == "11000":  # Group command
                    command_object["device"] = "group"
        command_object["command"] = get_command(binary_word3)
        command_object["data"] = get_data(binary_word3)
    command_object = get_button(command_object)
    return command_object


def get_system(binary_word1):
    bits_to_system = {
        "11111110": "tmcc",
        "11111000": "legacy_engine",
        "11111001": "legacy_train",
        "11111011": "parameter"
    }
    
    if binary_word1 not in bits_to_system:
        raise ValueError(f"Invalid binary_word1: {binary_word1}. Must be one of {list(bits_to_system.keys())}.")
    
    return bits_to_system[binary_word1]


def get_command(binary_word3):
    bits_to_command = {
        "00": "action",
        "01": "extended",
        "10": "relative",
        "11": "absolute"
    }
    
    command = binary_word3[1:3]
    
    if command not in bits_to_command:
        raise ValueError(f"Invalid command bits: {command}. Must be one of {list(bits_to_command.keys())}.")
    
    return bits_to_command[command]


def get_data(binary_word3):
    return binary_word3[3:8]
    
def get_address(binary_word2, binary_word3, number_bits):
    whole_word = binary_word2 + binary_word3
    start = 9 - number_bits
    end = start + number_bits
    binary_number = whole_word[start:end]
    int_returned = int(binary_number, 2)
    return int_returned


def get_button(command_object):
    global cfg
    speak_commands = cfg["tmcc_voice_enabled"]
    command_object["value"] = 0
    command_object["button"] = ""
    if command_object["device"] == "accessory" or command_object["device"] == "engine":
        if command_object["command"] != "extended" and command_object["data"] != "01011" and speak_commands:
            play_mix(code_folder + "mvc/" + command_object["device"] + ".wav")
            spk_str(str(command_object["address"]), False)
        if command_object["command"] == "extended" and command_object["data"] == "01011":
            if speak_commands:
                play_mix(code_folder + "mvc/" + command_object["device"] + ".wav")
                play_mix(code_folder + "mvc/set_to_id.wav")
                spk_str(str(command_object["address"]), False)
            command_object["button"] = "SET"
        elif command_object["command"] == "extended" and command_object["data"] == "01000":
            if speak_commands:
                play_mix(code_folder + "mvc/" + command_object["device"] + ".wav")
                spk_str(str(command_object["address"]), False)
                play_mix(code_folder + "mvc/low_momentum.wav")
            command_object["button"] = "LOWM"
        elif command_object["command"] == "extended" and command_object["data"] == "01001":
            if speak_commands:
                play_mix(code_folder + "mvc/" + command_object["device"] + ".wav")
                spk_str(str(command_object["address"]), False)
                play_mix(code_folder + "mvc/medium_momentum.wav")
            command_object["button"] = "MEDM"
        elif command_object["command"] == "extended" and command_object["data"] == "01010":
            if speak_commands:
                play_mix(code_folder + "mvc/" + command_object["device"] + ".wav")
                spk_str(str(command_object["address"]), False)
                play_mix(code_folder + "mvc/high_momentum.wav")
            command_object["button"] = "HIGHM"
        elif command_object["command"] == "relative":
            # Relative Speed “D”
            # D = 0xA => +5
            # D = 0x9 => +4
            # .....
            # D = 0x5 => 0 (no change) 
            # .....
            # D = 0x1 => -4 
            # D = 0x0 => -5
            binary_number = command_object["data"][1:5]
            decimal_number = int(binary_number, 2)
            command_object["button"] = "KNOB"
            command_object["value"] = 0
            if decimal_number > 5:
                command_object["value"] = decimal_number - 5
                print("throttle up :" + str(command_object["value"]))
                if speak_commands:
                    play_mix(code_folder + "mvc/trottle_up.wav")
                    spk_str(str(command_object["value"]), False)
            elif decimal_number < 5 :
                command_object["value"] = decimal_number - 5
                print("throttle down :" + str(command_object["value"]))
                if speak_commands:
                    play_mix(code_folder + "mvc/trottle_down.wav")
                    spk_str(str(command_object["value"]), False)
        elif command_object["command"] == "action" and command_object["data"] == "00001":
            if speak_commands:
                play_mix(code_folder + "mvc/direction.wav")
            command_object["button"] = "DIR"
        elif command_object["command"] == "action" and command_object["data"] == "11100":
            if speak_commands:
                play_mix(code_folder + "mvc/horn.wav")
            command_object["button"] = "HORN"
        elif command_object["command"] == "action" and command_object["data"] == "11101":
            if speak_commands:
                play_mix(code_folder + "mvc/bell.wav")
            command_object["button"] = "BELL"
        elif command_object["command"] == "action" and command_object["data"] == "00100":
            if speak_commands:
                play_mix(code_folder + "mvc/boost.wav")
            command_object["button"] = "BOOST"
        elif command_object["command"] == "action" and command_object["data"] == "00111":
            if speak_commands:
                play_mix(code_folder + "mvc/brake.wav")
            command_object["button"] = "BRAKE"
        elif command_object["command"] == "action" and command_object["data"] == "00101":
            if speak_commands:
                play_mix(code_folder + "mvc/front_coupler.wav")
            command_object["button"] = "FCOUPLER"
        elif command_object["command"] == "action" and command_object["data"] == "00110":
            if speak_commands:
                play_mix(code_folder + "mvc/rear_coupler.wav")
            command_object["button"] = "RCOUPLER"
        elif command_object["command"] == "action" and command_object["data"] == "01001":
            if speak_commands:
                play_mix(code_folder + "mvc/aux_1.wav")
            command_object["button"] = "AUX1"
        elif command_object["command"] == "action" and command_object["data"] == "01101":
            if speak_commands:
                play_mix(code_folder + "mvc/aux_2.wav")
            command_object["button"] = "AUX2"
        elif command_object["command"] == "action" and command_object["data"][0:1] == "1":
            binary_number = command_object["data"][1:5]
            decimal_number = int(binary_number, 2)
            if speak_commands:
                play_mix(code_folder + "mvc/numeric_button.wav")
                spk_str(str(decimal_number), False)
            command_object["button"] = str(decimal_number)

    if command_object["device"] == "switch":
        if command_object["command"] != "extended" and command_object["data"] != "01011" and speak_commands:
            play_mix(code_folder + "mvc/switch.wav")
            spk_str(str(command_object["address"]), False)
        if command_object["command"] == "extended" and command_object["data"] == "01011":
            if speak_commands:
                play_mix(code_folder + "mvc/switch.wav")
                play_mix(code_folder + "mvc/set_to_id.wav")
                spk_str(str(command_object["address"]), False)
            command_object["button"] = "SET"
        elif command_object["command"] == "action" and command_object["data"][0:5] == "00000":
            if speak_commands:
                play_mix(code_folder + "mvc/through.wav")
            command_object["button"] = "THROUGH"
        elif command_object["command"] == "action" and command_object["data"][0:5] == "11111":
            if speak_commands:
                play_mix(code_folder + "mvc/out.wav")
            command_object["button"] = "OUT"

    if command_object["device"] == "halt":
        if speak_commands:
            play_mix(code_folder + "mvc/halt.wav")
        command_object["button"] = "HALT"
    return command_object


def scale_number(num, exponent):
    return int((num if num >= 0 else -(-num)) ** exponent)


def animator_command_matches(command_object):
    global animator_configs
    # command_object = {
    # "system": "tmcc",
    # "device": "engine",
    # "address": 1,
    # "command": "action",
    # "data": "01001",
    # "button": "AUX1",
    # "value": 0
    # }
    matches = []  # Initialize an empty list to store matches

    for animator_config in animator_configs:
        if animator_config["device"] == command_object["device"] and animator_config["address"] == command_object["address"] or command_object["device"] == "halt":
            for row in animator_config['table_data']:
                if row[0] == command_object["button"]:
                    # Append the matched row and item to the list
                    matches.append((row, animator_config))
    return matches  # Return all matches


################################################################################
# Command encoding

def get_command_binary_words(system, device, address, button, value=0):
    address = int(address)
    
    if button == "HALT":
        binary_word1 = "11111110"
        binary_word2 = "11111111"
        binary_word3 = "11111111"
        return binary_word1, binary_word2, binary_word3

    binary_word1 = set_system(system)
    binary_word2 = set_device("00000000", device)
    binary_word3 = get_command_and_data(button, "00000000", value)
    binary_word2, binary_word3 = set_address(binary_word2, binary_word3, 7, address)
    return binary_word1, binary_word2, binary_word3

def set_system(command):
    system_to_bits = {
        "tmcc": "11111110",
        "legacy_engine": "11111000",
        "legacy_train": "11111001",
        "parameter": "11111011"
    }
    
    if command not in system_to_bits:
        raise ValueError(f"Invalid command: {command}. Must be one of {list(system_to_bits.keys())}.")
    
    return system_to_bits[command]

def set_device(binary_word2, device):
    # Device-to-command mapping
    device_command_mapping = {
        "engine": "00",      # 2 bits (index 0-1)
        "switch": "01",      # 2 bits (index 0-1)
        "accessory": "10",   # 2 bits (index 0-1)
        "route": "1101",     # 4 bits (index 0-3)
        "train": "11001",    # 5 bits (index 0-4)
        "group": "11000"     # 5 bits (index 0-4)
    }

    # Check if binary_word2 is exactly 8 bits
    if len(binary_word2) != 8:
        print(f"Error: binary_word2 '{binary_word2}' must be exactly 8 bits")
        return binary_word2  # Return unchanged word on error

    # Check if device is valid
    if device not in device_command_mapping:
        print(f"Warning: Device '{device}' not recognized")
        return binary_word2  # Return unchanged word

    # Get the command bits for the device
    new_command = device_command_mapping[device]
    command_length = len(new_command)

    # Extract the unchanged portion of binary_word2 (bits after the command)
    remaining_bits = binary_word2[command_length:]

    # Construct new word with updated command bits and unchanged remaining bits
    new_word = new_command + remaining_bits

    # Ensure the new word is exactly 8 bits (should always be true with this mapping)
    if len(new_word) != 8:
        print(f"Error: New word '{new_word}' is not 8 bits after modification")
        return binary_word2  # Return unchanged word on error

    return new_word

def set_address(binary_word2, binary_word3, number_bits, id):
    binary_int = bin(id)[2:]
    binary_int = binary_int.zfill(number_bits)
    
    max_value = 2 ** number_bits - 1
    if id > max_value:
        raise ValueError(f"int_supplied ({id}) is too large to fit in {number_bits} bits. Max value is {max_value}.")
    
    whole_word = binary_word2 + binary_word3
    
    start = 9 - number_bits
    end = start + number_bits
    
    new_whole_word = whole_word[:start] + binary_int + whole_word[end:]

    new_binary_word2 = new_whole_word[:8]
    new_binary_word3 = new_whole_word[8:]
    
    return new_binary_word2, new_binary_word3

def get_command_and_data(button, binary_word3, value=0):
    # Command mapping
    command_mapping = {
        "action": "00",
        "extended": "01",
        "relative": "10",
        "absolute": "11"
    }

    # Named button mappings for accessory/engine
    accessory_engine_buttons = {
        "SET": ("extended", "01011"),
        "LOWM": ("extended", "01000"),
        "MEDM": ("extended", "01001"),
        "HIGHM": ("extended", "01010"),
        "DIR": ("action", "00001"),
        "HORN": ("action", "11100"),  # Checked before numeric buttons
        "BELL": ("action", "11101"),  # Checked before numeric buttons
        "BOOST": ("action", "00100"),
        "BRAKE": ("action", "00111"),
        "FCOUPLER": ("action", "00101"),
        "RCOUPLER": ("action", "00110"),
        "AUX1": ("action", "01001"),
        "AUX2": ("action", "01101"),
        "KNOB": ("relative", None),  # Data will be set based on value
        "SPEED": ("absolute", None)  # Data will be set based on value (0-31)
    }

    # Named button mappings for switch
    switch_buttons = {
        "SET": ("extended", "01011"),
        "THROUGH": ("action", "00000"),
        "OUT": ("action", "11111")
    }

    # Check if binary_word3 is exactly 8 bits
    if len(binary_word3) != 8:
        print(f"Error: binary_word3 '{binary_word3}' must be exactly 8 bits")
        return binary_word3  # Return unchanged word on error

    # Extract prefix (index 0, unchanged)
    prefix = binary_word3[0]  # Index 0 (1 bit, unchanged)

    # Check named buttons (accessory/engine)
    if button in accessory_engine_buttons:
        command_type, default_data = accessory_engine_buttons[button]
        new_command = command_mapping[command_type]
        if button == "KNOB":
            # Map value (-5 to +5) to data field
            if not -5 <= value <= 5:
                print(f"Warning: Value {value} for KNOB must be between -5 and 5")
                return binary_word3  # Return unchanged word
            decimal_number = value + 5  # Shift to 0-10 (0x0 to 0xA)
            new_data = "0" + format(decimal_number, "04b")  # 00000 to 01010 (data[0] = 0)
        elif button == "SPEED":
            # Map value (0 to 31) to data field
            if not 0 <= value <= 31:
                print(f"Warning: Value {value} for SPEED must be between 0 and 31")
                return binary_word3  # Return unchanged word
            new_data = format(value, "05b")  # 00000 to 11111 (direct 5-bit encoding)
        else:
            new_data = default_data
        new_word = prefix + new_command + new_data
        return new_word

    # Check named buttons (switch)
    if button in switch_buttons:
        command_type, new_data = switch_buttons[button]
        new_command = command_mapping[command_type]
        new_word = prefix + new_command + new_data
        return new_word

    # Handle numeric buttons (0 through 9 only)
    if button.isdigit():
        num = int(button)
        if 0 <= num <= 9:  # Only consider values 0 through 9
            new_data = "1" + format(num, "04b")  # 10000 to 11001
            new_command = command_mapping["action"]
            new_word = prefix + new_command + new_data
            return new_word
        else:
            print(f"Warning: Numeric button {button} is invalid (must be 0-9)")
            return binary_word3  # Return unchanged word

    print(f"Warning: Button {button} not found")
    return binary_word3  # Return unchanged word

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


################################################################################
# Setup routes

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

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
        elif self.path == "/speaker":
            self.speaker_post(post_data_obj)
        elif self.path == "/get-scene-changes":
            self.get_scene_changes_post(post_data_obj)
        elif self.path == "/update-host-name":
            self.update_host_name_post(post_data_obj)
        elif self.path == "/lights":
            self.lights_lifx_post(post_data_obj)
        elif self.path == "/lights-scene":
            self.lights_scene_post(post_data_obj)
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
        elif self.path == "/set-tmcc-voice-enabled":
            self.set_tmcc_voice_enabled(post_data_obj)
        elif self.path == "/get-volume":
            self.get_volume_post(post_data_obj)
        elif self.path == "/get-lifx-enabled":
            self.get_lifx_enabled(post_data_obj)
        elif self.path == "/get-tmcc-voice-enabled":
            self.get_tmcc_voice_enabled(post_data_obj)
        elif self.path == "/get-scripts":
            self.get_scripts_post(post_data_obj)
        elif self.path == "/create-animator":
            self.create_animator_post(post_data_obj)
        elif self.path == "/get-animator":
            self.get_animator_post(post_data_obj)
        elif self.path == "/delete-animator":
            self.delete_animator_post(post_data_obj)
        elif self.path == "/save-animator-data":
            self.save_animator_data_post(post_data_obj)
        elif self.path == "/rename-animator":
            self.rename_animator_post(post_data_obj)
        elif self.path == "/test-animation":
            self.test_animation_post(post_data_obj)
        elif self.path == "/get-local-ip":
            self.get_local_ip(post_data_obj)

    def test_animation_post(self, rq_d):
        global exit_set_hdw
        exit_set_hdw = False
        # Replace "default_value" with whatever you want
        url = rq_d.get("ip", "")
        response = set_hdw(rq_d["an"], 3, url)
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

    def rename_animator_post(self, rq_d):
        global data
        fo = animators_folder + rq_d["fo"]
        fn = animators_folder + rq_d["fn"] + ".json"
        os.rename(fo, fn)
        upd_media()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "your response message"
        self.wfile.write(response.encode('utf-8'))
        print("Response sent:", response)

    data = []

    def save_animator_data_post(self, rq_d):
        f_n = animators_folder + rq_d["fn"]
        files.write_json_file(f_n, rq_d)
        upd_media()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "file save successfully"
        self.wfile.write(response.encode('utf-8'))

    def delete_animator_post(self, rq_d):
        f_n = animators_folder + rq_d["fn"]
        os.remove(f_n)
        upd_media()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["fn"] + " animator file deleted"
        self.wfile.write(response.encode('utf-8'))

    def get_animator_post(self, rq_d):
        global cfg, ts_mode
        if (f_exists(animators_folder + rq_d["an"]) == True):
            f_n = animators_folder + rq_d["an"]
            self.handle_serve_file_name(f_n)
            return
        else:
            f_n = code_folder + "animator_def/animator.json"
            self.handle_serve_file_name(f_n)
            return

    def get_scripts_post(self, rq_d):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = animator_files["animators"]
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def create_animator_post(self, rq_d):
        global data
        f_n = animators_folder + rq_d["fn"] + ".json"
        an_data = {
            "fn": f_n,
            "device": "accessory",
            "address": 1,
            "table_data": [
                [
                    "AUX1",
                    ""
                ],
                [
                    "AUX2",
                    ""
                ]
            ]
        }
        files.write_json_file(f_n, an_data)
        upd_media()
        gc_col("created animator")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = "created " + rq_d["fn"] + " animator"
        self.wfile.write(response.encode('utf-8'))

    def mode_post(self, rq_d):
        print(rq_d)
        global cfg
        if rq_d["an"] == "left":
            override_switch_state["switch_value"] = "left"
        elif rq_d["an"] == "right":
            override_switch_state["switch_value"] = "right"
        elif rq_d["an"] == "right_held":
            override_switch_state["switch_value"] = "right_held"
        elif rq_d["an"] == "three":
            override_switch_state["switch_value"] = "three"
        elif rq_d["an"] == "four":
            override_switch_state["switch_value"] = "four"
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"mode processed": rq_d["an"]}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def defaults_post(self, rq_d):
        global cfg
        if rq_d["an"] == "reset_to_defaults":
            rst_def()
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix(code_folder + "mvc/all_changes_complete.wav")
            st_mch.go_to('base_state')
        elif rq_d["an"] == "reset_scene_to_defaults":
            cfg["scene_changes"] = copy.deepcopy(default_cfg["scene_changes"])
            files.write_json_file(code_folder + "cfg.json", cfg)
            play_mix(code_folder + "mvc/all_changes_complete.wav")
            st_mch.go_to('base_state')
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def speaker_post(self, rq_d):
        global cfg
        if rq_d["an"] == "speaker_test":
            cmd_snt = "speaker_test"
            play_mix(code_folder + "mvc/left_speaker_right_speaker.wav")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def get_scene_changes_post(self, rq_d):
        response = cfg["scene_changes"]
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

    def set_tmcc_voice_enabled(self, rq_d):
        global cfg
        cfg["tmcc_voice_enabled"] = rq_d["enabled"]
        files.write_json_file(code_folder + "cfg.json", cfg)
        response = cfg["tmcc_voice_enabled"]
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

    def get_tmcc_voice_enabled(self, rq_d):
        response = cfg["tmcc_voice_enabled"]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def lights_lifx_post(self, rq_d):
        global exit_set_hdw
        exit_set_hdw = False
        set_hdw(rq_d["an"], 1, "")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = rq_d["an"]
        self.wfile.write(response.encode('utf-8'))

    def lights_scene_post(self, rq_d):
        global current_scene, exit_set_hdw
        current_scene = rq_d["an"]
        rgb_value = cfg["scene_changes"][current_scene]
        exit_set_hdw = False
        command = "LX0_" + str(rgb_value[0]) + "_" + \
            str(rgb_value[1]) + "_" + str(rgb_value[2])
        set_hdw(command, 0, "")
        response = rgb_value
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("Response sent:", response)

    def set_item_lights(self, rq_d):
        global current_scene, exit_set_hdw
        exit_set_hdw = False
        if rq_d["item"] == "lifx":
            command = "LX0_" + str(rq_d["r"]) + "_" + \
                str(rq_d["g"]) + "_" + str(rq_d["b"])
            set_hdw(command, 0, "")
            if current_scene != "":
                cfg["scene_changes"][current_scene] = [
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
        # Get the local IP address
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")

        QUEUE_PORT = 8001
        PORT = 8083

        httpd = None

        def start_http_server():
            global httpd
            handler = MyHttpRequestHandler
            httpd = socketserver.TCPServer((local_ip, PORT), handler)
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


def clear_command_queue():
    """Clear all commands from the queue."""
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_commands():
    """Stop all commands and clear the queue."""
    global exit_set_hdw
    clear_command_queue()
    exit_set_hdw = True
    mix.stop()
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
    mix.set_volume(volume_0_1*0.7)
    mix_media.set_volume(volume_0_1*0.7)
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
    play_mix(code_folder + "mvc/volume.wav")
    spk_str(cfg["volume"], False)


def play_mix(file_name, wait_until_done=True, allow_exit=True):
    print("playing " + file_name)
    if mix.get_busy():
        mix.stop()
        while mix.get_busy():
            pass
    mix_sound = pygame.mixer.Sound(file_name)
    upd_vol(.05)
    mix.play(mix_sound, loops=0)
    while mix.get_busy() and wait_until_done:
        if allow_exit:
            exit_early()
    print("done playing")


def play_mix_media(file_name):
    print("playing " + file_name)
    if mix_media.get_busy():
        mix_media.stop()
        while mix.get_busy():
            pass
    mix_media_sound = pygame.mixer.Sound(file_name)
    upd_vol(.05)
    mix_media.play(mix_media_sound, loops=0)
    print("done playing")


def wait_snd():
    while mix_media.get_busy():
        exit_early()
    print("done playing")


def stop_all_media():
    mix.stop()
    mix_media.stop()
    while mix.get_busy() or mix_media.get_busy():
        pass


def exit_early():
    switch_state = utilities.switch_state(
        l_sw, r_sw, time.sleep, 3.0, override_switch_state)
    if switch_state == "left":
        stop_all_media()
    time.sleep(0.05)


def spk_str(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_mix(code_folder + "mvc/" + character + ".wav")
        except Exception as e:
            files.log_item(e)
            print("Invalid character in string to speak")
    if addLocal:
        play_mix(code_folder + "mvc/dot_local_colon_8083.wav")


def l_r_but():
    play_mix(code_folder + "mvc/press_left_button_right_button.wav")


def sel_web():
    play_mix(code_folder + "mvc/web_menu.wav")
    l_r_but()


def opt_sel():
    play_mix(code_folder + "mvc/option_selected.wav")


def spk_sng_num(song_number):
    play_mix(code_folder + "mvc/song.wav")
    spk_str(song_number, False)


def no_trk():
    global override_switch_state
    play_mix(code_folder + "mvc/no_user_soundtrack_found.wav")
    while True:
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            break
        if switch_state == "right":
            play_mix(code_folder + "mvc/create_sound_track_files.wav")
            break


def spk_web():
    play_mix(code_folder + "mvc/animator_available_on_network.wav")
    play_mix(code_folder + "mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-base3":
        play_mix(code_folder + "mvc/animator_dash_base3.wav")
        play_mix(code_folder + "mvc/dot_local_colon_8083.wav")
    else:
        spk_str(cfg["HOST_NAME"], True)
    play_mix(code_folder + "mvc/in_your_browser.wav")


def get_random_joke():
    url = "https://official-joke-api.appspot.com/jokes/random"
    response = requests.get(url)

    if response.status_code == 200:
        joke = response.json()
        print(f"{joke['setup']} - {joke['punchline']}")
    else:
        print("Failed to retrieve a joke.")

    text_to_wav_file(joke['setup'], tmp_wav_file_name, 2)
    text_to_wav_file(joke['punchline'], tmp_wav_file_name, 2)

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

        play_mix(file_name)

    except TimeoutException:
        print("TTS operation timed out.")
        is_gtts_reachable = False
    except Exception as e:
        print(f"An error occurred: {e}")
        is_gtts_reachable = False


###################################################################################
# Hardware commands


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


def set_hdw(cmd, dur, url):
    global sp, br, exit_set_hdw

    if cmd == "":
        return "NOCMDS"

    if "API_" in cmd:
        segs = [cmd]
    else:
        segs = cmd.split(",")

    try:
        for seg in segs:
            if exit_set_hdw:
                return "STOP"
            if seg[0] == 'E':  # end an
                return "STOP"
            # USB connect to base3 usb port
            elif seg[:3] == 'USB':
                get_usb_ports()
            # switch SW_XXXX = Switch XXXX (left,right,three,four,left_held, ...)
            elif seg[:2] == 'SW':
                segs_split = seg.split("_")
                if len(segs_split) == 2:
                    override_switch_state["switch_value"] = segs_split[1]
                elif len(segs_split) == 3:
                    override_switch_state["switch_value"] = segs_split[1] + \
                        "_" + segs_split[2]
                else:
                    override_switch_state["switch_value"] = "none"
            # lights LXZZZ_R_G_B = Lifx lights ZZZ (0 All, 1 to 999) RGB 0 to 255
            elif seg[:2] == 'LX':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_light_color(light_n, r, g, b)
            # lights LPZZZ_YYY = Lifx lights ZZZ (0 All, 1 to 999) YYY power ON or OFF
            elif seg[:2] == 'LP':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                power = segs_split[1]
                set_light_power(light_n, power)
            # ZL_S_E_T_I = Scene change S start E end using (daylight,afternoon,....), time, increments
            elif seg[:2] == 'ZL':
                segs_split = seg[3:].split("_")
                scene_change("lifx", segs_split[0], segs_split[1],
                             float(segs_split[2]), int(segs_split[3]))
            # ZJ = Joke
            elif seg[:2] == 'ZJ':
                get_random_joke()
            # API_UUU_EEE_DDD = Api POST call UUU base url, EEE endpoint, DDD data object i.e. {"an": data_object}
            if seg[:3] == 'API':
                seg_split = split_string(seg)
                print(seg_split)
                if len(seg_split) == 3:
                    print("three params")
                    response = send_animator_post(url, seg_split[1], seg_split[2])
                    return response
                elif len(seg_split) == 4:
                    print("four params")
                    max_retries = 2
                    attempts = 0
                    while attempts < max_retries:
                        ip_from_mdns = get_ip_from_mdns(seg_split[1], overwrite=(attempts > 0))
                        print(f"Attempt {attempts + 1}: Resolved {seg_split[1]} to {ip_from_mdns}")
                        if ip_from_mdns:
                            try:
                                response = send_animator_post(ip_from_mdns, seg_split[2], seg_split[3])
                                if response is not None:  # Assuming None indicates failure
                                    return response
                                print(f"send_animator_post failed with {ip_from_mdns}, retrying...")
                            except Exception as e:
                                print(f"Error with {ip_from_mdns}: {e}, retrying...")
                        else:
                            print(f"Failed to resolve {seg_split[1]} to an IP, retrying...")
                        attempts += 1
                    
                    # If all retries fail, assume the mDNS entry no longer exists and clean up
                    if attempts >= max_retries:
                        if seg_split[1] in mdns_to_ip:
                            del mdns_to_ip[seg_split[1]]
                            print(f"Removed {seg_split[1]} from dictionary after {max_retries} failed attempts")
                        return "host not found after retries"
            # TMCC_DDD_ID_BUTTON_VALUE = TMCC command DDD device ("engine", "switch", "accessory", "route", "train", "group"), 
            # ID 1 to 99, button (SET, LOWM, MEDM, HIGHM, DIR, HORN, BELL, BOOST, BRAKE, FCOUPLER, RCOUPLER,
            # AUX1, AUX2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, HALT, KNOB, SPEED) VALUE is optional (KNOB 1-9, SPEED 0-31)
            if seg[:4] == 'TMCC':
                seg_split = split_string(seg)
                device = seg_split[1]
                id = int(seg_split[2])
                button = seg_split[3]
                value = 0
                if button == "KNOB" or button == "SPEED":
                    value = int(seg_split[4])
                send_command("tmcc", device, id, button, value)
    except Exception as e:
        files.log_item(e)


def split_string(seg):
    # Find the position of the first '_{' and the last '}'
    start_idx = seg.find('_{')
    end_idx = seg.find('}', start_idx)

    if start_idx != -1 and end_idx != -1:
        # Extract the object part including the curly braces
        object_part = seg[start_idx:end_idx+1]

        # Remove the object part from the string
        seg = seg[:start_idx] + seg[end_idx+1:]

        # Remove the leading underscore from the object part
        object_part = object_part[1:]  # Strip the first character '_'
    else:
        object_part = ''  # If no object is found, set it to empty

    # Now split the remaining part by underscores
    parts = seg.split('_')

    # Add the object part as the last item
    if object_part:
        parts.append(object_part)

    return parts

def get_ip_address(hostname):
    response = send_animator_post(hostname, "get-local-ip")
    return response

def get_ip_from_mdns(mdns_name, overwrite=False):
    # Check if mdns_name itself looks like an IP address (with or without port)
    ip_part = mdns_name.split(':')[0] if ':' in mdns_name else mdns_name
    is_ip = '.' in ip_part and all(part.isdigit() for part in ip_part.split('.'))

    if is_ip:
        # If it's already an IP, return it as-is without adding to dictionary
        print(f"{mdns_name} is already an IP address, skipping dictionary")
        return mdns_name
    else:
        # Use the full mdns_name (with port if present) as the key
        if mdns_name in mdns_to_ip and not overwrite:
            ip_with_port = mdns_to_ip[mdns_name]
            print(f"Found {mdns_name} in dictionary: {ip_with_port}")
        else:
            # Extract port from mdns_name if it exists
            port = None
            if ':' in mdns_name:
                _, port = mdns_name.rsplit(':', 1)
                if not port.isdigit():
                    port = None

            # Get the IP address using the full mdns_name (including port if present)
            ip_address = get_ip_address(mdns_name)

            # Validate the IP address and append the port if it exists
            if ip_address and isinstance(ip_address, str) and '.' in ip_address and all(part.isdigit() for part in ip_address.split('.')):
                # Append the original port to the IP if it exists
                ip_with_port = f"{ip_address}:{port}" if port else ip_address
                mdns_to_ip[mdns_name] = ip_with_port
                print(f"Resolved and added {mdns_name}: {ip_with_port} to the dictionary")
            else:
                print(f"Resolved {mdns_name} to {ip_address}, but it doesn't look like an IP - not adding to dictionary")
                ip_with_port = None

        return ip_with_port


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
        play_mix(code_folder + "mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global override_switch_state
        switch_state = utilities.switch_state_four_switches(
            l_sw, r_sw, three_sw, four_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            add_command(cfg["option_selected"])
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
        play_mix(code_folder + "mvc/main_menu.wav")
        l_r_but()
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global override_switch_state
        switch_state = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state)
        if switch_state == "left":
            play_mix(code_folder + "mvc/" + main_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(main_m)-1:
                self.i = 0
        if switch_state == "right":
            sel_mnu = main_m[self.sel_i]
            if sel_mnu == "web_options":
                mch.go_to('web_options')
            elif sel_mnu == "volume_level_adjustment":
                mch.go_to('volume_level_adjustment')
            else:
                play_mix(code_folder + "mvc/all_changes_complete.wav")
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
        play_mix(code_folder + "mvc/volume_adjustment_menu.wav")
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
                play_mix(code_folder + "mvc/all_changes_complete.wav")
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
            play_mix(code_folder + "mvc/" + web_m[self.i] + ".wav")
            self.sel_i = self.i
            self.i += 1
            if self.i > len(web_m)-1:
                self.i = 0
        if switch_state == "right":
            selected_menu_item = web_m[self.sel_i]
            if selected_menu_item == "hear_url":
                spk_str(cfg["HOST_NAME"], True)
                sel_web()
            if selected_menu_item == "hear_ip":
                spk_str(local_ip, True)
                sel_web()
            elif selected_menu_item == "hear_instr_web":
                play_mix(code_folder + "mvc/hear_instr_web_drive_in.wav")
                sel_web()
            elif selected_menu_item == "update_ssid_password_from_usb":
                play_mix(code_folder + "mvc/update_ssid_password_from_usb.wav")
                update_ssid_password_from_usb()
                restart_pi_timer()
            else:
                mch.go_to('base_state')

###############################################################################
# Create the state machine


st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())
st_mch.add(VolumeLevelAdjustment())
st_mch.add(WebOpt())

time.sleep(0.05)
aud_en.value = True
upd_vol(0.05)

if (web):
    files.log_item("starting server...")
    try:
        # Register mDNS service
        zeroconf = Zeroconf()
        print("Registering mDNS service...")
        zeroconf.register_service(mdns_info)

        # Run the server in a separate thread to allow mDNS to work simultaneously
        server_thread = threading.Thread(target=start_http_server)
        server_thread.daemon = True
        server_thread.start()

    except OSError:
        web = False
        files.log_item("server did not start...")

discover_lights()

is_gtts_reachable = check_gtts_status()

if (web):
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

if connect_to_base_3 == True:
    target_port = "/dev/ttyUSB0"
    ports = list_serial_ports()
    if target_port in ports:
        ser = open_serial_connection(target_port)
        play_mix(code_folder + "mvc/connected_to_base3.wav")

        # Start a thread to continuously read from the serial port
        read_thread = threading.Thread(
            target=read_command)
        read_thread.daemon = True
        read_thread.start()


def stop_program():
    stop_all_commands()
    if (web):
        print("Unregistering mDNS service...")
        zeroconf.unregister_service(mdns_info)
        zeroconf.close()
        httpd.shutdown()
    ser.close()
    quit()


while True:
    try:
        input("Press enter to exit...\n\n")
    finally:
        stop_program()


# type: ignore
