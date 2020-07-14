#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint
from libs.lcddriver import lcd
from libs.userInput import userInput
from time import sleep
import RPi.GPIO as GPIO
import threading

# Load the driver and set it to "display"
display = lcd()

# Set the GPIO Pin for the relay & push buttons to BMC mode (ex. Using 7th Pin aka BCM GPIO pin 4)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# User Input -  init(Buttons)
usr = userInput()

# User Input - Button callbacks (Activate when the button is pressed)
def button_1_callback(channel):
    usr.setUserInput(1)

def button_2_callback(channel):
    usr.setUserInput(2)

def button_3_callback(channel):
    usr.setUserInput(3)

def button_4_callback(channel):
    usr.setUserInput(4)

def button_5_callback(channel):
    usr.setUserInput(5)

# Event listeners that activate the callback functions (Bounce controls accidental button triggers)
GPIO.add_event_detect(26, GPIO.RISING, callback = button_1_callback, bouncetime=200)
GPIO.add_event_detect(19, GPIO.RISING, callback = button_2_callback, bouncetime=200)
GPIO.add_event_detect(13, GPIO.RISING, callback = button_3_callback, bouncetime=200)
GPIO.add_event_detect(6, GPIO.RISING, callback = button_4_callback, bouncetime=200)
GPIO.add_event_detect(5, GPIO.RISING, callback = button_5_callback, bouncetime=200)

###########################################################
################# Main Program Functions ##################
###########################################################
def enroll_f():
    display.lcd_print("Enrolling print")
    sleep(1)

    if fp_authenticate_access():
        print("Authenticated ... proceeding")
        display.lcd_print("Authenticated", "Continuing...")
        sleep(2)
    else: return

    print("Enrolling new fingerpint!")
    display.lcd_print("Enrolling", "New print ...")
    sleep(1)
    fp_enroll_new()

def delete_f():
    display.lcd_print("Deleting print")
    sleep(1)

    if fp_authenticate_access():
        print("Authenticated ... proceeding")
        display.lcd_print("Authenticated", "Continuing...")
        sleep(2)
    else: return

    display.lcd_print("Clearing Indexes")
    display.lcd_print_long("OPT: 1.ALL 2.SINGLE 5.BACK", 2)
    usr.handleUserInput()
    display.lcd_t_stop_set();
    sleep(0.1)

    if usr.getUserInput() == 1:
        pass
        delete_all()
    elif usr.getUserInput() == 2:
        print("Removing single fingerprint")
        display.lcd_print("Removing single", "fingerprint...")
        sleep(2)
        delete_single()
    elif usr.getUserInput() == 3:
        fp_print_all()
    elif usr.getUserInput() == 5:
        return
    sleep(2)

# Tries to search the finger and activates the relay
def search_f():
    display.lcd_print("Searching print")
    sleep(1)

    f = fp_init()
    f = fp_read(f)
    if usr.getUserInput() == 5:
        return
    if fp_authenticate(f)[0]:
        GPIO.output(4, GPIO.HIGH)

    sleep(3)
    GPIO.output(4, GPIO.LOW)
    sleep(0.1)

def index_f():
    display.lcd_print("Searching index: ")
    f = fp_init()
    tableIndex = f.getTemplateIndex(0)
    sleep(1)

    display.lcd_print("Printing Indexes")
    sleep(1)
    indexes = ""
    for i in range(0, len(tableIndex)):
        if str(tableIndex[i]) == "True":
            indexes = indexes + str(i) + ", "
            print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))

    if indexes != "":
        print("Indexes found!")
        display.lcd_print("Indexes found", indexes)
    else:
        print("Indexes not found!")
        display.lcd_print("Indexes empty", "No prints stored")
    sleep(4)

def exit_f():
    print("Exiting the program...")
    display.lcd_print("Exiting program")
    sleep(1)

def abort_f():
    print("Clearing the lcd screen text...")
    display.lcd_print("Farewell...")
    sleep(1)
    GPIO.cleanup()
    display.lcd_clear()

def exception_f():
    print("Exception dettected, closing program...")
    display.lcd_print("Exception thrown", "Exiting ...")
    GPIO.cleanup()
    sleep(2)
    display.lcd_clear()

###########################################################
################# Local Helper Functions ##################
###########################################################
def fp_init():
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if (f.verifyPassword() == False):
        display.lcd_print("Sesnor Init FAILED", "Password INVALID")
        sleep(2)
        raise ValueError('The given fingerprint sensor password is wrong!')
    return f

def fp_read(f):
    print('Waiting for finger...')
    display.lcd_print("Place a finger", "OPT: 5.ABORT")
    while (f.readImage() == False):
        if usr.getUserInput() == 5:
            display.lcd_print("Aborted", "Recovering...")
            sleep(2)
            return
    return f

def fp_authenticate_access():
    f = fp_init()

    print("Authenticate for Access!")
    display.lcd_print("Authenticate", "For root Access:")
    sleep(2)

    f = fp_read(f)
    if usr.getUserInput() == 5:
        return False
    return fp_authenticate(f)[0]

