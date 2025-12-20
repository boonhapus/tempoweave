import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    """
    # Tempoweave Demo

    This notebook demonstrates the core functionality of the Tempoweave library,
    which creates tempo-progressive playlists using simulated annealing.
    """
    return


@app.cell
def _():
    from tempoweave.schema import Song
    from tempoweave.playlist.generator import PlaylistCalculator, EasingType
    return EasingType, PlaylistCalculator, Song


@app.cell
def _(Song):
    # Create a sample library of songs with varying tempos
    song_library = [
        Song(track_id="1", title="Slow Start", artist="Artist A", album="Album 1", tempo=80, duration=3.5),
        Song(track_id="2", title="Easy Going", artist="Artist B", album="Album 2", tempo=85, duration=4.0),
        Song(track_id="3", title="Morning Vibe", artist="Artist C", album="Album 3", tempo=90, duration=3.8),
        Song(track_id="4", title="Wake Up", artist="Artist D", album="Album 4", tempo=95, duration=3.2),
        Song(track_id="5", title="Getting Started", artist="Artist E", album="Album 5", tempo=100, duration=4.1),
        Song(track_id="6", title="Building Up", artist="Artist F", album="Album 6", tempo=105, duration=3.9),
        Song(track_id="7", title="Moving Along", artist="Artist G", album="Album 7", tempo=110, duration=3.7),
        Song(track_id="8", title="Mid Pace", artist="Artist H", album="Album 8", tempo=115, duration=4.3),
        Song(track_id="9", title="Accelerate", artist="Artist I", album="Album 9", tempo=120, duration=3.4),
        Song(track_id="10", title="Pushing Hard", artist="Artist J", album="Album 10", tempo=125, duration=3.6),
        Song(track_id="11", title="High Energy", artist="Artist K", album="Album 11", tempo=130, duration=4.0),
        Song(track_id="12", title="Peak Performance", artist="Artist L", album="Album 12", tempo=135, duration=3.3),
        Song(track_id="13", title="Maximum Effort", artist="Artist M", album="Album 13", tempo=140, duration=3.8),
        Song(track_id="14", title="Sprint Mode", artist="Artist N", album="Album 14", tempo=145, duration=3.5),
        Song(track_id="15", title="All Out", artist="Artist O", album="Album 15", tempo=150, duration=3.2),
    ]
    return (song_library,)


@app.cell
def _(EasingType, PlaylistCalculator, song_library):
    # Create a playlist calculator for a 30-minute workout
    # Tempo progression: 80 BPM -> 150 BPM with linear easing
    calculator = PlaylistCalculator(
        total_duration=30.0,  # 30 minutes
        low_tempo=80,
        high_tempo=150,
        easing_type=EasingType.LINEAR,
        tempo_step=5
    )

    # Generate the optimized playlist
    result = calculator.generate_playlist(
        song_library=song_library,
        max_iterations=1000,
        allow_duplicates=False,
        shuffle_within_ranges=True
    )

    return calculator, result


@app.cell
def _(mo, result):
    # Display the results
    mo.md(f"""
    ## Playlist Results

    **Target Duration:** {result.target_duration:.1f} minutes
    **Actual Duration:** {result.total_duration:.1f} minutes
    **Fitness Score:** {result.fitness_score:.2%}
    **Number of Songs:** {len(result.songs)}
    """)
    return


@app.cell
def _(mo, result):
    # Show the playlist
    playlist_data = [
        {
            "Title": song.title,
            "Artist": song.artist,
            "Tempo (BPM)": song.tempo,
            "Duration (min)": song.duration
        }
        for song in result.songs
    ]

    mo.ui.table(playlist_data, label="Generated Playlist")
    return (playlist_data,)


@app.cell
def _(mo, result):
    # Show tempo distribution analysis
    distribution_data = [
        {
            "Tempo Range": f"{tempo_range.min_tempo}-{tempo_range.max_tempo} BPM",
            "Required (min)": f"{dist['required_duration']:.1f}",
            "Actual (min)": f"{dist['actual_duration']:.1f}",
            "Songs": dist['song_count'],
            "Deficit (min)": f"{dist['deficit']:.1f}"
        }
        for tempo_range, dist in result.tempo_distribution.items()
    ]

    mo.md("## Tempo Distribution")
    mo.ui.table(distribution_data, label="How well each tempo range is filled")
    return (distribution_data,)


if __name__ == "__main__":
    app.run()
