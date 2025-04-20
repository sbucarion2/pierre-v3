from typing import List, Dict
import cv2
import mediapipe as mp

from visual_mouse3.hand_gesture_operations import router


from PyQt5.QtGui import (QPainter,
                         QPen,
                         QColor)
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication)
from PyQt5.QtCore import (Qt,
                          QCoreApplication,
                          QTimer)


def get_handedness_data(results):

    handedness_data = results.multi_handedness

    hand_index = {}
    for hand in handedness_data:

        hand_index[hand.classification[0].label] = hand.classification[0].index

    return hand_index


def get_hand_data(landmarks, mp_hands):

    hand_data = {}

    hand_data["INDEX_TIP"] = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    hand_data["INDEX_MID"] = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]

    hand_data["MIDDLE_TIP"] = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    hand_data["MIDDLE_MID"] = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

    hand_data["RING_TIP"] = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    hand_data["RING_MID"] = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]

    hand_data["PINKY_TIP"] = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    hand_data["PINKY_MID"] = landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]

    hand_data["THUMB_TIP"] = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    hand_data["THUMB_IP"] = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

    return hand_data


def calculate_finger_placements(hand_data, hand):

    finger_placement = {}

    finger_placement["INDEX_FINGER"] = "EXTENDED" if hand_data["INDEX_TIP"].y <= hand_data["INDEX_MID"].y else "CLOSED"
    finger_placement["MIDDLE_FINGER"] = "EXTENDED" if hand_data["MIDDLE_TIP"].y <= hand_data["MIDDLE_MID"].y else "CLOSED"
    finger_placement["RING_FINGER"] = "EXTENDED" if hand_data["RING_TIP"].y <= hand_data["RING_MID"].y else "CLOSED"
    finger_placement["PINKY_FINGER"] = "EXTENDED" if hand_data["PINKY_TIP"].y <= hand_data["PINKY_MID"].y else "CLOSED"

    if hand == "Left":

        finger_placement["LEFT_THUMB_SIDE_EXTENSION"] = "EXTENDED" if hand_data["THUMB_TIP"].x > hand_data["THUMB_IP"].x else "CLOSED"


    if hand == "Right":

        finger_placement["RIGHT_THUMB_SIDE_EXTENSION"] = "EXTENDED" if hand_data["THUMB_TIP"].x < hand_data["THUMB_IP"].x else "CLOSED"

    return finger_placement


def determine_frame_gesture(finger_placement):

    gesture = None

    if (finger_placement["INDEX_FINGER"] == "EXTENDED" and 
        finger_placement["MIDDLE_FINGER"] == "CLOSED" and 
        finger_placement["RING_FINGER"] == "CLOSED" and 
        finger_placement["PINKY_FINGER"] == "CLOSED"):

        if "RIGHT_THUMB_SIDE_EXTENSION" in finger_placement:

            if finger_placement["RIGHT_THUMB_SIDE_EXTENSION"] == "EXTENDED":

                gesture = "FINGER_POINTING_CLICK"

            else:

                gesture = "FINGER_POINTING"


    if (finger_placement["INDEX_FINGER"] == "CLOSED" and 
        finger_placement["MIDDLE_FINGER"] == "CLOSED" and 
        finger_placement["RING_FINGER"] == "CLOSED" and 
        finger_placement["PINKY_FINGER"] == "CLOSED"):

        gesture = "CLOSED"


    if (finger_placement["INDEX_FINGER"] == "EXTENDED" and 
        finger_placement["MIDDLE_FINGER"] == "EXTENDED" and
        finger_placement["RING_FINGER"] == "EXTENDED" and 
        finger_placement["PINKY_FINGER"] == "EXTENDED"):

        gesture = "OPEN"


    if (finger_placement["INDEX_FINGER"] == "EXTENDED" and 
        finger_placement["MIDDLE_FINGER"] == "CLOSED" and
        finger_placement["RING_FINGER"] == "CLOSED" and 
        finger_placement["PINKY_FINGER"] == "EXTENDED"):

        gesture = "COYOTE"


    if (finger_placement["INDEX_FINGER"] == "EXTENDED" and 
        finger_placement["MIDDLE_FINGER"] == "CLOSED" and
        finger_placement["RING_FINGER"] == "CLOSED" and 
        finger_placement["PINKY_FINGER"] == "CLOSED"):

        if "LEFT_THUMB_SIDE_EXTENSION" in finger_placement:

            if finger_placement["LEFT_THUMB_SIDE_EXTENSION"] == "EXTENDED":

                gesture = "SQUEEZE"


    if (finger_placement["INDEX_FINGER"] == "EXTENDED" and 
        finger_placement["MIDDLE_FINGER"] == "CLOSED" and
        finger_placement["RING_FINGER"] == "CLOSED" and 
        finger_placement["PINKY_FINGER"] == "EXTENDED" and
        finger_placement["LEFT_THUMB_SIDE_EXTENSION"] == "EXTENDED"):

        gesture = "ROCK"

    print(gesture)

    return gesture


