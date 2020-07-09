#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint;
from libs.lcddriver import lcd;
import RPi.GPIO as GPIO
import threading;
import time;
import sys;

# Load the driver and set it to "display"
display = lcd()

# Set the GPIO Pin for the relay to BMC mode (Using 7th Pin aka BCM GPIO pin 4)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# User Input -  init(Buttons)
user_input = 0;

# Handle User Input
def input_f():
    global user_input
    #Loop to wait for user input
    print("Input: ");
    while True:
        user_input = 0;
        time.sleep(0.2);
        if user_input != 0:
            print("User Input: ", user_input)
            return user_input;
# End input_f()

# User Input - Button callbacks (Activate when the button is pressed)
def button_1_callback(channel):
    global user_input;
    print("Button [1] - GPIO Pin [26] Pressed!")
    user_input = 1;
    time.sleep(0.1)

def button_2_callback(channel):
    global user_input;
    print("Button [2] - GPIO Pin [19] Pressed!")
    user_input = 2;
    time.sleep(0.1)

def button_3_callback(channel):
    global user_input;
    print("Button [3] - GPIO Pin [13] Pressed!")
    user_input = 3;
    time.sleep(0.1)

def button_4_callback(channel):
    global user_input;
    print("Button [4] - GPIO Pin [6] Pressed!")
    user_input = 4;
    time.sleep(0.1)

def button_5_callback(channel):
    global user_input;
    print("Button [5] - GPIO Pin [5] Pressed!")
    user_input = 5;
    time.sleep(0.1)

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
    print("Starting enroll_f");
    display.lcd_clear()
    display.lcd_display_string("Enrolling print", 1)

    f = fp_init()
    if fp_read(f) == 5:
        return

    # Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    # Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        display.lcd_clear()
        display.lcd_display_string("Print already", 1)
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

    fp_read(f)

    # Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    # Trying to check for a match between buffers
    if ( f.compareCharacteristics() == 0 ):
        print("Prints do not match ... Aborting")
        display.lcd_clear()
        display.lcd_display_string("Prints do not", 1)
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
    display.lcd_display_string("Print enrolled", 1)
    display.lcd_display_string("SUCCESSFULLY...", 2)
    print('Print enrolled successfully!')
    print('New template position #' + str(positionNumber))

    time.sleep(1)
# End enroll_f()

def delete_f():
    print("Starting delete_f");
    display.lcd_clear()

    f = fp_init()

    display.lcd_clear()
    display.lcd_display_string("Clearing Indexes", 1)
    t_stop = threading.Event();
    t = threading.Thread(target=long_string, args=(display, t_stop, "OPT: 1.ALL 2.SINGLE 3.PRINT 5.BACK", 2,));
    t.start();

    # positionNumber = input('Please enter the template position you wish to clear: ')
    # positionNumber = int(positionNumber)
    # t_stop.set();

    user_button = input_f();
    if user_input == 1:
        pass
        # delete_all();
    elif user_input == 2:
        pass
        # delete_single();
    elif user_input == 3:
        pass
        print_all();
    elif user_input == 5:
        return

    t_stop.set();
    time.sleep(0.1)

    # print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    # print('Waiting for finger...')
    # display.lcd_display_string("Place a finger", 1)
    # display.lcd_display_string("On the sensor...", 2)
    # while (f.readImage() == False):
    #     pass

    # # # Converts read image to characteristics and stores it in charbuffer 1
    # f.convertImage(0x01)
    # # # Searches templates
    # result = f.searchTemplate()
    # positionNumber = result[0]
    # accuracyScore = result[1]

    # if (f.deleteTemplate(positionNumber) == True ):
    #     deleted = "Template [ " + str(positionNumber) + " ]"
    #     display.lcd_clear()
    #     display.lcd_display_string(deleted, 1)
    #     display.lcd_display_string("Has been cleared", 2)
    #     print(deleted + " has been cleared")
    # else:
    #     display.lcd_clear()
    #     display.lcd_display_string("Action FAILED", 1)
    #     display.lcd_display_string("Failed to clear!", 2)
    #     print("Failed to clear", deleted)
    # #End if

    time.sleep(2)
# End delete_f()

# Tries to search the finger and calculate hash
def search_f():
    print("Search for print");
    display.lcd_clear()
    display.lcd_display_string("Searching print", 1)

    f = fp_init()
    print_all(f);
    if fp_read(f) == 5:
        return

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
        GPIO.output(4, GPIO.HIGH)
    # End if

    time.sleep(3)
    GPIO.output(4, GPIO.LOW)
    time.sleep(0.1)
# End search_f()

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

def exit_f():
    print("Exiting the program...");
    display.lcd_clear()
    display.lcd_display_string("Exiting program", 1)
    time.sleep(1)
# End clear_f()

def exception_f():
    print("Exception dettected, closing program...");
    display.lcd_clear()
    display.lcd_display_string("Exception thrown", 1)
    display.lcd_display_string("Exiting ...", 2)
    display.lcd_clear()
    GPIO.cleanup()
    time.sleep(2)
# End clear_f()

def clear_f():
    print("Clearing the lcd screen text...");
    display.lcd_clear()
    display.lcd_display_string("Farewell...", 1)
    time.sleep(1)
    GPIO.cleanup()
    display.lcd_clear()
# End clear_f()

def switch_f(arg):
    switch = {
        1: enroll_f,
        2: delete_f,
        3: search_f,
        4: index_f,
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

            t_stop = threading.Event();
            t = threading.Thread(target=long_string, args=(display, t_stop, "OPT: 1.ENRL 2.DEL 3.SEARCH 4.PRINT 5.EXIT", 2,));
            t.start();
            user_button = input_f()
            t_stop.set();
            time.sleep(0.1)

            if (user_input == 5):
                exit_f
                break;
            switch_f(user_button);
            #End if
        #End while
    # End if
# End try

# If there is a exception, exit the program and cleanup
except Exception as e:
    print("Program Forcefully stopped - Cleaning up!");
    print('Exception message: ' + str(e));
    exception_f();
    exit(1);
# End except

# If there is a KeyboardInterrupt exit the program and cleanup
except KeyboardInterrupt:
    print("KeyboardInterrupt dettected - Cleaning up!");
    clear_f();
# End except

# Catch any exception
except:
    print("Program Forcefully stopped - Cleaning up!");
    exception_f();
    exit(1);

###########################################################
################# Local Helper Functions ##################
###########################################################
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

def fp_read(f):
    global user_input;
    print('Waiting for finger...')
    display.lcd_display_string("Place a finger", 1)
    display.lcd_display_string("OPT: 5.ABORT", 2)
    while (f.readImage() == False):
        if user_input == 5:
            print('Aborted!')
            display.lcd_clear()
            display.lcd_display_string("Aborted", 1)
            display.lcd_display_string("Recovering...", 2)
            time.sleep(2)
            return user_input
# End fp_read()

# def delete_pos(f):

# End delete_pos

def print_all(f):
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    print("Printing all used templates!");
    time.sleep(1)

    # TODO: Do it via Arrays!
    indexes = ""
    for page in range (0, 4):
        print('Page: [' + str(page) + ']')
        tableIndex = f.getTemplateIndex(page)
        for i in range(0, len(tableIndex)):
            if str(tableIndex[i]) == "True":
                indexes = indexes + str(i) + ", "
                print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))
# End delete_all()

if __name__ == "__main__":
    main();
    print("Exited normally - Cleaning up!");
    clear_f();
# End ___main___