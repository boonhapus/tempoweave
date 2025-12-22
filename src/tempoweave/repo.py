from advanced_alchemy.repository import SQLAlchemySyncRepository

from tempoweave import models


class SongRepository(SQLAlchemySyncRepository[models.Song]):
    model_type = models.Song


class SpotifyAuthRepository(SQLAlchemySyncRepository[models.SpotifyAuthInfo]):
    model_type = models.SpotifyAuthInfo