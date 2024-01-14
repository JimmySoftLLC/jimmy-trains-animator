import vlc
import time
import board
import digitalio
from adafruit_debouncer import Debouncer
import neopixel_spi
from rainbowio import colorwheel
import pwmio
from adafruit_motor import servo

# Setup the switches, there are two the Left and Right and two unused 3 and 4
switch_io_1 = digitalio.DigitalInOut(board.D17)
switch_io_1.direction = digitalio.Direction.INPUT
switch_io_1.pull = digitalio.Pull.UP

switch_io_2 = digitalio.DigitalInOut(board.D27)
switch_io_2.direction = digitalio.Direction.INPUT
switch_io_2.pull = digitalio.Pull.UP

switch_io_3 = digitalio.DigitalInOut(board.D22)
switch_io_3.direction = digitalio.Direction.INPUT
switch_io_3.pull = digitalio.Pull.UP

switch_io_4 = digitalio.DigitalInOut(board.D5)
switch_io_4.direction = digitalio.Direction.INPUT
switch_io_4.pull = digitalio.Pull.UP

left_switch = Debouncer(switch_io_1)
right_switch = Debouncer(switch_io_2)

# Setup the servo
m1_pwm = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50)
m2_pwm = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=50)
m3_pwm = pwmio.PWMOut(board.D23, duty_cycle=2 ** 15, frequency=50)
m4_pwm = pwmio.PWMOut(board.D24, duty_cycle=2 ** 15, frequency=50)
m5_pwm = pwmio.PWMOut(board.D25, duty_cycle=2 ** 15, frequency=50)
m6_pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=50)
m7_pwm = pwmio.PWMOut(board.D16, duty_cycle=2 ** 15, frequency=50)
m8_pwm = pwmio.PWMOut(board.D20, duty_cycle=2 ** 15, frequency=50)

m1_servo = servo.Servo(m1_pwm)
m2_servo = servo.Servo(m2_pwm)
m3_servo = servo.Servo(m3_pwm)
m4_servo = servo.Servo(m4_pwm)
m5_servo = servo.Servo(m5_pwm)
m6_servo = servo.Servo(m6_pwm)
m7_servo = servo.Servo(m7_pwm)
m8_servo = servo.Servo(m8_pwm)

m1_servo.angle = 180
m2_servo.angle = 180
m3_servo.angle = 180
m4_servo.angle = 180
m5_servo.angle = 180
m6_servo.angle = 180
m7_servo.angle = 180
m8_servo.angle = 180

# setup neopixels on spi GP10
num_pixels_rgb=40
ledStripRGB = neopixel_spi.NeoPixel_SPI(board.SPI(), num_pixels_rgb, brightness=1.0, auto_write=False)

# create vlc media player object for playing video, music etc
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
