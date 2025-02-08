import os
import datetime
import wikipedia
import webbrowser
import speech_recognition as sr
import pyttsx3
import requests
import random
import threading
from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize Text-to-Speech
engine = pyttsx3.init()
def speak(text):
    def run_speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    thread = threading.Thread(target=run_speak)
    thread.start()


def get_time():
    return datetime.datetime.now().strftime("%I:%M %p")

def get_weather(city="Warsaw"):
    API_KEY = "your_openweather_api_key"  # Replace with your OpenWeather API Key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    
    if response.get("main"):
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        return f"The current temperature in {city} is {temp}°C with {desc}."
    else:
        return "Sorry, I couldn't fetch the weather."

def get_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Parallel lines have so much in common. It’s a shame they’ll never meet!",
        "What do you call a factory that makes good products? A satisfactory!"
    ]
    return random.choice(jokes)

def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Sorry, no Wikipedia page found."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    user_input = request.form.get("command").lower()
    
    if "time" in user_input:
        response = f"The current time is {get_time()}"
    elif "wikipedia" in user_input:
        search_query = user_input.replace("wikipedia", "").strip()
        response = search_wikipedia(search_query)
    elif "google" in user_input:
        webbrowser.open("https://www.google.com")
        response = "Opening Google."
    elif "weather" in user_input:
        response = get_weather()
    elif "joke" in user_input:
        response = get_joke()
    else:
        response = "Sorry, I don't understand that command."

    speak(response)
    return render_template('response.html', response=response)

if __name__ == "__main__":
    app.run(debug=True)
