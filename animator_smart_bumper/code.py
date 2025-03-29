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
import busio
import time
import gc
import files
import os
import adafruit_vl53l4cd


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
# Sd card config variables

animators_folder = "/animations/"

cfg = files.read_json_file("cfg.json")

ts_jsons = files.return_directory(
    "", "t_s_def", ".json")

web = cfg["serve_webpage"]

exit_set_hdw_async = False

gc_col("config setup")


def upd_media():
    global animations

    animations = files.return_directory("", "animations", ".json")


upd_media()

br = 0

################################################################################
# Setup neo pixels

n_px = 1

# 15 on demo 17, GP18 on smart bumper
neo_pixel_pin = board.GP18

led = neopixel.NeoPixel(neo_pixel_pin, n_px)

led.fill((255, 0, 0))
led.show()
time.sleep(.2)

led.fill((0, 255, 0))
led.show()
time.sleep(.2)

led.fill((0, 0, 255))
led.show()
time.sleep(.2)

led.fill((0, 0, 0))
led.show()

gc_col("Neopixels setup")

################################################################################
# setup distance sensor

i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=400000)

vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200

print("VL53L4CD Simple Test.")
print("--------------------")
model_id, module_type = vl53.model_info
print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

vl53.start_ranging()

while not vl53.data_ready:
    print("data not ready")
    time.sleep(.2)


################################################################################
# Setup wifi and web server

if (web):
    import socketpool
    import mdns
    gc_col("config wifi imports")
    import wifi
    gc_col("config wifi imports")
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST, JSONResponse
    gc_col("config wifi imports")
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
        print("Using env ssid and password")
    except Exception as e:
        files.log_item(e)
        print("Using default ssid and password")

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
                add_command(cfg["option_selected"])
                files.write_json_file("cfg.json", cfg)
                return Response(request, "Animation " + cfg["option_selected"] + " started.")

            @server.route("/defaults", [POST])
            def btn(request: Request):
                global cfg
                rq_d = request.json()
                if rq_d["an"] == "reset_animation_timing_to_defaults":
                    for ts_fn in ts_jsons:
                        ts = files.read_json_file(
                            "t_s_def/" + ts_fn + ".json")
                        files.write_json_file(
                            "animations/"+ts_fn+".json", ts)
                elif rq_d["an"] == "reset_to_defaults":
                    rst_def()
                    files.write_json_file("cfg.json", cfg)
                return Response(request, "Utility: " + rq_d["an"])

            @server.route("/stop", [POST])
            def btn(request: Request):
                stop_all_commands()
                return Response(request, "Stopped all commands")

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
                    print(rq_d)
                    f_n = animators_folder + rq_d["fn"] + ".json"
                    print(f_n)
                    an_data = ["0.0|BN100,LN0_255_0_0", "1.0|BN100,LN0_0_255_0",
                               "2.0|BN100,LN0_0_0_255", "3.0|BN100,LN0_255_255_255"]
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
                    print(rq_d)
                    f_n = animators_folder + rq_d["fn"] + ".json"
                    print(f_n)
                    os.remove(f_n)
                    upd_media()
                    return Response(request, "Delete animation successfully.")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error setting lights.")

            @server.route("/get-light-string", [POST])
            def btn(req: Request):
                return Response(req, cfg["light_string"])

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
                    rq_d = request.json()
                    print(rq_d["an"])
                    gc_col("Save Data.")
                    # Schedule the async task
                    asyncio.create_task(set_hdw_async(rq_d["an"], 3))
                    return Response(request, "Test animation successfully")
                except Exception as e:
                    files.log_item(e)  # Log any errors
                    return Response(request, "Error test animation.")

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
            files.log_item(e)
            time.sleep(2)

def send_get_request(url):
    try:
        files.log_item("Sending GET request to " + url)
        response = requests.get(url)
        files.log_item("GET Response: " + response.text)
        response.close()
    except Exception as e:
        files.log_item("GET request failed: " + str(e))

def send_post_request(url, data):
    try:
        files.log_item("Sending POST request to " + url)
        response = requests.post(url, json=data)
        files.log_item("POST Response: " + response.text)
        response.close()
    except Exception as e:
        files.log_item("POST request failed: " + str(e))

gc_col("web server")

# Test GET request
files.log_item("Sending GET request to internet")
response = requests.get("http://httpbin.org/get")
files.log_item("GET Response: " + response.text)
response.close()

# Test POST request
try:
    data = {"test": "value"}  # Simple dictionary
    files.log_item("Sending POST request to http://httpbin.org/post")
    response = requests.post("http://httpbin.org/post", json=data)
    files.log_item("POST Response: " + response.text)
    response.close()
except Exception as e:
    files.log_item("POST request failed: " + str(e))
################################################################################
# Command queue
command_queue = []


