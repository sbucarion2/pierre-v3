import os
from dotenv import load_dotenv
from typing import Dict

import spotipy

from spotify_utils.spotify_auth import create_spotify_client


def get_spotify_device_id(client):

    devices = client.devices()["devices"]

    for device in devices:

        if device["type"] == 'Computer':

            return device["id"]


def search_for_music(client, audio_name, audio_type):

    return


def main():

    client = create_spotify_client()

    device_id = get_spotify_device_id(client)

    client.start_playback(
        device_id=device_id, 
        uris=['spotify:track:6gdLoMygLsgktydTQ71b15']
    )
