from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0

class MotionLego:
    pyboard = Pyboard(device, baudrate, wait)

    WHEEL_CIRCUMFERENCE = 17.5
    distanceSensor = 0
    

    def __init__(self):#, Pyboard):
        #self.pyboard = Pyboard
        self.pyboard.enter_raw_repl()
        command = f"""\
import motor, motor_pair
import distance_sensor
from hub import port
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)

runloop.run(main())
    """
        self.pyboard.exec(command) 

    def degreesForDistance(self,distance_cm):
        return int((distance_cm/self.WHEEL_CIRCUMFERENCE) * 360)

    def send_run(self, distance = 0, steering = 0, velocity = 600, acceleration = 1000, deceleration = 1000, distanceLimite = 100): 
        iDegrees = int(self.degreesForDistance(distance))
        iSteering = int(steering)
        iVelocity = int(velocity)
        iAcceleration = int(acceleration)
        iDeceleration = int(deceleration)
        iDistanceLimite = int(distanceLimite)
        command = f"""\
while distance_sensor.distance(port.C) >= {iDistanceLimite}:
    motor_pair.move_for_degrees(motor_pair.PAIR_1, {iDegrees}, {iSteering}, velocity={iVelocity}, stop = motor.BRAKE, acceleration={iAcceleration}, deceleration={iDeceleration})
    """
        self.pyboard.exec(command)

    def send_stop(self):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
    """
        self.pyboard.exec(command)

    def forward(self,distance):
        self.send_run(distance)

    def forward_steering(self,distance,steering):
        self.send_run(distance,steering)

    def stop(self):
        self.send_stop()

#    def getDistanceSensor(self):
#        iDistanceSensor = self.distanceSensor
#        command = f"""\
#{iDistanceSensor} = distance_sensor.distance(port.C)
#    """
#        return iDistanceSensor