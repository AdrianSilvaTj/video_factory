"""Generate a Colombian Spanish neural voice and normalize it to the pipeline WAV."""
from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--voice", default="es-CO-GonzaloNeural")
    parser.add_argument("--rate", default="-4%")
    parser.add_argument("--pitch", default="-1Hz")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root / "data" / "tts-packages"))
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("Falta edge-tts. Instala las dependencias de voz del proyecto.") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    async def generate() -> None:
        communicate = edge_tts.Communicate(
            args.text,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            volume="+0%",
        )
        await communicate.save(str(args.output))

    asyncio.run(generate())
    wav_path = args.output.with_suffix(".wav")
    proc = subprocess.run(
        [args.ffmpeg, "-y", "-i", str(args.output), "-vn", "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", str(wav_path)],
        capture_output=True, text=True, timeout=90,
    )
    if proc.returncode or not wav_path.is_file():
        raise RuntimeError(proc.stderr[-1600:] or "FFmpeg no pudo convertir la voz neural a WAV.")
    print(f"VOICE_NAME={args.voice}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error al sintetizar la voz neural: {exc}", file=sys.stderr)
        raise SystemExit(2)
