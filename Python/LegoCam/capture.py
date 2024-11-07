import cv2

videoCaptureObject = cv2.VideoCapture(0)

ret,frame = videoCaptureObject.read()
frame2 = cv2.rotate(frame, cv2.ROTATE_180)
cv2.imwrite('image.jpg', frame2)

videoCaptureObject.release()
cv2.destroyAllWindows()

