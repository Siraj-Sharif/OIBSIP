import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # speed of speech
engine.setProperty('volume', 0.9)


def speak(text):
    """Convert text to speech"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """Listen for microphone input and return recognized text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (say 'stop' to exit)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError:
        speak("Speech service is down. Check your internet.")
        return ""


def process_command(command):
    """Execute actions based on keywords"""
    if not command:
        return

    # Exit condition
    if command in ["stop", "exit", "quit", "bye"]:
        speak("Goodbye!")
        return False  # signal to stop loop

    # Respond to hello
    if "hello" in command:
        speak("Hello! How can I help you today?")

    # Tell the time
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")

    # Tell the date
    elif "date" in command:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {today}")

    # Web search
    elif "search for" in command:
        # Extract query after "search for"
        query = command.split("search for", 1)[-1].strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching Google for {query}")
        else:
            speak("What should I search for?")

    # Fallback for unrecognized commands
    else:
        speak("I can say hello, tell the time or date, or search the web. Try 'search for cats'.")

    return True  # continue running


def main():
    speak("Voice assistant ready. Say a command.")
    while True:
        command = listen()
        should_continue = process_command(command)
        if should_continue is False:
            break


if __name__ == "__main__":
    main()