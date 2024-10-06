# install with   pip install gtts pydub

from gtts import gTTS
from pydub import AudioSegment

# The text you want to convert to speech
text = "Hello, how are you?"

# Convert the text to speech in English and save as MP3
tts = gTTS(text=text, lang='en')
tts.save("speech.mp3")

# Load the MP3 file using pydub and convert it to WAV
audio = AudioSegment.from_mp3("speech.mp3")
audio.export("speech.wav", format="wav")

print("Speech saved as speech.wav")