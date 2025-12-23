"""Database models for Tempoweave."""
import datetime as dt
from typing import Any, Self

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

from tempoweave import types, schema


class SchemaMixin:
    """Mixin for pydantic.BaseModel schema conversion."""
    __schema__: type[schema.Base]

    def to_schema(self) -> schema.Base:
        """Convert model to schema."""
        return self.__schema__.model_validate(obj=self)

    @classmethod
    def validate_schema(cls, data: Any) -> Self:
        """Validate the model against its schema."""
        return cls.from_schema(obj=cls.__schema__.model_validate(obj=data))

    @classmethod
    def from_schema(cls, obj: schema.Base) -> Self:
        """Create model from schema."""
        return cls(**obj.model_dump_no_extras())


class Base(SchemaMixin, DeclarativeBase):
    """Base class for all models."""
    pass


class SpotifyAuthInfo(Base):
    """Authentication information for Spotify."""
    __tablename__ = "spotify_auth_info"
    __schema__ = schema.SpotifyAuthInfo

    access_token: Mapped[str] = mapped_column(sa.String, primary_key=True)
    token_type: Mapped[str] = mapped_column(sa.String)    
    expires_in: Mapped[int] = mapped_column(sa.Integer)
    refresh_token: Mapped[str | None] = mapped_column(sa.String)
    scope: Mapped[str] = mapped_column(sa.String)
    expires_at: Mapped[int] = mapped_column(sa.Integer)


class Song(Base):
    """A track in the Tempoweave database."""
    __tablename__ = "song"
    __schema__ = schema.Song

    track_id: Mapped[types.SpotifyIDT] = mapped_column(sa.String, primary_key=True)
    """Spotify track ID."""

    title: Mapped[str] = mapped_column(sa.String)
    """Song title."""

    artist: Mapped[str] = mapped_column(sa.String)
    """Primary artist."""

    album: Mapped[str] = mapped_column(sa.String)
    """Album the song is featured on."""

    duration: Mapped[float] = mapped_column(sa.Float)
    """The track length in minutes."""

    tempo: Mapped[int | None] = mapped_column(sa.Integer)
    """Tempo in BPM."""

    genre: Mapped[str | None] = mapped_column(sa.String)
    """Primary genre of the song."""

    last_verified: Mapped[dt.datetime] = mapped_column(sa.DateTime)
    """When the song was fetched from Spotify."""