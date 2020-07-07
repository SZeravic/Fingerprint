#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint;
from libs.lcddriver import lcd;
import threading;
import time;
import sys;

# Load the driver and set it to "display"
display = lcd()

### Main Program Functions
def enroll_f():
    print("Starting enroll_f");
    display.lcd_clear()
    display.lcd_display_string("Enrolling finger", 1)

    f = fp_init()

    print('Waiting for finger...')
    display.lcd_display_string("Place a finger", 1)
    display.lcd_display_string("On the sensor...", 2)
    while ( f.readImage() == False ):
        pass

    # Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    # Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        display.lcd_clear()
        display.lcd_display_string("Finger already", 1)
        display.lcd_display_string("enrolled...", 2)
        time.sleep(2)
        display.lcd_clear()
        display.lcd_display_string("Aborting process", 1)
        display.lcd_display_string("Recovering...", 2)
        time.sleep(2)
        return
    #End if

    print('Remove finger...')
    display.lcd_clear()
    display.lcd_display_string("Remove finger...", 1)
    time.sleep(1)

    print('Waiting for same finger again...')
    display.lcd_clear()
    display.lcd_display_string("Waiting for the", 1)
    display.lcd_display_string("same finger...", 2)
    while ( f.readImage() == False ):
        pass

    # Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    # Trying to check for a match between buffers
    if ( f.compareCharacteristics() == 0 ):
        print("Finger does not match ... Aborting")
        display.lcd_clear()
        display.lcd_display_string("Finger does not", 1)
        display.lcd_display_string("match...", 2)
        time.sleep(2)
        display.lcd_clear()
        display.lcd_display_string("Aborting process", 1)
        display.lcd_display_string("Recovering...", 2)
        time.sleep(2)
        return
    #End if

    # Creates a template
    f.createTemplate()

    # Saves template at new position number
    positionNumber = f.storeTemplate()
    display.lcd_clear()
    display.lcd_display_string("Finger enrolled", 1)
    display.lcd_display_string("SUCCESSFULLY...", 2)
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

    time.sleep(1)
# End enroll_f()

def index_f():
    print("Indexing...");
    display.lcd_clear()
    display.lcd_display_string("Searching index: ", 1)

    f = fp_init()

    tableIndex = f.getTemplateIndex(0)
    time.sleep(1)

    display.lcd_clear()
    display.lcd_display_string("Printing Indexes", 1)
    time.sleep(1)
    indexes = ""
    for i in range(0, len(tableIndex)):
        if str(tableIndex[i]) == "True":
            indexes = indexes + str(i) + ", "
            print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))

    if indexes != "":
        display.lcd_clear()
        display.lcd_display_string("Indexes found", 1)
        display.lcd_display_string(indexes, 2)
        print("Indexes found!");
    else:
        display.lcd_clear()
        display.lcd_display_string("Indexes empty", 1)
        display.lcd_display_string("No prints stored", 2)
        print("Indexes not found!");

    time.sleep(4)
# End index_f()

# Tries to search the finger and calculate hash
def search_f():
    print("Search for finger");
    display.lcd_clear()
    display.lcd_display_string("Searching finger", 1)

    f = fp_init()

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    print('Waiting for finger...')
    display.lcd_display_string("Place a finger", 1)
    display.lcd_display_string("On the sensor...", 2)
    while (f.readImage() == False):
        pass

    # Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    # Searches templates
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
    display.lcd_display_string("Deleting finger", 1)

    f = fp_init()

    display.lcd_clear()
    display.lcd_display_string("Which finger", 1)
    display.lcd_display_string("index to delete:", 2)

    positionNumber = input('Please enter the template position you wish to delete: ')
    positionNumber = int(positionNumber)

    if (f.deleteTemplate(positionNumber) == True ):
        deleted = "Template [ " + str(positionNumber) + " ]"
        display.lcd_clear()
        display.lcd_display_string(deleted, 1)
        display.lcd_display_string("Has been deleted", 2)
        print(deleted + " has been deleted")
    #End if

    time.sleep(2)
# End delete_f()

def exit_f():
    print("Exiting the program...");
    display.lcd_clear()
    display.lcd_display_string("Exiting program", 1)
    time.sleep(1)
# End clear_f()

def clear_f():
    print("Clearing the lcd screen text...");
    display.lcd_clear()
    display.lcd_display_string("Farewell...", 1)
    time.sleep(1)
    display.lcd_clear()
# End clear_f()

def switch_f(arg):
    switch = {
        1: enroll_f,
        2: index_f,
        3: search_f,
        4: delete_f,
        5: exit_f,
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

### Driver program
try:
    def main():
        print("Booting up...");
        display.lcd_display_string("Booting up...", 1);
        time.sleep(2);

        while True:
            print("-------------------------------------");
            display.lcd_clear();
            display.lcd_display_string("Awaiting input: ", 1);

            t1_stop = threading.Event();
            t1 = threading.Thread(target=long_string, args=(display, t1_stop, "OPT: 1.ENRL 2.INDX 3.SRCH 4.DEL 5.EXIT", 2,));
            t1.start();
            usr_input = input("Input: ");
            t1_stop.set();
            time.sleep(0.1)

            switch_f(usr_input);

            if (usr_input == 5):
                break;
            #End if
        #End while
    # End if
# End try

# If there is a exception, exit the program and cleanup
except Exception as e:
    print("Program Forcefully stopped - Cleaning up!");
    print('Exception message: ' + str(e));
    clear_f();
    exit(1);
# End except

# If there is a KeyboardInterrupt exit the program and cleanup
except KeyboardInterrupt:
    print("KeyboardInterrupt dettected - Cleaning up!");
    clear_f();
# End except

### Local Helper Functions
# @param display    - driver screen (lcd)
# @param stop_event - option to set thread event to stop
# @param text       - string to print
# @param line       - number of line to print
# @param colum      - number of columns of your display
# @return This function send to display your scrolling string.
def long_string(display, stop_event, text = '', line = 1, colum = 16):
    if(len(text) > colum):
        display.lcd_display_string(text[:colum],line)
        time.sleep(1)
        for i in range(len(text) - colum + 1):
            if stop_event.is_set():
                break
            text_to_print = text[i:i + colum]
            display.lcd_display_string(text_to_print,line)
            time.sleep(0.4)
        time.sleep(1)
    else:
        display.lcd_display_string(text, line)
    # End if
# End long_string

def fp_init():
    # @param port       - USB port  (string)
    # @param baudRate   - Baud Rate (integer)
    # @param address    - Address   (integer) (4 bytes) (0xFFFFFFFF by default)
    # @param password   - Password  (integer) (4 bytes) (0x00000000 by default)
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if (f.verifyPassword() == False):
        display.lcd_clear()
        display.lcd_display_string("Sesnor Init FAILED", 1)
        display.lcd_display_string("Password INVALID", 2)
        time.sleep(2)
        raise ValueError('The given fingerprint sensor password is wrong!')
    return f
# End fp_init()

if __name__ == "__main__":
    main();
    print("Exited normally - Cleaning up!");
    clear_f();
# End ___main___