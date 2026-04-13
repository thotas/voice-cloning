# Voice Cloning & TTS System

Local voice cloning and text-to-speech system running on Mac Mini (Apple Silicon). Clone your voice from a short audio sample and generate natural speech — fully offline, no cloud, no API keys.

## What's Installed

Everything is already set up on this Mac Mini (M4, 24GB):

| Component | Location | Status |
|---|---|---|
| MimikaStudio (GUI + API) | `~/MimikaStudio/` | Installed (Python 3.12 venv) |
| mlx-audio (CLI TTS) | `~/.voice-cloning/venv/` | Installed (Python 3.14 venv) |
| Qwen3-TTS 1.7B Base (voice cloning) | `~/.voice-cloning/models/` | Downloaded (2.3GB) |
| Qwen3-TTS 1.7B VoiceDesign | `~/.voice-cloning/models/` | Downloaded (2.2GB) |
| Qwen3-TTS 1.7B CustomVoice | `~/.voice-cloning/models/` | Downloaded (2.2GB) |
| ffmpeg, git-lfs, espeak-ng, sox | Homebrew | Installed |

## Getting Started

### 1. Record your voice

Record a 5-10 second sample in a quiet room, speaking at a natural pace:

```bash
~/.voice-cloning/scripts/record-voice.sh
```

Press Enter to start, Ctrl+C to stop. The script saves to `~/.voice-cloning/samples/thota-reference.wav`.

### 2. Generate speech with your cloned voice

```bash
~/.voice-cloning/scripts/tts-speak.sh "Hello, this is my cloned voice speaking."
```

### 3. Or use MimikaStudio GUI

```bash
cd ~/MimikaStudio && source venv/bin/activate && python bin/mimika
```

Then: AI Models → Voice Clone → upload your sample → type text → Generate.

## Scripts

All scripts are in `~/.voice-cloning/scripts/` and ready to use.

### tts-speak.sh

Generate and play TTS from text using your cloned voice:

```bash
~/.voice-cloning/scripts/tts-speak.sh "Your text here"
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --no-play          # Generate only
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --speed 1.2        # Adjust speed
~/.voice-cloning/scripts/tts-speak.sh "Your text here" --max-tokens 2400  # Longer output (~200s)
```

Default `--max-tokens` is 1200 (~100s of audio at 12Hz). Increase for longer text passages. For best quality on long content, consider splitting into paragraph-sized chunks.

### batch-tts.py

Batch process a text file into audio clips:

```bash
source ~/.voice-cloning/venv/bin/activate
python ~/.voice-cloning/scripts/batch-tts.py input.txt                    # One line = one clip
python ~/.voice-cloning/scripts/batch-tts.py input.txt --mode paragraph   # Split by blank lines
python ~/.voice-cloning/scripts/batch-tts.py input.txt --concat           # Merge into one file
```

### record-voice.sh

Record a voice reference sample with duration check and quality tips:

```bash
~/.voice-cloning/scripts/record-voice.sh              # Default: thota-reference.wav
~/.voice-cloning/scripts/record-voice.sh my-sample    # Custom name
```

## MimikaStudio REST API

Start MimikaStudio, then use the API at `http://127.0.0.1:8080/api`:

```bash
# Voice clone TTS
curl -X POST http://127.0.0.1:8080/api/tts/clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Text to speak.",
    "reference_audio": "/Users/thota/.voice-cloning/samples/thota-reference.wav",
    "model": "qwen3-tts-1.7b"
  }'

# Document to audiobook
curl -X POST http://127.0.0.1:8080/api/jobs/audiobook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "/Users/thota/Documents/book.pdf",
    "voice_clone_ref": "/Users/thota/.voice-cloning/samples/thota-reference.wav",
    "engine": "qwen3-tts"
  }'
```

## Directory Layout

```
~/.voice-cloning/
├── samples/               # Voice reference recordings
│   └── thota-reference.wav
├── models/                # Qwen3-TTS models (~7GB)
├── output/
│   ├── clips/             # Short TTS clips
│   └── audiobooks/        # Full document conversions
├── scripts/               # CLI tools
└── venv/                  # Python virtualenv (mlx-audio)
```

## TTS Engines

| Engine | Best For | Latency | Voice Cloning |
|---|---|---|---|
| Qwen3-TTS 1.7B | Natural narration, voice cloning | ~1-2s/sentence | Yes (3s sample) |
| Kokoro 82M | Fast daily TTS, preset voices | <200ms | No |
| Chatterbox | Multilingual, emotional control | Medium | Yes |

## Remote Access (SSH)

From another machine (e.g., a VPS):

```bash
ssh thota@macmini.local 'bash ~/.voice-cloning/scripts/tts-speak.sh "Your text here."'
```

Requires SSH enabled: System Settings → General → Sharing → Remote Login.

## Privacy

All processing is 100% local. Voice samples and generated audio never leave the machine. No API keys or accounts required.
