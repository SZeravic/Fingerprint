#!/usr/bin/python
from libs.userInput import userInput
from libs.lcddriver import lcd;
from time import sleep;
import RPi.GPIO as GPIO
import subprocess

# Load the driver and set it to "display"
display = lcd()

# User Input - Input control
usr = userInput()

# User Input - Button callbacks (Activate when the button is pressed)
def button_callback(channel):
    usr.setUserInput(channel)

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

def start_f():
    print("Calling control program (rp_fingerprint.py)")
    display.lcd_print("Starting up...")
    sleep(2)
    GPIO.cleanup()
    subprocess.call(['python', '/home/pi/Desktop/Fingerprint/Project/src/rp_fingerprint.py'])
    sleep(0.5)
    GPIO_setup()

def restart_f():
    print("Restarting Raspberry Pi")
    display.lcd_print("Restarting Pi...", "Be right back...")
    sleep(2)
    display.lcd_clear()
    GPIO.cleanup()
    sleep(1)
    subprocess.call("sudo reboot", shell=True)

def shutdown_f():
    print("Shutting Down Raspberry Pi")
    display.lcd_print("Shutting Down Pi", "Goodbye... =(")
    sleep(2)
    display.lcd_clear()
    GPIO.cleanup()
    sleep(1)
    subprocess.call("sudo shutdown -h now", shell=True)

def switch_f(arg):
    switch = {
        1: start_f,
        2: restart_f,
        3: shutdown_f,
    }

    func = switch.get(arg, "Invalid")
    if (func != "Invalid"):
        return func()
    else:
        print("Invalid Input ... Try again")
        display.lcd_print("Invalid Input ...", "Please try again")
        sleep(2)
        return

try:
    def main():
        print("Raspbeery Pi - Booting up...");
        display.lcd_print("Pi booting up...")
        sleep(2);

        while True:
            print("-------------------------------------")
            display.lcd_print("Select Option: ")
            display.lcd_print_long("OPT: 1.START 2.RESTART 3.SHUTDOWN 5.EXIT", 2)
            usr.handleUserInput()
            display.lcd_t_stop_set();
            sleep(0.1)

            if usr.getUserInput() == 5:
                sleep(1)
                display.lcd_print("Are you sure?: ", "OPT:  1.NO 5.YES")
                usr.handleUserInput()
                if usr.getUserInput() == 5:
                    display.lcd_print("Goodbye... =(")
                    sleep(2)
                    break
                else: continue
            switch_f(usr.getUserInput())

        print("Exiting main_startup.py")

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
    display.lcd_print("Exiting program!")
    sleep(1)
    GPIO.cleanup()
    display.lcd_clear()

if __name__ == "__main__":
    GPIO_setup()
    main()
    exit_f()