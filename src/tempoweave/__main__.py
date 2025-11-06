import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    import logging
    import os

    from cryptography.fernet import Fernet
    from spotipy.oauth2 import SpotifyOAuth
    import sqlalchemy as sa

    from tempoplay.const import ONE_MINUTE_IN_MILLISECONDS
    from tempoplay.fetch import SongFetcher
    from tempoplay.types import SpotifyIDT, SpotifyURIT, SpotifyURLT, SpotifyAuthInfoT
    from tempoplay.secrets import GitHubActionsCacheHandler
    from tempoplay.schema import SpotifyAuthInfo, Song, TempoPlaylistSettings
    return (
        Fernet,
        GitHubActionsCacheHandler,
        Song,
        SongFetcher,
        SpotifyIDT,
        SpotifyOAuth,
        SpotifyURIT,
        SpotifyURLT,
        TempoPlaylistSettings,
        logging,
        os,
        sa,
    )


@app.cell
def _(logging):
    logger = logging.getLogger()
    return


@app.cell
def _(
    Any,
    Song,
    SongFetcher,
    SpotifyIDT,
    SpotifyURIT,
    SpotifyURLT,
    TempoPlaylistSettings,
):
    class TempoPlaylist:
        """Manages the Spotify playlist."""

        def __init__(self, song_fetcher: SongFetcher, spotify_playlist: SpotifyURIT | SpotifyURLT | SpotifyIDT):
            self.song_fetcher = song_fetcher
            self.info: dict[str, Any] = song_fetcher.spotify.playlist(spotify_playlist)
            self.id: SpotifyIDT = self.info["id"]
            self.settings = TempoPlaylistSettings.model_validate(self.info["description"])

        def mine_song_recommendations(self) -> list[Song]:
            """
            Build a list of songs based on past listening.

            Spotify has deprecated the /recommendations endpoint, so we need to build them.
            """
            recent_tracks = self.song_fetcher.spotify.current
    return (TempoPlaylist,)


