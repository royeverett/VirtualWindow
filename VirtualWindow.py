#import argparse
#import os
import cv2
import time

from VideoGetHD import VideoGetHD
#from VideoShow import VideoShow
from FaceTracker import FaceTracker
#from PerspectiveRender import PerspectiveRender
import sys, pygame
import OpenGL
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
from objloader import *


#USER MUST UPDATE THE FOLLOWING
#Screen specifications, camera location, units are inches
cameraOffset = 4.75 #from center of screen, up is positive, inches. Program assumes camera is centered over or under the screen, with positive value being over.
#cameraOffset = 1.75 #If you'd like to record the program with a camera, place the camera below or above the user's face, and adjust this value to correct the perspective for the camera.
screenWidth = 15.04
screenHeight = 8.44
screenResolution = (1920,1080)




scrnW = screenWidth/2
scrnH = screenHeight/2
pixperinch = screenResolution[0] / screenWidth
i = screenResolution[0]/2
j = screenResolution[1]/2

distance = 45 #arbitrary, quickly overwritten with real values
distance2 = distance
distance3 = distance2
first = True

def threadVirtualWindow(source=0): #Source is which camera on your system you will be using, and for most users will be '0'
    loops = 0
    i = screenResolution[0]/2
    j = screenResolution[1]/2
    first = True
    video_getter = VideoGetHD(source).start()
    face_tracker = FaceTracker(video_getter.frame).start()
    #time.sleep(1)
    #renderer = PerspectiveRender(face_tracker.headxyz).start() #attempted rendering thread

    while True:
        loops += 1
        if video_getter.stopped or face_tracker.stopped:
            video_getter.stop()
            face_tracker.stop()
            #renderer.stop()
            

        frame = video_getter.frame
        time.sleep(0.001) #ESSENTIAL DELAY FOR PROGRAM TO WORK
        face_tracker.frame = frame
        headxyz = face_tracker.track()
        #print(headxyz)

        for e in pygame.event.get():
            if e.type == QUIT:
                #sys.exit()
                video_getter.stop()
                face_tracker.stop()
                pygame.quit()
                sys.exit()
                break
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                video_getter.stop()
                face_tracker.stop()
                pygame.quit()
                sys.exit()
                #exit()
                #sys.exit()
                break
            elif e.type == MOUSEMOTION:
                i, j = e.pos
                #print('x = ', (hx-i)/pixperinch, ', y = ', (hy-j)/pixperinch)
                #glLightfv(GL_LIGHT0, GL_POSITION,  ((hx-i)/pixperinch, (hy-j)/pixperinch , 1, 1.0))
                
        #if (tracking == True):
        headx = headxyz[0]
        heady = headxyz[1]
        if (first == True):
            #print("First!")
            distance = headxyz[2]
            distance2 = distance
            distance3 = distance
            first = False
            


        distance3 = distance2
        distance2 = distance
        distance = headxyz[2]
        distance = (distance + distance2 + distance3) / 3 # Since the current tracking is very jittery, average the last 3 values for smoothing. Kalman filter would be better

        #if (time.time() - headhyz[3] > 0.033):
            

        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum((scrnW-headx)/5, (-scrnW-headx)/5, (-scrnH-heady)/5, (scrnH-heady)/5, distance/5, 100) #Set the rendering frustum shape to the user's head angle, the 5 is arbitrary to ensure "pop-out" effects works by moving the near clipping plane closer to the user. glFrustum is really cool!
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(headx, heady, distance, headx, heady, 0, 0, 1, 0) #Place the camera at the tracked location and look straight ahead in the z direction.
        glLightfv(GL_LIGHT0, GL_POSITION,  ((hx-i)/pixperinch, (hy-j)/pixperinch , 1, 1.0)) #Move the light to the mouse position.
        obj.render()
        pygame.display.flip()
        #print('display updated')
        #time4 = time.time()
        #print(time4 - time3)
        #print(time.time())
        #clock.tick()
        #print(loops)


                
        

def main():

    threadVirtualWindow()


    

pygame.init()

hx = screenResolution[0]/2
hy = screenResolution[1]/2
srf = pygame.display.set_mode(screenResolution, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-60, 60, 20, 1.0))
#glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0)) #working
#glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0)) #working
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.3, 0.3, 0.3, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_FLAT)           # most obj files expect to be smooth-shaded

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ('samples.obj', swapyz=True) #Select the obj file to display.
obj.generate()

clock = pygame.time.Clock()

alternate = False
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = screenResolution
gluPerspective(20, width/height, 0.01, 100.0) # 20 is arbitrary, overwritten
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)


if __name__ == "__main__":
    main()
