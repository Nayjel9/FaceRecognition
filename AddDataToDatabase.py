import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimecriminaldetection-default-rtdb.firebaseio.com/"
})

ref = db.reference('Criminals')

data = {
    "312654":
        {
            "name": "Christian Ervin T. Tan",
            "Criminal No.": "312654"
        }

}

for key, value in data.items():
    ref.child(key).set(value)