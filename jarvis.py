import speech_recognition as sr
import datetime
import os
import sys
import time
from gtts import gTTS
import pygame
import uuid
import pyautogui
import threading
import subprocess
import tkinter as tk
import webbrowser   # <-- ADDED (required for search)

# ================= GLOBAL STATES =================
SLEEP_MODE = False
MUTE_MODE = False
HUD_STATUS = "Wake word"
HUD_ALPHA = 0.0
LAST_IDLE_TIME = time.time()

INACTIVITY_TIMEOUT = 4   # seconds
FADE_SPEED = 0.04

# ================= INVISIBLE HUD =================
def hud_thread():
    global HUD_STATUS, HUD_ALPHA, LAST_IDLE_TIME

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.geometry("260x30+20+20")
    root.configure(bg="black")
    root.attributes("-alpha", 0.0)

    label = tk.Label(
        root,
        text="JARVIS · Wake word",
        fg="white",
        bg="black",
        font=("Segoe UI", 10)
    )
    label.pack(anchor="w", padx=6)

    def update():
        global HUD_ALPHA, LAST_IDLE_TIME

        label.config(text=f"JARVIS · {HUD_STATUS}")

        if HUD_STATUS == "Wake word":
            if HUD_ALPHA > 0 and LAST_IDLE_TIME is None:
                LAST_IDLE_TIME = time.time()
        else:
            LAST_IDLE_TIME = None

        if HUD_STATUS == "Wake word" and LAST_IDLE_TIME:
            idle_time = time.time() - LAST_IDLE_TIME
            if idle_time > INACTIVITY_TIMEOUT:
                HUD_ALPHA = max(0.0, HUD_ALPHA - FADE_SPEED)
            else:
                HUD_ALPHA = min(0.85, HUD_ALPHA + FADE_SPEED)
        else:
            HUD_ALPHA = min(0.85, HUD_ALPHA + FADE_SPEED)

        root.attributes("-alpha", HUD_ALPHA)
        root.after(40, update)

    update()
    root.mainloop()

threading.Thread(target=hud_thread, daemon=True).start()

# ================= AUDIO =================
pygame.mixer.init()

WAKE_SOUND_PATH = r"C:\Jarvis\sounds\wake.wav"
wake_sound = pygame.mixer.Sound(WAKE_SOUND_PATH) if os.path.exists(WAKE_SOUND_PATH) else None

def play_wake_sound():
    if wake_sound:
        wake_sound.play()

def speak(text):
    global HUD_STATUS
    if MUTE_MODE:
        return

    HUD_STATUS = "Processing"
    print("Jarvis:", text)

    filename = f"voice_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang="en").save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    os.remove(filename)

    HUD_STATUS = "Done"
    time.sleep(1)
    HUD_STATUS = "Wake word"

# ================= SPEECH =================
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8

def listen_for_wake():
    global HUD_STATUS
    HUD_STATUS = "Wake word"

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, 0.4)
        try:
            audio = recognizer.listen(source, phrase_time_limit=3)
            return recognizer.recognize_google(audio).lower()
        except:
            return ""

def listen_for_command():
    global HUD_STATUS
    HUD_STATUS = "Listening"

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            HUD_STATUS = "Processing"
            return recognizer.recognize_google(audio).lower()
        except sr.WaitTimeoutError:
            HUD_STATUS = "Wake word"
            return ""
        except:
            HUD_STATUS = "Wake word"
            return ""

# ================= MEDIA =================
def play_pause(): pyautogui.press("playpause")
def next_track(): pyautogui.press("nexttrack")
def previous_track(): pyautogui.press("prevtrack")
def volume_up(): pyautogui.press("volumeup")
def volume_down(): pyautogui.press("volumedown")
def mute_volume(): pyautogui.press("volumemute")

# ================= APP CONTROL =================
def open_app(command):
    if "chrome" in command:
        speak("Opening Chrome")
        os.startfile("chrome")
    elif "spotify" in command:
        speak("Opening Spotify")
        os.startfile("spotify")
    elif "code" in command:
        speak("Opening Visual Studio Code")
        os.startfile(
            r"C:\Users\munaw\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk"
        )
    else:
        speak("I don't know that application")

def close_app(command):
    if "chrome" in command:
        subprocess.call("taskkill /f /im chrome.exe", shell=True)
        speak("Chrome closed")
    elif "spotify" in command:
        subprocess.call("taskkill /f /im spotify.exe", shell=True)
        speak("Spotify closed")
    elif "code" in command:
        subprocess.call("taskkill /f /im code.exe", shell=True)
        speak("Visual Studio Code closed")
    else:
        speak("I can't close that")

# ================= SHUTDOWN =================
def shutdown_system():
    subprocess.call("shutdown /s /t 10", shell=True)

# ================= STARTUP =================
speak("System Online")

# ================= MAIN LOOP =================
while True:
    wake = listen_for_wake()

    if "jarvis" in wake:
        play_wake_sound()

        command = listen_for_command()
        if not command:
            continue

        if command.startswith("open"):
            open_app(command)

        elif command.startswith("close"):
            close_app(command)

        # 🔍 GOOGLE SEARCH (ADDED)
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
            speak("Searching Google")
            webbrowser.open(f"https://www.google.com/search?q={query}")

        elif "search for" in command:
            query = command.replace("search for", "").strip()
            speak("Searching Google")
            webbrowser.open(f"https://www.google.com/search?q={query}")

        # ▶️ YOUTUBE SEARCH (ADDED)
        elif "search youtube for" in command or "play on youtube" in command:
            query = command.replace("search youtube for", "").replace("play on youtube", "").strip()
            speak("Searching YouTube")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

        elif "play" in command or "pause" in command:
            play_pause()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "next" in command:
            next_track()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "previous" in command:
            previous_track()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "volume up" in command:
            volume_up()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "volume down" in command:
            volume_down()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "mute" in command:
            mute_volume()
            HUD_STATUS = "Done"
            time.sleep(1)
            HUD_STATUS = "Wake word"

        elif "time" in command:
            speak(datetime.datetime.now().strftime("The time is %I:%M %p"))

        elif "date" in command:
            speak(datetime.datetime.now().strftime("Today is %A, %d %B %Y"))

        elif "shutdown" in command:
            speak("Shutting down")
            time.sleep(0.5)
            shutdown_system()
            sys.exit()

        elif "exit" in command or "stop" in command:
            speak("Goodbye")
            sys.exit()
