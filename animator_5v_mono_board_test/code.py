# This code was used to debug the animator 5v mono board, a low cost board for inexpensive products.
# It does not have a sd slot which limits audio files to mp3s and the limited storage available on the pico
from analogio import AnalogIn
import microcontroller
import board
import digitalio
import audiobusio
import audiomixer
import audiomp3
import time
import gc
import os


def gc_col(collection_point):
    gc.collect()
    start_mem = gc.mem_free()
    print("Point " + collection_point +
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
    
def upd_vol(seconds):
    volume = a_in.value / 65536
    mix.voice[0].level = volume
    time.sleep(seconds)


gc_col("Imports gc, files")

################################################################################
# Setup hardware

# Setup pin for vol on 5v aud board
a_in = AnalogIn(board.A2)

# setup pin for audio enable 21 on 5v aud board 22 on tiny 28 on large
aud_en = digitalio.DigitalInOut(board.GP21)
aud_en.direction = digitalio.Direction.OUTPUT
aud_en.value = True

# setup i2s audio
bclk = board.GP18  # BCLK on MAX98357A
lrc = board.GP19  # LRC on MAX98357A
din = board.GP20  # DIN on MAX98357A

aud = audiobusio.I2SOut(bit_clock=bclk, word_select=lrc, data=din)

# Setup the mixer to play wav files
mix = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=2,
                       bits_per_sample=16, samples_signed=True, buffer_size=8192)
aud.play(mix)

upd_vol(.1)

w0 = audiomp3.MP3Decoder(open("wav/taps.mp3", "rb"))

mix.voice[0].play(w0, loop=False)
while mix.voice[0].playing:
    upd_vol(.1)
    pass
