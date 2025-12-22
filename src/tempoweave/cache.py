"""Cache handler for Spotify authentication tokens."""

import logging
from typing import cast

from cryptography.fernet import Fernet
from spotipy.cache_handler import MemoryCacheHandler
from sqlalchemy.orm import Session
import sqlalchemy as sa

from tempoweave.types import SpotifyAuthInfoT
from tempoweave import models, schema

logger = logging.getLogger(__name__)


class GitHubActionsCacheHandler(MemoryCacheHandler):
    """Store the token in memory and in a database with encryption."""

    def __init__(self, secret_key: str, db_engine: sa.engine.Engine):
        super().__init__()
        self.db_engine = db_engine
        self.token_info: schema.SpotifyAuthInfo | None = None
        self._cipher = Fernet(key=secret_key.encode())

        models.Base.metadata.create_all(self.db_engine)

    def _public_token_info(self) -> SpotifyAuthInfoT:
        """Create a clear-text version of .token_info."""
        assert self.token_info is not None, "token_info is not set"
        token_info = cast(SpotifyAuthInfoT, self.token_info.model_dump())

        token_info["access_token"] = self.token_info.access_token.get_secret_value()
        if self.token_info.refresh_token:
            token_info["refresh_token"] = self.token_info.refresh_token.get_secret_value()

        return token_info

    def get_cached_token(self) -> SpotifyAuthInfoT | None:
        """Fetch the token from memory, falling back to the database."""
        if self.token_info is not None:
            return self._public_token_info()

        try:
            with Session(bind=self.db_engine) as sess:
                q = sa.select(models.SpotifyAuthInfo).order_by(models.SpotifyAuthInfo.expires_at.desc())
                db_token = sess.execute(q).scalars().first()

                if not db_token:
                    logger.info("No token found in database.")
                    return None

                token_data = db_token.to_dict()
                token_data["access_token"] = self._cipher.decrypt(
                    token_data["access_token"].encode()
                ).decode()

                if token_data["refresh_token"]:
                    token_data["refresh_token"] = self._cipher.decrypt(
                        token_data["refresh_token"].encode()
                    ).decode()

                self.token_info = schema.SpotifyAuthInfo.model_validate(token_data)
                logger.info("Loaded token from database.")
                return self._public_token_info()

        except Exception as e:
            logger.error(f"Error reading from token database: {e}")
            return None

    def save_token_to_cache(self, token: SpotifyAuthInfoT) -> None:
        """Store the token in memory and in the database."""
        self.token_info = schema.SpotifyAuthInfo.model_validate(token)

        if extras := self.token_info.__pydantic_extra__:
            logger.warning(f"Extra data found on token: {extras}")

        try:
            db_data = token.copy()
            db_data["access_token"] = self._cipher.encrypt(
                db_data["access_token"].encode()
            ).decode()

            if db_data["refresh_token"]:
                db_data["refresh_token"] = self._cipher.encrypt(
                    db_data["refresh_token"].encode()
                ).decode()

            with Session(bind=self.db_engine) as sess:
                new_token = models.SpotifyAuthInfo(**db_data)
                sess.add(new_token)
                sess.commit()
                logger.info("Saved new token to database.")

        except Exception as e:
            logger.error(f"Error saving token to database: {e}")
