import time
import audiocore
import audiomixer
import audiobusio
import sdcardio
import storage
import busio
import digitalio
import board
import microcontroller
import pwmio
from analogio import AnalogIn
from adafruit_debouncer import Debouncer
from adafruit_motor import servo
import utilities
import neopixel
import random
import asyncio
import gc
import files
import rtc


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

# Setup pin for v
a_in = AnalogIn(board.A0)

# setup pin for audio enable
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
i2s_bclk = board.GP18   # BCLK on MAX98357A
i2s_lrc = board.GP19  # LRC on MAX98357A
i2s_din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lrc, data=i2s_din)

# Setup sdCard
aud_en.value = True
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5
spi = busio.SPI(sck, si, so)

# Setup the mixer
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050,
                       channel_count=2, bits_per_sample=16, samples_signed=True, buffer_size=4096)
aud.play(mix)

mix.voice[0].level = .2

try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
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
                sdcard = sdcardio.SDCard(spi, cs)
                vfs = storage.VfsFat(sdcard)
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

# Setup the servo
d_s = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
g_s = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)
r_s = pwmio.PWMOut(board.GP12, duty_cycle=2 ** 15, frequency=50)

d_s = servo.Servo(d_s, min_pulse=500, max_pulse=2500)
g_s = servo.Servo(g_s, min_pulse=500, max_pulse=2500)
r_s = servo.Servo(r_s, min_pulse=500, max_pulse=2500)

d_lst_p = 90
d_min = 0
d_max = 180

g_lst_p = 90
g_min = 0
g_max = 180

r_lst_p = 90
r_min = 0
r_max = 180

# Setup time
r = rtc.RTC()
r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))

################################################################################
# Sd card data Variables

cfg = files.read_json_file("/sd/cfg.json")

snd_opt = files.return_directory("", "/sd/snds", ".wav")

cfg_mov_r_d = files.read_json_file("/sd/mvc/move_roof_door.json")
mov_r_d = cfg_mov_r_d["move_roof_door"]

cfg_adj_r_d = files.read_json_file("/sd/mvc/adjust_roof_door.json")
adj_r_d = cfg_adj_r_d["adjust_roof_door"]

web = cfg["serve_webpage"]

cfg_main = files.read_json_file("/sd/mvc/main_menu.json")
main_m = cfg_main["main_menu"]

cfg_web = files.read_json_file("/sd/mvc/web_menu.json")
web_m = cfg_web["web_menu"]

cfd_vol = files.read_json_file("/sd/mvc/volume_settings.json")
vol_set = cfd_vol["volume_settings"]

cfg_inst_m = files.read_json_file("/sd/mvc/install_menu.json")
inst_m = cfg_inst_m["install_menu"]

cont_run = False

gc_col("config setup")

################################################################################
# Setup neo pixels

num_px = 6