def get_gesture(results, frame, mp_drawing, mp_hands) -> Dict[str, Dict]:

    # If hand is present on screen
    if not results.multi_hand_landmarks:

        return None, None
    
    # Print Hand Landmarks on videos
    for landmarks in results.multi_hand_landmarks:

        mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    # Perform landmark operations
    hand_indicies = get_handedness_data(results)

    # Length will be one if one had detected, if 2 hands on screen len == 2
    # For now this will only read one hand (first to appear) on the screen
    # So if index is 0 we wont read second hand data but it will be present

    # RIGHT HAND INDEX WILL ALWAYS BE 1 EVEN IF NO LEFT HAND PRESENT
    # NEED TO DECREMENT RIGHT INDEX BY 1 IF LEFT HAND IS NONE

    ### IMPORTANT: ALL LEFT HGAND GESTURES WILL OVERRIDE RIGHT HAND IF BOTH ARE PRESENT

    hand_gesture_data = {}
    for hand, index in hand_indicies.items():

        if "LEFT" not in hand_indicies: # Need to refactor for redundencies 

            index = 0

        hand_landmark_data = results.multi_hand_landmarks[index]

        hand_data = get_hand_data(hand_landmark_data, mp_hands)

        finger_placement = calculate_finger_placements(hand_data, hand)

        gesture = determine_frame_gesture(finger_placement)

        hand_gesture_data[hand] = {
            "GESTURE": gesture, 
            "DATA": hand_data
        }

    # left_hand_gesture = hand_gestures.get("Left", None)
    # right_hand_gesture = hand_gestures.get("Right", None)

    return hand_gesture_data


def store_hand_data(pierre_client, hand_gesture_data):

    for hand in ["Left", "Right"]:

        if hand_gesture_data == (None, None):

            return {
                hand: {
                    "GESTURE": None, 
                    "DATA": None
                }
            }
        
        hand_data = hand_gesture_data.get(hand, {})

        pierre_client.hand_data_stack[hand.upper()]["GESTURE"].append(hand_data.get("GESTURE", None))
        pierre_client.hand_data_stack[hand.upper()]["DATA"].append(hand_data.get("DATA", None))


# def create_cursor():


#     app = QApplication([])
#     window = TransparentWindow(50, 50, 5, 5, "#aaaa00", 2)
#     window.setWindowOpacity(1)
#     window.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
#     # window.show()

#     self.cursor_window = window


def mouse_handler(pierre_client):

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    is_mouse_clicked = False

    app = QApplication([])
    window = pierre_client.window_object(50, 50, 5, 5, "#aaaa00", 2)
    window.setWindowOpacity(1)
    window.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
    window.show()

    
    while cap.isOpened():

        ret, frame = cap.read()

        # mirror image
        frame = cv2.flip(frame, 1)

        # Convert to rgb --bgr is cv ka default...convert to rgb bcs mediapipe rgb me operate krta hai
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        hand_gesture_data = get_gesture(results, frame, mp_drawing, mp_hands)

        store_hand_data(pierre_client, hand_gesture_data)

        router(pierre_client, window)

        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):

            break

    cap.release()
    cv2.destroyAllWindows()