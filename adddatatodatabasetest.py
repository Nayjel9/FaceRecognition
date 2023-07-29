import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/"
})

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
    show_notification()

def reset_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_criminal_no.delete(0, tk.END)
    entry_date_time.delete(0, tk.END)

def show_notification():
    messagebox.showinfo("Notification", "Another criminal has been added to the database.")

app = tk.Tk()
app.title("Add Criminal Data")

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

app.mainloop()
