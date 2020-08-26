#!/usr/bin/python
# -*- coding: utf-8 -*-
from libs.pyfingerprint import PyFingerprint
from libs.lcddriver import lcd
from libs.userInput import userInput
from time import sleep, time
import RPi.GPIO as GPIO

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

# User Input - Input control
usr = userInput()

# User Input - Button callbacks (Activate when the button is pressed)
def button_callback(channel):
    usr.setUserInput(channel)

# Event listeners that activate the callback functions (Bounce controls accidental button triggers)
GPIO.add_event_detect(26, GPIO.RISING, callback = button_callback, bouncetime=200)
GPIO.add_event_detect(19, GPIO.RISING, callback = button_callback, bouncetime=200)
GPIO.add_event_detect(13, GPIO.RISING, callback = button_callback, bouncetime=200)
GPIO.add_event_detect(6, GPIO.RISING, callback = button_callback, bouncetime=200)
GPIO.add_event_detect(5, GPIO.RISING, callback = button_callback, bouncetime=200)

######################## Main Program Functions ########################
def enroll_f():
    display.lcd_print("Enrolling print")
    sleep(1)

    if not setup_f(): return

    print("Enrolling new fingerpint!")
    display.lcd_print("Enrolling", "New print ...")
    sleep(1)
    fp_enroll_new()

def delete_f():
    display.lcd_print("Deleting prints")
    sleep(1)

    display.lcd_print("Clearing Indexes")
    display.lcd_print_long("OPT: 1.ALL 2.SINGLE 3.PRINT 5.BACK", 2)
    usr.handleUserInput()
    display.lcd_t_stop_set()
    sleep(0.1)

    if usr.getUserInput() == 1:
        fp_delete_all()
    elif usr.getUserInput() == 2:
        fp_delete_single()
    elif usr.getUserInput() == 3:
        fp_print_all()
    elif usr.getUserInput() == 5:
        display.lcd_print("Aborted", "Returning...")
        sleep(1)
        return

def search_f():
    display.lcd_print("Searching print!")
    sleep(1)

    f = fp_init()
    start_time = time()
    if not fp_read(f): return
    if fp_authenticate(f)[0]:
        print("Sucessful Execution time --- %s seconds ---" % (time() - start_time))
        GPIO.output(4, GPIO.HIGH)
        sleep(3)
        GPIO.output(4, GPIO.LOW)
        sleep(0.1)
        return
    print("Faliure Execution time --- %s seconds ---" % (time() - start_time))

def index_f():
    fp_print_all()
    sleep(0.2)

def setup_f():
    f = fp_init()
    number = f.getTemplateCount()

    print("Total template count = ", number)
    if number == 0:
        display.lcd_print("Root print not", "Dettected...!")
        sleep(2)
        display.lcd_print("Create new root?", "OPT:  1.YES 5.NO")
        usr.handleUserInput()
        sleep(0.1)
        if usr.getUserInput() == 5:
            return False
        return True
    else:
        return fp_authenticate_root_access(f)


######################## Local Helper Functions ########################
def fp_init():
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if (f.verifyPassword() == False):
        display.lcd_print("Sesnor Init FAILED", "Password INVALID")
        sleep(2)
        raise ValueError('The given fingerprint sensor password is wrong!')
    return f

def fp_read(f):
    print('Waiting for finger...')
    display.lcd_print("Place a finger", "OPT:     5.ABORT")
    while (f.readImage() == False):
        if usr.getUserInput() == 5:
            display.lcd_print("Aborted", "Recovering...")
            sleep(1)
            return False
    return True

def fp_authenticate_root_access(f):
    if fp_authenticate_access(f):
        print("Authenticated ... proceeding")
        sleep(1)
        return True
    else: return False

def fp_authenticate_access(f):
    print("Authenticate for Access!")
    display.lcd_print("Authenticate", "For root Access:")
    sleep(2)

    if not fp_read(f): return
    result = fp_authenticate(f)
    sleep(1)
    if usr.getUserInput() == 5:
        return False
    if result[1] == 0:
        print("Access Granted!")
        display.lcd_print("Access Granted!")
        sleep(1)
        return True
    else:
        print("Access Failed!")
        display.lcd_print("Access Failed!", "Need Root Access")
        sleep(2)
        return False

