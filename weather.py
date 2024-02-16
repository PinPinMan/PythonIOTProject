# Dependencies:
# - Python Rasberry Pi does't have ALL the Libraries that we need.
#   Hence we need to go to the TERMINAL and install our libraries
#
#
# sudo pip3 install python-telegram-bot
# sudo pip3 install pyautogui


# =========================== Raspberry Pi modules ==========================
from gpiozero import DistanceSensor, Buzzer
import dht11
import RPi.GPIO as GPIO
import datetime
import time
import pyautogui as pg                      # for clicking into simulator
import requests
from tkinter import *
import math
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# =========================== Setting of GPIO ==========================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)  # Stepper Motor
GPIO.setup(23, GPIO.OUT)  # DC Motor
GPIO.setup(4, GPIO.IN)  # Moisture sensor
GPIO.setup(25, GPIO.OUT)  # UltraSonic sensor (Trig)
GPIO.setup(27, GPIO.IN)  # UltraSonic sensor (Echo)
GPIO.setup(18, GPIO.OUT)  # Buzzer


# =========================== Ultrasonic Ranger ===========================
def distance1():
    # produce a 10us pulse at Trig
    GPIO.output(25, 1)
    time.sleep(0.00001)
    GPIO.output(25, 0)
    # measure pulse width (i.e. time of flight) at Echo
    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(27) == 0:
        StartTime = time.time()  # capture start of high pulse
    while GPIO.input(27) == 1:
        StopTime = time.time()  # capture end of high pulse

    ElapsedTime = StopTime-StartTime
    Distance = (ElapsedTime*34300)/2
    if Distance < 20:
        GPIO.output(18, 1)
        time.sleep(0.5)
        GPIO.output(18, 0)
    print(Distance)
    return Distance


# =========================== Temp & Humidity ===========================
def temp_hum():
    # read data using pin 21
    instance = dht11.DHT11(pin=21)
    try:
        while True:                                             # keep reading, unless a key is pressed on keyboard
            result = instance.read()
            if result.is_valid():                               # print date, time and sensor values
                # print("Last valid input: " + str(datetime.datetime.now()))
                # print("Temperature: %-3.1f C" % result.temperature)
                # print("Humidity: %-3.1f %%" % result.humidity)
                return [result.temperature, result.humidity]
            # short delay between reads
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Cleanup")
        # Google what this means...
        GPIO.cleanup()


# =========================== Retracting / Extending ===========================
def dc_motor():
    for i in range(1, 3):       # Splits it into 3 steps
        dist = distance1()
        while dist < 20:        # if the distance is less than 20cm
            pg.press("p")       # Simulator (PAUSE)
            time.sleep(2)
            dist = distance1()

        pg.press("o")           # Simulator (UNPAUSE)
        GPIO.output(23, 1)
        time.sleep(0.3)
        GPIO.output(23, 0)


# =========================== Rotating ===========================
def stepper(direction):
    PWM = GPIO.PWM(26, 100)
    if direction == "left":         # Direction of the Movement
        i = 3                       # set the PWM Start
        while i <= 24:              # Splits it into 11 steps
            dist = distance1()
            while dist < 20:
                pg.press("p")       # Simulator (PAUSE)
                time.sleep(2)
                dist = distance1()

            pg.press("o")           # Simulator (UNPAUSE)
            PWM.start(i)
            time.sleep(0.1)
            i += 2
    else:                           # Same thing but for the other direction
        i = 24
        while i >= 3:
            dist = distance1()
            while dist < 20:
                pg.press("p")       # Simulator (PAUSE)
                time.sleep(2)
                dist = distance1()

            pg.press("o")           # Simulator (UNPAUSE)
            PWM.start(i)
            time.sleep(0.1)
            i -= 2


# =========================== Moisture Sensor ===========================
def moisture():
    return GPIO.input(4)


