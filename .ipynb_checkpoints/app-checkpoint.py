import os
import wikipedia
import webbrowser
import datetime
import speech_recognition as sr
import pyttsx3
import requests
from flask_sqlalchemy import SQLAlchemy
#from app import db, app
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50))

    __table_args__ = {"extend_existing": True}

# ✅ Fix: Initialize DB inside the app context
with app.app_context():
    db.drop_all()
    db.create_all()

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50))


@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({"response": "No text provided."})

    engine.say(text)
    engine.runAndWait()
    return jsonify({"response": "Speaking..."})

@app.route('/listen', methods=['GET'])

def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio, language="en-US")
            print(f"User said: {command}")
            return command.lower()
    except OSError:
        print("Microphone not detected. Running in non-voice mode.")
        return input("Type your command: ").lower()
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Error connecting to speech recognition service."

    try:
        command = recognizer.recognize_google(audio, language="en-US")
        return jsonify({"response": command})
    except:
        return jsonify({"response": "Sorry, I couldn't understand."})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_wikipedia', methods=['POST'])
def search_wikipedia(query):
    try:
        speak("Searching Wikipedia...")
        query = query.replace("wikipedia", "").strip()
        if not query:
            speak("Please provide a search term for Wikipedia.")
            return
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        print(results)
        speak(results)
    except wikipedia.exceptions.DisambiguationError as e:
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("No matching Wikipedia page found.")
    except Exception as e:
        speak("An error occurred while searching Wikipedia.")
        print(e)


@app.route('/open_website', methods=['POST'])
def open_website():
    data = request.get_json()
    url = data.get('url')
    try:
        webbrowser.open(url)
        return jsonify({"response": f"Opened {url}"})
    except Exception as e:
        return jsonify({"response": f"Error: {e}"})

@app.route('/tell_time', methods=['GET'])
def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return jsonify({"response": f"The current time is {current_time}"})

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    city = data.get('city')
    if not city:
        return jsonify({"response": "Please enter a city name."})

    API_KEY = "bd5e378503939ddaee76f12ad7a97608"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url).json()
        temp = response["main"]["temp"]
        weather_desc = response["weather"][0]["description"]
        result = f"The temperature in {city} is {temp}°C with {weather_desc}."
        return jsonify({"response": result})
    except Exception:
        return jsonify({"response": "Couldn't fetch weather data. Try another city."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

