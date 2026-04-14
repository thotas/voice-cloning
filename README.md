# Voice Cloning & TTS System

Local voice cloning and text-to-speech system running on Mac Mini (Apple Silicon). Clone your voice from a short audio sample and generate natural speech — fully offline, no cloud, no API keys.

## What's Installed

Everything is already set up on this Mac Mini (M4, 24GB):

| Component | Location | Status |
|---|---|---|
| MLX Audio (Qwen3-TTS) | `~/.voice-cloning/venv/` | Installed |
| Qwen3-TTS 1.7B (voice cloning) | MLX model | Downloaded |
| OmniVoice (multilingual) | `~/.voice-cloning/venv/` | Installed |
| F5-TTS (voice prompting) | `~/.voice-cloning/venv/` | Installed |
| ffmpeg, git-lfs, sox | Homebrew | Installed |

## Quick Start

### Generate speech with your cloned voice

```bash
# Use the shell wrapper (simplest)
~/Development/Scripts/thota-voice-clone "Hello world"

# From a text file
~/Development/Scripts/thota-voice-clone /path/to/text.txt

# From markdown (strips formatting)
~/Development/Scripts/thota-voice-clone /path/to/file.md

# Play after generation
~/Development/Scripts/thota-voice-clone "Text" --play

# Use a different reference voice
~/Development/Scripts/thota-voice-clone "Text" --ref path/to/voice.wav

# Custom output path
~/Development/Scripts/thota-voice-clone "Text" --output /path/to/output.wav
```

Output goes to `/tmp/thota_voice_<timestamp>.wav`.

### Shell Wrapper Location

```
~/Development/Scripts/thota-voice-clone
```

## Scripts

### thota-voice-clone.py

**Recommended** — Generate TTS from text, files, or URLs. Supports:
- Direct text input
- `.txt` files
- `.md` files (strips markdown)
- `.html` files (strips HTML tags)

```bash
# Via shell wrapper (easiest)
~/Development/Scripts/thota-voice-clone "Your text here"
~/Development/Scripts/thota-voice-clone input.txt
~/Development/Scripts/thota-voice-clone /path/to/file.md
~/Development/Scripts/thota-voice-clone "Text" --play
~/Development/Scripts/thota-voice-clone "Text" --ref path/to/voice.wav

# Via python directly
~/.voice-cloning/venv/bin/python ~/.voice-cloning/scripts/thota-voice-clone.py "Text"
```

### tts-speak.sh

Generate TTS from text using MLX Qwen3-TTS (fast, English-focused):

```bash
~/.voice-cloning/scripts/tts-speak.sh "Your text here"
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --no-play          # Generate only
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --speed 1.2        # Adjust speed
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --ref voice.wav   # Different voice
~/.voice-cloning/scripts/tts-speak.sh "Telugu text" --engine omnivoice   # Multilingual
```

Options:
- `--ref <path>` — Reference voice audio (default: `thota-reference.wav`)
- `--engine qwen3|omnivoice` — TTS engine (default: `qwen3`)
- `--lang <language>` — Language for OmniVoice (auto-detect if omitted)
- `--speed <n>` — Speech speed multiplier
- `--no-play` — Save audio without playing

### batch-tts.py

Batch process a text file into audio clips:

```bash
source ~/.voice-cloning/venv/bin/activate
python ~/.voice-cloning/scripts/batch-tts.py input.txt
python ~/.voice-cloning/scripts/batch-tts.py input.txt --mode paragraph
python ~/.voice-cloning/scripts/batch-tts.py input.txt --concat
```

### record-voice.sh

Record a voice reference sample:

```bash
~/.voice-cloning/scripts/record-voice.sh
~/.voice-cloning/scripts/record-voice.sh my-sample  # Custom name
```

## TTS Engines

| Engine | Best For | Languages | Voice Cloning | Speed |
|---|---|---|---|---|
| **MLX Qwen3-TTS** | Natural narration | 10 (EN, ZH, JA, KO, etc.) | Yes (3s+ sample) | Fastest |
| **OmniVoice** | Multilingual + Indic | 600+ (Telugu, Hindi, etc.) | Yes (3-25s sample) | Medium |
| **F5-TTS** | Voice prompting | Multi | Yes (zero-shot) | Slow |

### Recommended engine by use case:
- **English TTS with voice cloning** → MLX Qwen3-TTS (fastest, best quality)
- **Telugu/Hindi/Indic languages** → OmniVoice
- **Quick voice prompting** → F5-TTS

## Reference Voices Available

| File | Duration | Description |
|---|---|---|
| `thota-reference.wav` | ~52s | Primary voice for cloning |
| `NarayanaThota-clean.wav` | ~9s | Dad's voice (Telugu) |

## Voice Samples Location

```
~/.voice-cloning/samples/
├── thota-reference.wav     # Your voice
├── NarayanaThota-clean.wav # Dad's voice
└── ...
```

## Generated Audio Location

```
/tmp/thota_voice_*.wav  # From thota-voice-clone.py
~/.voice-cloning/output/clips/  # From tts-speak.sh
```

## Remote Access (SSH)

From another machine:

```bash
ssh thota@macmini.local '~/Development/Scripts/thota-voice-clone "Text to speak"'
```

Requires SSH enabled: System Settings → General → Sharing → Remote Login.

## Privacy

All processing is 100% local. Voice samples and generated audio never leave the machine. No API keys or accounts required.

## Directory Layout

```
~/Development/Scripts/
└── thota-voice-clone          # Shell wrapper for TTS

~/.voice-cloning/
├── samples/               # Voice reference recordings
│   ├── thota-reference.wav
│   └── NarayanaThota-clean.wav
├── models/                # MLX/OmniVoice models
├── output/
│   ├── clips/             # TTS clips
│   └── audiobooks/
├── scripts/
│   ├── thota-voice-clone.py  # Main TTS script
│   ├── tts-speak.sh          # Shell wrapper
│   ├── batch-tts.py
│   ├── record-voice.sh
│   └── omnivoice-generate.py
└── venv/                  # Python virtualenv
```