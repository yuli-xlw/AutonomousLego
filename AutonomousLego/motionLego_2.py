from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0

class MotionLego:
    pyboard = Pyboard(device, baudrate, wait)

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

    def send_run(self,steering = 0, velocity = 360, acceleration = 1000): 
        iSteering = int(steering)
        iVelocity = int(velocity)
        iAcceleration = int(acceleration)
        command = f"""\
motor_pair.move(motor_pair.PAIR_1, steering={iSteering}, velocity={iVelocity}, acceleration={iAcceleration})
    """
        self.pyboard.exec(command)
        
    def send_stop(self):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
    """
        self.pyboard.exec(command)

    def forward(self,velocity):
        self.send_run(0,velocity)

    def stop(self):
        self.send_stop()