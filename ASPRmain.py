import cv2
import sys
import RPi.GPIO as GPIO
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading

#declare motor variables m1in1(motor 1 input 1) 
m1in1 = 11
m1in2 = 15
m2in1 = 16
m2in2 = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(m1in1, GPIO.OUT)
GPIO.setup(m1in2, GPIO.OUT)
GPIO.setup(m2in1, GPIO.OUT)
GPIO.setup(m2in2, GPIO.OUT)
GPIO.output(m1in1 , False)
GPIO.output(m1in2 , False)
GPIO.output(m2in1 , False)
GPIO.output(m2in2 , False)
print ("GPIO inputs declared.")


email_update_interval = 30 #interval in seconds for time between email notifications
video_camera = VideoCamera() # creates a camera object. Calls function from Picam
#model template loaded in object classifier. I am using haarcascade face model. Other models in the CaarHascade folder
object_classifier = cv2.CascadeClassifier("/home/pi/Documents/ASPR/HaarCascade/haarcascade_profileface.xml")


#initiate flask and authentication
app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'ASPR'
app.config['BASIC_AUTH_PASSWORD'] = 'ASPR'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
#timeStart starts at zero but lately given time as variable
timeStart = 0

def check_for_people():
    global timeStart
    while True:
        try:
            frame, found_intruder = video_camera.get_object(object_classifier)
            if found_intruder and (time.time() - timeStart) > email_update_interval:
                timeStart = time.time()
                print ("Sending email...")
                sendEmail(frame)
                print ("email sent")
        except:
            print ("Error sending email: script process will be terminated ")
            sys.exit(0)

@app.route('/')
@basic_auth.required
def index():
    return render_template('webcontrol.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(m1in1 , False)
    GPIO.output(m1in2 , False)
    GPIO.output(m2in1 , True)
    GPIO.output(m2in2 , False)
    return 'true'

@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(m1in1 , True)
   GPIO.output(m1in2 , False)
   GPIO.output(m2in1 , False)
   GPIO.output(m2in2 , False)
   return 'true'

@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(m1in1 , False)
   GPIO.output(m1in2 , True)
   GPIO.output(m2in1 , False)
   GPIO.output(m2in2 , True)
   return 'true'

@app.route('/down_side')
def down_side():
   data1="BACKWARD"
   GPIO.output(m1in1 , True)
   GPIO.output(m1in2 , False)
   GPIO.output(m2in1 , True)
   GPIO.output(m2in2 , False)
   return 'true'

@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(m1in1 , False)
   GPIO.output(m1in2 , False)
   GPIO.output(m2in1 , False)
   GPIO.output(m2in2 , False)
   return  'true'

if __name__ == '__main__':
    objThread = threading.Thread(target=check_for_people, args=())
    objThread.daemon = True
    objThread.start()
    app.run(host='0.0.0.0', debug=False)

