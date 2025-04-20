import os
from dotenv import load_dotenv
from typing import Dict

import spotipy


def setup_auth(client_id: str, client_secret: str, redirect_uri: str, scope: str) -> Dict[str, str]:
    """For first time use of api when no refresh token is present"""

    # Create OAuth Object
    oauth_object = spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )

    # Create token
    token_dict = oauth_object.get_access_token()
    
    return token_dict


def create_spotify_client():

    load_dotenv()

    scope = "user-read-playback-state,user-modify-playback-state"

    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    redirect_uri = os.getenv('redirect_uri')

    access_token = setup_auth(
        client_id, 
        client_secret, 
        redirect_uri, 
        scope
    )

    client = spotipy.Spotify(auth=access_token['access_token'])

    return client
