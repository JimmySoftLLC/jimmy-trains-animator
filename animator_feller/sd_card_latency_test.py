import board
import busio
import sdcardio
import storage
import time
import gc

# SD card
sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5

# Use a reasonably large WAV file
TEST_FILE = "/sd/feller_sounds/sounds_train.wav"
PASSES = 5

print("Setting up SD card...")

spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("SD card mounted")
print("Free memory:", gc.mem_free())

def test_sd_block(file_name, block_size):
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
    print("\n----------------------------------------")
    print("Block size:", block_size, "bytes")
    print("----------------------------------------")
    for p in range(1, PASSES + 1):
        gc.collect()
        buf = bytearray(block_size)
        f = open(file_name, "rb")
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
            if elapsed > 10:
                print("  SLOW: read", read_num, round(elapsed, 3), "ms")
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

def test_sd_latency(file_name):
    print("\n========================================")
    print("SD CARD LATENCY TEST")
    print("========================================")
    print("File:", file_name)
    print("Passes per block size:", PASSES)
    print("Block sizes: 512, 1024, 2048, 4096")
    print("========================================")
    results = []
    for block_size in (512, 1024, 2048, 4096):
        results.append(test_sd_block(file_name, block_size))
    print("\n========================================")
    print("COMPLETE SD CARD LATENCY REPORT")
    print("========================================")
    print("File:", file_name)
    print("Passes per block size:", PASSES)
    print()
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

test_sd_latency(TEST_FILE)