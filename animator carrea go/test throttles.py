import time
import board
import analogio

# ADC input on GP26 (A0)
throttle_adc = analogio.AnalogIn(board.A2)

# These are the approximate raw values you will get.
# You should measure and fine tune them on your setup.
RAW_MIN = 13500   # full press, about 0.68V
RAW_MAX = 51600   # released, about 2.60V

def read_throttle_percent():
    raw = throttle_adc.value

    # Clamp to expected range
    if raw < RAW_MIN:
        raw = RAW_MIN
    if raw > RAW_MAX:
        raw = RAW_MAX

    # Since released is higher voltage and pressed is lower,
    # invert so pressed = higher percent
    percent = (RAW_MAX - raw) / (RAW_MAX - RAW_MIN) * 100.0
    return raw, percent

while True:
    raw, percent = read_throttle_percent()
    print("Raw:", raw, "Throttle %:", round(percent, 1))
    time.sleep(0.1)