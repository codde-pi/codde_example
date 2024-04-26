"""    
This code will control Raspberry Pi GPIO PWM on four GPIO pins thanks to CODDE Pi Framework. 
The code test ran with L298N H-Bridge driver module connected.
The virtual controller sending instructions run on a mobile phone with CODDE Pi App.

Website:	www.codde-pi.com 
Date:		24/04/20224 
"""     
from gpiozero import PWMOutputDevice  
from gpiozero import DigitalOutputDevice  
from time import sleep, time
import RPi.GPIO as GPIO
import subprocess
import codde_protocol as cp
import time

#///////////////// Define Motor Driver GPIO Pins /////////////////  

# Motor A, Left Side GPIO CONSTANTS  
PWM_DRIVE_LEFT = 21
# ENA - H-Bridge enable pin  
REVERSE_LEFT_PIN = 20	
# IN1 - Forward Drive  
FORWARD_LEFT_PIN = 16	
# IN2 - Reverse Drive  # Motor B, Right Side GPIO CONSTANTS  
PWM_DRIVE_RIGHT = 15 # previously 18		
# ENB - H-Bridge enable pin  
REVERSE_RIGHT_PIN = 12	
# IN1 - Forward Drive  
FORWARD_RIGHT_PIN = 23	
# IN2 - Reverse Drive     
# Initialise objects for H-Bridge GPIO PWM pins  
# Set initial duty cycle to 0 and frequency to 1000  
driveLeft = PWMOutputDevice(pin=PWM_DRIVE_LEFT, active_high=True, initial_value=0, frequency=1000)  
driveRight = PWMOutputDevice(pin=PWM_DRIVE_RIGHT, active_high=True, initial_value=0, frequency=1000) 
# Initialise objects for H-Bridge digital GPIO pins  
forwardLeft = DigitalOutputDevice(FORWARD_LEFT_PIN)  
reverseLeft = DigitalOutputDevice(REVERSE_LEFT_PIN)  
forwardRight = DigitalOutputDevice(FORWARD_RIGHT_PIN)  
reverseRight = DigitalOutputDevice(REVERSE_RIGHT_PIN)     
interlock = DigitalOutputDevice(24)

# Start WebSocket server
server = cp.ComSocketServer('192.168.0.40:12345')

# //////////////////////////////// Common methods ////////////////////////////

def allStop():  	
    interlock.value = False
    forwardLeft.value = False  	
    reverseLeft.value = False  	
    forwardRight.value = False  	
    reverseRight.value = False  	
    driveLeft.value = 0  	
    driveRight.value = 0     

def forwardDrive():
    interlock.value = True
    forwardLeft.value = True  	
    reverseLeft.value = False  
    forwardRight.value = True  	
    reverseRight.value = False  	
    driveLeft.value = 1.0  	
    driveRight.value = 1.0     

def reverseDrive():
    interlock.value = True
    forwardLeft.value = False  	
    reverseLeft.value = True  	
    forwardRight.value = False  	
    reverseRight.value = True  	
    driveLeft.value = 1.0  	
    driveRight.value = 1.0     

def spinLeft():  	
    forwardLeft.value = False  	
    reverseLeft.value = True  	
    forwardRight.value = True  	
    reverseRight.value = False  	
    driveLeft.value = 1.0  	
    driveRight.value = 1.0     

def SpinRight():  	
    forwardLeft.value = True  	
    reverseLeft.value = False  	
    forwardRight.value = False  	
    reverseRight.value = True  	
    driveLeft.value = 1.0  	
    driveRight.value = 1.0     

def forwardTurnLeft():  	
    interlock.value = True
    forwardLeft.value = True  	
    reverseLeft.value = False  	
    forwardRight.value = True  	
    reverseRight.value = False  	
    driveLeft.value = 0.2  	
    driveRight.value = 0.8     

def forwardTurnRight():
    interlock.value = True
    forwardLeft.value = True  
    reverseLeft.value = False
    forwardRight.value = True 
    reverseRight.value = False  	
    driveLeft.value = 0.8
    driveRight.value = 0.2

def camera():
    subprocess.Popen(['mjpg_streamer', '-i', '"input_uvc.so -r 640x480 -f 10 -d /dev/video0 -y"', '-o', '"output_http.so -p 8080 -w /usr/local/share/mjpg-streamer/www”'])

# /////////////////// Handle CODDE Protocol events ////////////////////////////

def press_button_1(*args):
    widget: cp.ToggleButton = args[0]
    print('press' if widget.pressed else 'release')
    allStop()
    if widget.pressed:
        forwardDrive()

def directional_button_3(*args):
    widget = args[0]
    print('direction', widget.direction)
    if widget.direction == 1:
        forwardDrive()
    elif widget.direction == 2:
        forwardTurnRight()
    elif widget.direction == 3:
        reverseDrive()
    elif widget.direction == 4:
        forwardTurnLeft()
    else:
        allStop()


if __name__ == '__main__':
    camera()
    print('open server...')
    server.open()
    server.on(1, "PressButton", press_button_1)
    server.on(3, "DirectionalButton", directional_button_3)
    # server.callback(1, cp.ServerStatus.Idle, cp.ConfirmResult(True)) 
    try:
        server.serve()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Oh! you pressed CTRL + C.")
        print("Program interrupted.")
    finally:
        server.close()

