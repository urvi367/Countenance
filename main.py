from imutils import face_utils
from imutils.video import WebcamVideoStream
import numpy as np
import argparse
import dlib
import cv2
from apply_makeup1 import ApplyMakeup

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)

'''image = cv2.imread('img.png')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = np.array(image)
faces = detector(image, 1)
for face in faces:
	landmarks = predictor(image, face)
	landmarks=face_utils.shape_to_np(landmarks)
	a=ApplyMakeup(landmarks)
	image=a.apply_lipstick(image, 88, 0, 0)
	image=a.apply_liner(image)
    
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
cv2.imshow("Output", image)
cv2.waitKey(0)'''


#pass b g r values as command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("B", help="Enter colour B value")
parser.add_argument("G", help="Enter colour G value")
parser.add_argument("R", help="Enter colour R value")
args = parser.parse_args()


print("[INFO] starting video stream...")
video_capture = WebcamVideoStream(src=0).start()

while True:
    frame = video_capture.read()
    faces = detector(frame, 1)

    for face in faces:
    	landmarks = predictor(frame, face)
    	landmarks = face_utils.shape_to_np(landmarks)

    	a=ApplyMakeup(landmarks)
    	frame=a.apply_lipstick(frame, args.B, args.G, args.R)
    	frame=a.apply_liner(frame)

    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
vs.stop() 
