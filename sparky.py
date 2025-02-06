import streamlit as st
import speech_recognition as sr
import cohere
import os
import webbrowser
import datetime
from gtts import gTTS
import pygame
import threading
import time

# Initialize Cohere API
COHERE_API_KEY = "oJYNDT2A9wtL7Hs78AypiBkJJyqmPDZYRbrcPguG"
co = cohere.Client(COHERE_API_KEY)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Ensure unique filenames for responses
audio_folder = "audio_files"
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_command" not in st.session_state:
    st.session_state.last_command = ""
if "command_executed" not in st.session_state:
    st.session_state.command_executed = False
if "stop_audio" not in st.session_state:
    st.session_state.stop_audio = False

def chat(query):
    """Generate response using Cohere AI."""
    try:
        chat_history = "\n".join(st.session_state.messages) + f"\nUser: {query}\nSPARKY: "
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=chat_history,
            max_tokens=150,
            temperature=0.7,
            stop_sequences=["User:"]
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def say(text):
    """Convert text to speech and play it using threading."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    mp3_filename = os.path.join(audio_folder, f"response_{timestamp}.mp3")

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(mp3_filename)

        def play_audio():
            pygame.mixer.music.load(mp3_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if st.session_state.stop_audio:
                    pygame.mixer.music.stop()
                    break
            # Clean up the audio file after playback
            if os.path.exists(mp3_filename):
                os.remove(mp3_filename)

        # Use threading to avoid blocking the main thread
        audio_thread = threading.Thread(target=play_audio)
        audio_thread.start()
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")

def stop_audio():
    """Stop audio playback."""
    st.session_state.stop_audio = True
    pygame.mixer.music.stop()

def takeCommand():
    """Capture voice input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        try:
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio, language="en-in")
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Sorry, there was an issue with the speech recognition service."

def execute_command(user_input):
    """Execute user commands."""
    response = ""
    if "open youtube" in user_input.lower():
        response = "Opening YouTube..."
        webbrowser.open("https://www.youtube.com")
    elif "open google" in user_input.lower():
        response = "Opening Google..."
        webbrowser.open("https://www.google.com")
    elif "open notepad" in user_input.lower():
        response = "Opening Notepad..."
        os.system("notepad")
    elif "the time" in user_input.lower():
        now = datetime.datetime.now().strftime("%H:%M")
        response = f"The current time is {now}."
    elif "reset chat" in user_input.lower():
        st.session_state.messages = []
        response = "Chat history cleared."
    else:
        response = chat(user_input)
    return response
def execute_command(user_input):
    """Execute user commands."""
    response = ""
    user_input_lower = user_input.lower()
    
    if "open youtube" in user_input_lower:
        response = "Opening YouTube..."
        webbrowser.open("https://www.youtube.com")
    
    elif "open google" in user_input_lower:
        response = "Opening Google..."
        webbrowser.open("https://www.google.com")
    
    elif "open notepad" in user_input_lower:
        response = "Opening Notepad..."
        os.system("notepad")
    
    elif "the time" in user_input_lower:
        now = datetime.datetime.now().strftime("%H:%M")
        response = f"The current time is {now}."
    
    elif any(word in user_input_lower for word in ["today's date", "current date", "what's the date"]):
        today = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today's date is {today}."
        st.session_state.messages = []  # Clear chat history
    
    elif "reset chat" in user_input_lower:
        st.session_state.messages = []
        response = "Chat history cleared."
    
    else:
        response = chat(user_input)
    
    return response
# Streamlit UI
st.title("🎙️ SPARKY AI Voice Assistant")

# User input field
user_input = st.text_input("Type your command or use voice:", key="input_field")

# Buttons for speaking and stopping response
col1, col2 = st.columns(2)
with col1:
    if st.button("🎤 Speak"):
        user_input = takeCommand()
with col2:
    if st.button("🛑 Stop Response"):
        stop_audio()

# Display response below the input field
response_display = st.empty()

# Process input only if new and not already executing
if user_input and user_input != st.session_state.last_command:
    st.session_state.last_command = user_input
    st.session_state.messages.append(f"**You:** {user_input}")

    with st.spinner("Processing..."):
        response = execute_command(user_input)
        response_display.write(f"**SPARKY:** {response}")
        say(response)

# Reset command flag if reset chat is triggered
if "reset chat" in user_input.lower():
    st.session_state.command_executed = False