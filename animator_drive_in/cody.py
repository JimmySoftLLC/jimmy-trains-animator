import vlc
import time
import board
import digitalio
from adafruit_debouncer import Debouncer
import neopixel_spi
from rainbowio import colorwheel

# Setup the switches, there are two the Left and Right
switch_io_1 = digitalio.DigitalInOut(board.D17)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP
left_switch = Debouncer(switch_io_1)

switch_io_2 = digitalio.DigitalInOut(board.D27)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP
right_switch = Debouncer(switch_io_2)

num_pixels_rgb=40
ledStripRGB = neopixel_spi.NeoPixel_SPI(board.SPI(), num_pixels_rgb, brightness=1.0, auto_write=False)

# creating vlc media player object
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()
  
movie1 = ("/home/pi/Videos/oldmovie.mp4")
movie2 = ("/home/pi/Videos/commercial.mp4")

movie_playing = False

def play_movie_1():
    media = vlc.Media(movie1)
    media_player.set_media(media)
    media_player.audio_set_volume(50)
    play_movie()
    
def play_movie_2():
    media = vlc.Media(movie2)
    media_player.set_media(media)
    media_player.audio_set_volume(50)
    play_movie()
    
def pause_movie():
    global movie_playing
    media_player.pause()
    movie_playing = False
    
def play_movie():
    global movie_playing
    media_player.play()
    movie_playing = True

def rainbow(speed,duration):
    startTime = time.monotonic()
    for j in range(0,255,1):
        for i in range(num_pixels_rgb):
            pixel_index = (i * 256 // num_pixels_rgb) + j
            ledStripRGB[i] = colorwheel(pixel_index & 255)
        ledStripRGB.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
    for j in reversed(range(0,255,1)):
        for i in range(num_pixels_rgb):
            pixel_index = (i * 256 // num_pixels_rgb) + j
            ledStripRGB[i] = colorwheel(pixel_index & 255)
        ledStripRGB.show()
        time.sleep(speed)
        timeElasped = time.monotonic()-startTime
        if timeElasped > duration:
            return
  
while True:
    left_switch.update()
    right_switch.update()
    if left_switch.fell:
        print ("left fell")
        play_movie_1()
        
    if right_switch.fell:
        print ("right fell")
        if movie_playing:
            pause_movie()
        else:
            play_movie()
            rainbow(.005,5)
    pass

media_player.stop()      

