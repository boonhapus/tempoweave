from typing import Any

from urllib.parse import urlparse
import functools as ft
import logging
import pathlib
import tempfile

from spotipy.oauth2 import SpotifyClientCredentials
import librosa
import numpy as np
import spotipy
import yt_dlp

from tempoplay.const import ONE_MINUTE_IN_MILLISECONDS
from tempoplay.types import SpotifyIDT, SpotifyURIT, SpotifyURLT
from tempoplay.schema import Song

logger = logging.getLogger(__name__)


class SongFetcher:
    """Fetches information about Songs."""

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

    def estimate_tempo_from_yt(self, track_info: dict[str, Any], quiet: bool = False) -> int:
        """Download the song from YT and estimate its tempo."""
        try:
            temp_dir = tempfile.gettempdir()
            temp_mp3 = pathlib.Path(f"{temp_dir}/{track_info['id']}.mp3")

            ydl_opts = {
                "default_search": "ytsearch1:",
                "outtmpl": temp_mp3.as_posix().replace(".mp3", ".%(ext)s"),
                # choco install ffmpeg || pass the path to ffmpeg
                # 'ffmpeg_location': r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
                "quiet": quiet,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                artist = track_info["artists"][0]["name"]
                title  = track_info["name"]
                ydl.download([f"{artist} {title}"])

            # POST-PROCESS FOR TEMPO USING librosa.
            song_data, sampling_rate = librosa.load(path=temp_mp3)
            tempo, _ = librosa.beat.beat_track(y=song_data, sr=sampling_rate)
            tempo = tempo.item() if isinstance(tempo, np.ndarray) else tempo
            return int(tempo)

        except Exception as e:
            logger.exception(f"{e}")
            return 0

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
            tempo=self.estimate_tempo_from_yt(track),
            duration=track["duration_ms"] / ONE_MINUTE_IN_MILLISECONDS,
            # genre="",
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
            songs.append(self.get_song(track_id))

        return songs
