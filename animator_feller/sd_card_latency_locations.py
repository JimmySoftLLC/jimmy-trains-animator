import board
import busio
import sdcardio
import storage
import time
import gc

sck = board.GP2
si = board.GP3
so = board.GP4
cs = board.GP5

TEST_FILE = "/sd/feller_sounds/sounds_train.wav"
BLOCK_SIZE = 512
PASSES = 10
SLOW_MS = 5

print("Setting up SD card...")

spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("SD card mounted")
print("Free memory:", gc.mem_free())

def test_sd_slow_locations(file_name):
    buf = bytearray(BLOCK_SIZE)
    all_slow = []

    print("\n========================================")
    print("SD SLOW READ LOCATION TEST")
    print("========================================")
    print("File:", file_name)
    print("Block size:", BLOCK_SIZE)
    print("Passes:", PASSES)
    print("Slow threshold:", SLOW_MS, "ms")
    print("========================================")

    for p in range(1, PASSES + 1):
        gc.collect()
        f = open(file_name, "rb")
        read_num = 0
        pass_slow = []
        pass_worst = 0

        while True:
            start = time.monotonic_ns()
            n = f.readinto(buf)
            elapsed = (time.monotonic_ns() - start) / 1000000

            if not n:
                break

            read_num += 1

            if elapsed > pass_worst:
                pass_worst = elapsed

            if elapsed >= SLOW_MS:
                pass_slow.append((read_num, elapsed))

        f.close()
        all_slow.append(pass_slow)

        print("\nPass:", p, "worst:", round(pass_worst, 3), "ms")
        print("Slow reads:", len(pass_slow))

        for read_num, elapsed in pass_slow:
            byte_pos = (read_num - 1) * BLOCK_SIZE
            print("  read:", read_num, "byte:", byte_pos, "time:", round(elapsed, 3), "ms")

    print("\n========================================")
    print("LOCATION COMPARISON")
    print("========================================")

    for p, slow_reads in enumerate(all_slow, 1):
        print("Pass", p, ":", end=" ")
        for read_num, elapsed in slow_reads:
            print(read_num, end=" ")
        print()

    print("========================================")
    print("TEST COMPLETE")
    print("========================================")

test_sd_slow_locations(TEST_FILE)