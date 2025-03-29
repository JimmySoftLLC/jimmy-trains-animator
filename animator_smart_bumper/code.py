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
# Sd card config variables and globals

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

mdns_to_ip = {}

################################################################################
# Setup neo pixels

n_px = 1

# 15 on demo 17, GP18 on smart bumper
neo_pixel_pin = board.GP18

led = neopixel.NeoPixel(neo_pixel_pin, n_px)

led.fill((255, 255, 255))
led.show()
time.sleep(1)

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

led.fill((255, 255, 0))
led.show()

while not vl53.data_ready:
    print("data not ready")
    time.sleep(.2)

time.sleep(1)

led.fill((0, 0, 0))
led.show()
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

    led.fill((0, 0, 255))
    led.show()

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

    led.fill((0, 0, 0))
    led.show()

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
            # Assume new_data is a dict; no json.loads needed
            response = requests.post(new_url, json=new_data)
        else:
            response = requests.post(new_url)

        files.log_item("POST Response: " + response.text)
        created_data = response.text
        response.close()
        return created_data
    except Exception as e:
        files.log_item("Comms issue: " + str(e))
        return None


gc_col("web server")

# Test GET request
get_result = send_animator_get("httpbin.org", "get")
if get_result:
    files.log_item("GET test succeeded with result: " + get_result)
else:
    files.log_item("GET test failed")

# Test POST request
data = {"test": "value"}  # Simple dictionary
post_result = send_animator_post("httpbin.org", "post", data)
if post_result:
    files.log_item("POST test succeeded with result: " + post_result)
else:
    files.log_item("POST test failed")
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
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    led[0] = (r, g, b)


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
            # end animation
            if seg[0] == 'E':  
                return "STOP"
            # L_R_G_B = Neopixel light RGB 0 to 255
            elif seg[:1] == 'L':
                segs_split = seg.split("_")
                r = int(segs_split[1])
                g = int(segs_split[2])
                b = int(segs_split[3])
                led[0] = (r, g, b)
            # BXXX = Brightness XXX 000 to 100
            elif seg[0:1] == 'B':
                br = int(seg[1:])
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
                    # await asyncio.sleep(s)
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
            # API_UUU_EEE_DDD = Api POST call UUU base url, EEE endpoint, DDD data object i.e. {"an":data_object}
            if seg[:3] == 'API':
                seg_split = split_string(seg)
                files.log_item("Split segment: " + str(seg_split))
                files.log_item("Four params")
                max_retries = 2
                attempts = 0
                while attempts < max_retries:
                    ip_from_mdns = get_ip_from_mdns(
                        seg_split[1], overwrite=(attempts > 0))
                    files.log_item(
                        f"Attempt {attempts + 1}: Resolved {seg_split[1]} to {ip_from_mdns}")
                    if ip_from_mdns:
                        try:
                            response = send_animator_post(
                                ip_from_mdns, seg_split[2], seg_split[3])
                            if response is not None:
                                return response
                            files.log_item(
                                f"send_animator_post failed with {ip_from_mdns}, retrying...")
                        except Exception as e:
                            files.log_item(
                                f"Error with {ip_from_mdns}: {e}, retrying...")
                    else:
                        files.log_item(
                            f"Failed to resolve {seg_split[1]} to an IP, retrying...")
                    attempts += 1

                if attempts >= max_retries:
                    if seg_split[1] in mdns_to_ip:
                        del mdns_to_ip[seg_split[1]]
                        files.log_item(
                            f"Removed {seg_split[1]} from dictionary after {max_retries} failed attempts")
                    return "host not found after retries"
    except Exception as e:
        files.log_item(e)


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
