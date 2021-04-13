ECEN 631 Project: Chess2Go (An Augmented Reality Chess Game)

## Intsallation Guide
1. Make sure your OpenCV was installed using `pip install opencv-contrib-python`
2. Install OpenGL using the following youtube tutuorial [Install PyOpenGL + GLUT in Windows](https://www.youtube.com/watch?v=a4NVQC_2S2U&t=314s&ab_channel=NaseemShah)
3. You will also need Pillow `pip install pillow`
4. The python pickle module was used to import camera parameters but you can edit that part to work with the camera you will use

Our project has three main components:

### 1. 3D AR rendering of a chess board and pieces

Marker tracking: we need more than one ArUco marker to make sure all 3D AR rendering remain visible during a user's hand movement.

### 2. Human hand geture detection in 3D space

We use Google Mediapipe library to do the hand tracking. 

### 3. A chess engine to keep track of the game state


## Project milestones

* Milestone 1: 

    1. Have a chess board rendered on a flat surface
    2. Detect the hand motion, specifically pinch and unpich
    3. Can play a chess game with input and output

* Milestone 2: 


* Milestone 3: 
