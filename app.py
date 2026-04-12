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
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
WEATHER_KEY = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")

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
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    prompt = f"""
You are a smart ride suggestion agent for {city}.

Current local time in {city}: {city_time}
Weather: {weather}
User mood: {user_input}


You MUST NOT suggest any of these places: {previous_places}.
If a place is in this list, do not include it under any circumstances.
Always suggest completely different places from the list above.

Rules:
- If hot → suggest short or night rides
- If rainy → avoid long rides, suggest cafes
- If pleasant → suggest scenic rides

Suggest 3 ride destinations.

For each include:
- Name
- Distance (approx)
- Why it's good based on time + weather
- 1 nearby cafe or tea stop
- Parking availability (Easy / Moderate / Difficult)

Be realistic based on location type.
Keep it short and fun.

Return results STRICTLY in ONE LINE per place.

Each line must follow EXACTLY this format:

1. Place Name - Distance - Reason - Cafe: Cafe Name - Parking: Easy / Moderate / Difficult (include short reason why)
2. Place Name - Distance - Reason - Cafe: Cafe Name - Parking: Easy / Moderate / Difficult (include short reason why)
3. Place Name - Distance - Reason - Cafe: Cafe Name - Parking: Easy / Moderate / Difficult (include short reason why)

DO NOT skip labels.
DO NOT change order.
DO NOT add extra lines.
"""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    result = response.output_text

    lines = result.split("\n")
    places = []
    filtered_output = []

    for line in lines:
        if "." in line:
            try:
                parts = line.split(" - ")

                place = parts[0].split(".")[1].strip()
                distance = parts[1]
                reason = parts[2]
                cafe = parts[3].replace("Cafe: ", "")
                parking = parts[4].replace("Parking: ", "")

                if place not in previous_places:
                    places.append(place)
                    filtered_output.append(line)

            except:
                pass

    if len(filtered_output) < 3:
        print("⚠️ Retrying for new places...")

        prompt += "\nDo NOT repeat any previously suggested places. Suggest completely new ones."

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        result = response.output_text

        lines = result.split("\n")
        filtered_output = []

        for line in lines:
            if "." in line:
                try:
                    place = line.split("-")[0].split(".")[1].strip()
                    if place not in previous_places:
                        filtered_output.append(line)
                        places.append(place)
                except:
                    pass

    if len(filtered_output) == 0:
        final_result = result   # fallback to raw output
    else:
        renumbered_output = []

        for i, line in enumerate(filtered_output, start=1):
            try:
                # remove old number
                content = line.split(".", 1)[1].strip()
                new_line = f"{i}. {content}"
                renumbered_output.append(new_line)
            except:
                renumbered_output.append(line)

        final_result = "\n".join(renumbered_output)

    # store memory
    previous_places.extend(places)
    with open("memory.json", "w") as f:
        json.dump(previous_places, f)

    return final_result

if __name__ == "__main__":
    city = input("Enter your city: ")
    user_input = input("How are you feeling? ")

    weather,city_time = get_weather(city)
    result = get_ride_suggestions(user_input, weather,city,city_time)

    print("\n🚀 Ride Suggestions:\n")
    print(result)