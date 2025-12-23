from urllib.parse import urlparse

import spotipy

from tempoweave import types


class Spotify(spotipy.Spotify):
    """Fetches information about Songs from Spotify."""

    @staticmethod
    def get_spotify_id(identity: types.SpotifyIdentityT) -> types.SpotifyIDT:
        """Extract track or playlist ID from Spotify URI or URL."""
        if identity.startswith("spotify:"):
            *_, resource_id = identity.rpartition(":")
        elif "open.spotify.com" in identity:
            parsed = urlparse(identity)
            resource_id = parsed.path.split('/')[-1].split('?')[0]
        else:
            resource_id = identity

        return resource_id
