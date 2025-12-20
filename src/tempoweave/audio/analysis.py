from typing import Any
import logging
import pathlib
import tempfile

import librosa
import numpy as np
import yt_dlp

logger = logging.getLogger(__name__)


def estimate_tempo_from_yt(track_info: dict[str, Any], quiet: bool = False) -> int:
    """Download the song from YT and estimate its tempo."""
    try:
        temp_dir = tempfile.gettempdir()
        # Use track_info['id'] for a unique, stable filename
        temp_mp3 = pathlib.Path(f"{temp_dir}/{track_info['id']}.mp3")

        ydl_opts = {
            "default_search": "ytsearch1:",
            "outtmpl": temp_mp3.as_posix().replace(".mp3", ".%(ext)s"),
            # 'ffmpeg_location': r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
            "quiet": quiet,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            artist = track_info["artists"][0]["name"]
            title  = track_info["name"]
            ydl.download([f"{artist} {title}"])

        # POST-PROCESS FOR TEMPO USING librosa.
        song_data, sampling_rate = librosa.load(path=temp_mp3)
        tempo, _ = librosa.beat.beat_track(y=song_data, sr=sampling_rate)
        tempo = tempo.item() if isinstance(tempo, np.ndarray) else tempo
        return int(tempo)

    except Exception as e:
        logger.exception(f"Failed to estimate tempo for {track_info.get('name')}: {e}")
        return 0
