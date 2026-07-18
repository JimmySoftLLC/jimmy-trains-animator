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

import utilities
from adafruit_debouncer import Debouncer
from rainbowio import colorwheel
import neopixel
import asyncio
import microcontroller
import random
import board
import digitalio
import busio
import time
import gc
import files
import os
import adafruit_vl53l4cd
import json
import displayio
import i2cdisplaybus
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font


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
# Sd card config variables and globals

animators_folder = "/animations/"

cfg = files.read_json_file("cfg.json")

web = cfg["serve_webpage"]

exit_set_hdw_async = False

gc_col("config setup")

animations = []
mnu_o = []

def upd_media():
    global animations, mnu_o
    animations = []
    mnu_o = []
    animations = files.return_directory("", "animations", ".json")
    mnu_o.extend(animations)
    rnd_o = ['random all']
    mnu_o.extend(rnd_o)

upd_media()

br = 0
mdns_to_ip = {}
exit_set_hdw_async = False
an_just_added = False
an_running = False
button_release_required = False
button_lockout_until = 0
override_switch_state = {}
override_switch_state["switch_value"] = ""
last_displayed_train_pos = None

################################################################################
# setup switches

# -------------------------------------------------------------------
# Left bumper:
#   GP21 = input with pull-up
#   GP22 = output LOW (acts as ground)
# -------------------------------------------------------------------

gnd_pin = digitalio.DigitalInOut(board.GP22)
gnd_pin.direction = digitalio.Direction.OUTPUT
gnd_pin.value = False

l_sw_io = digitalio.DigitalInOut(board.GP21)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)


# -------------------------------------------------------------------
# Right bumper:
#   GP8 = input with pull-up
#   GND = other side of switch
# -------------------------------------------------------------------

r_sw_io = digitalio.DigitalInOut(board.GP8)
r_sw_io.direction = digitalio.Direction.INPUT
r_sw_io.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw_io)

################################################################################
# Setup neo pixels

n_px = 1

# GP12 on smart bumper
neo_pixel_pin = board.GP12

indicator = neopixel.NeoPixel(neo_pixel_pin, n_px)


def set_red():
    indicator.fill((255, 0, 0))
    indicator.show()


def set_blue():
    indicator.fill((0, 0, 255))
    indicator.show()


def set_green():
    indicator.fill((0, 255, 0))
    indicator.show()


def set_white():
    indicator.fill((255, 255, 255))
    indicator.show()


def set_off():
    indicator.fill((0, 0, 0))
    indicator.show()


def show_mode(cycles, r, g, b):
    for _ in range(cycles):
        indicator.fill((r, g, b))
        time.sleep(.5)
        indicator.fill((0, 0, 0))
        time.sleep(.5)

set_white()
time.sleep(1)

set_off()

gc_col("Neopixels setup")

################################################################################
# OLED display

MAX_ACTIVE_DISPLAYS = 2
display_enabled = True

# When True, files.log_item() output is also shown on the OLED.
print_console = False

# OLED used for console output.
console_display_n = 0

# terminalio.FONT is approximately 6 pixels wide.
CONSOLE_CHARACTERS_PER_LINE = 21
CONSOLE_LINE_COUNT = 8
CONSOLE_LINE_SPACING = 8

console_lines = []
console_group = None
console_labels = []
console_initialized = False

PIN_MAP = {
    "GP0": board.GP0,
    "GP1": board.GP1,
    "GP26": board.GP26,
    "GP27": board.GP27,
}

i2c_busses = {}
display_buses = {}
displays = {}
display_groups = {}
active_display_nums = []

displayio.release_displays()


def get_pin(pin_name):
    return PIN_MAP[pin_name.upper()]


def i2c_addr(addr_text):
    return int(addr_text, 16)


def i2c_key(dev):
    return dev["sda"].upper() + "_" + dev["scl"].upper()


def get_i2c_bus(dev):
    key = i2c_key(dev)

    if key not in i2c_busses:
        i2c_busses[key] = busio.I2C(
            scl=get_pin(dev["scl"]),
            sda=get_pin(dev["sda"])
        )

    return i2c_busses[key]


def center_text(font, txt, y):
    t = label.Label(
        font,
        text=txt,
        color=0xFFFFFF
    )
    t.x = (128 - t.bounding_box[2]) // 2
    t.y = y
    return t

# Maximum number of fonts held in memory.
# Sizes 20 and 30 are permanent, leaving room for two variable sizes.
MAX_CACHED_FONTS = 4
DEFAULT_FONT_SIZES = (20, 30)

# Stores:
#     font size: loaded font object
font_cache = {}

# Tracks only non-default fonts, oldest first.
font_cache_order = []


def font_filename(font_size):
    return "fonts/Arial-BoldMT-" + str(font_size) + ".bdf"


