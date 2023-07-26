import cv2
import os

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    full_path = os.path.join(folderModePath, path)
    imgModeList.append(cv2.imread(full_path))

while True:
    success, img = cap.read()
    
    imgBackground[162:162 + 480, 55:55 +640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[0]
    
    cv2.imshow("Criminal", imgBackground)
    cv2.waitKey(1)
