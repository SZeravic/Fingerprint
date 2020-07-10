#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint;
from libs.lcddriver import lcd;
from time import sleep;
import RPi.GPIO as GPIO
import threading;
import sys;

# Load the driver and set it to "display"
display = lcd()

# Set the GPIO Pin for the relay to BMC mode (Using 7th Pin aka BCM GPIO pin 4)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT, initial = GPIO.LOW)
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
        sleep(0.2);
        if user_input != 0:
            print("User Input: ", user_input)
            return user_input;
# End input_f()

# User Input - Button callbacks (Activate when the button is pressed)
def button_1_callback(channel):
    global user_input;
    print("Button [1] - GPIO Pin [26] Pressed!")
    user_input = 1;
    sleep(0.1)

def button_2_callback(channel):
    global user_input;
    print("Button [2] - GPIO Pin [19] Pressed!")
    user_input = 2;
    sleep(0.1)

def button_3_callback(channel):
    global user_input;
    print("Button [3] - GPIO Pin [13] Pressed!")
    user_input = 3;
    sleep(0.1)

def button_4_callback(channel):
    global user_input;
    print("Button [4] - GPIO Pin [6] Pressed!")
    user_input = 4;
    sleep(0.1)

def button_5_callback(channel):
    global user_input;
    print("Button [5] - GPIO Pin [5] Pressed!")
    user_input = 5;
    sleep(0.1)

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
    display.lcd_clear()
    display.lcd_display_string("Enrolling print", 1)
    sleep(1)

    if fp_authenticate_access():
        print("Authenticated ... proceeding")
        display.lcd_clear()
        display.lcd_display_string("Authenticated", 1)
        display.lcd_display_string("Continuing...", 2)
        sleep(2)
    else: return

    print("Enrolling new fingerpint!");
    display.lcd_clear()
    display.lcd_display_string("Enrolling", 1)
    display.lcd_display_string("New print ...", 2)
    sleep(1)
    fp_enroll_new()
# End enroll_f()

def delete_f():
    display.lcd_clear()
    display.lcd_display_string("Deleting print", 1)
    sleep(1)

    if fp_authenticate_access():
        print("Authenticated ... proceeding")
        display.lcd_clear()
        display.lcd_display_string("Authenticated", 1)
        display.lcd_display_string("Continuing...", 2)
        sleep(2)
    else: return

    display.lcd_clear()
    display.lcd_display_string("Clearing Indexes", 1)
    t_stop = threading.Event();
    t = threading.Thread(target=long_string, args=(display, t_stop, "OPT: 1.ALL 2.SINGLE 5.BACK", 2,));
    t.start();

    user_button = input_f();

    t_stop.set();
    sleep(0.1)

    if user_input == 1:
        pass
        delete_all();
    elif user_input == 2:
        print("Removing single fingerprint")
        display.lcd_clear()
        display.lcd_display_string("Removing single", 1)
        display.lcd_display_string("fingerprint...", 2)
        sleep(2)
        delete_single();
    elif user_input == 3:
        fp_print_all();
    elif user_input == 5:
        return

    sleep(2)
# End delete_f()

# Tries to search the finger and activates the relay
def search_f():
    display.lcd_clear()
    display.lcd_display_string("Searching print", 1)
    sleep(1)

    f = fp_init()
    f = fp_read(f)
    if user_input == 5:
        return
    if fp_authenticate(f)[0]:
        GPIO.output(4, GPIO.HIGH)

    sleep(3)
    GPIO.output(4, GPIO.LOW)
    sleep(0.1)
# End search_f()

def index_f():
    display.lcd_clear()
    display.lcd_display_string("Searching index: ", 1)

    f = fp_init()

    tableIndex = f.getTemplateIndex(0)
    sleep(1)

    display.lcd_clear()
    display.lcd_display_string("Printing Indexes", 1)
    sleep(1)
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

    sleep(4)
# End index_f()

def exit_f():
    print("Exiting the program...");
    display.lcd_clear()
    display.lcd_display_string("Exiting program", 1)
    sleep(1)
