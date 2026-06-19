import requests
API_KEY="882fea5c3c85bceab8ef510837a547a1"
def get_weather(city):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url)

    data = response.json()

    if data.get("cod") != 200:
        return "❌ City not found"

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    desc = data["weather"][0]["description"]

    return f"""
🌤 Weather Report

📍 City: {city}
🌡 Temperature: {temp}°C
💧 Humidity: {humidity}%
☁ Condition: {desc}
""" 