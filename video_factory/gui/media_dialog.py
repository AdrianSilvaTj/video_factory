"""Modal para elegir el recurso visual de una escena: buscar y descargar de bancos, o usar los archivos del proyecto."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QIcon, QImageReader, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QListView,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QPushButton, QTabWidget, QToolButton, QVBoxLayout, QWidget,
)

from ..clips import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, download_media
from ..pipeline import _find_ffmpeg
from ..project import add_search_term, import_media, list_assets, load_search_history, make_thumbnail, register_asset
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


def _icon_grid(grid: QListWidget, selection: QAbstractItemView.SelectionMode) -> None:
    grid.setViewMode(QListView.ViewMode.IconMode)
    grid.setResizeMode(QListView.ResizeMode.Adjust)
    grid.setMovement(QListView.Movement.Static)
    grid.setWordWrap(True)
    grid.setUniformItemSizes(True)
    grid.setIconSize(QSize(200, 200))
    grid.setGridSize(QSize(230, 270))
    grid.setSelectionMode(selection)
    grid.setStyleSheet("QListWidget::item:selected { background: #cfeef2; border: 2px solid #1fb6c8; color: black; }")


def _placeholder() -> QIcon:
    pixmap = QPixmap(200, 200)
    pixmap.fill(QColor("#cccccc"))
    return QIcon(pixmap)


class MediaDialog(QDialog):
    """After exec(), `media` holds the chosen scene media dict (or None if cancelled)."""

    def __init__(self, project_dir: Path, parent=None, initial_query: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Elegir imagen o video para la escena")
        self.resize(1100, 720)
        self.project_dir = project_dir
        self.media = None
        self.busy = False
        self.thumbs_tried: set[Path] = set()
        self.select_after: list[str] | None = None
        self.results = []
        self.net = QNetworkAccessManager(self)
        self.popup = _PreviewPopup()
        self.hover_item = None
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(500)
        self.hover_timer.timeout.connect(self._start_preview)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_search(initial_query), "Buscar en bancos (Pexels, Pixabay, NASA, Wikimedia, Openverse, Vecteezy)")
        self.tabs.addTab(self._build_local(), "Desde mi equipo")
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self._load_assets()

    # ---- search tab -------------------------------------------------------
    def _build_search(self, initial_query: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        row = QHBoxLayout()
        self.query = QComboBox()
        self.query.setEditable(True)
        self.query.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.query.addItems(load_search_history())
        self.query.setEditText(initial_query)
        self.query.lineEdit().setPlaceholderText("Palabras clave (en inglés dan más resultados); la lista guarda tus últimas búsquedas")
        self.query.lineEdit().returnPressed.connect(self.search)
        self.query.activated.connect(lambda _: self.search())
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
        _icon_grid(self.grid, QAbstractItemView.SelectionMode.MultiSelection)
        self.grid.setMouseTracking(True)
        self.grid.viewport().setMouseTracking(True)
        self.grid.viewport().installEventFilter(self)
        self.grid.itemSelectionChanged.connect(self._update_download_button)
        layout.addWidget(self.grid, 1)

        bottom = QHBoxLayout()
        self.status = QLabel("Busca un tema. Haz clic en los resultados que quieras (puedes marcar varios) y pulsa «Descargar»; pasa el mouse sobre un video para previsualizarlo.")
        self.status.setWordWrap(True)
        bottom.addWidget(self.status, 1)
        self.download_btn = QPushButton("Descargar")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_selected)
        bottom.addWidget(self.download_btn)
        layout.addLayout(bottom)
        return page

    def _update_bank_label(self, *_):
        chosen = [n for n, a in self.bank_actions.items() if a.isChecked()]
        self.bank.setText(f"Bancos ({len(chosen)}/{len(self.bank_actions)}) ▾")
        self.bank.setToolTip("Bancos donde buscar: " + ", ".join(chosen))

    def _update_download_button(self):
        count = len(self.grid.selectedItems())
        self.download_btn.setText(f"Descargar ({count})" if count else "Descargar")
        self.download_btn.setEnabled(bool(count) and not self.busy)

    def _set_busy(self, busy: bool):
        self.busy = busy
        self.search_btn.setEnabled(not busy)
        self.query.setEnabled(not busy)
        self.tabs.tabBar().setEnabled(not busy)
        self._update_download_button()
        self.use_btn.setEnabled(not busy and bool(self.assets_grid.selectedItems()))
        self.pick_btn.setEnabled(not busy)

    def done(self, result):
        if self.busy and result == 0:
            return
        self.popup.stop()
        super().done(result)

    def search(self):
        query = self.query.currentText().strip()
        if not query or self.busy:
            return
        providers, kind, vertical = tuple(n for n, a in self.bank_actions.items() if a.isChecked()), self.kind.currentData(), self.vertical.isChecked()
        if not providers:
            self.status.setText("Elige al menos un banco.")
            return
        history = add_search_term(query)
        self.query.blockSignals(True)
        self.query.clear()
        self.query.addItems(history)
        self.query.setEditText(query)
        self.query.blockSignals(False)
        self._set_busy(True)
        self.status.setText("Consultando los bancos…")
        run_task(self, lambda: search_media(query, providers, kind, vertical), self._show_results, self._search_failed)

    def _search_failed(self, error: str):
        self._set_busy(False)
        self.status.setText("ERROR: " + error)

    def _show_results(self, results):
        self._set_busy(False)
        self.results = results
        self.grid.clear()
        self.popup.stop()
        placeholder = _placeholder()
        for index, clip in enumerate(results):
            detail = "foto" if clip.get("media_type") == "image" else f"{clip.get('duration', 0)} s"
            item = QListWidgetItem(placeholder, f"{clip['provider']} · {detail} · {clip['width'] or '?'}×{clip['height'] or '?'}\n{clip['author']}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip("\n".join([clip.get("title", ""), "Licencia: " + (clip.get("license") or "?"), clip.get("page_url", "")]))
            self.grid.addItem(item)
            if clip.get("preview_url"):
                reply = self.net.get(QNetworkRequest(QUrl(clip["preview_url"])))
                reply.finished.connect(lambda r=reply, it=item: self._thumb_loaded(r, it))
        warnings = results[0].get("search_warnings", []) if results else []
        self.status.setText(f"{len(results)} resultados. Marca los que quieras y pulsa «Descargar»." + (" Avisos: " + " | ".join(warnings) if warnings else ""))
        self._update_download_button()

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

    def download_selected(self):
        clips = [self.results[item.data(Qt.ItemDataRole.UserRole)] for item in self.grid.selectedItems()]
        if not clips:
            return
        vecteezy = sum(1 for c in clips if c["provider"] == "Vecteezy")
        if vecteezy and QMessageBox.question(self, "Descargas de Vecteezy", f"{vecteezy} de los recursos son de Vecteezy y cada uno consume una descarga de tu cuota mensual. ¿Continuar?") != QMessageBox.StandardButton.Yes:
            return
        self._set_busy(True)
        self.status.setText(f"Descargando 0 de {len(clips)}…")
        run_task(self, lambda progress: self._download_all(clips, progress), self._downloaded, self._download_failed, self._download_progress)

    def _download_all(self, clips: list[dict], progress) -> dict:
        """Download every chosen clip into the project's assets; one failure does not stop the others."""
        saved, errors = [], []
        ffmpeg = _find_ffmpeg()
        for number, clip in enumerate(clips, start=1):
            try:
                path = download_media(clip, self.project_dir / "assets")
                thumb = make_thumbnail(ffmpeg, path, path.with_suffix(".thumb.jpg")) if ffmpeg else None
                media = {"path": path.relative_to(self.project_dir).as_posix(), "type": clip.get("media_type", "video"), "provider": clip["provider"], "author": clip["author"], "page_url": clip.get("page_url", ""),
                         "license": clip.get("license", ""), "license_url": clip.get("license_url", ""), "title": clip.get("title", ""), "attribution": clip.get("attribution", ""),
                         "thumb": thumb.relative_to(self.project_dir).as_posix() if thumb and thumb.is_file() else None}
                register_asset(self.project_dir, media)
                saved.append(media["path"])
            except Exception as exc:
                errors.append(f"{clip['provider']} {clip.get('provider_id', '')}: {exc}")
            progress((number, len(clips)))
        return {"saved": saved, "errors": errors}

    def _download_progress(self, step):
        number, total = step
        self.status.setText(f"Descargando {number} de {total}…")

    def _download_failed(self, error: str):
        self._set_busy(False)
        self.status.setText("ERROR: " + error)

    def _downloaded(self, result: dict):
        self._set_busy(False)
        self.grid.clearSelection()
        message = f"{len(result['saved'])} descargados en los archivos del proyecto."
        if result["errors"]:
            message += f" No se pudieron descargar {len(result['errors'])}: " + " | ".join(result["errors"])[:300]
        self.status.setText(message)
        self._load_assets(select=result["saved"])
        if result["saved"]:
            self.tabs.setCurrentIndex(1)
            self.assets_status.setText(message + " Elige uno y pulsa «Usar recurso».")

    # ---- project files tab --------------------------------------------------
    def _build_local(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Archivos de este proyecto (los descargados de bancos y los que copies de tu equipo). Elige uno y pulsa «Usar recurso»."))
        self.assets_grid = QListWidget()
        _icon_grid(self.assets_grid, QAbstractItemView.SelectionMode.SingleSelection)
        self.assets_grid.itemSelectionChanged.connect(lambda: self.use_btn.setEnabled(not self.busy and bool(self.assets_grid.selectedItems())))
        self.assets_grid.itemDoubleClicked.connect(lambda _: self.use_asset())
        layout.addWidget(self.assets_grid, 1)
        bottom = QHBoxLayout()
        self.assets_status = QLabel("")
        self.assets_status.setWordWrap(True)
        bottom.addWidget(self.assets_status, 1)
        self.pick_btn = QPushButton("Elegir archivo…")
        self.pick_btn.setToolTip("Copia imágenes o videos de tu equipo a los archivos del proyecto")
        self.pick_btn.clicked.connect(self.pick_local)
        bottom.addWidget(self.pick_btn)
        self.use_btn = QPushButton("Usar recurso")
        self.use_btn.setEnabled(False)
        self.use_btn.clicked.connect(self.use_asset)
        bottom.addWidget(self.use_btn)
        layout.addLayout(bottom)
        return page

    def _load_assets(self, select: list[str] | None = None):
        self.assets_grid.clear()
        missing = []
        placeholder = _placeholder()
        for entry in list_assets(self.project_dir):
            file = self.project_dir / entry["path"]
            source = self.project_dir / entry["thumb"] if entry["thumb"] else (file if entry["type"] == "image" else None)
            icon = placeholder
            if source:
                reader = QImageReader(str(source))
                size = reader.size()
                if size.isValid():
                    reader.setScaledSize(size.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                image = reader.read()
                if not image.isNull():
                    icon = QIcon(QPixmap.fromImage(image))
            elif entry["type"] == "video" and file not in self.thumbs_tried:
                missing.append(file)
            kind = "foto" if entry["type"] == "image" else "video"
            item = QListWidgetItem(icon, f"{file.name[:28]}\n{entry['provider']} · {kind}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            item.setToolTip("\n".join(filter(None, [entry.get("title", ""), entry["path"], "Licencia: " + entry["license"] if entry.get("license") else ""])))
            self.assets_grid.addItem(item)
            if select and entry["path"] in select:
                item.setSelected(True)
        count = self.assets_grid.count()
        self.assets_status.setText(f"{count} archivos en el proyecto." if count else "Todavía no hay archivos: descarga recursos de los bancos o usa «Elegir archivo…».")
        ffmpeg = _find_ffmpeg()
        if missing and ffmpeg:
            # Older videos have no thumbnail yet: make them in the background, then redraw once.
            self.thumbs_tried.update(missing)
            self.select_after = select
            run_task(self, lambda: [make_thumbnail(ffmpeg, f, f.with_suffix(".thumb.jpg")) for f in missing], self._thumbs_ready, self._thumbs_failed)

    def _thumbs_ready(self, _):
        self._load_assets(self.select_after)

    def _thumbs_failed(self, _):
        pass

    def use_asset(self):
        items = self.assets_grid.selectedItems()
        if self.busy or not items:
            return
        self.media = dict(items[0].data(Qt.ItemDataRole.UserRole))
        self.accept()

    def pick_local(self):
        extensions = " ".join("*" + e for e in sorted(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS))
        files, _ = QFileDialog.getOpenFileNames(self, "Elegir imágenes o videos", "", f"Imágenes y videos ({extensions})")
        if not files:
            return
        ffmpeg, copied = _find_ffmpeg(), []
        for file in files:
            path = self.project_dir / import_media(self.project_dir, Path(file))
            if ffmpeg:
                make_thumbnail(ffmpeg, path, path.with_suffix(".thumb.jpg"))
            copied.append(path.relative_to(self.project_dir).as_posix())
        self._load_assets(select=copied)
        self.assets_status.setText(f"{len(copied)} archivos copiados al proyecto. Elige uno y pulsa «Usar recurso».")
