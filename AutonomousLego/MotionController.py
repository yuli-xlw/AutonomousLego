import motor, motor_pair
from hub import port
from hub import light_matrix
import distance_sensor
from pyboard import Pyboard

class MotionController:
    pyboard = Pyboard()
    steerAngle = 0
    imgCount = 0

    def __init__(self,Pyboard):
        self.pyboard = Pyboard
        self.pyboard.enter_raw_repl()
        command = f"""\
import motor, motor_pair
from hub import port
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.E, port.A)

runloop.run(main())
    """
        self.pyboard.exec(command)

    def send_run(self, velocity, angle):
        iVelocity = int(velocity)
        iAngle = int(angle)
        command = f"""\
motor_pair.move(motor_pair.PAIR_1, {iAngle}, velocity={iVelocity})
    """
        self.pyboard.exec(command)
        
    def send_stop(self):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
        """
        self.pyboard.exec(command)

    def moveForward(self,velocity):
        self.send_run(velocity,self.steerAngle)

    def moveBackward(self,velocity):
        velocity = velocity * -1
        self.send_run(velocity,self.steerAngle)

    def turnLeft(self,angle):
        self.steerAngle = angle

    def turnRight(self,angle):
        self.steerAngle = angle * -1

    def stop(self):
        self.send_stop()

    def follow(self):
        command = f"""\
        """
        self.pyboard.exec(command)
