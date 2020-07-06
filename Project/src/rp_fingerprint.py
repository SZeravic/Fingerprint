#!/usr/bin/python
# -*- coding: utf-8 -*-
#from pyfingerprint.pyfingerprint import PyFingerprint
from libs.pyfingerprint import PyFingerprint
from libs import lcddriver
import hashlib
import time;
import sys;

global counter;
counter = 0;

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

def fp_init():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if (f.verifyPassword() == False):
            raise ValueError('The given fingerprint sensor password is wrong!')
        return f

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)
# End fp_init()

### Main Program Functions
def enroll_f():
    print("Starting enroll_f");
    counter;
    print("Counter: ", counter);
    display.lcd_clear()
    display.lcd_display_string("Starting enroll_f", 1)
    display.lcd_display_string("Function - (WIP)", 2)
    time.sleep(1)
    display.lcd_clear()
# End enroll_f()

def index_f():
    print("Indexing...");
    display.lcd_clear()
    display.lcd_display_string("Index page: ", 1)
    display.lcd_display_string("Options 0 1 2 3", 1)

    f = fp_init()

    page = input('Please enter the index page [0, 1, 2, 3] you want to see: ')
    page = int(page)
    tableIndex = f.getTemplateIndex(page)
    for i in range(0, len(tableIndex)):
        print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))

    time.sleep(4)
# End index_f()

# Tries to search the finger and calculate hash
def search_f():
    print("Search for Finger");
    display.lcd_clear()
    display.lcd_display_string("Searching finger", 1)

    f = fp_init()

    # Gets sensor information
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    print('Waiting for finger...')
    # Wait that finger is read
    while (f.readImage() == False):
        pass

    # Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    # Searchs template
    result = f.searchTemplate()
    positionNumber = result[0]
    accuracyScore = result[1]

    if (positionNumber == -1):
        print('No match found!')
        display.lcd_clear()
        display.lcd_display_string("Auth FAILED", 1)
        display.lcd_display_string("No match found!", 2)
    else:
        score = "Acc score: " + str(accuracyScore)
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))
        display.lcd_clear()
        display.lcd_display_string("Auth SUCCESSFUL", 1)
        display.lcd_display_string(score, 2)
    # End if

    time.sleep(2)
# End search_f()

def delete_f():
    print("Starting delete_f");
    display.lcd_clear()
    display.lcd_display_string("delete_f...", 1)
    display.lcd_display_string("Function - (WIP)", 2)
    time.sleep(1)
# End delete_f()

def clear_f():
    print("Clearing the text...");
    display.lcd_clear()
    display.lcd_display_string("Clearing text...", 1)
    time.sleep(1)
# End clear_f()

def switch_f(arg):
    switch = {
        0: enroll_f,
        1: index_f,
        2: search_f,
        3: delete_f,
        4: clear_f,
    }

    # Get the function from switch case
    func = switch.get(arg, "Invalid")
    # Execute the function
    if (func != "Invalid"):
        return func()
    else:
        print("Invalid Input ... Try again")
        display.lcd_clear()
        display.lcd_display_string("Invalid Input ...", 1)
        display.lcd_display_string("Please try again", 2)
        time.sleep(2);
        return
    # End if
# End switch_f

try:
    # Driver program
    if __name__ == "__main__":
        print("Booting up...");
        display.lcd_display_string("Booting up...", 1)
        time.sleep(2)

        while True:
            display.lcd_clear()
            display.lcd_display_string("Awaiting input: ", 1)
            usr_input = input("Input: ");
            switch_f(usr_input);

            if (usr_input == 4):
                break
    # End if

    print("Program finished - Cleaning up!")
    display.lcd_clear()
# End try

# If there is a exception, exit the program and cleanup
except Exception as e:
    print("Program Forcefully stopped - Cleaning up!")
    print('Exception message: ' + str(e))
    display.lcd_clear()
    exit(1)
# End except

# If there is a KeyboardInterrupt exit the program and cleanup
except KeyboardInterrupt:
    print("KeyboardInterrupt dettected - Cleaning up!")
    display.lcd_clear()
# End except