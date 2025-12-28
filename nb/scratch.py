import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import os

    import marimo as mo
    return mo, os


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
    from spotipy.oauth2 import SpotifyOAuth

    from tempoweave.weaver import Weaver
    from tempoweave.schema import Song, TempoweavePlaylistSettings
    from tempoweave.__project__ import __version__
    return SpotifyOAuth, Weaver


@app.cell
def _(SpotifyOAuth, Weaver, os):
    spot_creds = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="https://127.0.0.1:8888/callback",
        scope=" ".join([
            "user-read-playback-state",
            "user-modify-playback-state",
            "playlist-modify-public",
            "playlist-modify-private",
        ])
    )

    last_creds = {
        "api_key": os.environ["LAST_FM_API_KEY"],
        "api_secret": os.environ["LAST_FM_API_SECRET"],
    }

    weaver = Weaver(spotify_auth=spot_creds, last_fm_auth=last_creds, browser="firefox")
    return (weaver,)


@app.cell
def _(weaver):
    # THIS FLOW SHUFFLES A PLAYLIST BY FETCHING A RANDOM SONG ON IT, THEN REWRITING IT WITH SIMILAR SONGS
    import random

    _n = "https://open.spotify.com/playlist/2C6Jr9OBdUXWgHkjQix0tH?si=d284f295f8d34d57"

    _p = weaver.get_playlist(spotify_playlist_identity=_n)
    _c = random.choice(_p.songs)
    _s = weaver.get_recommendations(_c, limit=24)

    weaver.set_playlist(spotify_playlist_identity=_p.playlist_id, songs=[_c, *_s])
    weaver.get_playlist(spotify_playlist_identity=_p.playlist_id)
    return


@app.cell(disabled=True)
def _(weaver):
    # THIS FLOW PERFORMS SENTIMENT ANALYSIS (via LLM) ON A GIVEN PLAYLIST.
    _p = "https://open.spotify.com/playlist/2LcnMk8awgBcCo9S62Y7Ri?si=27b430b828be45b7"
    _t = "\n".join(f"{s.title} - {s.artist}" for s in weaver.get_playlist(spotify_playlist_identity=_p).songs)
    _q = f"""
    Act as an expert musicologist and psychologist. I will provide a list of songs. Your goal is to extract the 'soul' of this playlist.

    Please provide:

        The Narrative Arc: If this playlist were a movie soundtrack, what kind of story would it be telling?

        Subconscious Cues: Analyze the transition of moods. Is it a slow descent into sadness, or a high-energy build-up?

        Target Sentiment: What is the listener likely feeling, or what headspace are they trying to enter by playing this?

        The 'Outlier' Check: Identify if any song feels like it doesn't fit the theme and explain why.

    Playlist:
    {_t}
    """
    print(_q)
    return


@app.cell
def _(weaver):
    _n = "https://open.spotify.com/playlist/0baOrekhXPa0YpUKgrDhs9"
    _p = weaver.get_playlist(spotify_playlist_identity=_n)

    _p.songs
    return


@app.cell
def _(mo):
    # Song selection mode dropdown
    song_selection_mode = mo.ui.dropdown(
        options=["FIRST", "RANDOM"],
        value="RANDOM",
        label="Song Selection Mode",
    )

    # Duration slider (in minutes, 1-180 range)
    duration = mo.ui.slider(
        start=1,
        stop=180,
        value=30,
        step=1,
        label="Duration (minutes)",
        show_value=True,
    )

    # Tempo range slider
    tempo = mo.ui.range_slider(start=35, stop=250, step=1, value=[100, 160], label="Select Tempo Range (BPM)", show_value=True)

    # Min tempo slider
    min_tempo = mo.ui.slider(
        start=60,
        stop=200,
        value=100,
        step=1,
        label="Min Tempo (BPM)",
        show_value=True,
    )

    # Max tempo slider
    max_tempo = mo.ui.slider(
        start=60,
        stop=200,
        value=140,
        step=1,
        label="Max Tempo (BPM)",
        show_value=True,
    )

    # Easing function dropdown
    easing_function = mo.ui.dropdown(
        options=["linear"],
        value="linear",
        label="Easing Function",
    )
    return


@app.cell
def _(mo):
    class ValidatedText:
        """..."""

        def __init__(self, label, validate_fn):
            self.validate_fn = validate_fn
            self.feedback = ""
            self.text_area = mo.ui.text(
                label=label,
                debounce=False,
                on_change=self._handle_change
            )

        def _handle_change(self, new_value):
            print("handling")

            if matched := self.validate_fn(new_value):
                self.value = new_value
                self.feedback = mo.md("Success!").style({"color": "green"})
            else:
                self.feedback = mo.md(f"Please enter a value valid, got {new_value}").style({"color": "red"})

            print(matched)

        @property
        def value(self):
            return self.text_area.value

        def _display_(self):
            """..."""
            return mo.vstack([self.text_area, self.feedback])
    return (ValidatedText,)


@app.cell
def _(ValidatedText):
    import re

    zip_validator = ValidatedText(
        label="Zip Code",
        validate_fn=lambda v: False,
    )
    return (zip_validator,)


@app.cell
def _(zip_validator):
    zip_validator
    return


@app.cell
def _(zip_validator):
    zip_validator.value
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
