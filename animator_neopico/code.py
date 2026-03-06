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

from rainbowio import colorwheel
import neopixel
import asyncio
import microcontroller
import random
import board
import time
import gc
import files
import os
from adafruit_motor import servo
import pwmio

# used for the neo decoder
import pulseio
import digitalio


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    files.log_item("Point " + collection_point +
                   " Available memory: {} bytes".format(start_mem))


def f_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def rst():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()


gc_col("Imports gc, files")

################################################################################
# pin setups prototype

# prototype unit
# neo_branch_pin = board.GP6
# led_indicator_pin = board.GP14

# s_1_pin = board.GP8
# s_2_pin = board.GP9
# s_3_pin = board.GP12
# s_4_pin = board.GP13
# s_5_pin = board.GP14
# s_6_pin = board.GP22

# red_pin = board.GP3
# green_pin = board.GP2
# blue_pin = board.GP4

# animator pico board
neo_branch_pin = board.GP16
led_indicator_pin = board.GP17

s_1_pin = board.GP10
s_2_pin = board.GP11
s_3_pin = board.GP12
s_4_pin = board.GP13
s_5_pin = board.GP14
s_6_pin = board.GP22

red_pin = board.GP6
green_pin = board.GP8
blue_pin = board.GP9

################################################################################
# Sd card config variables

animators_folder = "/animations/"

cfg = files.read_json_file("cfg.json")

ts_jsons = files.return_directory("", "t_s_def", ".json")

web = cfg["serve_webpage"]

exit_set_hdw = False

gc_col("config setup")

def upd_media():
    global animations
    animations = files.return_directory("", "animations", ".json")

upd_media()

override_switch_state = {}
override_switch_state["switch_value"] = ""

################################################################################
# Setup the servos
s_1 = pwmio.PWMOut(s_1_pin, duty_cycle=2 ** 15, frequency=50)
s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)

s_2 = pwmio.PWMOut(s_2_pin, duty_cycle=2 ** 15, frequency=50)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)

s_3 = pwmio.PWMOut(s_3_pin, duty_cycle=2 ** 15, frequency=50)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

s_4 = pwmio.PWMOut(s_4_pin, duty_cycle=2 ** 15, frequency=50)
s_4 = servo.Servo(s_4, min_pulse=500, max_pulse=2500)

s_5 = pwmio.PWMOut(s_5_pin, duty_cycle=2 ** 15, frequency=50)
s_5 = servo.Servo(s_5, min_pulse=500, max_pulse=2500)

s_6 = pwmio.PWMOut(s_6_pin, duty_cycle=2 ** 15, frequency=50)
s_6 = servo.Servo(s_6, min_pulse=500, max_pulse=2500)

s_arr = [s_1, s_2, s_3, s_4, s_5, s_6]

################################################################################
# Setup neo pixels (main light string)

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
neorelays = []
neopicos = []

bar_arr = []
bolt_arr = []
neo_arr = []

n_px = 1  # keep non-zero so NeoPixel init doesn't choke before we rebuild

neo_branch = neopixel.NeoPixel(neo_branch_pin, n_px)
neo_branch.auto_write = False
neo_branch.fill((0, 0, 20))
neo_branch.show()

led_indicator = neopixel.NeoPixel(led_indicator_pin, 1)
led_indicator.auto_write = False
led_indicator.fill((0, 0, 20))
led_indicator.show()

pixel_scale = [(1.0, 1.0, 1.0)] * n_px
logical_led = {}


def clear_pixel_scale_all():
    """Clear ALL calibration (persistent) + reset runtime scalers to 1.0 on allowed light pixels."""
    cfg["pixel_scale"] = {}
    files.write_json_file("cfg.json", cfg)

    # reset runtime list
    for i in only_lights:
        pixel_scale[i] = (1.0, 1.0, 1.0)

    refresh_allowed_leds()


def clear_pixel_scale_one(i: int):
    """Clear ONE pixel calibration (0-based), persistent + runtime."""
    if i < 0 or i >= n_px:
        return
    if i not in only_lights_set:
        return  # IMPORTANT: relays/picos/etc are NOT lights

    # remove from cfg if present
    ps = cfg.get("pixel_scale", {}) or {}
    if str(i) in ps:
        del ps[str(i)]
        cfg["pixel_scale"] = ps
        files.write_json_file("cfg.json", cfg)

    # reset runtime
    pixel_scale[i] = (1.0, 1.0, 1.0)

    refresh_allowed_leds()


def bld_tree(p):
    i = []
    for t in trees:
        for ledi in t:
            si = ledi
            break
        if p == "ornaments":
            for ledi in range(0, 7):
                i.append(ledi + si)
        if p == "star":
            for ledi in range(7, 14):
                i.append(ledi + si)
        if p == "branches":
            for ledi in range(14, 21):
                i.append(ledi + si)
    return i


def bld_cane(p):
    i = []
    for c in canes:
        for led_i in c:
            si = led_i
            break
        if p == "end":
            for led_i in range(0, 2):
                i.append(led_i + si)
        if p == "start":
            for led_i in range(2, 4):
                i.append(led_i + si)
    return i


def bld_bar():
    i = []
    for b in bars:
        for l in b:
            si = l
            break
        for l in range(0, 10):
            i.append(l + si)
    return i


def bld_bolt():
    i = []
    for b in bolts:
        for l in b:
            si = l
            break
        if len(b) == 4:
            for l in range(0, 4):
                i.append(l + si)
        if len(b) == 1:
            for l in range(0, 1):
                i.append(l + si)
    return i


def bld_neo():
    i = []
    for n in neos:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l + si)
    return i