# =========================== Keypad ===========================
def keypad():
    MATRIX = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9],
              ['*', 0, '#']]  # layout of keys on keypad
    ROW = [6, 20, 19, 13]  # row pins
    COL = [12, 5, 16]  # column pins

    # set column pins as outputs, and write default value of 1 to each
    for i in range(3):
        GPIO.setup(COL[i], GPIO.OUT)
        GPIO.output(COL[i], 1)
    # set row pins as inputs, with pull up
    for j in range(4):
        GPIO.setup(ROW[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # scan keypad
    state = True
    while state:
        for i in range(3):  # loop through all columns
            GPIO.output(COL[i], 0)  # pull one column pin low
            for j in range(4):  # check which row pin becomes low
                if GPIO.input(ROW[j]) == 0:  # if a key is pressed
                    pressed = MATRIX[j][i]
                    if pressed == 1:
                        distance1()
                    elif pressed == 2:
                        dc_motor()
                    elif pressed == 3:
                        stepper("left")
                    elif pressed == 3:
                        stepper("right")
                    elif pressed == 4:
                        moisture()
                    elif pressed == 5:
                        print(temp_hum())
                    elif pressed == 0:  # Press 0 to break out of the keypad
                        state = False

                    while GPIO.input(ROW[j]) == 0:  # debounce
                        time.sleep(0.1)
            GPIO.output(COL[i], 1)  # write back default value of


# //////////////////////////////////////////// Commands ////////////////////////////////////////////


# =========================== Bring In ===========================
def bring_in_rack():
    pg.press("z")   # Simulator (Bring IN)

    # Run Hardware
    dc_motor()
    stepper('left')
    dc_motor()


# =========================== Bring Out ===========================
def bring_out_rack():
    pg.press("x")   # Simulator (Bring OUT)

    # Run Hardware
    dc_motor()
    stepper('right')
    dc_motor()


# =========================== Extend ===========================
def extend():
    pg.press("s")   # Simulator (Extend)

    # Run Hardware
    dc_motor()


# =========================== Retract ===========================
def retract():
    pg.press("a")   # Simulator (Retract)

    # Run Hardware
    dc_motor()


# ================================================================================= THINKER DISPLAY =================================================================================


def windowDisplay():
    # =========================== getting JSON ===========================
    api_key = "2ad3b0f531232afc044817a7e9a8627a"
    coord = {
        'lat': 1.3162,
        'lon': 103.7649
    }
    # =========================== getting JSON ===========================

    # =========================== Openweathermap API (Current)===========================

    def get_weather(api_key, coord):
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}"
            response = requests.get(url).json()
            return {
                'temp': math.floor(response['main']['temp'] - 273.15),
                'feels_like': math.floor(response['main']['feels_like'] - 273.15),
                'humidity': math.floor(response['main']['humidity']),
                'description': response['weather'][0]['description']
            }
        except:
            return "Location Not Found"
    # =========================== Openweathermap API (Current)===========================
    # =========================== Openweathermap API (geocoding)===========================

    def get_location(api_key, coord):
        try:
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}"
            response = requests.get(url).json()
            return {
                'name': response[0]["name"],
                'country': response[0]["country"]
            }
        except:
            return "Location Not Found"
    # =========================== Openweathermap API (geocoding)===========================

    # =========================== Sensor Data ===========================

    def sensorsWeather():
        SensorMoisture = moisture()
        SensorTemp, SensorHumidity = temp_hum()
        weather2 = {
            'SensorMoisture': SensorMoisture,
            'SensorTemp': SensorTemp,
            'SensorHumidity': SensorHumidity,
        }
        return weather2
    # =========================== Sensor Data ===========================

    # =========================== Window Header ===========================

    def display_city_name(location):
        if location == "Location Not Found":
            city_label.config(font=("Consolas", 22), text="Location Not Found")
        else:
            city_label.config(font=("Consolas", 28),
                              text=f"{location['name']}")
    # =========================== Window Header ===========================

    # =========================== Window Content ===========================

    def display_stats(weather1):
        temp1.config(font=("Consolas", 22),
                     text=f"Temperature: {weather1['temp']}°C")
        feels_like1.config(font=("Consolas", 16),
                           text=f"Feels Like: {weather1['feels_like']}°C")
        humidity1.config(font=("Consolas", 16),
                         text=f"Humidity: {weather1['humidity']}%")
        description1.config(font=("Consolas", 16),
                            text=f"\ndescription: {weather1['description']}")

        # Getting Hardware Sensor Data
        weather2 = sensorsWeather()
        bringInFlag = False
        bringOutFlag = False

        # Checking if surrounding hardware is ("Sunny" or "Rainy")
        if weather2['SensorMoisture'] == 1:
            isWater = True
            bringInFlag = True
        elif weather1["description"] in ["shower rain", "rain", "thunderstorm", "snow", "mist"]:
            bringInFlag = True
        elif weather1["description"] == "broken clouds" and weather2['SensorMoisture'] == 0:
            isWater = False
            bringOutFlag = True
        else:
            isWater = False

        temp2.config(font=("Consolas", 22),
                     text=f"Temperature: {weather2['SensorTemp']}°C")
        rain2.config(font=("Consolas", 16), text=f"Rain Contact: {isWater}")
        humidity2.config(font=("Consolas", 16),
                         text=f"Humidity: {weather2['SensorHumidity']}%")

        # Moving Hardware
        global isInside
        if bringInFlag and not isInside:
            bring_in_rack()
            isInside = True
            bringInFlag = False
        elif bringOutFlag and isInside:
            bring_out_rack()
            isInside = False
            bringOutFlag = False

        # =========================== Uploading Sensor Data ===========================
        # if isWater:
        #     isWater = 1
        # else:
        #     isWater = 0
        # requests.get("https://thingspeak.com/update?api_key=RC5MM7NJF3OLZJPY&field1=%s&field2=%s&field3=%s" %(weather2['temp'], weather2["humidity"], isWater))
    # =========================== Window Content ===========================

    # =========================== Refreshing Window ===========================

    def update():
        location = get_location(api_key, coord)
        weather = get_weather(api_key, coord)
        print(location, weather, sep="\n")

        if location == "Location Not Found":
            root.title(f'Error')
            display_city_name(location)
        else:
            # window title
            root.title(f'{location["name"]} Weather, {location["country"]}')
            display_city_name(location)
            display_stats(weather)

        # Call the update function again to refresh window
        root.after(2000, update)
    # =========================== Refreshing Window ===========================

    # =========================== Window ===========================
    root = Tk()
    root.geometry("900x300")    # size of windows (pixels)
    root.resizable(0, 0)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    city_label = Label(root)
    temp1 = Label(root)
    feels_like1 = Label(root)
    humidity1 = Label(root)
    description1 = Label(root)

    temp2 = Label(root)
    rain2 = Label(root)
    humidity2 = Label(root)

    sensors = Label(root)
    internet = Label(root)
    sensors.config(font=("Consolas", 20), text=f"\nSensors")
    internet.config(font=("Consolas", 20), text=f"\nInternet")

    city_label.grid(column=0, row=1, columnspan=2)
    sensors.grid(column=1, row=2)
    internet.grid(column=0, row=2)
    temp1.grid(column=0, row=3)
    feels_like1.grid(column=0, row=4)
    humidity1.grid(column=0, row=5)
    description1.grid(column=0, row=6)

    temp2.grid(column=1, row=3)
    rain2.grid(column=1, row=4)
    humidity2.grid(column=1, row=5)

    root.after(2000, update)
    mainloop()      # so window doesnt close immidately
    # =========================== Window ===========================


