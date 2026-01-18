import time
import board
import pulseio
import digitalio
import asyncio
import neopixel

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789,_/.+-*"
assert len(ALPHABET) == 43

PINS = {"R": board.GP2, "G": board.GP3, "B": board.GP4}

IDLE_STATE = False
MAXLEN = 1200

CAPTURE_S = 0.02
MIN_DURS = 40

T01 = 0.2512
T12 = 0.3293
T23 = 0.4040

ALPHA = 0.20
WIN = 5
MIN_MAJ = 5

# NEW: tuple confirmation
CONFIRM_COUNT = 3   # winning tuple must repeat this many times before we emit

################################################################################
# Setup neo pixels

n_px = 1

# 16 on demo, 17 tiny, 10 on large, 13 on motor board motor4 pin
led = neopixel.NeoPixel(board.GP6, n_px)
led.auto_write = False
led.fill((0, 0, 20))
led.show()

def enable_pullup(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    d.deinit()

def duty_raw_from_pulsein(pulses: pulseio.PulseIn):
    n = len(pulses)
    if n < MIN_DURS:
        return None

    data = [pulses[i] for i in range(n)]
    if len(data) % 2:
        data = data[1:]

    even_sum = 0
    odd_sum = 0
    total_sum = 0
    for i in range(0, len(data), 2):
        a = data[i]
        b = data[i + 1]
        even_sum += a
        odd_sum += b
        total_sum += (a + b)

    if total_sum == 0:
        return None

    duty_even = even_sum / total_sum
    duty_odd  = odd_sum  / total_sum
    return duty_even if duty_even <= duty_odd else duty_odd

def duty_to_digit(d):
    if d < T01: return 0
    if d < T12: return 1
    if d < T23: return 2
    return 3

def rgb_digits_to_char(r, g, b):
    idx = r * 16 + g * 4 + b
    if idx >= len(ALPHABET):
        return None
    return ALPHABET[idx]

def majority_tuple(buf):
    counts = {}
    for t in buf:
        counts[t] = counts.get(t, 0) + 1
    best_t = None
    best_n = 0
    for t, n in counts.items():
        if n > best_n:
            best_t, best_n = t, n
    return best_t, best_n

latest = {"char": None, "digits": None, "votes": 0, "lat_ms": 0}
new_char_event = asyncio.Event()

async def decoder_task():
    for pin in PINS.values():
        enable_pullup(pin)

    pulseins = {}
    for k, pin in PINS.items():
        pi = pulseio.PulseIn(pin, maxlen=MAXLEN, idle_state=IDLE_STATE)
        pi.pause()
        pulseins[k] = pi

    filt = {"R": None, "G": None, "B": None}
    hist = []
    last_char = None
    last_emit_t = time.monotonic()

    # NEW: confirmation state
    candidate = None
    candidate_n = 0

    while True:
        # parallel capture
        for ch in ("R", "G", "B"):
            pulseins[ch].clear()
            pulseins[ch].resume()

        await asyncio.sleep(CAPTURE_S)

        for ch in ("R", "G", "B"):
            pulseins[ch].pause()

        digits = {}

        for ch in ("R", "G", "B"):
            d = duty_raw_from_pulsein(pulseins[ch])
            if d is None:
                digits = None
                break

            if filt[ch] is None:
                filt[ch] = d
            else:
                filt[ch] = ALPHA * d + (1.0 - ALPHA) * filt[ch]

            digits[ch] = duty_to_digit(filt[ch])

        if digits is None:
            await asyncio.sleep(0)
            continue

        t = (digits["R"], digits["G"], digits["B"])

        hist.append(t)
        if len(hist) > WIN:
            hist.pop(0)

        best_t, best_n = majority_tuple(hist)

        if best_n < MIN_MAJ:
            await asyncio.sleep(0)
            continue

        # Convert to char; ignore reserved combos silently
        ch_out = rgb_digits_to_char(*best_t)
        if ch_out is None:
            # reset confirmation when we hit a reserved/transient combo
            candidate = None
            candidate_n = 0
            await asyncio.sleep(0)
            continue

        # NEW: require the same best tuple to repeat CONFIRM_COUNT times
        if best_t != candidate:
            candidate = best_t
            candidate_n = 1
        else:
            candidate_n += 1

        if candidate_n < CONFIRM_COUNT:
            await asyncio.sleep(0)
            continue

        if ch_out != last_char:
            last_char = ch_out
            now = time.monotonic()
            lat_ms = int((now - last_emit_t) * 1000)
            last_emit_t = now

            latest["char"] = ch_out
            latest["digits"] = best_t
            latest["votes"] = best_n
            latest["lat_ms"] = lat_ms
            new_char_event.set()

        await asyncio.sleep(0)

async def consumer_task():
    while True:
        await new_char_event.wait()
        new_char_event.clear()

        # Keep your debug print
        print("CHAR:", latest["char"],
              "| digits:", latest["digits"],
              "| votes:", latest["votes"],
              "| latency_ms:", latest["lat_ms"])

        # Set NeoPixel using the PWM-inspired brightness values
        if latest["digits"] is not None:
            r_digit, g_digit, b_digit = latest["digits"]

            # Map digits 0–3 to your requested brightness levels
            brightness_map = [20, 40, 60, 80]   # 0→0, 1→20, 2→40, 3→80

            r_val = brightness_map[r_digit]
            g_val = brightness_map[g_digit]
            b_val = brightness_map[b_digit]

            # Apply to the pixel
            led[0] = (r_val, g_val, b_val)
            led.show()

            # Optional: confirm in console what we set
            print(f"NeoPixel updated → R:{r_val} G:{g_val} B:{b_val}")


async def main():
    asyncio.create_task(decoder_task())
    await consumer_task()

asyncio.run(main())
