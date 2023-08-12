import serial
from time import sleep
from enum import Enum
#from module_jobmanager import mJobManager
#from module_logger import mLogger
from threading import Thread, Lock, Event
import threading


SERIAL_PORT      = "COM3"
SERIAL_BAUD_RATE = 19200

#REGISTER_REPLY_READ_MODULE_ADDRESSS      = 0x0000
#REGISTER_REPLY_READ_HW_VERSION           = 0x0001
#REGISTER_REPLY_READ_INPUT_VOLTAGE        = 0x0006
#REGISTER_REPLY_SET_MODULE_ADDRESS        = 0x0010
#REGISTER_REPLY_SET_MODULE_MEASURE_OFFSET = 0x0012
#REGISTER_REPLY_READ_HW_VERSION           = 0x000C
#REGISTER_REPLY_READ_SERIAL_NUMBER        = 0x000E
#REGISTER_REPLY_READ_MEASURE_RESULT       = 0x0022
#REGISTER_REPLY_TURN_ONOFF_LASER          = 0x01BE
#REGISTER_REPLY_1SHOT_AUTO_MEASURE        = 0x0022 #1shot_slow, 1shot_fast, continuous_auto, continuous_slow, continuous_fast


class SENSOR_REPLY_NAME(Enum):
    HEAD               = 0
    RWADDRESS          = 1
    REGISTER1          = 2
    REGISTER2          = 3
    PAYLOAD_COUNT1     = 4
    PAYLOAD_COUNT2     = 5
    PAYLOAD_DISTANCE   = 6
    PAYLOAD_SQ         = 7
    CHECKSUM           = 8

    RESET              = 9


