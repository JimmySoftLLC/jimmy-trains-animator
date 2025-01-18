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
import asyncio
import gc


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

cfg = files.read_json_file("cfg.json")

animations = files.return_directory("", "animations", ".json")

ts_jsons = files.return_directory(
    "", "t_s_def", ".json")

web = cfg["serve_webpage"]

cont_run = False
ts_mode = False

gc_col("config setup")

################################################################################
# Setup neo pixels

num_px = 2

#15 on demo 17 tiny 10 on large
led = neopixel.NeoPixel(board.GP17, num_px)

gc_col("Neopixels setup")

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

    files.log_item("Connecting to WiFi")

    # default for manufacturing and shows
    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

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
        # connect to your SSID
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        gc_col("wifi connect")

        # setup mdns server
        mdns = mdns.Server(wifi.radio)
        mdns.hostname = cfg["HOST_NAME"]
        mdns.advertise_service(
            service_type="_http", protocol="_tcp", port=80)

        # files.log_items IP address to REPL
        files.log_item("IP is" + str(wifi.radio.ipv4_address))
        files.log_item("Connected")

        # set up server
        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)

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
            global cfg, cont_run, ts_mode
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

        @server.route("/mode", [POST])
        def btn(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            if rq_d["an"] == "cont_mode_on":
                cont_run = True
            elif rq_d["an"] == "cont_mode_off":
                cont_run = False
            elif rq_d["an"] == "timestamp_mode_on":
                ts_mode = True
            elif rq_d["an"] == "timestamp_mode_off":
                ts_mode = False
            return Response(request, "Utility: " + rq_d["an"])

        @server.route("/lights", [POST])
        def btn(request: Request):
            rq_d = request.json()
            set_hdw_async(rq_d["an"])
            return Response(request, "Utility: " + "Utility: set lights")
        
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

        @server.route("/get-built-in-sound-tracks", [POST])
        def btn(request: Request):
            sounds = []
            sounds.extend(animations)
            my_string = files.json_stringify(sounds)
            return Response(request, my_string)

        @server.route("/test-animation", [POST])
        def btn(request: Request):
            rq_d = request.json()
            print(rq_d["an"])
            gc_col("Save Data.")
            set_hdw_async(rq_d["an"])
            return Response(request, "success")

        @server.route("/get-animation", [POST])
        def btn(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            snd_f = rq_d["an"]
            if (f_exists("animations/" + snd_f + ".json") == True):
                f_n = "animations/" + snd_f + ".json"
                return FileResponse(request, f_n, "/")
            else:
                f_n = "t_s_def/timestamp mode.json"
                return FileResponse(request, f_n, "/")

        @server.route("/delete-file", [POST])
        def btn(request: Request):
            rq_d = request.json()
            f_n = ""
            if "customers_owned_music_" in rq_d["an"]:
                snd_f = rq_d["an"].replace("customers_owned_music_", "")
                f_n = "customers_owned_music/" + snd_f + ".json"
            else:
                f_n = "animations/" + rq_d["an"] + ".json"
            os.remove(f_n)
            gc_col("get data")
            return JSONResponse(request, "file deleted")

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

# Command queue
command_queue = []

def add_command(command, to_start=False):
    """Add a command to the queue. If to_start is True, add to the front."""
    if to_start:
        command_queue.insert(0, command)  # Add to the front
        print("Command added to the start:", command)
    else:
        command_queue.append(command)  # Add to the end
        print("Command added to the end:", command)

async def process_commands():
    """Asynchronous function to process commands in a FIFO order."""
    while command_queue:
        command = command_queue.pop(0)  # Retrieve from the front of the queue
        print("Processing command:", command)
        await an_async(command)  # Process each command as an async operation
        await asyncio.sleep(0)  # Yield control to the event loop

def clear_command_queue():
    """Clear all commands from the queue."""
    command_queue.clear()
    print("Command queue cleared.")

def stop_all_commands():
    """Stop all commands and clear the queue."""
    global running_mode, cont_run, exit_set_hdw_async
    clear_command_queue()
    running_mode = ""
    exit_set_hdw_async = True
    cont_run = False
    print("Processing stopped and command queue cleared.")


################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"


################################################################################
# animations


lst_opt = ""


async def an_async(f_nm):
    """Run animation lighting as an async task."""
    global cfg, lst_opt
    print("Filename:", f_nm)
    try:
        await an_light_async(f_nm)
        gc_col("animation cleanup")
    except Exception as e:
        files.log_item(e)
    gc_col("Animation complete.")


async def an_light_async(f_nm):
    """Asynchronous animation lighting."""
    global ts_mode

    flsh_t = []
    if f_exists("animations/" + f_nm + ".json"):
        flsh_t = files.read_json_file("animations/" + f_nm + ".json")

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
                await set_hdw_async(f"L0{lgt},S0{pos}")
            else:
                await set_hdw_async(ft1[1])
            flsh_i += 1
            
        # print (flsh_i)

        await asyncio.sleep(0)  # Yield control to other tasks

        # Exit condition for stopping animation
        if flsh_i >= len(flsh_t)-1:
            led.fill((0, 0, 0))
            led.show()
            break

##############################
# animation effects


sp = [0, 0, 0, 0, 0, 0]
br = 0


async def set_hdw_async(input_string):
    """Async hardware control for NeoPixel lights."""
    global sp, br
    segs = input_string.split(",")

    for seg in segs:
        if seg[0] == 'L':  # Lights
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    sp[i] = v
            else:
                sp[num - 1] = v
            led[0] = (sp[1], sp[0], sp[2])
            led[1] = (sp[4], sp[3], sp[5])
            led.show()
        elif seg[0] == 'B':  # Brightness
            br = int(seg[1:])
            led.brightness = float(br / 100)
        elif seg[0] == 'F':  # Fade in/out
            v = int(seg[1:])
            while br != v:
                if br < v:
                    br += 1
                else:
                    br -= 1
                led.brightness = float(br / 100)
                await asyncio.sleep(0.01)  # Smoothly adjust brightness



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
        server_poll_task(server),
        garbage_collection_task(),
    ]
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
