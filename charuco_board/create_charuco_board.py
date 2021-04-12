import cv2 as cv
from cv2 import aruco

# ChAruco board variables
row_count = 8
col_count = 8
square_length = 1
marker_length = 0.7
aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)

# Create constants to be passed into OpenCV and Aruco methods
board = aruco.CharucoBoard_create(
        squaresX=col_count,
        squaresY=row_count,
        squareLength=square_length,
        markerLength=marker_length,
        dictionary=aruco_dict)

imboard = board.draw((2000, 2000))
cv.imshow('board', imboard)
cv.imwrite('charuco_board/charuco_board.png', imboard)
cv.waitKey(0)