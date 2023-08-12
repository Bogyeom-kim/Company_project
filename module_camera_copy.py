import threading
from threading import Lock
from time import sleep
import sys
sys.path.append(r'C:\Users\kim\Desktop\code\GUI\Source')
import mvsdk
import numpy as np
import cv2
#from module_imagelogger import mImageLogger

class Camera:
    def __init__(self,GUI):
        #print("Camera __init__ start!!!")
        #self.mID = inID
        #self.mImageTest = inID
        self.camlist = []
        self.kCamExposureTime = 12 * 10000
        self.kCamAnalogGain = 70
        self.mGUI = GUI
            
    def cam_initial(self):
        self.mGUI.add_message(self.mGUI.gMsg_cam_initial_start)
        self.mGUI.mLogger.add_log(self.cam_initial.__name__ + self.mGUI.gMsg_cam_initial_start)
        self.mGUI.add_message(self.mGUI.gMsg_cam_initial_end)
        self.mGUI.mLogger.add_log(self.cam_initial.__name__ + self.mGUI.gMsg_cam_initial_end)
        self.camlist = mvsdk.CameraEnumerateDevice()
        self.nCam = len(self.camlist)
        #print("nDev = ", self.camlist)
        if self.nCam < 1:
            print("There is no camera") 
            self.mGUI.mLogger.add_log(self.cam_initial.__name__)
        else:
            print("Found a camera to connect to...")                
            self.mGUI.mLogger.add_log(self.cam_initial.__name__)
            
        for i, DevInfo in enumerate(self.camlist):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        i = 0 if self.nCam == 1 else int(input("Select camera: "))
        DevInfo = self.camlist[i]
        print("DevInfo =" , DevInfo, "\n")
                       
        try:
            self.hCamera = mvsdk.CameraInit(DevInfo, -1, -1) #OneCam
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
            return
        # 카메라 기능 설명 가져오기
        self.cap = mvsdk.CameraGetCapability(self.hCamera)
        #print("Capability = ", self.cap, "\n")
        # 흑백 카메라인지 컬러 카메라인지 확인
        self.monoCamera = (self.cap.sIspCapacity.bMonoSensor != 0)

        # 흑백 카메라를 사용하면 R=G=B인 24비트 그레이 스케일로 확장하는 대신 ISP가 MONO 데이터를 직접 출력할 수 있습니다.
        if self.monoCamera:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)
        # 카메라 모드를 연속 획득으로 전환
        #0:continuous; 1:software trigger mode; 2:hardware trigger mode 
        mvsdk.CameraSetTriggerMode(self.hCamera, 0)
        # 수동 노출, 노출 시간 30ms
        #bState：TRUE，Enable automatic exposure; FALSE, stop auto
        
        print("Cam initialization finish")
        
    def cmd_parameter_setting(self):
        mvsdk.CameraSetAeState(self.hCamera, 0)
        mvsdk.CameraSetExposureTime(self.hCamera, self.kCamExposureTime)
        mvsdk.CameraSetAnalogGain(self.hCamera, self.kCamAnalogGain)
                
        
    def cmd_grab_image(self):
        # SDK 내부 이미지 가져오기 스레드 작동 시작
        mvsdk.CameraPlay(self.hCamera)
        # 카메라의 최대 해상도에 따라 직접 할당되는 RGB 버퍼의 필요한 크기를 계산
        self.FrameBufferSize = self.cap.sResolutionRange.iWidthMax * self.cap.sResolutionRange.iHeightMax * (1 if self.monoCamera else 3)
        # ISP에서 출력한 이미지를 저장할 RGB 버퍼 할당
        # 비고 : 카메라에서 PC로 전송되는 RAW 데이터는 PC의 소프트웨어 ISP에 의해 RGB 데이터로 변환됩니다. , 따라서 이 버퍼를 할당해야 함)	pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(self.FrameBufferSize, 16)
        self.pRawData, self.FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 2000)
        mvsdk.CameraImageProcess(self.hCamera, self.pRawData, self.pFrameBuffer, self.FrameHead)
        mvsdk.CameraReleaseImageBuffer(self.hCamera, self.pRawData)
        frame_data = (mvsdk.c_ubyte * self.FrameHead.uBytes).from_address(self.pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape((self.FrameHead.iHeight, self.FrameHead.iWidth, 1 if self.FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
        frame = cv2.resize(frame, (640,480), interpolation = cv2.INTER_LINEAR)
        self.mGUI.mImageLogger.add_image(frame)
        #self.mGUI.add_image(frame)
        print("Image grab is doen")
        frame = []
        
    def is_busy(self):
        result = False
        return result

class CameraSet:
    def __init__(self,GUI):
        self.camlist = []
        self.kCamExposureTime = 12 * 10000
        self.kCamAnalogGain = 70
        self.mGUI = GUI
        self.hCamera = [0,0]

    def start(self):
        result = True
        self.mGUI.add_message(self.mGUI.gMsg_cam_initial_start)
        self.mGUI.mLogger.add_log(self.start.__name__ + self.mGUI.gMsg_cam_initial_start)
        self.cam_initial()
        self.mGUI.add_message(self.mGUI.gMsg_cam_initial_end)
        self.mGUI.mLogger.add_log(self.start.__name__ + self.mGUI.gMsg_cam_initial_end)
        return result

        return result

    def cam_initial(self):
        self.camlist = mvsdk.CameraEnumerateDevice()
        self.nCam = len(self.camlist)
        print("nDev = ", self.camlist)
        if self.nCam < 1:
            print("There is no camera") 
            self.mGUI.mLogger.add_log(self.cam_initial.__name__)
        else:
            print("Found a camera to connect to...")                
            self.mGUI.mLogger.add_log(self.cam_initial.__name__)
            
        for i, DevInfo in enumerate(self.camlist):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        
        print("DevInfo =" , self.camlist, "\n")      
        for i in range(self.nCam):
            try:
                self.hCamera[i] = mvsdk.CameraInit(self.camlist[i], -1, -1) #OneCam
            except mvsdk.CameraException as e:
                print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
                return
            
        # 카메라 기능 설명 가져오기
            self.cap = mvsdk.CameraGetCapability(self.hCamera[i])
        #print("Capability = ", self.cap, "\n")
        # 흑백 카메라인지 컬러 카메라인지 확인
            self.monoCamera = (self.cap.sIspCapacity.bMonoSensor != 0)

        # 흑백 카메라를 사용하면 R=G=B인 24비트 그레이 스케일로 확장하는 대신 ISP가 MONO 데이터를 직접 출력할 수 있습니다.
            if self.monoCamera:
                mvsdk.CameraSetIspOutFormat(self.hCamera[i], mvsdk.CAMERA_MEDIA_TYPE_MONO8)
            else:
                mvsdk.CameraSetIspOutFormat(self.hCamera[i], mvsdk.CAMERA_MEDIA_TYPE_BGR8)
            # 카메라 모드를 연속 획득으로 전환
            #0:continuous; 1:software trigger mode; 2:hardware trigger mode 
            mvsdk.CameraSetTriggerMode(self.hCamera[i], 0)
            # 수동 노출, 노출 시간 30ms
            #bState：TRUE，Enable automatic exposure; FALSE, stop auto
            mvsdk.CameraSetAeState(self.hCamera[i], 0)
            
            print("Cam initialization finish")
       
    def cmd_grab_image(self):
    # SDK 내부 이미지 가져오기 스레드 작동 시작
        mvsdk.CameraSetExposureTime(self.hCamera[0], self.kCamExposureTime)
        mvsdk.CameraSetAnalogGain(self.hCamera[0], self.kCamAnalogGain)
        mvsdk.CameraPlay(self.hCamera[0])
        # 카메라의 최대 해상도에 따라 직접 할당되는 RGB 버퍼의 필요한 크기를 계산
        self.FrameBufferSize = self.cap.sResolutionRange.iWidthMax * self.cap.sResolutionRange.iHeightMax * (1 if self.monoCamera else 3)
        # ISP에서 출력한 이미지를 저장할 RGB 버퍼 할당
        # 비고 : 카메라에서 PC로 전송되는 RAW 데이터는 PC의 소프트웨어 ISP에 의해 RGB 데이터로 변환됩니다. , 따라서 이 버퍼를 할당해야 함)	pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(self.FrameBufferSize, 16)
        self.pRawData, self.FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera[0], 2000)
        mvsdk.CameraImageProcess(self.hCamera[0], self.pRawData, self.pFrameBuffer, self.FrameHead)
        mvsdk.CameraReleaseImageBuffer(self.hCamera[0], self.pRawData)
        frame_data = (mvsdk.c_ubyte * self.FrameHead.uBytes).from_address(self.pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape((self.FrameHead.iHeight, self.FrameHead.iWidth, 1 if self.FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
        frame = cv2.resize(frame, (640,480), interpolation = cv2.INTER_LINEAR)
        self.mGUI.mImageLogger.add_image(frame)
        #self.mGUI.add_image(frame)
        print("Image grab is doen")
        frame = []     

    def ask_image(self):
        threading.Thread(target = self.CameraSet_thread, args = ()).start()
        # Thread should be created every time

    def get_image(self):
        with self.mLockImageFromCamera:
            return self.mListImageFromCamera

    def CameraSet_thread(self):
        with self.mLockFlagCameraBusy:
            self.mFlagCameraBusy = True

        with self.mLockImageFromCamera:
            self.mListImageFromCamera.clear()
            for i in range(len(self.mTupleCamera)):
                frame = self.mTupleCamera[i].grab_image()
                self.mQueueImage.put(frame)
                #self.mListImageFromCamera.append(self.mTupleCamera[i].grab_image())
                self.mListImageFromCamera.append(frame)
        
        sleep(1) #카메라 찍는 시간 1초 정도?

        with self.mLockFlagCameraBusy:
            self.mFlagCameraBusy = False

        # tell JobManager to update the new data
        from module_jobmanager import mJobManager
        from module_jobs import Job_UpdateImage
        mJobManager.add_job(Job_UpdateImage())

        return # terminate the thread

    def image_store(self):
        image = self.mQueueImage.get(True, None)
        # 저장~



#mCameras = Camera()
