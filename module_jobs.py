class Job:

    def __init__(self,GUI):
        self.mGUI = GUI

    def is_good_to_go(self):
        pass

    def handle(self):
        pass

# 센서
# - 데이터 업데이트
# - 데이터를 비교
# 카메라
# - 요청
# - 결과를 업데이트
# - 분석
#로봇
# - 움직인다

class Job_inital_module:
    def __init__(self):
        pass
    def is_good_to_go(self):
        pass
    
# 센서 데이터 업데이트
class Job_UpdateSensorDistance:
    def __init__(self,GUI):
        self.mGUI = GUI

    def is_good_to_go(self): # override
        result = True
        log_data = self.__class__.__name__ + "->" + self.is_good_to_go.__name__ + ": " + str(result)
        self.mGUI.mLogger.add_log(log_data)
        self.mGUI.add_message(log_data)
        return result

    def handle(self): # override
        self.mGUI.mDataManager.set_sensing_distance(self.mGUI.mSensor.get_sensing_distance()) # 메인 스레드
        log_data = self.__class__.__name__ + "->" + self.handle.__name__ + ": " + str(self.mGUI.mDataManager.get_sensing_distance()) + " mm"
        self.mGUI.mLogger.add_log(log_data)
        self.mGUI.add_message(log_data)
        self.mGUI.mJobManager.add_job(self.mGUI.mJob_CheckSensorDistance)

# 센서 데이터 체크
class Job_CheckSensorDistance(Job):
    def __init__(self,GUI): # override
        self.mGUI = GUI
        self.mDistanceDiff = 0 # 추후 변경될 예정.

    def is_good_to_go(self): # override
        result = True
        log_data = self.__class__.__name__ + "->" + self.is_good_to_go.__name__ + ": " + str(result)
        self.mGUI.mLogger.add_log(log_data)
        return result


    def handle(self): # override
        detected = False

        if self.mGUI.mDataManager.get_sensing_distance() == self.mDistanceDiff:
            print("**************Detected!!!**********************")
            self.mGUI.mJobManager.add_job(self.mGUI.mJob_AskGrabImage)
            detected = True

        log_data = self.__class__.__name__ + "->" + self.handle.__name__ + ": " + str(detected)
        self.mGUI.mLogger.add_log(log_data)


# 카메라 촬영 요청
class Job_AskGrabImage(Job):
    
    def __init__(self,GUI): # override if it is required
        self.mGUI = GUI
    
    def is_good_to_go(self): # override if it is required
        # check whether the camera is busy
        #result = not (mCameras.is_busy())
        result = True
        log_data = self.__class__.__name__ + "->"+ self.is_good_to_go.__name__ + ": " + str(result)
        self.mGUI.mLogger.add_log(log_data)
        return result

    def handle(self): # override if it is required
        log_data = self.__class__.__name__ + "->"+ self.handle.__name__
        self.mGUI.mLogger.add_log(log_data)
        self.mGUI.mCamera.cmd_grab_image()


# 이미지 업데이트
class Job_UpdateImage(Job):

    def __init__(self,GUI): # override if it is required
        self.mGUI = GUI
    
    def is_good_to_go(self): # override if it is required
        # check whether the camera is busy
        result = not (mCameras.is_busy())
        log_data = self.__class__.__name__ + "->"+ self.is_good_to_go.__name__ + ": " + str(result)
        mLogger.add_log_data(log_data)
        return result

    def handle(self): # override if it is required
        mDataManager.set_images_from_camera(mCameras.get_image())
        log_data = self.__class__.__name__ + "->"+ self.handle.__name__ + ": " + str(mDataManager.get_images_from_camera())
        mLogger.add_log_data(log_data)
##########################################################################################################
#이미지 저장
class Job_ImageSave(Job):
    def __init__(self):
        pass
    
    def is_good_to_go(self):
        result = True
        log_data = self.__class__.__name__ + "->" + self.is_good_to_go.__name__ + ": " + str(result)
        mLogger.add_log_data(log_data)
        return result
    
    def handle(self):
        filePath = self.dirPath+"/Image_"+ str(fileName)+self.pictureFormat#fileSave
        cv2.imwrite(filePath,frame)

# 이미지 분석
class Job_AnalyzeImage(Job):

    def __init__(self): # override if it is required
        pass
    
    def is_good_to_go(self): # override if it is required
        pass


    def handle(self): # override if it is required
        pass


# 로봇팔 작동
class Job_RobotArm(Job):

    def __init__(self): # override if it is required
        pass
    
    def is_good_to_go(self): # override if it is required
        pass


    def handle(self): # override if it is required
        pass