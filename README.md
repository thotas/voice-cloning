# Voice Cloning & TTS System

Local voice cloning and text-to-speech system for Mac Mini (Apple Silicon). Clone your voice from a short audio sample and generate natural speech — fully offline, no cloud, no API keys.

## Stack

- **[MimikaStudio](https://github.com/BoltzmannEntropy/MimikaStudio)** — GUI + REST API + MCP server for voice cloning, TTS, and audiobook generation
- **[mlx-audio](https://github.com/Blaizzy/mlx-audio)** — CLI-based TTS using MLX (Metal GPU acceleration)
- **Qwen3-TTS 1.7B** — Voice cloning from a 3-second sample
- **Kokoro 82M** — Fast preset-voice TTS (<200ms latency)
- **Chatterbox** — Multilingual TTS with emotional control

## Requirements

| Component | Requirement |
|---|---|
| Mac | Apple Silicon (M1/M2/M3/M4) — Intel not supported |
| macOS | 14.0+ |
| RAM | 16GB minimum, 24GB recommended |
| Storage | ~10GB free for models + audio |
| Python | 3.12 (MimikaStudio), 3.14 works for mlx-audio |

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/thotas/voice-cloning.git
cd voice-cloning
```

### 2. Install system dependencies

```bash
brew install ffmpeg git-lfs espeak-ng sox python@3.12
git lfs install
```

### 3. Create directory structure

```bash
mkdir -p ~/.voice-cloning/{samples,models,output/clips,output/audiobooks,scripts}
```

### 4. Set up mlx-audio (CLI TTS)

```bash
python3 -m venv ~/.voice-cloning/venv
source ~/.voice-cloning/venv/bin/activate
pip install mlx-audio
```

### 5. Install MimikaStudio

```bash
git clone https://github.com/BoltzmannEntropy/MimikaStudio.git ~/MimikaStudio
cd ~/MimikaStudio

# Create venv with Python 3.12 (kokoro requires <3.13)
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install --no-deps chatterbox-tts==0.1.6
```

### 6. Download models (~7GB)

```bash
cd ~/.voice-cloning/models
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit

# Pull actual model weights (LFS)
for d in Qwen3-TTS-12Hz-1.7B-*; do cd "$d" && git lfs pull && cd ..; done
```

### 7. Record your voice

```bash
# Copy scripts to ~/.voice-cloning/scripts/
cp scripts/*.sh scripts/*.py ~/.voice-cloning/scripts/
chmod +x ~/.voice-cloning/scripts/*

# Record a 5-10 second sample (Ctrl+C to stop)
~/.voice-cloning/scripts/record-voice.sh
```

Tips: quiet room, normal pace, read 5-10 sentences steadily.

### 8. Generate speech

```bash
# CLI — speaks with your cloned voice
~/.voice-cloning/scripts/tts-speak.sh "Hello, this is my cloned voice."

# Or via MimikaStudio GUI
cd ~/MimikaStudio && source venv/bin/activate && python bin/mimika
```

## Scripts

| Script | Purpose |
|---|---|
| `tts-speak.sh` | Generate and play TTS from text using your cloned voice |
| `batch-tts.py` | Batch process a text file into multiple audio clips |
| `record-voice.sh` | Record a voice reference sample with quality checks |

### tts-speak.sh

```bash
./tts-speak.sh "Your text here"
./tts-speak.sh "Your text here" --no-play    # Generate only
./tts-speak.sh "Your text here" --speed 1.2  # Adjust speed
```

### batch-tts.py

```bash
python batch-tts.py input.txt                    # One line = one clip
python batch-tts.py input.txt --mode paragraph   # Split by blank lines
python batch-tts.py input.txt --concat           # Merge all into one file
```

## Directory Layout

```
~/.voice-cloning/
├── samples/               # Voice reference recordings
│   └── thota-reference.wav
├── models/                # Downloaded TTS models (~7GB)
├── output/
│   ├── clips/             # Short TTS clips
│   └── audiobooks/        # Full document conversions
├── scripts/               # CLI tools
└── venv/                  # Python virtualenv (mlx-audio)
```

## MimikaStudio REST API

```bash
# Voice clone TTS
curl -X POST http://127.0.0.1:8080/api/tts/clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Text to speak.",
    "reference_audio": "~/.voice-cloning/samples/thota-reference.wav",
    "model": "qwen3-tts-1.7b"
  }'

# Document to audiobook
curl -X POST http://127.0.0.1:8080/api/jobs/audiobook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "~/Documents/book.pdf",
    "voice_clone_ref": "~/.voice-cloning/samples/thota-reference.wav",
    "engine": "qwen3-tts"
  }'
```

## Performance

| Metric | Value |
|---|---|
| Voice cloning quality | >0.85 similarity from 3s sample |
| TTS latency (Kokoro) | <200ms |
| TTS latency (Qwen3 1.7B) | ~1-2s per sentence |
| RAM (Qwen3 1.7B) | ~3-4GB |
| RAM (Kokoro) | ~500MB |

## Privacy

All processing is 100% local. Voice samples and generated audio never leave the machine. No API keys or accounts required.
