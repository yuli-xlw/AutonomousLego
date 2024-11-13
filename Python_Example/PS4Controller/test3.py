from pyPS4Controller.controller import Controller
from pyboard import Pyboard
from time import sleep
import cv2

baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0
videoCaptureObject = cv2.VideoCapture(0)

class MyController(Controller):
    pyb = Pyboard(device, baudrate, wait)

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)        
        self.pyb.enter_raw_repl()
        command = f"""\
import motor, motor_pair
from hub import port
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.B, port.F)

runloop.run(main())
    """
        self.pyb.exec(command)

    def send_steer(self, pyb, angle):
        command = f"""\
motor.run_to_absolute_position(port.D, {angle}, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    """
        self.pyb.exec(command)
 
        

    def send_run(self, pyb, speed):
        iSpeed = int(speed)
        command = f"""\
motor_pair.move(motor_pair.PAIR_1, 0, velocity={iSpeed})
    """
        self.pyb.exec(command)
        
    def send_stop(self, pyb):
        command = f"""\
motor_pair.stop(motor_pair.PAIR_1)
    """
        self.pyb.exec(command)

    def on_R2_press(self, val):
       speed = (val+32767)/(2*32767) * 1000
       print("speed: {}".format(speed))
       self.send_run(self.pyb, speed)
       
    def on_R2_release(self):
       self.send_run(self.pyb, 0)

    def on_o_release(self):
       print("Goodbye world")
       self.send_stop(self.pyb)
       self.pyb.exit_raw_repl()
       self.pyb.close()
       
    def on_square_release(self):
        ret,frame = videoCaptureObject.read()
        frame2 = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imwrite('image.jpg', frame2)

    def on_x_release(self):
       print("Goodbye world")
       self.send_stop(self.pyb)
       videoCaptureObject.release()
       cv2.destroyAllWindows()
       
    def on_L3_left(self, val):
        self.send_steer(self.pyb, 270)

    def on_L3_right(self, val):
        self.send_steer(self.pyb, 90)

    def on_L3_x_at_rest(self):
        self.send_steer(self.pyb, 0)
    

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)