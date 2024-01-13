import vlc
import time

movie1 = ("/home/pi/Videos/oldmovie.mp4")
movie2 = ("/home/pi/Videos/commercial.mp4")

# creating vlc media player object
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()
media_player.audio_set_volume(50)

for _ in range(3):
    # set media and play
    media = vlc.Media(movie1)
    media_player.set_media(media)
    media_player.play()
    time.sleep(100)
    media_player.pause()

    # set media and play
    media = vlc.Media(movie2)
    media_player.set_media(media)
    media_player.play()
    time.sleep(100)
    media_player.pause()

media_player.stop()