def bld_neorelay():
    i = []
    for n in neorelays:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l+si)
    return i


def bld_neopico():
    i = []
    for n in neopicos:
        for l in n:
            si = l
            break
        for l in range(0, 6):
            i.append(l+si)
    return i

def show_l():
    neo_branch.show()
    time.sleep(.05)
    neo_branch.fill((0, 0, 0))
    neo_branch.show()


def l_tst():
    global ornmnts, stars, brnchs, cane_s, cane_e, bar_arr, bolt_arr, neo_arr, neorelay_arr, neopico_arr

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

    # Neorelay items
    neorelay_arr = bld_neorelay()

    # Neopico items
    neopico_arr = bld_neopico()

    # cane test
    cnt = 0
    for i in cane_s:
        neo_branch[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0
    for i in cane_e:
        neo_branch[i] = (50, 50, 50)
        cnt += 1
        if cnt > 1:
            show_l()
            cnt = 0

    # tree test
    cnt = 0
    for i in ornmnts:
        neo_branch[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in stars:
        neo_branch[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0
    for i in brnchs:
        neo_branch[i] = (50, 50, 50)
        cnt += 1
        if cnt > 6:
            show_l()
            cnt = 0

    # bar test
    for b in bars:
        for l in b:
            neo_branch[l] = (50, 50, 50)
        neo_branch.show()
        time.sleep(.3)
        neo_branch.fill((0, 0, 0))
        neo_branch.show()

    # bolt test
    for b in bolts:
        for l in b:
            neo_branch[l] = (50, 50, 50)
        neo_branch.show()
        time.sleep(.3)
        neo_branch.fill((0, 0, 0))
        neo_branch.show()

    # nood test
    for n in noods:
        neo_branch[n[0]] = (50, 50, 50)
        neo_branch.show()
        time.sleep(.3)
        neo_branch.fill((0, 0, 0))
        neo_branch.show()

    # neo test
    for n in neos:
        for i in n:
            neo_branch[i] = (0, 50, 0)
            time.sleep(.3)
            neo_branch.show()
            neo_branch[i] = (50, 0, 0)
            time.sleep(.3)
            neo_branch.show()
            neo_branch[i] = (0, 0, 50)
            time.sleep(.3)
            neo_branch.show()
            time.sleep(.3)
            neo_branch.fill((0, 0, 0))
            neo_branch.show()

    # reorelay test
    for n in neorelays:
        for i in n:
            neo_branch[i] = (255, 0, 0)
            neo_branch.show()
            time.sleep(.3)
            neo_branch[i] = (0, 255, 0)
            neo_branch.show()
            time.sleep(.3)
            neo_branch[i] = (0, 0, 255)
            neo_branch.show()
            time.sleep(.3)
            neo_branch[i] = (0, 0, 0)
            neo_branch.show()
            time.sleep(.3)

    # neopico test
    for n in neopicos:
        for i in n:
            neo_branch[i] = (80, 20, 20)
            neo_branch.show()
            time.sleep(1)
            neo_branch[i] = (20, 20, 20)
            neo_branch.show()
            time.sleep(.3)

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def load_pixel_scale_from_cfg():
    """Load sparse per-pixel RGB scalers from cfg['pixel_scale'] into pixel_scale list."""
    scales = cfg.get("pixel_scale", {}) or {}
    for k, v in scales.items():
        try:
            i = int(k)
            if i < 0 or i >= n_px:
                continue
            if i not in only_lights_set:
                continue  # IMPORTANT: relays/picos/etc are NOT lights
            rs, gs, bs = float(v[0]), float(v[1]), float(v[2])
            pixel_scale[i] = (clamp01(rs), clamp01(gs), clamp01(bs))
        except Exception:
            continue

def upd_l_str():
    global trees, canes, bars, bolts, noods, neos, neorelays, neopicos, only_lights, only_lights_set, n_px, neo_branch, pixel_scale, logical_led
    trees = []
    canes = []
    bars = []
    bolts = []
    noods = []
    neos = []
    neorelays = []
    neopicos = []
    only_lights = []

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
            if typ == 'neorelay':
                if qty == 3:
                    neorelayqty = 1
                s = list(range(n_px, n_px + neorelayqty))
                neorelays.append(s)
                n_px += neorelayqty
            if typ == 'neopico':
                s = list(range(n_px, n_px + qty))
                neopicos.append(s)
                n_px += qty

    print("Number of pixels total: ", n_px)
    try:
        neo_branch.deinit()
    except Exception:
        pass
    neo_branch = neopixel.NeoPixel(neo_branch_pin, n_px)
    neo_branch.auto_write = False
    neo_branch.brightness = 1.0

    # reset per-pixel scalers and logical cache whenever the light string changes
    pixel_scale = [(1.0, 1.0, 1.0)] * n_px
    logical_led = {}

    # --- flatten + sort + dedupe only_lights ---
    only_lights = []

    # normal groups (segments are lists of pixel indices)
    for group in (trees, canes, bars, bolts, neos):
        for seg in group:
            only_lights.extend(seg)

    # noods are [pixel_index, qty] — only first element is a pixel index
    for n in noods:
        only_lights.append(n[0])

    only_lights = sorted(set(only_lights))
    only_lights_set = set(only_lights)

    load_pixel_scale_from_cfg()

    l_tst()

upd_l_str()

########################################################################################################################
# Neo pixel / neo 6 module methods
# ---------------------------------------------------------------------------
# Per-allowed-pixel brightness (software brightness, NOT neo_branch.brightness)

neo_brightness = 1.0  # 0.0 .. 1.0
br = 100

# Shadow buffer of "logical" (unscaled) colors for allowed pixels only
# key: pixel index, value: (r,g,b) UNBRIGHTENED (0..255)
logical_led = {}


def persist_pixel_scale(i: int, rs: float, gs: float, bs: float):
    """Save a single pixel scaler to cfg.json (sparse dict). i is 0-based."""
    cfg.setdefault("pixel_scale", {})
    cfg["pixel_scale"][str(i)] = [clamp01(rs), clamp01(gs), clamp01(bs)]
    files.write_json_file("cfg.json", cfg)


def persist_pixel_scale_all(rs: float, gs: float, bs: float):
    """Apply to all allowed light pixels and persist."""
    cfg.setdefault("pixel_scale", {})
    for i in only_lights:
        cfg["pixel_scale"][str(i)] = [clamp01(rs), clamp01(gs), clamp01(bs)]
    files.write_json_file("cfg.json", cfg)


def apply_brightness(i: int, rgb, br: float):
    """Scale rgb by global brightness AND per-pixel (r,g,b) scaler. Accepts tuple or packed int."""
    br = clamp01(br)

    if isinstance(rgb, int):
        rgb = ((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF)

    r, g, b = rgb

    try:
        rs, gs, bs = pixel_scale[i]
    except Exception:
        rs, gs, bs = (1.0, 1.0, 1.0)

    r = int(r * br * rs)
    g = int(g * br * gs)
    b = int(b * br * bs)

    r = 0 if r < 0 else (255 if r > 255 else r)
    g = 0 if g < 0 else (255 if g > 255 else g)
    b = 0 if b < 0 else (255 if b > 255 else b)
    return (r, g, b)


def set_pixel_scale(i: int, rs: float = 1.0, gs: float = 1.0, bs: float = 1.0) -> None:
    """Per-pixel per-channel scaler; each channel is clamped to 0..1 (no boosting)."""
    global pixel_scale
    if i < 0:
        return
    if i >= len(pixel_scale):
        pixel_scale.extend([(1.0, 1.0, 1.0)] * (i - len(pixel_scale) + 1))
    pixel_scale[i] = (clamp01(rs), clamp01(gs), clamp01(bs))


def is_allowed_led(i: int) -> bool:
    return i in only_lights_set


def safe_set_led(i: int, rgb: tuple[int, int, int], store_logical: bool = True) -> bool:
    """
    Set an neo_branch ONLY if allowed. Applies pixel_scale + neo_brightness automatically.
    rgb is 'logical' (pre-scale, pre-brightness).
    """
    if not is_allowed_led(i):
        return False

    if store_logical:
        logical_led[i] = rgb  # store unscaled/unbrightened

    neo_branch[i] = apply_brightness(i, rgb, neo_brightness)
    return True


def refresh_allowed_leds():
    """Re-apply current pixel_scale and neo_brightness to all allowed pixels using logical_led."""
    for i in only_lights:
        if i in logical_led:
            neo_branch[i] = apply_brightness(i, logical_led[i], neo_brightness)
    neo_branch.show()


def is_neo(number, nested_array):
    return any(number in sublist for sublist in nested_array)


def set_neo_to(light_n, r, g, b):
    if light_n == -1:
        for i in range(n_px):
            if not is_allowed_led(i):
                continue

            if is_neo(i, neos):
                safe_set_led(i, (g, r, b))
            else:
                safe_set_led(i, (r, g, b))
    else:
        if not is_allowed_led(light_n):
            return

        if is_neo(light_n, neos):
            safe_set_led(light_n, (g, r, b))
        else:
            safe_set_led(light_n, (r, g, b))

    neo_branch.show()


def get_neo_ids():
    matches = []
    for num in range(n_px + 1):
        if any(num == sublist[0] for sublist in neos):
            matches.append(num)
    return matches


def set_neo_module_to(mod_n, ind, v):
    neo_ids = get_neo_ids()
    print(mod_n, ind, v, neo_ids)

    def set_pair(base):
        safe_set_led(base, (v, v, v))
        safe_set_led(base + 1, (v, v, v))

    if mod_n == 0:
        for base in neo_ids:
            set_pair(base)

    elif ind == 0:
        set_pair(neo_ids[mod_n - 1])

    elif ind < 4:
        base = neo_ids[mod_n - 1]

        ind -= 1
        if ind == 0:
            ind = 1
        elif ind == 1:
            ind = 0

        if is_allowed_led(base):
            cur = list(logical_led.get(base, (0, 0, 0)))
            cur[ind] = v
            safe_set_led(base, tuple(cur))

    else:
        base = neo_ids[mod_n - 1] + 1

        ind -= 1
        if ind == 3:
            ind = 4
        elif ind == 4:
            ind = 3

        if is_allowed_led(base):
            cur = list(logical_led.get(base, (0, 0, 0)))
            cur[ind - 3] = v
            safe_set_led(base, tuple(cur))

    neo_branch.show()


def get_neo_relay_ids():
    matches = []
    for num in range(n_px + 1):
        if any(num == sublist[0] for sublist in neorelays):
            matches.append(num)
    return matches


def get_neo_pico_ids():
    matches = []
    for num in range(n_px + 1):
        if any(num == sublist[0] for sublist in neopicos):
            matches.append(num)
    return matches


def set_neo_relay_to(mod_n, ind, off_on):
    cur = []
    neo_relay_ids = get_neo_relay_ids()
    print(mod_n, ind, off_on, neo_relay_ids)
    if off_on == 0:
        off_on = 0
    else:
        off_on = 255
    if mod_n == 0:
        for i in neo_relay_ids:
            neo_branch[i] = (off_on, off_on, off_on)
    elif ind == 0:
        neo_branch[neo_relay_ids[mod_n-1]] = (off_on, off_on, off_on)
    elif ind < 4:
        ind -= 1
        if ind == 0:
            ind = 1
        elif ind == 1:
            ind = 0
        cur = list(neo_branch[neo_relay_ids[mod_n-1]])
        cur[ind] = off_on
        neo_branch[neo_relay_ids[mod_n-1]] = (cur[0], cur[1], cur[2])
        print(neo_branch[neo_relay_ids[mod_n-1]])
    neo_branch.show()


def set_neo_pico_to(mod_n, char):
    neo_relay_ids = get_neo_pico_ids()
    r, g, b = char_to_pwm_rgb(char)
    # print("r: ", r, "g: ", g, "b: ", b)
    if mod_n == 0:
        for i in neo_relay_ids:
            neo_branch[i] = (r, g, b)
    else:
        neo_branch[neo_relay_ids[mod_n-1]] = (r, g, b)
    neo_branch.show()


gc_col("Neopixels setup")


################################################################################
# PWM RGB (base-5) encoder and decoder

# Digits returned by decoder:
#   0     = closest to 0/255
#   1     = closest to 20/255
#   2     = closest to 40/255
#   3     = closest to 60/255
#   4     = closest to 80/255

ALPHABET = "?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,_/.+-*!@#$%^ <>[]"

# Encoding

DIGIT_PWM = [0, 20, 40, 60, 80]  # base-5 bins


def char_to_base5_digits(ch: str) -> tuple[int, int, int]:
    idx = ALPHABET.find(ch)
    if idx < 0:
        raise ValueError(f"Character {ch!r} not in alphabet")

    r = idx // 25
    g = (idx % 25) // 5
    b = idx % 5
    return r, g, b


def char_to_pwm_rgb(ch: str) -> tuple[int, int, int]:
    """
    One-step: character -> (R, G, B) PWM values (0..255)
    """
    r_d, g_d, b_d = char_to_base5_digits(ch)
    return (
        DIGIT_PWM[r_d],
        DIGIT_PWM[g_d],
        DIGIT_PWM[b_d],
    )

# Decoding


PINS = {"R": red_pin, "G": green_pin, "B": blue_pin}

IDLE_STATE = False
MAXLEN = 1200

# Centers for the five valid levels
CENTERS = [0/255, 20/255, 40/255, 60/255, 80/255]
TOLERANCE = 8/255

CAPTURE_S = 0.002
WIN = 5
MIN_MAJ = 5
CONFIRM_COUNT = 3
ALPHA = 0.20


def _enable_pullup(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    d.deinit()


def _duty_raw_from_pulsein(pulses: pulseio.PulseIn):
    try:
        n = len(pulses)

        data = [pulses[i] for i in range(n)]
        if len(data) % 2:
            data = data[1:]

        even_sum = 0
        odd_sum = 0
        total_sum = 0
        for i in range(0, len(data), 2):
            a = data[i]
            b = data[i + 1]
            even_sum += a
            odd_sum += b
            total_sum += (a + b)

        if total_sum == 0:
            return 0

        duty_even = even_sum / total_sum
        duty_odd = odd_sum / total_sum
        return duty_even if duty_even <= duty_odd else duty_odd
    except Exception as e:
        print(f"Error: {e}")


def _duty_to_digit(d):
    """
    Returns:
      0 = closest to 0/255
      1 = closest to 20/255
      2 = closest to 40/255
      3 = closest to 60/255
      4 = closest to 80/255
    """

    min_dist = float('inf')
    best = 0  # default to invalid

    for i, center in enumerate(CENTERS):
        dist = abs(d - center)
        if dist < min_dist:
            min_dist = dist
            best = i

    if min_dist <= TOLERANCE:
        return best
    else:
        return 0


def _rgb_digits_to_char(r, g, b):
    idx = r * 25 + g * 5 + b
    if idx >= len(ALPHABET):
        return None
    return ALPHABET[idx]


def _majority_tuple(buf):
    counts = {}
    for t in buf:
        counts[t] = counts.get(t, 0) + 1
    best_t = None
    best_n = 0
    for t, n in counts.items():
        if n > best_n:
            best_t, best_n = t, n
    return best_t, best_n


comm_latest = {"char": None, "digits": None, "votes": 0, "lat_ms": 0}
comm_new_char_event = asyncio.Event()


async def decoder_task():

    for pin in PINS.values():
        _enable_pullup(pin)

    pulseins = {}
    for k, pin in PINS.items():
        pi = pulseio.PulseIn(pin, maxlen=MAXLEN, idle_state=IDLE_STATE)
        pi.pause()
        pulseins[k] = pi

    filt = {"R": None, "G": None, "B": None}
    hist = []
    last_char = None

    candidate = None
    candidate_n = 0
    candidate_start_t = None

    is_building_string = False
    built_string = ""

    while True:
        # parallel capture
        for ch in ("R", "G", "B"):
            pulseins[ch].clear()
            pulseins[ch].resume()

        await asyncio.sleep(CAPTURE_S)

        for ch in ("R", "G", "B"):
            pulseins[ch].pause()

        digits = {}

        for ch in ("R", "G", "B"):
            d = _duty_raw_from_pulsein(pulseins[ch])

            if filt[ch] is None:
                filt[ch] = d
            else:
                filt[ch] = ALPHA * d + (1.0 - ALPHA) * filt[ch]

            digits[ch] = _duty_to_digit(filt[ch])

        t = (digits["R"], digits["G"], digits["B"])

        hist.append(t)
        if len(hist) > WIN:
            hist.pop(0)

        best_t, best_n = _majority_tuple(hist)

        if best_n < MIN_MAJ:
            await asyncio.sleep(0)
            continue

        ch_out = _rgb_digits_to_char(*best_t)

        if ch_out is None:
            candidate = None
            candidate_n = 0
            candidate_start_t = None
            await asyncio.sleep(0)
            continue

        if best_t != candidate:
            candidate = best_t
            candidate_n = 1
            candidate_start_t = time.monotonic()
        else:
            candidate_n += 1

        if candidate_n < CONFIRM_COUNT:
            await asyncio.sleep(0)
            continue

        if ch_out != last_char:
            if ch_out == "?":
                print("Optocoupler is off")
            elif ch_out == "[":
                built_string = ""
                is_building_string = True
            elif ch_out == "]":
                now = time.monotonic()
                lat_ms = int((now - candidate_start_t) *
                             1000) if candidate_start_t is not None else 0
                comm_latest["char"] = built_string
                comm_latest["digits"] = best_t
                comm_latest["votes"] = best_n
                comm_latest["lat_ms"] = lat_ms
                comm_new_char_event.set()
                is_building_string = False
            elif is_building_string:
                built_string = built_string + ch_out
            else:
                now = time.monotonic()
                lat_ms = int((now - candidate_start_t) *
                             1000) if candidate_start_t is not None else 0
                comm_latest["char"] = ch_out
                comm_latest["digits"] = best_t
                comm_latest["votes"] = best_n
                comm_latest["lat_ms"] = lat_ms
                comm_new_char_event.set()
            last_char = ch_out
            candidate_start_t = None

        await asyncio.sleep(0)

################################################################################
# Setup wifi and web server


def measure_signal_strength(MY_SSID, cycles):
    print("Monitoring signal for:", MY_SSID)
    print("Showing current RSSI + running average (simple sum + count)\n")

    total_sum = 0.0      # running sum of all valid RSSI values
    count = 0            # number of valid readings so far

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
                # Update running total
                total_sum += current_rssi
                count += 1

                # Calculate and show average
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

        time.sleep(0.1)  # your fast polling; increase to 1–5 if needed
        if count > cycles:
            return avg_rssi


if web:
    import socketpool
    import mdns
    gc_col("config wifi imports")
    import wifi
    gc_col("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST
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
        print("Using env ssid and password")
    except Exception as e:
        files.log_item(e)
        print("Using default ssid and password")

    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        gc_col("wifi connect")

        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(service_type="_http", protocol="_tcp", port=80)

        local_ip = str(wifi.radio.ipv4_address)
        files.log_item("IP is" + local_ip)
        files.log_item("Connected")

        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)

        gc_col("wifi server")

        ################################################################################
        # Setup routes

        @server.route("/")
        def base(request: Request):
            gc_col("Home page.")
            return FileResponse(request, "index.html", "/")

        @server.route("/mui.min.css")
        def mui_css(request: Request):
            return FileResponse(request, "mui.min.css", "/")

        @server.route("/mui.min.js")
        def mui_js(request: Request):
            return FileResponse(request, "mui.min.js", "/")

        @server.route("/animation", [POST])
        def animation_btn(request: Request):
            global cfg
            rq_d = request.json()
            cfg["option_selected"] = rq_d["an"]
            add_command("AN_" + cfg["option_selected"])
            files.write_json_file("cfg.json", cfg)
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/defaults", [POST])
        def defaults_btn(request: Request):
            global cfg
            rq_d = request.json()
            if rq_d["an"] == "reset_animation_timing_to_defaults":
                for ts_fn in ts_jsons:
                    ts = files.read_json_file("t_s_def/" + ts_fn + ".json")
                    files.write_json_file("animations/" + ts_fn + ".json", ts)
            elif rq_d["an"] == "reset_to_defaults":
                rst_def()
                files.write_json_file("cfg.json", cfg)
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/stop", [POST])
        def stop_btn(request: Request):
            stop_all_commands()
            return Response(request, "Stopped all commands")

        @server.route("/lights", [POST])
        def lights_btn(request: Request):
            global exit_set_hdw
            exit_set_hdw = False
            try:
                rq_d = request.json()
                asyncio.create_task(set_hdw_async(rq_d["an"], 0))
                return Response(request, "Utility: set lights successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error setting lights.")

        @server.route("/create-animation", [POST])
        def create_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                f_n = animators_folder + rq_d["fn"] + ".json"
                an_data = [
                    "0.0|BN100,LN0_255_0_0",
                    "1.0|BN100,LN0_0_255_0",
                    "2.0|BN100,LN0_0_0_255",
                    "3.0|BN100,LN0_255_255_255"
                ]
                files.write_json_file(f_n, an_data)
                upd_media()
                return Response(request, "Created animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error creating animation.")

        @server.route("/rename-animation", [POST])
        def rename_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                fo = animators_folder + rq_d["fo"] + ".json"
                fn = animators_folder + rq_d["fn"] + ".json"
                os.rename(fo, fn)
                upd_media()
                return Response(request, "Renamed animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error renaming animation.")

        @server.route("/delete-animation", [POST])
        def delete_animation(request: Request):
            try:
                global animators_folder
                rq_d = request.json()
                f_n = animators_folder + rq_d["fn"] + ".json"
                os.remove(f_n)
                upd_media()
                return Response(request, "Delete animation successfully.")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error deleting animation.")

        @server.route("/update-light-string", [POST])
        def update_light_string(req: Request):
            global cfg
            rq_d = req.json()
            if rq_d["action"] in ("save", "clear", "defaults"):
                cfg["light_string"] = rq_d["text"]
                files.write_json_file("cfg.json", cfg)
                upd_l_str()
                return Response(req, cfg["light_string"])

            if cfg["light_string"] == "":
                cfg["light_string"] = rq_d["text"]
            else:
                cfg["light_string"] = cfg["light_string"] + "," + rq_d["text"]

            files.write_json_file("cfg.json", cfg)
            upd_l_str()
            return Response(req, cfg["light_string"])

        @server.route("/get-light-string", [POST])
        def get_light_string(req: Request):
            return Response(req, cfg["light_string"])

        @server.route("/update-host-name", [POST])
        def update_host_name(request: Request):
            global cfg
            rq_d = request.json()
            cfg["HOST_NAME"] = rq_d["an"]
            files.write_json_file("cfg.json", cfg)
            mdns.hostname = cfg["HOST_NAME"]
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def get_host_name(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-local-ip", [POST])
        def get_local_ip(request: Request):
            return Response(request, local_ip)

        @server.route("/get-wifi-signal", [POST])
        def get_local_ip(request: Request):
            avg_rssi = measure_signal_strength(WIFI_SSID, 10)
            return Response(request, str(avg_rssi))

        @server.route("/get-animations", [POST])
        def get_animations(request: Request):
            sounds = []
            sounds.extend(animations)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/test-animation", [POST])
        def test_animation(request: Request):
            global exit_set_hdw
            exit_set_hdw = False
            try:
                rq_d = request.json()
                asyncio.create_task(set_hdw_async(rq_d["an"], 3))
                return Response(request, "Test animation successfully")
            except Exception as e:
                files.log_item(e)
                return Response(request, "Error test animation.")

        @server.route("/get-animation", [POST])
        def get_animation(request: Request):
            rq_d = request.json()
            snd_f = rq_d["an"]
            if f_exists("animations/" + snd_f + ".json"):
                f_n = "animations/" + snd_f + ".json"
                return FileResponse(request, f_n, "/")
            else:
                f_n = "t_s_def/timestamp mode.json"
                return FileResponse(request, f_n, "/")

        data = []

        @server.route("/save-data", [POST])
        def save_data(request: Request):
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

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")


cycles = 10
avg_rssi = measure_signal_strength(WIFI_SSID, cycles)
print(f"Avg ({cycles} readings): {avg_rssi:.1f} dBm")


################################################################################
# Command queue
command_queue = []


def add_command(command, to_start=False):
    global exit_set_hdw
    exit_set_hdw = False
    if to_start:
        command_queue.insert(0, command)
        print("Command added to the start:", command)
    else:
        command_queue.append(command)
        print("Command added to the end:", command)


async def process_commands():
    while command_queue:
        cmd = command_queue.pop(0)
        print("Processing command:", cmd)
        if cmd[:2] == 'AN':  # AN_XXX = Animation XXX filename
            cmd_split = cmd.split("_")
            clr_cmd_queue()
            await an_async(cmd_split[1])
        else:
            await set_hdw_async(cmd)
        await asyncio.sleep(0)


def clr_cmd_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_commands():
    global exit_set_hdw
    clr_cmd_queue()
    exit_set_hdw = True
    print("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"


################################################################################
# animations

async def an_async(f_nm):
    print("Filename:", f_nm)
    try:
        await an_light_async(f_nm)
        gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    flsh_t = []
    if f_exists("animations/" + f_nm + ".json"):
        flsh_t = files.read_json_file("animations/" + f_nm + ".json")
    else:
        # If it's not an animation file, treat it as a direct hardware command string
        # so queued decoder commands like "LN1_..." work immediately.
        result = await set_hdw_async(f_nm, 0)
        await asyncio.sleep(0)
        return result

    ft_last = flsh_t[len(flsh_t) - 1].split("|")
    tm_last = float(ft_last[0]) + .1
    flsh_t.append(str(tm_last) + "|E")
    flsh_t.append(str(tm_last + .1) + "|E")

    flsh_i = 0
    srt_t = time.monotonic()

    while True:
        t_past = time.monotonic() - srt_t
        if flsh_i < len(flsh_t) - 1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i + 1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0

        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t) - 1:
            files.log_item(f"time elapsed: {t_past} Timestamp: {ft1[0]}")
            if len(ft1) == 1 or ft1[1] == "":
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                result = await set_hdw_async(f"L0{lgt},S0{pos}", dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)
                    break
            flsh_i += 1

        await asyncio.sleep(0)

        if flsh_i >= len(flsh_t) - 1:
            break

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
    global exit_set_hdw
    st = time.monotonic()

    pxs = only_lights
    n = len(pxs)
    if n == 0:
        return

    while (time.monotonic() - st) < dur:
        for j in range(0, 255):
            if exit_set_hdw:
                return

            for k, i in enumerate(pxs):
                pixel_index = (k * 256 // n) + j
                safe_set_led(i, colorwheel(pixel_index & 255), store_logical=False)

            neo_branch.show()
            await asyncio.sleep(spd)

            if (time.monotonic() - st) > dur:
                return

        for j in range(254, -1, -1):
            if exit_set_hdw:
                return

            for k, i in enumerate(pxs):
                pixel_index = (k * 256 // n) + j
                safe_set_led(i, colorwheel(pixel_index & 255), store_logical=False)

            neo_branch.show()
            await asyncio.sleep(spd)

            if (time.monotonic() - st) > dur:
                return


async def fire(dur):
    global exit_set_hdw
    st = time.monotonic()

    firei = []
    firei.extend(ornmnts)
    firei.extend(cane_s)
    firei.extend(cane_e)

    # overlays: guard them
    for i in stars:
        if i in only_lights_set:
            safe_set_led(i, (255, 255, 255), store_logical=False)

    for i in brnchs:
        if i in only_lights_set:
            safe_set_led(i, (50, 50, 50), store_logical=False)

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Flicker
    while True:
        for i in firei:
            if exit_set_hdw:
                return
            if i not in only_lights_set:
                continue
            f = random.randint(0, 110)
            r1 = bnd(r - f, 0, 255)
            g1 = bnd(g - f, 0, 255)
            b1 = bnd(b - f, 0, 255)
            safe_set_led(i, (r1, g1, b1), store_logical=False)
            neo_branch.show()
        await asyncio.sleep(random.uniform(0.05, 0.1))
        
        if (time.monotonic() - st) > dur:
            return


def multi_color():
    pxs = only_lights
    if not pxs:
        return

    for i in pxs:
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        c = random.randint(0, 2)

        if c == 0:
            r1, g1, b1 = r, 0, 0
        elif c == 1:
            r1, g1, b1 = 0, g, 0
        else:
            r1, g1, b1 = 0, 0, b

        safe_set_led(i, (r1, g1, b1), store_logical=False)

    for i in stars:
        if i in only_lights_set:
            safe_set_led(i, (255, 255, 255), store_logical=False)
    for i in brnchs:
        if i in only_lights_set:
            safe_set_led(i, (7, 163, 30), store_logical=False)

    for i in cane_e:
        if i in only_lights_set:
            safe_set_led(i, (255, 255, 255), store_logical=False)

    neo_branch.show()


def bnd(c, l, u):
    if c < l:
        c = l
    if c > u:
        c = u
    return c


async def set_hdw_async(input_string, dur=0):
    global br, exit_set_hdw, neo_brightness
    segs = input_string.split(",")

    try:
        for seg in segs:
            if exit_set_hdw:
                return "STOP"
            elif seg[0] == 'E':
                return "STOP"
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
            # UPDLS = update light string    
            elif seg[:5] == 'UPDLS':
                upd_l_str()
                led_indicator.fill((20, 0, 0))
                led_indicator.show()
                time.sleep(.3)
                led_indicator.fill((0, 20, 0))
                led_indicator.show()
                time.sleep(.3)
                led_indicator.fill((0, 0, 20))
                led_indicator.show()
                time.sleep(.3)
                led_indicator.fill((0, 0, 0))
                led_indicator.show()
                time.sleep(.3)
            # lights LI_R_G_B = Nep pico indicator RGB 0 to 255
            elif seg[:2] == 'LI':
                segs_split = seg.split("_")
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                led_indicator.fill((r, g, b))
                led_indicator.show()
            # lights LNZZZ_R_G_B = Neopixel lights/Neo 6 modules ZZZ (0 All, 1 to 999) RGB 0 to 255
            elif seg[:2] == 'LN':
                segs_split = seg.split("_")
                light_n = int(segs_split[0][2:])-1
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                set_neo_to(light_n, r, g, b)
            # modules NMZZZ_I_XXX = Neo 6 modules only ZZZ (0 All, 1 to 999) I index (0 All, 1 to 6) XXX 0 to 255</div>
            elif seg[:2] == 'NM':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0][2:])
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_module_to(mod_n, index, v)
            # brightness BXXX = Brightness XXX 000 to 100
            elif seg[0:2] == 'BN':
                br = int(seg[2:])
                neo_brightness = clamp01(br / 100.0)
                refresh_allowed_leds()
            # fade in or out FXXX_TTT = Fade brightness in or out XXX 0 to 100, TTT time between transitions in decimal seconds
            elif seg[0] == 'F':
                segs_split = seg.split("_")
                target = int(segs_split[0][1:])
                step_s = float(segs_split[1])

                target = max(0, min(100, target))

                while br != target:
                    if exit_set_hdw:
                        return "STOP"
                    br += 1 if br < target else -1
                    neo_brightness = clamp01(br / 100.0)
                    refresh_allowed_leds()
                    await asyncio.sleep(step_s)
            # SCNZZZ_RS_GS_BS = per-pixel per-color scaler (0.0..1.0) ZZZ = 0 (all allowed light pixels) or 1-based pixel index
            elif seg[:3] =='SCN':
                parts = seg.split('_')
                px_n = int(parts[0][3:])   # after 'SCN'
                rs = clamp01(float(parts[1]))
                gs = clamp01(float(parts[2]))
                bs = clamp01(float(parts[3]))

                if px_n == 0:
                    for i in only_lights:
                        pixel_scale[i] = (rs, gs, bs)
                    persist_pixel_scale_all(rs, gs, bs)
                else:
                    i = px_n - 1
                    if i in only_lights_set:
                        pixel_scale[i] = (rs, gs, bs)
                        persist_pixel_scale(i, rs, gs, bs)

                refresh_allowed_leds()
            # SCCZZZ = Scale Clear Calibration. ZZZ=0 clears all, else clears pixel (1-based)
            elif seg[:3] == 'SCC':
                try:
                    n = int(seg[3:])  # SCC0, SCC12, etc.
                except Exception:
                    n = -1

                if n == 0:
                    clear_pixel_scale_all()
                elif n > 0:
                    clear_pixel_scale_one(n - 1)  # convert to 0-based

            # modules NRZZZ_I_XXX = Neo relay modules only ZZZ (0 All, 1 to 999) I index (0 All, 1 to 3) XXX 0 off 1 on
            elif seg[:2] == 'NR':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0].replace("NR", ""))
                index = int(segs_split[1])
                v = int(segs_split[2])
                set_neo_relay_to(mod_n, index, v)
            # modules NPZZZ_XXX = Neo pico modules only ZZZ (0 All, 1 to 999) XXX command abcdefghijklmnopqrstuvwxyz0123456789,_/.+-*!@#$%^)
            elif seg[:2] == 'NP':
                segs_split = seg.split("_")
                mod_n = int(segs_split[0].replace("NP", ""))
                char = segs_split[1]
                set_neo_pico_to(mod_n, char)
            elif seg[0:] == 'ZRAND':
                await random_effect(1, 3, dur)
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                await rbow(v, dur)
            elif seg[0:] == 'ZFIRE':
                await fire(dur)
            elif seg[0:] == 'ZCOLCH':
                multi_color()
                await asyncio.sleep(dur)
            elif seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)
            # SNXXX = Servo N (0 All, 1-6) XXX 0 to 180
            elif seg[0] == 'S':
                num = int(seg[1])
                v = int(seg[2:])
                if num == 0:
                    for i in range(len(s_arr)):
                        s_arr[i].angle = v
                else:
                    s_arr[num-1].angle = int(v)
            # WXXX = Wait XXX decimal seconds
            elif seg[0] == 'W':  # wait time
                s = float(seg[1:])
                await asyncio.sleep(s)
            # modules NPZZZ_XXX = Neo pico modules only ZZZ (0 All, 1 to 999) XXX command using these characters ?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,_/.+-*!@#$%^ <>[]
            elif seg[:2] == 'PN':
                start_time = time.monotonic()
                my_wait = 0.1
                segs_split = seg.split("_")
                mod_n = int(segs_split[0].replace("PN", ""))

                if len(segs_split[1])==1:
                    set_neo_pico_to(mod_n, segs_split[1])
                    await asyncio.sleep(my_wait) 
                else:
                    set_neo_pico_to(mod_n, "?")
                    await asyncio.sleep(my_wait)

                    set_neo_pico_to(mod_n, "[")
                    await asyncio.sleep(my_wait)

                    prev = None
                    is_first = True

                    for v in segs_split[1]:
                        if v == prev and not is_first:
                            set_neo_pico_to(mod_n, "?")
                            await asyncio.sleep(my_wait)

                        is_first = False

                        set_neo_pico_to(mod_n, v)
                        await asyncio.sleep(my_wait)

                        prev = v

                    set_neo_pico_to(mod_n, "[")
                    await asyncio.sleep(my_wait)

                    end_time = time.monotonic()
                    print("Time it took: ", end_time-start_time)
            elif seg[0:2] == 'NS':
                start_time = time.monotonic()
                my_wait = 0.1

                r, g, b = char_to_pwm_rgb("?")
                set_neo_to(0, r, g, b)
                await asyncio.sleep(my_wait)

                r, g, b = char_to_pwm_rgb("[")
                set_neo_to(0, r, g, b)
                await asyncio.sleep(my_wait)

                prev = None
                is_first = True

                for v in seg[2:]:
                    is_first
                    if v == prev and not is_first:
                        r, g, b = char_to_pwm_rgb("?")
                        set_neo_to(0, r, g, b)
                        await asyncio.sleep(my_wait)

                    is_first = False

                    r, g, b = char_to_pwm_rgb(v)
                    set_neo_to(0, r, g, b)
                    await asyncio.sleep(my_wait)

                    prev = v

                r, g, b = char_to_pwm_rgb("]")
                set_neo_to(0, r, g, b)
                await asyncio.sleep(my_wait)
                end_time = time.monotonic()

                print("Time it took: ", end_time-start_time)
    except Exception as e:
        files.log_item(e)
    

################################################################################
# Decoder consumer: map a/b/c -> hardware command string, then enqueue
# Map decoded characters to *hardware command strings* (enqueued)
# Change these to whatever you want.
CHAR_TO_HDW = {
    "^": "UPDLS"
}


async def consumer_task():
    while True:
        await comm_new_char_event.wait()
        comm_new_char_event.clear()

        ch = comm_latest["char"]
        if ch is None:
            await asyncio.sleep(0)
            continue

        print("CHAR:", ch,
              "| digits:", comm_latest["digits"],
              "| votes:", comm_latest["votes"],
              "| latency_ms:", comm_latest["lat_ms"])

        if ch in CHAR_TO_HDW:
            add_command(CHAR_TO_HDW[ch])
            print("Enqueued mapped HW:", CHAR_TO_HDW[ch])
        else:
            add_command(ch)

        await asyncio.sleep(0)


################################################################################
# Start server

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address), port=80)
        led_indicator[0] = (0, 20, 0)
        led_indicator.show()
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except Exception as e:
        files.log_item(e)
        time.sleep(5)
        files.log_item("restarting...")
        rst()
else:
    led_indicator[0] = (20, 0, 0)
    led_indicator.show()
    time.sleep(3)

files.log_item("animator has started...")
gc_col("animations started.")

################################################################################
# Main task handling


async def process_commands_task():
    while True:
        try:
            await process_commands()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)


async def server_poll_task(server):
    while True:
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)


async def garbage_collection_task():
    while True:
        gc.collect()
        await asyncio.sleep(10)


async def main():
    tasks = [
        process_commands_task(),
        garbage_collection_task(),
        decoder_task(),
        consumer_task(),
    ]

    if web:
        tasks.append(server_poll_task(server))

    await asyncio.gather(*tasks)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
