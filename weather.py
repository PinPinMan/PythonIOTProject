import requests
from tkinter import *
import math

# =========================== Openweathermap API (Current)===========================
def get_weather(api_key, coord):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}"
    response = requests.get(url).json()
    return {
        'temp': math.floor(response['main']['temp'] - 273.15),
        'feels_like': math.floor(response['main']['feels_like'] - 273.15),
        'humidity': math.floor(response['main']['humidity']),
        'description': response['weather'][0]['description']
    }
# =========================== Openweathermap API (Current)===========================


# =========================== Openweathermap API (geocoding)===========================
def get_location(api_key, coord):
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}"
    response = requests.get(url).json()
    return {
        'name': response[0]["name"],
        'country': response[0]["country"]
    }
# =========================== Openweathermap API (geocoding)===========================


# =========================== getting JSON ===========================
api_key = "API KEY from Openweathermap.org"        # MUST EDIT
coord = {
    'lat': "coords N",
    'lon': "coords E"
}
location = get_location(api_key, coord)
weather = get_weather(api_key, coord)
print(location,weather,sep="\n")
# =========================== getting JSON ===========================



# =========================== Window Header ===========================
def display_city_name(location):
    city_label = Label(root, text=f"{location['name']}")
    city_label.config(font=("Consolas", 28))
    city_label.pack(side='top')
# =========================== Window Header ===========================


# =========================== Window Content ===========================
def display_stats(weather):
    temp = Label(root, text=f"Temperature: {weather['temp']}°C")
    feels_like = Label(root, text=f"Feels Like: {weather['feels_like']}°C")
    humidity = Label(root, text=f"Humidity: {weather['humidity']}%")
    description = Label(root, text=f"\ndescription: {weather['description']}")

    temp.config(font=("Consolas", 22))
    feels_like.config(font=("Consolas", 16))
    humidity.config(font=("Consolas", 16))
    description.config(font=("Consolas", 16))

    temp.pack(side='top')
    feels_like.pack(side='top')
    humidity.pack(side='top')
    description.pack(side='top')
# =========================== Window Content ===========================


# =========================== Window ===========================
root = Tk()
root.geometry("350x200")    # size of windows (pixels)
root.title(f'{location["name"]} Weather, {location["country"]}')    # window title

display_city_name(location)
display_stats(weather)

mainloop()      # so window doesnt close immidately
# =========================== Window ===========================