# End exit_f()

def exception_f():
    print("Exception dettected, closing program...");
    display.lcd_clear()
    display.lcd_display_string("Exception thrown", 1)
    display.lcd_display_string("Exiting ...", 2)
    display.lcd_clear()
    GPIO.cleanup()
    sleep(2)
# End exception_f()

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
        sleep(2);
        return
    # End if
# End switch_f

### Driver program
try:
    def main():
        print("Booting up...");
        display.lcd_display_string("Booting up...", 1);
        sleep(1);

        while True:
            print("-------------------------------------");
            display.lcd_clear();
            display.lcd_display_string("Awaiting input: ", 1);

            t_stop = threading.Event();
            t = threading.Thread(target=long_string, args=(display, t_stop, "OPT: 1.ENRL 2.DEL 3.SEARCH 4.PRINT 5.EXIT", 2,));
            t.start();
            user_button = input_f()
            t_stop.set();
            sleep(0.1)

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
    abort_f();
# End except

# Catch any exception
except:
    print("Program Forcefully stopped - Cleaning up!");
    exception_f();
    exit(1);

def abort_f():
    print("Clearing the lcd screen text...");
    display.lcd_clear()
    display.lcd_display_string("Farewell...", 1)
    sleep(1)
    GPIO.cleanup()
    display.lcd_clear()
# End abort_f()

###########################################################
################# Local Helper Functions ##################
###########################################################
def fp_init():
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if (f.verifyPassword() == False):
        display.lcd_clear()
        display.lcd_display_string("Sesnor Init FAILED", 1)
        display.lcd_display_string("Password INVALID", 2)
        sleep(2)
        raise ValueError('The given fingerprint sensor password is wrong!')
    return f
# End fp_init()

def fp_read(f):
    global user_input;
    print('Waiting for finger...')
    display.lcd_clear()
    display.lcd_display_string("Place a finger", 1)
    display.lcd_display_string("OPT: 5.ABORT", 2)
    while (f.readImage() == False):
        if user_input == 5:
            print('Aborted!')
            display.lcd_clear()
            display.lcd_display_string("Aborted", 1)
            display.lcd_display_string("Recovering...", 2)
            sleep(2)
            return;
    return f
# End fp_read()

def fp_authenticate_access():
    f = fp_init()

    print("Authenticate for Access!");
    display.lcd_clear()
    display.lcd_display_string("Authenticate", 1)
    display.lcd_display_string("For root Access:", 2)
    sleep(2)

    f = fp_read(f)
    if user_input == 5:
        return False
    return fp_authenticate(f)[0]
# End fp_authenticate_access

def fp_authenticate(f):
    f.convertImage(0x01)
    result = f.searchTemplate()
    position = result[0]
    accuracy = result[1]

    print("(fp_authenticate) Position is: ", position)

    if (position == -1):
        print('No match found!')
        display.lcd_clear()
        display.lcd_display_string("Auth FAILED", 1)
        display.lcd_display_string("No match found!", 2)
        sleep(1)
        return False, position, accuracy;
    else:
        score = "Acc score: " + str(accuracy)
        print('Found template at position #' + str(position))
        print('The accuracy score is: ' + str(accuracy))
        display.lcd_clear()
        display.lcd_display_string("Auth SUCCESSFUL", 1)
        display.lcd_display_string(score, 2)
        sleep(1)
        return True, position, accuracy;
    # End if
# End fp_authenticate

