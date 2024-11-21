from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0

class MotionLego:
    pyboard = Pyboard(device, baudrate, wait)
    
    steerAngle = 0
    imgCount = 0

    def __init__(self, Pyboard):
        self.pyboard = Pyboard
        self.pyboard.enter_raw_repl()
        command = f"""\
import motor, motor_pair
from hub import port
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)

runloop.run(main())
    """
        self.pyboard.exec(command) 
        

    def send_run(self, speed, angle):
        iSpeed = int(speed)
        iAngle = int(angle)
        command = f"""\
motor_pair.move(motor_pair.PAIR_1, {iAngle}, velocity={iSpeed})
    """
        self.pyboard.exec(command)
        
    def send_stop(self):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
    """
        self.pyboard.exec(command)

    def forward(self,speed):
        self.send_run(speed,self.steerAngle)

    def stop(self):
        self.send_stop()