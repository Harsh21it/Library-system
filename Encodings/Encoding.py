import os
import pickle
import cv2
import face_recognition

# providing Front_images Path
folderPathFront = r'E:\Library system\DataImages'
PathListFront = os.listdir(folderPathFront)

# initializing empty arrays
ImgListFront = []
studentId = []

# appending path and id
for path in PathListFront:
    studentId.append(os.path.splitext(path)[0])
    ImgListFront.append(cv2.imread(os.path.join(folderPathFront, path)))



print(studentId)


# defining encodings
def findEncodings(imageLists):
    encodeList = []
    for img in imageLists:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


# finding encodings
print("Encoding started")
# finding encodings front
EncodeKnownListFront = findEncodings(ImgListFront)
# merging with ids
EncodeKnownListFrontWithIds = [EncodeKnownListFront, studentId]
# Encoding done
print("Encoding Done")
# creating encodings file
file = open("Encoding.p", 'wb')
pickle.dump(EncodeKnownListFrontWithIds, file)
file.close()
print("Encoding file Created")
