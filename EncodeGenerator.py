# Import libraries
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://facialrecognition-gdsc-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket' : "facialrecognition-gdsc.appspot.com"
})


# Import image
folderPathImages = "Images"
listPathImages = os.listdir(folderPathImages)
imgListImages = []

# Extracting Student IDs
studentIDs = []

for path in listPathImages:
    imgListImages.append(cv2.imread(os.path.join(folderPathImages, path)))
    # Remove .png from image to get IDs
    studentIDs.append(os.path.splitext(path)[0])

    fileName = f'{folderPathImages}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)



# Show Students IDs
print(len(imgListImages))

# Function for encodings
def generateEncodings(images):
    encodingList = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingList.append(encode)

    return encodingList

encodingsListKnown = generateEncodings(imgListImages)
encodingListWithIDs = [encodingsListKnown, studentIDs]

# Open a new file called EncodingFile.p in WRITE MODE
encodingFile = open("EncodingFile.p", "wb")
# using PICKLE to dump into file 
pickle.dump(encodingListWithIDs, encodingFile)
#Closing file
encodingFile.close()
