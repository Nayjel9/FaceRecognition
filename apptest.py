import cv2
import torch
import numpy as np
import os
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from flask import Flask, render_template, Response, request, redirect, url_for
from flask import Flask
from yolov5.models.experimental import attempt_load
from yolov5.utils.general import non_max_suppression
import serial

ser = serial.Serial('COM5', 9600)

# Load Firebase credentials and initialize the app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimecriminaldetection.appspot.com"
})

bucket = storage.bucket()

# Load the YOLOv5 model
path = 'model/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path, force_reload=True)

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image and mode images
imgBackground = cv2.imread('Resources/background2.png')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load the face encoding file
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, CriminalIds = encodeListKnownWithIds
print("Encode File Loaded")

# Variables for criminal detection
modeType = 0
counter = 0
id = -1
imgCriminal = []

# Flask app initialization
app = Flask(__name__)

def control_siren(command):
    ser.write(command.encode())

# Create a dummy login check function for demonstration purposes
def check_login(username, password):
    return username == "123456" and password == "123456"

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        police_number = request.form['police_number']
        password = request.form['password']
        
        # Perform the check_login function here to validate the credentials
        if check_login(police_number, password):
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

def gen():
    global imgBackground, modeType, counter, id, imgCriminal

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))
        results = model(frame)
        frame = np.squeeze(results.render())

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = frame
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        # Criminal detection code
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, y2 - y1, x2 - x1  # Swap h and w
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = CriminalIds[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 1
                    control_siren('ON')
            else:
                # If the face is not recognized from the database, add "Unknown" label and draw a red box
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(imgBackground, (55 + x1, 162 + y1), (55 + x2, 162 + y2), (0, 0, 255), 2)
                cv2.putText(imgBackground, "Civilian", (55 + x1 + 6, 162 + y1 - 6),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
                control_siren('OFF')
                    
        if counter != 0:
            
            if counter == 1:            
                # Get data
                criminalInfo = db.reference(f'Criminals/{id}').get()
                # Get data from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgCriminal = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                
                datetimeObject = datetime.strptime(criminalInfo['date_and_time_detected'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                ref = db.reference(f'Criminals/{id}')
                ref.child('date_and_time_detected').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
            if counter <= 30:    
                cv2.putText(imgBackground, str(criminalInfo['criminal_no']), (1050, 495),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(criminalInfo['name']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(criminalInfo['date_and_time_detected']), (920, 620),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                
                imgBackground[175:175 + 216, 909:909 + 216] = imgCriminal
            
            counter += 1
            
            if counter >= 30:
                counter = 0
                modeType = 0
                criminalInfo = []
                imgCriminal = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        
        ret, buffer = cv2.imencode('.jpg', imgBackground)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

cap.release()
cv2.destroyAllWindows()
