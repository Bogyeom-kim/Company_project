class Auto_mode:
    def __init__(self,GUI):
        self.mGUI = GUI
    
    def auto_mode(): 
        self.mGUI.mJobManager.run()
        self.mGUI.mSensor.cmd_start_continuous_fast_distance_measure(1)
        #print("i'm in the while loop of main.py")

        #센서 모듈 로컬 데이터를 메인스레드가 직접 읽을 경우
        #mDataManger.mSensingDistance < 50
        # 센서가 로컬 데이터를 업데이트 하는 순간 vs 메인 스레드가 읽는 순간
        # write vs read
        # 같은 데이터를 하나 이상의 스레드가 보는 경우 -> race condition, undefined behavior
#mAuto = Auto_mode()

# 센서 스레드 - mSensor
# 로거 스레드 - mLogger
# 메인 스레드 - mJobManger, mDataManager
# 카메라 스레드 - mCamera

# 모듈 간의 데이터 교환 -> Job 시작, 처리
print("done1")
