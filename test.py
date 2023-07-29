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
imgBackground = cv2.imread('Resources/background.png')
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

# GUI functions
def select_png_file():
    global imgCriminal
    file_path = tk.filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    imgCriminal = cv2.imread(file_path)

def submit_data():
    criminal_id = entry_id.get()
    name = entry_name.get()
    criminal_no = entry_criminal_no.get()
    date_time_detected = entry_date_time.get()

    data = {
        "name": name,
        "criminal_no": criminal_no,
        "date_and_time_detected": date_time_detected
    }

    ref.child(criminal_id).set(data)
    reset_fields()
    show_notification()

def reset_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_criminal_no.delete(0, tk.END)
    entry_date_time.delete(0, tk.END)

def show_notification():
    messagebox.showinfo("Notification", "Another criminal has been added to the database.")

# Create the GUI window
app = tk.Tk()
app.title("Real-time Criminal Detection")

label_id = ttk.Label(app, text="Criminal ID:")
entry_id = ttk.Entry(app)

label_name = ttk.Label(app, text="Name:")
entry_name = ttk.Entry(app)

label_criminal_no = ttk.Label(app, text="Criminal No.:")
entry_criminal_no = ttk.Entry(app)

label_date_time = ttk.Label(app, text="Date and Time Detected:")
entry_date_time = ttk.Entry(app)

select_png_button = ttk.Button(app, text="Select PNG", command=select_png_file)
submit_button = ttk.Button(app, text="Submit", command=submit_data)

label_id.grid(row=0, column=0)
entry_id.grid(row=0, column=1)

label_name.grid(row=1, column=0)
entry_name.grid(row=1, column=1)

label_criminal_no.grid(row=2, column=0)
entry_criminal_no.grid(row=2, column=1)

label_date_time.grid(row=3, column=0)
entry_date_time.grid(row=3, column=1)

select_png_button.grid(row=4, column=0)
submit_button.grid(row=4, column=1)

# Variables for criminal detection
modeType = 0
counter = 0
id = -1
imgCriminal = []

# Start the real-time criminal detection loop
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
    
    cv2.imshow("Criminal", imgBackground)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
