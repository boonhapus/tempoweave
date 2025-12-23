from typing import Any
import copy
import logging
import pathlib
import tempfile

import librosa
import numpy as np
import yt_dlp

logger = logging.getLogger(__name__)


class YouTube(yt_dlp.YoutubeDL):
    # DEV NOTE:
    #  YT-DLP is essentially a command line interface, so some of the patterns below are
    #  going to look a bit odd. YoutubeDL.download() physically downloads a file from
    #  the YouTube service instead of interacting with it in memory.

    def __init__(self, ffmpeg_location: pathlib.Path | None = None):
        params = {
            "default_search": "ytsearch1:",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }

        if ffmpeg_location is not None:
            params["ffmpeg_location"] = ffmpeg_location.as_posix()

        super().__init__(params)

    def estimate_tempo(self, track_info: dict[str, Any], quiet: bool = False) -> int:
        """Download the song from YT and estimate its tempo."""
        try:
            original_params = copy.deepcopy(self.params)

            # Use track_info.id for a unique, stable filename
            temp_mp3 = pathlib.Path(f"{tempfile.gettempdir()}/{track_info['id']}.mp3")

            # Update parameters to match given info
            self.params["outtmpl"] = temp_mp3.as_posix().replace(".mp3", ".%(ext)s")
            self.params["quiet"] = quiet

            # YoutubeDL.__init__() does this.. so we emulate it.
            self._parse_outtmpl()

            # SEARCH: "{artist} {title}"
            self.download([f"{track_info['artists'][0]['name']} {track_info['name']}"])

            # POST-PROCESS FOR TEMPO USING librosa.
            song_data, sampling_rate = librosa.load(path=temp_mp3)
            tempo, _ = librosa.beat.beat_track(y=song_data, sr=sampling_rate)
            tempo = tempo.item() if isinstance(tempo, np.ndarray) else tempo
            return int(tempo)

        except Exception as e:
            logger.exception(f"Failed to estimate tempo for {track_info.get('id')}: {e}")
            return 0
        
        finally:
            self.params = original_params
