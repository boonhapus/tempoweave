from typing import Any
import copy
import logging
import pathlib
import tempfile
import random

import librosa
import yt_dlp

from tempoweave import const, types

logger = logging.getLogger(__name__)


class YouTube(yt_dlp.YoutubeDL):
    """Fetches information about Songs from YouTube."""
    # DEV NOTE:
    #   YT-DLP is essentially a command line interface, so some of the patterns below
    #   are going to look a bit odd. YoutubeDL.download() physically downloads a file
    #   from the YouTube service instead of interacting with it in memory.
    #

    def __init__(self, browser_cookie_for_age_verify: types.BrowserT, ffmpeg_location: pathlib.Path | None = None):
        params = {
            "default_search": "ytsearch1:",
            "cookiesfrombrowser": (browser_cookie_for_age_verify,),
            "format": "bestaudio/best",
            "force_keyframe_at_cuts": True,
            "ignoreerrors": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }

        if ffmpeg_location is not None:
            params["ffmpeg_location"] = ffmpeg_location.as_posix()

        super().__init__(params)

    def estimate_tempo(self, track_info: dict[str, Any], quiet: bool = True) -> int | None:
        """Download the song from YT and estimate its tempo."""
        MIN_SEC_FOR_TEMPO_ESTIMATION = 45

        # Calculate the boundaries for a song sample.
        dur = (track_info["duration_ms"] / const.ONE_MINUTE_IN_MILLISECONDS)
        beg = int(random.uniform(dur * 0.2, dur - MIN_SEC_FOR_TEMPO_ESTIMATION))

        # Use track_info.id for a unique, stable filename
        temp_mp3 = pathlib.Path(f"{tempfile.gettempdir()}/{track_info['id']}-sample.mp3")

        try:
            original_params = copy.deepcopy(self.params)

            # Update parameters to match given info
            self.params.update({
                "outtmpl": temp_mp3.as_posix().replace(".mp3", ".%(ext)s"),
                "quiet": quiet,
                "noprogress": quiet,
                "no_warnings": quiet,
                "download_ranges": lambda *a: [{"start_time": beg, "end_time": beg + MIN_SEC_FOR_TEMPO_ESTIMATION}],
            })

            # YoutubeDL.__init__() does this.. so we emulate it.
            self._parse_outtmpl()

            # SEARCH: "{artist} {title}"
            self.download([f"{track_info['artists'][0]['name']} {track_info['name']}"])

            if not temp_mp3.exists():
                return None

            # POST-PROCESS FOR TEMPO USING librosa.
            song_data, sampling_rate = librosa.load(path=temp_mp3, sr=22050)
            envelope = librosa.onset.onset_strength(y=song_data, sr=sampling_rate)
            tempo, beats = librosa.beat.beat_track(onset_envelope=envelope, sr=sampling_rate)

            return int(round(float(tempo)))

        except Exception as e:
            logger.exception(f"Failed to estimate tempo for {track_info.get('id')}: {e}")
            return None
        
        finally:
            self.params = original_params
