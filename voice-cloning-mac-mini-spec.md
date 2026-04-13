# Local Voice Cloning & TTS System for Mac Mini
**Spec Version:** 1.0 | **Date:** 2026-04-13 | **Author:** Babu 🧡
**Audience:** Any AI coding agent | **Target Hardware:** Mac Mini (Apple Silicon, M-series)

---

## 1. Executive Summary

**Goal:** Clone Thota's voice from audio samples and generate natural TTS audio entirely on his Mac Mini — no cloud, no API keys, no subscription.

**Recommended Stack:** [MimikaStudio](https://github.com/BoltzmannEntropy/MimikaStudio) (primary) + [Qwen3-TTS via mlx-audio](https://github.com/kapi2800/qwen3-tts-apple-silicon) (CLI fallback).

**Why MimikaStudio:** It is a purpose-built macOS Apple Silicon app that unifies multiple TTS engines (Qwen3-TTS, Kokoro, Chatterbox) under one GUI with a REST API, MCP server, and document-to-audiobook pipeline. Zero cloud dependency. One install, full voice cloning + TTS + audiobook generation.

---

## 2. Hardware & System Requirements

| Component | Requirement |
|---|---|
| **Mac Mini** | Apple Silicon (M1/M2/M3/M4/M4 Pro) — Intel NOT supported |
| **macOS** | 26.4 or later |
| **RAM** | 16GB minimum, **24GB recommended** (M4 Pro) |
| **Storage** | 10GB free for models + audio files |
| **Network** | Required only for initial model downloads; fully offline afterwards |

> **M4 Pro note:** With 24GB unified memory, you can run Qwen3-TTS 1.7B (voice cloning) + Kokoro 82M simultaneously with room to spare. The M4's Neural Engine accelerates MLX inference significantly over M1/M2.

---

## 3. TTS Engine Comparison

| Engine | Model Size | Voice Cloning | Speed | Languages | Best For |
|---|---|---|---|---|---|
| **Qwen3-TTS 1.7B** | ~3.4GB (8-bit) | ✅ 3-second sample | Medium | 10 | Voice cloning, natural narration |
| **Qwen3-TTS 0.6B** | ~1.2GB (8-bit) | ✅ 3-second sample | Faster | 10 | Lighter cloning, faster iteration |
| **Kokoro 82M** | ~500MB | ❌ (preset voices only) | **Very fast** (<200ms) | English (BRP + US) | Daily consumption, speed-first |
| **Chatterbox** | ~2GB | ✅ | Medium | 23 | Multilingual, emotional control |

**Recommendation for Thota:**
- **Voice cloning:** Qwen3-TTS 1.7B (use 0.6B if 24GB+ RAM is not available)
- **Fast daily TTS (preset voices):** Kokoro 82M
- **Emotional/expressive control:** Chatterbox

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Mac Mini (Apple Silicon)              │
│                                                          │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────┐  │
│  │  MimikaStudio │   │  mlx-audio    │   │  Your CLI  │  │
│  │  GUI + API    │   │  (Qwen3 CLI) │   │  Scripts   │  │
│  └──────┬───────┘   └───────┬───────┘   └─────┬──────┘  │
│         │                   │                  │         │
│  ┌──────▼───────────────────▼──────────────────▼──────┐  │
│  │              MLX (Metal GPU Acceleration)          │  │
│  │   Qwen3-TTS 1.7B  │  Kokoro 82M  │  Chatterbox   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  Voice Samples: ~/.voice-cloning/samples/                 │
│  Generated Audio: ~/.voice-cloning/output/               │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Installation

### 5.1 Primary: Install MimikaStudio

```bash
# Clone the repository
git clone https://github.com/BoltzmannEntropy/MimikaStudio.git
cd MimikaStudio

# Run the install script (downloads models on first launch)
./install.sh

# Launch the app
open MimikaStudio.app
# OR via CLI:
./MimikaStudio
```

On first launch, MimikaStudio will prompt to download the TTS models. Accept all defaults.

**Models downloaded (~5GB total):**
- Qwen3-TTS-12Hz-1.7B-Base-8bit (voice cloning)
- Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit (preset voices + style control)
- Kokoro-82M ONNX
- Chatterbox (multilingual)
- Supertonic-2

### 5.2 Alternative/Companion: Qwen3-TTS CLI (mlx-audio)

```bash
# Install mlx-audio (Apple Silicon MLX TTS library)
pip install mlx-audio

# Download models from HuggingFace MLX Community
# Voice cloning model (1.7B):
git lfs install
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  ~/.voice-cloning/models/Qwen3-TTS-12Hz-1.7B-Base-8bit

# Voice design model:
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit \
  ~/.voice-cloning/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit

# CustomVoice preset model:
git clone https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit \
  ~/.voice-cloning/models/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit
```

### 5.3 Voice Sample Recording

Record 5–10 seconds of yourself speaking clearly:

```bash
# macOS: record via QuickTime or ffmpeg
ffmpeg -f avfoundation -i ":0" -ar 16000 -ac 1 -acodec pcm_s16le \
  ~/.voice-cloning/samples/thota-reference.wav
```

**Recording quality rules:**
- Quiet room, no background noise
- Read at natural pace, normal tone
- 5–10 seconds minimum
- WAV format, 16kHz, mono, 16-bit PCM
- Single speaker only (no overlapping voices)

**Good text to read:** Any 5–10 sentences. Consistency of tone matters more than content.

---

## 6. Voice Cloning Workflow

### 6.1 Via MimikaStudio (GUI)

1. Open MimikaStudio
2. Go to **AI Models → Voice Clone**
3. Upload `thota-reference.wav`
4. Type any text → click **Generate**
5. Adjust speed (0.8x–1.3x), emotion via style prompt
6. Export as WAV or MP3

### 6.2 Via MimikaStudio REST API

```bash
# Start the API server (MimikaStudio must be running)
# The app exposes http://127.0.0.1:8080/api

# Voice clone TTS via API
curl -X POST http://127.0.0.1:8080/api/tts/clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is my cloned voice reading this text aloud.",
    "reference_audio": "/Users/thota/.voice-cloning/samples/thota-reference.wav",
    "model": "qwen3-tts-1.7b",
    "speed": 1.0,
    "output": "/Users/thota/.voice-cloning/output/clip-001.wav"
  }'
```

### 6.3 Via mlx-audio CLI

```bash
# Activate venv
source ~/.voice-cloning/venv/bin/activate

# Voice cloning with Qwen3-TTS mlx
python -m mlx_audio.cli.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --text "Hello world, this is my cloned voice." \
  --ref_audio /Users/thota/.voice-cloning/samples/thota-reference.wav \
  --ref_text "The reference audio transcript goes here." \
  --output generated.wav

# Voice design (create voice from description, no sample needed)
python -m mlx_audio.cli.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit \
  --text "Deep narrator voice reading this calmly." \
  --voice_prompt "deep male narrator with a slight british accent" \
  --output generated.wav
```

---

## 7. Daily Consumption Workflows

### 7.1 Text-to-Speech CLI Script

```bash
#!/bin/bash
# tts-speak.sh — Generate TTS audio from text, played locally

REF_AUDIO="${HOME}/.voice-cloning/samples/thota-reference.wav"
OUTPUT_DIR="${HOME}/.voice-cloning/output"
MODEL="mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"

mkdir -p "$OUTPUT_DIR"

text="$1"
output_file="${OUTPUT_DIR}/$(date +%s).wav"

python -m mlx_audio.cli.tts.generate \
  --model "$MODEL" \
  --text "$text" \
  --ref_audio "$REF_AUDIO" \
  --output "$output_file" \
  && afplay "$output_file"  # macOS native audio player
```

Usage:
```bash
./tts-speak.sh "Your daily briefing starts now. Weather is sunny, 72 degrees."
```

### 7.2 Document to Audiobook Pipeline

```bash
# Convert a PDF/EPUB/DOCX to audiobook using Thota's cloned voice
# Via MimikaStudio GUI:
# 1. Open MimikaStudio
# 2. Select "Audiobook Creator"
# 3. Import document
# 4. Select cloned voice preset
# 5. Click Generate

# Via MimikaStudio jobs API:
curl -X POST http://127.0.0.1:8080/api/jobs/audiobook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "/Users/thota/Documents/book.pdf",
    "voice_clone_ref": "/Users/thota/.voice-cloning/samples/thota-reference.wav",
    "engine": "qwen3-tts",
    "speed": 1.0,
    "output_dir": "/Users/thota/.voice-cloning/output/audiobooks/"
  }'
```

### 7.3 Batch TTS via MCP Server (for AI coding agents)

MimikaStudio exposes an MCP server with 50+ tools. Any MCP-compatible AI (Claude Code, Codex) can call TTS generation directly:

```json
// Claude Code / Codex can call these tools via MCP:
{
  "tool": "mimika_clone_voice",
  "params": {
    "reference_audio": "/Users/thota/.voice-cloning/samples/thota-reference.wav",
    "text": "Hello, this is Thota speaking."
  }
}
{
  "tool": "mimika_tts_preset",
  "params": {
    "text": "Quick reminder: standup meeting in 10 minutes.",
    "voice": "alastair",
    "speed": 1.2
  }
}
```

---

## 8. Directory Structure

```
~/.voice-cloning/
├── samples/                  # Voice reference recordings
│   └── thota-reference.wav   # 5–10 second sample
├── models/                   # Downloaded MLX/ONNX models
│   ├── Qwen3-TTS-12Hz-1.7B-Base-8bit/
│   ├── Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit/
│   └── Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit/
├── output/                    # Generated audio
│   ├── clips/                # Short TTS clips
│   └── audiobooks/           # Full document conversions
├── scripts/
│   ├── tts-speak.sh          # CLI TTS script
│   └── batch-tts.py          # Python batch processor
└── venv/                     # Python virtualenv (mlx-audio)
```

---

## 9. Memory & Performance Targets

| Metric | Target | Notes |
|---|---|---|
| Voice cloning quality | 3-second sample, >0.85 similarity | Qwen3-TTS 1.7B |
| TTS latency (Kokoro) | <200ms | Real-time interaction |
| TTS latency (Qwen3 1.7B) | ~1–2s per sentence | High quality, batch OK |
| RAM usage (Qwen3 1.7B) | ~3–4GB | MLX 8-bit quantization |
| RAM usage (Kokoro) | ~500MB | ONNX, very lightweight |
| Storage for models | ~5GB | All engines + extras |
| Concurrent operation | Voice clone + Kokoro | M4 Pro 24GB can handle both |

---

## 10. Security & Privacy

- **100% local:** All audio processing happens on the Mac Mini. No network requests after model downloads.
- **Voice data stays local:** Reference samples and generated audio never leave the machine.
- **No API keys:** Neither MimikaStudio nor mlx-audio require any external API credentials.
- **File permissions:** Ensure `~/.voice-cloning/samples/` is not shared or backed up to cloud services.

---

## 11. Troubleshooting

| Problem | Solution |
|---|---|
| `mlx_audio not found` | Run `source venv/bin/activate` first |
| Model not found | Check folder names match exactly (case-sensitive) |
| Audio won't play | `afplay output.wav` or check macOS sound output |
| MimikaStudio crashes on launch | Update to latest release; check macOS 26.4+ |
| Qwen3-TTS produces garbled output | Reference audio may be too short or noisy; try 10+ seconds |
| Out of memory | Switch to 0.6B model, or close other apps |
| Slow inference on M1/M2 | Normal — M3/M4 significantly faster; use Kokoro for speed |

---

## 12. macOS-Specific Notes

- **No Homebrew required** for MimikaStudio (standalone app)
- **ffmpeg** needed for mlx-audio CLI: `brew install ffmpeg`
- **GPU acceleration:** MLX uses Metal automatically — no manual GPU configuration
- **Battery/thermal:** Qwen3-TTS on M4 MacBook Air (fanless) runs at 40–50°C vs 80–90°C on standard PyTorch
- **Audio output:** Use `afplay` for local playback, or any macOS audio app

---

## 13. Integration with Babu (Babu on VPS)

Once Thota's Mac Mini is set up, Babu can:
1. **Send text** to the Mac Mini via SSH + the `tts-speak.sh` script
2. **Trigger audiobook generation** via the MimikaStudio REST API
3. **Read TTS clips** back via a connected audio channel

Example remote invocation:
```bash
# Babu sends this command to Mac Mini via SSH
ssh thota@macmini.local 'bash /Users/thota/.voice-cloning/scripts/tts-speak.sh \
  "Your dividend alert: AAPL dividend of \$0.26 per share pays tomorrow."'
```

> **Note:** Thota's Mac Mini needs SSH enabled (System Settings → General → Sharing → Remote Login). Babu can store the SSH key for passwordless access.

---

## 14. Quick-Start Summary (for AI coding agents)

```
Day 1 — Setup:
1. git clone https://github.com/BoltzmannEntropy/MimikaStudio.git && ./install.sh
2. brew install ffmpeg
3. pip install mlx-audio
4. Record 5–10s voice sample → ~/.voice-cloning/samples/thota-reference.wav

Day 1 — Test:
5. open MimikaStudio → Voice Clone → upload sample → generate test clip
6. python -m mlx_audio.cli.tts.generate --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
     --text "Hello, my name is Thota." --ref_audio ~/.voice-cloning/samples/thota-reference.wav

Day 2+ — Daily Use:
7. ./tts-speak.sh "Your briefing text here"
8. MimikaStudio → Audiobook Creator → import doc → generate
```

---

## 15. Key Resources

| Resource | URL |
|---|---|
| MimikaStudio (main app) | https://github.com/BoltzmannEntropy/MimikaStudio |
| MimikaStudio docs | https://boltzmannentropy.github.io/mimikastudio.github.io/ |
| Qwen3-TTS Apple Silicon (mlx) | https://github.com/kapi2800/qwen3-tts-apple-silicon |
| MLX Audio (mlx-audio library) | https://github.com/Blaizzy/mlx-audio |
| Qwen3-TTS HuggingFace | https://huggingface.co/QwenLM/Qwen3-TTS |
| Kokoro TTS ONNX | https://github.com/hexgrad/kokoro |
| Whisper.cpp (STT, optional) | https://github.com/ggerganov/whisper.cpp |

---

*Spec prepared by Babu 🧡 for Thota — 2026-04-13*
