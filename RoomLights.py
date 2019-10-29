from datetime import datetime, time, date, datetime, timedelta
from yeelight import Bulb
from astral import Astral

import RPi.GPIO as GPIO
import time as timer
import pytz

#LedStripControl_gpio
RledStrip_gpio = None
GledStrip_gpio = None
BledStrip_gpio = None
WledStrip_gpio = None

#LEDout_gpio
isOnled_gpio = 40
pirOnOffLed_gpio = 15
LedStripModeStatusLed_gpio = 38
BulbModeStatusLed_gpio = 36

#input_gpio
pir_gpio = 11
pirOnOffBtn_gpio = 13
onOffManualBtn_gpio = 31
changeModeBtn_gpio = 29
onOffLEDIndicatorsBtn_gpio = 33

#flags
areLED_indicators_enabled = True
isOn = False
isPirStopped = False


bulb_ip = "192.168.178.186"

lightMode = 1

#PIR mode settings
timeOn_duration = 10
timeWhenPirRestart = None

def changeStatusofLed(gpio, value):
    if areLED_indicators_enabled:
        GPIO.output(gpio, value)

def isNight(city: str='Berlin'):
    """
    Checks if it is a night in the provided city.
    The list of the cities is supported by the Astral library.
    
    :param city: String name of interested city.
        The list of supported cities could be found here: 
        https://astral.readthedocs.io/en/latest/#cities
    """
    astral = Astral()
    astral_location = astral[city]
    current_time = datetime.now(pytz.utc)

    sun_information = astral_location.sun(date=current_time, local=False) # Gets time of sunrise and sunset
    # It is early morning (before sun dawn) or late evening (after sun dusk).
    return sun_information['dawn'] >= current_time or sun_information['dusk'] <= current_time   


def pirOnOffBtn_callback(channel):
    changePirStatus()
    if isPirStopped:
        timeWhenPirRestart = (datetime.now() + timedelta(days=1)).date().strftime("%d/%m/%Y")
        print(timeWhenPirRestart)
    else:
        timeWhenPirRestart = None
        

def onOffManualBtn_callback(channel):
    togleLight()

def updateLED_indicators():
    if areLED_indicators_enabled:
        
        GPIO.output(isOnled_gpio, isOn)
        GPIO.output(pirOnOffLed_gpio, isPirStopped)

        # Change modes indicators according to mode
        if lightMode == 1: # Only Bulb will be turned on
            GPIO.output(LedStripModeStatusLed_gpio, False)
            GPIO.output(BulbModeStatusLed_gpio, True)
        elif lightMode == 2: # Only LED will be turned on
            GPIO.output(LedStripModeStatusLed_gpio, True)
            GPIO.output(BulbModeStatusLed_gpio, False)
        elif lightMode == 3: # Both LED and Bulb will be turned on
            GPIO.output(LedStripModeStatusLed_gpio, True)
            GPIO.output(BulbModeStatusLed_gpio, True)
        else:
            GPIO.output(LedStripModeStatusLed_gpio, False)
            GPIO.output(BulbModeStatusLed_gpio, False)
            print("Unexpected lightMode: %s" % lightMode)
    else:
        for led in [LedStripModeStatusLed_gpio, BulbModeStatusLed_gpio, isOnled_gpio, pirOnOffLed_gpio]:
            GPIO.output(led, False)

def changeModeBtn_callback(channel):
    global lightMode
    if lightMode == 1:
        lightMode = 2
    elif lightMode == 2:
        lightMode = 3
    elif lightMode == 3:
        lightMode = 1
    else:
        print("Unexpected lightMode: %s" % lightMode)
    updateLED_indicators()

def togleLight():
    global isOn
    
    if not isOn:
        isOn = True
        if lightMode == 1 or lightMode == 3:
            bulb.turn_on()
        elif lightMode == 2 or lightMode == 3:
            print("Led strip is On")
    else:
        isOn = False
        if lightMode == 1 or lightMode == 3:
            bulb.turn_off()
        elif lightMode == 2 or lightMode == 3:
            print("Led strip is Off")
    changeStatusofLed(isOnled_gpio, isOn)
    print(isOn)

def changePirStatus():
    global isPirStopped
    isPirStopped = not isPirStopped
    changeStatusofLed(pirOnOffLed_gpio, isPirStopped)

def checkPirRestart(isStillNight):
    global timeWhenPirRestart
    if (timeWhenPirRestart is not None) and not isStillNight and datetime.now().date().strftime("%d/%m/%Y") == timeWhenPirRestart:
        changePirStatus()
        timeWhenPirRestart = "None"

bulbrequests_count = 0

def checkBulbPowerStatus():
    global bulbrequests_count
    bulbrequests_count += 1
    print(bulbrequests_count)
    if bulbrequests_count == 60:
        timer.sleep(10)
        bulbrequests_count = 0
    props = bulb.get_properties(['power'])
    return props['power']

def OnOffLEDInticators_callback(channel):
    global areLED_indicators_enabled
    areLED_indicators_enabled = not areLED_indicators_enabled
    updateLED_indicators()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(isOnled_gpio, GPIO.OUT)
GPIO.setup(pirOnOffLed_gpio, GPIO.OUT)
GPIO.setup(LedStripModeStatusLed_gpio, GPIO.OUT)
GPIO.setup(BulbModeStatusLed_gpio, GPIO.OUT)

GPIO.setup(pir_gpio, GPIO.IN)
GPIO.setup(pirOnOffBtn_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(onOffManualBtn_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(changeModeBtn_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(onOffLEDIndicatorsBtn_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(pirOnOffBtn_gpio, GPIO.RISING, callback=pirOnOffBtn_callback)
GPIO.add_event_detect(onOffManualBtn_gpio, GPIO.RISING, callback=onOffManualBtn_callback)
GPIO.add_event_detect(changeModeBtn_gpio, GPIO.RISING, callback=changeModeBtn_callback)
GPIO.add_event_detect(onOffLEDIndicatorsBtn_gpio, GPIO.RISING, callback=OnOffLEDInticators_callback)

changeStatusofLed(LedStripModeStatusLed_gpio, False)
changeStatusofLed(BulbModeStatusLed_gpio, True)


bulb = Bulb(bulb_ip)

if checkBulbPowerStatus() == 'on':
    isOn = True
    changeStatusofLed(isOnled_gpio, isOn)


while True:
    isStillNight = isNight()

    checkPirRestart(isStillNight)

    if isStillNight and not isPirStopped and checkBulbPowerStatus() != 'on':
        if GPIO.input(pir_gpio) == 0:
        # if True:
            timer.sleep(2)
        if GPIO.input(pir_gpio) == 1:
        # if False:
            togleLight()
            timer.sleep(timeOn_duration)
            if not isPirStopped:
                togleLight()
    else:
        timer.sleep(10)
