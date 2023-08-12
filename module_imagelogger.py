from queue import Queue
import threading
from datetime import datetime
#from module_logger import mLogger
import numpy as np
import cv2
import os
import time

class ImageLogger:
    def __init__(self,GUI):
        #print("ImageLogger __init__ start!!!")
        self.mGUI = GUI
        self.mQueueImage = Queue()
        self.mThread = threading.Thread(target = self.imagesave_thread, args = ())
        self.dir_create()
        self.pictureFormat = ".png"
        self.start()
        
    def start(self):
        result = True
        self.mThread.start()
        print("Image Logger has started")
        return result
    
    def add_image(self, new_image):    
        self.mQueueImage.put(new_image)

    def dir_create(self):
        today = time.localtime(time.time()) #오늘 시간
        date_str = '%04d-%02d-%02d' % (today.tm_year, today.tm_mon, today.tm_mday)
        root_dir = './ImageSave_' #폴더이름
        self.dirPath = root_dir + date_str
        try: #이미 있으면 생성하지 않고 없을 시에만 생성
            if not os.path.exists(self.dirPath):
                os.makedirs(self.dirPath)
                self.mGUI.add_message('ImageSave Dir has been created as '+ self.dirPath)
        except OSError:
            print('Error: Creating directory. ' + self.dirPath)
            print("dir already exist!")
        
    def imagesave_thread(self):
        while True:
            image = self.mQueueImage.get(True,None)
            date_format = '%Y%m%d_%H%M%S.%f'
            image_file_name = self.dirPath + '/' + datetime.now().strftime(date_format) + self.pictureFormat
            frame = cv2.resize(image, (640,480), interpolation = cv2.INTER_LINEAR)
            cv2.imwrite(image_file_name,frame)
            self.mGUI.add_image(image_file_name)
            self.mGUI.add_message(self.imagesave_thread.__name__ + image_file_name + " Saved")
            self.mGUI.mLogger.add_log(self.imagesave_thread.__name__ + image_file_name + " Saved")
            
#mImageLogger = ImageLogger()