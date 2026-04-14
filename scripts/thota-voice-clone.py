#!/usr/bin/env python3
"""
thota-voice-clone.py — Generate TTS audio using your cloned voice

Usage:
    thota-voice-clone "Hello, this is my voice"
    thota-voice-clone /path/to/text.txt
    thota-voice-clone /path/to/file.html
    thota-voice-clone /path/to/file.md

Output: /tmp/thota_voice_<timestamp>.wav

Supports:
    - Direct text input
    - .txt files
    - .md files (strips markdown formatting)
    - .html files (strips HTML tags)
"""

import argparse
import re
import subprocess
import sys
import tempfile
import os
from datetime import datetime

VENV_PYTHON = os.path.expanduser("~/.voice-cloning/venv/bin/python")
DEFAULT_REF = os.path.expanduser("~/.voice-cloning/samples/thota-reference.wav")
MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    return text.strip()


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    # Remove script and style elements
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    # Remove HTML comments
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # Remove tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def read_input(source: str) -> str:
    """Read text from string, file path, or URL."""
    if os.path.isfile(source):
        ext = source.lower().split('.')[-1]
        with open(source, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if ext == 'html':
            return strip_html(content)
        elif ext == 'md':
            return strip_markdown(content)
        elif ext == 'txt':
            return content.strip()
        else:
            # Try to detect format from content
            if content.strip().startswith('<') and '</' in content:
                return strip_html(content)
            elif content.strip().startswith('#'):
                return strip_markdown(content)
            return content.strip()
    else:
        # Direct text string
        return source.strip()


def generate_tts(text: str, ref_audio: str, output_path: str) -> bool:
    """Generate TTS using MLX Qwen3-TTS."""
    cmd = [
        VENV_PYTHON, "-m", "mlx_audio.tts.generate",
        "--model", MODEL,
        "--text", text,
        "--ref_audio", ref_audio,
        "--output_path", "/tmp",
        "--file_prefix", os.path.basename(output_path).replace('.wav', ''),
        "--join_audio",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return False

    # Move to desired output path
    generated = f"/tmp/{os.path.basename(output_path).replace('.wav', '')}.wav"
    if os.path.exists(generated):
        if generated != output_path:
            os.rename(generated, output_path)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate TTS audio using your cloned voice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    thota-voice-clone "Hello, this is my voice"
    thota-voice-clone /path/to/text.txt
    thota-voice-clone /path/to/file.html
    thota-voice-clone /path/to/file.md --ref ~/.voice-cloning/samples/other-voice.wav
        """
    )
    parser.add_argument("input", help="Text, .txt, .md, .html file, or file path")
    parser.add_argument("--ref", default=DEFAULT_REF, help=f"Reference audio (default: {DEFAULT_REF})")
    parser.add_argument("--output", help="Output WAV path (default: /tmp/thota_voice_<timestamp>.wav)")
    parser.add_argument("--play", action="store_true", help="Play audio after generation")

    args = parser.parse_args()

    if not os.path.exists(args.ref):
        print(f"Error: Reference audio not found: {args.ref}", file=sys.stderr)
        sys.exit(1)

    # Read text from input
    text = read_input(args.input)
    if not text:
        print("Error: No text content found", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/thota_voice_{timestamp}.wav"

    print(f"Generating TTS...")
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")

    if generate_tts(text, args.ref, output_path):
        print(f"Output: {output_path}")
        duration = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1", output_path],
            capture_output=True, text=True
        )
        if duration.returncode == 0:
            dur = duration.stdout.strip().replace('duration=', '')
            print(f"Duration: {float(dur):.2f}s")

        if args.play:
            subprocess.run(["afplay", output_path])
    else:
        print("Error: Generation failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()