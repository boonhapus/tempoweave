import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import os

    import marimo as mo
    return (os,)


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
    from tempoweave.schema import Song
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

    # MusicBrainz? MusicBrainz Labs?

    weaver = Weaver(spotify_auth=spot_creds, last_fm_auth=last_creds)
    return (weaver,)


@app.cell
def _():
    # THIS FLOW SHUFFLES A PLAYLIST BY FETCHING A RANDOM SONG ON IT, THEN REWRITING IT WITH SIMILAR SONGS
    import random

    _t = "FIRST"
    _f = lambda choices: choices[0] if _t == "FIRST" else random.choice
    _n = "https://open.spotify.com/playlist/0baOrekhXPa0YpUKgrDhs9"

    # _p = weaver.get_playlist(spotify_playlist_identity=_n)
    # _c = _f(_p.songs)
    # _s = weaver.get_recommendations(_c, limit=24)

    # weaver.set_playlist(spotify_playlist_identity=_p.playlist_id, songs=[_c, *_s])
    # weaver.get_playlist(spotify_playlist_identity=_p.playlist_id)
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
def _():
    return


if __name__ == "__main__":
    app.run()
