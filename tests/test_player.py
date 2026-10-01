"""Unit tests for SystemAudioPlayer."""

import os
import unittest
from unittest.mock import patch, MagicMock

from talking_clock.player import SystemAudioPlayer
from talking_clock.exceptions import AudioPlayerNotFoundError, AudioPlaybackError


class TestSystemAudioPlayer(unittest.TestCase):
    """Test suite for SystemAudioPlayer."""

    @patch("shutil.which", return_value="/usr/bin/mock_player")
    def test_os_detection(self, mock_which):
        with patch("platform.system", return_value="Darwin"):
            player = SystemAudioPlayer()
            self.assertEqual(player.os_type, "darwin")

        with patch("platform.system", return_value="Linux"):
            player = SystemAudioPlayer()
            self.assertEqual(player.os_type, "linux")

        with patch("platform.system", return_value="Windows"):
            player = SystemAudioPlayer()
            self.assertEqual(player.os_type, "windows")

    @patch("shutil.which")
    def test_detect_mac_player(self, mock_which):
        def side_effect(cmd):
            if cmd == "afplay":
                return "/usr/bin/afplay"
            return None

        mock_which.side_effect = side_effect
        with patch("platform.system", return_value="Darwin"):
            player = SystemAudioPlayer()
            detected = player.detect_player()
            self.assertEqual(detected["name"], "afplay")
            self.assertEqual(detected["binary"], "/usr/bin/afplay")

    @patch("shutil.which")
    def test_detect_linux_player(self, mock_which):
        def side_effect(cmd):
            if cmd == "play":
                return "/usr/bin/play"
            return None

        mock_which.side_effect = side_effect
        with patch("platform.system", return_value="Linux"):
            player = SystemAudioPlayer()
            detected = player.detect_player()
            self.assertEqual(detected["name"], "play")
            self.assertEqual(detected["binary"], "/usr/bin/play")

    @patch("shutil.which")
    def test_detect_windows_player(self, mock_which):
        def side_effect(cmd):
            if cmd == "powershell":
                return "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
            return None

        mock_which.side_effect = side_effect
        with patch("platform.system", return_value="Windows"):
            player = SystemAudioPlayer()
            detected = player.detect_player()
            self.assertEqual(detected["name"], "powershell")

    @patch("shutil.which", return_value=None)
    def test_no_player_found_raises_exception(self, mock_which):
        with patch("platform.system", return_value="Linux"):
            with self.assertRaises(AudioPlayerNotFoundError):
                SystemAudioPlayer(allow_dummy=False)

    @patch("shutil.which", return_value=None)
    def test_dummy_player_fallback(self, mock_which):
        player = SystemAudioPlayer(allow_dummy=True)
        self.assertEqual(player.detected_player["name"], "dummy")

    @patch("shutil.which")
    def test_preferred_player_override(self, mock_which):
        mock_which.return_value = "/usr/local/bin/mpv"
        player = SystemAudioPlayer(preferred_player="mpv")
        self.assertEqual(player.detected_player["name"], "mpv")
        self.assertEqual(player.detected_player["binary"], "/usr/local/bin/mpv")

    @patch("subprocess.Popen")
    @patch("os.path.isfile", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/mock_player")
    def test_play_file_blocking(self, mock_which, mock_isfile, mock_popen):
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        player = SystemAudioPlayer()
        player.play_file("test.mp3", blocking=True)
        mock_popen.assert_called_once()
        mock_process.wait.assert_called_once()

    @patch("os.path.isfile", return_value=False)
    @patch("shutil.which", return_value="/usr/bin/mock_player")
    def test_play_file_nonexistent_raises(self, mock_which, mock_isfile):
        player = SystemAudioPlayer()
        with self.assertRaises(FileNotFoundError):
            player.play_file("nonexistent.mp3")


if __name__ == "__main__":
    unittest.main()
