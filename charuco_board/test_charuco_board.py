import cv2 as cv
from cv2 import aruco

# ChAruco board variables
row_count = 8
col_count = 8
square_length = 1
marker_length = 0.4
aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)

# Create constants to be passed into OpenCV and Aruco methods
board = aruco.CharucoBoard_create(
        squaresX=col_count,
        squaresY=row_count,
        squareLength=square_length,
        markerLength=marker_length,
        dictionary=aruco_dict)

arucoParams = aruco.DetectorParameters_create()
cap = cv.VideoCapture(1)

while(True):
    ret, frame = cap.read() # Capture frame-by-frame
    
    if ret == True:
        # frame_remapped = cv.remap(frame, map1, map2, cv.INTER_LINEAR, cv.BORDER_CONSTANT)    # for fisheye remapping
        im_with_charuco_board = frame.copy
        frame_remapped_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame_remapped_gray, aruco_dict, parameters=arucoParams)  # First, detect markers
        aruco.refineDetectedMarkers(frame_remapped_gray, board, corners, ids, rejectedImgPoints)

        if ids != None: # if there is at least one marker detected
            charucoretval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(corners, ids, frame_remapped_gray, board)
            im_with_charuco_board = aruco.drawDetectedCornersCharuco(frame_remapped, charucoCorners, charucoIds, (0,255,0))
            retval, rvec, tvec = aruco.estimatePoseCharucoBoard(charucoCorners, charucoIds, board, camera_matrix, dist_coeffs)  # posture estimation from a charuco board
            if retval == True:
                im_with_charuco_board = aruco.drawAxis(im_with_charuco_board, camera_matrix, dist_coeffs, rvec, tvec, 100)  # axis length 100 can be changed according to your requirement
        else:
            im_with_charuco_left = frame

        cv.imshow("charucoboard", im_with_charuco_board)

        if cv.waitKey(2) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()   # When everything done, release the capture
cv.destroyAllWindows()