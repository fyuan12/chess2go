import cv2 as cv
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from threading import Thread
import numpy as np
import pickle
from objloader import *
from pathlib import Path

INVERSE_MATRIX = np.array([ [ 1.0, 1.0, 1.0, 1.0],
                            [-1.0,-1.0,-1.0,-1.0],
                            [-1.0,-1.0,-1.0,-1.0],
                            [ 1.0, 1.0, 1.0, 1.0]])

texture_id = 0
thread_quit = 0
X_AXIS = 0.0
Y_AXIS = 0.0
Z_AXIS = 0.0
DIRECTION = 1
current_view_matrix = np.array([])
new_frame = np.array([])
white_pieces = {}
zoom = -20.0
aruco_d = 5.5
aruco_x = 0
aruco_y = 0
aruco_z = 0

# Set the needed parameters to find the refined corners
winSize = (5, 5)
zeroZone = (-1, -1)
criteria = (cv.TERM_CRITERIA_EPS + cv.TermCriteria_COUNT, 40, 0.001)

cap = cv.VideoCapture(1)
global mtx, dist, newcameramtx, roi
_, mtx, dist, _, _ = pickle.load(open("my_camera_calibration.p", "rb"))
new_frame = cap.read()[1]
h,  w = new_frame.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx,dist,(w,h),0,(w,h))

# Start a thread for the camera
def init():
    video_thread = Thread(target=update, args=())
    video_thread.start()

# Initialize opengl frame and load in .obj files into opengl
def init_gl(width, height):
    global texture_id
    global white_pieces
    global black_pieces
    global chessboard

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, 640/480, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    def load_item(item):
        return OBJ(item, swapyz=True)
    
    chessboard = OBJ("Chessboard/Chessboard.obj", swapyz=False)

    # for item in Path("White").glob("*.obj"):
    #     if "King" in item.name:
    #         white_pieces["king"] = load_item(item)
    #     elif "Queen" in item.name:
    #         white_pieces["queen"] = load_item(item)
    #     elif "Rook" in item.name:
    #         white_pieces["rook"] = load_item(item)
    #     elif "Bishop" in item.name:
    #         white_pieces["bishop"] = load_item(item)
    #     elif "Pawn" in item.name:
    #         white_pieces["pawn"] = load_item(item)
    #     elif "Knight" in item.name:
    #         white_pieces["knight"] = load_item(item) 
    
    # for item in Path("Black").glob("*.obj"):
    #     if "King" in item.name:
    #         black_pieces["king"] = load_item(item)
    #     elif "Queen" in item.name:
    #         black_pieces["queen"] = load_item(item)
    #     elif "Rook" in item.name:
    #         black_pieces["rook"] = load_item(item)
    #     elif "Bishop" in item.name:
    #         black_pieces["bishop"] = load_item(item)
    #     elif "Pawn" in item.name:
    #         black_pieces["pawn"] = load_item(item)
    #     elif "Knight" in item.name:
    #         black_pieces["knight"] = load_item(item) 
        
    # assign texture
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)

