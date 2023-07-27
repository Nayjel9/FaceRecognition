import cv2
import face_recognition
import pickle
import os

#Importing Criminal Images
folderPath = 'Images'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
CriminalIds = []
for path in PathList:
    full_path = os.path.join(folderPath, path)
    imgList.append(cv2.imread(full_path))
    #print(path)
    #print(os.path.splitext(path)[0])
    CriminalIds.append(os.path.splitext(path)[0])
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
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")