from advanced_alchemy.repository import SQLAlchemySyncRepository

from tempoweave import models


class SongRepository(SQLAlchemySyncRepository[models.Song]):
    model_type = models.Song
    id_attribute = "track_id"
