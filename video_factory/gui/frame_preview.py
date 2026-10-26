"""Vista previa estática de un cuadro: encuadre y subtítulos tal como los dibuja el render (sin ejecutar FFmpeg)."""
from __future__ import annotations

import textwrap
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen, QPixmap

from ..project import caption_chunks, wrap_width_for

SAMPLE_TEXT = "Así se verán los subtítulos"
TOP_MARGIN = 260


def _cover(pixmap: QPixmap, width: int, height: int) -> QPixmap:
    scaled = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    return scaled.copy((scaled.width() - width) // 2, (scaled.height() - height) // 2, width, height)


def _blurred_background(pixmap: QPixmap, width: int, height: int) -> QPixmap:
    """Cheap stand-in for the render's boxblur + darkening: shrink hard, enlarge smoothly, dim."""
    tiny = pixmap.scaled(max(6, width // 28), max(6, height // 28), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    background = _cover(tiny.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation), width, height)
    painter = QPainter(background)
    painter.fillRect(background.rect(), QColor(0, 0, 0, 60))
    painter.end()
    return background


def _draw_frame(painter: QPainter, source: QPixmap, crop: str, width: int, height: int) -> None:
    if crop in {"fill_9_16", "fill_16_9"}:
        painter.drawPixmap(0, 0, _cover(source, width, height))
        return
    painter.drawPixmap(0, 0, _blurred_background(source, width, height))
    if crop == "4_3_blur" and width < height:
        window = round(width * 3 / 4)
        painter.drawPixmap(0, (height - window) // 2, _cover(source, width, window))
    elif crop == "4_3_blur":
        window_height = round(height * 3 / 4)
        painter.drawPixmap((width - round(window_height * 4 / 3)) // 2, 0, _cover(source, round(window_height * 4 / 3), window_height))
    else:
        fitted = source.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap((width - fitted.width()) // 2, (height - fitted.height()) // 2, fitted)


def _draw_subtitles(painter: QPainter, text: str, sub: dict, position: str, width: int, height: int) -> None:
    landscape = width > height
    frame_height = 1080 if landscape else 1920
    k = height / frame_height
    size = round(int(sub["size"]) * 0.72) if landscape else int(sub["size"])
    font = QFont(sub["font"])
    font.setBold(bool(sub.get("bold", True)))
    # libass uses the style size as the full line height, so pick the em size that gives that height.
    font.setPixelSize(100)
    font.setPixelSize(max(6, round(size * k * 100 / QFontMetricsF(font).height())))
    metrics = QFontMetricsF(font)
    frame_width = round(width / k)
    wrap_width = wrap_width_for(size, frame_width)
    chunk = (caption_chunks(text, wrap_width * 2) or [SAMPLE_TEXT])[0]
    lines = textwrap.wrap(chunk, width=wrap_width, break_long_words=False)
    line_height, block = size * k, size * k * len(lines)
    if position == "top":
        top = (146 if landscape else TOP_MARGIN) * k
    elif position == "middle":
        top = (height - block) / 2
    else:
        top = height - (120 if landscape else int(sub.get("margin_v", 420))) * k - block
    outline = max(4, round(size / 12)) * k
    for index, line in enumerate(lines):
        path = QPainterPath()
        x = max(12 * k, (width - metrics.horizontalAdvance(line)) / 2)
        path.addText(x, top + index * line_height + metrics.ascent(), font, line)
        painter.setPen(QPen(QColor(sub["outline"]), 2 * outline, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(sub["color"]))
        painter.drawPath(path)


def compose_preview(project_dir: Path, scene: dict, sub: dict, height: int, video_frame: Path | None = None, orientation: str = "portrait", max_width: int | None = None) -> QPixmap | None:
    """Return a pixmap of the scene as it will be framed and captioned, or None if there is no picture to show."""
    media = scene.get("media")
    if not media:
        return None
    if media.get("type") == "image":
        source = QPixmap(str(project_dir / media["path"]))
    else:
        thumb = media.get("thumb")
        source = QPixmap(str(video_frame)) if video_frame else QPixmap(str(project_dir / thumb)) if thumb else QPixmap()
    if source.isNull():
        return None
    frame_width, frame_height = (1920, 1080) if orientation == "landscape" else (1080, 1920)
    scale = height / frame_height
    if max_width:
        scale = min(scale, max_width / frame_width)
    width, height = round(frame_width * scale), round(frame_height * scale)
    canvas = QPixmap(width, height)
    canvas.fill(Qt.GlobalColor.black)
    painter = QPainter(canvas)
    painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.TextAntialiasing)
    _draw_frame(painter, source, scene.get("crop", "fill_9_16"), width, height)
    if scene.get("show_subtitles", True):
        _draw_subtitles(painter, scene.get("dialogue", "").strip(), sub, scene.get("subtitle_pos", "bottom"), width, height)
    painter.end()
    return canvas
