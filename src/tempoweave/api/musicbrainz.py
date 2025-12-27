from typing import Any
import logging

import httpx
import musicbrainzngs

from tempoweave import __project__

logger = logging.getLogger(__name__)


class MusicBrainz(httpx.Client):
    """Fetches information about Songs from MusicBrainz."""

    def __init__(self):
        super().__init__()

        # INIT musicbrainz as well.
        musicbrainzngs.set_rate_limit(limit_or_interval=1.0, new_requests=1)
        musicbrainzngs.set_useragent(
            app=__project__.__name__,
            version=__project__.__version__,
            contact="github:boonhapus@tempoweave",
        )
    
    # @retry
    def _get_recordings_by_isrc(self, **options) -> dict[str, Any]:
        return musicbrainzngs.get_recordings_by_isrc(**options)

    # @retry
    def _get_recordings_by_query(self, **options) -> dict[str, Any]:
        return musicbrainzngs.search_recordings(**options)

    def get_musicbrainz_id(self, track_info: dict[str, Any]) -> str | None:
        """Attempts to find a MusicBrainz ID using a tiered fallback system."""
        mbid: str | None = None

        info = {
            "title": track_info["name"],
            "artist": track_info["artists"][0]["name"],
        }

        # 1. High Precision: ISRC (Global Standard)
        if mbid is None and track_info["external_ids"].get("isrc", None):
            try:
                d = self._get_recordings_by_isrc(isrc=track_info["external_ids"]["isrc"])
                mbid = d["isrc"]["recording-list"][0]["id"]

            # TRACK NOT FOUND
            except musicbrainzngs.musicbrainz.ResponseError:
                logger.warning(f"Could not find a MBID based on ISRC for '{info['title']}' [{info['artist']}]")

            # TRACK MISSING KEY DATA
            except (IndexError, KeyError):
                logger.warning(f"Could not fetch complete MBID info for '{info['title']}' [{info['artist']}]")

        # 2. Fallback: Metadata Search
        if mbid is None:
            q = " AND ".join(f'{k}:"{v}"' for k, v in info.items())

            try:
                d = self._get_recordings_by_query(query=q, limit=1)
                mbid = d["recording-list"][0]["id"]

            # TRACK NOT FOUND
            except musicbrainzngs.musicbrainz.NetworkError:
                logger.warning(f"Could not find a MBID based on query for '{info['title']}' [{info['artist']}]")

            # TRACK MISSING KEY DATA
            except (KeyError, IndexError):
                logger.warning(f"Could not fetch complete MBID info for '{info['title']}' [{info['artist']}]")

        return mbid