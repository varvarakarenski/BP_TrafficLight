import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

img = cv.imread('Test3.jpg')
assert img is not None, "file could not be read, check with os.path.exists()"

pts1 = np.float32([[950,497],[1066,507],[939,602],[1066,612]])
# pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
pts2 = np.float32([[200,200],[300,200],[200,300],[300,300]])

M = cv.getPerspectiveTransform(pts1,pts2)
# dst = cv.warpPerspective(img,M,(300,300))
dst = cv.warpPerspective(img,M,(500,500))

cv.imshow('Webcam', dst)
cv.waitKey(0)