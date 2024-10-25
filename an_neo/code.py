from adafruit_debouncer import Debouncer
from rainbowio import colorwheel
import neopixel
import microcontroller
import rtc
import random
import board
import digitalio
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

# Setup the switches
l_sw = digitalio.DigitalInOut(board.GP6)
l_sw.direction = digitalio.Direction.INPUT
l_sw.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw)

r_sw = digitalio.DigitalInOut(board.GP7)
r_sw.direction = digitalio.Direction.INPUT
r_sw.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw)

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# config variables

cfg = files.read_json_file("cfg.json")

################################################################################
# Setup neo pixels

num_px = 6

# 10 on an_neo
led = neopixel.NeoPixel(board.GP10, num_px)

gc_col("Neopixels setup")

led.fill((255, 255, 255))
led.show()
################################################################################
# animations

br = 100


def set_hdw(cmd):
    global sp, br
    # Split the input string into segments
    segs = cmd.split(",")

    # Process each segment
    try:
        for seg in segs:
            if seg[0] == 'L':  # lights
                v = int(seg[1])*100+int(seg[2])*10+int(seg[3])
                if seg[1] == "-1":
                    led.fill((v, v, v))
                else:
                    led[int(seg[1])] = (cur[0], cur[1], cur[2])
                led.show()
            if seg[0] == 'B':  # brightness
                br = int(seg[1:])
                led.brightness = float(br/100)
                led.show()
            if seg[0] == 'F':  # fade in or out
                v = int(seg[1])*100+int(seg[2])*10+int(seg[3])
                s = float(seg[5:])
                while not br == v:
                    if br < v:
                        br += 1
                        led.brightness = float(br/100)
                    else:
                        br -= 1
                        led.brightness = float(br/100)
                    led.show()
                    time.sleep(s)
    except Exception as e:
        files.log_item(e)


def rainbow(spd, dur):
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            for i in range(num_px):
                pixel_index = (i * 256 // num_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st
        for j in reversed(range(0, 255, 1)):
            for i in range(num_px):
                pixel_index = (i * 256 // num_px) + j
                led[i] = colorwheel(pixel_index & 255)
            led.show()
            time.sleep(spd)
            te = time.monotonic()-st


def fire(dur):
    st = time.monotonic()
    led.brightness = 1.0

    fire_array = [0, 1, 2, 3, 4, 5]

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    print(len(fire_array))

    # Flicker, based on our initial RGB values
    while True:
        for i in fire_array:
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


def mlt_c(dur):
    st = time.monotonic()
    led.brightness = 1.0

    # Flicker, based on our initial RGB values
    while True:
        for i in range(0, num_px):
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
        time.sleep(random.uniform(.2, 0.3))
        te = time.monotonic()-st
        if te > dur:
            return


def all_c(dur):
    st = time.monotonic()
    led.brightness = 1.0
    while True:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        led.fill((r, g, b))
        led.show()
        time.sleep(random.uniform(.5, 1.0))
        te = time.monotonic()-st
        if te > dur:
            return


def fade_out_in(dur):
    st = time.monotonic()
    while True:
        set_hdw("F0000.005")
        set_hdw("F1000.005")
        te = time.monotonic()-st
        if te > dur:
            return


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


while True:
    dur = random.randint(3, 7)
    i = random.randint(0, 5)
    if i == 0:
        fade_out_in(dur)
    elif i == 1:
        rainbow(0.001, dur)
    elif i == 2:
        fire(dur)
    elif i == 3:
        mlt_c(dur)
    elif i == 4:
        fade_out_in(dur)
    elif i == 5:
        all_c(dur)
