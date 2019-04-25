import RPi.GPIO as GPIO  
import time
from time import sleep
import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import threading

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
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    objThread = threading.Thread(target=check_for_people, args=())
    objThread.daemon = True
    objThread.start()
    app.run(host='0.0.0.0', debug=False)  
