"""Audio player detector and executor supporting macOS, Linux, and Windows."""

import os
import platform
import shutil
import subprocess
import sys
import time
from typing import List, Optional, Tuple, Dict, Any

from .exceptions import AudioPlayerNotFoundError, AudioPlaybackError


class SystemAudioPlayer:
    """Detects system command to play MP3 audio files across macOS, Linux, and Windows."""

    PLAYER_CONFIGS: Dict[str, List[Dict[str, Any]]] = {
        "darwin": [
            {
                "name": "afplay",
                "binary": "afplay",
                "args": ["{file}"],
                "description": "macOS Native Audio Player",
            },
            {
                "name": "ffplay",
                "binary": "ffplay",
                "args": ["-nodisp", "-autoexit", "-loglevel", "quiet", "{file}"],
                "description": "FFmpeg Media Player",
            },
            {
                "name": "mpv",
                "binary": "mpv",
                "args": ["--no-terminal", "{file}"],
                "description": "MPV Media Player",
            },
            {
                "name": "vlc",
                "binary": "vlc",
                "args": ["-I", "dummy", "--play-and-exit", "{file}"],
                "description": "VLC Media Player",
            },
            {
                "name": "cvlc",
                "binary": "cvlc",
                "args": ["--play-and-exit", "{file}"],
                "description": "Command-line VLC",
            },
        ],
        "linux": [
            {
                "name": "play",
                "binary": "play",
                "args": ["-q", "{file}"],
                "description": "SoX Audio Player",
            },
            {
                "name": "paplay",
                "binary": "paplay",
                "args": ["{file}"],
                "description": "PulseAudio Sound Player",
            },
            {
                "name": "mpg123",
                "binary": "mpg123",
                "args": ["-q", "{file}"],
                "description": "MPG123 Console Player",
            },
            {
                "name": "mpg321",
                "binary": "mpg321",
                "args": ["-q", "{file}"],
                "description": "MPG321 Console Player",
            },
            {
                "name": "ffplay",
                "binary": "ffplay",
                "args": ["-nodisp", "-autoexit", "-loglevel", "quiet", "{file}"],
                "description": "FFmpeg Media Player",
            },
            {
                "name": "mpv",
                "binary": "mpv",
                "args": ["--no-terminal", "{file}"],
                "description": "MPV Media Player",
            },
            {
                "name": "cvlc",
                "binary": "cvlc",
                "args": ["--play-and-exit", "{file}"],
                "description": "Command-line VLC",
            },
            {
                "name": "vlc",
                "binary": "vlc",
                "args": ["-I", "dummy", "--play-and-exit", "{file}"],
                "description": "VLC Media Player",
            },
            {
                "name": "aplay",
                "binary": "aplay",
                "args": ["-q", "{file}"],
                "description": "ALSA Player",
            },
        ],
        "windows": [
            {
                "name": "powershell",
                "binary": "powershell",
                "args": [
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    (
                        "$wm = New-Object -ComObject WMPlayer.OCX; "
                        "$media = $wm.newMedia('{file}'); "
                        "$wm.currentMedia = $media; "
                        "while($wm.playState -ne 1 -and $wm.playState -ne 0 -and $wm.playState -ne 8) "
                        "{ Start-Sleep -m 100 }"
                    ),
                ],
                "description": "Windows PowerShell WMPlayer COM",
            },
            {
                "name": "cmd_start",
                "binary": "cmd",
                "args": ["/c", "start", "/wait", "", "{file}"],
                "description": "Windows Command Prompt Shell Launcher",
            },
            {
                "name": "wmplayer",
                "binary": "wmplayer",
                "args": ["{file}", "/close"],
                "description": "Windows Media Player",
            },
            {
                "name": "ffplay",
                "binary": "ffplay",
                "args": ["-nodisp", "-autoexit", "-loglevel", "quiet", "{file}"],
                "description": "FFmpeg Media Player",
            },
            {
                "name": "mpv",
                "binary": "mpv",
                "args": ["--no-terminal", "{file}"],
                "description": "MPV Media Player",
            },
            {
                "name": "vlc",
                "binary": "vlc",
                "args": ["-I", "dummy", "--play-and-exit", "{file}"],
                "description": "VLC Media Player",
            },
        ],
    }

    def __init__(self, preferred_player: Optional[str] = None):
        """Initialize SystemAudioPlayer.

        Args:
            preferred_player: Optional player name or command executable to force use.
        """
        self.os_type = self._detect_os()
        self.preferred_player = preferred_player
        self.detected_player = self.detect_player()

    @staticmethod
    def _detect_os() -> str:
        """Detect normalized operating system name."""
        sys_name = platform.system().lower()
        if sys_name == "darwin":
            return "darwin"
        elif sys_name == "windows" or os.name == "nt":
            return "windows"
        else:
            return "linux"

    def get_supported_players(self) -> List[Dict[str, Any]]:
        """Get the list of supported player configurations for current OS."""
        return self.PLAYER_CONFIGS.get(self.os_type, self.PLAYER_CONFIGS["linux"])

    def detect_player(self) -> Dict[str, Any]:
        """Detect available player command on the current system.

        Returns:
            Dict containing name, binary path, args template, and description.

        Raises:
            AudioPlayerNotFoundError if no player executable is found.
        """
        if self.preferred_player:
            # Check if preferred player exists as exact binary or name in config
            binary_path = shutil.which(self.preferred_player)
            if binary_path:
                # Find matching config template if available
                candidates = self.get_supported_players()
                for c in candidates:
                    if c["name"] == self.preferred_player or c["binary"] == self.preferred_player:
                        return {
                            "name": c["name"],
                            "binary": binary_path,
                            "args": c["args"],
                            "description": c["description"],
                        }
                return {
                    "name": self.preferred_player,
                    "binary": binary_path,
                    "args": ["{file}"],
                    "description": f"Custom player ({self.preferred_player})",
                }

        candidates = self.get_supported_players()
        for candidate in candidates:
            binary_path = shutil.which(candidate["binary"])
            if binary_path:
                return {
                    "name": candidate["name"],
                    "binary": binary_path,
                    "args": candidate["args"],
                    "description": candidate["description"],
                }

        raise AudioPlayerNotFoundError(
            f"No compatible MP3 audio player found on system ({self.os_type}). "
            f"Tested candidates: {[c['binary'] for c in candidates]}"
        )

    def build_command(self, file_path: str) -> List[str]:
        """Build execution command for a given audio file path."""
        abs_path = os.path.abspath(file_path)
        player = self.detected_player
        cmd = [player["binary"]]
        for arg in player["args"]:
            cmd.append(arg.format(file=abs_path))
        return cmd

    def play_file(self, file_path: str, blocking: bool = True) -> Optional[subprocess.Popen]:
        """Play a single audio file.

        Args:
            file_path: Path to MP3 file.
            blocking: If True, waits for playback to finish before returning.

        Returns:
            subprocess.Popen process object if non-blocking, None if blocking.

        Raises:
            FileNotFoundError if the target file does not exist.
            AudioPlaybackError if execution fails.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        cmd = self.build_command(file_path)
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if blocking:
                returncode = process.wait()
                if returncode != 0:
                    raise AudioPlaybackError(
                        f"Player '{self.detected_player['name']}' exited with code {returncode} while playing '{file_path}'"
                    )
                return None
            return process
        except Exception as e:
            if isinstance(e, (FileNotFoundError, AudioPlaybackError)):
                raise
            raise AudioPlaybackError(f"Failed to execute audio player command: {e}") from e

    def play_sequence(self, file_paths: List[str], blocking: bool = True) -> None:
        """Play a list of audio files sequentially.

        Args:
            file_paths: List of MP3 file paths.
            blocking: If True, plays synchronously in current thread. If False, runs in background thread.

        Raises:
            MissingAudioFileError / FileNotFoundError if files are missing.
            AudioPlaybackError if playback fails.
        """
        for f in file_paths:
            if not os.path.isfile(f):
                raise FileNotFoundError(f"Audio file missing in sequence: {f}")

        if blocking:
            for f in file_paths:
                self.play_file(f, blocking=True)
        else:
            import threading
            thread = threading.Thread(
                target=self._play_sequence_worker,
                args=(file_paths,),
                daemon=True,
            )
            thread.start()

    def _play_sequence_worker(self, file_paths: List[str]) -> None:
        """Worker thread method for non-blocking sequential playback."""
        for f in file_paths:
            try:
                self.play_file(f, blocking=True)
            except Exception as e:
                sys.stderr.write(f"Background playback error playing {f}: {e}\n")
                break