led_B = neopixel.NeoPixel(board.GP15, num_px)
led_F = neopixel.NeoPixel(board.GP16, 1)

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
        env = files.read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        gc_col("wifi env")
        print("Using env ssid and password")
    except:
        print("Using default ssid and password")

    try:
        # connect to your SSID
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        gc_col("wifi connect")

        # setup mdns server
        mdns_server = mdns.Server(wifi.radio)
        mdns_server.hostname = cfg["HOST_NAME"]
        mdns_server.advertise_service(
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
        def buttonpress(request: Request):
            global cfg
            global cont_run
            raw_text = request.raw_request.decode("utf8")
            if "random" in raw_text:
                cfg["option_selected"] = "random"
                animate_outhouse()
            elif "explosions" in raw_text:
                cfg["option_selected"] = "explosions"
                animate_outhouse()
            elif "humor" in raw_text:
                cfg["option_selected"] = "humor"
                animate_outhouse()
            elif "objectionable" in raw_text:
                cfg["option_selected"] = "objectionable"
                animate_outhouse()
            elif "thoughts on the toilet" in raw_text:
                cfg["option_selected"] = "thoughts on the toilet"
                animate_outhouse()
            elif "waiting crowd" in raw_text:
                cfg["option_selected"] = "waiting crowd"
                animate_outhouse()
            elif "home life" in raw_text:
                cfg["option_selected"] = "home life"
                animate_outhouse()
            elif "cont_mode_on" in raw_text:
                cont_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
            elif "cont_mode_off" in raw_text:
                cont_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            return Response(request, "Animation " + cfg["option_selected"] + " started.")

        @server.route("/utilities", [POST])
        def buttonpress(request: Request):
            global cfg
            raw_text = request.raw_request.decode("utf8")
            if "speaker_test" in raw_text:
                play_audio_0("/sd/mvc/left_speaker_right_speaker.wav")
            elif "volume_pot_off" in raw_text:
                cfg["volume_pot"] = False
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "volume_pot_on" in raw_text:
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
            elif "reset_to_defaults" in raw_text:
                reset_to_defaults()
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')

            return Response(request, "Dialog option cal saved.")

        @server.route("/update-host-name", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            cfg["HOST_NAME"] = data_object["text"]
            files.write_json_file("/sd/cfg.json", cfg)
            mdns_server.hostname = cfg["HOST_NAME"]
            speak_webpage()
            return Response(request, cfg["HOST_NAME"])

        @server.route("/get-host-name", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["HOST_NAME"])

        @server.route("/update-v", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            changeVolume(data_object["action"])
            return Response(request, cfg["v"])

        @server.route("/get-v", [POST])
        def buttonpress(request: Request):
            return Response(request, cfg["v"])

        @server.route("/roof", [POST])
        def buttonpress(request: Request):
            global cfg
            global roof_movement_type
            raw_text = request.raw_request.decode("utf8")
            if "roof_open_pos" in raw_text:
                roof_movement_type = "roof_open_position"
                moveRoofToPositionGently(cfg[roof_movement_type], 0.01)
                return Response(request, "Moved to roof open position.")
            elif "roof_closed_pos" in raw_text:
                roof_movement_type = "roof_closed_position"
                moveRoofToPositionGently(cfg[roof_movement_type], 0.01)
                return Response(request, "Moved to roof closed position.")
            elif "roof_open_more" in raw_text:
                calibrationLeftButtonPressed(
                    r_s, roof_movement_type, -1, 0, 180)
                return Response(request, "Moved door open more.")
            elif "roof_close_more" in raw_text:
                calibrationRightButtonPressed(
                    r_s, roof_movement_type, -1, 0, 180)
                return Response(request, "Moved door close more.")
            elif "roof_cal_saved" in raw_text:
                write_calibrations_to_config_file()
                state_machine.go_to_state('base_state')
                return Response(request, "Tree " + roof_movement_type + " cal saved.")

        @server.route("/door", [POST])
        def buttonpress(request: Request):
            global cfg
            global door_movement_type
            raw_text = request.raw_request.decode("utf8")
            if "door_open_pos" in raw_text:
                door_movement_type = "door_open_position"
                moveDoorToPositionGently(cfg[door_movement_type], 0.01)
                return Response(request, "Moved to door open position.")
            elif "door_closed_pos" in raw_text:
                door_movement_type = "door_closed_position"
                moveDoorToPositionGently(cfg[door_movement_type], 0.01)
                return Response(request, "Moved to door closed position.")
            elif "door_open_more" in raw_text:
                calibrationLeftButtonPressed(
                    d_s, door_movement_type, 1, 0, 180)
                return Response(request, "Moved door open more.")
            elif "door_close_more" in raw_text:
                calibrationRightButtonPressed(
                    d_s, door_movement_type, 1, 0, 180)
                return Response(request, "Moved door close more.")
            elif "door_cal_saved" in raw_text:
                write_calibrations_to_config_file()
                state_machine.go_to_state('base_state')
                return Response(request, "Tree " + door_movement_type + " cal saved.")

        @server.route("/install-figure", [POST])
        def buttonpress(request: Request):
            global cfg
            data_object = request.json()
            if data_object["action"] != "right":
                cfg["figure"] = data_object["action"]
                print(cfg["figure"])
                install_figure(False)
            if data_object["action"] == "right":
                moveGuyToPositionGently(cfg["guy_down_position"], 0.01)
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                state_machine.go_to_state('base_state')
            return Response(request, cfg["v"])

    except Exception as e:
        web = False
        files.log_item(e)

gc_col("web server")

################################################################################
# Dialog and sound play methods


def sleepAndUpdateVolume(seconds):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        time.sleep(seconds)
    else:
        try:
            v = int(cfg["volume"]) / 100
        except:
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        time.sleep(seconds)


def changeVolume(action):
    v = int(cfg["volume"])
    if "v" in action:
        v = action.split("v")
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
    play_audio_0("/sd/mvc/volume.wav")
    speak_this_string(cfg["volume"], False)


def play_audio_0(file_name):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            sleepAndUpdateVolume(0.02)
    print("playing" + file_name)
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    while mix.voice[0].playing:
        shortCircuitDialog()
    print("done playing")


def shortCircuitDialog():
    sleepAndUpdateVolume(0.02)
    l_sw.update()
    if l_sw.fell:
        mix.voice[0].stop()


def speak_this_string(str_to_speak, addLocal):
    for character in str_to_speak:
        try:
            if character == " ":
                character = "space"
            if character == "-":
                character = "dash"
            if character == ".":
                character = "dot"
            play_audio_0("/sd/mvc/" + character + ".wav")
        except:
            print("Invalid character in string to speak")
    if addLocal:
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")


def speak_webpage():
    play_audio_0("/sd/mvc/animator_available_on_network.wav")
    play_audio_0("/sd/mvc/to_access_type.wav")
    if cfg["HOST_NAME"] == "animator-outhouse":
        play_audio_0("/sd/mvc/animator_dash_outhouse.wav")
        play_audio_0("/sd/mvc/dot.wav")
        play_audio_0("/sd/mvc/local.wav")
    else:
        speak_this_string(cfg["HOST_NAME"], True)
    play_audio_0("/sd/mvc/in_your_browser.wav")


def left_right_mouse_button():
    play_audio_0("/sd/mvc/press_left_button_right_button.wav")


def option_selected_announcement():
    play_audio_0("/sd/mvc/option_selected.wav")


def doorCalAnnouncement():
    play_audio_0("/sd/mvc/adjust_the_door_position_instruct.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")


def roofCalAnnouncement():
    play_audio_0("/sd/mvc/adjust_the_roof_position_instruct.wav")
    play_audio_0("/sd/mvc/to_exit_press_and_hold_button_down.wav")


def selectWebOptionsAnnouncement():
    play_audio_0("/sd/mvc/web_menu.wav")
    left_right_mouse_button()


def checkLimits(min_servo_pos, max_servo_pos, servo_pos):
    if servo_pos < min_servo_pos:
        play_audio_0("/sd/mvc/limit_reached.wav")
        return False
    if servo_pos > max_servo_pos:
        play_audio_0("/sd/mvc/limit_reached.wav")
        return False
    return True


################################################################################
# Servo helpers


def moveDoorServo(servo_pos):
    if servo_pos < d_min:
        servo_pos = d_min
    if servo_pos > d_max:
        servo_pos = d_max
    d_s.angle = servo_pos
    global d_lst_p
    d_lst_p = servo_pos


def moveDoorToPositionGently(new_position, speed):
    global d_lst_p
    sign = 1
    if d_lst_p > new_position:
        sign = - 1
    for door_angle in range(d_lst_p, new_position, sign):
        moveDoorServo(door_angle)
        time.sleep(speed)
    moveDoorServo(new_position)


def moveGuyServo(servo_pos):
    if servo_pos < g_min:
        servo_pos = g_min
    if servo_pos > g_max:
        servo_pos = g_max
    g_s.angle = servo_pos
    global g_lst_p
    g_lst_p = servo_pos


def moveGuyToPositionGently(new_position, speed):
    global g_lst_p
    sign = 1
    if g_lst_p > new_position:
        sign = - 1
    for guy_angle in range(g_lst_p, new_position, sign):
        moveGuyServo(guy_angle)
        time.sleep(speed)
    moveGuyServo(new_position)


def moveRoofServo(servo_pos):
    if servo_pos < r_min:
        servo_pos = r_min
    if servo_pos > r_max:
        servo_pos = r_max
    r_s.angle = servo_pos
    global r_lst_p
    r_lst_p = servo_pos


def moveRoofToPositionGently(new_position, speed):
    global r_lst_p
    sign = 1
    if r_lst_p > new_position:
        sign = - 1
    for roof_angle in range(r_lst_p, new_position, sign):
        moveRoofServo(roof_angle)
        time.sleep(speed)
    moveRoofServo(new_position)


def calibrationLeftButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global cfg
    cfg[movement_type] -= 1 * sign
    if checkLimits(min_servo_pos, max_servo_pos, cfg[movement_type]):
        servo.angle = cfg[movement_type]
    else:
        cfg[movement_type] += 1 * sign


def calibrationRightButtonPressed(servo, movement_type, sign, min_servo_pos, max_servo_pos):
    global cfg
    cfg[movement_type] += 1 * sign
    if checkLimits(min_servo_pos, max_servo_pos, cfg[movement_type]):
        servo.angle = cfg[movement_type]
    else:
        cfg[movement_type] -= 1 * sign


def write_calibrations_to_config_file():
    play_audio_0("/sd/mvc/all_changes_complete.wav")
    global cfg
    files.write_json_file("/sd/cfg.json", cfg)


def calibratePosition(servo, movement_type):
    if movement_type == "door_close_position" or movement_type == "door_open_position":
        min_servo_pos = 0
        max_servo_pos = 180
        sign = 1
    else:
        min_servo_pos = 0
        max_servo_pos = 180
        sign = -1
    calibrations_complete = False
    while not calibrations_complete:
        servo.angle = cfg[movement_type]
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            calibrationLeftButtonPressed(
                servo, movement_type, sign, min_servo_pos, max_servo_pos)
        if r_sw.fell:
            button_check = True
            number_cycles = 0
            while button_check:
                sleepAndUpdateVolume(.1)
                r_sw.update()
                number_cycles += 1
                if number_cycles > 30:
                    write_calibrations_to_config_file()
                    button_check = False
                    calibrations_complete = True
                if r_sw.rose:
                    button_check = False
            if not calibrations_complete:
                calibrationRightButtonPressed(
                    servo, movement_type, sign, min_servo_pos, max_servo_pos)
    if movement_type == "door_close_position" or movement_type == "door_open_position":
        global d_lst_p
        d_lst_p = cfg[movement_type]
    else:
        global r_lst_p
        r_lst_p = cfg[movement_type]

################################################################################
# async methods


# Create an event loop
loop = asyncio.get_event_loop()


async def sleepAndUpdateVolumeAsync(seconds):
    if cfg["volume_pot"]:
        v = a_in.value / 65536
        mix.voice[0].level = v
        await asyncio.sleep(seconds)
    else:
        try:
            v = int(cfg["v"]) / 100
        except:
            v = .5
        if v < 0 or v > 1:
            v = .5
        mix.voice[0].level = v
        await asyncio.sleep(seconds)


async def fireAsync():
    led_B.brightness = 1.0

    r = random.randint(150, 255)
    g = 0  # random.randint(0,255)
    b = 0  # random.randint(0,255)

    # Flicker, based on our initial RGB values
    while mix.voice[0].playing:
        for i in range(0, num_px):
            flicker = random.randint(0, 175)
            r1 = bounds(r-flicker, 0, 255)
            led_B[i] = (r1, 0, 0)
        led_B.show()
        await sleepAndUpdateVolumeAsync(random.uniform(0.05, 0.1))
    led_F[0] = (0, 0, 0)
    led_F.show()


def fire():
    led_B.brightness = 1.0

    r = random.randint(0, 0)
    g = random.randint(150, 255)
    b = random.randint(0, 0)

    # Flicker, based on our initial RGB values
    while mix.voice[0].playing:
        for i in range(0, 3):
            flicker = random.randint(0, 175)
            r1 = bounds(r-flicker, 0, 255)
            g1 = bounds(g-flicker, 0, 255)
            b1 = bounds(b-flicker, 0, 255)
            led_B[i] = (r1, g1, b1)
            led_B.show()
            sleepAndUpdateVolume(random.uniform(0.05, 0.1))
        for i in range(0, 3):
            led_B[i] = (0, 0, 0)
        led_B.show()


async def cycleGuyAsync(speed, pos_up, pos_down):
    global g_lst_p
    while mix.voice[0].playing:
        new_position = pos_up
        sign = 1
        if g_lst_p > new_position:
            sign = - 1
        for guy_angle in range(g_lst_p, new_position, sign):
            moveGuyServo(guy_angle)
            await asyncio.sleep(speed)
        new_position = pos_down
        sign = 1
        if g_lst_p > new_position:
            sign = - 1
        for guy_angle in range(g_lst_p, new_position, sign):
            moveGuyServo(guy_angle)
            await asyncio.sleep(speed)


async def runExplosion():
    cycle_guy = asyncio.create_task(cycleGuyAsync(
        0.01, cfg["guy_up_position"]+20, cfg["guy_up_position"]))
    cycle_lights = asyncio.create_task(fireAsync())
    await asyncio.gather(cycle_guy, cycle_lights)
    while mix.voice[0].playing:
        shortCircuitDialog()

################################################################################
# Animations


def play_audio_0_lit(file_name, match_start, match_time):
    if mix.voice[0].playing:
        mix.voice[0].stop()
        while mix.voice[0].playing:
            sleepAndUpdateVolume(0.02)
    print("playing" + file_name)
    w0 = audiocore.WaveFile(open(file_name, "rb"))
    mix.voice[0].play(w0, loop=False)
    time.sleep(match_start)
    led_B[0] = ((255, 0, 0))
    led_B.show()
    time.sleep(match_time)
    led_B[0] = ((0, 0, 0))
    led_B.show()
    while mix.voice[0].playing:
        shortCircuitDialog()
    print("done playing")


def sitting_down():
    print("sitting down")
    moveGuyToPositionGently(cfg["guy_down_position"]-10, 0.05)
    led_F[0] = ((255, 147, 41))
    led_F.show()
    moveDoorToPositionGently(cfg["door_open_position"], .05)
    print(cfg["figure"])
    if cfg["figure"] == "alien":
        w0 = audiocore.WaveFile(
            open("/sd/o_s/alien_1_unusual_space_portal.wav", "rb"))
        mix.voice[0].play(w0, loop=False)
        fire()
        w0 = audiocore.WaveFile(
            open("/sd/o_s/alien_1_lets_get_seated.wav", "rb"))
        mix.voice[0].play(w0, loop=False)
        fire()
        moveGuyToPositionGently(cfg["guy_down_position"], 0.05)
        moveDoorToPositionGently(cfg["door_closed_position"], .05)
        play_audio_0("/sd/o_s/alien_1_communication.wav")
    elif cfg["figure"] == "man":
        moveGuyToPositionGently(cfg["guy_down_position"], 0.05)
        moveDoorToPositionGently(cfg["door_closed_position"], .05)
        led_F[0] = ((0, 0, 0))
        play_audio_0("/sd/o_s/man_2_roses_light_a_match.wav")
        play_audio_0_lit("/sd/m_f/fail1.wav", .1, .1)
        play_audio_0_lit("/sd/m_f/fail1.wav", .1, .1)
        play_audio_0_lit("/sd/m_f/fail1.wav", .1, .1)
        play_audio_0_lit("/sd/m_l/lit3.wav", .4, .4)


def animate_outhouse():
    sitting_down()

    print("explosion")
    current_option_selected = cfg["option_selected"]
    print("Sound file: " + current_option_selected)
    w0 = audiocore.WaveFile(
        open("/sd/snds/" + current_option_selected + ".wav", "rb"))
    mix.voice[0].play(w0, loop=False)
    time.sleep(.1)
    moveRoofServo(cfg["roof_open_position"])
    moveGuyServo(cfg["guy_up_position"])
    moveDoorServo(cfg["door_open_position"])
    delay_time = .05
    led_F[0] = (0, 255, 0)
    led_F.show()
    for i in range(0, 6):
        led_B[i] = (255, 0, 0)
        led_B.show()
        time.sleep(delay_time)
    asyncio.run(runExplosion())

    print("reset")
    led_B.fill((0, 0, 0))
    led_B.show()
    moveDoorServo(cfg["door_closed_position"])
    moveGuyToPositionGently(cfg["guy_down_position"]-10, 0.001)
    time.sleep(.2)
    moveRoofToPositionGently(cfg["roof_closed_position"]+20, .001)
    moveRoofToPositionGently(cfg["roof_closed_position"], .05)
    time.sleep(2)


def bounds(my_color, lower, upper):
    if (my_color < lower):
        my_color = lower
    if (my_color > upper):
        my_color = upper
    return my_color


def install_figure(wait_for_button):
    moveRoofToPositionGently(cfg["roof_open_position"], 0.01)
    moveDoorToPositionGently(cfg["door_open_position"], 0.01)
    moveGuyToPositionGently(cfg["guy_up_position"], 0.01)
    play_audio_0("/sd/mvc/install_figure_instructions.wav")
    while wait_for_button:
        l_sw.update()
        r_sw.update()
        if r_sw.fell:
            moveGuyToPositionGently(cfg["guy_down_position"], 0.01)
            files.write_json_file("/sd/cfg.json", cfg)
            play_audio_0("/sd/mvc/all_changes_complete.wav")
            break

################################################################################
# State Machine


class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.paused_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def update(self):
        if self.state:
            self.state.update(self)

################################################################################
# States

# Abstract parent state class.


class State(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        pass


class BaseState(State):

    def __init__(self):
        pass

    @property
    def name(self):
        return 'base_state'

    def enter(self, machine):
        # set servos to starting position
        moveGuyToPositionGently(cfg["guy_down_position"], 0.01)
        moveDoorToPositionGently(cfg["door_closed_position"], 0.01)
        moveRoofToPositionGently(cfg["roof_closed_position"], 0.01)

        play_audio_0("/sd/mvc/animations_are_now_active.wav")
        files.log_item("Entered base state")
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global cont_run
        switch_state = utilities.switch_state(
            l_sw, r_sw, sleepAndUpdateVolume, 3.0)
        if switch_state == "left_held":
            if cont_run:
                cont_run = False
                play_audio_0("/sd/mvc/continuous_mode_deactivated.wav")
            else:
                cont_run = True
                play_audio_0("/sd/mvc/continuous_mode_activated.wav")
        elif switch_state == "left" or cont_run:
            animate_outhouse()
        elif switch_state == "right":
            machine.go_to_state('main_menu')


class MoveRoofDoor(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'move_roof_door'

    def enter(self, machine):
        files.log_item('Move roof or door menu')
        play_audio_0("/sd/mvc/move_roof_or_door_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + mov_r_d[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(mov_r_d)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = mov_r_d[self.selectedMenuIndex]
            if selected_menu_item == "move_door_open_position":
                moveDoorToPositionGently(cfg["door_open_position"], 0.01)
            elif selected_menu_item == "move_door_closed_position":
                moveDoorToPositionGently(cfg["door_closed_position"], 0.01)
            elif selected_menu_item == "move_roof_open_position":
                moveRoofToPositionGently(cfg["roof_open_position"], 0.01)
            elif selected_menu_item == "move_roof_closed_position":
                moveRoofToPositionGently(cfg["roof_closed_position"], 0.01)
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class AdjustRoofDoor(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'adjust_roof_door'

    def enter(self, machine):
        files.log_item('Adjust roof or door menu')
        play_audio_0("/sd/mvc/adjust_roof_or_door_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0(
                "/sd/mvc/" + adj_r_d[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(adj_r_d)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = adj_r_d[self.selectedMenuIndex]
            if selected_menu_item == "adjust_door_open_position":
                moveDoorToPositionGently(cfg["door_open_position"], 0.01)
                doorCalAnnouncement()
                calibratePosition(d_s, "door_open_position")
                machine.go_to_state('base_state')
            elif selected_menu_item == "adjust_door_closed_position":
                moveDoorToPositionGently(cfg["door_closed_position"], 0.01)
                doorCalAnnouncement()
                calibratePosition(d_s, "door_closed_position")
                machine.go_to_state('base_state')
            elif selected_menu_item == "adjust_roof_open_position":
                moveRoofToPositionGently(cfg["roof_open_position"], 0.01)
                roofCalAnnouncement()
                calibratePosition(r_s, "roof_open_position")
                machine.go_to_state('base_state')
            elif selected_menu_item == "adjust_roof_closed_position":
                moveRoofToPositionGently(cfg["roof_closed_position"], 0.01)
                roofCalAnnouncement()
                calibratePosition(r_s, "roof_closed_position")
                machine.go_to_state('base_state')
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class VolumeSettings(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'volume_settings'

    def enter(self, machine):
        files.log_item('Set Web Options')
        play_audio_0("/sd/mvc/volume_settings_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + vol_set[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(vol_set)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = vol_set[self.selectedMenuIndex]
            if selected_menu_item == "volume_level_adjustment":
                play_audio_0("/sd/mvc/volume_adjustment_menu.wav")
                done = False
                while not done:
                    switch_state = utilities.switch_state(
                        l_sw, r_sw, sleepAndUpdateVolume, 3.0)
                    if switch_state == "left":
                        changeVolume("lower")
                    elif switch_state == "right":
                        changeVolume("raise")
                    elif switch_state == "right_held":
                        files.write_json_file("/sd/cfg.json", cfg)
                        play_audio_0("/sd/mvc/all_changes_complete.wav")
                        done = True
                        machine.go_to_state('base_state')
                    sleepAndUpdateVolume(0.1)
                    pass
            elif selected_menu_item == "volume_pot_off":
                cfg["volume_pot"] = False
                if cfg["v"] == 0:
                    cfg["v"] = 10
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')
            elif selected_menu_item == "volume_pot_on":
                cfg["volume_pot"] = True
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class WebOptions(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'web_options'

    def enter(self, machine):
        files.log_item('Set Web Options')
        selectWebOptionsAnnouncement()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                play_audio_0("/sd/mvc/" + web_m[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex += 1
                if self.menuIndex > len(web_m)-1:
                    self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = web_m[self.selectedMenuIndex]
            if selected_menu_item == "web_on":
                cfg["serve_webpage"] = True
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "web_off":
                cfg["serve_webpage"] = False
                option_selected_announcement()
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_url":
                speak_this_string(cfg["HOST_NAME"], True)
                selectWebOptionsAnnouncement()
            elif selected_menu_item == "hear_instr_web":
                play_audio_0("/sd/mvc/web_instruct.wav")
                selectWebOptionsAnnouncement()
            else:
                files.write_json_file("/sd/cfg.json", cfg)
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')


class ChooseSounds(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'choose_sounds'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        play_audio_0("/sd/mvc/sound_selection_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            if mix.voice[0].playing:
                mix.voice[0].stop()
                while mix.voice[0].playing:
                    pass
            else:
                play_audio_0("/sd/mvc/option_" +
                             snd_opt[self.menuIndex] + ".wav")
                self.selectedMenuIndex = self.menuIndex
                self.menuIndex += 1
                if self.menuIndex > len(snd_opt)-1:
                    self.menuIndex = 0
        if r_sw.fell:
            cfg["option_selected"] = snd_opt[self.selectedMenuIndex]
            files.log_item("Selected index: " + str(self.selectedMenuIndex) +
                           " Saved option: " + cfg["option_selected"])
            files.write_json_file("/sd/cfg.json", cfg)
            option_selected_announcement()
            machine.go_to_state('base_state')


class InstallFigure(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'install_figure'

    def enter(self, machine):
        files.log_item('Choose sounds menu')
        play_audio_0("/sd/mvc/install_figure_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        global cfg
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0(
                "/sd/mvc/" + inst_m[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(main_m)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = inst_m[self.selectedMenuIndex]
            cfg["figure"] = selected_menu_item
            install_figure(True)
            machine.go_to_state('base_state')


class MainMenu(State):

    def __init__(self):
        self.menuIndex = 0
        self.selectedMenuIndex = 0

    @property
    def name(self):
        return 'main_menu'

    def enter(self, machine):
        files.log_item('Main menu')
        play_audio_0("/sd/mvc/main_menu.wav")
        left_right_mouse_button()
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        l_sw.update()
        r_sw.update()
        if l_sw.fell:
            play_audio_0("/sd/mvc/" + main_m[self.menuIndex] + ".wav")
            self.selectedMenuIndex = self.menuIndex
            self.menuIndex += 1
            if self.menuIndex > len(main_m)-1:
                self.menuIndex = 0
        if r_sw.fell:
            selected_menu_item = main_m[self.selectedMenuIndex]
            if selected_menu_item == "choose_sounds":
                machine.go_to_state('choose_sounds')
            elif selected_menu_item == "adjust_roof_door":
                machine.go_to_state('adjust_roof_door')
            elif selected_menu_item == "move_roof_door":
                machine.go_to_state('move_roof_door')
            elif selected_menu_item == "set_dialog_options":
                machine.go_to_state('set_dialog_options')
            elif selected_menu_item == "web_options":
                machine.go_to_state('web_options')
            elif selected_menu_item == "volume_settings":
                machine.go_to_state('volume_settings')
            elif selected_menu_item == "install_figure":
                machine.go_to_state('install_figure')
            else:
                play_audio_0("/sd/mvc/all_changes_complete.wav")
                machine.go_to_state('base_state')

# StateTemplate copy and add functionality


class StateTemplate(State):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'example'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        State.update(self, machine)


gc_col("state machine")

###############################################################################
# Create the state machine

state_machine = StateMachine()
state_machine.add_state(BaseState())
state_machine.add_state(MainMenu())
state_machine.add_state(ChooseSounds())
state_machine.add_state(AdjustRoofDoor())
state_machine.add_state(MoveRoofDoor())
state_machine.add_state(WebOptions())
state_machine.add_state(VolumeSettings())
state_machine.add_state(InstallFigure())

sleepAndUpdateVolume(.1)
aud_en.value = True

if (web):
    files.log_item("starting server...")
    try:
        server.start(str(wifi.radio.ipv4_address))
        files.log_item("Listening on http://%s:80" % wifi.radio.ipv4_address)
        speak_webpage()
    except OSError:
        time.sleep(5)
        files.log_item("restarting...")

state_machine.go_to_state('base_state')
files.log_item("animator has started...")
gc_col("animations started.")

while True:
    loop.run_forever()
    state_machine.update()
    sleepAndUpdateVolume(.1)
    if (web):
        try:
            server.poll()
        except Exception as e:
            files.log_item(e)
            continue
