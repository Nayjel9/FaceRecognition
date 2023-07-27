import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimecriminaldetection.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#Importing images
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    full_path = os.path.join(folderModePath, path)
    imgModeList.append(cv2.imread(full_path))

#load the encoding file
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, CriminalIds = encodeListKnownWithIds
#print(CriminalIds)
print("Encode File Loaded")


modeType = 0
counter = 0
id = -1
imgCriminal = []

while True:
    success, img = cap.read()
    
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    
    
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        #print("matches", matches)
        #print("FaceDis", faceDis)
        
        matchIndex = np.argmin(faceDis)
        #print("Match Index", matchIndex)
        
        if matches[matchIndex]:
            #print("Wanted Criminal Detected")
            #print(CriminalIds[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, y2 - y1, x2 - x1  # Swap h and w
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = CriminalIds[matchIndex]           
            if counter == 0:
                counter = 1
                modeType = 1
                
    if counter!= 0:
        
        if counter ==1:            
            #get data
            criminalInfo = db.reference(f'Criminals/{id}').get()
            print(criminalInfo)
            #Get data from storage
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgCriminal = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            
            datetimeObject = datetime.strptime(criminalInfo['date_and_time_detected'],
                                              "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)
            ref = db.reference(f'Criminals/{id}')
            ref.child('date_and_time_detected').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
        if counter<= 30:    
            cv2.putText(imgBackground, str(criminalInfo['criminal_no']), (1050, 495),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(criminalInfo['name']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(criminalInfo['date_and_time_detected']), (920, 620),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
            
            imgBackground[175:175+216, 909:909+216] = imgCriminal
        
        counter+=1
        
        
        if counter>=30:
            counter = 0
            modeType = 0
            criminalInfo = []
            imgCriminal = []
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    
    cv2.imshow("Criminal", imgBackground)
    cv2.waitKey(1)

