"""Command-line interface entrypoint for thai-talking-clock executable."""

import argparse
import os
import sys
from datetime import datetime

from .clock import TalkingClock
from .player import SystemAudioPlayer


def main():
    """Main CLI entrypoint for thai-talking-clock command."""
    parser = argparse.ArgumentParser(
        prog="thai-talking-clock",
        description="Thai Talking Clock - Audio time announcement utility.",
    )
    parser.add_argument(
        "--time",
        type=str,
        help="Announce specific time in HH:MM:SS format (e.g. 09:05:07)",
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Announce current system time (default behavior when run without arguments)",
    )
    parser.add_argument(
        "--mp3-dir",
        type=str,
        help="Custom MP3 audio folder path",
    )
    parser.add_argument(
        "--player",
        type=str,
        help="Force specific audio player command (e.g. afplay, play, ffplay, mpv)",
    )
    parser.add_argument(
        "--list-players",
        action="store_true",
        help="List detected system player and candidates for current OS",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify all 65 required MP3 files in mp3-thai-clock directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate time sequence without playing audio output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.1",
    )

    args = parser.parse_args()

    # List players option
    if args.list_players:
        player = SystemAudioPlayer(preferred_player=args.player, allow_dummy=True)
        print("=" * 60)
        print(f"AUDIO PLAYER DETECTION SUMMARY (OS: {player.os_type.upper()})")
        print("=" * 60)
        detected = player.detected_player
        print(f"Active Selected Player: {detected['name']} ({detected['description']})")
        print(f"Binary Path:            {detected['binary']}")
        print(f"Command Template:       {detected['binary']} {' '.join(detected['args'])}\n")
        print("Supported Player Candidates for this OS:")
        for idx, cand in enumerate(player.get_supported_players(), 1):
            import shutil
            found_path = shutil.which(cand["binary"])
            status = f"AVAILABLE ({found_path})" if found_path else "NOT FOUND"
            print(f"  {idx}. [{cand['name']}] -> {status}")
        print("=" * 60)
        return

    player = SystemAudioPlayer(preferred_player=args.player, allow_dummy=True)
    clock = TalkingClock(mp3_dir=args.mp3_dir, player=player)

    # Verify option
    if args.verify:
        print("=" * 60)
        print("VERIFYING MP3 AUDIO FILES")
        print("=" * 60)
        print(f"Target Directory: {clock.mp3_dir}")
        missing = clock.verify_files()
        if missing:
            print(f"❌ ERROR: Missing {len(missing)} audio files:")
            for f in missing:
                print(f"   - {f}")
            sys.exit(1)
        else:
            print("✅ SUCCESS: All 65 required MP3 files exist and are verified!")
            return

    # Announce target time or current system time
    if args.time:
        parts = args.time.split(":")
        if len(parts) != 3:
            print("Error: --time must be in HH:MM:SS format (e.g. 09:05:07)")
            sys.exit(1)
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        print(f"Evaluating time: {h:02d}:{m:02d}:{s:02d} (hour={h}, minute={m}, second={s})")
        seq = clock.get_sequence_for_time(h, m, s)
    else:
        now = datetime.now()
        print(f"Evaluating current system time: {now.strftime('%H:%M:%S')} (hour={now.hour}, minute={now.minute}, second={now.second})")
        seq = clock.get_current_time_sequence()

    print("\nGenerated Audio Sequence:")
    for idx, path in enumerate(seq, 1):
        print(f"  {idx}. {os.path.basename(path)}")

    if args.dry_run:
        print("\n[DRY RUN] Audio playback skipped.")
    else:
        print(f"\nPlaying audio via player: '{player.detected_player['name']}'...")
        clock.player.play_sequence(seq, blocking=True)
        print("✅ Done!")


if __name__ == "__main__":
    main()
