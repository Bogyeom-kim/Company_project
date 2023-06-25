import threading
from threading import Lock
from time import sleep


class Camera:
    def __init__(self, inID):
        self.mID = inID
        self.mImageTest = inID

    def start(self):
        result = True
        print("Camera(" + str(self.mID) + ") has started")
        sleep(0.5)

        return result

    def grab_image(self):
        self.mImageTest += 1
        return self.mImageTest




class CameraSet:
    def __init__(self):
        print("CameraSet Instance Initialized")
        self.mTupleCamera = ( Camera(0), Camera(1) )
        self.mListImageFromCamera = []
        self.mFlagCameraBusy = False
        self.mLockFlagCameraBusy = Lock()
        self.mLockImageFromCamera = Lock()
        self.mQueueImage = Queue()


    def start(self):
        result = True
        for camera in self.mTupleCamera:
            result &= camera.start()

        return result

    def is_busy(self):
        with self.mLockFlagCameraBusy:
            return self.mFlagCameraBusy

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



mCameras = CameraSet()
