"""
To install:

```
pip install mediapipe
```
"""

import cv2
import mediapipe as mp
import time

class HandDetector():
    def __init__(self, mode=False, max_hands=2, min_detect_confidence=0.5, min_track_confidence=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.min_detect_confidence = min_detect_confidence
        self.min_track_confidence = min_track_confidence

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.min_detect_confidence, self.min_track_confidence)
        self.mp_drawing = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        img_rgb.flags.writeable = False
        self.results = self.hands.process(img_rgb)

        # Draw the hand annotations on the image.
        # img_rgb.flags.writeable = True
        # img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            return True, img
        return False, img

    def get_coordinates(self, img, hand_no=0):
        lm_list = []

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[hand_no]
            for i, landmark in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                print(i, cx, cy)
                lm_list.append([i, cx, cy])
        return lm_list

def main():
    p_time = 0
    c_time = 0
    cap = cv2.VideoCapture(1)
    detector = HandDetector()
    while True:
        ret, img = cap.read()
        found, img = detector.find_hands(img)
        if found:
            lmList = detector.get_coordinates(img)
            # if len(lmList) != 0:
            #     print(lmList[4])
 
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