def load_font(font_size):
    """
    Return a loaded font object.

    Font sizes 20 and 30 remain permanently cached.
    Other sizes are cached until the four-font limit is reached.
    The oldest non-default font is then removed.
    """
    font_size = int(font_size)

    # Return an existing cached font immediately.
    if font_size in font_cache:
        # Treat variable fonts as recently used.
        if font_size not in DEFAULT_FONT_SIZES:
            if font_size in font_cache_order:
                font_cache_order.remove(font_size)

            font_cache_order.append(font_size)

        return font_cache[font_size]

    # Make room before loading another variable font.
    if (
        font_size not in DEFAULT_FONT_SIZES
        and len(font_cache) >= MAX_CACHED_FONTS
    ):
        if font_cache_order:
            oldest_size = font_cache_order.pop(0)

            files.log_item(
                "Removing font " + str(oldest_size) + " from cache"
            )

            del font_cache[oldest_size]
            gc.collect()

    files.log_item("Loading font size " + str(font_size))

    loaded_font = bitmap_font.load_font(
        font_filename(font_size)
    )

    font_cache[font_size] = loaded_font

    if font_size not in DEFAULT_FONT_SIZES:
        font_cache_order.append(font_size)

    return loaded_font


# Load the two permanent fonts once during startup.
font_cache[20] = bitmap_font.load_font(font_filename(20))
font_cache[30] = bitmap_font.load_font(font_filename(30))

gc_col("Default fonts loaded")


if "i2c" not in cfg:
    cfg["i2c"] = [
        {"sda": "GP0", "scl": "GP1", "address": "3C"}
    ]
    files.write_json_file("cfg.json", cfg)


def valid_display(display_n):
    return display_n >= 0 and display_n < len(cfg["i2c"])


def clear_active_displays():
    global active_display_nums
    global console_group
    global console_labels
    global console_initialized

    displayio.release_displays()

    display_buses.clear()
    displays.clear()
    display_groups.clear()
    active_display_nums = []

    # DisplayIO objects were released, so rebuild the console next time.
    console_group = None
    console_labels = []
    console_initialized = False

def select_display(display_n):
    global active_display_nums, display_enabled

    if not display_enabled:
        return None

    if not valid_display(display_n):
        return None

    if display_n in displays:
        return displays[display_n]

    dev = cfg["i2c"][display_n]
    new_bus_key = i2c_key(dev)

    for active_n in active_display_nums:
        active_dev = cfg["i2c"][active_n]
        if i2c_key(active_dev) == new_bus_key:
            clear_active_displays()
            break

    if len(displays) >= MAX_ACTIVE_DISPLAYS:
        clear_active_displays()

    try:
        i2c_bus = get_i2c_bus(dev)

        # Optional but helpful: verify the display address exists
        while not i2c_bus.try_lock():
            pass
        try:
            found = i2c_bus.scan()
        finally:
            i2c_bus.unlock()

        addr = i2c_addr(dev["address"])
        if addr not in found:
            print("No OLED found at address " + dev["address"])
            return None

        display_bus = i2cdisplaybus.I2CDisplayBus(
            i2c_bus,
            device_address=addr
        )

        disp = adafruit_displayio_ssd1306.SSD1306(
            display_bus,
            width=128,
            height=64
        )

        grp = displayio.Group()
        disp.root_group = grp

        display_buses[display_n] = display_bus
        displays[display_n] = disp
        display_groups[display_n] = grp
        active_display_nums.append(display_n)

        return disp

    except Exception as e:
        print(e)
        return None
    
def set_display_group(display_n, group):
    disp = select_display(display_n)
    if disp is None:
        return

    disp.root_group = group
    display_groups[display_n] = group

def initialize_console():
    """
    Create the OLED console labels once.

    Reusing labels avoids creating and destroying display objects
    every time a message is logged.
    """
    global console_group
    global console_labels
    global console_initialized

    if console_initialized:
        return True

    if not valid_display(console_display_n):
        return False

    disp = select_display(console_display_n)

    if disp is None:
        return False

    console_group = displayio.Group()
    console_labels = []

    for line_number in range(CONSOLE_LINE_COUNT):
        console_label = label.Label(
            terminalio.FONT,
            text="",
            color=0xFFFFFF,
            x=0,
            y=4 + line_number * CONSOLE_LINE_SPACING
        )

        console_labels.append(console_label)
        console_group.append(console_label)

    console_initialized = True
    return True


def split_console_line(text):
    """
    Split one message into lines that fit the 128-pixel-wide OLED.

    Existing newline characters are also honored.
    """
    wrapped_lines = []

    for original_line in str(text).split("\n"):
        if original_line == "":
            wrapped_lines.append("")
            continue

        while len(original_line) > CONSOLE_CHARACTERS_PER_LINE:
            wrapped_lines.append(
                original_line[:CONSOLE_CHARACTERS_PER_LINE]
            )
            original_line = original_line[
                CONSOLE_CHARACTERS_PER_LINE:
            ]

        wrapped_lines.append(original_line)

    return wrapped_lines


def refresh_console():
    """
    Update the existing OLED label objects with the newest messages.
    """
    if not initialize_console():
        return

    for line_number in range(CONSOLE_LINE_COUNT):
        if line_number < len(console_lines):
            console_labels[line_number].text = console_lines[line_number]
        else:
            console_labels[line_number].text = ""

    set_display_group(console_display_n, console_group)


def console_write(item):
    """
    Callback used by files.log_item().

    This function must accept one string argument.
    """
    global console_lines

    if not print_console:
        return

    new_lines = split_console_line(str(item))
    console_lines.extend(new_lines)

    # Keep only the newest lines that fit on the OLED.
    if len(console_lines) > CONSOLE_LINE_COUNT:
        console_lines = console_lines[-CONSOLE_LINE_COUNT:]

    refresh_console()


def clear_console():
    global console_lines

    console_lines = []

    if console_initialized:
        refresh_console()


