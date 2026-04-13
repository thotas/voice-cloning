#!/bin/bash
# tts-speak.sh — Generate TTS audio from text using Thota's cloned voice, played locally
#
# Usage:
#   ./tts-speak.sh "Your text here"
#   ./tts-speak.sh "Your text here" --no-play          # Generate only, don't play
#   ./tts-speak.sh "Your text here" --speed 1.2        # Adjust speed
#   ./tts-speak.sh "Your text here" --max-tokens 2400  # Longer output (~200s)

set -euo pipefail

REF_AUDIO="${HOME}/.voice-cloning/samples/thota-reference.wav"
OUTPUT_DIR="${HOME}/.voice-cloning/output/clips"
VENV_DIR="${HOME}/.voice-cloning/venv"
MODEL="mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"

# Parse arguments
text=""
play_audio=true
speed=""
max_tokens=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-play)
            play_audio=false
            shift
            ;;
        --speed)
            speed="$2"
            shift 2
            ;;
        --max-tokens)
            max_tokens="$2"
            shift 2
            ;;
        *)
            if [[ -z "$text" ]]; then
                text="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$text" ]]; then
    echo "Usage: tts-speak.sh \"Your text here\" [--no-play] [--speed 1.0] [--max-tokens 1200]"
    exit 1
fi

if [[ ! -f "$REF_AUDIO" ]]; then
    echo "Error: Reference audio not found at $REF_AUDIO"
    echo "Record a 5-10 second voice sample first:"
    echo "  ffmpeg -f avfoundation -i \":0\" -ar 16000 -ac 1 -acodec pcm_s16le $REF_AUDIO"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Activate venv
source "${VENV_DIR}/bin/activate"

file_prefix="$(date +%s)"
output_file="${OUTPUT_DIR}/${file_prefix}.wav"

# Build command
cmd=(python -m mlx_audio.tts.generate
    --model "$MODEL"
    --text "$text"
    --ref_audio "$REF_AUDIO"
    --output_path "$OUTPUT_DIR"
    --file_prefix "$file_prefix"
    --join_audio)

if [[ -n "$speed" ]]; then
    cmd+=(--speed "$speed")
fi

if [[ -n "$max_tokens" ]]; then
    cmd+=(--max_tokens "$max_tokens")
fi

echo "Generating speech..."
"${cmd[@]}"

echo "Audio saved: $output_file"

if [[ "$play_audio" == true ]]; then
    afplay "$output_file"
fi
