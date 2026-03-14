import cv2
import face_recognition
import os
from djitellopy import Tello

# -----------------------------
# TELLO CONNECTION
# -----------------------------
me = Tello()
me.connect()
print("Battery:", me.get_battery())

me.streamon()

# -----------------------------
# LOAD KNOWN FACES
# -----------------------------
known_encodings = []
known_names = []

path = "faces"

for img_name in os.listdir(path):

    img_path = f"{path}/{img_name}"

    image = face_recognition.load_image_file(img_path)

    encoding = face_recognition.face_encodings(image)[0]

    known_encodings.append(encoding)

    # assign name based on filename
    if "anuj" in img_name.lower():
        known_names.append("Anuj")

    elif "krish" in img_name.lower():
        known_names.append("Krish")

print("Faces Loaded:", len(known_encodings))

# -----------------------------
# CAMERA SETTINGS
# -----------------------------
w, h = 640, 480


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(imgRGB)
    face_encodings = face_recognition.face_encodings(imgRGB, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        matches = face_recognition.compare_faces(known_encodings, face_encoding)

        name = "Unknown"

        if True in matches:
            matchIndex = matches.index(True)
            name = known_names[matchIndex]

        # Draw rectangle
        cv2.rectangle(img,(left,top),(right,bottom),(0,255,0),2)

        # Draw name label
        cv2.rectangle(img,(left,bottom-35),(right,bottom),(0,255,0),cv2.FILLED)

        cv2.putText(img,name,(left+6,bottom-6),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

    cv2.imshow("Tello Face Recognition", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()