#!/usr/bin/env python3
"""Comprehensive test runner and test code for Talking Clock library."""

import argparse
import os
import sys
import unittest
from datetime import datetime

# Ensure talking_clock package is importable from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from talking_clock import TalkingClock, SystemAudioPlayer, announce_current_time
from talking_clock.exceptions import TalkingClockError


def run_unit_tests():
    """Run all automated unit tests in the tests directory."""
    print("=" * 60)
    print("RUNNING TALKING CLOCK UNIT TESTS")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(os.path.dirname(__file__), "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def list_players():
    """List system player candidates for current operating system."""
    player = SystemAudioPlayer()
    print("=" * 60)
    print(f"AUDIO PLAYER DETECTION SUMMARY (OS: {player.os_type.upper()})")
    print("=" * 60)
    detected = player.detected_player
    print(f"Active Selected Player: {detected['name']} ({detected['description']})")
    print(f"Binary Path:            {detected['binary']}")
    print(f"Command Template:       {detected['binary']} {' '.join(detected['args'])}\n")

    print("All Supported Player Candidates for this OS:")
    for idx, cand in enumerate(player.get_supported_players(), 1):
        import shutil
        found_path = shutil.which(cand['binary'])
        status = f"AVAILABLE ({found_path})" if found_path else "NOT FOUND"
        print(f"  {idx}. [{cand['name']}] -> {status}")
    print("=" * 60)


def verify_mp3_files(mp3_dir: str):
    """Verify all required MP3 files in directory."""
    print("=" * 60)
    print("VERIFYING MP3 AUDIO FILES")
    print("=" * 60)
    clock = TalkingClock(mp3_dir=mp3_dir)
    print(f"Target MP3 Directory: {clock.mp3_dir}")
    missing = clock.verify_files()
    if missing:
        print(f"❌ ERROR: Missing {len(missing)} required audio files:")
        for f in missing:
            print(f"   - {f}")
        return False
    else:
        print("✅ SUCCESS: All 65 required MP3 files exist and are verified!")
        return True


def test_time_announcement(
    time_str: str = None,
    mp3_dir: str = None,
    preferred_player: str = None,
    dry_run: bool = False,
):
    """Test time evaluation and audio sequence playback."""
    print("=" * 60)
    print("TESTING TIME ANNOUNCEMENT")
    print("=" * 60)

    player = SystemAudioPlayer(preferred_player=preferred_player)
    clock = TalkingClock(mp3_dir=mp3_dir, player=player)

    if time_str:
        parts = time_str.split(":")
        if len(parts) != 3:
            print("Error: --time must be in HH:MM:SS format (e.g. 09:05:07)")
            return False
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        print(f"Evaluating requested time: {h:02d}:{m:02d}:{s:02d} (hour={h}, minute={m}, second={s})")
        seq = clock.get_sequence_for_time(h, m, s)
    else:
        now = datetime.now()
        print(f"Evaluating current system time: {now.strftime('%H:%M:%S')} (hour={now.hour}, minute={now.minute}, second={now.second})")
        seq = clock.get_current_time_sequence()

    print("\nGenerated MP3 Playback Sequence:")
    for idx, path in enumerate(seq, 1):
        print(f"  {idx}. {os.path.basename(path)} -> ({path})")

    if dry_run:
        print("\n[DRY RUN] Skipping actual audio output.")
    else:
        print(f"\nPlaying audio using player: '{player.detected_player['name']}'...")
        clock.player.play_sequence(seq, blocking=True)
        print("✅ Audio playback completed successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Talking Clock Python Library Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run automated unit test suite")
    parser.add_argument("--now", action="store_true", help="Announce current system time")
    parser.add_argument("--time", type=str, help="Announce specific time in HH:MM:SS format (e.g. 09:05:07)")
    parser.add_argument("--mp3-dir", type=str, help="Custom MP3 audio folder path")
    parser.add_argument("--player", type=str, help="Force specific audio player executable (e.g., afplay, play, ffplay, mpv)")
    parser.add_argument("--list-players", action="store_true", help="List detected and candidate system players")
    parser.add_argument("--verify", action="store_true", help="Verify presence of all required MP3 files")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate time and sequence without playing sound")

    args = parser.parse_args()

    # If no flags passed, run unit tests AND demonstrate 09:05:07 sequence
    if not (args.unit or args.now or args.time or args.list_players or args.verify):
        print("No specific command flag specified. Running full verification and unit test suite...\n")
        list_players()
        print()
        verify_mp3_files(args.mp3_dir)
        print()
        success = run_unit_tests()
        print()
        print("Testing example time announcement (09:05:07):")
        test_time_announcement(time_str="09:05:07", mp3_dir=args.mp3_dir, preferred_player=args.player, dry_run=args.dry_run)
        sys.exit(0 if success else 1)

    if args.list_players:
        list_players()

    if args.verify:
        verify_mp3_files(args.mp3_dir)

    if args.unit:
        success = run_unit_tests()
        if not success:
            sys.exit(1)

    if args.now or args.time:
        test_time_announcement(
            time_str=args.time,
            mp3_dir=args.mp3_dir,
            preferred_player=args.player,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
