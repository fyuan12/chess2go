# Chess2Go Project Summary

Team members: Christian Carver, Sequoia Ploeg, Franklin Yuan

## Overview
Chess2Go is a fun and interactive way to play chess. By using a Charuco chess board and the camera parameters of a webcam the program allows one to play augmented reaslity chess. The Charuco board is used to easily identify the playing area for both the program and the players. The program uses it to estimate the 3d pose of where the chessboard will be and the player can use it to know how to interact with the augmented reality pieces. Using openGL and chess models created in blender we are able to render the augmented reality pieces to the screen and make it feel like you are playing real chess. Under the hood it uses the chess python library to keep track of the game and ensure we play legal moves. 


## Idea generation
We wanted to use something with 3d information. One of our original ideas was to make a reverse 3d printer where we would get the 3d inforation of an object in real life and then make a .stl or .obj file form that. We also thought it would be cool to use some of the stuff we learned from our augmented reality project and maybe render some things in 3d. We thought we could also make it interactive somehow and thats how we came up with the idea of AR chesss


## Challenges
There were a lot of challeenges we faced when doing this project. On the openGL side of things challanges included positioning of all the individual pieces at once ensuring they had all the same relative rotation but different translations, performance when all the pieces at once, what to do when a hand covers the marker the board doesn't disappear, ect. On the interaction sice of things we had to figure out how to track a hand and a chess board at the same time let alone track specific movements like a pinch and where a pinch in the 3d world corresponds to the openGL world of the chessboard.  


## Solutions
OpenGL: Using blender's decimate function we were able to decrease the number of vertices for each object which greatly improved our game launching time and frame rate when rendering the pieces with impovements of load times in the minutes to a few seconds and frame rates from low single digits to 30+ fps. We ended up not using just a single aruco tag for the 3d estimation and opted for a charuco board which solved the issue of a hand interupting the image and an issue of the player knowing where their hand is relative to the board. 

Hand information: One of the harder ploblems we needed to solve was how to figure out which square a pinch corresponds to. This is not a trivial problem since the grid of possible values can be almost any arbitray range and since the board can be rotated or translated in 3d figuring out which square isn't as simple and just checking whether a pixel location is less then or greater than a certain nubmer. We ended up using what we learned from our homography project to beble to work get the correct perspective transform of the corners of each square and then using an algorithm to map a pixel location to a specific square. Another issue we solved was ensuring proper state updates when attempting to pick up a piece and move it somewhere. 


## Individual Contributions

Christian: I worked mostly with the rendering of the augmented parts which included optimization of our 3d objects using blender and figuring out the correct way to map the pose we got from the board to the 3d world of our openGL world. 

Sequoia: Chess functionality

Franklin: Hand detection


## Video recording link

[https://youtu.be/NrvClDfRyTk](https://youtu.be/NrvClDfRyTk)

## Source code

Due to the large size of our source code, we are not uploading it to the Learning Suite. You can check it out or clone and run it yourself at this [Github repo](https://github.com/fyuan12/chess2go).