# My Smart Room

## Abstract
This small script was designed to control the light sources inside of the room (unfortunately the sunlight control is not supported, yet).

## Overall architecture, controls and sensors
The core of SmartRoom&copy; is the RaspberryPy PI 3.
There are several buttons, motion sensor and light indicators connected to Raspberry. Raspberry by itself is connected to the Wi-Fi network, as well as the Smart LED Bulb. 

Raspberry Py changes the state of the LED Bulb in one of specified scenarios by connecting to it using internal IP address.

## Control scenarios
1. It is possible to turn the Bulb on using the `onOffManualBtn_gpio` button.
2. There is a PIR sensor `pirOnOffBtn_gpio`, that turns on light for 10 seconds.

## Goals

1. Add LED Strip
    - [x] Fix LED strip on the wall.
    - [ ] Connect strip to Raspberry.
    - [ ] Add management logic to Raspberry.

## Ideas

- Control light with Google Assistant ([tutorial](https://medium.com/@kevalpatel2106/turn-your-raspberry-pi-into-homemade-google-home-9e29ad220075))