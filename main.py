import cv2      # Library for opening web cam
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
    'databaseURL' : "https://facialrecognition-gdsc-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket' : "facialrecognition-gdsc.appspot.com"
})

bucket = storage.bucket()

capture = cv2.VideoCapture(0)

# Set window size
capture.set(3, 1280)
capture.set(4, 720)

# Set variable for bckground image
backgroundImg = cv2.imread("Resources/Background.png")

# Set path 
folderPathMode = "Resources/Modes"
listPathMode = os.listdir(folderPathMode)
imgListMode = []

# Append image into listPathMode
for path in listPathMode:
    imgListMode.append(cv2.imread(os.path.join(folderPathMode, path)))

# Read file EncodingFile.p and read studentIDs
encodingsFile = open("EncodingFile.p", "rb")
encodingListWithIDs = pickle.load(encodingsFile)
encodingsFile.close()

encodingsListKnown, studentIDs = encodingListWithIDs
print(studentIDs)

modeType = 0
counter = 0
id = -1


while True:
    # if success = true, image will contain what cam received
    success, image = capture.read()

    # Set webcam to background
    image = cv2.resize(image, (640, 480))
    backgroundImg[162:162 + 480, 55:55 + 640] = image
    backgroundImg[44: 44+633, 808: 808+414 ] = imgListMode[modeType]

    # Setting image resolution
    smallImage = cv2.resize(image, (0,0), None, 0.25, 0.25)
    # Converting image to rgb colot format
    smallImage = cv2.cvtColor(smallImage, cv2.COLOR_BGR2RGB)

    # Find face in webcam
    faceCurrentFrame = face_recognition.face_locations(smallImage)
    # Encoding face in image
    encodeCurrentFrame = face_recognition.face_encodings(smallImage, faceCurrentFrame)


    if faceCurrentFrame:
    # # Set background image
    # cv2.imshow("My Webcam", image)

        for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame) :
            matches = face_recognition.compare_faces(encodingsListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodingsListKnown, encodeFace)
            print("Matches", matches)
            print("Face Distance", faceDistance)

            matchIndex = np.argmin(faceDistance)
            print("Match Index", matchIndex)

            if matches[matchIndex]:
                print("Registered Student Detected")
                print(studentIDs[matchIndex])

                # Creating 4 points to map as "corners"
                y1, x2, x1, y2 = faceLocation
                # Resizing size of webcam feed
                y1, x2, x1, y2 = y1*4, x2*4, x1*4, y2*4
                # Creating a bax with line that warp face
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                # Having rectangle follow face around
                backgroundImg = cvzone.cornerRect(backgroundImg, bbox, rt=0)
                id = studentIDs[matchIndex]

                if counter == 0:
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Retrieve student info
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Retrieve student image
                blob = bucket.get_blob(f'image{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uints)
                studentimg = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                # Update attendance record and data
                datetimeObject = datetime.strptime(studentInfo['last_attendance_taken'],
                                                "%Y-%m-%d %H:%M:%S")
                timeInSecsElapsed = (datetime.now() - datetimeObject).total_seconds()
                if timeInSecsElapsed > 30 :
                    # Update attendance record and data
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1

                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_taken').set(datetime.now().strftime("%Y-%m-%d %H:%M:%s"))
                else:
                    modeType = 3
                    counter = 0
                    backgroundImg[44 : 44 + 633, 808 : 808 + 414] = imgListMode[modeType]

                if 10 < counter < 20:
                    modeType = 2

                backgroundImg[44 : 44 + 633, 808 : 808 + 414] = imgListMode[modeType]

                if counter < 10:
                    cv2.putText(backgroundImg, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['grades']), (910, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(backgroundImg, str(studentInfo['year']), (861, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(backgroundImg, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 1)
                
                # Centrer name
                (width, height), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SIMPLEX,1 , 1)

                center_offset = (414 - width) // 2
                cv2.putText(backgroundImg, str(studentInfo['name']), (808 + center_offset, 445),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 1)
                
                backgroundImg[175 : 175 + 216, 909 : 909 + 216] = studentimg

            counter += 1

            if counter > 20:
                counter = 0
                modeType = 0
                studentInfo = []
                studentimg = []
                backgroundImg[44 : 44 + 633, 808 : 808 + 414] = imgListMode[modeType]
    
    else :
        modeType = 0
        counter = 0

     # use image show (imshow) to start a window named Attendance System
    cv2.imshow("Attendance System", backgroundImg)
    cv2.waitKey(1)