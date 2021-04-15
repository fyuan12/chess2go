# Chess2Go Project Summary

Team members: Christian Carver, Sequoia Ploeg, Franklin Yuan

## Overview
Chess2Go is a fun and interactive way to play chess. By using a ChArUco chess board and the camera parameters of a webcam the program allows one to play augmented reality chess. The ChArUco board is used to easily identify the playing area for both the program and the players. The program uses it to estimate the 3D pose of where the chessboard will be and the players use it to know how to interact with the augmented reality pieces. Using OpenGL and chess models created in blender we are able to render the augmented reality pieces to the screen and make it feel like playing real chess. Under the hood it uses the chess python library to keep track of the game and ensure we play legal moves.


## Idea generation
We wanted to use something with 3D information. One of our original ideas was to make a reverse 3D printer where we would get the 3D information of an object in real life and then make a `.stl` or `.obj` file form that. We also thought it would be cool to use some of the stuff we learned from our augmented reality project and maybe render some things in 3D. We thought we could also make it interactive somehow and thats how we came up with the idea of AR chess.

## Challenges
There were a lot of challeenges we faced when doing this project. 

3D rendering: we had several challanges, including making sure all individual chess pieces are rendered at once with the same relative rotation but different translations and keeping the chess board from disappearing when a hand covers the fiducial markers.

Gesture tracking: we had to figure out how to detect a hand in the video frame and track its movement. We also experimented with various techniques to track specific hand movements such as pinching and unpinching in attempts to move AR chess pieces.


## Solutions
3D Rendering: Using blender's decimate function we were able to decrease the number of vertices for each object which greatly improved our game launching time and frame rate when rendering the pieces with impovements of load times from in the minutes to a few seconds and frame rates from low single digits to 30+ fps. We ended up not using a single ArUco marker for the 3D estimation and opted for a ChArUco chess board which solved the issue of hand covering the marker and helps the players know where to move their hands relative to the rendered 3D chess board.

Gesture tracking: we first used image segmentation to track the hand's pinch motion and achieved little success. After much research, we settled on utilizing the MediaPipe library, a pre-trained model from Google, to track the players' hand gestures. The tracking results turned out to be both fast and accurate.

Chess playing: One of the harder ploblems we needed to solve was how to figure out which square a hand pinch motion corresponds to. This is not a trivial problem since the grid of possible values can be almost any arbitray range and since the board can be rotated or translated in 3D figuring out which square isn't as simple as just checking whether a pixel location is less then or greater than a certain nubmer. We ended up using what we learned from our homography project to get the correct perspective transform of the corners of each square and then using an algorithm to map a pixel location to a specific square. Another issue we solved was ensuring proper state updates when attempting to pick up a piece and move it somewhere. 

## Individual Contributions

Christian: I worked mostly with the rendering of the augmented parts which included optimization of our 3D objects using blender and figuring out the correct way to map the pose we got from the board to the 3D world of our OpenGL world. 

Sequoia: Chess functionality

Franklin: I worked mostly with devising algorithms to track the hand gestures and pinch/unpinch motions. I also wrote code to generate our ChArUco chess board for the game

## Video recording link

[https://youtu.be/NrvClDfRyTk](https://youtu.be/NrvClDfRyTk)

## Source code

Due to the large size of our source code, we are not uploading it to the Learning Suite. You can check it out or clone and run it yourself at this [Github repo](https://github.com/fyuan12/chess2go).