def add_command(command, to_start=False):
    global exit_set_hdw_async
    exit_set_hdw_async = False
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        print("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        print("Command added to the end:", command)


async def process_commands():
    while command_queue:
        command = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", command)
        await an_async(command)  # Process each command as an async operation
        await asyncio.sleep(0)  # Yield control to the event loop


def clear_command_queue():
    command_queue.clear()
    print("Command queue cleared.")


def stop_all_commands():
    global exit_set_hdw_async
    clear_command_queue()
    exit_set_hdw_async = True
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

    # add end command to time stamps to stop video when timestamps run out
    ft_last = flsh_t[len(flsh_t)-1].split("|")
    tm_last = float(ft_last[0]) + .1
    flsh_t.append(str(tm_last) + "|E")
    flsh_t.append(str(tm_last + .1) + "|E")

    flsh_i = 0
    srt_t = time.monotonic()

    while True:
        t_past = time.monotonic() - srt_t
        if flsh_i < len(flsh_t)-1:
            ft1 = flsh_t[flsh_i].split("|")
            ft2 = flsh_t[flsh_i + 1].split("|")
            dur = float(ft2[0]) - float(ft1[0]) - 0.25
        else:
            dur = 0.25
        if dur < 0:
            dur = 0

        if t_past > float(ft1[0]) - 0.25 and flsh_i < len(flsh_t)-1:
            files.log_item(f"time elapsed: {t_past} Timestamp: {ft1[0]}")
            if len(ft1) == 1 or ft1[1] == "":
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                result = await set_hdw_async(f"L0{lgt},S0{pos}", dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            else:
                result = await set_hdw_async(ft1[1], dur)
                if result == "STOP":
                    await asyncio.sleep(0)  # Yield control to other tasks
                    break
            flsh_i += 1

        # print (flsh_i)

        await asyncio.sleep(0)  # Yield control to other tasks

        # Exit condition for stopping animation
        if flsh_i >= len(flsh_t)-1:
            # led.fill((0, 0, 0))
            # led.show()
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
    global exit_set_hdw_async
    st = time.monotonic()
    te = time.monotonic()-st
    while te < dur:
        for j in range(0, 255, 1):
            if exit_set_hdw_async:
                return
            pixel_index = (i * 256 // n_px) + j
            led[0] = colorwheel(pixel_index & 255)
            led.show()
            await asyncio.sleep(spd)
            te = time.monotonic()-st
            if te > dur:
                return
        for j in reversed(range(0, 255, 1)):
            if exit_set_hdw_async:
                return
            pixel_index = (i * 256 // n_px) + j
            led[0] = colorwheel(pixel_index & 255)
            led.show()
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
        led[0] = (r1, g1, b1)
        led.show()
        await asyncio.sleep(random.uniform(0.05, 0.1))
        te = time.monotonic()-st
        if te > dur:
            return


def multi_color():
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
    led[0] = (r1, g1, b1)


def bnd(c, l, u):
    if (c < l):
        c = l
    if (c > u):
        c = u
    return c


async def set_hdw_async(input_string, dur):
    global sp, br, exit_set_hdw_async
    segs = input_string.split(",")

    try:
        for seg in segs:
            if exit_set_hdw_async:
                return "STOP"
            if seg[0] == 'E':  # end an
                return "STOP"
            elif seg[:1] == 'L':
                segs_split = seg.split("_")
                r = int(segs_split[0])
                g = int(segs_split[1])
                b = int(segs_split[2])
                led[0] = (r, g, b)
            # brightness BXXX = Brightness XXX 000 to 100
            elif seg[0:1] == 'B':
                br = int(seg[2:])
                led.brightness = float(br/100)
                led.show()
            # fade in or out FXXX_TTT = Fade brightness in or out XXX 0 to 100, TTT time between transitions in decimal seconds
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
                    await asyncio.sleep(s)
            # ZRAND = Random rainbow, fire, or color change
            elif seg[0:] == 'ZRAND':
                await random_effect(1, 3, dur)
            # ZRTTT = Rainbow, TTT cycle speed in decimal seconds
            elif seg[:2] == 'ZR':
                v = float(seg[2:])
                await rbow(v, dur)
            # ZFIRE = Fire
            elif seg[0:] == 'ZFIRE':
                await fire(dur)
            # ZCOLCH = Color change
            elif seg[0:] == 'ZCOLCH':
                multi_color()
                await asyncio.sleep(dur)
            # QXXX/XXX = Add media to queue XXX/XXX (folder/filename)
            if seg[0] == 'Q':
                file_nm = seg[1:]
                add_command(file_nm)
    except Exception as e:
        files.log_item(e)

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        rst()

files.log_item("animator has started...")
gc_col("animations started.")

if web:
    led.fill((0, 255, 0))
    led.show()
else:
    led.fill((255, 0, 0))
    led.show()

# Main task handling


async def process_commands_task():
    """Task to continuously process commands."""
    while True:
        try:
            await process_commands()  # Async command processing
        except Exception as e:
            files.log_item(e)
        await asyncio.sleep(0)  # Yield control to other tasks


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
        gc.collect()  # Collect garbage
        await asyncio.sleep(10)  # Run every 10 seconds (adjust as needed)


async def main():
    # Create asyncio tasks
    tasks = [
        process_commands_task(),
        garbage_collection_task(),
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

