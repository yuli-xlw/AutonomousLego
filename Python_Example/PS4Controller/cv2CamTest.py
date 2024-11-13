from pyPS4Controller.controller import Controller
from time import sleep
import cv2



class MyController(Controller):
    imgCount = 0
    
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_x_release(self):
       print("Goodbye world")
       
       cv2.destroyAllWindows()
    
    def flush_camera(self):
        self.videoCaptureObject
    
    def on_square_release(self):
        videoCaptureObject = cv2.VideoCapture(0)
        ret,frame = videoCaptureObject.read()
        frame2 = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imwrite('image_{}.jpg'.format(self.imgCount), frame)
        print(f"ret value {ret}")
        videoCaptureObject.release()
        self.imgCount = self.imgCount + 1

    

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)