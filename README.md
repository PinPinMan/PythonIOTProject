<div align="center">
    <h1 >Python IOT Mini Project</h1>
    <h2>Websites</h2>
    <p>
        https://thingspeak.com/channels/2419041 (Senor Data)<br>
        https://sites.google.com/view/ilovesp (Virtual Demo)<br>
        https://openweathermap.org (Weather API)<br>
    </p>
</div>
<hr>

![Screenshot 2024-03-18 175435](https://github.com/PinPinMan/PythonIOTProject/assets/129681701/731523ef-7d05-4684-a2ad-6a5ae48b649b)

<hr>

# Flow of Program:
<hr>

### Start Telegram Bot;

-   Print - “Starting bot...”
-   Telegram commands can be used ( Manual | Auto )
    - Auto ( Weather API | Sensors )
        -  If conditions are met, hardware will move accordingly
    - `Note: for Auto, we need to close the window to run manually.`
-   Moving Hardware
    - If there's something in the way (<20cm). It will pause and wait (Sound Buzzer).
<hr>

# Dependencies:
<hr>

### Set up;
-   Python Raspberry Pi doesn’t have ALL the libraries that we need. Hence, we need to go to the TERMINAL and install our libraries.
    -   `sudo pip3 install python-telegram-bot`
    -   `sudo pip3 install pyautogui`
<hr>

# Hardware:
<hr>

### Movement;
-   DC- Motor
-   Stepper Motor
### Sensor;
-   Moisture Sensor
-   Temperature & Humidity Sensor (DHT11)
-   Ultrasonic Ranger
### Others;
-   Keypad
    - (0) Break out of keypad
    - (1) Prints Distance
    - (2) Move DC Motor
    - (3) Move Stepper Motor to the left
    - (4) Move Stepper Motor to the right
    - (5) Prints the Temperature and Humidity
<hr>

# Telegram:
<hr>

### Commands;
-   **about** - give a description of bot & rack
-   **auto** - Allow the Sensors & API to take over
-   **bring in** - brings in the rack (Extends)
-   **bring out** - brings out the rack (Extends)
-   **retract** - Retract the rack
-   **extend** - Extend the rack
-   **keypad** - allows 1 key to be pressed
<hr>

### Weather API:
<hr>

### Location (Coordinates);
-   http://api.openweathermap.org/geo/1.0/reverse?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}
-   Given in JSON format
### Senors Data (From API);
-   https://api.openweathermap.org/data/2.5/weather?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}
-   Given in JSON format
