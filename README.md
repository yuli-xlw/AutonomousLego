### AutonomousLego

## Main Content
# To start the main object
cd ~/tflite1
source tflite1-env/bin/activate
cd ~/AutonomousLego
python autonomousLego.py --modeldir=Sample_TFLite_model --resolution=720x480 --edgetpu



## Additional Content
# To start the default object detector

cd ~/tflite1
source tflite1-env/bin/activate
python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --resolution=720x480

--or--

python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --resolution=720x480 --edgetpu