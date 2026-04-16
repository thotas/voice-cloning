#!/bin/bash
# tts-speak.sh — Generate TTS audio from text using Thota's cloned voice, played locally
#
# Usage:
#   ./tts-speak.sh "Your text here"
#   ./tts-speak.sh "Your text here" --no-play          # Generate only, don't play
#   ./tts-speak.sh "Your text here" --speed 1.2        # Adjust speed
#   ./tts-speak.sh "Your text here" --max-tokens 2400  # Longer output (~200s)
#   ./tts-speak.sh "Your text here" --ref ~/samples/other-voice.wav  # Use different voice
#   ./tts-speak.sh "Telugu text" --engine omnivoice                 # Use OmniVoice (600+ langs)

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
engine="qwen3"
language=""
temperature=""
top_p=""
guidance_scale=""
num_steps=""
target_sr=""

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
        --ref)
            REF_AUDIO="$2"
            shift 2
            ;;
        --engine)
            engine="$2"
            shift 2
            ;;
        --lang)
            language="$2"
            shift 2
            ;;
        --temp)
            temperature="$2"
            shift 2
            ;;
        --top-p)
            top_p="$2"
            shift 2
            ;;
        --guide)
            guidance_scale="$2"
            shift 2
            ;;
        --steps)
            num_steps="$2"
            shift 2
            ;;
        --target-sr)
            target_sr="$2"
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
    echo "Usage: tts-speak.sh \"Your text here\" [--no-play] [--speed 1.0] [--max-tokens 1200] [--ref voice.wav] [--engine qwen3|omnivoice] [--lang telugu]"
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

echo "Generating speech..."

if [[ "$engine" == "omnivoice" ]]; then
    # OmniVoice: 600+ languages including Telugu
    cmd=(python "${HOME}/.voice-cloning/scripts/omnivoice-generate.py"
        --text "$text"
        --ref_audio "$REF_AUDIO"
        --output "$output_file")

    if [[ -n "$speed" ]]; then
        cmd+=(--speed "$speed")
    fi

    if [[ -n "$language" ]]; then
        cmd+=(--language "$language")
    fi

    if [[ -n "$temperature" ]]; then
        cmd+=(--temperature "$temperature")
    fi

    if [[ -n "$top_p" ]]; then
        cmd+=(--top-p "$top_p")
    fi

    if [[ -n "$guidance_scale" ]]; then
        cmd+=(--guidance-scale "$guidance_scale")
    fi

    if [[ -n "$num_steps" ]]; then
        cmd+=(--num-steps "$num_steps")
    fi

    if [[ -n "$target_sr" ]]; then
        cmd+=(--target-sr "$target_sr")
    fi

    "${cmd[@]}"
else
    # Qwen3-TTS (default): 10 languages, MLX-native
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

    "${cmd[@]}"
fi

echo "Audio saved: $output_file"

if [[ "$play_audio" == true ]]; then
    afplay "$output_file"
fi
