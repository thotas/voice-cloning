#!/bin/bash
# record-voice.sh — Record a voice reference sample for voice cloning
#
# Usage:
#   ./record-voice.sh              # Records to default location
#   ./record-voice.sh my-sample    # Records to samples/my-sample.wav
#
# Press Ctrl+C to stop recording. Aim for 5-10 seconds of clear speech.

set -euo pipefail

SAMPLES_DIR="${HOME}/.voice-cloning/samples"
mkdir -p "$SAMPLES_DIR"

name="${1:-thota-reference}"
output="${SAMPLES_DIR}/${name}.wav"

if [[ -f "$output" ]]; then
    echo "Warning: $output already exists."
    read -p "Overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "=== Voice Recording ==="
echo ""
echo "Tips for best results:"
echo "  - Quiet room, no background noise"
echo "  - Normal speaking pace and tone"
echo "  - Read 5-10 sentences steadily"
echo "  - Hold mic at consistent distance"
echo ""
echo "Output: $output"
echo "Format: 16kHz, mono, 16-bit PCM WAV"
echo ""
echo "Press ENTER to start recording, then Ctrl+C to stop."
read -r

echo "Recording... (Ctrl+C to stop)"
ffmpeg -f avfoundation -i ":0" -ar 16000 -ac 1 -acodec pcm_s16le "$output" 2>/dev/null

echo ""
echo "Saved: $output"

# Show duration
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$output" 2>/dev/null)
if [[ -n "$duration" ]]; then
    printf "Duration: %.1f seconds\n" "$duration"
    dur_int=${duration%.*}
    if [[ "$dur_int" -lt 3 ]]; then
        echo "Warning: Recording is very short. Aim for at least 5 seconds."
    elif [[ "$dur_int" -lt 5 ]]; then
        echo "Note: Recording is short. 5-10 seconds recommended for best cloning quality."
    else
        echo "Good length for voice cloning."
    fi
fi
