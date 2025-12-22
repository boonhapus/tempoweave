from urllib.parse import urlparse
import logging

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from tempoweave.types import SpotifyIDT, SpotifyURIT, SpotifyURLT

logger = logging.getLogger(__name__)


class Spotify(spotipy.Spotify):
    """Fetches information about Songs from Spotify."""

    @staticmethod
    def get_spotify_id(identity: SpotifyURIT | SpotifyURLT | SpotifyIDT) -> SpotifyIDT:
        """Extract track or playlist ID from Spotify URI or URL."""
        if identity.startswith("spotify:"):
            *_, resource_id = identity.rpartition(":")
        elif "open.spotify.com" in identity:
            parsed = urlparse(identity)
            resource_id = parsed.path.split('/')[-1].split('?')[0]
        else:
            resource_id = identity

        return resource_id

    # def get_songs_from_playlist(self, playlist_identity: SpotifyURIT | SpotifyURLT | SpotifyIDT) -> list[schema.Song]:
    #     """Fetch all songs from a playlist."""
    #     playlist_id = self.get_spotify_id(playlist_identity)
    #     playlist = self.spotify.playlist(playlist_id)

    #     if playlist is None:
    #         raise RuntimeError(f"Could not find a Playlist for '{playlist_identity}'")

    #     songs: list[schema.Song] = []

    #     for playlist_item in playlist["tracks"]["items"]:
    #         if track_id := playlist_item["track"]["id"]:
    #             songs.append(self.get_song(track_id))

    #     return songs

    # def get_similar_songs(
    #     self,
    #     song: schema.Song,
    #     limit: int = 20,
    #     target_tempo: int | None = None,
    #     min_tempo: int | None = None,
    #     max_tempo: int | None = None,
    # ) -> list[schema.Song]:
    #     """Fetch similar songs based on a seed song."""
    #     SPOTIFY_MAX_PAGE_SIZE = 100

    #     params = {
    #         'seed_tracks': [song.track_id],
    #         'limit': min(limit, SPOTIFY_MAX_PAGE_SIZE),
    #     }

    #     if target_tempo is not None:
    #         params['target_tempo'] = target_tempo

    #     if min_tempo is not None:
    #         params['min_tempo'] = min_tempo

    #     if max_tempo is not None:
    #         params['max_tempo'] = max_tempo

    #     results = self.spotify.recommendations(**params)

    #     similar_songs: list[schema.Song] = []

    #     for track in results['tracks']:
    #         similar_songs.append(
    #             schema.Song(
    #                 track_id=track["id"],
    #                 title=track["name"],
    #                 artist=track["artists"][0]["name"],
    #                 album=track["album"]["name"],
    #                 tempo=estimate_tempo_from_ytdl(track),
    #                 duration=track["duration_ms"] / ONE_MINUTE_IN_MILLISECONDS,
    #             )
    #         )

    #     return similar_songs
