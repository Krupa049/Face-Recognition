import face_recognition
import os
import cv2
import pickle
import time

KNOWN_FACES_DIR = "known_faces"

TOLERANCE = 0.5
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "cnn"

video = cv2.VideoCapture("facerecvideo.mp4")

print("loading known faces")

known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):
  for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):    
    encoding = pickle.load(open(f"{name}/{filename}", "rb"))
    known_faces.append(encoding)
    known_names.append(name)

if len(known_names) > 0:
  next_id = max(known_names) + 1
else:
  next_id = 0


print("processing unknown faces")
while True:
  ret, image = video.read()

  locations = face_recognition.face_locations(image, model=MODEL)
  encodings = face_recognition.face_encodings(image, locations)

  for face_encoding, face_location in zip(encodings, locations):
    results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
    match = None
    if True in results:
      match = known_names[results.index(True)]
      print(f"Match found: {match}")
    else:
      match = str(next_id)
      next_id += 1
      known_names.append(match)
      known_faces.append(face_encoding)
      os.mkdir(f"{KNOWN_FACES_DIR}/{match}")
      pickle.dump(face_encoding, open(f"{KNOWN_FACES_DIR}/{match}/{match}-{int(time.time())}.pkl", "wb"))
  
    top_left = (face_location[3], face_location[0])
    bottom_right = (face_location[1], face_location[2])
    color = [0, 255, 0]
    cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

    top_left = (face_location[3], face_location[2])
    bottom_right = (face_location[1], face_location[2]+22)
    cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
    cv2.putText(image, match, (face_location[3]+10, face_location[2]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), FONT_THICKNESS)

  cv2.imshow("", image)
  if cv2.waitKey(1) & 0xFF == ord("q"):
    break
