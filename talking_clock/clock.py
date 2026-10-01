"""Talking Clock core module for constructing MP3 audio sequences and announcing time."""

import os
from datetime import datetime
from typing import List, Optional, Union

from .exceptions import MissingAudioFileError
from .player import SystemAudioPlayer


class TalkingClock:
    """Talking Clock manager class."""

    DEFAULT_MP3_DIR = "mp3-thai-clock"

    REQUIRED_KEYWORD_FILES = [
        "begintime.mp3",
        "endtime.mp3",
        "hour.mp3",
        "minute.mp3",
        "second.mp3",
    ]

    def __init__(
        self,
        mp3_dir: Optional[str] = None,
        player: Optional[SystemAudioPlayer] = None,
        use_12_hour: bool = False,
        allow_dummy: bool = True,
    ):
        """Initialize Talking Clock.

        Args:
            mp3_dir: Path to directory containing MP3 audio files. If None, resolves default directory.
            player: SystemAudioPlayer instance. If None, auto-creates and detects system player.
            use_12_hour: If True, converts 24-hour hour (0-23) to 12-hour format (1-12). Default False (0-23).
            allow_dummy: If True, allows falling back to dummy silent player when no system player is found.
        """
        self.mp3_dir = self._resolve_mp3_dir(mp3_dir)
        self.player = player or SystemAudioPlayer(allow_dummy=allow_dummy)
        self.use_12_hour = use_12_hour

    def _resolve_mp3_dir(self, custom_dir: Optional[str]) -> str:
        """Resolve MP3 directory path."""
        if custom_dir:
            if os.path.isabs(custom_dir):
                return custom_dir
            # Relative to current working directory
            if os.path.exists(custom_dir):
                return os.path.abspath(custom_dir)

        # Try to locate mp3-thai-clock relative to package or workspace
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(pkg_dir)

        candidates = [
            os.path.join(parent_dir, self.DEFAULT_MP3_DIR),
            os.path.join(os.getcwd(), self.DEFAULT_MP3_DIR),
            self.DEFAULT_MP3_DIR,
        ]

        for path in candidates:
            if os.path.exists(path):
                return os.path.abspath(path)

        # Fallback to provided directory or default string
        return os.path.abspath(custom_dir or self.DEFAULT_MP3_DIR)

    def verify_files(self) -> List[str]:
        """Verify that all required MP3 files exist in the mp3_dir.

        Returns:
            List of missing file names (empty if all exist).
        """
        missing = []
        # Check keyword files
        for fname in self.REQUIRED_KEYWORD_FILES:
            full_path = os.path.join(self.mp3_dir, fname)
            if not os.path.isfile(full_path):
                missing.append(fname)

        # Check number files 0.mp3 to 59.mp3
        for num in range(60):
            fname = f"{num}.mp3"
            full_path = os.path.join(self.mp3_dir, fname)
            if not os.path.isfile(full_path):
                missing.append(fname)

        return missing

    def get_sequence_for_time(
        self,
        hour: int,
        minute: int,
        second: int,
        include_keywords: bool = True,
    ) -> List[str]:
        """Generate ordered list of MP3 file paths for the given hour, minute, and second.

        Pattern:
        begintime.mp3 -> {hour}.mp3 -> hour.mp3 -> {minute}.mp3 -> minute.mp3 -> {second}.mp3 -> second.mp3 -> endtime.mp3

        Args:
            hour: Integer hour (0-23 or 1-12 if 12-hour clock).
            minute: Integer minute (0-59).
            second: Integer second (0-59).
            include_keywords: If True, includes begintime/endtime/hour/minute/second keyword mp3s.

        Returns:
            List of absolute paths to MP3 files.
        """
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute must be between 0 and 59, got {minute}")
        if not (0 <= second <= 59):
            raise ValueError(f"Second must be between 0 and 59, got {second}")

        h_val = hour
        if self.use_12_hour:
            h_val = hour % 12
            if h_val == 0:
                h_val = 12
        else:
            if not (0 <= hour <= 23):
                raise ValueError(f"Hour must be between 0 and 23 for 24-hour mode, got {hour}")

        filenames = []
        if include_keywords:
            filenames.append("begintime.mp3")

        filenames.append(f"{h_val}.mp3")
        if include_keywords:
            filenames.append("hour.mp3")

        filenames.append(f"{minute}.mp3")
        if include_keywords:
            filenames.append("minute.mp3")

        filenames.append(f"{second}.mp3")
        if include_keywords:
            filenames.append("second.mp3")

        if include_keywords:
            filenames.append("endtime.mp3")

        file_paths = []
        missing = []
        for name in filenames:
            path = os.path.join(self.mp3_dir, name)
            if not os.path.isfile(path):
                missing.append(name)
            file_paths.append(path)

        if missing:
            raise MissingAudioFileError(
                f"Missing required audio files in '{self.mp3_dir}': {', '.join(missing)}"
            )

        return file_paths

    def get_current_time_sequence(self, include_keywords: bool = True) -> List[str]:
        """Get MP3 audio sequence for the current system time."""
        now = datetime.now()
        return self.get_sequence_for_time(
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            include_keywords=include_keywords,
        )

    def announce_time(
        self,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        dt: Optional[datetime] = None,
        blocking: bool = True,
    ) -> List[str]:
        """Announce specific time or current time via audio playback.

        Args:
            hour: Optional hour integer.
            minute: Optional minute integer.
            second: Optional second integer.
            dt: Optional datetime object (takes precedence over hour/minute/second if specified).
            blocking: If True, waits for full audio playback to complete before returning.

        Returns:
            List of MP3 file paths that were played.
        """
        if dt is not None:
            seq = self.get_sequence_for_time(dt.hour, dt.minute, dt.second)
        elif hour is not None and minute is not None and second is not None:
            seq = self.get_sequence_for_time(hour, minute, second)
        else:
            seq = self.get_current_time_sequence()

        self.player.play_sequence(seq, blocking=blocking)
        return seq
