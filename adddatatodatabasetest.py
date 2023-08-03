import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, storage, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimecriminaldetection.appspot.com"
})

storage_bucket = storage.bucket()
ref = db.reference('Criminals')

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

def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        upload_directory(selected_directory)

def upload_directory(directory_path):
    directory_name = directory_path.split("/")[-1]
    blob = storage_bucket.blob(directory_name)
    blob.upload_from_directory(directory_path)
    show_notification(f"The directory '{directory_name}' has been uploaded to Firebase Storage.")

def browse_png_file():
    selected_file = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if selected_file:
        upload_png_file(selected_file)

def upload_png_file(png_file_path):
    file_name = png_file_path.split("/")[-1]
    blob = storage_bucket.blob(f"Images/{file_name}")  # Upload to "Images/" directory
    blob.upload_from_filename(png_file_path)
    show_notification(f"The PNG file '{file_name}' has been uploaded to 'Images/' directory in Firebase Storage.")

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

browse_png_button = ttk.Button(app, text="Browse PNG File", command=browse_png_file)
browse_png_button.grid(row=6, column=0, columnspan=2)

app.mainloop()