def fp_authenticate(f):
    f.convertImage(0x01)
    result = f.searchTemplate()
    position = result[0]
    accuracy = result[1]

    if (position == -1):
        print('No match found!')
        display.lcd_print("Auth FAILED", "No match found!")
        sleep(1)
        return False, position, accuracy
    else:
        score = 'Pos [' + str(position) + '] Ac [' + str(accuracy) + ']'
        print('Found template at position #' + str(position))
        print('The accuracy score is: ' + str(accuracy))
        display.lcd_print("Auth SUCCESSFUL", score)
        return True, position, accuracy

def fp_enroll_new():
    f = fp_init()
    if not fp_read(f): return
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

    if not fp_read(f): return
    f.convertImage(0x02)
    if ( f.compareCharacteristics() == 0 ):
        print("Prints do not match ... Aborting")
        display.lcd_print("Prints do not", "match...")
        sleep(2)
        display.lcd_print("Aborting process", "Recovering...")
        sleep(1)
        return

    f.createTemplate()
    position = f.storeTemplate()
    display.lcd_print("Print enrolled", "SUCCESSFULLY...")
    print('Print enrolled successfully!')
    print('New template position #' + str(position))
    sleep(1)

def fp_delete_all():
    print("Removing all fingerprints")
    display.lcd_print("ROOT Action...", "Detected...!")
    sleep(2)

    f = fp_init()
    if not fp_authenticate_root_access(f): return
    display.lcd_print("Removing ALL", "fingerprints...")
    delete_all(f)
    sleep(2)
    print("Prints Deleted ... SUCCESSFULLY")
    display.lcd_print("Prints Deleted", "SUCCESSFULLY...")
    sleep(1)

def delete_all(f):
    for page in range(0, 4):
        tableIndex = f.getTemplateIndex(page)
        for position in range(0, len(tableIndex)):
            if str(tableIndex[position]) == "True":
                if f.deleteTemplate(position):
                    print('Template at position #' + str(position) + ' Removed!')
                else:
                    print('FAILED to delete Template at position #' + str(position))
                    sleep(1)
                    return

def fp_delete_single():
    print("Removing single fingerprint")
    display.lcd_print("ROOT Action...", "Detected...!")
    sleep(2)

    f = fp_init()
    if not fp_authenticate_root_access(f): return
    display.lcd_print("Removing single", "fingerprint...")
    sleep(2)
    if not fp_read(f): return
    result = fp_authenticate(f)
    position = result[1]
    authenticated = result[0]
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

    if position == 0:
        display.lcd_print("Action ABORTED!")
        sleep(1)
        display.lcd_print("ROOT acess print", "UNABLE to remove")
        sleep(4)
        return

    sleep(1)
    if authenticated:
        if f.deleteTemplate(position):
            deleted = "Template [ " + str(position) + " ]"
            display.lcd_print(deleted, "Has been cleared")
            print(deleted + " has been cleared")
        else:
            print("Failed to clear", deleted)
            display.lcd_print("Action FAILED", "Failed to clear!")
    else:
        print("Failed to Authenticate!")
        display.lcd_print("Action ABORTED!")
        sleep(1)
        display.lcd_print("Authentication", "FAILED!!!")
    sleep(2)

def fp_print_all():
    f = fp_init()
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    indexes = map_all(f)
    total = 'Total =  [' + str(len(indexes)) + ']'
    display.lcd_print("Template list", total)
    sleep(2)

    display.lcd_print("Print every pos?", "OPT:  1.YES 5.NO")
    usr.handleUserInput()
    sleep(0.1)

    if usr.getUserInput() == 1:
        total = "|"
        for index in indexes:
            total = total + str(index) + '|'
        display.lcd_print("OPT:      5.BACK")
        display.lcd_print_long(total, 2)
        usr.handleUserInput()
        display.lcd_t_stop_set();
        sleep(0.1)
    elif usr.getUserInput() == 5:
        return

def map_all(f):
    indexes = []
    for page in range(0, 4):
        tableIndex = f.getTemplateIndex(page)
        for i in range(0, len(tableIndex)):
            if str(tableIndex[i]) == "True":
                indexes.append(str(i))
                print('Template at position #' + str(i) + ' is used: ' + str(tableIndex[i]))
    return indexes

def switch_f(arg):
    switch = {
        1: enroll_f,
        2: delete_f,
        3: search_f,
        4: index_f,
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
            display.lcd_print("Awaiting input: ")
            display.lcd_print_long("OPT: 1.ENRL 2.DEL 3.SEARCH 4.PRINT 5.EXIT", 2)
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
    main()
    exit_f()