import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import datetime
import requests
import json

try:
    with open("memory.json", "r") as f:
        previous_places = json.load(f)
except:
    previous_places = []

# Load API key from .env file
load_dotenv()

# Get API key (priority: Streamlit → fallback: .env)
try:
    OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
    WEATHER_KEY = st.secrets["WEATHER_API_KEY"]
except:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    WEATHER_KEY = os.getenv("WEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)
def get_weather(city):
    api_key = WEATHER_KEY

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url).json()

    temp = response["main"]["temp"]
    condition = response["weather"][0]["description"]
    timezone_offset = response["timezone"]
    utc_time = datetime.datetime.now(datetime.UTC)
    local_time = utc_time + datetime.timedelta(seconds=timezone_offset)
    
    formatted_time = local_time.strftime("%H:%M")

    return f"{temp}°C, {condition}", formatted_time

def get_ride_suggestions(user_input, weather, city, city_time, parking_pref):
    global previous_places

    
    low_energy_moods = ["angry", "tired", "sad", "exhausted", "lazy"]
    is_low_energy = user_input.lower() in low_energy_moods

    prompt = f"""
    You are a smart ride suggestion agent for {city}.

    Current local time in {city}: {city_time}
    Weather: {weather}
    User mood: {user_input}

    You MUST NOT suggest any of these places: {previous_places}.
    If a place is in this list, do not include it under any circumstances.

    Rules:
    - If hot -> suggest short or night rides
    - If rainy -> avoid long rides, suggest cafes
    - If pleasant -> suggest scenic rides

    Suggest 3 ride destinations.

    For each include:
    - Name
    - Distance (approx)
    - Why it's good based on time + weather
    - 1 nearby cafe or tea stop
    - Parking availability (Easy / Moderate / Difficult)

    Be realistic based on location type.
    Keep it short and fun.

    Return results as JSON ONLY.

    Format:
    [
    {{
        "place": "...",
        "distance": "...",
        "reason": "...",
        "cafe": "...",
        "parking": "Easy/Moderate/Difficult"
    }}
    ]

    STRICT RULES:
    - No text outside JSON
    - No HTML
    - No markdown
    - No numbering
    - Only valid JSON array
    - DO NOT add explanations
    """

    if is_low_energy:
        prompt += """
    If the user seems low energy:
    - Suggest staying home as the FIRST option
    - Suggest rest or relaxing
    - Then give only 1-2 short nearby options
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt        
    )

    result = response.output_text.strip()
    return result
