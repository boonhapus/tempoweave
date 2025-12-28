from typing import Any, Literal
import logging

import httpx

from tempoweave import __project__, api

logger = logging.getLogger(__name__)


type MusicBrainzEntityT = Literal[
    "annotation", "area", "artist", "cdstub", "event", "instrument", "label", "place", "recording", "release",
    "release-group", "series", "tag", "work", "url",
]


def _build_lucene_query(params: dict) -> str:
    """
    Build a Lucene query string from a dictionary of parameters.
    
    Supports:
        - Basic key:value pairs
        - Negation with "-" prefix (e.g., {"-status": "inactive"})
        - Lists for OR logic (e.g., {"status": ["active", "pending"]})
        - Range queries (e.g., {"price": {"gte": 10, "lte": 100}})
        - Exclusive ranges with "gt"/"lt" use curly braces
    """
    
    def escape_value(value: str) -> str:
        """Escape special Lucene characters and quote if necessary."""
        special_chars = r'+-&|!(){}[]^"~*?:\/'
        needs_quoting = " " in value or any(c in value for c in special_chars)
        if needs_quoting:
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value

    def format_value(value) -> str:
        """Format a single value for Lucene query."""
        match value:
            case str():
                return escape_value(value)
            case bool():
                return str(value).lower()
            case int() | float():
                return str(value)
            case None:
                return "null"
            case _:
                return escape_value(str(value))

    def format_list(values: list) -> str:
        """Format a list as OR query."""
        if not values:
            return ""
        formatted = " OR ".join(format_value(v) for v in values)
        return f"({formatted})"

    def format_range(range_dict: dict) -> str:
        """Format a range query with proper bracket types."""
        low = range_dict.get("gte") or range_dict.get("gt") or "*"
        high = range_dict.get("lte") or range_dict.get("lt") or "*"
        
        # Use [ ] for inclusive, { } for exclusive
        left_bracket = "{" if "gt" in range_dict and "gte" not in range_dict else "["
        right_bracket = "}" if "lt" in range_dict and "lte" not in range_dict else "]"
        
        return f"{left_bracket}{low} TO {high}{right_bracket}"

    def is_range_dict(d: dict) -> bool:
        """Check if dict represents a range query."""
        range_keys = {"gt", "gte", "lt", "lte"}
        return bool(d) and all(k in range_keys for k in d)

    query_parts = []
    
    for key, value in params.items():
        if value is None or (isinstance(value, list) and not value):
            continue
            
        prefix, field = ("-", key[1:]) if key.startswith("-") else ("", key)
        
        match value:
            case list():
                formatted = format_list(value)
            case dict() if is_range_dict(value):
                formatted = format_range(value)
            case dict():
                # Nested dict that isn't a range - skip or raise
                continue
            case _:
                formatted = format_value(value)
        
        operator = "NOT " if prefix else ""
        query_parts.append(f"{operator}{field}:{formatted}")

    return " AND ".join(query_parts)


class MusicBrainz(httpx.Client):
    """
    Fetches information about Songs from MusicBrainz.
    
    Further reading:
      https://wiki.musicbrainz.org/MusicBrainz_API
      https://wiki.musicbrainz.org/MusicBrainz_API/Rate_Limiting
    """

    def __init__(self):
        super().__init__(
            transport=api.RetryRateLimitTransport(requests_per_second=0.8),
            base_url="http://musicbrainz.org",
            headers={
                "User-Agent": f"{__project__.__name__}/{__project__.__version__} (+github/boonhapus/tempoweave)",
                "Accept": "application/json",
            }
        )
    
    def search(
        self,
        type: MusicBrainzEntityT = "recording",
        limit: int | None = None,
        offset: int | None = None,
        **lucene_query_items,
    ) -> httpx.Response:
        """
        The query field supports the full Lucene Search syntax.

        Further reading:
          https://lucene.apache.org/core/7_7_2/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description
        """
        p = {"query": _build_lucene_query(params=lucene_query_items)}

        if limit is not None:
            p["limit"] = limit

        if offset is not None:
            p["offset"] = offset

        r = self.get(url=f"/ws/2/{type}", params=p)

        return r

    def get_musicbrainz_id(self, track_info: dict[str, Any]) -> str | None:
        """Attempts to find a MusicBrainz ID using a tiered fallback system."""
        mbid: str | None = None

        spotify_title = track_info["name"]
        spotify_artist = track_info["artists"][0]["name"]

        # 1. High Precision: ISRC (Global Standard)
        if mbid is None and track_info["external_ids"].get("isrc", None):
            r = self.search(type="recording", limit=1, isrc=track_info['external_ids']['isrc'])
            d = r.json()

            try:
                mbid = d["recordings"][0]["id"]

            # TRACK MISSING KEY DATA
            except (IndexError, KeyError):
                logger.warning(f"Could not fetch MBID based on ISRC for '{spotify_title}' [{spotify_artist}]")

        # 2. Fallback: Metadata Search
        if mbid is None:
            r = self.search(type="recording", limit=1, title=spotify_title, artist=spotify_artist)
            d = r.json()

            try:
                mbid = d["recordings"][0]["id"]

            # TRACK MISSING KEY DATA
            except (KeyError, IndexError):
                logger.warning(f"Could not fetch MBID based on Query for '{spotify_title}' [{spotify_artist}]")

        return mbid