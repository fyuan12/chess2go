import cv2 as cv
from cv2 import aruco
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from threading import Thread
import numpy as np
import pickle
from objloader import *
from pathlib import Path
from pychess import BoardTiles
import time
import cProfile, pstats, io
from hand_tracker import HandTracker, PinchState

# Update per computer
cap = cv.VideoCapture(1)
_, mtx, dist, _, _ = pickle.load(open("camera_params/my_camera_calibration.p", "rb"))
# with np.load('camera_params/cap_int_params.npz') as data:
#     mtx, dist = data['arr_0'], data['arr_1']

# Hand tracking variables
max_pinch_dist = 50
min_pinch_dist = 20
p_time = 0
c_time = 0
tracker = HandTracker(min_detect_confidence=0.7)
start_pinch = 0

board = 0 #initialize a board object

INVERSE_MATRIX = np.array([ [ 1.0, 1.0, 1.0, 1.0],
                            [-1.0,-1.0,-1.0,-1.0],
                            [-1.0,-1.0,-1.0,-1.0],
                            [ 1.0, 1.0, 1.0, 1.0]])

texture_id = 0
thread_quit = 0
current_view_matrix = np.array([])
new_frame = np.array([])
zoom = -16.5
aruco_d = 2.08
aruco_x = 14.5
aruco_y = 1.5
aruco_z = 0
c_d = 1

# Set the needed parameters to find the refined corners
winSize = (5, 5)
zeroZone = (-1, -1)
criteria = (cv.TERM_CRITERIA_EPS + cv.TermCriteria_COUNT, 40, 0.001)

# Charuco board variables
aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)

aruco_params = aruco.DetectorParameters_create()

rvec = np.array([])
tvec = np.array([])
pinched_piece = None

new_frame = cap.read()[1]
h, w = new_frame.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx,dist,(w,h),0,(w,h))

# Start a thread for the camera
def init():
    video_thread = Thread(target=update, args=())
    video_thread.start()
    console_thread = Thread(target=console, args=())
    console_thread.start()

def console():
    global board
    while board == 0:
        continue
    while True:
        try:
            move = input(f'Enter move for {"white" if board.board.turn else "black"}: ')
            board.board.push_uci(move)
        except ValueError:
            print("Invalid move")


def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

# Initialize opengl frame and load in .obj files into opengl
def init_gl(width, height):
    global texture_id
    global board

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()
    gluPerspective(40, 640/480, 0.1, 100.0)
    #glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
    glLight(GL_LIGHT0, GL_POSITION,  (5, 5, 5, 1)) # point light from the left, top, front
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glMatrixMode(GL_MODELVIEW)

    def load_item(item):
        return OBJ(item, swapyz=True)
    
    tiles = {}
    for item in Path("Tiles").glob("*.obj"):
        if "Black" in item.name:
            tiles["black"] = OBJ(item)
        elif "White" in item.name:
            tiles["white"] = OBJ(item)
        elif "DarkBlue" in item.name:
            tiles["dblue"] = OBJ(item)
        elif "LightBlue" in item.name:
            tiles["lblue"] = OBJ(item)
        elif "Dark" in item.name:
            tiles["dark"] = OBJ(item)
        elif "Light" in item.name:
            tiles["light"] = OBJ(item)
        
        
    print(f"loaded tiles: {tiles.keys()}")

    white_pieces = {}
    for item in Path("WhiteLP").glob("*.obj"):
        if "King" in item.name:
            white_pieces["king"] = load_item(item)
        elif "Queen" in item.name:
            white_pieces["queen"] = load_item(item)
        elif "Rook" in item.name:
            white_pieces["rook"] = load_item(item)
        elif "Bishop" in item.name:
            white_pieces["bishop"] = load_item(item)
        elif "Pawn" in item.name:
            white_pieces["pawn"] = load_item(item)
        elif "Knight" in item.name:
            white_pieces["knight"] = load_item(item) 
    print("loaded white pieces")
    
    black_pieces = {}
    for item in Path("BlackLP").glob("*.obj"):
        if "King" in item.name:
            black_pieces["king"] = load_item(item)
        elif "Queen" in item.name:
            black_pieces["queen"] = load_item(item)
        elif "Rook" in item.name:
            black_pieces["rook"] = load_item(item)
        elif "Bishop" in item.name:
            black_pieces["bishop"] = load_item(item)
        elif "Pawn" in item.name:
            black_pieces["pawn"] = load_item(item)
        elif "Knight" in item.name:
            black_pieces["knight"] = load_item(item) 

    print("loaded the black pieces")

    board = BoardTiles(tiles["black"], tiles["white"], tiles["dark"], tiles["light"], black_pieces, white_pieces, tiles["dblue"], tiles["lblue"], 2)
        
    # assign texture
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)

