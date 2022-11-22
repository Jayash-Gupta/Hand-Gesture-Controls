##importing all the required libraries ##
import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import screen_brightness_control as sbc
import time
import pyautogui
import os
#########################################

print("Press 1: to access Volume Control")
print("Press 2: to access Brightness Control")
print("Press 3: for Play/Pause")
control_in=int(input()) # control input by user

def count_fingers(lst):
    cnt = 0

    thresh = (lst.landmark[0].y*100 - lst.landmark[9].y*100)/2

    if (lst.landmark[5].y*100 - lst.landmark[8].y*100) > thresh:
        cnt += 1

    if (lst.landmark[9].y*100 - lst.landmark[12].y*100) > thresh:
        cnt += 1

    if (lst.landmark[13].y*100 - lst.landmark[16].y*100) > thresh:
        cnt += 1

    if (lst.landmark[17].y*100 - lst.landmark[20].y*100) > thresh:
        cnt += 1

    if (lst.landmark[5].x*100 - lst.landmark[4].x*100) > 6:
        cnt += 1
    return cnt

cap = cv2.VideoCapture(0)    # Checks for camera
pTime=0     #  FPS
mpHands = mp.solutions.hands  # detects hand/fin2ger
hands = mpHands.Hands()  # complete the initialization configuration of hands
mpDraw = mp.solutions.drawing_utils
dd=mp.solutions.hands
hand_obj = dd.Hands(max_num_hands=1)
start_init = False
prev = -1

# To access speaker through the library pycaw
devices = AudioUtilities.GetSpeakers()      # get speakers access by pycaw
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volbar = 400        # Volume level in rectangular bar
volper = 0          # Volume level in %

volMin, volMax = volume.GetVolumeRange()[:2]

if(control_in==1):
    while True:

        success, img = cap.read()  # If camera works capture an image
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to rgb

        # Collection of gesture information
        results = hands.process(imgRGB)  # completes the image processing.

        lmList = []  # empty list
        if results.multi_hand_landmarks:  # list of all hands detected.
            # By accessing the list, we can get the information of each hand's corresponding flag
            for handlandmark in results.multi_hand_landmarks:
                for id, lm in enumerate(handlandmark.landmark):  # adding counter and returning it
                    # Get finger joint points
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])  # adding to the empty list 'lmList'
                mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

        if lmList != []:
            # getting the value at a point
            # x      #y
            x1, y1 = lmList[4][1], lmList[4][2]  # thumb
            x2, y2 = lmList[8][1], lmList[8][2]  # index finger
            # x3, y3 = lmList[12][1], lmList[12][2] # middle finger
            # creating circle at the tips of thumb and index finger
            cv2.circle(img, (x1, y1), 13, (255, 0, 0), cv2.FILLED)  # image #fingers #radius #rgb
            cv2.circle(img, (x2, y2), 13, (255, 0, 0), cv2.FILLED)  # image #fingers #radius #rgb
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)  # create a line b/w tips of index finger and thumb

            length = hypot(x2 - x1, y2 - y1)  # distance b/w tips using hypotenuse
            # from numpy we find our length,by converting hand range in terms of volume range ie b/w -63.5 to 0
            vol = np.interp(length, [30, 350], [volMin, volMax])
            volbar = np.interp(length, [30, 350], [400, 150])
            volper = np.interp(length, [30, 350], [0, 100])

            print(vol, int(length))
            volume.SetMasterVolumeLevel(vol, None)

            # Hand range 30 - 350
            # Volume range -63.5 - 0.0
            # creating volume bar for volume level
            # cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255),4)  # vid ,initial position ,ending position ,rgb ,thickness
            cv2.rectangle(img, (65, int(volbar)), (85, 400), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, f"{int(volper)}%", (50, 120), cv2.FONT_ITALIC, 1, (0, 0, 0), 1)
            # tell the volume percentage ,location,font of text,length,rgb color,thickness

        #############################################################################################
        #                                        FPS                                                #
        #############################################################################################
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        #############################################################################################

        end_time = time.time()
        res = hand_obj.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if res.multi_hand_landmarks:

            hand_keyPoints = res.multi_hand_landmarks[0]

            cnt = count_fingers(hand_keyPoints)
            print(cnt)

            if not (prev == cnt):
                if not (start_init):
                    start_time = time.time()
                    start_init = True

                elif (end_time - start_time) > 0.1:

                    if (cnt == 5):
                        break

                    prev = cnt
                    start_init = False

            mpDraw.draw_landmarks(img, hand_keyPoints, dd.HAND_CONNECTIONS)

        cv2.imshow('Image', img)  # Show the video
        if cv2.waitKey(1) & 0xff == ord(' '):  # By using spacebar delay will stop
            break
