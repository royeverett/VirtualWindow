from threading import Thread
import cv2

#USER MUST UPADATE the values for self.stream.set below!


class VideoGetHD:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, 1280) #USER MUST UPADATE, Camera x resolution
        self.stream.set(4, 720) #USER MUST UPADATE, Camera x resolution
        (self.grabbed, self.frame) = self.stream.read()

        #self.stream.set(cv2.CAP_PROP_FPS, 30) #For my webcam this did not increase the framerate, there's also the exposure property but most laptop webcams suck and without auto exposure the image is too dark.
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True
        self.stream.release()
