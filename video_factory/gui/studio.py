"""Ventana única de Video Factory: opciones generales, escenas y detalle de la escena. Ejecutar con: python -m video_factory.gui"""
from __future__ import annotations

import os
import subprocess
import sys
import traceback
from pathlib import Path

import time

from PySide6.QtCore import QEvent, QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QDoubleSpinBox, QFileDialog, QFontComboBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox, QPlainTextEdit,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSlider, QSpinBox, QSplitter, QStackedWidget,
    QVBoxLayout, QWidget,
)

from ..channels import CHANNELS, TARGET_SECONDS, VOICES
from .. import proc
from ..pipeline import _find_ffmpeg
from ..project import (
    CROPS, MUSIC_EXTENSIONS, PROJECTS_DIR, create_project, estimate_seconds, extract_frame, import_media,
    load_project, new_scene, render_project, save_project, split_script, synthesize_voice, voice_defaults,
)
from ..storage import APP_ROOT
from .frame_preview import compose_preview
from .media_dialog import MediaDialog
from .workers import run_task

ZOOM_LABELS = {"none": "Sin zoom", "slow": "Zoom lento", "medium": "Zoom medio", "fast": "Zoom rápido"}


class SceneCard(QFrame):
    """One row of the scene list: dialogue text, thumbnail and ordering buttons."""

    selected = Signal(int)
    edited = Signal()
    media_requested = Signal(int)
    move_requested = Signal(int, int)
    delete_requested = Signal(int)

    def __init__(self, index: int, scene: dict, project_dir: Path):
        super().__init__()
        self.index, self.scene, self.project_dir = index, scene, project_dir
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        head = QHBoxLayout()
        self.title = QLabel()
        head.addWidget(self.title, 1)
        for text, tip, slot in (("↑", "Subir", lambda: self.move_requested.emit(index, -1)), ("↓", "Bajar", lambda: self.move_requested.emit(index, 1)), ("✕", "Eliminar escena", lambda: self.delete_requested.emit(index))):
            button = QPushButton(text)
            button.setToolTip(tip)
            button.setFixedWidth(28)
            button.clicked.connect(slot)
            head.addWidget(button)
        layout.addLayout(head)
        body = QHBoxLayout()
        self.text = QPlainTextEdit(scene["dialogue"])
        self.text.setPlaceholderText("Diálogo de la escena…")
        self.text.setFixedHeight(84)
        self.text.textChanged.connect(self._text_changed)
        body.addWidget(self.text, 1)
        self.thumb = QPushButton()
        self.thumb.setFixedSize(96, 96)
        self.thumb.setToolTip("Elegir imagen o video")
        self.thumb.clicked.connect(lambda: self.media_requested.emit(index))
        body.addWidget(self.thumb)
        layout.addLayout(body)
        self.refresh()

    def refresh(self):
        self.title.setText(f"Escena {self.index + 1} · ~{estimate_seconds(self.text.toPlainText(), self.scene.get('duration', 3.0)):.1f} s")
        media = self.scene.get("media")
        source = media and (media.get("thumb") or (media["path"] if media["type"] == "image" else None))
        pixmap = QPixmap(str(self.project_dir / source)) if source else QPixmap()
        if pixmap.isNull():
            self.thumb.setIcon(QIcon())
            self.thumb.setText("Elegir\nrecurso" if not media else "video")
        else:
            self.thumb.setText("")
            self.thumb.setIcon(pixmap.scaled(92, 92, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.thumb.setIconSize(QSize(88, 88))

    def set_highlight(self, on: bool):
        self.setStyleSheet("#card { border: 2px solid #1fb6c8; border-radius: 6px; }" if on else "#card { border: 1px solid #bbb; border-radius: 6px; }")

    def _text_changed(self):
        self.scene["dialogue"] = self.text.toPlainText()
        self.refresh()
        self.edited.emit()

    def mousePressEvent(self, event):
        self.selected.emit(self.index)
        super().mousePressEvent(event)

    def focusInEvent(self, event):
        self.selected.emit(self.index)
        super().focusInEvent(event)


class StudioWindow(QMainWindow):
    def __init__(self, projects_dir: Path = PROJECTS_DIR):
        super().__init__()
        self.projects_dir = projects_dir
        self.folder: Path | None = None
        self.project: dict = {}
        self.current = 0
        self.cards: list[SceneCard] = []
        self.loading = False
        self.setWindowTitle("Video Factory")
        self.resize(1360, 820)
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self._save_now)
        self.frame_timer = QTimer(self)
        self.frame_timer.setSingleShot(True)
        self.frame_timer.setInterval(120)
        self.frame_timer.timeout.connect(self._refresh_frame)
        self.frames_pending: set[Path] = set()

        splitter = QSplitter()
        self.busy = False
        self.general_panel = self._build_general()
        self.scenes_panel = self._build_scenes()
        splitter.addWidget(self.general_panel)
        splitter.addWidget(self.scenes_panel)
        splitter.addWidget(self._build_detail())
        splitter.setSizes([300, 480, 560])
        self.setCentralWidget(splitter)
        self._open_initial_project()

    def _build_general(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        box = QGroupBox("Proyecto")
        form = QFormLayout(box)
        self.project_combo = QComboBox()
        self.project_combo.activated.connect(self._project_chosen)
        form.addRow("Abrir:", self.project_combo)
        new_btn = QPushButton("Nuevo proyecto…")
        new_btn.clicked.connect(self.new_project)
        form.addRow(new_btn)
        layout.addWidget(box)

        options = QGroupBox("Opciones generales")
        form = QFormLayout(options)
        self.channel = QComboBox()
        for key, preset in CHANNELS.items():
            self.channel.addItem(preset["label"], key)
        self.channel.activated.connect(self._channel_changed)
        form.addRow("Canal:", self.channel)
        self.voice = QComboBox()
        for key, preset in VOICES.items():
            self.voice.addItem(preset["label"], key)
        self.voice.activated.connect(self._voice_changed)
        form.addRow("Voz:", self.voice)
        self.music = QCheckBox("Música de fondo")
        self.music.toggled.connect(self._options_changed)
        form.addRow(self.music)
        self.gain = QSlider(Qt.Orientation.Horizontal)
        self.gain.setRange(0, 100)
        self.gain.valueChanged.connect(self._options_changed)
        form.addRow("Volumen música:", self.gain)
        self.music_file = QLabel("Música del canal")
        self.music_file.setWordWrap(True)
        form.addRow("Archivo:", self.music_file)
        music_buttons = QHBoxLayout()
        pick_music = QPushButton("Elegir archivo…")
        pick_music.clicked.connect(self.pick_music)
        music_buttons.addWidget(pick_music)
        reset_music = QPushButton("Usar la del canal")
        reset_music.clicked.connect(self.reset_music)
        music_buttons.addWidget(reset_music)
        form.addRow(music_buttons)
        self.music_btn = QPushButton("▶ Escuchar música")
        self.music_btn.setToolTip("Reproduce la música elegida (la del canal o tu archivo) con el volumen del slider")
        self.music_btn.clicked.connect(self._toggle_music)
        form.addRow(self.music_btn)
        self.music_player = QMediaPlayer(self)
        self.music_audio = QAudioOutput()
        self.music_player.setAudioOutput(self.music_audio)
        self.music_player.playbackStateChanged.connect(lambda state: self.music_btn.setText("⏹ Detener música" if state == QMediaPlayer.PlaybackState.PlayingState else "▶ Escuchar música"))
        self.outro = QCheckBox("Incluir outro del canal")
        self.outro.toggled.connect(self._options_changed)
        form.addRow(self.outro)
        layout.addWidget(options)

        tune = QGroupBox("Ajustes de la voz")
        form = QFormLayout(tune)
        self.voice_rate = self._voice_slider(form, "Velocidad:", -50, 50, "%")
        self.voice_pitch = self._voice_slider(form, "Tono:", -30, 30, " Hz")
        self.voice_volume = self._voice_slider(form, "Volumen:", -50, 50, "%")
        tune_buttons = QHBoxLayout()
        reset_voice = QPushButton("Restablecer")
        reset_voice.setToolTip("Vuelve a los valores recomendados de esta voz")
        reset_voice.clicked.connect(self._voice_changed)
        tune_buttons.addWidget(reset_voice)
        self.test_btn = QPushButton("▶ Probar voz")
        self.test_btn.clicked.connect(self.test_voice)
        tune_buttons.addWidget(self.test_btn)
        form.addRow(tune_buttons)
        self.test_player = QMediaPlayer(self)
        self.test_audio = QAudioOutput()
        self.test_player.setAudioOutput(self.test_audio)
        layout.addWidget(tune)

        subs = QGroupBox("Subtítulos")
        form = QFormLayout(subs)
        self.font = QFontComboBox()
        self.font.activated.connect(self._subtitles_changed)
        form.addRow("Fuente:", self.font)
        self.sub_size = QSpinBox()
        self.sub_size.setRange(30, 250)
        self.sub_size.valueChanged.connect(self._subtitles_changed)
        form.addRow("Tamaño:", self.sub_size)
        self.sub_color = QPushButton("Color del texto")
        self.sub_color.clicked.connect(lambda: self.choose_color("color"))
        form.addRow(self.sub_color)
        self.sub_outline = QPushButton("Color del contorno")
        self.sub_outline.clicked.connect(lambda: self.choose_color("outline"))
        form.addRow(self.sub_outline)
        self.sub_bold = QCheckBox("Negrita")
        self.sub_bold.toggled.connect(self._subtitles_changed)
        form.addRow(self.sub_bold)
        self.sub_sample = QLabel("Así se verán")
        self.sub_sample.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_sample.setMinimumHeight(60)
        form.addRow(self.sub_sample)
        layout.addWidget(subs)
        layout.addStretch(1)
        return page

    def _build_scenes(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        top = QHBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 16px; font-weight: 700;")
        top.addWidget(self.title, 1)
        paste = QPushButton("Pegar guion…")
        paste.setToolTip("Pega un guion completo; cada párrafo (separado por una línea en blanco) será una escena")
        paste.clicked.connect(self.paste_script)
        top.addWidget(paste)
        layout.addLayout(top)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scene_host = QWidget()
        self.scene_layout = QVBoxLayout(self.scene_host)
        self.scene_layout.addStretch(1)
        scroll.setWidget(self.scene_host)
        layout.addWidget(scroll, 1)
        add = QPushButton("+ Añadir escena")
        add.clicked.connect(self.add_scene)
        layout.addWidget(add)
        return page

    def _build_detail(self) -> QWidget:
        top = QWidget()
        outer = QVBoxLayout(top)
        self.detail_body = QWidget()
        outer.addWidget(self.detail_body, 1)
        self.progress_row = QWidget()
        progress_layout = QHBoxLayout(self.progress_row)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress = QProgressBar()
        progress_layout.addWidget(self.progress, 1)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setToolTip("Detiene el proceso en curso")
        self.cancel_btn.clicked.connect(self._cancel)
        progress_layout.addWidget(self.cancel_btn)
        self.progress_row.setVisible(False)
        outer.addWidget(self.progress_row)
        layout = QVBoxLayout(self.detail_body)
        layout.setContentsMargins(0, 0, 0, 0)
        self.detail_title = QLabel("Escena")
        self.detail_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(self.detail_title)
        self.preview = QLabel("Sin recurso visual")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(120, 380)
        self.preview.setStyleSheet("background: #111; color: #bbb; border-radius: 8px;")
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video = QVideoWidget()
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.preview)
        self.stack.addWidget(self.video)
        layout.addWidget(self.stack, 1)
        self.controls = QWidget()
        controls = QHBoxLayout(self.controls)
        controls.setContentsMargins(0, 0, 0, 0)
        self.play_btn = QPushButton("⏸")
        self.play_btn.setFixedWidth(40)
        self.play_btn.setToolTip("Pausar / reanudar la vista previa (también con clic sobre el video)")
        self.play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self.play_btn)
        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.sliderMoved.connect(self.player.setPosition)
        controls.addWidget(self.seek, 1)
        self.time_label = QLabel("0:00")
        controls.addWidget(self.time_label)
        self.controls.setVisible(False)
        layout.addWidget(self.controls)
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(lambda ms: self.seek.setRange(0, ms))
        self.player.playbackStateChanged.connect(lambda state: self.play_btn.setText("⏸" if state == QMediaPlayer.PlaybackState.PlayingState else "▶"))
        self.video.installEventFilter(self)
        self.preview.installEventFilter(self)
        buttons = QHBoxLayout()
        pick = QPushButton("Elegir o cambiar imagen / video…")
        pick.clicked.connect(lambda: self.pick_media(self.current))
        buttons.addWidget(pick)
        self.preview_btn = QPushButton("▶ Vista previa de la escena")
        self.preview_btn.setToolTip("Genera un video de baja resolución de esta escena con su voz, encuadre, zoom y subtítulos")
        self.preview_btn.clicked.connect(self.preview_scene)
        buttons.addWidget(self.preview_btn)
        layout.addLayout(buttons)
        form = QFormLayout()
        self.crop = QComboBox()
        for key, label in CROPS.items():
            self.crop.addItem(label, key)
        self.crop.activated.connect(self._scene_options_changed)
        form.addRow("Encuadre:", self.crop)
        zoom_row = QHBoxLayout()
        self.zoom_speed = QComboBox()
        for key, label in ZOOM_LABELS.items():
            self.zoom_speed.addItem(label, key)
        self.zoom_speed.activated.connect(self._scene_options_changed)
        zoom_row.addWidget(self.zoom_speed)
        self.zoom_direction = QComboBox()
        self.zoom_direction.addItem("Acercar", "in")
        self.zoom_direction.addItem("Alejar", "out")
        self.zoom_direction.activated.connect(self._scene_options_changed)
        zoom_row.addWidget(self.zoom_direction)
        self.zoom_label = QLabel("Zoom (imágenes):")
        form.addRow(self.zoom_label, zoom_row)
        self.start = QDoubleSpinBox()
        self.start.setRange(0, 3600)
        self.start.setSuffix(" s")
        self.start.setDecimals(1)
        self.start.valueChanged.connect(self._scene_options_changed)
        self.start_label = QLabel("Inicio del video:")
        form.addRow(self.start_label, self.start)
        self.sub_show = QCheckBox("Mostrar subtítulos en esta escena")
        self.sub_show.toggled.connect(self._scene_options_changed)
        form.addRow(self.sub_show)
        self.sub_pos = QComboBox()
        for label, key in (("Abajo", "bottom"), ("Centro", "middle"), ("Arriba", "top")):
            self.sub_pos.addItem(label, key)
        self.sub_pos.activated.connect(self._scene_options_changed)
        form.addRow("Posición de subtítulos:", self.sub_pos)
        layout.addLayout(form)

        self.total = QLabel()
        layout.addWidget(self.total)
        self.render_btn = QPushButton("Renderizar video")
        self.render_btn.setStyleSheet("font-weight: 700; padding: 8px;")
        self.render_btn.clicked.connect(self.render)
        layout.addWidget(self.render_btn)
        self.open_btn = QWidget()
        open_row = QHBoxLayout(self.open_btn)
        open_row.setContentsMargins(0, 0, 0, 0)
        play = QPushButton("Abrir video renderizado")
        play.clicked.connect(lambda: os.startfile(self.folder / "render" / "video.mp4"))
        open_row.addWidget(play)
        show = QPushButton("Abrir carpeta del video")
        show.setToolTip("Abre el Explorador de archivos con el video seleccionado")
        show.clicked.connect(lambda: subprocess.Popen(["explorer", "/select,", str((self.folder / "render" / "video.mp4").resolve())]))
        open_row.addWidget(show)
        self.open_btn.setVisible(False)
        layout.addWidget(self.open_btn)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Mensajes y errores aparecerán aquí. Arrastra el borde superior para cambiar su tamaño.")
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(top)
        splitter.addWidget(self.log)
        splitter.setCollapsible(0, False)
        splitter.setStretchFactor(0, 1)
        splitter.setSizes([700, 110])
        return splitter

    def _say(self, text: str):
        if text:
            self.log.appendPlainText(f"[{time.strftime('%H:%M:%S')}] {text}")

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _on_position(self, ms: int):
        if not self.seek.isSliderDown():
            self.seek.setValue(ms)
        self.time_label.setText(f"{ms // 60000}:{ms // 1000 % 60:02d}")

    def eventFilter(self, obj, event):
        if obj is self.video and event.type() == QEvent.Type.MouseButtonPress:
            self._toggle_play()
        elif obj is self.preview and event.type() == QEvent.Type.Resize:
            self.frame_timer.start()
        return super().eventFilter(obj, event)

    # ---- project handling -------------------------------------------------
    def _project_dirs(self) -> list[Path]:
        folders = [p for p in self.projects_dir.iterdir() if (p / "project.json").is_file()] if self.projects_dir.is_dir() else []
        return sorted(folders, key=lambda p: (p / "project.json").stat().st_mtime, reverse=True)

    def _open_initial_project(self):
        folders = self._project_dirs()
        if folders:
            self.open_project(folders[0])
        else:
            self.new_project(first=True)

    def new_project(self, first: bool = False):
        name, ok = QInputDialog.getText(self, "Nuevo proyecto", "Nombre del proyecto:", text="Mi video" if first else "")
        if not ok or not name.strip():
            if first:
                name = "Mi video"
            else:
                return
        self.open_project(create_project(name.strip(), root=self.projects_dir))

    def _project_chosen(self, index: int):
        self._save_now()
        self.open_project(self.project_combo.itemData(index))

    def open_project(self, folder: Path):
        self._save_now()
        self._stop_music()
        self.loading = True
        self.folder, self.project = folder, load_project(folder)
        self.current = 0
        self.project_combo.clear()
        for path in self._project_dirs():
            self.project_combo.addItem(path.name, path)
        self.project_combo.setCurrentIndex(max(0, self.project_combo.findData(folder)))
        self.channel.setCurrentIndex(self.channel.findData(self.project["channel"]))
        self.voice.setCurrentIndex(self.voice.findData(self.project["voice"]))
        self.music.setChecked(self.project["music"]["enabled"])
        self.gain.setValue(round(self.project["music"]["gain"] * 100))
        self.outro.setChecked(self.project["outro"])
        self._load_subtitles()
        self._load_music_label()
        self._load_voice_settings()
        self.title.setText(self.project["name"])
        self.setWindowTitle(f"Video Factory — {self.project['name']}")
        self._say("")
        self.open_btn.setVisible((folder / "render" / "video.mp4").is_file())
        self.loading = False
        self._rebuild_scenes()

    def _changed(self):
        if not self.loading:
            self.save_timer.start()
            self.frame_timer.start()

    def _save_now(self):
        self.save_timer.stop()
        if self.folder is not None and self.project:
            save_project(self.folder, self.project)

    def closeEvent(self, event):
        if self.busy:
            QMessageBox.warning(self, "Proceso en curso", "Hay un proceso en curso. Espera a que termine para cerrar la aplicación.")
            event.ignore()
            return
        self._save_now()
        super().closeEvent(event)

    def _set_busy(self, busy: bool):
        """Lock every control (the log stays usable) while a blocking process runs."""
        self.busy = busy
        if busy:
            self._stop_music()
        for widget in (self.general_panel, self.scenes_panel, self.detail_body):
            widget.setEnabled(not busy)
        self.progress_row.setVisible(busy)
        if busy:
            proc.reset()
            self.progress.setRange(0, 0)
            self.cancel_btn.setEnabled(True)
            QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        else:
            QApplication.restoreOverrideCursor()

    def _cancel(self):
        proc.cancel_all()
        self.cancel_btn.setEnabled(False)
        self._say("Cancelando…")

    def _was_cancelled(self, error: str) -> bool:
        if error == proc.CANCELLED:
            self._say("Proceso cancelado.")
            return True
        return False

    # ---- general options --------------------------------------------------
    def _options_changed(self, *_):
        if self.loading:
            return
        self.project.update({"voice": self.voice.currentData(), "outro": self.outro.isChecked()})
        self.project["music"].update({"enabled": self.music.isChecked(), "gain": self.gain.value() / 100})
        self.music_audio.setVolume(self.project["music"]["gain"])
        self._changed()

    def _channel_changed(self, *_):
        channel = CHANNELS[self.channel.currentData()]
        self._stop_music()
        self.project["channel"] = self.channel.currentData()
        self.loading = True
        self.voice.setCurrentIndex(self.voice.findData(channel["default_voice"]))
        self.gain.setValue(round(channel["music_gain"] * 100))
        self.outro.setChecked(channel["outro"] is not None)
        self.project["subtitles"] = dict(channel["subtitles"])
        self.project["voice"] = self.voice.currentData()
        self.project["voice_settings"] = voice_defaults(self.voice.currentData())
        self.loading = False
        self._load_subtitles()
        self._load_voice_settings()
        self._options_changed()

    def _voice_slider(self, form, text: str, low: int, high: int, suffix: str) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(low, high)
        label = QLabel()
        label.setMinimumWidth(56)
        slider.valueChanged.connect(lambda value: label.setText(f"{value:+d}{suffix}"))
        slider.valueChanged.connect(self._voice_settings_changed)
        row = QHBoxLayout()
        row.addWidget(slider, 1)
        row.addWidget(label)
        form.addRow(text, row)
        return slider

    def _load_voice_settings(self):
        settings = self.project["voice_settings"]
        self.loading = True
        for slider, key in ((self.voice_rate, "rate"), (self.voice_pitch, "pitch"), (self.voice_volume, "volume")):
            slider.setValue(int(settings.get(key, 0)))
            slider.valueChanged.emit(slider.value())
        self.loading = False

    def _voice_changed(self, *_):
        """A voice was picked (or 'Restablecer' pressed): go back to that voice's recommended settings."""
        self.project["voice"] = self.voice.currentData()
        self.project["voice_settings"] = voice_defaults(self.voice.currentData())
        self._load_voice_settings()
        self._changed()

    def _voice_settings_changed(self, *_):
        if not self.loading:
            self.project["voice_settings"] = {"rate": self.voice_rate.value(), "pitch": self.voice_pitch.value(), "volume": self.voice_volume.value()}
            self._changed()

    def test_voice(self):
        self._save_now()
        folder, voice, settings = self.folder, self.project["voice"], dict(self.project["voice_settings"])
        self._set_busy(True)
        self._say("Generando la muestra de voz…")
        run_task(self, lambda: synthesize_voice(folder, "Hola, así sonará la narración de tu video.", voice, settings, _find_ffmpeg()), self._test_ready, self._test_failed)

    def _test_ready(self, wav):
        self._set_busy(False)
        self._say("Muestra de voz lista.")
        self.test_player.setSource(QUrl.fromLocalFile(str(wav)))
        self.test_player.play()

    def _test_failed(self, error: str):
        self._set_busy(False)
        if self._was_cancelled(error):
            return
        self._say("ERROR: " + error)

    def _toggle_music(self):
        if self.music_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.music_player.stop()
            return
        music = self.project["music"]
        path = self.folder / music["path"] if music["path"] else CHANNELS[self.project["channel"]]["music"]
        if not path.is_file():
            self._say(f"No encuentro el archivo de música: {path}")
            return
        self.music_audio.setVolume(music["gain"])
        self.music_player.setSource(QUrl.fromLocalFile(str(path)))
        self.music_player.play()

    def _stop_music(self):
        self.music_player.stop()

    def pick_music(self):
        extensions = " ".join("*" + e for e in sorted(MUSIC_EXTENSIONS))
        file, _ = QFileDialog.getOpenFileName(self, "Elegir música de fondo", "", f"Audio ({extensions})")
        if not file:
            return
        if Path(file).suffix.casefold() not in MUSIC_EXTENSIONS:
            QMessageBox.warning(self, "Formato no admitido", "Usa MP3, WAV, M4A, OGG, AAC o FLAC.")
            return
        self._stop_music()
        self.project["music"].update({"path": import_media(self.folder, Path(file)), "enabled": True, "name": Path(file).name})
        self.loading = True
        self.music.setChecked(True)
        self.loading = False
        self._load_music_label()
        self._changed()

    def reset_music(self):
        self._stop_music()
        self.project["music"].update({"path": None, "name": None})
        self._load_music_label()
        self._changed()

    def _load_music_label(self):
        music = self.project["music"]
        self.music_file.setText(music.get("name") or Path(music["path"]).name if music["path"] else "Música del canal")

    def _load_subtitles(self):
        sub = self.project["subtitles"]
        self.loading = True
        self.font.setCurrentFont(QFont(sub["font"]))
        self.sub_size.setValue(int(sub["size"]))
        self.sub_bold.setChecked(bool(sub.get("bold", True)))
        self.loading = False
        self._apply_subtitle_preview()

    def _apply_subtitle_preview(self):
        sub = self.project["subtitles"]
        self.frame_timer.start()
        for button, key in ((self.sub_color, "color"), (self.sub_outline, "outline")):
            color = QColor(sub[key])
            button.setStyleSheet(f"background: {sub[key]}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.sub_sample.setStyleSheet(f"background: #555; color: {sub['color']}; font-family: '{sub['font']}'; font-size: {max(10, round(int(sub['size']) * 0.22))}px; font-weight: {'bold' if sub.get('bold', True) else 'normal'};")

    def _subtitles_changed(self, *_):
        if self.loading:
            return
        self.project["subtitles"].update({"font": self.font.currentFont().family(), "size": self.sub_size.value(), "bold": self.sub_bold.isChecked()})
        self._apply_subtitle_preview()
        self._changed()

    def choose_color(self, key: str):
        color = QColorDialog.getColor(QColor(self.project["subtitles"][key]), self, "Elegir color")
        if color.isValid():
            self.project["subtitles"][key] = color.name().upper()
            self._apply_subtitle_preview()
            self._changed()

    # ---- scenes -----------------------------------------------------------
    def _rebuild_scenes(self):
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards = []
        for index, scene in enumerate(self.project["scenes"]):
            card = SceneCard(index, scene, self.folder)
            card.selected.connect(self.select_scene)
            card.edited.connect(self._scene_text_edited)
            card.media_requested.connect(self.pick_media)
            card.move_requested.connect(self.move_scene)
            card.delete_requested.connect(self.delete_scene)
            self.scene_layout.insertWidget(index, card)
            self.cards.append(card)
        self.current = min(self.current, len(self.cards) - 1)
        self.select_scene(self.current)

    def _refresh_frame(self):
        """Draw the current scene's framing and subtitles in the preview area (skipped while a video preview plays)."""
        if not self.project.get("scenes") or self.stack.currentIndex() != 0:
            return
        scene = self.project["scenes"][self.current]
        media = scene.get("media")
        frame = self._video_frame(scene) if media and media.get("type") == "video" else None
        pixmap = compose_preview(self.folder, scene, self.project["subtitles"], max(300, self.preview.height() - 8), frame)
        if pixmap is None:
            self.preview.setPixmap(QPixmap())
            self.preview.setText("Sin recurso visual" if not scene.get("media") else "Video (sin miniatura)")
        else:
            self.preview.setPixmap(pixmap)

    def _video_frame(self, scene: dict) -> Path | None:
        """Frame of the clip at the chosen start second; extracts it in the background the first time and refreshes when ready."""
        media, start = scene["media"], float(scene.get("start") or 0)
        target = self.folder / "render" / "frames" / f"{Path(media['path']).stem}_{start:.1f}.jpg"
        if target.is_file():
            return target
        ffmpeg = _find_ffmpeg()
        if ffmpeg and target not in self.frames_pending:
            self.frames_pending.add(target)
            source = self.folder / media["path"]
            run_task(self, lambda: extract_frame(ffmpeg, source, start, target), self._frame_ready, self._frame_failed)
        return None

    def _frame_ready(self, target):
        self.frames_pending.discard(target)
        self._refresh_frame()

    def _frame_failed(self, error: str):
        self.frames_pending.clear()
        self._say(error)

    def _scene_text_edited(self):
        self._update_total()
        self._changed()

    def select_scene(self, index: int):
        if not 0 <= index < len(self.cards):
            return
        self.current = index
        self._stop_preview()
        for i, card in enumerate(self.cards):
            card.set_highlight(i == index)
        scene = self.project["scenes"][index]
        self.loading = True
        self.detail_title.setText(f"Escena {index + 1}")
        self.crop.setCurrentIndex(self.crop.findData(scene["crop"]))
        self.zoom_speed.setCurrentIndex(self.zoom_speed.findData(scene["zoom"]["speed"]))
        self.zoom_direction.setCurrentIndex(self.zoom_direction.findData(scene["zoom"]["direction"]))
        self.start.setValue(float(scene.get("start") or 0))
        self.sub_pos.setCurrentIndex(self.sub_pos.findData(scene.get("subtitle_pos", "bottom")))
        self.sub_show.setChecked(scene.get("show_subtitles", True))
        self.sub_pos.setEnabled(self.sub_show.isChecked())
        media = scene.get("media")
        is_image = bool(media) and media["type"] == "image"
        for widget in (self.zoom_label, self.zoom_speed, self.zoom_direction):
            widget.setEnabled(is_image)
        for widget in (self.start_label, self.start):
            widget.setEnabled(bool(media) and not is_image)
        self._refresh_frame()
        self.loading = False
        self._update_total()

    def _scene_options_changed(self, *_):
        if self.loading or not self.project.get("scenes"):
            return
        scene = self.project["scenes"][self.current]
        scene["crop"] = self.crop.currentData()
        scene["zoom"] = {"speed": self.zoom_speed.currentData(), "direction": self.zoom_direction.currentData()}
        scene["start"] = self.start.value()
        scene["subtitle_pos"] = self.sub_pos.currentData()
        scene["show_subtitles"] = self.sub_show.isChecked()
        self.sub_pos.setEnabled(self.sub_show.isChecked())
        self._changed()

    def _update_total(self):
        total = sum(estimate_seconds(s["dialogue"], s.get("duration", 3.0)) for s in self.project["scenes"])
        color = "#2e7d32" if abs(total - TARGET_SECONDS) <= 5 else "#c77700"
        self.total.setText(f"<b>Duración estimada: ~{total:.0f} s</b> <span style='color:{color}'>(objetivo {TARGET_SECONDS} s; la real depende de la voz)</span>")

    def add_scene(self):
        self.project["scenes"].append(new_scene())
        self.current = len(self.project["scenes"]) - 1
        self._rebuild_scenes()
        self._changed()

    def paste_script(self):
        text, ok = QInputDialog.getMultiLineText(self, "Pegar guion", "Cada párrafo (separado por una línea en blanco) será una escena:")
        if not ok or not text.strip():
            return
        scenes = [new_scene(t) for t in split_script(text)]
        only_empty = len(self.project["scenes"]) == 1 and not self.project["scenes"][0]["dialogue"].strip() and not self.project["scenes"][0]["media"]
        self.project["scenes"] = scenes if only_empty else self.project["scenes"] + scenes
        self.current = len(self.project["scenes"]) - len(scenes)
        self._rebuild_scenes()
        self._changed()

    def move_scene(self, index: int, step: int):
        target = index + step
        scenes = self.project["scenes"]
        if 0 <= target < len(scenes):
            scenes[index], scenes[target] = scenes[target], scenes[index]
            self.current = target
            self._rebuild_scenes()
            self._changed()

    def delete_scene(self, index: int):
        scenes = self.project["scenes"]
        if len(scenes) == 1:
            scenes[0] = new_scene()
        elif QMessageBox.question(self, "Eliminar escena", f"¿Eliminar la escena {index + 1}?") == QMessageBox.StandardButton.Yes:
            del scenes[index]
        else:
            return
        self._rebuild_scenes()
        self._changed()

    def pick_media(self, index: int):
        scene = self.project["scenes"][index]
        dialog = MediaDialog(self.folder, self, initial_query=" ".join(scene["dialogue"].split()[:3]))
        if dialog.exec() and dialog.media:
            scene["media"] = dialog.media
            self.current = index
            self.cards[index].refresh()
            self.select_scene(index)
            self._changed()

    # ---- scene preview ----------------------------------------------------
    def _stop_preview(self):
        self.player.stop()
        self.player.setSource(QUrl())
        self.stack.setCurrentIndex(0)
        self.controls.setVisible(False)

    def preview_scene(self):
        index = self.current
        if not self.project["scenes"][index].get("media"):
            QMessageBox.information(self, "Falta el recurso", "Elige primero una imagen o video para esta escena.")
            return
        self._save_now()
        self._stop_preview()
        folder = self.folder
        self.preview_index = index
        self._set_busy(True)
        self._say("Generando la vista previa de la escena (la primera vez sintetiza la voz)…")
        run_task(self, lambda: render_project(folder, only_scene=index), self._preview_ready, self._preview_failed)

    def _preview_ready(self, report: dict):
        self._set_busy(False)
        self._say("Vista previa de la escena lista.")
        if self.preview_index == self.current:
            self.player.setSource(QUrl.fromLocalFile(report["output"]))
            self.stack.setCurrentIndex(1)
            self.controls.setVisible(True)
            self.player.play()

    def _preview_failed(self, error: str):
        self._set_busy(False)
        if self._was_cancelled(error):
            return
        self._say("ERROR: " + error)

    # ---- render -----------------------------------------------------------
    def render(self):
        self._save_now()
        self._stop_preview()
        folder = self.folder
        self._set_busy(True)
        self.open_btn.setVisible(False)
        self._say(f"Renderizando el video ({len(self.project['scenes'])} escenas)…")
        run_task(self, lambda progress: render_project(folder, progress=lambda n, total: progress((n, total))), self._rendered, self._render_failed, self._render_progress)

    def _render_progress(self, step):
        number, total = step
        self.progress.setRange(0, total)
        self.progress.setValue(number)
        self._say(f"Preparando escena {number} de {total} (voz, encuadre y zoom)…")

    def _render_failed(self, error: str):
        self._set_busy(False)
        if self._was_cancelled(error):
            return
        self._say("ERROR: " + error)
        QMessageBox.critical(self, "El render falló", error[-1200:])

    def _rendered(self, report: dict):
        self._set_busy(False)
        self.open_btn.setVisible(True)
        self._say(f"Listo: {report['duration_seconds']} s. " + " ".join(report["warnings"]) + f"\n{report['output']}")


def _install_error_hook():
    """The desktop shortcut has no console: show unexpected errors in a dialog and keep them in data/logs/error.log."""
    log_file = PROJECTS_DIR.parent / "logs" / "error.log"

    def hook(exc_type, exc, tb):
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n{text}\n")
        QMessageBox.critical(None, "Error inesperado", f"{exc_type.__name__}: {exc}\n\nEl detalle completo quedó en:\n{log_file}")

    sys.excepthook = hook


def main():
    if sys.platform == "win32":
        import ctypes
        # Own AppUserModelID so the taskbar shows this app's icon instead of Python's.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Genxapp.VideoFactory")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(str(APP_ROOT / "assets" / "video_factory.ico")))
    _install_error_hook()
    window = StudioWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
