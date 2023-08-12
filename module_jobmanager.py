from queue import Queue
import threading
class JobManager:
    def __init__(self,GUI):
        print("JobManager __init__ start!!!")
        self.mGUI = GUI
        self.mQueueJob = Queue()
        self.mJobThread = threading.Thread(target = self.run, args = ())
        self.mJobThread.start()
        
    def add_job(self, new_job):
        self.mQueueJob.put(new_job)

    def run(self):
        while True:
            job = self.mQueueJob.get(True, None) # (block = True, wait = None)z: wait until any job has been queued
            if job.is_good_to_go() == True: # job = 센서 업데이트
                job.handle()

#mJobManager = JobManager()