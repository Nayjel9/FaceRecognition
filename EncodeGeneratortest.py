import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimecriminaldetection.appspot.com"
})

# Importing Criminal Images
folderPath = 'Images'
PathList = os.listdir(folderPath)
imgList = []
CriminalIds = []

for path in PathList:
    full_path = os.path.join(folderPath, path)
    imgList.append(cv2.imread(full_path))
    CriminalIds.append(os.path.splitext(path)[0])

    # Upload the image to Firebase Storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, CriminalIds]
print("Encoding Complete")

# Save the facial encodings to a file
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")

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

    # Store the criminal data in the Firebase Realtime Database
    ref = db.reference('Criminals')
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

app = tk.Tk()
app.title("Facial Recognition and Criminal Data Entry")

# Create GUI widgets
label_id = ttk.Label(app, text="Criminal ID:")
entry_id = ttk.Entry(app)

label_name = ttk.Label(app, text="Name:")
entry_name = ttk.Entry(app)

label_criminal_no = ttk.Label(app, text="Criminal No.:")
entry_criminal_no = ttk.Entry(app)

label_date_time = ttk.Label(app, text="Date and Time Detected:")
entry_date_time = ttk.Entry(app)

submit_button = ttk.Button(app, text="Submit", command=submit_data)

# Arrange the widgets on the window using grid layout
label_id.grid(row=0, column=0)
entry_id.grid(row=0, column=1)

label_name.grid(row=1, column=0)
entry_name.grid(row=1, column=1)

label_criminal_no.grid(row=2, column=0)
entry_criminal_no.grid(row=2, column=1)

label_date_time.grid(row=3, column=0)
entry_date_time.grid(row=3, column=1)

submit_button.grid(row=4, column=0, columnspan=2)

# Real-time Criminal Detection using Face Recognition
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1280, 720))

    # Face recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Match faces with known criminals
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(encodeListKnownWithIds[0], face_encoding)
        name = "Unknown"

        if True in matches:
            matched_index = matches.index(True)
            name = encodeListKnownWithIds[1][matched_index]

        # Draw a rectangle around the face and display the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    cv2.imshow("Real-time Criminal Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
app.mainloop()
