#!/usr/bin/env python3
"""Generate TTS audio using OmniVoice with voice cloning support for 600+ languages."""

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from omnivoice import OmniVoice, OmniVoiceGenerationConfig


def main():
    parser = argparse.ArgumentParser(description="OmniVoice TTS with voice cloning")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--ref_audio", required=True, help="Reference voice audio file")
    parser.add_argument("--output", required=True, help="Output WAV file path")
    parser.add_argument("--language", default=None, help="Language code (auto-detect if omitted)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Sampling temperature (lower=more stable, 0.1-1.0)")
    parser.add_argument("--top-p", type=float, default=0.9,
                        help="Nucleus sampling threshold (0.8-0.95 recommended for voice cloning)")
    parser.add_argument("--guidance-scale", type=float, default=2.0,
                        help="Classifier-free guidance scale (higher=stronger voice conditioning, 2.0-5.0)")
    parser.add_argument("--num-steps", type=int, default=32,
                        help="Number of diffusion steps (more steps=higher quality but slower)")
    parser.add_argument("--target-sr", type=int, default=None,
                        help="Target sample rate for output (default: model's native rate)")
    args = parser.parse_args()

    ref_path = Path(args.ref_audio)
    if not ref_path.exists():
        print(f"Error: Reference audio not found: {ref_path}", file=sys.stderr)
        sys.exit(1)

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Loading OmniVoice on {device}...")

    model = OmniVoice.from_pretrained(
        "k2-fsa/OmniVoice",
        device_map=device,
        dtype=torch.float16,
        load_asr=False,
    )

    gen_config = OmniVoiceGenerationConfig(
        num_step=args.num_steps,
        guidance_scale=args.guidance_scale,
        denoise=True,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    voice_prompt = model.create_voice_clone_prompt(ref_audio=str(ref_path))

    kw = dict(
        text=args.text,
        voice_clone_prompt=voice_prompt,
        generation_config=gen_config,
    )
    if args.language:
        kw["language"] = args.language
    if args.speed != 1.0:
        kw["speed"] = args.speed

    print("Generating speech...")
    audio = model.generate(**kw)

    waveform = (audio[0] * 32767).astype(np.int16)

    # Resample if target_sr specified
    if args.target_sr is not None and args.target_sr != model.sampling_rate:
        from scipy import signal
        orig_sr = model.sampling_rate
        target_sr = args.target_sr
        print(f"Resampling from {orig_sr} to {target_sr} Hz...")
        waveform_np = waveform.astype(np.float64)
        resampled = signal.resample_poly(waveform_np, target_sr, orig_sr)
        waveform = resampled.astype(np.int16)
        write_sr = target_sr
    else:
        write_sr = model.sampling_rate

    sf.write(args.output, waveform, write_sr)
    print(f"Audio saved: {args.output}")


if __name__ == "__main__":
    main()
