#!/usr/bin/python
from libs.lcddriver import lcd;
from time import sleep;
import subprocess

try:
    # Load the driver and set it to "display"
    display = lcd()

    print("Raspbeery Pi - Booting up...");
    display.lcd_clear()
    display.lcd_display_string("Pi Booting up...", 1);
    sleep(2);

    display.lcd_clear()
    display.lcd_display_string("Calling py file:", 1);
    display.lcd_display_string("rp_startup.py", 2);
    sleep(1);

    display.lcd_clear()
    display.lcd_display_string("Calling py file:", 1);
    display.lcd_display_string("rp_fingerprint", 2);
    sleep(1);

    subprocess.call(['python', '/home/pi/Desktop/Fingerprint/Project/src/rp_fingerprint.py'])

except BaseException as e:
    print("Program Forcefully stopped - Cleaning up!")
    print('Exception message: ' + str(e))
    exit(1)