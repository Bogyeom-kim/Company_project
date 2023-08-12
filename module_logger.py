import threading
from queue import Queue
#https://docs.python.org/3/library/queue.html

from datetime import datetime


################################################################################
class Logger:

    def __init__(self,GUI):
        #print("Logger __init__ start!!!")
        self.mLogFileFormat = "./Log/logger_"
        self.mQueue = Queue()
        self.mThread = threading.Thread(target = self.logging_thread, args = ())
        self.mGUI = GUI
        self.start()

    def start(self):
        self.mThread.start()
        self.add_log("***** BK Solution Work Logger Start *****")
        #self.mGUI.add_message(self.mGUI.gMsg_logger_start)
        return True

    def add_log(self, data_str):
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.mQueue.put([current_timestamp, data_str])

    def logging_thread(self):
        while True:
            # ��� false
            data = self.mQueue.get(True, None) # wait until any log data has been queued

            #date_format = '%Y%m%d_%H%M' # Every minute
            date_format = '%Y%m%d_%H'   # Every hour
            log_file_name = self.mLogFileFormat + datetime.now().strftime(date_format) + ".txt" 
            
            with open(log_file_name, "a") as logger_file:
                logger_file.write(str(data) + '\n')
        
################################################################################

#mLogger = Logger()

# Logger Instance
"""if __name__=='__main__':
    mLogger = Logger()
    print("mLogger start")
    mLogger.start()
"""
#1. ������ �ױ� - put
#2. ���� ������� - FIFO - First in  First Out: data.get()
#3. �����͸� ��������, �ڵ������� ������� pop - data.get()