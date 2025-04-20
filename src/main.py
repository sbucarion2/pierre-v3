import time
from typing import List
import cv2
import pyautogui
import mediapipe as mp
import threading
from multiprocessing import Queue, Process
from screeninfo import get_monitors

from spotify_utils.spotify_auth import create_spotify_client
from spotify_utils.spotify_controller import get_spotify_device_id
from visual_mouse3.mouse import mouse_handler


from PyQt5.QtGui import (QPainter,
                         QPen,
                         QColor)
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication)
from PyQt5.QtCore import (Qt,
                          QCoreApplication,
                          QTimer)


class TransparentWindow(QMainWindow):

    def __init__(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            pen_color: str,
            pen_size: int):
        super().__init__()
        self.highlight_x = x
        self.highlight_y = y
        self.highlight_width = width
        self.highlight_height = height
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.initUI()

    def initUI(self):
        """Initialize the user interface of the window."""
        self.setGeometry(
            self.highlight_x,
            self.highlight_y,
            self.highlight_width + self.pen_size,
            self.highlight_height + self.pen_size)
        self.setStyleSheet('background: transparent')
        self.setWindowFlag(Qt.FramelessWindowHint)

    def paintEvent(self, event):
        """Paint the user interface."""
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(QColor(self.pen_color), self.pen_size))
        painter.drawRect(
            self.pen_size - 1,
            self.pen_size - 1,
            self.width() - 2 * self.pen_size,
            self. height() - 2 * self.pen_size)
        painter.end()


class Pierre:

    def __init__(self):

        self.get_hardware_info()
        self.setup_pierre_spotify()

        self.window_object = TransparentWindow


        # Record all hand placement and gestures
        self.hand_data_stack = {
            "LEFT": {
                "GESTURE": [],
                "DATA": [],
            }, 
            "RIGHT": {
                "GESTURE": [],
                "DATA": [],
            }
        }

    
    def setup_pierre_spotify(self):

        self.spotify_client = create_spotify_client()
        self.spotify_device = get_spotify_device_id(self.spotify_client)
        self.spotify_metadata = {
            "isPlaying": False,
            "isPause": False,
            "spotifyOn": False,
        }

    
    def get_hardware_info(self):

        hardware_info = {"MONITORS": {}}
        for m in get_monitors():

            hardware_info["MONITORS"][m.name] = {
                "WIDTH": m.width,
                "HEIGHT": m.height,
                "PRIM": m.is_primary
            }

            if m.is_primary:

                hardware_info["MONITORS"]["PRIMARY"] = hardware_info["MONITORS"][m.name]

        self.hardware_info = hardware_info


# Still look into shared memory between viosual input and visual processor, but as or right now just have the router / process in the visual input loop
def main():

    pierre_client = Pierre()
    print(pierre_client.hardware_info)
    mouse_handler(pierre_client)


if __name__ == '__main__':

    main()
