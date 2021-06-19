import cv2
import mediapipe as mp
import time
import math
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

hfov = 70
vfov = 39
cameraOffset = 4.75
screenWidth = 15.04
screenHeight = 8.44

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(1)


def change_res(width, height):
    cap.set(3, width)
    cap.set(4, height)

change_res(1280, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, 
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4) as face_mesh:
  while cap.isOpened():
    success, image = cap.read()
    start = time.time()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    #image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_face_landmarks:
      for face_landmarks in results.multi_face_landmarks:
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACE_CONNECTIONS,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=drawing_spec)
        #headx = results.multi_face_landmarks[0].landmark[6].x * hfov - (hfov/2)
        #heady = results.multi_face_landmarks[0].landmark[6].y * vfov - (vfov/2)
        #headz = (-1/results.multi_face_landmarks[0].landmark[6].z)

        eyesh = ( ( (results.multi_face_landmarks[0].landmark[33].x + results.multi_face_landmarks[0].landmark[263].x) / 2) * hfov - (hfov/2))
        eyesv = ( ( (results.multi_face_landmarks[0].landmark[33].y + results.multi_face_landmarks[0].landmark[263].y) / 2) * vfov - (vfov/2))
        #z = ( (results.multi_face_landmarks[0].landmark[173].z + results.multi_face_landmarks[0].landmark[398].z) / 2)
        #z = results.multi_face_landmarks[0].landmark[0].z * 100

        shape = image.shape 
        eyesx = int(( (results.multi_face_landmarks[0].landmark[33].x + results.multi_face_landmarks[0].landmark[263].x) / 2) * shape[1])
        eyesy = int(( (results.multi_face_landmarks[0].landmark[33].y + results.multi_face_landmarks[0].landmark[263].y) / 2) * shape[0])

        nosex = int(results.multi_face_landmarks[0].landmark[4].x * shape[1])
        nosey = int(results.multi_face_landmarks[0].landmark[4].y * shape[0])

        nosetopx = int(results.multi_face_landmarks[0].landmark[6].x * shape[1])
        nosetopy = int(results.multi_face_landmarks[0].landmark[6].y * shape[0])

        nosebottomx = int(results.multi_face_landmarks[0].landmark[164].x * shape[1])
        nosebottomy = int(results.multi_face_landmarks[0].landmark[164].y * shape[0])


        reyex = int(results.multi_face_landmarks[0].landmark[33].x * shape[1])
        reyey = int(results.multi_face_landmarks[0].landmark[33].y * shape[0])
        leyex = int(results.multi_face_landmarks[0].landmark[263].x * shape[1])
        leyey = int(results.multi_face_landmarks[0].landmark[263].y * shape[0])

        #pointTop = (int(results.multi_face_landmarks[0].landmark[168].x * shape[1]), int(results.multi_face_landmarks[0].landmark[168].y * shape[0]))        
        eyewidth = math.sqrt((reyex-leyex)**2 + (reyey-leyey)**2)

        array_longi  = np.array([nosetopx-nosebottomx, nosetopy-nosebottomy])
        array_trans = np.array([nosetopx-nosex, nosetopy-nosey])
         # Use vector to calculate distance from point to line
        array_temp = (float(array_trans.dot(array_longi)) / array_longi.dot(array_longi)) # Note that it is converted to floating-point arithmetic
        array_temp = array_longi.dot(array_temp)
        eyenose = eyewidth + np.sqrt((array_trans - array_temp).dot(array_trans - array_temp))

        drawRadius = int(eyenose / 40 + 1)

        #image = np.zeros((shape[0],shape[1],3), np.uint8)

        centerx = int(shape[1]/2)
        centery = int(shape[0]/2)

        cv2.circle(image, (eyesx, eyesy), radius= drawRadius, color=(0, 0, 255), thickness=2)
        cv2.line(image, (centerx, centery), (eyesx, eyesy), color=(0, 0, 255), thickness=1)
        #cv2.circle(image, (reyex, reyey), radius= drawRadius, color=(0, 0, 255), thickness=2)
        #cv2.line(image, (reyex, reyey), (leyex, leyey), color=(0, 0, 255), thickness=2)
        #cv2.line(image, (nosetopx, nosetopy), (nosebottomx, nosebottomy), color=(0, 0, 255), thickness=2)

        #distance = 3400/eyenose #working
        distance = 3100/eyenose


        headx = math.tan(math.radians(eyesh)) * distance
        heady = (math.tan(math.radians(eyesv)) * distance) - cameraOffset
        #headz = distance

        #print(results.multi_face_landmarks[0].landmark[6].z)
        print("Head Coordinates X,Y,Z", round(headx, 2), ", ", round(heady, 2), ", ", round(distance, 1))
        #print("distance: ", round(headz, 1))
        
    end = time.time()
    totalTime = end - start

    fps = 1 / totalTime
    #print("FPS: ", fps)

    cv2.circle(image, (centerx, centery), radius= 4, color=(255, 255, 255), thickness=2)
    cv2.imshow('MediaPipe FaceMesh', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
cv2.destroyAllWindows()
