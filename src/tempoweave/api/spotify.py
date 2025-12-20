from urllib.parse import urlparse
import functools as ft
import logging

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from tempoweave.const import ONE_MINUTE_IN_MILLISECONDS
from tempoweave.types import SpotifyIDT, SpotifyURIT, SpotifyURLT
from tempoweave.schema import Song
from tempoweave.audio.analysis import estimate_tempo_from_yt

logger = logging.getLogger(__name__)


class SpotifyAPIClient:
    """Fetches information about Songs from Spotify."""

    def __init__(self, spotify_auth: SpotifyClientCredentials):
        self.spotify = spotipy.Spotify(client_credentials_manager=spotify_auth)

    @staticmethod
    def get_spotify_id(song_identity: SpotifyURIT | SpotifyURLT | SpotifyIDT) -> SpotifyIDT:
        """Extract track or playlist ID from Spotify URI or URL."""
        if song_identity.startswith("spotify:"):
            *_, resource_id = song_identity.rpartition(":")
        elif "open.spotify.com" in song_identity:
            parsed = urlparse(song_identity)
            resource_id = parsed.path.split('/')[-1].split('?')[0]
        else:
            resource_id = song_identity

        return resource_id

    def is_song_on_spotify(self, song: Song) -> bool:
        """Determine if a song still exists on Spotify."""
        try:
            self.spotify.track(song.track_id)
        except Exception:
            return False
        else:
            return True 

    @ft.cache
    def get_song(self, song_identity: SpotifyURIT | SpotifyURLT | SpotifyIDT) -> Song:
        """Fetch a song."""
        track_id = self.get_spotify_id(song_identity)
        track = self.spotify.track(track_id)

        if track is None:
            raise RuntimeError(f"Could not find a Song for '{song_identity}'")

        song = Song(
            track_id=track["id"],
            title=track["name"],
            artist=track["artists"][0]["name"],
            album=track["album"]["name"],
            tempo=estimate_tempo_from_yt(track),
            duration=track["duration_ms"] / ONE_MINUTE_IN_MILLISECONDS,
        )

        return song

    def get_songs_from_playlist(self, playlist_identity: SpotifyURIT | SpotifyURLT | SpotifyIDT) -> list[Song]:
        """Fetch all songs from a playlist."""
        playlist_id = self.get_spotify_id(playlist_identity)
        playlist = self.spotify.playlist(playlist_id)

        if playlist is None:
            raise RuntimeError(f"Could not find a Song for '{playlist_identity}'")

        songs: list[Song] = []

        for playlist_item in playlist["tracks"]["items"]:
            track_id = playlist_item["track"]["id"]
            if track_id:
                songs.append(self.get_song(track_id))

        return songs

    def get_similar_songs(
        self,
        song: Song,
        limit: int = 20,
        target_tempo: int | None = None,
        min_tempo: int | None = None,
        max_tempo: int | None = None,
    ) -> list[Song]:
        """Fetch similar songs based on a seed song."""
        SPOTIFY_MAX_PAGE_SIZE = 100

        params = {
            'seed_tracks': [song.track_id],
            'limit': min(limit, SPOTIFY_MAX_PAGE_SIZE),
        }

        if target_tempo is not None:
            params['target_tempo'] = target_tempo

        if min_tempo is not None:
            params['min_tempo'] = min_tempo

        if max_tempo is not None:
            params['max_tempo'] = max_tempo

        results = self.spotify.recommendations(**params)

        similar_songs: list[Song] = []

        for track in results['tracks']:
            similar_songs.append(
                Song(
                    track_id=track["id"],
                    title=track["name"],
                    artist=track["artists"][0]["name"],
                    album=track["album"]["name"],
                    tempo=estimate_tempo_from_yt(track),
                    duration=track["duration_ms"] / ONE_MINUTE_IN_MILLISECONDS,
                )
            )

        return similar_songs
