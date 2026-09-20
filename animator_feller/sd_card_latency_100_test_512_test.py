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

TEST_FILE = "/sd/feller_sounds/sounds_train.wav"
BLOCK_SIZE = 512
PASSES = 100

print("Setting up SD card...")

spi = busio.SPI(sck, si, so)
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("SD card mounted")
print("Free memory:", gc.mem_free())

def test_sd_latency(file_name):
    total_reads = 0
    total_bytes = 0
    total_time = 0
    worst = 0
    worst_read = 0
    worst_pass = 0

    # Histogram buckets
    under_1 = 0
    from_1_to_2 = 0
    from_2_to_3 = 0
    from_3_to_4 = 0
    from_4_to_5 = 0
    from_5_to_6 = 0
    from_6_to_7 = 0
    from_7_to_8 = 0
    from_8_to_10 = 0
    from_10_to_20 = 0
    from_20_to_50 = 0
    over_50 = 0

    print("\n========================================")
    print("512 BYTE SD CARD LONG LATENCY TEST")
    print("========================================")
    print("File:", file_name)
    print("Block size:", BLOCK_SIZE)
    print("Passes:", PASSES)
    print("========================================")

    buf = bytearray(BLOCK_SIZE)

    for p in range(1, PASSES + 1):
        gc.collect()
        f = open(file_name, "rb")
        read_num = 0
        pass_total = 0
        pass_worst = 0

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

            if elapsed > pass_worst:
                pass_worst = elapsed

            if elapsed > worst:
                worst = elapsed
                worst_read = read_num
                worst_pass = p

            if elapsed < 1:
                under_1 += 1
            elif elapsed < 2:
                from_1_to_2 += 1
            elif elapsed < 3:
                from_2_to_3 += 1
            elif elapsed < 4:
                from_3_to_4 += 1
            elif elapsed < 5:
                from_4_to_5 += 1
            elif elapsed < 6:
                from_5_to_6 += 1
            elif elapsed < 7:
                from_6_to_7 += 1
            elif elapsed < 8:
                from_7_to_8 += 1
            elif elapsed < 10:
                from_8_to_10 += 1
            elif elapsed < 20:
                from_10_to_20 += 1
            elif elapsed < 50:
                from_20_to_50 += 1
            else:
                over_50 += 1

            if elapsed >= 10:
                print("SLOW: pass", p, "read", read_num, round(elapsed, 3), "ms")

        f.close()

        print("Pass:", p,
              "avg:", round(pass_total / read_num, 3), "ms",
              "worst:", round(pass_worst, 3), "ms")

    print("\n========================================")
    print("FINAL RESULTS")
    print("========================================")
    print("Total passes:", PASSES)
    print("Total reads:", total_reads)
    print("Total bytes:", total_bytes)
    print("Average read:", round(total_time / total_reads, 3), "ms")
    print("Worst read:", round(worst, 3), "ms")
    print("Worst location: pass", worst_pass, "read", worst_read)

    print("\n========================================")
    print("LATENCY HISTOGRAM")
    print("========================================")
    print("< 1 ms:     ", under_1)
    print("1 - <2 ms:  ", from_1_to_2)
    print("2 - <3 ms:  ", from_2_to_3)
    print("3 - <4 ms:  ", from_3_to_4)
    print("4 - <5 ms:  ", from_4_to_5)
    print("5 - <6 ms:  ", from_5_to_6)
    print("6 - <7 ms:  ", from_6_to_7)
    print("7 - <8 ms:  ", from_7_to_8)
    print("8 - <10 ms: ", from_8_to_10)
    print("10 - <20 ms:", from_10_to_20)
    print("20 - <50 ms:", from_20_to_50)
    print(">= 50 ms:   ", over_50)

    print("\n========================================")
    print("PERCENTAGES")
    print("========================================")
    print("< 1 ms:     ", round(under_1 * 100 / total_reads, 4), "%")
    print("< 2 ms:     ", round((under_1 + from_1_to_2) * 100 / total_reads, 4), "%")
    print("< 5 ms:     ", round((under_1 + from_1_to_2 + from_2_to_3 + from_3_to_4 + from_4_to_5) * 100 / total_reads, 4), "%")
    print("< 10 ms:    ", round((under_1 + from_1_to_2 + from_2_to_3 + from_3_to_4 + from_4_to_5 + from_5_to_6 + from_6_to_7 + from_7_to_8 + from_8_to_10) * 100 / total_reads, 4), "%")

    print("========================================")
    print("TEST COMPLETE")
    print("========================================")

test_sd_latency(TEST_FILE)