#!/usr/bin/env python3
"""
batch-tts.py — Batch text-to-speech processor using Qwen3-TTS voice cloning.

Reads text from a file (one utterance per line, or paragraphs separated by blank lines)
and generates audio for each segment using Thota's cloned voice.

Usage:
    python batch-tts.py input.txt
    python batch-tts.py input.txt --output-dir ~/audiobooks
    python batch-tts.py input.txt --mode paragraph
    python batch-tts.py input.txt --concat  # Concatenate all segments into one file
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_REF_AUDIO = Path.home() / ".voice-cloning" / "samples" / "thota-reference.wav"
DEFAULT_OUTPUT_DIR = Path.home() / ".voice-cloning" / "output" / "clips"
DEFAULT_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"


def split_text(text: str, mode: str) -> list[str]:
    """Split input text into segments based on mode."""
    if mode == "line":
        return [line.strip() for line in text.splitlines() if line.strip()]
    elif mode == "paragraph":
        paragraphs = text.split("\n\n")
        return [p.strip().replace("\n", " ") for p in paragraphs if p.strip()]
    else:
        raise ValueError(f"Unknown mode: {mode}")


def generate_segment(
    text: str,
    output_path: Path,
    ref_audio: Path,
    model: str,
    speed: float | None = None,
) -> bool:
    """Generate TTS audio for a single text segment. Returns True on success."""
    cmd = [
        sys.executable, "-m", "mlx_audio.cli.tts.generate",
        "--model", model,
        "--text", text,
        "--ref_audio", str(ref_audio),
        "--output", str(output_path),
    ]
    if speed is not None:
        cmd.extend(["--speed", str(speed)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def concatenate_wav_files(wav_files: list[Path], output_path: Path) -> None:
    """Concatenate multiple WAV files into one using ffmpeg."""
    if not wav_files:
        return

    # Create a file list for ffmpeg
    list_file = output_path.parent / ".concat_list.txt"
    with open(list_file, "w") as f:
        for wav in wav_files:
            f.write(f"file '{wav}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c", "copy", str(output_path)],
        capture_output=True, text=True,
    )
    list_file.unlink(missing_ok=True)
    print(f"\nConcatenated output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Batch TTS with voice cloning")
    parser.add_argument("input_file", help="Text file to process")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for generated audio")
    parser.add_argument("--ref-audio", type=Path, default=DEFAULT_REF_AUDIO,
                        help="Reference voice audio file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="TTS model to use")
    parser.add_argument("--mode", choices=["line", "paragraph"], default="line",
                        help="How to split input text (default: line)")
    parser.add_argument("--speed", type=float, default=None, help="Speech speed")
    parser.add_argument("--concat", action="store_true",
                        help="Concatenate all segments into one output file")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not args.ref_audio.exists():
        print(f"Error: Reference audio not found: {args.ref_audio}", file=sys.stderr)
        print("Record a 5-10 second voice sample first.", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text()
    segments = split_text(text, args.mode)

    if not segments:
        print("No text segments found in input file.")
        sys.exit(0)

    print(f"Processing {len(segments)} segment(s) from {input_path.name}")
    print(f"Model: {args.model}")
    print(f"Reference: {args.ref_audio}")
    print()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    batch_id = int(time.time())
    generated_files: list[Path] = []

    for i, segment in enumerate(segments, 1):
        preview = segment[:60] + "..." if len(segment) > 60 else segment
        print(f"[{i}/{len(segments)}] \"{preview}\"")

        output_path = args.output_dir / f"batch-{batch_id}-{i:03d}.wav"
        success = generate_segment(
            segment, output_path, args.ref_audio, args.model, args.speed
        )
        if success:
            generated_files.append(output_path)
            print(f"  -> {output_path}")
        else:
            print(f"  -> FAILED, skipping")

    print(f"\nDone: {len(generated_files)}/{len(segments)} segments generated")

    if args.concat and generated_files:
        concat_output = args.output_dir / f"batch-{batch_id}-full.wav"
        concatenate_wav_files(generated_files, concat_output)


if __name__ == "__main__":
    main()
