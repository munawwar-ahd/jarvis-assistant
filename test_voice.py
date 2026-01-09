import pyttsx3

engine = pyttsx3.init(driverName="sapi5")
voices = engine.getProperty("voices")

engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 180)

engine.say("This is a voice test.")
engine.runAndWait()
engine.stop()
