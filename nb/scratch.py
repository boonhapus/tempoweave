import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return


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

    from tempoweave.api.spotify import SpotifyAPIClient
    from tempoweave.schema import Song
    return SpotifyAPIClient, SpotifyClientCredentials


@app.cell
def _():
    SPOTIFY_CLIENT_ID = "3684d516e73a49caadc2723b59d226c5"
    SPOTIFY_SECRET_ID = "62200338b5934074898ec37738ff7b23"
    return SPOTIFY_CLIENT_ID, SPOTIFY_SECRET_ID


@app.cell
def _(
    SPOTIFY_CLIENT_ID,
    SPOTIFY_SECRET_ID,
    SpotifyAPIClient,
    SpotifyClientCredentials,
):
    auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_SECRET_ID)
    api = SpotifyAPIClient(spotify_auth=auth)
    return (api,)


@app.cell
def _(api):
    api.get_song("https://open.spotify.com/track/1bdS7Ba4vaNaGywh5qiyUn?si=16424f465f744038")
    return


@app.cell
def _(api):
    songs = api.get_songs_from_playlist("https://open.spotify.com/playlist/2Iy2d4z9OyHc87gHaODDCa?si=6a0bcb3975484f6d")
    songs
    return (songs,)


@app.cell
def _(songs):
    tracks = "\n".join(f"{s.title} - {s.artist}" for s in songs)
    prompt = f"""
    Act as an expert musicologist and psychologist. I will provide a list of songs. Your goal is to extract the 'soul' of this playlist.

    Please provide:

        The Narrative Arc: If this playlist were a movie soundtrack, what kind of story would it be telling?

        Subconscious Cues: Analyze the transition of moods. Is it a slow descent into sadness, or a high-energy build-up?

        Target Sentiment: What is the listener likely feeling, or what headspace are they trying to enter by playing this?

        The 'Outlier' Check: Identify if any song feels like it doesn't fit the theme and explain why.

    Playlist:
    {tracks}
    """
    print(prompt)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
