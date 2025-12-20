"""Database models for Tempoweave."""

from sqlalchemy.orm import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class AuthToken(Base):
    """Database model for storing encrypted auth tokens."""

    __tablename__ = "auth_tokens"

    id = sa.Column(sa.Integer, primary_key=True)
    access_token = sa.Column(sa.String, nullable=False)
    token_type = sa.Column(sa.String)
    expires_in = sa.Column(sa.Integer)
    refresh_token = sa.Column(sa.String)
    scope = sa.Column(sa.String)
    expires_at = sa.Column(sa.Integer, index=True)

    def to_dict(self) -> dict[str, str | int | None]:
        """Convert the model to a dictionary."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "expires_at": self.expires_at,
        }
