"""Genera assets/video_factory.ico (varios tamaños) y assets/video_factory.png con el logo de Video Factory.

Uso (desde la raíz del proyecto):
    video_factory\\.venv\\Scripts\\python.exe assets\\make_icon.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF

SIZES = (16, 24, 32, 48, 64, 128, 256)
HERE = Path(__file__).resolve().parent


def draw(size: int) -> QImage:
    """Draw the logo: violet-to-blue squircle, a white 9:16 frame and a play triangle with a scene timeline."""
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
    s = float(size)

    background = QLinearGradient(0, 0, s, s)
    background.setColorAt(0.0, QColor("#7C3AED"))
    background.setColorAt(1.0, QColor("#0EA5E9"))
    tile = QPainterPath()
    tile.addRoundedRect(QRectF(s * 0.03, s * 0.03, s * 0.94, s * 0.94), s * 0.22, s * 0.22)
    p.fillPath(tile, QBrush(background))

    gloss = QLinearGradient(0, 0, 0, s * 0.55)
    gloss.setColorAt(0.0, QColor(255, 255, 255, 70))
    gloss.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.save()
    p.setClipPath(tile)
    p.fillRect(QRectF(0, 0, s, s * 0.55), QBrush(gloss))
    p.restore()

    frame_w, frame_h = s * 0.40, s * 0.40 * 16 / 9
    frame = QRectF((s - frame_w) / 2, s * 0.13, frame_w, frame_h)
    shadow = QPainterPath()
    shadow.addRoundedRect(frame.translated(0, s * 0.025), s * 0.07, s * 0.07)
    p.fillPath(shadow, QColor(20, 10, 60, 70))
    body = QPainterPath()
    body.addRoundedRect(frame, s * 0.07, s * 0.07)
    p.fillPath(body, QColor("white"))

    cx, cy, r = frame.center().x(), frame.center().y() - s * 0.03, s * 0.095
    play = QPolygonF([QPointF(cx - r * 0.7, cy - r), QPointF(cx - r * 0.7, cy + r), QPointF(cx + r * 1.1, cy)])
    mark = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
    mark.setColorAt(0.0, QColor("#7C3AED"))
    mark.setColorAt(1.0, QColor("#0EA5E9"))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(mark))
    p.drawPolygon(play)

    if size >= 48:
        bar_y, bar_h, gap = frame.bottom() - s * 0.085, s * 0.03, s * 0.012
        inner = frame.width() - s * 0.10
        widths = (0.42, 0.26, 0.32)
        x = frame.left() + s * 0.05
        colors = ("#7C3AED", "#0EA5E9", "#A78BFA")
        for fraction, color in zip(widths, colors):
            w = (inner - 2 * gap) * fraction
            p.setBrush(QColor(color))
            p.drawRoundedRect(QRectF(x, bar_y, w, bar_h), bar_h / 2, bar_h / 2)
            x += w + gap
    p.end()
    return image


def png_bytes(image: QImage) -> bytes:
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def write_ico(path: Path, images: list[QImage]) -> None:
    """Write a multi-size .ico whose entries are PNG-compressed (supported since Windows Vista)."""
    payloads = [png_bytes(image) for image in images]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    for image, payload in zip(images, payloads):
        side = image.width() % 256  # 256 is stored as 0
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(payload), offset)
        offset += len(payload)
    path.write_bytes(header + entries + b"".join(payloads))


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    images = [draw(size) for size in SIZES]
    write_ico(HERE / "video_factory.ico", images)
    images[-1].save(str(HERE / "video_factory.png"))
    print("Iconos generados en", HERE)
