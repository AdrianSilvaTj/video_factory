"""Split an AI-generated 2x3 contact sheet into five 9:16 scene stills."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("prefix")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(args.source) as sheet:
        sheet = sheet.convert("RGB")
        sheet_w, sheet_h = sheet.size
        cell_w, cell_h = sheet_w // 2, sheet_h // 3
        if sheet_w % 2 or sheet_h % 3:
            raise ValueError(f"La hoja {sheet.size} no se divide uniformemente en 2x3.")
        crop_w = round(cell_h * 9 / 16)
        for i in range(5):
            row, col = divmod(i, 2)
            x0, y0 = col * cell_w, row * cell_h
            xcenter = x0 + cell_w // 2
            left = xcenter - crop_w // 2
            still = sheet.crop((left, y0, left + crop_w, y0 + cell_h))
            still = still.resize((1080, 1920), Image.Resampling.LANCZOS)
            still.save(args.output_dir / f"{args.prefix}-{i + 1:02d}.png", optimize=True)
    print(f"Generadas cinco imágenes verticales en {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
