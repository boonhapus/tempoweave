"""Domain models for Tempoweave."""

import datetime as dt
import math
from typing import Any, Literal

import pydantic

from tempoweave.types import SpotifyIDT


class Base(pydantic.BaseModel):

    model_config = pydantic.ConfigDict(
        from_attributes=True,
    )

    def model_dump_no_extras(self) -> dict[str, Any]:
        """Return a dictionary of the model's fields, excluding any extras."""
        return {k: v for k, v in self.model_dump().items() if k in self.model_fields.keys()}


class SpotifyAuthInfo(Base):
    """Represents the information about a Spotify session."""

    access_token: pydantic.SecretStr
    token_type: str
    expires_in: int
    refresh_token: pydantic.SecretStr | None
    scope: str
    expires_at: int

    @property
    def scopes(self) -> list[str]:
        """Return the auth scope as a list of scopes."""
        return self.scope.split(" ")

    @property
    def expires_when(self) -> dt.datetime:
        """Return the .expires_at as a datetime."""
        return dt.datetime.fromtimestamp(self.expires_at)


class Song(Base):
    """Represents a song on Spotify."""

    track_id: SpotifyIDT
    """Spotify track ID."""

    title: str
    """Song title."""

    artist: str
    """Primary artist."""

    album: str
    """Album the song is featured on."""

    tempo: pydantic.PositiveInt
    """Tempo in BPM."""

    duration: pydantic.PositiveFloat
    """The track length in minutes."""

    genre: str | None = None
    """Primary genre of the song."""

    last_verified: dt.datetime = pydantic.Field(default_factory=lambda: dt.datetime.now(tz=dt.timezone.utc))
    """When this song was last verified against Spotify's API."""

    @pydantic.computed_field
    @property
    def spotify_uri(self) -> str:
        """Spotify URI of the song."""
        return f"spotify:track:{self.track_id}"
    
    # ==========
    # VALIDATORS
    # ==========

    @pydantic.field_validator("tempo", mode="before")
    @classmethod
    def validate_round_precision_to_nearest_5(cls, v: float) -> float:
        return math.floor(v / 5) * 5

    @pydantic.field_validator("duration")
    @classmethod
    def validate_limit_precision_to_one_decimal(cls, v: float) -> float:
        return round(number=v, ndigits=1)


class TempoweavePlaylistSettings(Base):
    """Represents the type of tempo playlist to build."""

    duration: pydantic.PositiveInt
    """How long the playlist should run for in minutes."""

    min_tempo: pydantic.PositiveInt
    """The minimum boundary for tempo in this playlist."""

    max_tempo: pydantic.PositiveInt
    """The maximum boundary for tempo in this playlist."""

    easing_function: Literal["linear"] = "linear"
    """The progression of tempo throughout the playlist."""

    @pydantic.model_validator(mode="before")
    @classmethod
    def validate_parse_description_as_input(cls, v: str | dict[str, Any]) -> dict[str, Any]:
        if not isinstance(v, str):
            return v

        if ";" not in v:
            raise ValueError("This playlist does not contain a semicolon-delimited description.")

        parts = v.replace(" ", "").split(";")

        if len(parts) == 4:
            return dict(zip(("duration", "min_tempo", "max_tempo", "easing_function"), parts))
        elif len(parts) == 3:
            return dict(zip(("duration", "min_tempo", "max_tempo"), parts))
        else:
            raise ValueError("This playlist must define at least duration; min_tempo; max_tempo")

    @pydantic.field_validator("duration", mode="before")
    @classmethod
    def validate_calculate_minutes_shorthand(cls, v: str | int) -> int:
        if isinstance(v, int):
            return v

        if "m" in v:
            return int(v.replace("m", ""))

        if "h" in v:
            return int(float(v.replace("h", "")) * 60)

        assert isinstance(v, int), f"'{v}' is not a valid duration shorthand"

        return v

    @pydantic.field_validator("min_tempo", "max_tempo", mode="before")
    @classmethod
    def validate_calculate_tempo_shorthand(cls, v: str | int) -> int:
        if isinstance(v, int) or v.isnumeric():
            return int(v)

        if "bpm" in v:
            return int(v.replace("bpm", ""))

        assert isinstance(v, int), f"'{v}' is not a valid tempo shorthand"

        return v

    @pydantic.field_validator("max_tempo")
    @classmethod
    def validate_max_is_greater_than_min(cls, v: int, info: pydantic.ValidationInfo) -> int:
        if (min_tempo := info.data["min_tempo"]) > v:
            raise ValueError(f".max_tempo ({v}) must be greater than .min_tempo ({min_tempo})")
        return v
