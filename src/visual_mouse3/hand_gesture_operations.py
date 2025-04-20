from typing import List, Tuple
import math

import pyautogui
from spotipy.exceptions import SpotifyException


def move_visual_mouse(x_coor, y_coor):

    return


def click_visual_mouse(x_coor, y_coor):
                       
    return


def normalize_visual_mouse_input(x_coor: int, y_coor: int) -> Tuple[int, int]:
    """normalizes input to fit in smaller window than default camera size"""

    X_COOR_NORMALIZATION_MIN = 0.20
    X_COOR_NORMALIZATION_MAX = 0.80

    Y_COOR_NORMALIZATION_MIN = 0.1
    Y_COOR_NORMALIZATION_MAX = 0.45

    # Min-Max feature scaling
    # normalized_x_coor = ((x_coor - X_COOR_NORMALIZATION_MIN)) / (X_COOR_NORMALIZATION_MAX - X_COOR_NORMALIZATION_MIN)
    # normalized_y_coor = ((y_coor - Y_COOR_NORMALIZATION_MIN)) / (Y_COOR_NORMALIZATION_MAX - Y_COOR_NORMALIZATION_MIN)

    normalized_x_coor = ((x_coor - X_COOR_NORMALIZATION_MIN) / (X_COOR_NORMALIZATION_MAX - X_COOR_NORMALIZATION_MIN))
    normalized_y_coor = ((y_coor - Y_COOR_NORMALIZATION_MIN) / (Y_COOR_NORMALIZATION_MAX - Y_COOR_NORMALIZATION_MIN))

    return (normalized_x_coor, normalized_y_coor)


# def is_micro_movement(current_hand_data, historical_hand_data):

#     if len(historical_hand_data) < 2:

#         return False

#     last_x_coor = historical_hand_data[-2]["INDEX_TIP"].x
#     last_y_coor = historical_hand_data[-2]["INDEX_TIP"].y

#     current_x_coor = current_hand_data["INDEX_TIP"].x
#     current_y_coor = current_hand_data["INDEX_TIP"].y

#     # May break it out into more statements or change to or
#     # Cuz if moving in straight line along x axis then y axis wont change and will be with the range
#     # Of micromovements but also this current solution could reduce sporatic y movement in that case
#     if ((last_x_coor < current_x_coor * 0.9955) or (last_x_coor > current_x_coor * 1.0045) and
#         (last_y_coor < current_y_coor * 0.9955) or (last_y_coor > current_y_coor * 1.0045)):

#         return False

#     return True


def get_volume_percent(pierre_client):

    index_tip_loc_x = pierre_client.hand_data_stack["LEFT"]["DATA"][-1]["INDEX_TIP"].x
    index_tip_loc_y = pierre_client.hand_data_stack["LEFT"]["DATA"][-1]["INDEX_TIP"].y

    thumb_tip_loc_x = pierre_client.hand_data_stack["LEFT"]["DATA"][-1]["THUMB_TIP"].x
    thumb_tip_loc_y = pierre_client.hand_data_stack["LEFT"]["DATA"][-1]["THUMB_TIP"].y

    # Raise the result because fingers arent long enough to max volume go past like 40 when full extended
    return int(int(math.sqrt((index_tip_loc_x-thumb_tip_loc_x)**2 + (index_tip_loc_y-thumb_tip_loc_y)**2) * 100) ** 1.4)



def router(pierre_client, cursor_window):

    left_gesture_stack = pierre_client.hand_data_stack["LEFT"]["GESTURE"]
    right_gesture_stack = pierre_client.hand_data_stack["RIGHT"]["GESTURE"]


    # if (left_gesture_stack[-5:] == ["ROCK"]*5 and left_gesture_stack[-6] != "ROCK") or (right_gesture_stack[-5:] == ["ROCK"]*5 and right_gesture_stack[-6] != "ROCK"):

    #     print("ACTIVATE SPOTIFY")


    # Pause song
    if (left_gesture_stack[-5:] == ["CLOSED"]*5): # or (right_gesture_stack[-5:] == ["CLOSED"]*5):

        if pierre_client.spotify_metadata["isPause"] is False:

            try:

                pierre_client.spotify_client.pause_playback(
                    device_id=pierre_client.spotify_device,
                )

            except SpotifyException as e:

                return

            pierre_client.spotify_metadata["isPause"] = True
            pierre_client.spotify_metadata["isPlaying"] = False

        return

    # Play Song
    if (left_gesture_stack[-5:] == ["OPEN"]*5): # or (right_gesture_stack[-5:] == ["OPEN"]*5):

        # When URI passed, will restart, if no URI will resume from last paused place

        if pierre_client.spotify_metadata["isPlaying"] is False:

            pierre_client.spotify_client.start_playback(
                device_id=pierre_client.spotify_device, 
                # uris=['spotify:track:6gdLoMygLsgktydTQ71b15']
            )

            pierre_client.spotify_metadata["isPlaying"] = True
            pierre_client.spotify_metadata["isPause"] = False

        return


    if (left_gesture_stack[-5:] == ["COYOTE"]*5 and left_gesture_stack[-6] != "COYOTE"): # or (right_gesture_stack[-5:] == ["COYOTE"]*5 and right_gesture_stack[-6] != "COYOTE"):

        # if pierre_client.spotify_metadata["isPlaying"] in [True, False] or :

        pierre_client.spotify_client.next_track(
            device_id=pierre_client.spotify_device,
        )

        pierre_client.spotify_metadata["isPlaying"] = True
        pierre_client.spotify_metadata["isPause"] = False

        return
    

    # Adjust Spotify Volume
    if (left_gesture_stack[-5:] == ["SQUEEZE"]*5):

        volume = get_volume_percent(pierre_client)

        print("SET VOL: ", volume)

        if (volume < 0) or (volume > 100):

            return

        pierre_client.spotify_client.volume(
            volume_percent=volume,
            device_id=pierre_client.spotify_device,
        )


    if (right_gesture_stack[-2:] == ["FINGER_POINTING_CLICK"]*2) or (right_gesture_stack[-2:] == ["FINGER_POINTING"]*2):

        finger_tip_x_loc = pierre_client.hand_data_stack["RIGHT"]["DATA"][-1]["INDEX_TIP"].x
        finger_tip_y_loc = pierre_client.hand_data_stack["RIGHT"]["DATA"][-1]["INDEX_TIP"].y


        # print("\n\n\n\n\nDATA", pierre_client.hand_data_stack["RIGHT"]["DATA"])
        # print("SHOULD BE MOVING: ", finger_tip_x_loc, finger_tip_y_loc)

        primary_monitor = pierre_client.hardware_info["MONITORS"]["PRIMARY"]

        print(finger_tip_x_loc, finger_tip_y_loc)

        x_coor, y_coor = normalize_visual_mouse_input(finger_tip_x_loc, finger_tip_y_loc)

        print(x_coor, y_coor, "\n\n\n")


        if right_gesture_stack[-1] == "FINGER_POINTING":

            cursor_window.move(
                int(primary_monitor["WIDTH"]*x_coor), 
                int(primary_monitor["HEIGHT"]*y_coor)
            )

        if right_gesture_stack[-1] == "FINGER_POINTING_CLICK":

            pyautogui.click(
                int(primary_monitor["WIDTH"]*x_coor), 
                int(primary_monitor["HEIGHT"]*y_coor)
            )
