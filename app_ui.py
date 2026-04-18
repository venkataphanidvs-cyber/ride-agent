import streamlit as st
from app import get_weather, get_ride_suggestions
import json
import re

st.set_page_config(page_title="Ride Agent", layout="centered")

st.title("🛵 Smart Ride Agent")
st.markdown("""
<style>
.card {
    padding: 16px;
    border-radius: 16px;
    background-color: #111827;
    margin-bottom: 16px;
    border: 1px solid #374151;
}

.best {
    border: 2px solid #22c55e;
    background-color: #052e16;
}

.title {
    font-size: 20px;
    font-weight: 600;
}

.sub {
    color: #9ca3af;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

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

        

        try:
            data = json.loads(result)

            for idx, item in enumerate(data):
                def clean(text):
                    return re.sub(r"<[^>]+>", "", str(text))

                place = clean(item["place"])
                distance = clean(item["distance"])
                reason = clean(item["reason"])
                cafe = clean(item["cafe"])
                parking = clean(item["parking"])

                card_class = "card best" if idx == 0 else "card"

                if "Easy" in parking:
                    parking_color = "#22c55e"
                elif "Moderate" in parking:
                    parking_color = "#eab308"
                else:
                    parking_color = "#ef4444"

                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div class="title">📍 {place}</div>'
                    f'<div class="sub">🚗 {distance}</div>'
                    f'{reason}<br>'
                    f'☕ <b>{cafe}</b>'
                    f'<div style="color:{parking_color};">🅿️ <b>{parking}</b></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error("⚠️ Failed to parse response")
            st.text(result)