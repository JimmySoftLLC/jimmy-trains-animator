from rainbowio import colorwheel
import neopixel
from analogio import AnalogIn
import asyncio
from adafruit_motor import servo
import pwmio
import microcontroller
import rtc
import randomfrom rainbowio import colorwheel
import neopixel
from analogio import AnalogIn
import asyncio
from adafruit_motor import servo
import pwmio
import microcontroller
import rtc
import random
import board
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

# Setup the servos
s_1 = pwmio.PWMOut(board.GP9, duty_cycle=2 ** 15, frequency=50)
s_2 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
s_3 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

s_4 = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)
s_5 = pwmio.PWMOut(board.GP13, duty_cycle=2 ** 15, frequency=50)
s_6 = pwmio.PWMOut(board.GP14, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

s_4 = servo.Servo(s_4, min_pulse=500, max_pulse=2500)
s_5 = servo.Servo(s_5, min_pulse=500, max_pulse=2500)
s_6 = servo.Servo(s_6, min_pulse=500, max_pulse=2500)

s_arr = [s_1, s_2, s_3, s_4, s_5, s_6]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

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
            an(cfg["option_selected"])
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
                        "snds/"+ts_fn+".json", ts)
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
            set_hdw(rq_d["an"])
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
            set_hdw(rq_d["an"])
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
                f_n = "snds/" + rq_d["an"] + ".json"
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
                    f_n = ""
                    if "customers_owned_music_" in rq_d[3]:
                        snd_f = rq_d[3].replace("customers_owned_music_", "")
                        f_n = "customers_owned_music/" + \
                            snd_f + ".json"
                    else:
                        f_n = "snds/" + \
                            rq_d[3] + ".json"
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

################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"


################################################################################
# async methods


# Create an event loop
loop = asyncio.get_event_loop()

p_arr = [90, 90, 90, 90, 90, 90]


async def cyc_servo(n, s, p_up, p_dwn):
    global p_arr
    while True:
        n_p = p_up
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)
        n_p = p_dwn
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)


def m_servo(n, p):
    global p_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    s_arr[n].angle = p
    p_arr[n][n] = p

################################################################################
# animations


lst_opt = ""


def an(f_nm):
    global cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        an_light(cur_opt)
        gc_col("animation cleanup")
    except Exception as e:
            files.log_item(e)
    gc_col("Animation complete.")


