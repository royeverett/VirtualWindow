from threading import Thread
import cv2
import mediapipe as mp
import time
import math
import numpy as np
mp_face_mesh = mp.solutions.face_mesh


#USER MUST UPDATE THE FOLLOWING
camhfov = 80 #camera horizontal field of view, DEGREES
camvfov = 39 #camera vertical field of view
camxres = 1280 #camera x resolution
camyres = 720
cameraOffset = 4.75 #from center of screen, up is positive, inches. Program assumes camera is centered over or under the screen, with positive value being over.
#cameraOffset = 1.75 #for recording with a camera below the face adjust this
screenWidth = 15.04 #inches
screenHeight = 8.44 #inches
screenResolution = (1920,1080)
userHead = 3400 #user head size scales only distance estimate, adjust this value until distance is correct. There's a print(distance) down there to help with this process, see README file.




scrnW = screenWidth/2
scrnH = screenHeight/2
pixperinch = screenResolution[0] / screenWidth




distance = 45 #arbitrary, quickly overwritten with real values
distance2 = 45
distance3 = 45
starttime = time.time()
frames = 0
tracking = False



def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, 
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4)


class FaceTracker:



    def __init__(self, frame=None):
        self.frame = frame
        self.headxyz = [0, 0, 24, time.time()]

        self.stopped = False
        #self.tracking = False

    def start(self):
        Thread(target=self.track, args=()).start()
        return self

    def track(self):

        while not self.stopped:
            #cv2.imshow("Video", self.frame)
            #if cv2.waitKey(1) == ord("q"):
                #self.stopped = True
            #print("facetracker worked")
            results = face_mesh.process(self.frame)
            
            if results.multi_face_landmarks:

                #This is where the user's head location is calculated.
                #Mediapipe does not give any sort of value for distance measurement, so we have to figure it out based on how far apart the eyes are.
                #Mediapipe outputs landmark locations as on-screen coordinates -1 to 1, so we must scale them to pixel values (do we?)

                eyesh = ( ( (results.multi_face_landmarks[0].landmark[33].x + results.multi_face_landmarks[0].landmark[263].x) / 2) * camhfov - (camhfov/2)) #Calculate the angle from the center of the webcam's FOV to the center of the user's eyes
                eyesv = ( ( (results.multi_face_landmarks[0].landmark[33].y + results.multi_face_landmarks[0].landmark[263].y) / 2) * camvfov - (camvfov/2))

                shape = self.frame.shape 
                eyesx = int(( (results.multi_face_landmarks[0].landmark[33].x + results.multi_face_landmarks[0].landmark[263].x) / 2) * shape[1]) #Convert to pixel values for use in drawing tracked location if desired
                eyesy = int(( (results.multi_face_landmarks[0].landmark[33].y + results.multi_face_landmarks[0].landmark[263].y) / 2) * shape[0])

                nosex = int(results.multi_face_landmarks[0].landmark[4].x * shape[1]) #Get the nose pixel coodinates, this is to help with when the user turns thier head left/right and shrinks the distance between thier eyes
                nosey = int(results.multi_face_landmarks[0].landmark[4].y * shape[0])

                nosetopx = int(results.multi_face_landmarks[0].landmark[6].x * shape[1]) #We're making a line between the top and bottom of the user's nose
                nosetopy = int(results.multi_face_landmarks[0].landmark[6].y * shape[0])

                nosebottomx = int(results.multi_face_landmarks[0].landmark[164].x * shape[1])
                nosebottomy = int(results.multi_face_landmarks[0].landmark[164].y * shape[0])

                reyex = int(results.multi_face_landmarks[0].landmark[33].x * shape[1]) #Get x and y coordinates for left and right eyes
                reyey = int(results.multi_face_landmarks[0].landmark[33].y * shape[0])
                leyex = int(results.multi_face_landmarks[0].landmark[263].x * shape[1])
                leyey = int(results.multi_face_landmarks[0].landmark[263].y * shape[0])
           
                eyewidth = math.sqrt((reyex-leyex)**2 + (reyey-leyey)**2) #Calculate pixel distance between left and right eyes

                array_longi  = np.array([nosetopx-nosebottomx, nosetopy-nosebottomy]) #Line between top and bottom of user's nose
                array_trans = np.array([nosetopx-nosex, nosetopy-nosey]) 
                 # Use vector to calculate distance from point to line
                array_temp = (float(array_trans.dot(array_longi)) / array_longi.dot(array_longi)) # Note that it is converted to floating-point arithmetic
                array_temp = array_longi.dot(array_temp) #get the distance from the top/bottom nose line to the tip of the nose
                eyenose = eyewidth + np.sqrt((array_trans - array_temp).dot(array_trans - array_temp)) #add the square root of the nose tip from centerline distance to the eye width calculated earlier, this helps offset eye width shrinking from the user turning their head left/right

                
                distance = userHead/eyenose #finally convert our pixel values to inches, it's very important userHead is calibrated for distances to be accurate
                #print(distance) #uncomment this to see the distance value in real time, useful for determining userHead value.

                


                headx = (math.tan(math.radians(eyesh)) * distance) #convert angles to user head coordinates
                heady = ((math.tan(math.radians(eyesv)) * distance) - cameraOffset)*-1 #invert y value to ensure coords make sense

                self.headxyz = [headx, heady, distance, time.time()] #output head xyz coordinates and timestamp

                
            return self.headxyz
            #return self.tracking

    def stop(self):
        self.stopped = True

