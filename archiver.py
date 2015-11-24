# __author__ = 'aeggum'

import spotify
import threading
import time

TODAY = time.strftime('%Y-%m-%d')
ARCHIVE_NAME = 'Archive'
DISCOVER_WEEKLY = ('Discover Weekly - %s', 'spotify:user:spotifydiscover:playlist:4iiVaeYEm437YkXGAlzOxV')
DISCOVER_WEEKLY_JUSTIN = ('Discover Weekly - Justin - %s', 'spotify:user:spotifydiscover:playlist:6FIYj459RfUKIDpk3vtFqN')
NEW_MUSIC_FRIDAY = ('New Music Friday - %s', 'spotify:user:spotify:playlist:1yHZ5C3penaxRdWR7LRIOb')

PLAYLISTS = [DISCOVER_WEEKLY, DISCOVER_WEEKLY_JUSTIN, NEW_MUSIC_FRIDAY]

def login(session, username, password):
    logged_in_event = threading.Event()

    def connection_state_listener(session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            logged_in_event.set()

    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, connection_state_listener)
    session.login(username, password)

    if not logged_in_event.wait(10):
        raise RuntimeError('Login timed out')

def logout(session):
    logged_out_event = threading.Event()

    def logged_out_listener(session):
        logged_out_event.set()

    session.on(spotify.SessionEvent.LOGGED_OUT, logged_out_listener)
    session.logout()

    if not logged_out_event.wait(10):
        raise RuntimeError('Logout timed out')

session = spotify.Session()
loop = spotify.EventLoop(session)
loop.start()

login(session, 'aeggum', 'foobar')

container = session.playlist_container
if not container.is_loaded:
    container.load()

archive_folder_idx = next((idx for idx, x in enumerate(container) if type(x) == spotify.PlaylistFolder and x.name == ARCHIVE_NAME), -1)

if archive_folder_idx == -1:
    container.add_folder(ARCHIVE_NAME, 0)
    archive_folder_idx = 0

for playlist_tuple in PLAYLISTS:
    playlist = session.get_playlist(playlist_tuple[1])
    playlist.load()

    copy_playlist = container.add_new_playlist(playlist_tuple[0] % TODAY, archive_folder_idx + 1)
    copy_playlist.add_tracks(playlist.tracks)

time.sleep(3)  # Perhaps not necessary (?), but would rather wait a little extra than something not work here due to impatience

logout(session)
