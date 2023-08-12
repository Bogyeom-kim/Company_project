from tkinter import *
import pandas as pd
import numpy as np
import cv2
import datetime
import time
from logging.config import dictConfig
import logging
from PIL import ImageTk
import sys
from time import sleep
import time
from module_camera_copy import Camera
from module_logger import Logger
from module_sensor_20Hz import Sensor
#from module_jobs import Job_CheckSensorDistance
#from module_jobs import Job_UpdateSensorDistance
from module_datamanager import DataManager
from module_jobmanager import JobManager
from module_imagelogger import ImageLogger
#from module_auto import Auto_mode
from module_jobs import Job_UpdateSensorDistance
from module_jobs import Job_CheckSensorDistance
from module_jobs import Job_AskGrabImage
import threading
from queue import Queue

class BK_GUI():
    def __init__(self):
        self.window = Tk() #윈도우 창 생성
        self.window.geometry("1920x800") #윈도우 창 크기 설정
        self.window.config(bg = "black") #윈도우 창 배경색 설정
        self.window.title("BK Solution") #윈도우 창 이름 설정
        self.window.option_add("*Font","Arial 10") #윈도우 창 글꼴 설정
        self.window.iconbitmap('C:/Users/kim/Desktop/logo.ico') #윈도우 창 로고 설정
        #Module###################################################################################
        self.mSensor = Sensor(self)
        self.mLogger = Logger(self)
        self.mCamera = Camera(self)
        self.mImageLogger = ImageLogger(self)
        #self.mAuto_mode = Auto_mode(self)
        self.mJobManager = JobManager(self)
        self.mDataManager = DataManager(self)
        #Job######################################################################################
        self.mJob_CheckSensorDistance = Job_CheckSensorDistance(self)
        self.mJob_UpdateSensorDistance = Job_UpdateSensorDistance(self)
        self.mJob_AskGrabImage = Job_AskGrabImage(self)
        #Frame####################################################################################
        self.frame_cnt = LabelFrame(self.window, text = "Control Frame", relief="solid", bd=2, bg='red',height = 10,width=100)
        self.frame_cnt.pack(side="bottom", fill = "both", expand = True)
        self.frame_rst = LabelFrame(self.window, text = "Logs Frame", relief="solid", bd=2, bg="blue", height = 800,width=100)
        self.frame_rst.pack(side="left", fill = "both", expand = True)
        self.frame_rst2 = LabelFrame(self.window, text = "Image Frame", relief="solid", bd=2, bg="yellow", height = 800,width=100)
        self.frame_rst2.pack(side="left", fill = "both", expand = True)
        
        #GUI Display Message#######################################################################
        self.gMsg_sen_txt = "Enter the detection distance"
        self.gMsg_senConnect_start = "Sensor initial start"
        self.gMsg_senConnect_end = "Sensor initial finished"
        self.gMsg_senConnect_fail = "Sensor initial failed"
        self.gMsg_senCal_start = "Distance calibration mode start"
        self.gMsg_senCal_stop = "Sensor stopped"
        self.gMsg_senCal_end = "Distance calibration mode end"
        self.gMsg_logger_start = "Logger recording start"
        self.gMsg_camSetting_exposure = "Camera's expoure time is set to: "
        self.gMsg_camSetting_gain = "Camera's analogue gain is set to: "
        self.gMsg_camSetting_time = "Camera's timer is set to: "
        self.gMsg_camConnect_start = "Cam conection start..."
        self.gMsg_camConnect_end = "Cam initialization is complete. You can now take pictures!"
        self.gMsg_imagegrab = "Image grab start"
        self.gMsg_startUI = "Start Program"
        self.gMsg_grabOne_start = "One-time photo taking has been executed..."
        self.gMsg_grabOne_end = "One shot is over. Please check the image window."
        self.gMsg_camNoCam = "No camera was found!"
        self.gMsg_camFound = "Found a camera to connect to..."
        self.gMsg_cam_initial_start = "Camera is in initializing..."
        self.gMsg_cam_initial_end = "Camera initial is done"
        self.gMsg_senConnect_start = "Start sensor connection..."
        self.gMsg_senConnect_test = "Start sensor test..."
        self.gMsg_senConnect_end = "Complete sensor connection!"
        self.gMsg_senSetting_error = "You have set an invalid value. Please enter an integer!"
        self.gMsg_startJob_start = "Start the continuous job..."
        self.gMsg_startJob_end = "All job have been completed!"
        self.gMsg_camSetting_error = "It should be integer"
        #Label Message(Gui Label Button Message)#############################################################################
        self.gLBM_camSetting_exposure = "Exposure set"
        self.gLBM_camSetting_gain = "Gain set"
        self.gLBM_camSetting_time = "Alignment time(s)"
        self.gLBM_senConnect = "Sensor connect"
        self.gLBM_senCal = "Sensor cal."
        self.gLBM_senStop = "Sensor stop"
        self.gLBM_camConnect = "Cam connect"
        self.gLBM_camGrab_image = "Image grab"
        #Logger Message############################################################################
        self.lMsg_click_senInitial = "Sensor initial btn clicked"
        #Label#####################################################################################
        self.scroll_rst = Scrollbar(self.frame_rst, orient='vertical') #result scroll bar
        self.label_rst = Listbox(self.frame_rst, width = 100, height = 600, bg="red", relief="solid", 
                               yscrollcommand=self.scroll_rst.set) #result ListBox
        self.label_rst.pack(side="left")
        self.scroll_rst.pack(side="right",fill="y")
        self.scroll_rst.config(command=self.label_rst.yview)
        self.canvas = Canvas(self.frame_rst2, width=650, height=650)
        self.canvas.pack()
        
        self.mLabel_camSetting_exposure = Label(self.frame_cnt, text= self.gLBM_camSetting_exposure)
        self.mLabel_camSetting_exposure.pack(side="left")
        
        self.mLabel_camInput_exposure = Entry(self.frame_cnt, width=20)
        self.mLabel_camInput_exposure.insert(0,"Wait")
        self.mLabel_camInput_exposure.pack(side="left")
        
        self.mLabel_camSetting_gain = Label(self.frame_cnt, text= self.gLBM_camSetting_gain)
        self.mLabel_camSetting_gain.pack(side="left")
        
        self.mLabel_camInput_gain = Entry(self.frame_cnt, width=20)
        self.mLabel_camInput_gain.insert(0,"Wait")
        self.mLabel_camInput_gain.pack(side="left")
        
        self.mLabel_camSetting_time = Label(self.frame_cnt, text= self.gLBM_camSetting_time)
        self.mLabel_camSetting_time.pack(side="left")
        
        self.mLabel_camInput_time = Entry(self.frame_cnt, width=20)
        self.mLabel_camInput_time.insert(0,"Wait")
        self.mLabel_camInput_time.pack(side="left")
        #button######################################################################################        
          
        self.mBtn_senConnect = Button(self.frame_cnt, text = self.gLBM_senConnect,
                                command = lambda:[self.mSensor.sensor_initial()])
        self.mBtn_senConnect.pack(side = "left")
    
        self.mBtn_senCal = Button(self.frame_cnt, text = self.gLBM_senCal,
                                command = lambda:[self.mSensor.cmd_start_continuous_fast_distance_measure(0)])
        self.mBtn_senCal.pack(side = "left")
        
        self.mBtn_senStop_cal = Button(self.frame_cnt, text = self.gLBM_senStop,
                                command = lambda:[self.mSensor.cmd_terminate_continuousMode()])
        self.mBtn_senStop_cal.pack(side = "left")
    
        self.mBtn_camConnect = Button(self.frame_cnt, text = self.gLBM_camConnect, 
                                 command = lambda:[self.mCamera.cam_initial()])
        self.mBtn_camConnect.pack(side = "left")
                        
        self.mBtn_camGrab_image = Button(self.frame_cnt, text = self.gLBM_camGrab_image,
                                command = lambda:[self.mCamera.cmd_grab_image()])
        self.mBtn_camGrab_image.pack(side = "left")
        
        self.cam_initial_btn = Button(self.frame_cnt, text = 'Module initial',
                                command = lambda:[self.mCamera.cam_cmd_initial()])
        self.cam_initial_btn.pack(side = "left")
        
        self.startJob_btn = Button(self.frame_cnt, text = 'Start Job',
                                command = lambda:[self.mSensor.cmd_start_continuous_fast_distance_measure(1)])
        self.startJob_btn.pack(side = "left")
        
        self.mBtn_camSettiing_exposure = Button(self.frame_cnt, text="Exposure set", bg="green", fg="white", 
                                command= lambda:[self.btn_confirm(1)])
        self.mBtn_camSettiing_exposure.pack(side = "bottom")
        
        self.mBtn_camSetting_gain = Button(self.frame_cnt, text="Gain set", bg="green", fg="white", 
                                command= lambda:[self.btn_confirm(2)])
        self.mBtn_camSetting_gain.pack(side = "bottom")
        
        self.mBtn_camSetting_time = Button(self.frame_cnt, text="timer set", bg="green", fg="white", 
                                command= lambda:[self.btn_confirm(3)])
        self.mBtn_camSetting_time.pack(side = "bottom")
         
        #GUI Logger###################################################################################
        self.mQueueMessage = Queue()
        self.mQueueImage = Queue()
         
    def Thread_initial(self):
        self.mMessageThread = threading.Thread(target = self.message_thread, args = ())
        self.mMessageThread.start()
        self.mImageThread = threading.Thread(target = self.image_thread, args=())
        self.mImageThread.start()
        self.add_message("Program has been started")
        
    def add_message(self, data_str):
        self.mQueueMessage.put(data_str)
        #print("data_str = ", data_str)
    def job_thread(self):
        while True:
            self.mJobManager.run()
        
    def message_thread(self):
        while True:
            data = self.mQueueMessage.get(True,None)
            self.now = str(datetime.datetime.now())[0:-7]
            self.label_rst.insert(END, "[{}] {}".format(self.now, data))
            self.label_rst.update()
            self.label_rst.see(END)
            self.scroll_rst.config(command=self.label_rst.yview)
    
    def add_image(self, new_image):
        self.mQueueImage.put(new_image)
        
    
    def image_thread(self):
        while True:
            new_image = self.mQueueImage.get(True,None)
            #frame = cv2.resize(new_image, (640,480), interpolation = cv2.INTER_LINEAR)
            self.display_image=ImageTk.PhotoImage(file=new_image)
            self.canvas.create_image(300,300,image=self.display_image)
            self.label_rst.insert(END, "[{}] {}".format(self.now, "Image Grab finished"))
            self.label_rst.update()
            self.label_rst.see(END)
            self.scroll_rst.config(command=self.label_rst.yview)
       
    def btn_confirm(self, parameter):
        try:
            if parameter == 1:
                self.mCamera.kCamExposureTime = int(self.mLabel_camInput_exposure.get())
                self.mCamera.cmd_parameter_setting()
                in_text = self.gMsg_camSetting_exposure + self.mLabel_camInput_exposure.get()
                self.mLabel_camInput_exposure.configure(text=in_text)
                self.add_message(in_text)
            
            if parameter == 2:
                self.mCamera.kCamAnalogGain = int(self.mLabel_camInput_gain.get())
                self.mCamera.cmd_parameter_setting()
                in_text = self.gMsg_camSetting_gain + self.mLabel_camInput_gain.get()
                self.mLabel_camInput_gain.configure(text=in_text)
                self.add_message(in_text)

            if parameter == 3:
                self.mCamera.kCamExposureTime = int(self.mLabel_camInput_time.get())
                self.mCamera.cmd_parameter_setting()
                in_text = self.gMsg_camSetting_time + self.mLabel_camInput_time.get()
                self.mLabel_camInput_time.configure(text=in_text)
                self.add_message(in_text)
        
        except:
            self.add_message(self.gMsg_camSetting_error)
    
    def Auto_job(self):
        self.mSensor.cmd_start_continuous_fast_distance_measure(1)
        
        
                 
    def start(self):
        self.Thread_initial()
        self.window.mainloop()
        
mGUI = BK_GUI()

if __name__ == "__main__":
    mGUI.start()