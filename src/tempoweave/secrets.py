from typing import cast

from cryptography.fernet import Fernet
from spotipy.cache_handler import MemoryCacheHandler
from sqlalchemy.orm import Session
import sqlalchemy as sa

from tempoplay.types import SpotifyAuthInfoT
from tempoplay.schema import SpotifyAuthInfo


class GitHubActionsCacheHandler(MemoryCacheHandler):
    """Store the token in memory and in GitHub secret store."""

    def __init__(self, secret_key: str, db_engine: sa.engine.Engine):
        self.db_engine = db_engine
        self.token_info: SpotifyAuthInfo | None = None
        self._cipher = Fernet(key=secret_key.encode())

    def _public_token_info(self) -> SpotifyAuthInfoT:
        """Create a clear-text version of .token_info."""
        assert self.token_info is not None, "token_info is not set"
        token_info = cast(SpotifyAuthInfoT, self.token_info.model_dump())
        token_info["access_token"] = self.token_info.access_token.get_secret_value()

        if self.token_info.refresh_token is not None:
            token_info["refresh_token"] = self.token_info.refresh_token.get_secret_value()

        return token_info

    # def get_cached_token(self) -> SpotifyAuthInfoT | None:
    #     """Fetch the token from memory, falling back to secret store."""
    #     if self.token_info is not None:
    #         return self._public_token_info()

    #     with Session(bind=self.db_engine) as sess:
    #         q = """SELECT * FROM auth_tokens ORDER BY expires_at DESC LIMIT 1"""

    #         if not (r := sess.execute(sa.text(q))):
    #             return None

    #     d = r.scalar().asdict()
    #     d["access_token"] = self._cipher.decrypt(d.access_token)
    #     d["refresh_token"] = self._cipher.decrypt(d.refresh_token)

    #     self.token_info = SpotifyAuthInfo.model_validate(r)

    #     return self._public_token_info()

    # def save_token_to_cache(self, token: SpotifyAuthInfoT) -> None:
    #     """Store the token in memory and secret store."""
    #     self.token_info = SpotifyAuthInfo.model_validate(token)

    #     if extras := self.token_info.__pydantic_extra__:
    #         logger.warning(f"Extra data found on token: {extras}")

    #     d = self._public_token_info()
    #     d["access_token"] = self._cipher.encrypt(d["access_token"]).decode()
    #     d["refresh_token"] = self._cipher.encrypt(d["refresh_token"]).decode()

    #     with Session(bind=self.db_engine) as sess:
    #         q = """INSERT INTO auth_tokens"""
    #         r = sess.execute(sa.text(q))
