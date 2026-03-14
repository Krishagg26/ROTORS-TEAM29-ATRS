import cv2
import face_recognition
import os
import numpy as np
from djitellopy import Tello
from time import sleep

# -----------------------------
# CONNECT TO TELLO
# -----------------------------
tello = Tello()
tello.connect()

print("Battery:", tello.get_battery())

tello.streamoff()
tello.streamon()

sleep(2)

frame_read = tello.get_frame_read()

# -----------------------------
# LOAD KNOWN FACES
# -----------------------------
known_encodings = []
known_names = []

path = "faces"

for file in os.listdir(path):

    img_path = f"{path}/{file}"

    img = face_recognition.load_image_file(img_path)
    enc = face_recognition.face_encodings(img)

    if len(enc) == 0:
        continue

    known_encodings.append(enc[0])

    if "anuj" in file.lower():
        known_names.append("Anuj")

    elif "krish" in file.lower():
        known_names.append("Krish")

print("Faces Loaded:", len(known_encodings))

# -----------------------------
# CAMERA SETTINGS
# -----------------------------
width = 480
height = 360

pid = [0.5, 0.3, 0]
pError = 0

targetArea = 10000

smooth_x = 0

cv2.namedWindow("Tello Face Tracking", cv2.WINDOW_NORMAL)

# -----------------------------
# FACE DETECTION
# -----------------------------
def findFace(img):

    small = cv2.resize(img,(0,0),fx=0.5,fy=0.5)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb, model="hog")
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    centers=[]
    areas=[]

    for (top,right,bottom,left),face_encoding in zip(face_locations,face_encodings):

        top*=2
        right*=2
        bottom*=2
        left*=2

        name="Unknown"

        distances = face_recognition.face_distance(known_encodings,face_encoding)

        if len(distances)>0:

            matchIndex = np.argmin(distances)

            if distances[matchIndex] < 0.5:
                name = known_names[matchIndex]

        w = right-left
        h = bottom-top
        area = w*h

        cx = left + w//2
        cy = top + h//2

        centers.append([cx,cy])
        areas.append(area)

        cv2.rectangle(img,(left,top),(right,bottom),(0,255,0),2)

        cv2.rectangle(img,(left,bottom-30),(right,bottom),(0,255,0),cv2.FILLED)

        cv2.putText(img,name,(left+5,bottom-5),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

    if len(areas)!=0:

        i = areas.index(max(areas))
        return img,(centers[i],areas[i])

    else:

        return img,[[0,0],0]

# -----------------------------
# TRACK FACE
# -----------------------------
def trackFace(info,width,pid,pError,target_height):

    global smooth_x

    x,y = info[0]
    area = info[1]

    fb = 0

    smooth_x = int(0.7*smooth_x + 0.3*x)

    error = width//2 - smooth_x

    speed = pid[0]*error + pid[1]*(error - pError)

    if abs(error) < 20:
        speed = 0

    speed = int(np.clip(speed,-60,60))

    # distance control
    if area > 0:

        distance_error = targetArea - area
        fb = int(np.clip(distance_error/200 , -30 , 30))

    else:
        fb = 0

    # HEIGHT CONTROL
    current_height = tello.get_height()
    height_error = target_height - current_height
    ud = int(np.clip(height_error * 2 , -20 , 20))

    if x == 0:

        speed = 0
        fb = 0
        ud = 0
        error = 0

    tello.send_rc_control(0, fb, ud, -speed)

    return error


# -----------------------------
# WAIT FOR FIRST FRAME
# -----------------------------
while frame_read.frame is None:
    sleep(0.1)

# -----------------------------
# TAKE OFF
# -----------------------------
tello.takeoff()

sleep(2)

# LOCK HEIGHT
target_height = tello.get_height()

print("Target Height:", target_height)

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    frame = frame_read.frame

    if frame is None:
        continue

    img = cv2.resize(frame,(width,height))

    img,info = findFace(img)

    pError = trackFace(info,width,pid,pError,target_height)

    cv2.imshow("Tello Face Tracking",img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        tello.land()
        break

    if key == ord('e'):
        tello.emergency()
        break

cv2.destroyAllWindows()