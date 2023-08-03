import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, storage, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimecriminaldetection.appspot.com"
})

storage_bucket = storage.bucket()
ref = db.reference('Criminals')

# Function to perform face encoding and upload images to Firebase Storage
def perform_face_encoding_and_upload():
    folderPath = 'Images'
    PathList = os.listdir(folderPath)
    print(PathList)
    imgList = []
    CriminalIds = []
    for path in PathList:
        full_path = os.path.join(folderPath, path)
        imgList.append(cv2.imread(full_path))
        CriminalIds.append(os.path.splitext(path)[0])

        fileName = f'{folderPath}/{path}'
        blob = storage_bucket.blob(fileName)
        blob.upload_from_filename(fileName)

    print(CriminalIds)

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

    file = open("EncodeFile.p", 'wb')
    pickle.dump(encodeListKnownWithIds, file)
    file.close()
    print("File Saved")

    # After encoding is complete, show a notification
    show_notification("Face encoding complete and images have been uploaded to the databse.")

def browse_png_file():
    selected_file = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if selected_file:
        upload_png_file(selected_file)

def upload_png_file(png_file_path):
    file_name = png_file_path.split("/")[-1]
    blob = storage_bucket.blob(f"Images/{file_name}")  # Upload to "Images/" directory
    blob.upload_from_filename(png_file_path)
    show_notification(f"The PNG file '{file_name}' has been uploaded to 'Images/' directory in Firebase Storage.")

# Rest of the Tkinter GUI code
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
    show_notification("Another criminal has been added to the database.")

def reset_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_criminal_no.delete(0, tk.END)
    entry_date_time.delete(0, tk.END)

def show_notification(message):
    messagebox.showinfo("Notification", message)

app = tk.Tk()
app.title("Add Criminal Data and Upload Directory")

label_id = ttk.Label(app, text="Criminal ID:")
entry_id = ttk.Entry(app)

label_name = ttk.Label(app, text="Name:")
entry_name = ttk.Entry(app)

label_criminal_no = ttk.Label(app, text="Criminal No.:")
entry_criminal_no = ttk.Entry(app)

label_date_time = ttk.Label(app, text="Date and Time Detected:")
entry_date_time = ttk.Entry(app)

submit_button = ttk.Button(app, text="Submit", command=submit_data)

label_id.grid(row=0, column=0)
entry_id.grid(row=0, column=1)

label_name.grid(row=1, column=0)
entry_name.grid(row=1, column=1)

label_criminal_no.grid(row=2, column=0)
entry_criminal_no.grid(row=2, column=1)

label_date_time.grid(row=3, column=0)
entry_date_time.grid(row=3, column=1)

submit_button.grid(row=4, column=0, columnspan=2)

face_encoding_button = ttk.Button(app, text="Start Encoding and Upload", command=perform_face_encoding_and_upload)
face_encoding_button.grid(row=7, column=0, columnspan=2)

app.mainloop()