# Augmented Reality with opencv and opengl
def track(frame):
    global mtx
    global dist
    global aruco_d
    global aruco_x
    global aruco_y
    global aruco_z
    global p_time
    global c_time
    global c_d
    global start_pinch
    global rvec
    global tvec
    global pre_pos
    global post_pos
    global pinched_piece

    # From charuco board to 3D rendering
    hand_frame = np.copy(frame)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)  # First, detect markers
    charuco_board = aruco.CharucoBoard_create(
        squaresX=8,
        squaresY=8,
        squareLength=aruco_d,
        markerLength=aruco_d*0.7,
        dictionary=aruco_dict)
    aruco.refineDetectedMarkers(gray, charuco_board, corners, ids, rejectedImgPoints)
    
    all_corners = np.empty((49,2), dtype=np.float32)
    if np.all(ids is not None): # if there is at least one marker detected
        c_retval, c_corners, c_ids = aruco.interpolateCornersCharuco(corners, ids, gray, charuco_board)
        hand_frame = aruco.drawDetectedCornersCharuco(frame, c_corners, c_ids, (0,255,0))
        retval, rvec, tvec = aruco.estimatePoseCharucoBoard(c_corners, c_ids, charuco_board, mtx, dist, rvec, tvec)  # posture estimation from a charuco board

        # if pose estimation is successful, render the chessboard and chess pieces
        if retval:
            c_corners = np.reshape(np.array(c_corners), (-1, 2))
            for i in range(len(c_corners)):
                all_corners[c_ids[i]] = c_corners[i]
    
            rmtx = cv.Rodrigues(rvec)[0]
            view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0,0]],
                                    [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[1,0]],
                                    [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[2,0]],
                                    [0.0       ,0.0       ,0.0       ,1.0    ]])
            view_matrix = view_matrix * INVERSE_MATRIX
            view_matrix = np.transpose(view_matrix)

            # Draw Chessboard
            for dx, dy, tile in board.get_tiles():
                glPushMatrix()
                glLoadMatrixd(view_matrix)
                
                glTranslate(aruco_x + c_d*dx*-1, aruco_y + c_d*dy, aruco_z)
                glRotate(90, 1, 0, 0)
                glRotate(90, 0, 1, 0)
                
                tile.render()
                glPopMatrix()

            # Draw Pieces
            for dx, dy, piece in board.get_pieces():
                glPushMatrix()
                glLoadMatrixd(view_matrix)
                
                glTranslate(aruco_x + c_d*dx*-1, aruco_y + c_d*dy, aruco_z)
                glRotate(90, 1, 0, 0)
                glRotate(90, 0, 1, 0)
                
                piece.render()
                glPopMatrix()

    # detect pinch/unpinch actions
    found, hand_frame = tracker.find_hands(hand_frame, mirror=False, draw=False)

    # if at least one hand is found
    if found:
        pinch_state, pinch_pt = tracker.get_pinch(hand_frame, max_dist=max_pinch_dist, min_dist=min_pinch_dist, draw=True) # pinch_pt: the pixel coordinates of the pinch point

    # with pinch point coordinate and all corners coordinates, generate the tile that the pinch point is in
    chpts = np.array([[1,1],
                  [1,7],
                  [7,7],
                  [7,1]], dtype=np.float32)
    pts = all_corners[np.array([6,0,42,48])]
    
    # translate to the tile number
    if pts.all() and found:
        m = cv.getPerspectiveTransform(pts.astype(np.float32), chpts)
        pinch_pt = np.array([pinch_pt[0], pinch_pt[1], 1])
        coords = m @ pinch_pt
        valid_coords = True

        for coord in coords[0:2]:
            if coord < 0 or coord > 8:
                valid_coords = False
        
        if valid_coords:
            letter_index = int(coords[0])
            number_index = int(coords[1])
            index = int(coords[0])+int(coords[1])*8

            if pinch_state == PinchState.PINCH and pinched_piece is None:
                board.set_active_tile(index)
                pinched_piece = "{}{}".format(board.LETTERS[letter_index], board.NUMBERS[number_index])
                print("Select piece:", pinched_piece)

            elif pinch_state == PinchState.UNPINCH and pinched_piece is not None:
                board.set_active_tile(index)
                # make the move
                move_str = "{}{}{}".format(pinched_piece, board.LETTERS[letter_index], board.NUMBERS[number_index])
                print("Move: ", move_str)
                try:
                    board.board.push_uci(move_str)
                except ValueError:
                    print("Invalid move")
                pinched_piece = None

    # calculate and output fps
    c_time = time.time()
    fps = 1/(c_time - p_time)
    p_time = c_time
    cv.putText(hand_frame, str(int(fps)), (10, 70), cv.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    cv.imshow('frame', hand_frame)

# Update and undistort each camera frame
def update():
    global new_frame
    while(True):
        new_frame = cap.read()[1]
        #     # undistort
        # dst = cv.undistort(frame, mtx, dist)

        # # crop the image
        # x,y,w,h = roi
        # dst = dst[y:y+h, x:x+w]
        # new_frame = dst
        if thread_quit == 1:
            break
    cap.release()
    cv.destroyAllWindows()

# Main drawing loop
def draw_gl_scene():
    global new_frame
    global texture_id
    global zoom
    global mtx
    global dist

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glLoadIdentity()

    frame = np.copy(new_frame)
    dst = cv.undistort(frame, mtx, dist)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    glDisable(GL_DEPTH_TEST)
    # convert image to OpenGL texture format
    tx_image = cv.flip(dst, 0)
    tx_image = Image.fromarray(tx_image)
    ix = tx_image.size[0]
    iy = tx_image.size[1]
    tx_image = tx_image.tobytes('raw', 'BGRX', 0, -1)
    # create texture
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
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
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # RENDER OBJECT
    glEnable(GL_DEPTH_TEST)
    track(new_frame)
    
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHTING)
    glutSwapBuffers()

