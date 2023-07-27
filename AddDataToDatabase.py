import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/"
})

ref = db.reference('Criminals')

data = {
    "321654":
        {
            "name": "Christian Tan",
            "criminal_no": "1",
            "date_and_time_detected": "2022-12-11 00:54:34",
        },
    "852741":
        {
            "name": "Emily Blunt",
            "criminal_no": "2",
            "date_and_time_detected": "2022-12-11 00:54:34",
        },
    "963852":
        {
            "name": "Elon Musk",
            "criminal_no": "3",
            "date_and_time_detected": "2022-12-11 00:54:34",
        }
}

for key, value in data.items():
    ref.child(key).set(value)