from pyPS4Controller.controller import Controller
from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0

class MyController(Controller):
    pyb = Pyboard(device, baudrate, wait)
    
    steerAngle = 0
    imgCount = 0

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)        
        self.pyb.enter_raw_repl()
        command = f"""\
import motor, motor_pair
from hub import port
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.E, port.A)

runloop.run(main())
    """
        self.pyb.exec(command) 
        

    def send_run(self, pyb, speed, angle):
        iSpeed = int(speed)
        iAngle = int(angle)
        command = f"""\
motor_pair.move(motor_pair.PAIR_1, {iAngle}, velocity={iSpeed})
    """
        self.pyb.exec(command)
        
    def send_stop(self, pyb):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
    """
        self.pyb.exec(command)

    def on_R2_press(self, val):
       speed = (val+32767)/(2*32767) * -1000
       print("speed: {}".format(speed))
       self.send_run(self.pyb, speed, self.steerAngle)
       
    def on_R2_release(self):
       self.send_run(self.pyb, 0, 0)
       
    def on_L2_press(self, val):
       speed = (val+32767)/(2*32767) * 1000
       print("speed: {}".format(speed))
       self.send_run(self.pyb, speed, self.steerAngle)
       
    def on_L2_release(self):
       self.send_run(self.pyb, 0, 0)

    def on_o_release(self):
       print("Goodbye world")
       self.send_stop(self.pyb)
       self.pyb.exit_raw_repl()
       self.pyb.close()
       
    def on_square_release(self):
        videoCaptureObject = cv2.VideoCapture(0)
        ret,frame = videoCaptureObject.read()
        frame2 = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imwrite('image_{}.jpg'.format(self.imgCount), frame2)
        print(f"ret value {ret}")
        videoCaptureObject.release()
        self.imgCount = self.imgCount + 1

    def on_x_release(self):
       print("Goodbye world")
       self.send_stop(self.pyb)
       videoCaptureObject.release()
       cv2.destroyAllWindows()
       
    def on_L3_left(self, val):
        self.steerAngle = 30

    def on_L3_right(self, val):
        self.steerAngle = -30

    def on_L3_x_at_rest(self):
        self.steerAngle = 0
    

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window

controller.listen(timeout=60)
