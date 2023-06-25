
# place all data used by your application
class DataManager:

    def __init__(self,GUI):
        #print("DataManager __init__ start!!!")
        self.mGUI = GUI
        self.mCurrent_Distance = 0
        self.mPrevious_Distance = 0
        self.mDistanceDiff = 0
        self.mListImagesFromCameraSet = []

    def set_sensing_distance(self, DataList): #데이터를 저장
        self.mCurrent_Distance = DataList[1]
        self.mPrevious_Distance = DataList[0]

    def get_sensing_distance(self): #이전 데이터와 거리 차이 데이터 전송
        self.mDistanceDiff = self.mPrevious_Distance - self.mCurrent_Distance 
        return self.mDistanceDiff
    
    def set_images_from_camera(self, images):
        self.mListImagesFromCameraSet = images.copy()

    def get_images_from_camera(self):
        return self.mListImagesFromCameraSet


#mDataManager = DataManager()