def set_print_console(enabled):
    """
    Turn OLED console output on or off at runtime.
    """
    global print_console

    print_console = bool(enabled)

    if print_console:
        files.set_console_writer(console_write)
        refresh_console()
    else:
        files.set_console_writer(None)


def invert_display(display_n, invert_on):
    if select_display(display_n) is None:
        return
    try:
        if invert_on:
            display_buses[display_n].send(0xA7, "")
        else:
            display_buses[display_n].send(0xA6, "")
    except Exception as e:
        files.log_item(e)


def show_bmp(display_n, filename):
    if not valid_display(display_n):
        return

    bitmap = displayio.OnDiskBitmap(filename)

    tile_grid = displayio.TileGrid(
        bitmap,
        pixel_shader=bitmap.pixel_shader
    )

    tile_grid.x = (128 - bitmap.width) // 2
    tile_grid.y = (64 - bitmap.height) // 2

    group = displayio.Group()
    group.append(tile_grid)

    set_display_group(display_n, group)


def draw_text(display_n, line1, line2, line1_size=20, line2_size=30):
    if not valid_display(display_n):
        return

    line1_text = center_text(
        font_cache[line1_size],
        line1,
        12
    )

    line2_text = center_text(
        font_cache[line2_size],
        line2,
        40
    )

    group = displayio.Group()
    group.append(line1_text)
    group.append(line2_text)

    set_display_group(display_n, group)


def display_text(display_n, line1, line2, blink_times, background_on=False, line1_size=20, line2_size=30):
    if not valid_display(display_n):
        return

    draw_text(display_n, line1, line2, line1_size, line2_size)

    for x in range(blink_times):
        invert_display(display_n, True)
        time.sleep(1)
        invert_display(display_n, False)
        time.sleep(1)

    invert_display(display_n, background_on)


async def display_text_async(display_n, line1, line2, blink_times, background_on=False, line1_size=20, line2_size=30):
    if not valid_display(display_n):
        return

    draw_text(display_n, line1, line2, line1_size=20, line2_size=30)

    for x in range(blink_times):
        invert_display(display_n, True)
        await asyncio.sleep(1)
        invert_display(display_n, False)
        await asyncio.sleep(1)

    invert_display(display_n, background_on)


async def roll_text_async(
    display_n,
    line1,
    font_size,
    background_on=False
):
    if not valid_display(display_n):
        return

    invert_display(display_n, background_on)

    line1_text = label.Label(
        load_font(font_size),
        text=line1,
        color=0xFFFFFF
    )

    line1_text.y = 32

    group = displayio.Group()
    group.append(line1_text)

    set_display_group(display_n, group)

    text_width = line1_text.bounding_box[2]

    for x in range(128, -text_width, -1):
        line1_text.x = x
        await asyncio.sleep(0.01)


# Startup test
show_bmp(0, "fonts/logo.bmp")

if len(cfg["i2c"]) > 1:
    show_bmp(1, "fonts/logo.bmp")

time.sleep(1)

# Send files.log_item() messages to the OLED when enabled.
set_print_console(print_console)

files.log_item("OLED console initialized")

################################################################################
# setup distance sensor

i2c1 = busio.I2C(scl=board.GP3, sda=board.GP2, frequency=400000)

vl53 = adafruit_vl53l4cd.VL53L4CD(i2c1)

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200

files.log_item("VL53L4CD Simple Test.")
files.log_item("--------------------")
model_id, module_type = vl53.model_info
files.log_item("Model ID: 0x{:0X}".format(model_id))
files.log_item("Module Type: 0x{:0X}".format(module_type))
files.log_item("Timing Budget: {}".format(vl53.timing_budget))
files.log_item("Inter-Measurement: {}".format(vl53.inter_measurement))
files.log_item("--------------------")

vl53.start_ranging()

indicator.fill((255, 255, 0))
indicator.show()

while not vl53.data_ready:
    files.log_item("data not ready")
    time.sleep(.2)

for _ in range(3):
    vl53.clear_interrupt()
    time.sleep(0.1)
vl53.clear_interrupt()
train_pos = vl53.distance  # Distance in cm
files.log_item("Train pos: ", train_pos)

time.sleep(1)

indicator.fill((0, 0, 0))
indicator.show()
################################################################################
# Setup wifi and web server


def measure_signal_strength(MY_SSID, cycles):
    files.log_item("Monitoring signal for: " + MY_SSID)
    files.log_item(
        "Showing current RSSI + running average "
        "(simple sum + count)"
    )

    total_sum = 0.0
    count = 0
    avg_rssi = None

    while count < cycles:
        current_rssi = None

        try:
            for network in wifi.radio.start_scanning_networks():
                if network.ssid == MY_SSID:
                    current_rssi = network.rssi
                    break

            wifi.radio.stop_scanning_networks()

            if current_rssi is not None:
                total_sum += current_rssi
                count += 1
                avg_rssi = total_sum / count

                files.log_item(
                    str(round(time.monotonic(), 1))
                    + "s | "
                    + MY_SSID
                    + " RSSI="
                    + str(current_rssi)
                    + " Avg="
                    + str(round(avg_rssi, 1))
                    + " dBm"
                )
            else:
                files.log_item("SSID not found during scan")

        except Exception as e:
            files.log_item("Scan error: " + str(e))

            try:
                wifi.radio.stop_scanning_networks()
            except Exception:
                pass

        time.sleep(0.1)

    return avg_rssi


