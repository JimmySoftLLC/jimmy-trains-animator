import time
import board
import pulseio
import digitalio

PIN = board.GP2

ACTIVE_LOW = True
IDLE_STATE = False
MAXLEN = 1000

CAPTURE_S = 0.10
MIN_DURS = 10

# enable pull-up once
dio = digitalio.DigitalInOut(PIN)
dio.direction = digitalio.Direction.INPUT
dio.pull = digitalio.Pull.UP
dio.deinit()

p = pulseio.PulseIn(PIN, maxlen=MAXLEN, idle_state=IDLE_STATE)
p.pause()

print("GP2 PWM decoder (stable phase)")
print("ACTIVE_LOW =", ACTIVE_LOW, "IDLE_STATE =", IDLE_STATE)
print("---")

while True:
    p.clear()
    p.resume()
    time.sleep(CAPTURE_S)
    p.pause()

    n = len(p)
    if n < MIN_DURS:
        print("Insufficient pulses:", n)
        time.sleep(0.2)
        continue

    data = [p[i] for i in range(n)]
    if len(data) % 2:
        data = data[1:]

    even_sum = 0
    odd_sum = 0
    total_sum = 0
    periods = []

    for i in range(0, len(data), 2):
        a = data[i]
        b = data[i + 1]
        even_sum += a
        odd_sum += b
        total_sum += (a + b)
        periods.append(a + b)

    if total_sum == 0:
        print("Invalid capture")
        time.sleep(0.2)
        continue

    duty_even = even_sum / total_sum
    duty_odd = odd_sum / total_sum

    # Always pick the smaller one to avoid phase flip
    duty_raw = duty_even if duty_even <= duty_odd else duty_odd

    duty = (1.0 - duty_raw) if ACTIVE_LOW else duty_raw

    avg_period = sum(periods) / len(periods)
    freq = 1_000_000 / avg_period if avg_period > 0 else 0

    print(
        "durations:", n,
        "| duty_raw:", round(duty_raw, 4),
        "| duty:", round(duty, 4),
        "| freq_hz:", int(freq)
    )

    time.sleep(0.2)

