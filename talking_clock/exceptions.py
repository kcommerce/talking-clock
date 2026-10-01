"""Custom exceptions for Talking Clock library."""

class TalkingClockError(Exception):
    """Base exception for Talking Clock library errors."""
    pass

class AudioPlayerNotFoundError(TalkingClockError):
    """Raised when no suitable audio player command is found on the host system."""
    pass

class AudioPlaybackError(TalkingClockError):
    """Raised when audio playback fails during execution."""
    pass

class MissingAudioFileError(TalkingClockError):
    """Raised when one or more required MP3 files are missing."""
    pass