def fp_enroll_new():
    f = fp_init();
    f = fp_read(f);
    sleep(0.1)
    if user_input == 5: return
    f.convertImage(0x01)
    position = f.searchTemplate()[0]

    if ( position >= 0 ):
        print('Template already exists at position #' + str(position))
        display.lcd_clear()
        display.lcd_display_string("Print already", 1)
        display.lcd_display_string("enrolled...", 2)
        sleep(2)
        display.lcd_clear()
        display.lcd_display_string("Aborting process", 1)
        display.lcd_display_string("Recovering...", 2)
        sleep(2)
        return
    #End if

    print('Remove finger...')
    display.lcd_clear()
    display.lcd_display_string("Remove finger...", 1)
    sleep(1)

    f = fp_read(f)
    sleep(0.1)
    if user_input == 5: return
    f.convertImage(0x02)
    if ( f.compareCharacteristics() == 0 ):
        print("Prints do not match ... Aborting")
        display.lcd_clear()
        display.lcd_display_string("Prints do not", 1)
        display.lcd_display_string("match...", 2)
        sleep(2)
        display.lcd_clear()
        display.lcd_display_string("Aborting process", 1)
        display.lcd_display_string("Recovering...", 2)
        sleep(2)
        return
    #End if

    # Creates a template
    f.createTemplate()
    position = f.storeTemplate()

    display.lcd_clear()
    display.lcd_display_string("Print enrolled", 1)
    display.lcd_display_string("SUCCESSFULLY...", 2)
    print('Print enrolled successfully!')
    print('New template position #' + str(position))

    sleep(1)
# End enroll_new_f

def delete_all():
    display.lcd_clear()
    display.lcd_display_string("Deleting all...", 1)

    f = fp_init()
    tableIndex = f.getTemplateIndex(0)
    sleep(0.2)

    display.lcd_clear()
    display.lcd_display_string("Searching Indexes", 1)
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
                display.lcd_clear()
                display.lcd_display_string("ABORTING ...", 1)
                display.lcd_display_string("Delete Failed!", 2)
                sleep(2)
                return;

    if indexes_list != "":
        display.lcd_clear()
        indexes_found = "Total found:" + str(indexes_counter)
        display.lcd_display_string(indexes_found, 1)
        display.lcd_display_string(indexes_list, 2)
        print("Indexes found!");
        sleep(1)
        print("Index list cleared:")
        print("Index list was: ", indexes_list)
        display.lcd_clear()
        display.lcd_display_string("All templates", 1)
        display.lcd_display_string("Cleared ...", 2)
    else:
        display.lcd_clear()
        display.lcd_display_string("Indexes empty", 1)
        display.lcd_display_string("No prints stored", 2)
        print("Indexes not found!");
    sleep(4)
# End delete_all

def delete_single():
    f = fp_init()
    f = fp_read(f)
    result = fp_authenticate(f)
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

    if result[1] == 0: 
        display.lcd_clear()
        display.lcd_display_string("Action ABORTED!", 1)
        sleep(1)
        display.lcd_clear()
        display.lcd_display_string("UNABLE to Remove", 1)
        display.lcd_display_string("Root acess print", 2)
        sleep(4)
        return

    if result[0]:
        if f.deleteTemplate(result[1]):
            deleted = "Template [ " + str(result[1]) + " ]"
            display.lcd_clear()
            display.lcd_display_string(deleted, 1)
            display.lcd_display_string("Has been cleared", 2)
            print(deleted + " has been cleared")
        else:
            display.lcd_clear()
            display.lcd_display_string("Action FAILED", 1)
            display.lcd_display_string("Failed to clear!", 2)
            print("Failed to clear", deleted)
    sleep(2)
# End delete_single

def fp_print_all(f):
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    print("Printing all used templates!");
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
# End fp_print_all

# @param display    - driver screen (lcd)
# @param stop_event - flag to stop the thread
# @param text       - string to print
# @param line       - number of line to print
# @param colum      - number of columns of your display
# @return This function send to display your scrolling string.
def long_string(display, stop_event, text = '', line = 1, colum = 16):
    if(len(text) > colum):
        display.lcd_display_string(text[:colum],line)
        sleep(1)
        for i in range(len(text) - colum + 1):
            if stop_event.is_set():
                break
            text_to_print = text[i:i + colum]
            display.lcd_display_string(text_to_print,line)
            sleep(0.4)
        sleep(1)
    else:
        display.lcd_display_string(text, line)
    # End if
# End long_string

if __name__ == "__main__":
    main();
    abort_f();
# End ___main___