# Augmented Reality with opencv and opengl
def track(frame):
    global mtx
    global dist
    global white_pieces
    global black_pieces
    global chessboard
    global aruco_d
    global aruco_x
    global aruco_y
    global aruco_z

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
    gray = cv.GaussianBlur(gray, winSize, 0)
    aruco_dict = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_50)  
    parameters = cv.aruco.DetectorParameters_create()  
    parameters.cornerRefinementMethod = cv.aruco.CORNER_REFINE_SUBPIX
    corners, ids, _ = cv.aruco.detectMarkers(gray, aruco_dict,
                                              parameters=parameters,
                                              cameraMatrix=mtx,
                                              distCoeff=dist)
    # if len(corners) > 0:
    #     corners = cv.cornerSubPix(gray, np.array(corners), winSize, zeroZone, criteria)
    #     print(type(corners))
    if np.all(ids is not None):  # If there are markers found by detector
        # print(ids)
        for i in range(0, len(ids)):  # Iterate in markers
            # Estimate pose of each marker and return the values rvec and tvec

            rvec, tvec, markerPoints = cv.aruco.estimatePoseSingleMarkers(corners[i], aruco_d, mtx, dist)
            rmtx = cv.Rodrigues(rvec)[0]

            view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0,0,0]],
                                    [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[0,0,1]],
                                    [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[0,0,2]],
                                    [0.0       ,0.0       ,0.0       ,1.0    ]])
            view_matrix = view_matrix * INVERSE_MATRIX
            view_matrix = np.transpose(view_matrix)
            glPushMatrix()
            glLoadMatrixd(view_matrix)
            
            glTranslate(aruco_x, aruco_y, aruco_z)
            glRotate(90, 1, 0, 0)
            glRotate(90, 0, 1, 0)

            
            vals = ['pawn', 'knight', 'king', 'rook', 'bishop', 'queen']
            # if ids[i] == 1:
            # print(vals[i])
            # white_pieces['queen'].render()
            # elif ids[i] == 2:
            #     white_pieces['knight'].render()
            # elif ids[i] == 3:
            #     white_pieces['king'].render()
            # else:
            #     obj.render()
            chessboard.render()

            glPopMatrix()

            # #(rvec - tvec).any()  # get rid of that nasty numpy value array error
            # cv.aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers
            # cv.aruco.drawAxis(frame, mtx, dist, rvec, tvec, 0.05)  # Draw Axis

    cv.imshow('frame', frame)

# Update and undistort each camera frame
def update():
    global new_frame
    while(True):
        frame = cap.read()[1]
            # undistort
        dst = cv.undistort(frame, mtx, dist)

        # crop the image
        x,y,w,h = roi
        dst = dst[y:y+h, x:x+w]
        new_frame = dst
        if thread_quit == 1:
            break
    cap.release()
    cv.destroyAllWindows()

# Main drawing loop
def draw_gl_scene():
    global new_frame
    global texture_id
    global zoom

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glLoadIdentity()
    frame = new_frame
    glDisable(GL_DEPTH_TEST)
    # convert image to OpenGL texture format
    tx_image = cv.flip(frame, 0)
    tx_image = Image.fromarray(tx_image)
    ix = tx_image.size[0]
    iy = tx_image.size[1]
    tx_image = tx_image.tobytes('raw', 'BGRX', 0, -1)
    # create texture
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, tx_image)
    

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPushMatrix()
    glTranslatef(0.0, 0.0, zoom)

    # draw background
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex3f(-8.0, -6.0, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f( 8.0, -6.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f( 8.0,  6.0, 0.0)
    glTexCoord2f(0.0, 0.0); glVertex3f(-8.0,  6.0, 0.0)
    glEnd()
    glPopMatrix()
    
    # RENDER OBJECT
    glEnable(GL_DEPTH_TEST)
    track(frame)
    
    glutSwapBuffers()

# Keyboard control loop
def key_pressed(key, x, y):
    global thread_quit
    global zoom
    global aruco_d
    global aruco_x
    global aruco_y
    global aruco_z
    key = key.decode("utf-8") 
    if key == "q":
        thread_quit = 1
        os._exit(1)
    elif key == "m":
        zoom += 0.1
        print(f"zoom: {zoom}")
    elif key == "n":
        zoom -= 0.1
        print(f"zoom: {zoom}")
    elif key == "a":
        aruco_z += 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == "z":
        aruco_z -= 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == "s":
        aruco_x += 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == "x":
        aruco_x -= 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == "d":
        aruco_y += 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == "c":
        aruco_y -= 0.5
        print(f"pos: ({aruco_x}, {aruco_y}, {aruco_z})")
    elif key == ".":
        aruco_d += 0.5
        print(f"aruco_d: {aruco_d}")
    elif key == ",":
        aruco_d -= 0.5
        if aruco_d <= 0:
            aruco_d = 0.001
        print(f"aruco_d: {aruco_d}")


def run():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(800, 400)
    window = glutCreateWindow('My and Cube')
    glutDisplayFunc(draw_gl_scene)
    glutIdleFunc(draw_gl_scene)
    glutKeyboardFunc(key_pressed)
    init_gl(640, 480)
    glutMainLoop()


if __name__ == "__main__":
    init()
    run()