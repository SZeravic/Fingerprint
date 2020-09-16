#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint
from libs.lcddriver import lcd
from libs.userInput import userInput
from time import sleep, time
import RPi.GPIO as GPIO
import subprocess
import os

# Load the driver and set it to "display"
display = lcd()

def GPIO_setup():
    # Set the GPIO Pin for the relay & push buttons to BMC mode (ex. Using 7th Pin aka BCM GPIO pin 4)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    # Event listeners that activate the callback functions (Bounce controls accidental button triggers)
    GPIO.add_event_detect(26, GPIO.RISING, callback = button_callback, bouncetime=200)
    GPIO.add_event_detect(19, GPIO.RISING, callback = button_callback, bouncetime=200)
    GPIO.add_event_detect(13, GPIO.RISING, callback = button_callback, bouncetime=200)
    GPIO.add_event_detect(6, GPIO.RISING, callback = button_callback, bouncetime=200)
    GPIO.add_event_detect(5, GPIO.RISING, callback = button_callback, bouncetime=200)

# User Input - Input control
usr = userInput()

# User Input - Button callbacks (Activate when the button is pressed)
def button_callback(channel):
    usr.setUserInput(channel)

######################## Main Program Functions ########################
def record_f():
    print('Waiting for finger...')
    display.lcd_print("First Print","Image Download")
    sleep(1)

    f = fp_init()

    display.lcd_print("Place a finger", "OPT:     5.ABORT")
    while (f.readImage() == False):
        if usr.getUserInput() == 5:
            display.lcd_print("Aborted", "Recovering...")
            sleep(1)
            return False

    print('Saving first print image')
    display.lcd_print("Saving first","Image print")
    os.chdir("/home/pi/Desktop/Fingerprint/Project/src/openCV/database")
    imageDestination =  os.getcwd() + '/000.bmp'
    f.downloadImage(imageDestination)
    print('The image was saved to "' + imageDestination + '".')
    display.lcd_print("Image Saved!")
    sleep(1)

    display.lcd_print("Second Print","Image Download")
    sleep(1)

    display.lcd_print("Place a finger", "OPT:     5.ABORT")
    while (f.readImage() == False):
        if usr.getUserInput() == 5:
            display.lcd_print("Aborted", "Recovering...")
            sleep(1)
            return False

    print('Saving second print image')
    display.lcd_print("Saving second","Image print")
    imageDestination =  os.getcwd() + '/001.bmp'
    f.downloadImage(imageDestination)
    print('The image was saved to "' + imageDestination + '".')
    display.lcd_print("Image Saved!")
    sleep(1)
    
def search_f():
    print("Calling control program (fingerprint.py)")
    display.lcd_print("Starting up...")
    sleep(2)
    display.lcd_print("Analizing prints")
    GPIO.cleanup()
    os.chdir("/home/pi/Desktop/Fingerprint/Project/src/openCV/")
    print(os.getcwd())
    start_time = time()
    returncode = subprocess.call(['python3', '/home/pi/Desktop/Fingerprint/Project/src/openCV/fingerprint.py'])
    print("Execution time --- %s seconds ---" % (time() - start_time))
    print("Returncode: ", returncode)
    sleep(0.5)
    GPIO_setup()
    sleep(0.5)
    if returncode == 0:
        display.lcd_print("Access Granted!")
        sleep(0.1)
        GPIO.output(4, GPIO.HIGH)
        sleep(3)
        GPIO.output(4, GPIO.LOW)
        sleep(0.1)
    elif returncode == 1:
        display.lcd_print("Auth FAILED", "No match found!")
        sleep(2)
    sleep(0.1)

def fp_init():
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if (f.verifyPassword() == False):
        display.lcd_print("Sesnor Init FAILED", "Password INVALID")
        sleep(2)
        raise ValueError('The given fingerprint sensor password is wrong!')
    return f

def switch_f(arg):
    switch = {
        1: record_f,
        3: search_f,
    }

    func = switch.get(arg, "Invalid")
    if (func != "Invalid"):
        return func()
    else:
        print("Invalid Input ... Try again")
        display.lcd_print("Invalid Input ...", "Please try again")
        sleep(2)
        return

########################## Main Driver program ##########################
try:
    def main():
        sleep(0.5)
        while True:
            print("-------------------------------------")
            display.lcd_print("Select Option: ")
            display.lcd_print_long("OPT: 1.RECORD_IMAGES 3.COMPARE 5.EXIT", 2)
            usr.handleUserInput()
            display.lcd_t_stop_set();
            sleep(0.1)

            if (usr.getUserInput() == 5):
                break
            switch_f(usr.getUserInput())

except KeyboardInterrupt:
    print("KeyboardInterrupt dettected - Cleaning up!")
    exit_f()

except BaseException as e:
    print("Program Forcefully stopped - Cleaning up!")
    print('Exception message: ' + str(e))
    exception_f()
    exit(1)

def exception_f():
    print("Exception dettected, closing program...")
    display.lcd_print("Exception thrown", "Exiting ...")
    display.lcd_t_stop_set()
    GPIO.cleanup()
    sleep(2)
    display.lcd_clear()

def exit_f():
    print("Clearing the lcd screen text...")
    display.lcd_print("Farewell...")
    sleep(1)
    GPIO.cleanup()
    display.lcd_clear()

if __name__ == "__main__":
    GPIO_setup()
    main()
    exit_f()