if (web):
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
    import adafruit_requests
    gc_col("config wifi imports")

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    local_ip = ""

    try:
        env = files.read_json_file("env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        files.log_item("Using env ssid and password")
    except Exception as e:
        files.log_item(e)
        files.log_item("Using default ssid and password")

    set_blue()

    for i in range(3):
        web = True
        try:
            # connect to your SSID
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            gc_col("wifi connect")

            # setup mdns server
            mdns = mdns.Server(wifi.radio)
            mdns.hostname = cfg["HOST_NAME"]
            mdns.advertise_service(
                service_type="_http", protocol="_tcp", port=80)

            # files.log_items IP address to REPL
            local_ip = str(wifi.radio.ipv4_address)
            files.log_item("IP is " + local_ip)
            files.log_item("Connected")

            # set up server
            pool = socketpool.SocketPool(wifi.radio)
            server = Server(pool, "/static", debug=True)
            server.port = 80  # Explicitly set port to 80

            # Set up requests session for HTTP requests
            requests = adafruit_requests.Session(pool)

            gc_col("wifi server")

            ################################################################################
            # Setup routes

            @server.route("/")
            def base(request: HTTPRequest):
                gc_col("Home page.")
                return FileResponse(request, "index.html", "/")

            @server.route("/mui.min.css")
            def base(request: HTTPRequest):
                return FileResponse(request, "mui.min.css", "/")

            @server.route("/mui.min.js")
            def base(request: HTTPRequest):
                return FileResponse(request, "mui.min.js", "/")

            @server.route("/animation", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                cfg["option_selected"] = rq_d["an"]
                add_command("AN_" + cfg["option_selected"])
                files.write_json_file("cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                if rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("cfg.json", cfg)
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/stop", [POST])
            def btn(request: Request):
                stop_all_commands()
                return Response(request, "Stopped all commands")
            
            @server.route("/set-debug-console", [POST])
            def set_debug_console_route(request: Request):
                try:
                    rq_d = request.json()
                    enabled_value = rq_d.get("enabled", False)

                    # Do not use bool("false"), because that evaluates to True.
                    if isinstance(enabled_value, str):
                        enabled = enabled_value.lower() in (
                            "true",
                            "1",
                            "on",
                            "yes"
                        )
                    else:
                        enabled = bool(enabled_value)

                    if enabled:
                        clear_console()
                        set_print_console(True)
                        files.log_item("OLED debugging enabled")
                        status = "on"
                    else:
                        # Log this before disconnecting the OLED callback so the
                        # final message appears on the OLED.
                        files.log_item("OLED debugging disabled")
                        set_print_console(False)
                        status = "off"

                        # Restore your normal status display.
                        if web and avg_rssi is not None:
                            dbm_string = str(-int(avg_rssi)) + "dbm"
                            display_text(
                                0,
                                cfg["HOST_NAME"] + ".local",
                                dbm_string,
                                0,
                                False
                            )

                    return Response(
                        request,
                        json.dumps({
                            "debug_console": status
                        }),
                        content_type="application/json"
                    )

                except Exception as e:
                    print("Set debug console route error:", e)

                    return Response(
                        request,
                        json.dumps({
                            "error": str(e)
                        }),
                        content_type="application/json",
                        status=500
                    )


            @server.route("/get-debug-console", [POST])
            def get_debug_console_route(request: Request):
                return Response(
                    request,
                    json.dumps({
                        "debug_console": print_console
                    }),
                    content_type="application/json"
                )

            @server.route("/lights", [POST])
            def btn(request: Request):
                global exit_set_hdw_async
                exit_set_hdw_async = False
                try:
                    rq_d = request.json()  # Parse the incoming JSON
                    # Schedule the async task
                    asyncio.create_task(set_hdw_async(rq_d["an"], 0))
                    return Response(request, "Utility: set lights successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/create-animation", [POST])
            def btn(request: Request):
                try:
                    global data, animators_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    files.log_item(rq_d)
                    f_n = animators_folder + rq_d["fn"] + ".json"
                    files.log_item(f_n)
                    an_data = ["0.0|", "1.0|",
                               "2.0|", "3.0|"]
                    files.write_json_file(f_n, an_data)
                    upd_media()
                    return Response(request, "Created animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error creating animation.")

            @server.route("/rename-animation", [POST])
            def btn(request: Request):
                try:
                    global data, animators_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    fo = animators_folder + rq_d["fo"] + ".json"
                    fn = animators_folder + rq_d["fn"] + ".json"
                    os.rename(fo, fn)
                    upd_media()
                    return Response(request, "Renamed animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/delete-animation", [POST])
            def btn(request: Request):
                try:
                    global data, animators_folder
                    rq_d = request.json()  # Parse the incoming JSON
                    files.log_item(rq_d)
                    f_n = animators_folder + rq_d["fn"] + ".json"
                    files.log_item(f_n)
                    os.remove(f_n)
                    upd_media()
                    return Response(request, "Delete animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/get-train-pos", [POST])
            def btn(req: Request):
                set_blue()
                for _ in range(3):
                    vl53.clear_interrupt()
                    time.sleep(0.1)
                vl53.clear_interrupt()
                train_pos = vl53.distance  # Distance in cm
                return Response(req, train_pos)
            set_green()


            @server.route("/update-host-name", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                cfg["HOST_NAME"] = rq_d["an"]
                files.write_json_file("cfg.json", cfg)
                mdns.hostname = cfg["HOST_NAME"]
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-host-name", [POST])
            def btn(request: Request):
                return Response(request, cfg["HOST_NAME"])

            @server.route("/get-local-ip", [POST])
            def btn(request: Request):
                return Response(request, local_ip)

            @server.route("/get-animations", [POST])
            def btn(request: Request):
                sounds = []
                sounds.extend(animations)
                my_string = files.json_stringify(sounds)
                return Response(request, my_string)

            @server.route("/test-animation", [POST])
            def btn(request: Request):
                global exit_set_hdw_async
                exit_set_hdw_async = False
                try:
                    set_blue()
                    rq_d = request.json()
                    files.log_item(rq_d["an"])
                    gc_col("Added hardware task.")
                    # Schedule the async task
                    asyncio.create_task(set_hdw_async(rq_d["an"], 3))
                    set_green()
                    return Response(request, "Test animation successfully")
                except Exception as e:
                    set_red()
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error test animation.")
                
            @server.route("/update-startup-string", [POST])
            def update_startup_string(req: Request):
                global cfg
                rq_d = req.json()
                if rq_d["action"] in ("save"):
                    cfg["startup_string"] = rq_d["text"]
                    files.write_json_file("cfg.json", cfg)
                    add_command(cfg["startup_string"])
                    return Response(req, cfg["startup_string"])
                
            @server.route("/get-startup-string", [POST])
            def get_startup_string(req: Request):
                return Response(req, cfg["startup_string"])

            @server.route("/get-animation", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                snd_f = rq_d["an"]
                if (f_exists("animations/" + snd_f + ".json") == True):
                    f_n = "animations/" + snd_f + ".json"
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")

            data = []

            @server.route("/save-data", [POST])
            def btn(request: Request):
                global data
                rq_d = request.json()
                try:
                    if rq_d[0] == 0:
                        data = []
                    data.extend(rq_d[2])
                    if rq_d[0] == rq_d[1]:
                        f_n = "animations/" + rq_d[3] + ".json"
                        files.write_json_file(f_n, data)
                        data = []
                        gc_col("get data")
                    upd_media()
                except Exception as e:
                    files.log_item(e)
                    data = []
                    gc_col("get data")
                    return Response(request, "out of memory")
                return Response(request, "success")
            break
        except Exception as e:
            web = False
            files.log_item(e)
            time.sleep(2)

    set_off()


def send_animator_get(url, endpoint=""):
    try:
        # Construct the full URL (e.g., "http://httpbin.org" + "/get")
        full_url = "http://" + url + "/" + endpoint
        files.log_item("Sending GET request to " + full_url)
        response = requests.get(full_url)
        files.log_item("GET Response: " + response.text)
        created_data = response.text  # Store response to return
        response.close()
        return created_data
    except Exception as e:
        files.log_item("GET request failed: " + str(e))
        return None  # Return None on failure


def send_animator_post(url, endpoint, new_data=None):
    try:
        new_url = "http://" + url + "/" + endpoint
        files.log_item("Sending POST request to " + new_url)

        if new_data is not None:
            files.log_item("sending new_data object")
            if isinstance(new_data, str):
                new_data_loads = json.loads(new_data)
                response = requests.post(new_url, json=new_data_loads)
            else:
                response = requests.post(new_url, json=new_data)
        else:
            files.log_item("not sending new_data object")
            response = requests.post(new_url, json={"status": "empty"}
                                     )

        files.log_item("POST Response: " + response.text)
        created_data = response.text
        response.close()
        return created_data
    except Exception as e:
        files.log_item("Comms issue: " + str(e))
        return None
    
if (web):
    cycles = 10
    avg_rssi = measure_signal_strength(WIFI_SSID, cycles)
    files.log_item(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")


gc_col("web server")

################################################################################
# Command queue
command_queue = []


def add_command(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        files.log_item("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        files.log_item("Command added to the end:", command)


async def process_commands():
    global last_an_call_end

    while command_queue:
        command = command_queue.pop(0)
        if command.startswith("AN_"):
            filename = command[3:]
            if filename:
                await an_async(filename)
                await asyncio.sleep(0)
        else:
            await set_hdw_async(command)
            await asyncio.sleep(0)


def clear_command_queue():
    command_queue.clear()
    files.log_item("Command queue cleared.")


def stop_all_commands():
    global exit_set_hdw_async
    clear_command_queue()
    exit_set_hdw_async = True
    files.log_item("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"


################################################################################
# animations

async def an_async(f_nm):
    global an_running

    files.log_item("Filename:", f_nm)
    cur = f_nm
    an_running = True

    try:
        if f_nm == "random all":
            hi = len(animations) - 1
            cur = animations[random.randint(0, hi)]

        await an_light_async(cur)

    except Exception as e:
        files.log_item(e)

    finally:
        an_running = False
        display_text(
            0,
            "Animation",
            "Done",
            0,
            False,
            20,
            30
        )

async def an_light_async(f_nm):
    global exit_set_hdw_async

    animation_path = "animations/" + f_nm + ".json"

    if not f_exists(animation_path):
        files.log_item("Animation file not found:", animation_path)
        return

    flsh_t = files.read_json_file(animation_path)

    if not flsh_t:
        files.log_item("Animation file is empty:", animation_path)
        return

    # Add end commands so the final real timestamp gets processed.
    ft_last = flsh_t[-1].split("|")
    tm_last = float(ft_last[0]) + 0.001

    flsh_t.append(str(tm_last) + "|E")
    flsh_t.append(str(tm_last + 0.001) + "|E")

    flsh_i = 0
    srt_t = time.monotonic()

    while flsh_i < len(flsh_t) - 1:

        # Either bumper stops the current animation.
        if not l_sw_io.value or not r_sw_io.value:
            files.log_item("Bumper pressed - stopping animation")
            stop_all_commands()
            return "STOP"

        if exit_set_hdw_async:
            files.log_item("Animation stop requested")
            return "STOP"

        ft1 = flsh_t[flsh_i].split("|")
        ft2 = flsh_t[flsh_i + 1].split("|")

        timestamp = float(ft1[0])
        dur = float(ft2[0]) - timestamp - 0.25

        if dur < 0:
            dur = 0

        t_past = time.monotonic() - srt_t

        if t_past > timestamp - 0.25:
            files.log_item(
                "time elapsed: "
                + str(t_past)
                + " Timestamp: "
                + ft1[0]
            )

            if len(ft1) > 1 and ft1[1] != "":
                result = await set_hdw_async(ft1[1], dur)

                if result == "STOP":
                    return "STOP"

            flsh_i += 1

        await asyncio.sleep(0)

##############################
# animation effects


async def random_effect(il, ih, d):
    i = random.randint(il, ih)
    if i == 1:
        await rbow(.005, d)
    elif i == 2:
        multi_color()
        await asyncio.sleep(d)
    elif i == 3:
        await fire(d)


async def rbow(spd, dur):
    global exit_set_hdw_async
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw_async:
                return
            pixel_index = (i * 256 // n_px) + j
            indicator[0] = colorwheel(pixel_index & 255)
            indicator.show()
            await asyncio.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
        for j in reversed(range(0, 255, 1)):
            if exit_set_hdw_async:
                return
            pixel_index = (i * 256 // n_px) + j
            indicator[0] = colorwheel(pixel_index & 255)
            indicator.show()
            await asyncio.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return


async def fire(dur):
    global exit_set_hdw_async
    st = time.monotonic()

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker, based on our initial RGB values
    while True:
        f = random.randint(0, 110)
        r1 = bnd(r-f, 0, 255)
        g1 = bnd(g-f, 0, 255)
        b1 = bnd(b-f, 0, 255)
        indicator[0] = (r1, g1, b1)
        indicator.show()
        await asyncio.sleep(random.uniform(0.05, 0.1))
        te = time.monotonic()-st
        if te > dur:
            return


def multi_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    indicator[0] = (r, g, b)


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c

async def set_hdw_async(input_string, dur=0):
    global sp, br, exit_set_hdw_async, vl53, last_displayed_train_pos

    segs = input_string.split(",")

    try:
        for seg in segs:

            if exit_set_hdw_async:
                return "STOP"

            # End animation
            if seg[0] == 'E':
                return "STOP"

            # L_R_G_B = NeoPixel RGB
            elif seg[:1] == 'L':
                segs_split = seg.split("_")
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                indicator[0] = (r, g, b)

            # BXXX = Brightness 000 to 100
            elif seg[0:1] == 'B':
                br = int(seg[1:])
                indicator.brightness = float(br / 100)
                indicator.show()

            # FXXX_TTT = Fade brightness
            elif seg[0] == 'F':
                segs_split = seg.split("_")
                v = int(segs_split[0][1:])
                s = float(segs_split[1])

                while not br == v:
                    if exit_set_hdw_async:
                        return "STOP"

                    if br < v:
                        br += 1
                    else:
                        br -= 1

                    indicator.brightness = float(br / 100)
                    indicator.show()
                    await asyncio.sleep(s)

            # ZRAND = Random effect
            elif seg == 'ZRAND':
                await random_effect(1, 3, dur)

            # ZRTTT = Rainbow
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                await rbow(v, dur)

            # ZFIRE = Fire
            elif seg == 'ZFIRE':
                await fire(dur)

            # ZCOLCH = Color change
            elif seg == 'ZCOLCH':
                multi_color()
                await asyncio.sleep(dur)

            # QXXXX = Queue another command
            elif seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)

            # DT_NN_LLL_MMM_CC_BB = Display text
            elif seg[:2] == "DT":
                segs_split = seg.split("_")
                screen_number = int(segs_split[1])
                line1 = segs_split[2]
                line2 = segs_split[3]
                cycles = int(segs_split[4])
                background = bool(int(segs_split[5]))

                await display_text_async(
                    screen_number,
                    line1,
                    line2,
                    cycles,
                    background
                )

            # RT_NN_LLL_FF_BB = Rolling text
            elif seg[:2] == "RT":
                segs_split = seg.split("_")
                screen_number = int(segs_split[1])
                line1 = segs_split[2]
                font_size = int(segs_split[3])
                background = bool(int(segs_split[4]))

                await roll_text_async(
                    screen_number,
                    line1,
                    font_size,
                    background
                )

            # WXXX = Wait
            elif seg[0] == 'W':
                s = float(seg[1:])
                start_wait = time.monotonic()

                while time.monotonic() - start_wait < s:
                    if exit_set_hdw_async:
                        return "STOP"

                    if not l_sw_io.value or not r_sw_io.value:
                        stop_all_commands()
                        return "STOP"

                    await asyncio.sleep(0.05)

            # API_UUU_EEE_DDD = API POST call
            elif seg[:3] == 'API':
                seg_split = split_string(seg)

                files.log_item("Split segment: " + str(seg_split))
                files.log_item("Four params")

                max_retries = 2
                attempts = 0

                while attempts < max_retries:

                    if exit_set_hdw_async:
                        return "STOP"

                    if not l_sw_io.value or not r_sw_io.value:
                        stop_all_commands()
                        return "STOP"

                    ip_from_mdns = get_ip_from_mdns(
                        seg_split[1],
                        overwrite=(attempts > 0)
                    )

                    files.log_item(
                        "Attempt "
                        + str(attempts + 1)
                        + ": Resolved "
                        + seg_split[1]
                        + " to "
                        + str(ip_from_mdns)
                    )

                    if ip_from_mdns:
                        try:
                            response = send_animator_post(
                                ip_from_mdns,
                                seg_split[2],
                                seg_split[3]
                            )

                            if response is not None:
                                return response

                            files.log_item(
                                "send_animator_post failed with "
                                + str(ip_from_mdns)
                                + ", retrying..."
                            )

                        except Exception as e:
                            files.log_item(
                                "Error with "
                                + str(ip_from_mdns)
                                + ": "
                                + str(e)
                                + ", retrying..."
                            )
                    else:
                        files.log_item(
                            "Failed to resolve "
                            + seg_split[1]
                            + " to an IP, retrying..."
                        )

                    attempts += 1

                if attempts >= max_retries:
                    if seg_split[1] in mdns_to_ip:
                        del mdns_to_ip[seg_split[1]]

                        files.log_item(
                            "Removed "
                            + seg_split[1]
                            + " from dictionary after "
                            + str(max_retries)
                            + " failed attempts"
                        )

                    return "host not found after retries"

            # TMCC command
            elif seg[:4] == 'TMCC':
                seg_split = split_string(seg)

                device = seg_split[1]
                ii = int(seg_split[2])
                button = seg_split[3]
                value = None

                if button in ["KNOB", "SPEED"]:
                    value = int(seg_split[4])

                command = (
                    'API_animator-base3.local:8083_test-animation_'
                    '{"an":"TMCC_'
                    + device
                    + "_"
                    + str(ii)
                    + "_"
                    + button
                )

                display_text(
                    0,
                    "TMCC cmd",
                    f"{button} {value}" if value is not None else button,
                    0,
                    False,
                    20,
                    20
                )

                if value is not None:
                    command += "_" + str(value)

                command += '"}'

                result = await set_hdw_async(command, 0)

                if result == "STOP":
                    return "STOP"

            # POS_II_PPP_GL_DDD_SSS_TT
            elif seg[:3] == 'POS':
                seg_split = seg.split("_")

                ii = int(seg_split[1])
                position = float(seg_split[2])
                gl = seg_split[3]
                direction = seg_split[4]
                speed = int(seg_split[5])
                time_out = float(seg_split[6])

                stop_requested = False

                # Set direction
                command = (
                    'API_animator-base3.local:8083_test-animation_'
                    '{"an":"TMCC_engine_'
                    + str(ii)
                    + "_"
                    + direction
                    + '"}'
                )

                display_text(
                    0,
                    "TMCC cmd",
                    direction,
                    0,
                    False,
                    20,
                    20
                )

                result = await set_hdw_async(command, 0)

                if result == "STOP":
                    return "STOP"

                # Clear initial measurements
                for _ in range(3):
                    vl53.clear_interrupt()
                    await asyncio.sleep(0.1)

                # Set speed
                command = (
                    'API_animator-base3.local:8083_test-animation_'
                    '{"an":"TMCC_engine_'
                    + str(ii)
                    + "_SPEED_"
                    + str(speed)
                    + '"}'
                )

                display_text(
                    0,
                    "TMCC cmd",
                    "SPEED " + str(speed),
                    0,
                    False,
                    20,
                    20
                )

                result = await set_hdw_async(command, 0)

                if result == "STOP":
                    return "STOP"

                srt_t = time.monotonic()

                while True:
                    vl53.clear_interrupt()
                    train_pos = vl53.distance

                    files.log_item("train pos: ", train_pos)

                    if (
                        not print_console
                        and train_pos != last_displayed_train_pos
                    ):
                        last_displayed_train_pos = train_pos

                        display_text(
                            0,
                            "Train Position",
                            str(train_pos) + " cm",
                            0,
                            False
                        )

                    if gl == "L":
                        if train_pos < position:
                            files.log_item("target found")
                            break
                    else:
                        if train_pos > position:
                            files.log_item("target found")
                            break

                    if time.monotonic() - srt_t > time_out:
                        files.log_item("target timeout exceeded")
                        break

                    # Just spill out of the move.
                    if not l_sw_io.value or not r_sw_io.value:
                        files.log_item("Bumper pressed during POS")
                        stop_requested = True
                        break

                    if exit_set_hdw_async:
                        files.log_item("POS stop requested")
                        stop_requested = True
                        break

                    await asyncio.sleep(0.1)

                # Existing normal stop command.
                command = (
                    'API_animator-base3.local:8083_test-animation_'
                    '{"an":"TMCC_engine_'
                    + str(ii)
                    + '_SPEED_0"}'
                )

                # Temporarily allow this final stop command to execute.
                previous_exit_state = exit_set_hdw_async
                exit_set_hdw_async = False

                display_text(
                    0,
                    "TMCC cmd",
                    "SPEED 0",
                    0,
                    False,
                    20,
                    20
                )

                await set_hdw_async(command, 0)

                exit_set_hdw_async = previous_exit_state

                # Spill completely out of the animation.
                if stop_requested:
                    stop_all_commands()
                    return "STOP"

        return None

    except Exception as e:
        files.log_item(e)
        return None


def split_string(seg):
    start_idx = seg.find('_{')
    end_idx = seg.find('}', start_idx)

    if start_idx != -1 and end_idx != -1:
        object_part = seg[start_idx:end_idx+1]
        seg = seg[:start_idx] + seg[end_idx+1:]
        object_part = object_part[1:]  # Strip the leading '_'
    else:
        object_part = ''

    parts = seg.split('_')
    if object_part:
        parts.append(object_part)

    return parts


def get_ip_address(hostname):
    response = send_animator_post(hostname, "get-local-ip")
    return response


def get_ip_from_mdns(mdns_name, overwrite=False):
    ip_part = mdns_name.split(':')[0] if ':' in mdns_name else mdns_name
    is_ip = '.' in ip_part and all(part.isdigit()
                                   for part in ip_part.split('.'))

    if is_ip:
        files.log_item(
            f"{mdns_name} is already an IP address, skipping dictionary")
        return mdns_name
    else:
        if mdns_name in mdns_to_ip and not overwrite:
            ip_with_port = mdns_to_ip[mdns_name]
            files.log_item(f"Found {mdns_name} in dictionary: {ip_with_port}")
        else:
            port = None
            if ':' in mdns_name:
                _, port = mdns_name.rsplit(':', 1)
                if not port.isdigit():
                    port = None

            ip_address = get_ip_address(mdns_name)

            if ip_address and isinstance(ip_address, str) and '.' in ip_address and all(part.isdigit() for part in ip_address.split('.')):
                ip_with_port = f"{ip_address}:{port}" if port else ip_address
                mdns_to_ip[mdns_name] = ip_with_port
                files.log_item(
                    f"Resolved and added {mdns_name}: {ip_with_port} to the dictionary")
            else:
                files.log_item(
                    f"Resolved {mdns_name} to {ip_address}, but it doesn't look like an IP - not adding to dictionary")
                ip_with_port = None

        return ip_with_port
    
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
        return 'base_state'

    def enter(self, mch):
        files.log_item("Entered base state")
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        global an_just_added
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state, False)
        if (sw == "left" or sw == "right") and not an_running:
            add_command("AN_" + cfg["option_selected"])
            an_just_added = True
        elif (sw == "left_held" or sw == "right_held"):
            mch.go_to('main_menu')


class Main(Ste):
    def __init__(self):
        self.i = 0
        self.sel_i = 0

    @property
    def name(self):
        return "main_menu"

    def enter(self, mch):
        files.log_item("Main menu")
        indicator.fill((0, 0, 120))
        Ste.enter(self, mch)

    def exit(self, mch):
        Ste.exit(self, mch)

    def upd(self, mch):
        sw = utilities.switch_state(
            l_sw, r_sw, time.sleep, 3.0, override_switch_state, False)
        if (sw == "left" or sw == "right"):
            self.sel_i = self.i
            if self.sel_i == len(mnu_o) - 1:
                show_mode(1, 255, 255, 255)
            else:
                show_mode(self.sel_i + 1, 255, 255, 0)
            self.i += 1
            if self.i > len(mnu_o) - 1:
                self.i = 0
        if (sw == "left_held" or sw == "right_held"):
            cfg["option_selected"] = mnu_o[self.sel_i]
            indicator.fill((0, 255, 0))
            files.write_json_file("cfg.json", cfg)
            mch.go_to("base_state")

###############################################################################
# Create the state machine

st_mch = StMch()
st_mch.add(BseSt())
st_mch.add(Main())

################################################################################
# Start server

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        dbm_string = str(-int(avg_rssi))+"dbm"
        display_text(0, cfg["HOST_NAME"] + ".local", dbm_string, 0, 0)
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()

files.log_item("animator has started...")
gc_col("animations started.")

if web:
    set_green()
else:
    set_red()

st_mch.go_to('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

################################################################################
# Main task handling


startup_command_sent = False

async def process_commands_task():
    global startup_command_sent
    while True:
        if not startup_command_sent:
            await asyncio.sleep(2)
            startup_command_sent = True
            add_command(cfg["startup_string"])
        try:
            await process_commands()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0.01)


async def server_poll_task(server):
    """Poll the web server."""
    while True:
        try:
            server.poll()  # Web server polling
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks


async def garbage_collection_task():
    while True:
        await asyncio.sleep(60)
        if not an_running:
            gc.collect()


async def state_mach_upd_task(st_mch):
    global an_just_added
    while True:
        st_mch.upd()
        if an_just_added:
            await asyncio.sleep(3)
            an_just_added = False
        else:
            await asyncio.sleep(0.02)


async def main():
    # Create asyncio tasks
    tasks = [
        process_commands_task(),
        garbage_collection_task(),
        state_mach_upd_task(st_mch)
    ]

    if web:
        tasks.append(server_poll_task(server))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

