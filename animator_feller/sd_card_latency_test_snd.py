from adafruit_debouncer import Debouncer
from adafruit_motor import servo
from analogio import AnalogIn
import board
import busio
import digitalio
import pwmio
import storage
import sdcardio
import audiobusio
import audiomixer
import audiocore
import asyncio
import time
import gc
import os
import json

TEST_FILE = "/sd/feller_sounds/sounds_train.wav"
PASSES = 5
BLOCK_SIZES = (512, 1024, 2048, 4096)

################################################################################
# Audio

aud = audiobusio.I2SOut(
    bit_clock=board.GP18,
    word_select=board.GP19,
    data=board.GP20)

mix = audiomixer.Mixer(
    voice_count=1, sample_rate=22050, channel_count=2,
    bits_per_sample=16, samples_signed=True, buffer_size=4096)

aud.play(mix)
mix.voice[0].level = .2

a_in = AnalogIn(board.A0)

aud_en = digitalio.DigitalInOut(board.GP22)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

################################################################################
# Switches - same setup as Feller

l_sw_io = digitalio.DigitalInOut(board.GP6)
l_sw_io.direction = digitalio.Direction.INPUT
l_sw_io.pull = digitalio.Pull.UP
l_sw = Debouncer(l_sw_io)

r_sw_io = digitalio.DigitalInOut(board.GP7)
r_sw_io.direction = digitalio.Direction.INPUT
r_sw_io.pull = digitalio.Pull.UP
r_sw = Debouncer(r_sw_io)

t_sw_io = digitalio.DigitalInOut(board.GP8)
t_sw_io.direction = digitalio.Direction.INPUT
t_sw_io.pull = digitalio.Pull.UP
t_sw = Debouncer(t_sw_io)

################################################################################
# SD card - same setup as Feller

print("Setting up SD card...")

spi = busio.SPI(board.GP2, board.GP3, board.GP4)
sdcard = sdcardio.SDCard(spi, board.GP5)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("SD card mounted")

################################################################################
# Servos - same hardware as Feller

f_pwm = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)
t_pwm = pwmio.PWMOut(board.GP11, duty_cycle=2 ** 15, frequency=50)

f_s = servo.Servo(f_pwm)
t_s = servo.Servo(t_pwm)

################################################################################
# Read config so web setup matches actual Feller

def read_json_file(file_name):
    with open(file_name, "r") as f:
        return json.loads(f.read())

try:
    cfg = read_json_file("/sd/cfg.json")
except Exception as e:
    print("Config error:", e)
    cfg = read_json_file("/sd/cfg_default.json")

web = cfg["serve_webpage"]

################################################################################
# Wi-Fi/web - same basic setup as Feller

if web:
    import socketpool
    import mdns
    import wifi
    from adafruit_httpserver import Server, Request, FileResponse, Response, POST

    WIFI_SSID = "jimmytrainsguest"
    WIFI_PASSWORD = ""

    try:
        env = read_json_file("/sd/env.json")
        WIFI_SSID = env["WIFI_SSID"]
        WIFI_PASSWORD = env["WIFI_PASSWORD"]
        print("Using env ssid and password")
    except Exception as e:
        print(e)
        print("Using default ssid and password")

    print("Connecting to WiFi")
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)

    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = cfg["HOST_NAME"]
    mdns_server.advertise_service(
        service_type="_http", protocol="_tcp", port=80)

    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)

    @server.route("/")
    def base(request):
        return FileResponse(request, "index.html", "/")

    @server.route("/test")
    def test_route(request):
        return Response(request, "SD stress test running")

    server.start(str(wifi.radio.ipv4_address))

    print("WiFi connected:", wifi.radio.ipv4_address)
    print("Web server started")
else:
    print("Web disabled in cfg.json")

################################################################################
# Continuous flash audio

w0 = audiocore.WaveFile(open("wav/no_card.wav", "rb"))
mix.voice[0].play(w0, loop=True)

print("Internal flash audio looping")
print("Free memory:", gc.mem_free())

test_running = True

################################################################################
# Simulate Feller/tree servo activity

async def servo_task():
    f_pos = 0
    t_pos = 165
    f_dir = 1
    t_dir = -1
    while test_running:
        f_s.angle = f_pos
        f_pos += f_dir * 5
        if f_pos >= 150:
            f_pos = 150
            f_dir = -1
        elif f_pos <= 0:
            f_pos = 0
            f_dir = 1

        t_s.angle = t_pos
        t_pos += t_dir * 3
        if t_pos <= 100:
            t_pos = 100
            t_dir = 1
        elif t_pos >= 165:
            t_pos = 165
            t_dir = -1

        await asyncio.sleep(0.02)

################################################################################
# Same sort of volume activity as actual program

async def volume_task():
    while test_running:
        mix.voice[0].level = a_in.value / 65536
        await asyncio.sleep(0.01)

################################################################################
# Debouncer activity

async def switch_task():
    while test_running:
        l_sw.update()
        r_sw.update()
        t_sw.update()

        # Access properties too, similar to production use.
        left = l_sw.value
        right = r_sw.value
        trigger = t_sw.value

        await asyncio.sleep(0.01)