@app.cell
def _(
    Fernet,
    GitHubActionsCacheHandler,
    SongFetcher,
    SpotifyOAuth,
    TempoPlaylist,
    os,
    sa,
):
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

    assert os.getenv("SPOTIFY_CLIENT_ID", False), "Spotify Client ID is not set."
    assert os.getenv("SPOTIFY_CLIENT_SECRET", False), "Spotify Client Secret is not set."
    assert os.getenv("ENCRYPTION_KEY", False), "Encryption key is not set."


    db_engine = sa.create_engine("sqlite://")

    song_fetcher = SongFetcher(
        spotify_auth=SpotifyOAuth(
            client_id=os.environ["SPOTIFY_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
            redirect_uri="http://127.0.0.1:9090",
            scope=[
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-private",
                "playlist-modify-public",
                "user-follow-read",
                "user-top-read",
                "user-read-recently-played",
                "user-library-read",
                "user-read-email",
                "user-read-private",
            ],
            cache_handler=GitHubActionsCacheHandler(
                secret_key=os.environ["ENCRYPTION_KEY"],
                db_engine=db_engine,
            ),
        ),
    )

    playlist = TempoPlaylist(
        song_fetcher=song_fetcher,
        spotify_playlist="https://open.spotify.com/playlist/0baOrekhXPa0YpUKgrDhs9?si=22badfd9a32b48dd",
    )

    # songs = song_fetcher.get_songs_from_playlist(playlist=playlist.id)
    song_fetcher.spotify.current_user()
    return


@app.cell(disabled=True, hide_code=True)
def _():


    # # --- Easing Functions (No changes needed, already excellent) ---
    # def linear(t: float) -> float:
    #     """Linear easing: constant rate of change."""
    #     return t

    # def ease_in(t: float) -> float:
    #     """Ease in: slow start, accelerating. (t^2)"""
    #     return t * t

    # def ease_out(t: float) -> float:
    #     """Ease out: fast start, decelerating. (1 - (1-t)^2)"""
    #     return 1 - (1 - t) * (1 - t)

    # def ease_in_out(t: float) -> float:
    #     """Ease in-out: slow start and end, fast middle."""
    #     if t < 0.5:
    #         return 2 * t * t
    #     return 1 - 2 * (1 - t) * (1 - t)

    # # --- Data Models and Type Definitions (No changes needed, already excellent) ---

    # class Song(pydantic.BaseModel):
    #     track_id: str
    #     title: str
    #     artist: str
    #     album: str
    #     tempo: int
    #     duration: float
    #     genre: Optional[str] = None

    #     @pydantic.field_validator("tempo", mode="before")
    #     @classmethod
    #     def round_tempo_to_nearest_5(cls, v: float) -> int:
    #         return math.floor(v / 5) * 5

    #     @pydantic.field_validator("duration", mode="before")
    #     @classmethod
    #     def limit_duration_precision(cls, v: float) -> float:
    #         return round(v, 1)

    #     @pydantic.computed_field
    #     @property
    #     def spotify_uri(self) -> str:
    #         return f"spotify:track:{self.track_id}"

    # class EasingType(Enum):
    #     LINEAR = "linear"
    #     EASE_IN = "ease_in"
    #     EASE_OUT = "ease_out"
    #     EASE_IN_OUT = "ease_in_out"

    # @dataclass(frozen=True)
    # class TempoRange:
    #     min_tempo: int
    #     max_tempo: int
    #     required_duration: float

    # class TempoDistribution(TypedDict):
    #     required_duration: float
    #     actual_duration: float
    #     song_count: int
    #     deficit: float
    #     songs: List[Song]

    # @dataclass
    # class PlaylistResult:
    #     songs: List[Song]
    #     total_duration: float
    #     target_duration: float
    #     tempo_distribution: Dict[TempoRange, TempoDistribution]
    #     fitness_score: float

    # # --- Core Playlist Logic (Refactored) ---

    # class PlaylistCalculator:
    #     """Calculates and generates playlists with a specified tempo progression."""

    #     _FITNESS_DISTRIBUTION_WEIGHT = 0.7
    #     _FITNESS_DURATION_WEIGHT = 0.3
    #     _GREEDY_UPPER_TOLERANCE = 1.1
    #     _GREEDY_LOWER_TOLERANCE = 0.9

    #     def __init__(self, total_duration: float, low_tempo: int, high_tempo: int,
    #                  easing_type: EasingType = EasingType.LINEAR, tempo_step: int = 5):
    #         if low_tempo >= high_tempo:
    #             raise ValueError("low_tempo must be less than high_tempo.")
    #         self.total_duration = total_duration
    #         self.low_tempo = low_tempo
    #         self.high_tempo = high_tempo
    #         self.easing_type = easing_type
    #         self.tempo_step = tempo_step
    #         self.easing_func = self._get_easing_function(easing_type)
    #         self.tempo_ranges = self._calculate_tempo_ranges()

    #         # IMPROVEMENT: Pre-calculate the minimum tempo of each range for fast lookups.
    #         # This list is inherently sorted, which is perfect for binary search.
    #         self._range_min_tempos = [r.min_tempo for r in self.tempo_ranges]

    #     def _get_easing_function(self, easing_type: EasingType) -> Callable[[float], float]:
    #         # IMPROVEMENT: Added a more specific type hint for the map.
    #         easing_map: Dict[EasingType, Callable[[float], float]] = {
    #             EasingType.LINEAR: linear,
    #             EasingType.EASE_IN: ease_in,
    #             EasingType.EASE_OUT: ease_out,
    #             EasingType.EASE_IN_OUT: ease_in_out,
    #         }
    #         return easing_map[easing_type]

    #     def _calculate_tempo_ranges(self) -> List[TempoRange]:
    #         tempo_ranges = []
    #         tempo_span = self.high_tempo - self.low_tempo

    #         current_tempo = self.low_tempo
    #         while current_tempo < self.high_tempo:
    #             next_tempo = min(current_tempo + self.tempo_step, self.high_tempo)

    #             range_start_norm = (current_tempo - self.low_tempo) / tempo_span
    #             range_end_norm = (next_tempo - self.low_tempo) / tempo_span

    #             # The difference in the eased value determines the duration proportion.
    #             # Since the input 't' is normalized (0 to 1), the sum of all
    #             # duration_weights will also be 1, so no further normalization is needed.
    #             duration_weight = self.easing_func(range_end_norm) - self.easing_func(range_start_norm)

    #             tempo_ranges.append(TempoRange(
    #                 min_tempo=current_tempo,
    #                 max_tempo=next_tempo,
    #                 required_duration=self.total_duration * duration_weight
    #             ))
    #             current_tempo = next_tempo

    #         return tempo_ranges

    #     def _get_range_for_song(self, song: Song) -> Optional[TempoRange]:
    #         """
    #         IMPROVEMENT: Efficiently finds the correct TempoRange for a single song
    #         using binary search (bisect).
    #         """
    #         if not self.low_tempo <= song.tempo < self.high_tempo:
    #             return None

    #         # Find the index of the range this song's tempo falls into.
    #         # bisect_right gives us the insertion point, and subtracting 1 gives the correct index.
    #         index = bisect.bisect_right(self._range_min_tempos, song.tempo) - 1
    #         return self.tempo_ranges[index]

    #     def _group_songs_by_tempo_range(self, songs: List[Song]) -> Dict[TempoRange, List[Song]]:
    #         """
    #         IMPROVEMENT: Now uses the highly efficient `_get_range_for_song` method.
    #         This is now O(N * log M) instead of O(N * M).
    #         """
    #         songs_by_range = defaultdict(list)
    #         for song in songs:
    #             tempo_range = self._get_range_for_song(song)
    #             if tempo_range:
    #                 songs_by_range[tempo_range].append(song)
    #         return songs_by_range

    #     def _calculate_distribution(self, playlist: List[Song]) -> Dict[TempoRange, TempoDistribution]:
    #         """Calculates the tempo distribution for a given playlist."""
    #         distribution: Dict[TempoRange, TempoDistribution] = {}
    #         # This call is now much more efficient.
    #         songs_by_range = self._group_songs_by_tempo_range(playlist)

    #         for tempo_range in self.tempo_ranges:
    #             songs_in_range = songs_by_range.get(tempo_range, [])
    #             actual_duration = sum(song.duration for song in songs_in_range)

    #             distribution[tempo_range] = {
    #                 'required_duration': tempo_range.required_duration,
    #                 'actual_duration': actual_duration,
    #                 'song_count': len(songs_in_range),
    #                 'deficit': tempo_range.required_duration - actual_duration,
    #                 'songs': songs_in_range
    #             }
    #         return distribution

    #     def _calculate_fitness(self, playlist: List[Song]) -> float:
    #         """Calculates how well the playlist matches the target distribution."""
    #         if not playlist:
    #             return 0.0

    #         distribution = self._calculate_distribution(playlist)
    #         total_error = sum(abs(data['deficit']) for data in distribution.values())

    #         if self.total_duration > 0:
    #             # Fitness based on how well the duration of each tempo range was met
    #             distribution_fitness = 1.0 - (total_error / self.total_duration)

    #             # Fitness based on how close the total playlist duration is to the target
    #             total_actual_duration = sum(data['actual_duration'] for data in distribution.values())
    #             duration_penalty = abs(self.total_duration - total_actual_duration) / self.total_duration
    #             duration_fitness = 1.0 - duration_penalty

    #             # Weighted average of the two fitness scores
    #             return (distribution_fitness * self._FITNESS_DISTRIBUTION_WEIGHT) + \
    #                    (duration_fitness * self._FITNESS_DURATION_WEIGHT)
    #         return 0.0

    #     def generate_playlist(self, song_library: List[Song],
    #                           max_iterations: int = 2000,
    #                           allow_duplicates: bool = False,
    #                           shuffle_within_ranges: bool = True) -> PlaylistResult:
    #         """
    #         Generates an optimized playlist using Simulated Annealing.
    #         """
    #         if not song_library:
    #             raise ValueError("Song library cannot be empty")

    #         # Group the entire library once for efficient access.
    #         songs_by_range = self._group_songs_by_tempo_range(song_library)

    #         # 1. Generate a good starting point using a greedy approach.
    #         current_playlist = self._greedy_selection(songs_by_range, allow_duplicates)
    #         current_score = self._calculate_fitness(current_playlist)

    #         best_playlist = current_playlist
    #         best_score = current_score

    #         # IMPROVEMENT: Swapped hill-climbing for a Simulated Annealing algorithm.
    #         # This is much better at avoiding local optima to find a better overall solution.
    #         temp = 1.0
    #         cooling_rate = 0.995 # Cooldown rate per iteration

    #         for i in range(max_iterations):
    #             # 2. Mutate the current solution to create a neighbor.
    #             candidate = self._mutate_playlist(current_playlist, song_library, allow_duplicates)
    #             if not candidate:
    #                 continue

    #             candidate_score = self._calculate_fitness(candidate)

    #             # 3. Decide whether to move to the new solution.
    #             # Always move if the new solution is better.
    #             # Sometimes move to a worse solution, controlled by the current temperature.
    #             acceptance_prob = math.exp((candidate_score - current_score) / temp)

    #             if candidate_score > current_score or random.random() < acceptance_prob:
    #                 current_playlist = candidate
    #                 current_score = candidate_score

    #                 # Update the best-so-far solution
    #                 if current_score > best_score:
    #                     best_playlist = current_playlist
    #                     best_score = current_score

    #             # 4. Cool the temperature.
    #             temp *= cooling_rate

    #         # 5. Finalize the playlist.
    #         if shuffle_within_ranges:
    #             best_playlist = self._shuffle_within_ranges(best_playlist)

    #         return PlaylistResult(
    #             songs=best_playlist,
    #             total_duration=sum(song.duration for song in best_playlist),
    #             target_duration=self.total_duration,
    #             tempo_distribution=self._calculate_distribution(best_playlist),
    #             fitness_score=best_score
    #         )

    #     # _greedy_selection and _mutate_playlist are helper methods for the generation
    #     # algorithm. Their logic remains sound for this purpose. No major changes needed.
    #     def _greedy_selection(self, songs_by_range: Dict[TempoRange, List[Song]], allow_duplicates: bool) -> List[Song]:
    #         """Greedy algorithm to select songs for each tempo range."""
    #         playlist = []
    #         used_songs = set()

    #         for tempo_range in self.tempo_ranges:
    #             available_songs = songs_by_range.get(tempo_range, [])
    #             if not available_songs:
    #                 continue

    #             sorted_songs = sorted(available_songs, key=lambda x: x.duration, reverse=True)

    #             current_duration = 0.0
    #             target_duration = tempo_range.required_duration

    #             for song in sorted_songs:
    #                 if not allow_duplicates and song.track_id in used_songs:
    #                     continue

    #                 if current_duration + song.duration <= target_duration * self._GREEDY_UPPER_TOLERANCE:
    #                     playlist.append(song)
    #                     current_duration += song.duration
    #                     if not allow_duplicates:
    #                         used_songs.add(song.track_id)

    #                 if current_duration >= target_duration * self._GREEDY_LOWER_TOLERANCE:
    #                     break
    #         return playlist

    #     def _mutate_playlist(self, playlist: List[Song], song_library: List[Song], allow_duplicates: bool) -> Optional[List[Song]]:
    #         """Creates a mutated version of the playlist for optimization."""
    #         if not playlist:
    #             return None

    #         new_playlist = playlist.copy()
    #         mutation_type = random.choice(['add', 'remove', 'swap'])

    #         playlist_ids = {song.track_id for song in new_playlist}

    #         if mutation_type == 'add' and (allow_duplicates or len(new_playlist) < len(song_library)):
    #             # Add a random, unused song from the library
    #             if allow_duplicates:
    #                 unused_songs = song_library
    #             else:
    #                 unused_songs = [s for s in song_library if s.track_id not in playlist_ids]

    #             if unused_songs:
    #                 new_playlist.append(random.choice(unused_songs))

    #         elif mutation_type == 'remove' and len(new_playlist) > 1:
    #             # Remove a random song
    #             new_playlist.pop(random.randint(0, len(new_playlist) - 1))

    #         elif mutation_type == 'swap' and len(new_playlist) > 0:
    #             # Swap a song from the playlist with one from the library
    #             idx_to_replace = random.randint(0, len(new_playlist) - 1)

    #             if allow_duplicates:
    #                  replacement_candidates = song_library
    #             else:
    #                 # Candidates for replacement can include any song not in the *rest* of the playlist
    #                 candidate_ids = playlist_ids - {new_playlist[idx_to_replace].track_id}
    #                 replacement_candidates = [s for s in song_library if s.track_id not in candidate_ids]

    #             if replacement_candidates:
    #                 new_playlist[idx_to_replace] = random.choice(replacement_candidates)

    #         return new_playlist

    #     def _shuffle_within_ranges(self, playlist: List[Song]) -> List[Song]:
    #         """Shuffles songs within their tempo ranges to create variety."""
    #         songs_by_range = self._group_songs_by_tempo_range(playlist)

    #         shuffled_playlist = []
    #         # Iterate through the canonical tempo_ranges to maintain order
    #         for tempo_range in self.tempo_ranges:
    #             songs_in_range = songs_by_range.get(tempo_range, [])
    #             random.shuffle(songs_in_range)
    #             shuffled_playlist.extend(songs_in_range)

    #         return shuffled_playlist
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
