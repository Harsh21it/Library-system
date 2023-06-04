import mysql.connector
import numpy as np
import face_recognition
import cv2
import cvzone
import pickle
from datetime import datetime
import pyzbar.pyzbar as pyzbar
import pyttsx3

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='**********',
    port='3306',
    database='mydb'
)

mycursor = mydb.cursor()

# videoCapture
cap = cv2.VideoCapture(0)
background = cv2.imread('Graphics/background.png')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# opening encoding files
file = open('Encodings/Encoding.p', 'rb')
EncodeKnownListFrontWithIds = pickle.load(file)
file.close()
EncodeKnownListFront, studentId = EncodeKnownListFrontWithIds

# creating a set of recognised entities
student = {'null'}
student.clear()

# video feed
while True:
    ret, frame = cap.read()
    # Encoding Current Frame
    img = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faceCurframe = face_recognition.face_locations(img)
    encodeCurframe = face_recognition.face_encodings(img, faceCurframe)
    background[162:162 + 480, 55:55 + 640] = frame

    # matching with current frame
    # matching with front_img
    for encoface, faceloc in zip(encodeCurframe, faceCurframe):
        matches_front = face_recognition.compare_faces(EncodeKnownListFront, encoface)
        faceDis_front = face_recognition.face_distance(EncodeKnownListFront, encoface)
        # front_index
        matchIndexFront = np.argmin(faceDis_front)
        if matches_front[matchIndexFront]:
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            img_background = cvzone.cornerRect(background, bbox, rt=0)
        student.add(studentId[matchIndexFront])
        id = studentId[matchIndexFront]
    if len(student) == 0:
        print("No recognised face")

    cv2.imshow('Library Login', background)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# intialising cam
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# decoding qr
def decode(im1):
    # Find barcodes and QR codes
    decodedings = pyzbar.decode(im1)
    return decodedings


# bookid set
bookid = {'NULL'}
bookid.clear()

# fetching today's day
todayDate = datetime.today()
Date = str(todayDate.strftime("%x")).replace('/', '')

# finePerDay
finePerDay = 10

# initiating capture
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# fetching book id
def getBookId(recap):
    # decoding books data
    while True:
        reret, reframe = recap.read()
        im = cv2.cvtColor(reframe, cv2.COLOR_BGR2RGB)
        decodedObjects = decode(im)

        for decodedObject in decodedObjects:
            points = decodedObject.polygon

            # If the points do not form a quad, find convex hull
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else:
                hull = points

            # Number of points in the convex hull
            n = len(hull)
            # Draw the convext hull
            for j in range(0, n):
                cv2.line(frame, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)

            x = decodedObject.rect.left
            y = decodedObject.rect.top

            bookid.add(decodedObject.data.decode('utf-8'))

            barCode = str(decodedObject.data)
            cv2.putText(reframe, barCode, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("qrCode", reframe)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    recap.release()
    cv2.destroyAllWindows()
    return bookid


studentID = list(student)

studentName = []
for item in range(len(student)):
    query = "select FirstName,LastName from mydb.student where idStudent = '" + studentID[item] + "' ;"
    mycursor.execute(query)
    for st in mycursor:
        studentName.append(st[0] + " " + st[1])

for i in range(len(student)):
    read_out = pyttsx3.init()
    print("welcome " + studentName[i])
    welcome = "welcome " + studentName[i]
    read_out.say(welcome)
    read_out.runAndWait()
    choice = 'y'
    while choice == 'y':
        print(
            '''Hi There! Welcome to LIBONTHEGO.
            You can now get books issued to without waiting in line
            Enter 1 for getting a book issued
            Enter 2 for returning a book,
            Thank you.''')
        read = pyttsx3.init()
        read.say('''Hi There! Welcome to LIB ON THE GO.
                You can now get books issued to without waiting in line
                Enter 1 for getting a book issued
                Enter 2 for returning a book,
                Thank you.''')
        read.runAndWait()
        option = int(input('Please make your choice:'))
        if option == 1:
            print("scan the book QR code")
            flag = 0
            bookID = getBookId(cam)
            bookid = list(bookID)
            query = "select StudentId from mydb.issuedbooks where BookId='" + bookid[0] + "';"
            mycursor.execute(query)
            for ids in mycursor:
                for item in ids:
                    if str(item) == studentID[i]:
                        flag = 1
                        print("Book already issued!")
                        break
            if flag == 0:
                query = "insert into mydb.issuedbooks values  ('" + studentID[
                    i] + "' , '" + bookid[0] + "' , '" + Date + "');"
                mycursor.execute(query)
                mydb.commit()
                print("Book issued successfully!")
        elif option == 2:
            print("scan the book QR code")
            bookID = getBookId(cam)
            bookid = list(bookID)
            query = "delete from mydb.issuedbooks where StudentId= '" + studentID[i] + "' and BookId ='" + bookid[
                0] + "';"
            mycursor.execute(query)
            mydb.commit()
            print("Returned successful!")
        else:
            print("Invalid Option")
        choice = input("Do you wish to continue(y/n)?: ")
        if choice == 'n':
            shoutout = pyttsx3.init()
            shoutout.say("Thank you for using our services. Hope you are satisfied")
            shoutout.runAndWait()
            break
