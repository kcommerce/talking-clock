"""Unit tests for TalkingClock."""

import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from talking_clock.clock import TalkingClock
from talking_clock.exceptions import MissingAudioFileError


class TestTalkingClock(unittest.TestCase):
    """Test suite for TalkingClock core class."""

    def setUp(self):
        self.mp3_dir = os.path.abspath("mp3-thai-clock")
        self.mock_player = MagicMock()
        self.clock = TalkingClock(mp3_dir=self.mp3_dir, player=self.mock_player)

    def test_sequence_generation_user_example(self):
        """Test exact pattern rule: 09:05:07 -> begintime, 9, hour, 5, minute, 7, second, endtime."""
        seq = self.clock.get_sequence_for_time(9, 5, 7)
        expected_basenames = [
            "begintime.mp3",
            "9.mp3",
            "hour.mp3",
            "5.mp3",
            "minute.mp3",
            "7.mp3",
            "second.mp3",
            "endtime.mp3",
        ]
        actual_basenames = [os.path.basename(p) for p in seq]
        self.assertEqual(actual_basenames, expected_basenames)

    def test_sequence_generation_midnight(self):
        """Test 00:00:00 sequence generation."""
        seq = self.clock.get_sequence_for_time(0, 0, 0)
        actual_basenames = [os.path.basename(p) for p in seq]
        expected_basenames = [
            "begintime.mp3",
            "0.mp3",
            "hour.mp3",
            "0.mp3",
            "minute.mp3",
            "0.mp3",
            "second.mp3",
            "endtime.mp3",
        ]
        self.assertEqual(actual_basenames, expected_basenames)

    def test_sequence_generation_end_of_day(self):
        """Test 23:59:59 sequence generation."""
        seq = self.clock.get_sequence_for_time(23, 59, 59)
        actual_basenames = [os.path.basename(p) for p in seq]
        expected_basenames = [
            "begintime.mp3",
            "23.mp3",
            "hour.mp3",
            "59.mp3",
            "minute.mp3",
            "59.mp3",
            "second.mp3",
            "endtime.mp3",
        ]
        self.assertEqual(actual_basenames, expected_basenames)

    def test_sequence_without_keywords(self):
        """Test sequence generation without keyword mp3s."""
        seq = self.clock.get_sequence_for_time(9, 5, 7, include_keywords=False)
        actual_basenames = [os.path.basename(p) for p in seq]
        self.assertEqual(actual_basenames, ["9.mp3", "5.mp3", "7.mp3"])

    def test_invalid_time_values_raise_value_error(self):
        """Test bounds checking for hour, minute, second."""
        with self.assertRaises(ValueError):
            self.clock.get_sequence_for_time(24, 0, 0)
        with self.assertRaises(ValueError):
            self.clock.get_sequence_for_time(-1, 0, 0)
        with self.assertRaises(ValueError):
            self.clock.get_sequence_for_time(12, 60, 0)
        with self.assertRaises(ValueError):
            self.clock.get_sequence_for_time(12, 0, -5)

    def test_verify_files_success(self):
        """Test verify_files against actual workspace mp3-thai-clock directory."""
        missing = self.clock.verify_files()
        self.assertEqual(missing, [], f"Missing files found in mp3-thai-clock: {missing}")

    def test_missing_files_exception(self):
        """Test exception raised when files are missing."""
        empty_clock = TalkingClock(mp3_dir="/invalid/directory/path", player=self.mock_player)
        with self.assertRaises(MissingAudioFileError):
            empty_clock.get_sequence_for_time(9, 5, 7)

    def test_announce_time_calls_player(self):
        """Test announce_time triggers player.play_sequence."""
        seq = self.clock.announce_time(hour=9, minute=5, second=7, blocking=True)
        self.mock_player.play_sequence.assert_called_once_with(seq, blocking=True)

    def test_announce_time_with_datetime(self):
        """Test announce_time with datetime object."""
        test_dt = datetime(2026, 10, 1, 14, 30, 45)
        seq = self.clock.announce_time(dt=test_dt, blocking=False)
        actual_basenames = [os.path.basename(p) for p in seq]
        self.assertIn("14.mp3", actual_basenames)
        self.assertIn("30.mp3", actual_basenames)
        self.assertIn("45.mp3", actual_basenames)
        self.mock_player.play_sequence.assert_called_once_with(seq, blocking=False)


if __name__ == "__main__":
    unittest.main()