# Keyboard control loop
def key_pressed(key, x, y):
    global thread_quit
    global zoom
    global aruco_d
    global aruco_x
    global aruco_y
    global aruco_z
    global c_d
    global board
    global pre_pos
    global post_pos

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
        aruco_d += 0.01
        print(f"aruco_d: {aruco_d}")
    elif key == ",":
        aruco_d -= 0.01
        if aruco_d <= 0:
            aruco_d = 0.001
        print(f"aruco_d: {aruco_d}")
    elif key == ";":
        c_d += 0.01
        print(f"aruco_d: {c_d}")
    elif key == "'":
        c_d -= 0.01
        if c_d <= 0:
            c_d = 0.01
        print(f"aruco_d: {c_d}")
    elif key == "t":
        row, col = board.uci_to_rc('e2')
        print(f"row: {row} col: {col}")
        ind = (row)*8+(col)
        print(f"ind: {ind}")
        board.set_active_tile(ind)
        print(f"pos: {str(board.board)}")
    elif key == "y":
        board.board.push_uci('e2e4')
        row, col = board.uci_to_rc('e7')
        print(f"row: {row} col: {col}")
        ind = (row)*8+(col)
        print(f"ind: {ind}")
        board.set_active_tile(ind)
        print(f"pos: {str(board.board)}")
    elif key == "u":
        board.board.push_uci('e7e5')
        row, col = board.uci_to_rc('f1')
        print(f"row: {row} col: {col}")
        ind = (row)*8+(col)
        print(f"ind: {ind}")
        board.set_active_tile(ind)
        print(f"pos: {str(board.board)}")
    elif key == "i":
        board.board.push_uci('f1b5')
        row, col = board.uci_to_rc('c7')
        print(f"row: {row} col: {col}")
        ind = (row)*8+(col)
        print(f"ind: {ind}")
        board.set_active_tile(ind)
        print(f"pos: {str(board.board)}")
    elif key == '1':
        pre_pos[0] -= 30
        print(f"pre_pos: {pre_pos}")
    elif key == '4':
        pre_pos[0] += 30
        print(f"pre_pos: {pre_pos}")
    elif key == '2':
        pre_pos[1] -= 30
        print(f"pre_pos: {pre_pos}")
    elif key == '5':
        pre_pos[1] += 30
        print(f"pre_pos: {pre_pos}")
    elif key == '3':
        pre_pos[2] -= 30
        print(f"pre_pos: {pre_pos}")
    elif key == '6':
        pre_pos[2] += 30
        print(f"pre_pos: {pre_pos}")


def run():
    # import cProfile
    # cProfile.run('main()', "output.dat")

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()

    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(0, -800)
    window = glutCreateWindow('OPENGL Frame')
    glutDisplayFunc(draw_gl_scene)
    glutIdleFunc(draw_gl_scene)
    glutKeyboardFunc(key_pressed)
    init_gl(640, 480)
    glutMainLoop()

def main():
    try:
        init()
        run()
    except TypeError:
        print("We should just pass")
        pass

if __name__ == "__main__":
    main()