from PyQt5.QtGui import (QPainter,
                         QPen,
                         QColor)
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication)
from PyQt5.QtCore import (Qt,
                          QCoreApplication,
                          QTimer)

import pyautogui


# class TransparentWindow(QMainWindow):

#     def __init__(
#             self,
#             x: int,
#             y: int,
#             width: int,
#             height: int,
#             pen_color: str,
#             pen_size: int):
#         super().__init__()
#         self.highlight_x = x
#         self.highlight_y = y
#         self.highlight_width = width
#         self.highlight_height = height
#         self.pen_color = pen_color
#         self.pen_size = pen_size
#         self.initUI()

#     def initUI(self):
#         """Initialize the user interface of the window."""
#         self.setGeometry(
#             self.highlight_x,
#             self.highlight_y,
#             self.highlight_width + self.pen_size,
#             self.highlight_height + self.pen_size)
#         self.setStyleSheet('background: transparent')
#         self.setWindowFlag(Qt.FramelessWindowHint)

#     def paintEvent(self, event):
#         """Paint the user interface."""
#         painter = QPainter()
#         painter.begin(self)
#         painter.setPen(QPen(QColor(self.pen_color), self.pen_size))
#         painter.drawRect(
#             self.pen_size - 1,
#             self.pen_size - 1,
#             self.width() - 2 * self.pen_size,
#             self. height() - 2 * self.pen_size)
#         painter.end()



def normalize_visual_mouse_input(raw_location: int, axis: str):
    """normalizes input to fit in smaller window than default camera size"""

    X_COOR_NORMALIZATION_MIN = 0.20
    X_COOR_NORMALIZATION_MAX = 0.80

    Y_COOR_NORMALIZATION_MIN = 0.1
    Y_COOR_NORMALIZATION_MAX = 0.45

    if axis == "x":

        normalized_location = ((raw_location - X_COOR_NORMALIZATION_MIN)) / (X_COOR_NORMALIZATION_MAX - X_COOR_NORMALIZATION_MIN)

    else:

        normalized_location = ((raw_location - Y_COOR_NORMALIZATION_MIN)) / (Y_COOR_NORMALIZATION_MAX - Y_COOR_NORMALIZATION_MIN)

    return normalized_location


def is_micro_movement(current_hand_data, historical_hand_data):

    if len(historical_hand_data) < 2:

        return False

    last_x_coor = historical_hand_data[-2]["INDEX_TIP"].x
    last_y_coor = historical_hand_data[-2]["INDEX_TIP"].y

    current_x_coor = current_hand_data["INDEX_TIP"].x
    current_y_coor = current_hand_data["INDEX_TIP"].y

    # May break it out into more statements or change to or
    # Cuz if moving in straight line along x axis then y axis wont change and will be with the range
    # Of micromovements but also this current solution could reduce sporatic y movement in that case
    if ((last_x_coor < current_x_coor * 0.9955) or (last_x_coor > current_x_coor * 1.0045) and
        (last_y_coor < current_y_coor * 0.9955) or (last_y_coor > current_y_coor * 1.0045)):

        return False

    return True


def finger_mouse_handler(gesture: str, frame_counter: int, hand_data: dict, historical_hand_data: list, gestures: list):

    tmp_monitor_length = 2560
    tmp_monitor_height = 1440

    # Where mediapipe says index is on screen -
    # So we need to map that mediapipe landmark to qt cursor

    tip_loc_x = hand_data["INDEX_TIP"].x
    tip_loc_y = hand_data["INDEX_TIP"].y

    # This method causes a jump when u hit 50% of screen with finger (30% of screen with mouse)
    # then it will jump to right hemisphere
    normalized_x_tip_location = normalize_visual_mouse_input(tip_loc_x, "x")
    normalized_y_tip_location = normalize_visual_mouse_input(tip_loc_y, "y")

    video_index_location_x = int(normalized_x_tip_location * tmp_monitor_length)
    video_index_location_y = int(normalized_y_tip_location * tmp_monitor_height)

    print("INDEX ON SCREEN X:", tip_loc_x)
    print("NORMALIZED X:", normalized_x_tip_location)

    # Above note: So we know mediapipe gives percent of distance from top left for x y coor
    # So if far left montior is 0% that means we will send cursor to far left
    # But if we said index finger at 0% is really 3 inches left off screen that mean
    # 20% from left will translate to cursor being much close to the edge

    # Notes add 0.1 to percent work well when moving to right but causes the left side to not fully cover movitor
    # Cuz its moving the border 0.1% to the right so its reducing left side of monitor
    # So we can split into four quadrants where if index_tip.x is < 0.5 we subtract 0.1
    # Actually dont think this is good because then when going from 0.49% to 0.51% will cause massive jump
    # Distance needs to be percent based i think


    # More logic - so if finger at 20% x coor we want it to really map to 0%
    # So on video mediapipe we will get 20% - 50% for left x hemisphere 

    # Should be simple movement of qt window around screen
    # With some logic to support smooth window movement
    # And reduction of micro movements
    global is_mouse_clicked
    if gesture == "FINGER_POINTING":

        if frame_counter % 3: # Only move cursor ever 3 frames (reduces micro movements due to finger shakes or model inaccuracies)

            if is_micro_movement(hand_data, historical_hand_data):

                return

            window.move(video_index_location_x, video_index_location_y)

            is_mouse_clicked = False

        return
    
    else:

        if is_mouse_clicked is True:

            return

        pyautogui.click(video_index_location_x, video_index_location_y)

        is_mouse_clicked = True

    return


def get_finger_positon():

    return
