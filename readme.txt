# To start the default object detector

cd ~/tflite1
source tflite1-env/bin/activate
python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --resolution=720x480

--or--

python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --resolution=720x480 --edgetpu


# To communicate with the Lego hub
# First activate the tflite environment as shown above
# Next connect a motor to port a on the hub then
cd ~/Python/Lego-Linux-Control
python3 simpleTest.py

# Note This is using a usb cable from the raspberry pi to the hub
# using the hub in this way rahter than the pi hat means
1. I can use it without a 'special' powerpack
2. I can make use of the IMU in the Hub for gyro correction of steering


Drive Wheel for the car are C+F

Steering is E

47 right
318'

You can push a motor test using ...

python pushProg.py motortest.py


After activating the tflite environment you can also use the camera to control 
the lego

cd ~/Python/LegoCam
python cam2Lego.py --modeldir=Sample_TFLite_model --resolution=720x480 --edgetpu

Note that the wiggle.py file gets sent to the Lego robot each time a person
enters the frame.

cd ~/Python/AutonomousLego
python autonomousLego.py --modeldir=Sample_TFLite_model --resolution=720x480 --edgetpu

