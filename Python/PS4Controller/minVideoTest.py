import cv2

videoCaptureObject = cv2.VideoCapture(0)


while True:
    ret,frame = videoCaptureObject.read()
    frame2 = cv2.rotate(frame, cv2.ROTATE_180)

    cv2.imshow('Video Stream', frame2)
    cv2.waitKey(1)

videoCaptureObject.release()
cv2.destroyAllWindows()
