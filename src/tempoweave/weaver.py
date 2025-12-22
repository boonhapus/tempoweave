from typing import cast

from advanced_alchemy.config import SQLAlchemySyncConfig

from tempoweave import api, const, models, repo, schema, types


class Weaver:
    """A coordinator of songs."""

    def __init__(self):
        self.db_config = SQLAlchemySyncConfig(connection_string="sqlite:///.tempoweave_song_cache.db")
        self.spotify = api.Spotify(client_credentials_manager=SpotifyClientCredentials)
        self.youtube = api.YouTube()
        # self.last_fm = api.LastFM()

        with self.db_config.get_engine().begin() as conn:
            models.Base.metadata.create_all(bind=conn)
    
    def get_song(self, spotify_track_identity: types.SpotifyIdentityT) -> schema.Song:
        """Get a song."""
        track_id = self.spotify.get_spotify_id(spotify_track_identity)

        with self.db_config.get_session() as sess:
            song_repo = repo.SongRepository(session=sess)

            if cached := song_repo.get_one_or_none(track_id=track_id):
                return cached.to_schema()

            if (track := self.spotify.track(track_id)) is None:
                raise RuntimeError(f"Could not find a Song on Spotify for '{spotify_track_identity}'")

            song = models.Song.validate_schema({
                "track_id": track["id"],
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "tempo": self.youtube.estimate_tempo(track),
                "duration": track["duration_ms"] / const.ONE_MINUTE_IN_MILLISECONDS,
            })

            song_repo.add(data=song, auto_commit=True)

        return cast(typ=schema.Song, val=song.to_schema())

    def get_recommendations(self, song: schema.Song) -> list[schema.Song]:
        """Get similar songs to the given song."""
        return [song]
