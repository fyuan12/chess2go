"""
This is a sample code to find the pinch point in a video stream

The HandTracker class has two main methods:
- find_hands() returns 1) whether a hand is found and 2) the flipped image
- get_pinch(): returns 1) whether a pinch is detected and 2) the xy coordinates of the pinch point
"""

import cv2
import time
import numpy as np
from hand_tracker import HandTracker

MAX_PINCH_DIST = 100

def main():
    p_time = 0
    c_time = 0
    cap = cv2.VideoCapture(1)

    tracker = HandTracker(min_detect_confidence=0.7)

    while True:
        ret, img = cap.read()

        found, img = tracker.find_hands(img, mirror=True, draw=False)
        # if at least one hand is found
        if found:
            detected, pinch_pt = tracker.get_pinch(img, max_dist=MAX_PINCH_DIST, draw=True)
            if detected:
                print('A pinch is detected:', pinch_pt) # the x,y coordinate of the pinch point
            else:
                print('A pinch is not detected.')

        # calculate and output fps
        c_time = time.time()
        fps = 1/(c_time - p_time)
        p_time = c_time
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
 
        cv2.imshow('MediaPipe Hands', img)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
 
if __name__ == "__main__":
    main()