def fp_authenticate(f):
    f.convertImage(0x01)
    result = f.searchTemplate()
    position = result[0]
    accuracy = result[1]

    print("(fp_authenticate) Position is: ", position)

    if (position == -1):
        print('No match found!')
        display.lcd_print("Auth FAILED", "No match found!")
        sleep(1)
        return False, position, accuracy
    else:
        score = "Acc score: " + str(accuracy)
        print('Found template at position #' + str(position))
        print('The accuracy score is: ' + str(accuracy))
        display.lcd_print("Auth SUCCESSFUL", score)
        return True, position, accuracy

def fp_enroll_new():
    f = fp_init()
    f = fp_read(f)
    sleep(0.1)
    if usr.getUserInput() == 5: return
    f.convertImage(0x01)
    position = f.searchTemplate()[0]

    if ( position >= 0 ):
        print('Template already exists at position #' + str(position))
        display.lcd_print("Print already", "enrolled...")
        sleep(2)
        display.lcd_print("Aborting process", "Recovering...")
        sleep(2)
        return

    print('Remove finger...')
    display.lcd_print("Remove finger...")
    sleep(1)

    f = fp_read(f)
    sleep(0.1)
    if usr.getUserInput() == 5: return
    f.convertImage(0x02)
    if ( f.compareCharacteristics() == 0 ):
        print("Prints do not match ... Aborting")
        display.lcd_print("Prints do not", "match...")
        sleep(2)
        display.lcd_print("Aborting process", "Recovering...")
        sleep(2)
        return

    # Creates a template
    f.createTemplate()
    position = f.storeTemplate()
    display.lcd_print("Print enrolled", "SUCCESSFULLY...")
    print('Print enrolled successfully!')
    print('New template position #' + str(position))
    sleep(1)

def delete_all():
    display.lcd_print("Deleting all...")

    f = fp_init()
    tableIndex = f.getTemplateIndex(0)
    sleep(0.2)

    display.lcd_print("Searching Indexes")
    sleep(1)
    indexes_list = ""
    indexes_counter = 0
    for position in range(0, len(tableIndex)):
        if str(tableIndex[position]) == "True" and position != 0:
            if f.deleteTemplate(position):
                print('Template at position #' + str(position) + ' is used: ' + str(tableIndex[position]))
                indexes_counter += 1
                indexes_list += str(position) + ", "
            else:
                display.lcd_print("ABORTING ...", "Delete Failed!")
                sleep(2)
                return

    if indexes_list != "":
        print("Indexes found!")
        indexes_found = "Total found:" + str(indexes_counter)
        display.lcd_print(indexes_found, indexes_list)
        sleep(1)
        print("Index list cleared:")
        print("Index list was: ", indexes_list)
        display.lcd_print("All templates", "Cleared ...")
    else:
        print("Indexes not found!")
        display.lcd_print("Indexes empty", "No prints stored")
    sleep(4)

def delete_single():
    f = fp_init()
    f = fp_read(f)
    result = fp_authenticate(f)
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

    if result[1] == 0:
        display.lcd_print("Action ABORTED!")
        sleep(1)
        display.lcd_print("UNABLE to Remove", "Root acess print")
        sleep(4)
        return

    if result[0]:
        if f.deleteTemplate(result[1]):
            deleted = "Template [ " + str(result[1]) + " ]"
            display.lcd_print(deleted, "Has been cleared")
            print(deleted + " has been cleared")
        else:
            print("Failed to clear", deleted)
            display.lcd_print("Action FAILED", "Failed to clear!")
    sleep(2)

def fp_print_all(f):
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    print("Printing all used templates!")
    sleep(1)

    # TODO: Do it via Arrays!
    indexes = ""
    for page in range (0, 4):
        print('Page: [' + str(page) + ']')
        tableIndex = f.getTemplateIndex(page)
        for i in range(0, len(tableIndex)):
            if str(tableIndex[i]) == "True":
                indexes = indexes + str(i) + ", "
                print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))

def switch_f(arg):
    switch = {
        1: enroll_f,
        2: delete_f,
        3: search_f,
        4: index_f,
    }

    print('B4 User input is %s', usr.getUserInput())
    func = switch.get(arg, "Invalid")
    if (func != "Invalid"):
        return func()
    else:
        print('Aft User input is %s', usr.getUserInput())
        print("Invalid Input ... Try again")
        display.lcd_print("Invalid Input ...", "Please try again")
        sleep(2)
        return

### Driver program
try:
    def main():
        sleep(0.5)
        while True:
            print("-------------------------------------")
            display.lcd_print("Awaiting input: ")
            display.lcd_print_long("OPT: 1.ENRL 2.DEL 3.SEARCH 4.PRINT 5.EXIT", 2)
            usr.handleUserInput()
            display.lcd_t_stop_set();
            sleep(0.1)

            if (usr.getUserInput() == 5):
                exit_f()
                break
            switch_f(usr.getUserInput())

except KeyboardInterrupt:
    print("KeyboardInterrupt dettected - Cleaning up!")
    abort_f()

except BaseException as e:
    print("Program Forcefully stopped - Cleaning up!")
    print('Exception message: ' + str(e))
    exception_f()
    exit(1)

if __name__ == "__main__":
    main()
    abort_f()