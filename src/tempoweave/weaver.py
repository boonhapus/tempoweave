from typing import cast
import datetime as dt
import logging

from advanced_alchemy.config import SQLAlchemySyncConfig
from spotipy.oauth2 import SpotifyOAuth
import sqlalchemy as sa

from tempoweave import api, const, models, repo, schema, types

logger = logging.getLogger(__name__)


class Weaver:
    """A coordinator of songs."""

    def __init__(
        self,
        spotify_auth: SpotifyOAuth,
        last_fm_auth: dict[str, str],
        browser: types.BrowserT,
        database_fp: str = ".tempoweave_song_cache.db",
    ):
        self.db_config = SQLAlchemySyncConfig(connection_string=f"sqlite:///{database_fp}")
        self.spotify = api.Spotify(auth_manager=spotify_auth)
        self.last_fm = api.LastFM(**last_fm_auth)
        self.mbrainz = api.MusicBrainz()
        self.youtube = api.YouTube(browser_cookie_for_age_verify=browser)

        with self.db_config.get_engine().begin() as conn:
            models.Base.metadata.create_all(bind=conn)

    def get_song(self, spotify_track_identity: types.SpotifyIdentityT) -> schema.Song:
        """Get a song."""
        track_id = self.spotify.get_spotify_id(spotify_track_identity)

        with self.db_config.get_session() as sess:
            song_repo = repo.SongRepository(session=sess)

            q = (
                sa
                .select(models.Song)
                .where(
                    models.Song.track_id == track_id,
                    models.Song.last_verified > (dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=30)),
                    models.Song.musicbrainz_id.is_not(None),
                    models.Song.tempo.is_not(None),
                )
            )

            if cached := song_repo.get_one_or_none(statement=q):
                return cached.to_schema()

            if (track := self.spotify.track(track_id)) is None:
                raise RuntimeError(f"Could not find a Song on Spotify for '{spotify_track_identity}'")

            song = models.Song.validate_schema({
                "track_id": track["id"],
                "musicbrainz_id": self.mbrainz.get_musicbrainz_id(track),
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "tempo": self.youtube.estimate_tempo(track),
                "duration": track["duration_ms"] / const.ONE_MINUTE_IN_MILLISECONDS,
            })

            song_repo.upsert(data=song, auto_commit=True)

        return cast(typ=schema.Song, val=song.to_schema())

    def get_recommendations(self, song: schema.Song, *, limit: int = 5) -> list[schema.Song]:
        """Get similar songs to the given song."""
        recommendations: list[schema.Song] = []

        for similar in self.last_fm.get_similar_tracks(song, limit=limit):
            query = f"track:{similar['title']} artist:{similar['artist']}"

            if data := self.spotify.search(q=query, limit=1, type="track"):
                recommendations.append(self.get_song(spotify_track_identity=data["tracks"]["items"][0]["uri"]))
            else:
                logger.warning(f"Could not find a Song on Spotify for '{query}'")

        return recommendations

    def get_playlist(self, spotify_playlist_identity: types.SpotifyIdentityT) -> schema.Playlist:
        """Fetch all info from a playlist."""
        playlist_id = self.spotify.get_spotify_id(spotify_playlist_identity)
        playlist_info = self.spotify.playlist(playlist_id)

        if playlist_info is None:
            raise RuntimeError(f"Could not find a Playlist for '{spotify_playlist_identity}'")

        playlist = schema.Playlist(
            playlist_id=playlist_info["id"],
            title=playlist_info["name"],
            description=playlist_info["description"],
            songs=[
                schema.PlaylistSong.model_validate(
                    {
                        **self.get_song(spotify_track_identity=t["track"]["id"]).model_dump_no_extras(),
                        "order": idx,
                        "added_at": t["added_at"],
                    },
                )
                for idx, t in enumerate(playlist_info["tracks"]["items"], start=1)
            ],
        )

        return playlist

    def set_playlist(self, spotify_playlist_identity: types.SpotifyIdentityT, *, songs: list[schema.Song]) -> schema.Playlist:
        """Define all the songs in this playlist."""
        playlist_id = self.spotify.get_spotify_id(spotify_playlist_identity)
        playlist_info = self.spotify.playlist(playlist_id)

        if playlist_info is None:
            raise RuntimeError(f"Could not find a Playlist for '{spotify_playlist_identity}'")

        self.spotify.playlist_replace_items(playlist_id=playlist_id, items=[s.spotify_uri for s in songs])

        playlist = schema.Playlist(
            playlist_id=playlist_info["id"],
            title=playlist_info["name"],
            description=playlist_info["description"],
            songs=[
                schema.PlaylistSong.model_validate(
                    {
                        **self.get_song(spotify_track_identity=t["track"]["id"]).model_dump_no_extras(),
                        "order": idx,
                        "added_at": t["added_at"],
                    },
                )
                for idx, t in enumerate(playlist_info["tracks"]["items"], start=1)
            ]
        )

        return playlist
