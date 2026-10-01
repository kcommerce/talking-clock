#!/usr/bin/env python3
"""Example script showing how to use the talking_clock Python library."""

from talking_clock import TalkingClock, SystemAudioPlayer, announce_current_time

def main():
    print("--- Talking Clock Library Usage Example ---\n")

    # 1. Quick convenience function to announce current time:
    # announce_current_time()

    # 2. Instantiate clock with auto-detected player:
    clock = TalkingClock(mp3_dir="mp3-thai-clock")

    # Display detected player info:
    player_info = clock.player.detected_player
    print(f"Detected OS Audio Player: {player_info['name']} ({player_info['binary']})")

    # 3. Generate MP3 sequence for 09:05:07
    h, m, s = 9, 5, 7
    seq = clock.get_sequence_for_time(h, m, s)

    print(f"\nSequence for {h:02d}:{m:02d}:{s:02d}:")
    for f in seq:
        print(f"  - {f}")

    # 4. Announce custom time
    print("\nAnnouncing 09:05:07...")
    clock.announce_time(hour=9, minute=5, second=7, blocking=True)
    print("Done!")

if __name__ == "__main__":
    main()
