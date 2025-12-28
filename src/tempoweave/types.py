from typing import Annotated, Literal, TypedDict

type BrowserT = Literal["chrome", "firefox", "chromium"]

type SpotifyIDT = Annotated[str, "A base-62 identifier found at the end of the Spotify URI."]
type SpotifyURIT = Annotated[str, "Takes the format 'spotify:<resource_type>:<spotify_id>'."]
type SpotifyURLT = Annotated[str, "Takes the format 'http://open.spotify.com/<resource_type>/<spotify_id>'"]
type SpotifyIdentityT = SpotifyIDT | SpotifyURIT | SpotifyURLT


class SpotifyAuthInfoT(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    expires_at: int
