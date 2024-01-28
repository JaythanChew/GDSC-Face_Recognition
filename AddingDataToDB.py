import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://facialrecognition-gdsc-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference("Students")

data = {
    # Store details for each students
    "TP011111":
    {
        "name" : "Lee Wen Han",
        "major" : "CS(AI)",
        "starting_year" : 2021,
        "total_attendance" : 20,
        "grades" : "A",
        "year" : 2,
        "last_attendance_taken" : "2024-01-26 16:10:30",
    },
     "TP072585":
    {
        "name" : "Chew Kam Wye",
        "major" : "CS(CYB)",
        "starting_year" : 2022,
        "total_attendance" : 20,
        "grades" : "A",
        "year" : 2,
        "last_attendance_taken" : "2024-01-26 16:23:07",
    },
    "TP012345":
    {
      "name" : "Student A",
        "major" : "CS(AI)",
        "starting_year" : 2021,
        "total_attendance" : 20,
        "grades" : "A",
        "year" : 2,
        "last_attendance_taken" : "2024-01-26 16:14:48",  
    },
    "TP054321":
    {
        "name" : "Student B",
        "major" : "CS(AI)",
        "starting_year" : 2021,
        "total_attendance" : 20,
        "grades" : "A",
        "year" : 2,
        "last_attendance_taken" : "2024-01-26 15:10:30",
    }
}

# collect key and import info to database
for key, value in data.items():
    ref.child(key).set(value)