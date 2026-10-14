"""Modal para elegir el recurso visual de una escena: buscar en bancos o cargar desde el equipo."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QPushButton, QTabWidget, QToolButton, QVBoxLayout, QWidget,
)

from ..clips import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, download_media
from ..pipeline import _find_ffmpeg
from ..project import import_media, make_thumbnail
from ..stock_sources import SOURCES, search_media
from .workers import run_task


class _PreviewPopup(QVideoWidget):
    """Floating muted looping preview shown while the mouse rests over a result."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.audio = QAudioOutput()
        self.audio.setMuted(True)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

    def play(self, url: str, width: int, height: int, pos: QPoint):
        self.resize(QSize(240, 427) if height >= width else QSize(427, 240))
        self.move(pos)
        self.player.setSource(QUrl(url))
        self.show()
        self.player.play()

    def stop(self):
        self.player.stop()
        self.hide()


class MediaDialog(QDialog):
    """After exec(), `media` holds the chosen scene media dict (or None if cancelled)."""

    def __init__(self, project_dir: Path, parent=None, initial_query: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Elegir imagen o video para la escena")
        self.resize(1100, 720)
        self.project_dir = project_dir
        self.media = None
        self.results = []
        self.net = QNetworkAccessManager(self)
        self.popup = _PreviewPopup()
        self.hover_item = None
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(500)
        self.hover_timer.timeout.connect(self._start_preview)

        tabs = QTabWidget()
        tabs.addTab(self._build_search(initial_query), "Buscar en bancos (Pexels, Pixabay, NASA, Wikimedia, Openverse)")
        tabs.addTab(self._build_local(), "Desde mi equipo")
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)

    def _build_search(self, initial_query: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        row = QHBoxLayout()
        self.query = QLineEdit(initial_query)
        self.query.setPlaceholderText("Palabras clave en inglés dan más resultados, ej.: ocean, forest, city")
        self.query.returnPressed.connect(self.search)
        row.addWidget(self.query, 1)
        self.bank = QToolButton()
        self.bank.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self.bank)
        self.bank_actions = {}
        for name in SOURCES:
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self._update_bank_label)
            self.bank_actions[name] = action
        self.bank.setMenu(menu)
        row.addWidget(self.bank)
        self._update_bank_label()
        self.kind = QComboBox()
        self.kind.addItem("Videos", "video")
        self.kind.addItem("Imágenes", "image")
        self.kind.addItem("Videos e imágenes", "both")
        row.addWidget(self.kind)
        self.vertical = QCheckBox("Solo verticales")
        self.vertical.setChecked(False)
        row.addWidget(self.vertical)
        self.search_btn = QPushButton("Buscar")
        self.search_btn.clicked.connect(self.search)
        row.addWidget(self.search_btn)
        layout.addLayout(row)

        self.grid = QListWidget()
        self.grid.setViewMode(QListView.ViewMode.IconMode)
        self.grid.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid.setMovement(QListView.Movement.Static)
        self.grid.setWordWrap(True)
        self.grid.setUniformItemSizes(True)
        self.grid.setIconSize(QSize(200, 200))
        self.grid.setGridSize(QSize(230, 270))
        self.grid.setMouseTracking(True)
        self.grid.viewport().setMouseTracking(True)
        self.grid.viewport().installEventFilter(self)
        self.grid.itemDoubleClicked.connect(lambda _: self.use_selected())
        layout.addWidget(self.grid, 1)

        bottom = QHBoxLayout()
        self.status = QLabel("Busca un tema; pasa el mouse sobre un video para previsualizarlo. Doble clic o «Usar este recurso» para elegirlo.")
        self.status.setWordWrap(True)
        bottom.addWidget(self.status, 1)
        self.use_btn = QPushButton("Usar este recurso")
        self.use_btn.clicked.connect(self.use_selected)
        bottom.addWidget(self.use_btn)
        layout.addLayout(bottom)
        return page

    def _build_local(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Elige una imagen (JPG, PNG, WEBP) o un video (MP4, MOV, MKV, WEBM) de tu equipo. Se copia dentro del proyecto."))
        pick = QPushButton("Elegir archivo…")
        pick.clicked.connect(self.pick_local)
        layout.addWidget(pick)
        layout.addStretch(1)
        return page

    def _update_bank_label(self, *_):
        chosen = [n for n, a in self.bank_actions.items() if a.isChecked()]
        self.bank.setText(f"Bancos ({len(chosen)}/{len(self.bank_actions)}) ▾")
        self.bank.setToolTip("Bancos donde buscar: " + ", ".join(chosen))

    def done(self, result):
        self.popup.stop()
        super().done(result)

    def search(self):
        query = self.query.text().strip()
        if not query:
            return
        self.search_btn.setEnabled(False)
        self.status.setText("Consultando los bancos…")
        providers, kind, vertical = tuple(n for n, a in self.bank_actions.items() if a.isChecked()), self.kind.currentData(), self.vertical.isChecked()
        if not providers:
            self.search_btn.setEnabled(True)
            self.status.setText("Elige al menos un banco.")
            return
        run_task(self, lambda: search_media(query, providers, kind, vertical), self._show_results, self._search_failed)

    def _search_failed(self, error: str):
        self.search_btn.setEnabled(True)
        self.status.setText("ERROR: " + error)

    def _show_results(self, results):
        self.search_btn.setEnabled(True)
        self.results = results
        self.grid.clear()
        self.popup.stop()
        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("#cccccc"))
        for index, clip in enumerate(results):
            detail = "foto" if clip.get("media_type") == "image" else f"{clip.get('duration', 0)} s"
            item = QListWidgetItem(QIcon(placeholder), f"{clip['provider']} · {detail} · {clip['width']}×{clip['height']}\n{clip['author']}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip("\n".join([clip.get("title", ""), "Licencia: " + (clip.get("license") or "?"), clip.get("page_url", "")]))
            self.grid.addItem(item)
            if clip.get("preview_url"):
                reply = self.net.get(QNetworkRequest(QUrl(clip["preview_url"])))
                reply.finished.connect(lambda r=reply, it=item: self._thumb_loaded(r, it))
        warnings = results[0].get("search_warnings", []) if results else []
        self.status.setText(f"{len(results)} resultados." + (" Avisos: " + " | ".join(warnings) if warnings else ""))

    def _thumb_loaded(self, reply, item):
        pixmap = QPixmap()
        if reply.error() == reply.NetworkError.NoError and pixmap.loadFromData(reply.readAll().data()):
            try:
                item.setIcon(QIcon(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            except RuntimeError:
                pass
        reply.deleteLater()

    def eventFilter(self, obj, event):
        if obj is self.grid.viewport():
            if event.type() == QEvent.Type.MouseMove:
                item = self.grid.itemAt(event.position().toPoint())
                if item is not self.hover_item:
                    self.hover_item = item
                    self.popup.stop()
                    self.hover_timer.stop()
                    if item is not None:
                        self.hover_timer.start()
            elif event.type() == QEvent.Type.Leave:
                self.hover_item = None
                self.hover_timer.stop()
                self.popup.stop()
        return super().eventFilter(obj, event)

    def _start_preview(self):
        if self.hover_item is None:
            return
        clip = self.results[self.hover_item.data(Qt.ItemDataRole.UserRole)]
        if clip.get("preview_video_url"):
            self.popup.play(clip["preview_video_url"], clip.get("width", 0), clip.get("height", 0), self.grid.mapToGlobal(QPoint(self.grid.width() - 260, 10)))

    def use_selected(self):
        item = self.grid.currentItem()
        if item is None:
            QMessageBox.information(self, "Elige un resultado", "Haz clic en un resultado primero.")
            return
        clip = self.results[item.data(Qt.ItemDataRole.UserRole)]
        self.use_btn.setEnabled(False)
        self.status.setText("Descargando el recurso elegido…")
        run_task(self, lambda: self._finish_download(clip), self._chosen, self._download_failed)

    def _finish_download(self, clip: dict) -> dict:
        path = download_media(clip, self.project_dir / "assets")
        ffmpeg = _find_ffmpeg()
        thumb = make_thumbnail(ffmpeg, path, path.with_suffix(".thumb.jpg")) if ffmpeg else None
        return {"path": path.relative_to(self.project_dir).as_posix(), "type": clip.get("media_type", "video"), "provider": clip["provider"], "author": clip["author"], "page_url": clip.get("page_url", ""), "license": clip.get("license", ""), "license_url": clip.get("license_url", ""), "title": clip.get("title", ""), "attribution": clip.get("attribution", ""), "thumb": thumb.relative_to(self.project_dir).as_posix() if thumb and thumb.is_file() else None}

    def _download_failed(self, error: str):
        self.use_btn.setEnabled(True)
        self.status.setText("ERROR: " + error)

    def _chosen(self, media: dict):
        self.media = media
        self.accept()

    def pick_local(self):
        extensions = " ".join("*" + e for e in sorted(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS))
        file, _ = QFileDialog.getOpenFileName(self, "Elegir imagen o video", "", f"Imágenes y videos ({extensions})")
        if not file:
            return
        source = Path(file)
        copied = self.project_dir / import_media(self.project_dir, source)
        ffmpeg = _find_ffmpeg()
        thumb = make_thumbnail(ffmpeg, copied, copied.with_suffix(".thumb.jpg")) if ffmpeg else None
        self.media = {"path": copied.relative_to(self.project_dir).as_posix(), "type": "image" if source.suffix.casefold() in IMAGE_EXTENSIONS else "video", "provider": "Archivo propio", "author": "Aportado por el usuario", "page_url": "", "thumb": thumb.relative_to(self.project_dir).as_posix() if thumb and thumb.is_file() else None}
        self.accept()
