"""Talking Clock package.

A cross-platform Python library for audio time announcement.
"""

from .clock import TalkingClock
from .player import SystemAudioPlayer
from .exceptions import (
    TalkingClockError,
    AudioPlayerNotFoundError,
    AudioPlaybackError,
    MissingAudioFileError,
)

__version__ = "1.0.1"

__all__ = [
    "TalkingClock",
    "SystemAudioPlayer",
    "TalkingClockError",
    "AudioPlayerNotFoundError",
    "AudioPlaybackError",
    "MissingAudioFileError",
]


def announce_current_time(
    mp3_dir: str = None,
    preferred_player: str = None,
    blocking: bool = True,
):
    """Convenience function to announce the current system time immediately."""
    player = SystemAudioPlayer(preferred_player=preferred_player)
    clock = TalkingClock(mp3_dir=mp3_dir, player=player)
    return clock.announce_time(blocking=blocking)