################################################################################
# Force occasional GC while everything is running

async def gc_task():
    while test_running:
        await asyncio.sleep(1)
        gc.collect()

################################################################################
# Same server.poll() behavior as production code

async def server_poll_task():
    while test_running:
        try:
            server.poll()
        except Exception as e:
            print("Server poll:", e)
        await asyncio.sleep(0)

################################################################################
# SD latency test

async def test_sd_block(block_size):
    total_reads = 0
    total_bytes = 0
    total_time = 0
    worst = 0
    worst_read = 0
    worst_pass = 0
    over_2ms = 0
    over_5ms = 0
    over_10ms = 0
    over_20ms = 0
    over_50ms = 0

    print()
    print("----------------------------------------")
    print("Block size:", block_size, "bytes")
    print("----------------------------------------")

    for p in range(1, PASSES + 1):
        gc.collect()

        buf = bytearray(block_size)
        f = open(TEST_FILE, "rb")

        read_num = 0
        pass_total = 0
        pass_bytes = 0
        pass_worst = 0

        print("Pass:", p)

        while True:
            start = time.monotonic_ns()
            n = f.readinto(buf)
            elapsed = (time.monotonic_ns() - start) / 1000000

            if not n:
                break

            read_num += 1
            total_reads += 1
            total_bytes += n
            total_time += elapsed
            pass_total += elapsed
            pass_bytes += n

            if elapsed > pass_worst:
                pass_worst = elapsed

            if elapsed > worst:
                worst = elapsed
                worst_read = read_num
                worst_pass = p

            if elapsed > 2:
                over_2ms += 1
            if elapsed > 5:
                over_5ms += 1
            if elapsed > 10:
                over_10ms += 1
            if elapsed > 20:
                over_20ms += 1
            if elapsed > 50:
                over_50ms += 1

            if elapsed > 20:
                print("  SLOW:", read_num, round(elapsed, 3), "ms")

            await asyncio.sleep(0)

        f.close()

        print("  Reads:", read_num)
        print("  Bytes:", pass_bytes)
        print("  Average:", round(pass_total / read_num, 3), "ms")
        print("  Worst:", round(pass_worst, 3), "ms")

    return {
        "block": block_size,
        "reads": total_reads,
        "bytes": total_bytes,
        "average": total_time / total_reads,
        "worst": worst,
        "worst_read": worst_read,
        "worst_pass": worst_pass,
        "over_2": over_2ms,
        "over_5": over_5ms,
        "over_10": over_10ms,
        "over_20": over_20ms,
        "over_50": over_50ms
    }

################################################################################

async def sd_test_task():
    global test_running

    print()
    print("========================================")
    print("FULL FELLER ASYNC SD STRESS TEST")
    print("========================================")
    print("File:", TEST_FILE)
    print("Passes:", PASSES)
    print("I2S audio: ON")
    print("Flash audio loop: ON")
    print("Feller servo: ON")
    print("Tree servo: ON")
    print("Switch debouncers: ON")
    print("Volume pot: ON")
    print("Garbage collection: ON")
    print("WiFi:", web)
    print("Web server:", web)
    print("========================================")

    results = []

    for block_size in BLOCK_SIZES:
        results.append(await test_sd_block(block_size))

    test_running = False

    print()
    print("========================================")
    print("COMPLETE SD LATENCY REPORT")
    print("========================================")

    for r in results:
        print("Block size:", r["block"], "bytes")
        print("  Total reads:", r["reads"])
        print("  Total bytes:", r["bytes"])
        print("  Average read:", round(r["average"], 3), "ms")
        print("  Worst read:", round(r["worst"], 3), "ms")
        print("  Worst location: pass", r["worst_pass"], "read", r["worst_read"])
        print("  Reads > 2ms:", r["over_2"])
        print("  Reads > 5ms:", r["over_5"])
        print("  Reads > 10ms:", r["over_10"])
        print("  Reads > 20ms:", r["over_20"])
        print("  Reads > 50ms:", r["over_50"])
        print()

    print("========================================")
    print("SUMMARY")
    print("========================================")

    for r in results:
        print(r["block"], "bytes:",
              "avg", round(r["average"], 3), "ms,",
              "worst", round(r["worst"], 3), "ms,",
              ">2ms", r["over_2"],
              ">5ms", r["over_5"],
              ">10ms", r["over_10"],
              ">20ms", r["over_20"],
              ">50ms", r["over_50"])

    print("========================================")
    print("TEST COMPLETE")
    print("========================================")

################################################################################

async def main():
    tasks = [
        sd_test_task(),
        servo_task(),
        volume_task(),
        switch_task(),
        gc_task()
    ]

    if web:
        tasks.append(server_poll_task())

    await asyncio.gather(*tasks)

################################################################################

try:
    asyncio.run(main())
except KeyboardInterrupt:
    test_running = False

mix.voice[0].stop()
w0.deinit()

f_s.fraction = None
t_s.fraction = None

gc.collect()

print("Final free memory:", gc.mem_free())