################################################################################
class Sensor:
    def __init__(self,GUI):
        #print("Sensor __init__ start!!!")
        self.mSensingMode = 0
        self.mSensorThreadEvent = Event()
        self.mSerial = 1
        print("Now mSerial")
        self.mSerial = serial.Serial(SERIAL_PORT, SERIAL_BAUD_RATE, timeout = None)
        self.mCurrentReplyName = SENSOR_REPLY_NAME.HEAD #### Start
        self.mFirstDistance = 0
        self.mSecondDistance = 0
        self.mThirdDistance = 0
        self.mDataList = [9999,9999]
        self.mLockForSensingDistance = Lock() #Lock 함수 가져오기
        self.mGUI = GUI
        self.mSensorThread = Thread(target = self.read_thread, args = ())
        
    def sensor_initial(self):
        result = False
        print("Hello")
        self.mGUI.add_message(self.mGUI.gMsg_senConnect_start)
        if self.cmd_baud_rate_detect() == True:
            self.cmd_check_status()
            self.mGUI.add_message(self.mGUI.gMsg_senConnect_end)
            #self.cmd_start_continuous_fast_distance_measure()
            self.mSensorThread.start()
        else:
            self.mGUI.add_message(self.mGUI.gMsg_senConnect_fail)
        return result

    def cmd_baud_rate_detect(self):
        self.mSerial.rts = True
        sleep(0.1)
        self.mSerial.rts = False
        print("Baud end")
        
        #self.mSerial.write(0x55)
        print("Send 0x55")
        return True
        #received_address = int.from_bytes(self.mSerial.read(), "big", signed = False)
        #print("recived data", received_address)
        #if (received_address == 0x00):
            #log_data_result = "Success - Address: " + str(received_address)
            #result = True
            #sleep(0.1)
        #else:
            #log_data_result = "Failed"
            #result = False

        return result

    def cmd_check_status(self):
        print("cmd_check")
        sensor_command_checkStatus = [0xAA, 0x80, 0x00, 0x00, 0x80]
        self.mSerial.write(sensor_command_checkStatus)
        reply = self.mSerial.read(9)
        print("reply!", reply)

    def cmd_start_continuous_fast_distance_measure(self,mode):
        self.mSensingMode = mode #Sensor mode setting
        self.mSensorThreadEvent.clear() #clear: make event value to be false, set make event value to be true 
        sensor_command_start_continuous_fast = [0xAA, 0x00, 0x00, 0x24, 0x00, 0x01, 0x00, 0x07, 0x2C]
        self.mSerial.write(sensor_command_start_continuous_fast)
        self.mCurrentReplyName = SENSOR_REPLY_NAME.HEAD #### Start
        self.mGUI.add_message("Thread_getident = "+str(threading.get_ident())) #get thread id


    def get_sensing_distance(self): # with 문으로 lock을 하면 aqiure(), release()를 안해줘도 된다.
        with self.mLockForSensingDistance:
            self.mDataList = [self.mFirstDistance,self.mSecondDistance, self.mThirdDistance]
            #self.mGUI.add_message("the get_sensing_distance=", self.mDataList)
            return self.mDataList


    def read_thread(self):

        # Constants for Reply 1-shot auto
        ################################################
        REPLY_1SHOT_AUTO_HEAD              = 0xAA
        REPLY_1SHOT_AUTO_RWADDRESS         = 0x00
        REPLY_1SHOT_AUTO_REGISTER_MSB8     = 0x00
        REPLY_1SHOT_AUTO_REGISTER_LSB8     = 0x22
        REPLY_1SHOT_AUTO_PAYLOADCOUNT_MSB8 = 0x00
        REPLY_1SHOT_AUTO_PAYLOADCOUNT_LSB8 = 0x03
        ################################################

        data = []
        count = 0 # for payload distance and payload SQ
        while True:
            temp = int.from_bytes(self.mSerial.read(), "big", signed = False)
            
            self.mFirstDistance = self.mSecondDistance
            self.mSecondDistance = self.mThirdDistance          
            
            if self.mCurrentReplyName == SENSOR_REPLY_NAME.HEAD:
                if temp == REPLY_1SHOT_AUTO_HEAD:
                    data.append(temp)
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RWADDRESS
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET
        
            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.RWADDRESS:
                if temp == REPLY_1SHOT_AUTO_RWADDRESS:
                    data.append(temp)
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.REGISTER1
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.REGISTER1:
                if temp == REPLY_1SHOT_AUTO_REGISTER_MSB8:
                    data.append(temp)
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.REGISTER2
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.REGISTER2:
                if temp == REPLY_1SHOT_AUTO_REGISTER_LSB8:
                    data.append(temp)
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.PAYLOAD_COUNT1
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.PAYLOAD_COUNT1:
                if temp == REPLY_1SHOT_AUTO_PAYLOADCOUNT_MSB8:
                    data.append(temp)
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.PAYLOAD_COUNT2
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.PAYLOAD_COUNT2:
                if temp == REPLY_1SHOT_AUTO_PAYLOADCOUNT_LSB8: # 3
                    data.append(temp)
                    count = (temp + 1) # Payload = 4 bytes
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.PAYLOAD_DISTANCE
                else:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.PAYLOAD_DISTANCE:
                data.append(temp)
                count -= 1 # 4->3 3->2 2->1 1->0
                if count == 0:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.PAYLOAD_SQ
                    count = 2 # SQ = 2 bytes

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.PAYLOAD_SQ:
                data.append(temp)
                count -= 1 # 2->1 1->0
                if count == 0:
                    self.mCurrentReplyName = SENSOR_REPLY_NAME.CHECKSUM

            elif self.mCurrentReplyName == SENSOR_REPLY_NAME.CHECKSUM:
                if temp == sensor_checksum(data):
                    new_distance = sensor_distance_conversion(data)
                    
                    # read
                    ###########################################################
                    #with self.mLockForSensingDistance:
                    self.mThirdDistance = new_distance # local update
                    ###########################################################
                    #if SensingMode == 1:
                    # tell JobManager to grab the new data
                    #print("i'm before the if loop of sensor.py")
                    #from module_jobs import Job_UpdateSensorDistance
                    #print("i'm after the if loop of sensor.py")
                    #mJobManager.add_job(Job_UpdateSensorDistance())
                    if self.mSensingMode == 0:
                        self.mGUI.add_message((str(new_distance)+' mm'))

                    elif self.mSensingMode == 1:
                        self.mGUI.add_message((str(new_distance)+' mm'))
                        self.mGUI.mLogger.add_log((str(new_distance)+' mm'))
                        self.mGUI.mJobManager.add_job(self.mGUI.mJob_UpdateSensorDistance)
                        #print("What is type? ", type(self.mGUI.mJob_UpdateSensorDistance))
                    
                    
                self.mCurrentReplyName = SENSOR_REPLY_NAME.RESET


            if self.mCurrentReplyName == SENSOR_REPLY_NAME.RESET:
                data.clear()
                count = 0
                self.mCurrentReplyName = SENSOR_REPLY_NAME.HEAD
                
            #if self.mSensorThreadEvent.is_set():
                #self.mGUI.add_message(self.mGUI.gMsg_senCal_stop)
                #break
    
    def cmd_terminate_continuousMode(self):
        sensor_command_terminateContinuousMode = [0x58]
        sensor_command_turnOFFLaser = [0xAA, 0x00, 0x01, 0xBE, 0x00, 0x01, 0x00,0x01]
        self.mSerial.write(sensor_command_terminateContinuousMode)
        #reply = self.mSerial.read()
        print("sensor stop")
        self.mSerial.write(sensor_command_turnOFFLaser)
        print("sensor turn off")
        #self.mSensorThreadEvent.set()
        
        
################################################################################


# Local Functions
def sensor_checksum(data_list):
    result = 0
    for i in range(1,12,1):
        result += data_list[i]
    result &= 0xFF # Overflow ignored
    return result

def sensor_distance_conversion(data_list):
    #distance = data_list[6] + data_list[7] + data_list[8] + data_list[9]
    distance  = (data_list[6] << (8 * 3))
    distance |= (data_list[7] << (8 * 2))
    distance |= (data_list[8] << (8 * 1))
    distance |= (data_list[9] << (8 * 0))
    return distance

if __name__ == "__main__":
    # Sensor Instance
    mSensor = Sensor()
    mSensor.start()
    mSensor.cmd_start_continuous_fast_distance_measure(0)
    sleep(10)
    mSensor.cmd_terminate_continuousMode()