def an_light(f_nm):
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm

    flsh_t = []

    if cust_f:
        f_nm = f_nm.replace("customers_owned_music_", "")
        if (f_exists("customers_owned_music/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "customers_owned_music/" + f_nm + ".json")
        else:
            flsh_t = files.read_json_file(
                "customers_owned_music/" + f_nm + ".json")

    else:
        if (f_exists("snds/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "snds/" + f_nm + ".json")

    flsh_i = 0

    srt_t = time.monotonic()

    ft1 = []
    ft2 = []

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
            files.log_item("time elapsed: " + str(t_past) +
                  " Timestamp: " + ft1[0])
            if (len(ft1) == 1 or ft1[1] == ""):
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                set_hdw("L0" + str(lgt) + ",S0" + str(pos))
            else:
                set_hdw(ft1[1])
            flsh_i += 1
        if "quit" == "quit":
            led.fill((0, 0, 0))
            led.show()
            return

##############################
# animation effects


sp = [0, 0, 0, 0, 0, 0]
br = 0


def set_hdw(input_string):
    loop.create_task(set_hdw_async(input_string))
    loop.run_forever()


async def set_hdw_async(input_string):
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
            led[0] = (sp[1], sp[0], sp[2])
            led[1] = (sp[4], sp[3], sp[5])
            led.show()
        if seg[0] == 'S':  # servos
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    s_arr[i].angle = v
            else:
                s_arr[num-1].angle = int(v)
        if seg[0] == 'B':  # brightness
            br = int(seg[1:])
            led.brightness = float(br/100)
        if seg[0] == 'F':  # fade in or out
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    led.brightness = float(br/100)
                else:
                    br -= 1
                    led.brightness = float(br/100)



if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        rst()

#  set all servos to 90
set_hdw("S090")

files.log_item("animator has started...")
gc_col("animations started.")

while True:
    if (web):
        try:
            server.poll()
            gc.collect()
        except Exception as e:
            files.log_item(e)
            continue




import board
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

# Setup the servos
s_1 = pwmio.PWMOut(board.GP9, duty_cycle=2 ** 15, frequency=50)
s_2 = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
s_3 = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

s_4 = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)
s_5 = pwmio.PWMOut(board.GP13, duty_cycle=2 ** 15, frequency=50)
s_6 = pwmio.PWMOut(board.GP14, duty_cycle=2 ** 15, frequency=50)

s_1 = servo.Servo(s_1, min_pulse=500, max_pulse=2500)
s_2 = servo.Servo(s_2, min_pulse=500, max_pulse=2500)
s_3 = servo.Servo(s_3, min_pulse=500, max_pulse=2500)

s_4 = servo.Servo(s_4, min_pulse=500, max_pulse=2500)
s_5 = servo.Servo(s_5, min_pulse=500, max_pulse=2500)
s_6 = servo.Servo(s_6, min_pulse=500, max_pulse=2500)

s_arr = [s_1, s_2, s_3, s_4, s_5, s_6]

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card config variables

cfg = files.read_json_file("cfg.json")

animations = files.return_directory("", "animations", ".wav")

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
            an(cfg["option_selected"])
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
                        "snds/"+ts_fn+".json", ts)
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
            set_hdw(rq_d["an"])
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
            set_hdw(rq_d["an"])
            return Response(request, "success")

        @server.route("/get-animation", [POST])
        def btn(request: Request):
            global cfg, cont_run, ts_mode
            rq_d = request.json()
            snd_f = rq_d["an"]
            if "customers_owned_music_" in snd_f:
                snd_f = snd_f.replace("customers_owned_music_", "")
                if (f_exists("customers_owned_music/" + snd_f + ".json") == True):
                    f_n = "customers_owned_music/" + snd_f + ".json"
                    print(f_n)
                    return FileResponse(request, f_n, "/")
                else:
                    f_n = "t_s_def/timestamp mode.json"
                    return FileResponse(request, f_n, "/")
            else:
                if (f_exists("snds/" + snd_f + ".json") == True):
                    f_n = "snds/" + snd_f + ".json"
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
                f_n = "snds/" + rq_d["an"] + ".json"
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
                    f_n = ""
                    if "customers_owned_music_" in rq_d[3]:
                        snd_f = rq_d[3].replace("customers_owned_music_", "")
                        f_n = "customers_owned_music/" + \
                            snd_f + ".json"
                    else:
                        f_n = "snds/" + \
                            rq_d[3] + ".json"
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

################################################################################
# Global Methods

def rst_def():
    global cfg
    cfg["volume_pot"] = True
    cfg["HOST_NAME"] = "animator-bandstand"
    cfg["option_selected"] = "random all"
    cfg["volume"] = "20"


################################################################################
# async methods


# Create an event loop
loop = asyncio.get_event_loop()

p_arr = [90, 90, 90, 90, 90, 90]


async def cyc_servo(n, s, p_up, p_dwn):
    global p_arr
    while True:
        n_p = p_up
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)
        n_p = p_dwn
        sign = 1
        if p_arr[n] > n_p:
            sign = - 1
        for a in range(p_arr[n], n_p, sign):
            m_servo(a)
            await asyncio.sleep(s)


def m_servo(n, p):
    global p_arr
    if p < 0:
        p = 0
    if p > 180:
        p = 180
    s_arr[n].angle = p
    p_arr[n][n] = p

################################################################################
# animations


lst_opt = ""


def an(f_nm):
    global cfg, lst_opt
    print("Filename: " + f_nm)
    cur_opt = f_nm
    try:
        an_light(cur_opt)
        gc_col("animation cleanup")
    except Exception as e:
            files.log_item(e)
    gc_col("Animation complete.")


def an_light(f_nm):
    global ts_mode

    cust_f = "customers_owned_music_" in f_nm

    flsh_t = []

    if cust_f:
        f_nm = f_nm.replace("customers_owned_music_", "")
        if (f_exists("customers_owned_music/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "customers_owned_music/" + f_nm + ".json")
        else:
            flsh_t = files.read_json_file(
                "customers_owned_music/" + f_nm + ".json")

    else:
        if (f_exists("snds/" + f_nm + ".json") == True):
            flsh_t = files.read_json_file(
                "snds/" + f_nm + ".json")

    flsh_i = 0

    srt_t = time.monotonic()

    ft1 = []
    ft2 = []

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
            files.log_item("time elapsed: " + str(t_past) +
                  " Timestamp: " + ft1[0])
            if (len(ft1) == 1 or ft1[1] == ""):
                pos = random.randint(60, 120)
                lgt = random.randint(60, 120)
                set_hdw("L0" + str(lgt) + ",S0" + str(pos))
            else:
                set_hdw(ft1[1])
            flsh_i += 1
        if "quit" == "quit":
            led.fill((0, 0, 0))
            led.show()
            return

##############################
# animation effects


sp = [0, 0, 0, 0, 0, 0]
br = 0


def set_hdw(input_string):
    loop.create_task(set_hdw_async(input_string))
    loop.run_forever()


async def set_hdw_async(input_string):
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
            led[0] = (sp[1], sp[0], sp[2])
            led[1] = (sp[4], sp[3], sp[5])
            led.show()
        if seg[0] == 'S':  # servos
            num = int(seg[1])
            v = int(seg[2:])
            if num == 0:
                for i in range(6):
                    s_arr[i].angle = v
            else:
                s_arr[num-1].angle = int(v)
        if seg[0] == 'B':  # brightness
            br = int(seg[1:])
            led.brightness = float(br/100)
        if seg[0] == 'F':  # fade in or out
            v = int(seg[1:])
            while not br == v:
                if br < v:
                    br += 1
                    led.brightness = float(br/100)
                else:
                    br -= 1
                    led.brightness = float(br/100)



if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")
        rst()

#  set all servos to 90
set_hdw("S090")

files.log_item("animator has started...")
gc_col("animations started.")

while True:
    if (web):
        try:
            server.poll()
            gc.collect()
        except Exception as e:
            files.log_item(e)
            continue


