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
    from spotipy.oauth2 import SpotifyClientCredentials

    from tempoweave.weaver import Weaver
    from tempoweave.schema import Song
    return SpotifyClientCredentials, Weaver


@app.cell
def _(SpotifyClientCredentials, Weaver, os):
    creds = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
    )

    weaver = Weaver(spotify_auth=creds)
    return (weaver,)


@app.cell
def _(weaver):
    weaver.get_song("https://open.spotify.com/track/1bdS7Ba4vaNaGywh5qiyUn?si=16424f465f744038")
    return


@app.cell
def _(weaver):
    songs = weaver.get_songs_from_playlist("https://open.spotify.com/playlist/2Iy2d4z9OyHc87gHaODDCa?si=6a0bcb3975484f6d")
    songs
    return


@app.cell
def _():
    # tracks = "\n".join(f"{s.title} - {s.artist}" for s in songs)
    # prompt = f"""
    # Act as an expert musicologist and psychologist. I will provide a list of songs. Your goal is to extract the 'soul' of this playlist.

    # Please provide:

    #     The Narrative Arc: If this playlist were a movie soundtrack, what kind of story would it be telling?

    #     Subconscious Cues: Analyze the transition of moods. Is it a slow descent into sadness, or a high-energy build-up?

    #     Target Sentiment: What is the listener likely feeling, or what headspace are they trying to enter by playing this?

    #     The 'Outlier' Check: Identify if any song feels like it doesn't fit the theme and explain why.

    # Playlist:
    # {tracks}
    # """
    # print(prompt)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
