"""
To install:

```
pip install mediapipe
```
"""

import cv2 as cv
import mediapipe as mp
import time
import math

class HandTracker():
    def __init__(self, mode=False, max_hands=2, min_detect_confidence=0.5, min_track_confidence=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.min_detect_confidence = min_detect_confidence
        self.min_track_confidence = min_track_confidence

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.min_detect_confidence, self.min_track_confidence)
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.pinch_state = False
        self.false_counter = 0 # used to avoid false negatives

    def find_hands(self, img, mirror=True, draw=True):
        # Selfie: Flip the image horizontally for a later selfie-view displayconvert
        if mirror:
            img = cv.flip(img, 1)
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        img_rgb.flags.writeable = False
        self.results = self.hands.process(img_rgb)

        # Draw the hand annotations on the image.
        # img_rgb.flags.writeable = True
        # img_rgb = cv.cvtColor(img_rgb, cv.COLOR_RGB2BGR)
        if self.results.multi_hand_landmarks:
            if draw:
                for hand_landmarks in self.results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            return True, img
        return False, img

    def _get_coordinates(self, img, hand_no=0):
        lm_list = []

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[hand_no]
            for i, landmark in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                lm_list.append([i, cx, cy])
        return lm_list

    def get_pinch(self, img, max_dist, draw=True):
        lmList = self._get_coordinates(img)
        dist = 0.0
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            dist = math.hypot(x2 - x1, y2 - y1) # pixel distance between thumb and index
            
            # if it's a pinch draw the pinch
            if dist < max_dist:
                cv.circle(img, (x1, y1), 15, (255, 0, 255), cv.FILLED)
                cv.circle(img, (x2, y2), 15, (255, 0, 255), cv.FILLED)
                cv.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv.circle(img, (cx, cy), 15, (255, 0, 255), cv.FILLED)
                self.false_counter = 0
                self.pinch_state = True
            else:
                self.false_counter += 1
                # check if the pinch state has been false for at least 5 frames in a row
                if self.false_counter >= 5:
                    self.pinch_state = False
            return self.pinch_state, (cx, cy)
    
    def get_closest_tile(frame, pinch_pt):
        # px, py = pinch_pt
        pass
        # go through the frame to discover point 

def main():
    p_time = 0
    c_time = 0
    cap = cv.VideoCapture(1)
    detector = HandTracker()
    while True:
        ret, img = cap.read()
        found, img = detector.find_hands(img)
        if found:
            lmList = detector.get_coordinates(img)
 
        c_time = time.time()
        fps = 1/(c_time - p_time)
        p_time = c_time
 
        cv.putText(img, str(int(fps)), (10, 70), cv.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
 
        cv.imshow('MediaPipe Hands', img)
        if cv.waitKey(5) & 0xFF == ord('q'):
            break
 
if __name__ == "__main__":
    main()