from datetime import datetime, time, date, datetime, timedelta
from yeelight import Bulb

import RPi.GPIO as GPIO
import time as timer

#LedStripControl_gpio
RledStrip_gpio = None
GledStrip_gpio = None
BledStrip_gpio = None
WledStrip_gpio = None

#LEDout_gpio
isOnled_gpio = 7
pirOnOffLed_gpio = None
LedStripModeStatusLed_gpio = None
BulbModeStatusLed_gpio = None

#input_gpio
pir_gpio = 11
pirOnOffBtn_gpio = None
onOffManualBtn_gpio = None
changeModeBtn_gpio = None

#flags
isOn = False
isPirStopped = False


bulb_ip = "192.168.178.186"

lightMode = 1

#PIR mode settings
night_start = time(16)
night_end = time(5)
timeOn_duration = 300
timeWhenPirRestart = None



def isNight():
    now = datetime.now().time()
    if night_start <= night_end:
        return night_start <= now < night_end
    else:
        return night_start <= now or now < night_end

def pirOnOffBtn_callback(channel):
    changePirStatus()
    if isPirStopped:
        timeWhenPirRestart = (datetime.now() + timedelta(days=1)).date().strftime("%d/%m/%Y")
    else:
        timeWhenPirRestart = None
        

def onOffManualBtn_callback(channel):
    togleLight()

def changeModeBtn_callback(channel):
    global lightMode
    if lightMode == 1:
        lightMode = 2
        GPIO.outpit(LedStripModeStatusLed_gpio, True)
        GPIO.outpit(BulbModeStatusLed_gpio, False)
        return
    if lightMode == 2:
        lightMode = 3
        GPIO.outpit(LedStripModeStatusLed_gpio, True)
        GPIO.outpit(BulbModeStatusLed_gpio, True)
        return
    if lightMode == 3:
        lightMode = 1
        GPIO.outpit(LedStripModeStatusLed_gpio, False)
        GPIO.outpit(BulbModeStatusLed_gpio, True)
        return

def togleLight():
    if not isOn:
        if lightMode == 1 or lightMode == 3:
            bulb.turn_on()
        elif lightMode == 2 or lightMode == 3:
            print("Led strip is On")
    else:
        if lightMode == 1 or lightMode == 3:
            bulb.turn_off()
        elif lightMode == 2 or lightMode == 3:
            print("Led strip is Off")

def changePirStatus():
    isPirStopped = not isPirStopped
    GPIO.outpit(pirOnOffLed_gpio, isPirStopped)

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

GPIO.add_event_detect(pirOnOffBtn_gpio, GPIO.RISING, callback=pirOnOffBtn_callback)
GPIO.add_event_detect(onOffManualBtn_gpio, GPIO.RISING, callback=onOffManualBtn_callback)
GPIO.add_event_detect(changeModeBtn_gpio, GPIO.RISING, callback=changeModeBtn_callback)

bulb = Bulb(bulb_ip)

while True:
    isStillNight = isNight()

    checkPirRestart(isStillNight)

    if isStillNight and not isPirStopped and checkBulbPowerStatus() != 'on':
        if GPIO.input(pir_gpio) == 0:
        # if True:
            GPIO.outpit(isOnled_gpio, False)
            timer.sleep(2)
        if GPIO.input(pir_gpio) == 1:
        # if False:
            GPIO.outpit(isOnled_gpio, True)
            togleLight()
            timer.sleep(timeOn_duration)
            if not isPirStopped:
                bulb.turn_off()
    else:
        timer.sleep(10)