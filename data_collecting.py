"""
Aeyesafe Thermal Image collecting program

"""
isShowGUI = True   # Show window
minutes_to_record = 15   # Video-length minutes as unit (integer)
SECONDS_CAPTURE = 15 # every 15s capture one image
VIDEO_FPS = 20.0 # Frame per second for the video recording

import timeit
import datetime
import os
import time
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler

try:
    import cv2
except ImportError:
    print("ERROR opencv-python must be installed")
    exit(1)


class OpenCvCapture(object):
    """
    Encapsulate state for capture from Pure Thermal 1 with OpenCV
    """
    PATH = ""
    IMG = None
    
    def __init__(self):
        # capture from the LAST camera in the system
        # presumably, if the system has a built-in webcam it will be the first
        # for i in reversed(range(10)): # this works better for Raspian OS
        for i in range(10):
            print("Testing for presense of camera #{0}...".format(i))
            cv2_cap = cv2.VideoCapture(i)
            if cv2_cap.isOpened():
                break

        if not cv2_cap.isOpened():
            print("Camera not found!")
            exit(1)

        width = cv2_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        height  = cv2_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)


        width = int(cv2_cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(cv2_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)

        fourcc = cv2.VideoWriter_fourcc(*'XVID') 
        out_file_name = "./" + time.strftime("%d-%m-%Y_%X")+".avi"
        self.out = cv2.VideoWriter(out_file_name, fourcc, VIDEO_FPS, (width, height))

        self.cv2_cap = cv2_cap
        

    def show_video(self):
        """
        Run loop for cv2 capture from lepton
        """
        print("Running, ESC or Ctrl-c to exit...")
        id = 0
#         counter = 3
        self.PATH = "./collected_image/" + time.strftime("%d-%m-%Y") + "/"
        
        if os.path.exists(self.PATH):
            print("%s path existed" % self.PATH)
        else:
            print("Trying to create folder")
            try:
                 os.makedirs(self.PATH)
            except OSError:
                print("Creation of the directory %s failed" % self.PATH)
                exit(1)
            else:
                print("Successfully created the directory %s" % self.PATH)

        start = timeit.default_timer()
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.capture_img, 'interval', seconds = SECONDS_CAPTURE)
        
        while True:
            ret, self.IMG = self.cv2_cap.read()
            if ret == False:
                print("Error reading image")
                break

            if isShowGUI:
                cv2.imshow("lepton", self.IMG )
            self.out.write(self.IMG)

            if isShowGUI:
                if cv2.waitKey(5) == 27:
                    break
            
#             time.sleep(0.200) # sleep for 200 miliseconds
            
            minutes_recorded = (timeit.default_timer() - start) // 60
            if minutes_recorded > minutes_to_record:
                break
            

        # When everything done, release the capture
        self.cv2_cap.release()
        sched.shutdown()
        if isShowGUI:
            # self.cv2_cap.destroyAllWindows()
            cv2.destroyAllWindows()
    
    def capture_img(self):        
        img = self.IMG
        out_image_name = self.PATH + time.strftime("%d-%m-%Y_%X")+".jpg"
        print(out_image_name)
#         cv2.imwrite(out_image_name, cv2.resize(img, (640, 480)))
        cv2.imwrite(out_image_name, img)
        

if __name__ == '__main__':
    OpenCvCapture().show_video()

