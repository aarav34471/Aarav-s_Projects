import pyttsx3
import threading

def speak_text(text):
    engine = pyttsx3.init()
    text = str(text).strip()
    if text:
        engine.say(text)
        engine.runAndWait()