import RPi.GPIO as GPIO  
import time
from time import sleep

GPIO.setmode(GPIO.BOARD) # Sets the pin numbering system to use the physical layout
GPIO.setwarnings(False)
m1in1 = 11
m1in2 = 15
m2in1 = 16
m2in2 = 18

#set up trigger and echo for ultrasonic sensor
TRIG = 7
ECHO = 22

GPIO.setup(m1in1, GPIO.OUT)
GPIO.setup(m1in2, GPIO.OUT)
GPIO.setup(m2in1, GPIO.OUT)
GPIO.setup(m2in2, GPIO.OUT)


GPIO.setup(3,GPIO.OUT)  # Sets up pin 3 to an output (instead of an input)
pwm = GPIO.PWM(3, 50)     # Sets up pin 3 as a PWM pin
pwm.start(0)               # Starts running PWM on the pin and sets it to 0

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

def measure():
  
  GPIO.output(TRIG, False)
  #sensor is warming up
  time.sleep(2)
  
  #turns on ultrasonic sensor
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  #turns off ultrasonic sensor
  GPIO.output(TRIG, False)
  
  #calculate distance from sensor reading
  while GPIO.input(ECHO)==0:
    start = time.time()

  while GPIO.input(ECHO)==1:
    stop = time.time()

  duration = stop-start
  distance = duration * 17150
  distance = round(distance,2)

  return distance
def reverse(sec):

 GPIO.output(m1in1, True)
 GPIO.output(m1in2, False)
 GPIO.output(m2in1, True) 
 GPIO.output(m2in2, False)
 time.sleep(sec)
 
def forward(sec):

 GPIO.output(m1in1, False)
 GPIO.output(m1in2, True)
 GPIO.output(m2in1, False) 
 GPIO.output(m2in2, True)
 time.sleep(sec)
 
 
def turn_left(sec):
 
 GPIO.output(m1in1, False)
 GPIO.output(m1in2, True)
 GPIO.output(m2in1, True) 
 GPIO.output(m2in2, False)
 time.sleep(sec)
 
 
def turn_right(sec):
 
 GPIO.output(m1in1, True)
 GPIO.output(m1in2, False)
 GPIO.output(m2in1, False) 
 GPIO.output(m2in2, True)
 time.sleep(sec)

def stop():
 
 GPIO.output(m1in1, False)
 GPIO.output(m1in2, False)
 GPIO.output(m2in1, False) 
 GPIO.output(m2in2, False)
 

try:

    while True:
            
        pwm.ChangeDutyCycle(1)     
        sleep(1)
        checkRight = measure()
        print ("Distance : %.lf cm" % checkRight)
        time.sleep(1)

        pwm.ChangeDutyCycle(3)     
        sleep(1)
        checkMid = measure()
        print ("Distance : %.1f cm" % checkMid)
        time.sleep(1)
        
        pwm.ChangeDutyCycle(5)     
        sleep(1)
        checkLeft = measure()
        print ("Distance : %.1f cm \n" % checkLeft )
        time.sleep(1)
        
        
        if checkRight >= 30  and checkMid >= 30 and checkLeft >= 40:
            print("going forward \n \n")
            forward(.75)
            stop()
           
        elif checkRight < 30 and checkMid >= 30 and checkLeft >= 40:
            print("Something to my Right, turning left\n \n")
            turn_left(.5)
            stop()
            
        elif checkLeft < 40 and checkMid >= 30 and checkRight >= 30:
            print("Something to my left, turn right \n \n")
            turn_right(.5)
            stop()
            
        elif checkMid < 30 and checkRight >= 30 and checkLeft >= 40:
            print("something in front of me, reversing. \n \n")
            reverse(1)
            stop()
        else:
            print("stuff all around me. Just gunna back up and go left. \n")
            reverse(1)
            turn_left(1)
            stop()
           
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
