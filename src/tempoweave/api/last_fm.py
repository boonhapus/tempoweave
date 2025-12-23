from typing import Any
import logging

import pylast

from tempoweave import schema

logger = logging.getLogger(__name__)


class LastFM(pylast.LastFMNetwork):
    """Fetches information about Songs from LastFM."""
    # DEV NOTE:
    #   LastFM implements object-based API requests, instead of having a central API
    #   coordinator. Instead, every object inherits from a private _Network object and
    #   we pass around the LastFMNetwork.
    #

    def get_similar_tracks(self, song: schema.Song, limit: int = 5) -> list[dict[str, Any]]:
        """..."""
        results = []

        try:
            track = self.get_track(artist=song.artist, title=song.title)

            for similar in track.get_similar(limit=limit):
                if isinstance(similar.item, pylast.Track):
                    results.append({
                        "title": similar.item.get_title(),
                        "artist": similar.item.get_artist(),
                        "album": similar.item.get_album(),
                    })
            
            if not results:
                logger.warning(f"No similar tracks found on LastFM to '{song.title}' [{song.artist}]")

        except pylast.WSError as e:
            # Handle API errors (e.g., Track not found on Last.fm)
            logger.error(f"Last.fm Error: {e}")

        except Exception as e:
            logger.error(f"Unexpected Last.fm error: {e}")
        
        return results
