from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0

class MotionController():
    pyboard = Pyboard(device, baudrate, wait)
    velocity = 360
    steerAngle = 0
    imgCount = 0

    def __init__(self):
        #self.pyboard = Pyboard
        self.pyboard.enter_raw_repl()
        command = f"""\
import motor, motor_pair
from hub import port
import runloop
import sys

WHEEL_CIRCUMFERENCE = 17.5

def degreesForDistance(distance_cm):
    return int((distance_cm/WHEEL_CIRCUMFERENCE) * 360)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)

runloop.run(main())
    """
        self.pyboard.exec(command)

    def send_run(self, degrees, velocity, angle):
        iVelocity = int(velocity)
        iAngle = int(angle)
        iDegrees = int(degrees)
        command = f"""\
motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees=degreesForDistance({iDegrees}), steering={iAngle}, velocity={iVelocity})
    """
        self.pyboard.exec(command)
        
    def send_stop(self):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
        """
        self.pyboard.exec(command)

    def moveForward(self,degrees):
        self.send_run(degrees,self.velocity,self.steerAngle)

    def moveBackward(self,degrees):
        degrees = degrees * -1
        self.send_run(degrees,self.velocity,self.steerAngle)

    def turnLeft(self,angle):
        self.steerAngle = angle * -1

    def turnRight(self,angle):
        self.steerAngle = angle 

    def stop(self):
        self.send_stop()

    def follow(self):
        command = f"""\
        """
        self.pyboard.exec(command)