# //////////////////////////////////////////////////////////////// Telegram Bot ////////////////////////////////////////////////////////////////
isInside = True     # Position / State of Current Drying Rack
isExtend = True     # state of extend for drying rack
TOKEN = '6976094973:AAGeYyFW_qB4nleUvE86khxcNa0aJkYFXTw'
BOT_USERNAME = '@SmartDryingCompanionBot'
CHAT_ID = "-1002099990265"


def send_message(text):
    url_req = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
    results = requests.get(url_req)
    return results.json()


send_message("Starting Bot...")


# ================================================= Commands =================================================
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome your Automatic Drying Rack!!!\nIt will give you a log of when its opening or closing.\n\nManual Controllers:\n- /bring_in\n- /bring_out\n- /retract\n- /extend\n- /auto")


async def bring_in_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Conditions for position of hardware ("Inside" or "Outside")
    global isInside
    global isExtend
    if isInside:
        await update.message.reply_text("Rack is already inside")
    else:
        await update.message.reply_text("Bring in Rack (Manual)")
        bring_in_rack()     # Moving Hardware
        isInside = True
        isExtend = True


async def bring_out_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Conditions for position of hardware ("Inside" or "Outside")
    global isInside
    global isExtend
    if not isInside:
        await update.message.reply_text("Rack is already outside")
    else:
        await update.message.reply_text("Bring outa Rack (Manual)")
        bring_out_rack()     # Moving Hardware
        isInside = False
        isExtend = True


async def retract_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global isExtend
    if isExtend:
        # Conditions for position of hardware ("Inside" or "Outside")
        if isInside:
            await update.message.reply_text("Rack is Retracting Inside... (Manual)")
        else:
            await update.message.reply_text("Rack is Retracting Outside... (Manual)")
        retract()     # Moving Hardware
        isExtend = False
    else:
        await update.message.reply_text("Rack is already retracted")


async def extend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global isExtend
    if not isExtend:
        # Conditions for position of hardware ("Inside" or "Outside")
        if isInside:
            await update.message.reply_text("Rack is Extending Inside... (Manual)")
        else:
            await update.message.reply_text("Rack is Extending Outside... (Manual)")
        extend()     # Moving Hardware
        isExtend = True
    else:
        await update.message.reply_text("Rack is already extended")


async def auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Changing back to auto...")
    windowDisplay()


async def keypad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Press a Key...\n0) Break out of keypad\n1) Prints Distance\n2) Move DC Motor\n3) Move Stepper Motor to the left\n4) Move Stepper Motor to the right\n5) Prints the Temmperature and Humidity")
    keypad()
    print("Broken Out of Keypad")


# ===================================================================== Errors =====================================================================
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# ===================================================================== Running Server =====================================================================
if __name__ == "__main__":
    print("Starting Bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("bring_in", bring_in_command))
    app.add_handler(CommandHandler("bring_out", bring_out_command))
    app.add_handler(CommandHandler("retract", retract_command))
    app.add_handler(CommandHandler("extend", extend_command))
    app.add_handler(CommandHandler("auto", auto_command))
    app.add_handler(CommandHandler("keypad", keypad_command))

    # # Messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # # Polls the bot
    app.run_polling(poll_interval=3)    # intervals = 3 seconds

    # Errors
    app.add_error_handler(error)
