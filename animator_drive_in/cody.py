import RPi.GPIO as GPIO
import os
import sys
import vlc
import time

movie1 = ("/home/pi/Videos/oldmovie.mp4")
movie2 = ("/home/pi/Videos/Feller.mp4")
movie3 = ("/home/pi/Videos/jimmytrains.jpg")
movie4 = ("/home/pi/Videos/grand_central.mp4")
movie5 = ("/home/pi/Videos/commercial.mp4")

# creating vlc media player object
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()

for _ in range(3):
    # set media and play
    media = vlc.Media(movie1)
    media_player.set_media(media)
    media_player.play()
    time.sleep(2)
    media_player.pause()

    # set media and play
    media = vlc.Media(movie2)
    media_player.set_media(media)
    media_player.play()
    time.sleep(5)
    media_player.pause()

    # set media and play
    media = vlc.Media(movie3)
    media_player.set_media(media)
    time.sleep(2)
    media_player.pause()

    # set media and play
    media = vlc.Media(movie4)
    media_player.set_media(media)
    media_player.play()
    time.sleep(2)
    media_player.pause()

    # set media and play
    media = vlc.Media(movie5)
    media_player.set_media(media)
    media_player.play()
    time.sleep(10)
    media_player.pause()

media_player.stop()