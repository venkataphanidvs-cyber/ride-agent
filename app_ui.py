import streamlit as st
from app import get_weather, get_ride_suggestions

st.set_page_config(page_title="Ride Agent", layout="centered")

st.title("🛵 Smart Ride Agent")

city = st.text_input("Enter your city")
mood = st.text_input("How are you feeling?")

parking_pref = st.selectbox(
    "Parking preference",
    ["any", "easy", "moderate"]
)

if st.button("Get Ride Suggestions"):
    if city and mood:
        weather, city_time = get_weather(city)
        result = get_ride_suggestions(
            mood,
            weather,
            city,
            city_time,
            parking_pref
        )

        st.subheader("🚀 Ride Suggestions")
        lines = result.split("\n")

        for line in lines:
            if "." in line:
                parts = line.split(" - ")

                place = parts[0].split(".")[1].strip()
                distance = parts[1]
                reason = parts[2]
                cafe = parts[3].replace("Cafe: ", "")
                parking = parts[4].replace("Parking: ", "")

                with st.container():
                    st.markdown(f"### 📍 {place}")
                    st.write(f"🚗 Distance: {distance}")
                    st.write(f"✨ {reason}")
                    st.write(f"☕ Cafe: {cafe}")

                    # Highlight parking
                    if "Easy" in parking:
                        st.success(f"🅿️ Parking: {parking}")
                    elif "Moderate" in parking:
                        st.warning(f"🅿️ Parking: {parking}")
                    else:
                        st.error(f"🅿️ Parking: {parking}")

                    st.divider()
            else:
                st.warning("Please enter both city and mood")