if(control_in==2):
    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Collection of gesture information
        results = hands.process(imgRGB)
        lmList = []     # empty list
        if results.multi_hand_landmarks:

            # By accessing the list, we can get the information of each hand's corresponding flag
            for handlandmark in results.multi_hand_landmarks:
                for id, lm in enumerate(handlandmark.landmark):

                    # get finger joint points
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])     # Adding to the empty list "lmList"
                mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

        if lmList != []:
            # getting the value at a poinnt2
            # x      #y
            x1, y1 = lmList[4][1], lmList[4][2]     # Thumb
            x3, y3 = lmList[12][1], lmList[12][2]  # middle finger
            # x2, y2 = lmList[8][1], lmList[8][2]  # index finger

            cv2.circle(img, (x1, y1), 4, (255, 0, 0), cv2.FILLED)       # image #fingers #radius #rgb
            cv2.circle(img, (x3, y3), 4, (255, 0, 0), cv2.FILLED)       # image #fingers #radius #rgb
            cv2.line(img, (x1, y1), (x3, y3), (255, 0, 0), 3)           # create a line b/w tips of index finger and thumb

            # create a circle on the finger pointed by it # image # finger # radius # rgb
            cv2.circle(img, (x1, y1), 13, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 13, (255, 0, 0), cv2.FILLED)
            length = hypot(x3 - x1, y3 - y1)    # distance b/w tips using hypotenuse

            # from numpy we find our length, by converting hand range in terms of brightness range
            bright = np.interp(length, [15, 220], [0, 100])     # to get the current brightness # int
            bribar = np.interp(length, [150, 220], [400, 150])         # get brightness info for bightness bar

            # print(bright, length)
            sbc.set_brightness(int(bright))

            # Hand range
            # Brightness range
            # creating brightness bar for brightness level
            cv2.rectangle(img, (65, int(bribar)), (85, 400), (0, 0, 0), cv2.FILLED)     #
            cv2.putText(img, f"{int(bright)}%", (50, 120), cv2.FONT_ITALIC, 1, (0, 0, 0), 1)

        #############################################################################################
        #                                        FPS                                                #
        #############################################################################################
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS:{int(fps)}', (480, 400), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        #############################################################################################

        end_time = time.time()
        res = hand_obj.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if res.multi_hand_landmarks:

            hand_keyPoints = res.multi_hand_landmarks[0]

            cnt = count_fingers(hand_keyPoints)
            print(cnt)

            if not (prev == cnt):
                if not (start_init):
                    start_time = time.time()
                    start_init = True

                elif (end_time - start_time) > 0.2:

                    if (cnt == 5):
                        break

                    prev = cnt
                    start_init = False

            mpDraw.draw_landmarks(img, hand_keyPoints, dd.HAND_CONNECTIONS)

        cv2.imshow('Image', img)        # show the video
        if cv2.waitKey(1) & 0xff == ord('q'):        # By using spacebar delay will stop
            break

if(control_in==3):
    while True:

        end_time = time.time()
        success, img = cap.read()
        img = cv2.flip(img, 1)

        res = hand_obj.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        #############################################################################################
        #                                        FPS                                                #
        #############################################################################################
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS:{int(fps)}', (480, 400), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        #############################################################################################


        if res.multi_hand_landmarks:

            hand_keyPoints = res.multi_hand_landmarks[0]

            cnt = count_fingers(hand_keyPoints)
            print(cnt)

            if not (prev == cnt):
                if not (start_init):
                    start_time = time.time()
                    start_init = True

                elif (end_time - start_time) > 0.2:
                    if (cnt == 1):
                        pyautogui.press("left")

                    elif (cnt == 2):
                        pyautogui.press("right")

                    elif (cnt == 3):
                        os.startfile('Death Note Hindi Ep-19.mp4')

                    elif (cnt == 5):
                        break

                    if (cnt == 4):
                        pyautogui.press("space")

                    prev = cnt
                    start_init = False
            mpDraw.draw_landmarks(img, hand_keyPoints, dd.HAND_CONNECTIONS)
        cv2.imshow('Image', img)  # show the video
        if cv2.waitKey(1) & 0xff == ord('q'):  # By using spacebar delay will stop
            break

cap.release()  # stop cam
cv2.destroyAllWindows()  # close window
