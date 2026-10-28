"""Proyectos por escenas: guion libre, un recurso visual por escena y render con voz por escena.

Un proyecto vive en data/projects/<slug>/ con project.json, assets/, voice/ y render/.
La duración de cada escena la fija su diálogo (voz sintetizada) más una pausa corta.
"""
from __future__ import annotations

import hashlib
import os
import re
import json
import shutil
import subprocess
import sys
import textwrap
import uuid
import wave
from pathlib import Path

from .channels import _AUDIO_FMT, CHANNELS, TARGET_SECONDS, VOICES
from .clips import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from .pipeline import EDGE_TTS_PACKAGES, _find_ffmpeg
from .proc import run
from .storage import APP_ROOT, load_json, now_iso, save_json, slug

PROJECTS_DIR = APP_ROOT / "data" / "projects"
SCENE_PAUSE = 0.35
EMPTY_SCENE_SECONDS = 3.0
CROPS = {
    "fill_9_16": "Llenar el cuadro",
    "4_3_blur": "4:3 sobre fondo difuminado",
    "fit_blur": "Completo sobre fondo difuminado",
}
ZOOM_SPEEDS = {"none": 0.0, "slow": 0.08, "medium": 0.16, "fast": 0.28}
IMAGE_MOTIONS = {
    "none": "Imagen fija",
    "zoom_in": "Zoom suave de acercamiento",
    "zoom_out": "Zoom suave de alejamiento",
    "pan_up": "Paneo de abajo hacia arriba",
    "pan_down": "Paneo de arriba hacia abajo",
    "pan_left": "Paneo de derecha a izquierda",
    "pan_right": "Paneo de izquierda a derecha",
    "zoom_left": "Zoom lateral hacia la izquierda",
    "zoom_right": "Zoom lateral hacia la derecha",
}
TEXT_OVERLAY_DEFAULTS = {"text": "", "position": "top", "size": 64, "color": "#FFFFFF"}
MUSIC_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac"}


SUBTITLE_POSITIONS = {"bottom": ("Default", 2), "middle": ("Middle", 5), "top": ("Top", 8)}


def subtitle_style_line(sub: dict, name: str = "Default", alignment: int = 2, margin_v: int | None = None) -> str:
    """Build an ASS 'Style:' line from the project's subtitle settings."""
    def bgr(color: str) -> str:
        c = color.lstrip("#")
        return f"&H00{c[4:6]}{c[2:4]}{c[0:2]}".upper()
    size = int(sub["size"])
    return f"Style: {name},{sub['font']},{size},{bgr(sub['color'])},&H0000FFFF,{bgr(sub['outline'])},&HAA061018,{1 if sub.get('bold', True) else 0},0,0,0,100,100,0,0,1,{max(4, round(size / 12))},1,{alignment},90,90,{int(sub.get('margin_v', 420) if margin_v is None else margin_v)},1"


_ASS_HEADER = (
    "[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
    "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
    "{style}\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
)


def voice_defaults(voice_key: str) -> dict:
    """Speed (%), pitch (Hz) and volume (%) offsets of a voice preset, as integers."""
    preset = VOICES[voice_key]
    return {"rate": int(preset["rate"].rstrip("%")), "pitch": int(preset["pitch"].removesuffix("Hz")), "volume": 0}


def synthesize_voice(folder: Path, text: str, voice_key: str, settings: dict, ffmpeg: str) -> Path:
    """Return the cached WAV for this text and voice settings, synthesizing it with Edge neural TTS if needed."""
    if not EDGE_TTS_PACKAGES.is_dir():
        raise RuntimeError(f"Falta edge-tts en {EDGE_TTS_PACKAGES}.")
    preset = VOICES[voice_key]
    rate, pitch, volume = f"{settings['rate']:+d}%", f"{settings['pitch']:+d}Hz", f"{settings.get('volume', 0):+d}%"
    key = hashlib.sha256(f"{text}|{preset['voice']}|{rate}|{pitch}|{volume}".encode("utf-8")).hexdigest()[:16]
    wav = folder / "voice" / f"{key}.wav"
    wav.parent.mkdir(exist_ok=True)
    if not wav.is_file():
        proc = run([sys.executable, str(Path(__file__).resolve().parent / "synthesize_neural_voice.py"), "--text", text, "--output", str(wav.with_suffix(".mp3")), "--ffmpeg", ffmpeg, "--voice", preset["voice"], "--rate", rate, "--pitch", pitch, "--volume", volume], capture_output=True, text=True, timeout=180)
        if proc.returncode or not wav.is_file():
            raise RuntimeError(f"No se pudo generar la voz: {(proc.stderr or proc.stdout)[-800:]}")
    return wav


def new_scene(dialogue: str = "", orientation: str = "portrait") -> dict:
    """Empty scene; landscape videos start with subtitles hidden."""
    return {"id": uuid.uuid4().hex[:8], "dialogue": dialogue, "chapter": "", "media": None, "crop": "fill_9_16", "motion": "zoom_in", "zoom": {"speed": "slow", "direction": "in"}, "start": 0.0, "duration": EMPTY_SCENE_SECONDS, "text_overlay": dict(TEXT_OVERLAY_DEFAULTS), "subtitle_pos": "bottom", "show_subtitles": orientation != "landscape", "mute_music": False, "clip_volume": 0.0, "sfx": []}


def create_project(name: str, channel: str | None = None, root: Path | None = None) -> Path:
    channel = channel or last_channel()
    if channel not in CHANNELS:
        raise ValueError(f"Canal desconocido: {channel}")
    folder = (root or PROJECTS_DIR) / f"{slug(name)}-{uuid.uuid4().hex[:4]}"
    (folder / "assets").mkdir(parents=True)
    project = {
        "schema_version": 1, "name": name, "channel": channel, "orientation": "portrait", "voice": CHANNELS[channel]["default_voice"], "voice_settings": voice_defaults(CHANNELS[channel]["default_voice"]),
        "music": {"enabled": True, "gain": CHANNELS[channel]["music_gain"], "path": None}, "outro": CHANNELS[channel]["outro"] is not None, "outro_file": None, "outro_name": None,
        "subtitles": dict(CHANNELS[channel]["subtitles"]), "youtube": {"title": name, "description": "", "tags": []}, "scenes": [new_scene()], "created_at": now_iso(),
    }
    apply_channel_defaults(folder, project)
    save_json(folder / "project.json", project)
    return folder


DEFAULTS_FILE = PROJECTS_DIR.parent / "channel_defaults.json"


def _read_defaults() -> dict:
    try:
        return json.loads(DEFAULTS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"last_channel": None, "channels": {}}


def last_channel() -> str:
    """Channel of the last settings change; new projects start with it."""
    key = _read_defaults().get("last_channel")
    return key if key in CHANNELS else "que-curioso"


def load_search_history() -> list[str]:
    """Search terms used before, most recent first."""
    try:
        return [t for t in json.loads((DEFAULTS_FILE.parent / "search_history.json").read_text(encoding="utf-8")) if isinstance(t, str)]
    except (OSError, ValueError):
        return []


def add_search_term(term: str, limit: int = 20) -> list[str]:
    history = [t for t in load_search_history() if t.casefold() != term.casefold()]
    history = [term.strip(), *history][:limit]
    save_json(DEFAULTS_FILE.parent / "search_history.json", history)
    return history


SHARED_PREFIX = "shared:"
OUTRO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def import_shared(channel: str, source: Path) -> str:
    """Store a music or outro file once per channel (data/channel_defaults/<canal>/) and return a reference every project can share."""
    target_dir = DEFAULTS_FILE.parent / "channel_defaults" / channel
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{slug(source.stem)}{source.suffix.casefold()}"
    if target.exists() and target.stat().st_size != source.stat().st_size:
        target = target_dir / f"{slug(source.stem)}-{uuid.uuid4().hex[:4]}{source.suffix.casefold()}"
    if not target.exists():
        shutil.copy2(source, target)
    return SHARED_PREFIX + target.relative_to(DEFAULTS_FILE.parent).as_posix()


def resolve_asset(folder: Path, reference: str) -> Path:
    """Path of a project file, or of a file shared between projects ('shared:...' references)."""
    if reference.startswith(SHARED_PREFIX):
        return DEFAULTS_FILE.parent / reference[len(SHARED_PREFIX):]
    return folder / reference


SFX_DIR = DEFAULTS_FILE.parent / "sfx_library"
SFX_PRESETS = {
    "Whoosh": "anoisesrc=d=0.8:c=pink:a=0.6,highpass=f=250,lowpass=f=5000,afade=t=in:d=0.4,afade=t=out:st=0.4:d=0.4",
    "Subida": "aevalsrc='0.5*sin(2*PI*(300*t+500*t*t))':d=1:s=48000,afade=t=out:st=0.8:d=0.2",
    "Bajada": "aevalsrc='0.5*sin(2*PI*(1100*t-500*t*t))':d=1:s=48000,afade=t=out:st=0.8:d=0.2",
    "Pop": "sine=f=650:d=0.15:r=48000,afade=t=out:st=0.03:d=0.12",
    "Ding": "sine=f=1318:d=1.2:r=48000,aecho=0.8:0.6:60:0.4,afade=t=out:st=0.2:d=1",
    "Golpe grave": "sine=f=55:d=0.6:r=48000,afade=t=out:st=0.05:d=0.55,volume=3",
    "Tic": "sine=f=2200:d=0.05:r=48000,afade=t=out:st=0.01:d=0.04",
    "Alerta": "aevalsrc='0.5*sin(2*PI*880*t)*lt(mod(t,0.3),0.15)':d=0.9:s=48000",
    "Suspenso": "anoisesrc=d=2.5:c=brown:a=0.8,lowpass=f=800,afade=t=in:d=2.3,afade=t=out:st=2.3:d=0.2",
}


def list_sfx_library(ffmpeg: str | None) -> list[tuple[str, str]]:
    """(label, reference) of every sound effect in data/sfx_library, creating the built-in ones with FFmpeg when missing."""
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    for name, source in SFX_PRESETS.items():
        target = SFX_DIR / f"{slug(name)}.wav"
        if ffmpeg and not target.is_file():
            run([ffmpeg, "-y", "-f", "lavfi", "-i", source, "-ar", "48000", "-ac", "2", str(target)], capture_output=True, text=True, timeout=60)
    files = sorted(p for p in SFX_DIR.iterdir() if p.suffix.casefold() in MUSIC_EXTENSIONS)
    return [(p.stem.replace("-", " ").capitalize(), f"{SHARED_PREFIX}sfx_library/{p.name}") for p in files]


def import_sfx(source: Path) -> str:
    """Copy a sound effect into the shared library and return its reference."""
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    target = SFX_DIR / f"{slug(source.stem)}{source.suffix.casefold()}"
    if target.exists() and target.stat().st_size != source.stat().st_size:
        target = SFX_DIR / f"{slug(source.stem)}-{uuid.uuid4().hex[:4]}{source.suffix.casefold()}"
    if not target.exists():
        shutil.copy2(source, target)
    return f"{SHARED_PREFIX}sfx_library/{target.name}"


def _shared_reference(folder: Path, channel: str, reference: str | None) -> str | None:
    """Turn a project-owned file (older projects) into a shared one; shared references are kept as they are."""
    if not reference or reference.startswith(SHARED_PREFIX):
        return reference
    owned = folder / reference
    return import_shared(channel, owned) if owned.is_file() else None


def remember_channel_defaults(folder: Path, project: dict) -> None:
    """Keep the project's voice, subtitles, music and outro as the starting point of the next project of this channel."""
    data = _read_defaults()
    data.setdefault("channels", {})
    music = project["music"]
    data["channels"][project["channel"]] = {
        "voice": project["voice"], "voice_settings": dict(project["voice_settings"]), "outro": project["outro"], "subtitles": dict(project["subtitles"]),
        "outro_file": _shared_reference(folder, project["channel"], project.get("outro_file")), "outro_name": project.get("outro_name"),
        "music": {"enabled": music["enabled"], "gain": music["gain"], "name": music.get("name"), "file": _shared_reference(folder, project["channel"], music["path"])},
    }
    data["last_channel"] = project["channel"]
    save_json(DEFAULTS_FILE, data)


def apply_channel_defaults(folder: Path, project: dict) -> bool:
    """Replace the project's channel settings with the saved ones; returns False if nothing was saved for this channel."""
    entry = _read_defaults().get("channels", {}).get(project["channel"])
    if not entry or entry.get("voice") not in VOICES:
        return False
    project["voice"] = entry["voice"]
    project["voice_settings"] = {**voice_defaults(entry["voice"]), **entry.get("voice_settings", {})}
    project["outro"] = bool(entry.get("outro"))
    project["subtitles"] = {**CHANNELS[project["channel"]]["subtitles"], **entry.get("subtitles", {})}
    saved = entry.get("music", {})
    project["music"].update({"enabled": bool(saved.get("enabled", True)), "gain": saved.get("gain", project["music"]["gain"]), "path": None, "name": None})
    if saved.get("file") and resolve_asset(folder, saved["file"]).is_file():
        project["music"].update({"path": saved["file"], "name": saved.get("name")})
    project["outro_file"], project["outro_name"] = None, None
    if entry.get("outro_file") and resolve_asset(folder, entry["outro_file"]).is_file():
        project["outro_file"], project["outro_name"] = entry["outro_file"], entry.get("outro_name")
    return True


def load_project(folder: Path) -> dict:
    project = load_json(folder / "project.json")
    project.pop("subtitle_style", None)
    project.setdefault("voice_settings", voice_defaults(project["voice"]))
    project.setdefault("outro_file", None)
    project.setdefault("outro_name", None)
    project.setdefault("subtitles", dict(CHANNELS[project["channel"]]["subtitles"]))
    project.setdefault("orientation", "portrait")
    project.setdefault("youtube", {"title": project["name"], "description": "", "tags": []})
    project["youtube"].setdefault("title", project["name"])
    project["youtube"].setdefault("description", "")
    project["youtube"].setdefault("tags", [])
    project["music"].setdefault("path", None)
    for scene in project.get("scenes", []):
        scene.setdefault("zoom", {"speed": "slow", "direction": "in"})
        scene.setdefault("mute_music", False)
        scene.setdefault("clip_volume", 0.0)
        scene.setdefault("sfx", [])
        scene["text_overlay"] = {**TEXT_OVERLAY_DEFAULTS, **(scene.get("text_overlay") or {})}
        if scene.get("motion") not in IMAGE_MOTIONS:
            speed = scene["zoom"].get("speed", "slow")
            direction = scene["zoom"].get("direction", "in")
            scene["motion"] = "none" if speed == "none" else "zoom_out" if direction == "out" else "zoom_in"
    return project


def write_credits(folder: Path, project: dict) -> Path:
    """Write creditos.txt with the source, author and license of every bank-sourced image or video in use."""
    used = {}
    for scene in project["scenes"]:
        media = scene.get("media")
        if media and media.get("provider") != "Archivo propio":
            used.setdefault(media["path"], media)
    lines = ["CRÉDITOS DE IMÁGENES Y VIDEOS", f"Proyecto: {project['name']}", f"Actualizado: {now_iso()}", ""]
    for number, media in enumerate(used.values(), start=1):
        lines.append(f"{number}. {media['provider']} — {media.get('author') or 'Autor no informado'} ({'imagen' if media.get('type') == 'image' else 'video'})")
        for label, key in (("Título", "title"), ("Enlace", "page_url"), ("Licencia", "license"), ("Términos", "license_url"), ("Atribución sugerida", "attribution")):
            if media.get(key):
                lines.append(f"   {label}: {media[key]}")
        lines.append("")
    if not used:
        lines.append("Este proyecto todavía no usa imágenes ni videos de bancos.")
    lines.append("Verifica los términos vigentes de cada banco antes de publicar.")
    target = folder / "creditos.txt"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def save_project(folder: Path, project: dict) -> None:
    project["updated_at"] = now_iso()
    save_json(folder / "project.json", project)
    write_credits(folder, project)


def import_media(folder: Path, source: Path) -> str:
    """Copy a file (image, video or music) into the project's assets folder and return its project-relative path."""
    target = folder / "assets" / f"{uuid.uuid4().hex[:6]}_{slug(source.stem)}{source.suffix.casefold()}"
    shutil.copy2(source, target)
    return target.relative_to(folder).as_posix()


def load_library(folder: Path) -> dict:
    """Credits and source data of the media downloaded into this project, keyed by project-relative path."""
    try:
        return json.loads((folder / "assets" / "library.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def register_asset(folder: Path, media: dict) -> None:
    library = load_library(folder)
    library[media["path"]] = media
    save_json(folder / "assets" / "library.json", library)


def list_assets(folder: Path) -> list[dict]:
    """Media dicts for every image and video in the project's assets folder, newest first.

    Files downloaded from a bank keep their author and license; anything else counts as the user's own.
    """
    library = load_library(folder)
    for scene in load_project(folder)["scenes"]:
        if scene.get("media"):
            library.setdefault(scene["media"]["path"], scene["media"])
    assets = folder / "assets"
    files = [f for f in assets.iterdir() if f.is_file() and not f.name.endswith(".thumb.jpg") and f.suffix.casefold() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS] if assets.is_dir() else []
    result = []
    for file in sorted(files, key=lambda f: f.stat().st_mtime, reverse=True):
        rel = file.relative_to(folder).as_posix()
        kind = "image" if file.suffix.casefold() in IMAGE_EXTENSIONS else "video"
        entry = dict(library.get(rel) or {"path": rel, "type": kind, "provider": "Archivo propio", "author": "Aportado por el usuario", "page_url": ""})
        thumb = file.with_suffix(".thumb.jpg")
        entry["thumb"] = thumb.relative_to(folder).as_posix() if thumb.is_file() else None
        result.append(entry)
    return result


def make_thumbnail(ffmpeg: str, media: Path, target: Path) -> Path:
    """Write a small JPEG preview (first frame for videos) and return its path."""
    proc = run([ffmpeg, "-y", "-ss", "0.5" if media.suffix.casefold() in {".mp4", ".mov", ".mkv", ".webm"} else "0", "-i", str(media), "-frames:v", "1", "-vf", "scale=640:-2", str(target)], capture_output=True, text=True, timeout=60)
    if proc.returncode or not target.is_file():
        proc = run([ffmpeg, "-y", "-i", str(media), "-frames:v", "1", "-vf", "scale=640:-2", str(target)], capture_output=True, text=True, timeout=60)
    return target


def extract_frame(ffmpeg: str, media: Path, second: float, target: Path) -> Path:
    """Write the video frame at `second` as a 640 px wide JPEG (used to preview the chosen start of a clip)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    proc = run([ffmpeg, "-y", "-ss", f"{second:.2f}", "-i", str(media), "-frames:v", "1", "-vf", "scale=640:-2", str(target)], capture_output=True, text=True, timeout=60)
    if proc.returncode or not target.is_file():
        raise RuntimeError(f"No hay un fotograma en el segundo {second:.1f} de este video.")
    return target


def estimate_seconds(dialogue: str, fallback: float = EMPTY_SCENE_SECONDS, extra_seconds: float = 0.0) -> float:
    """Rough scene length before the voice exists: ~2.6 spoken words per second plus the pause."""
    words = len(dialogue.split())
    base = round(words / 2.6 + SCENE_PAUSE, 1) if words else fallback
    return round(base + max(0.0, float(extra_seconds)), 1)


def split_script(text: str) -> list[str]:
    """Split a pasted script into scene dialogues: one per blank-line separated paragraph."""
    paragraphs = [" ".join(p.split()) for p in text.replace("\r", "").split("\n\n")]
    return [p for p in paragraphs if p]


def _frame_graph(crop: str, k: int = 1, orientation: str = "portrait") -> str:
    """Filter graph that turns input 0 into a portrait or landscape frame labelled [l]."""
    width, height = (1920, 1080) if orientation == "landscape" else (1080, 1920)
    w, h = width * k, height * k
    blur = f"[0:v]split[bg][fg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur={28 * k}:{10 * k},eq=brightness=-0.18:saturation=0.78[b];"
    if crop == "4_3_blur":
        window_w, window_h = (1440, 1080) if orientation == "landscape" else (1080, 810)
        return blur + f"[fg]scale={window_w * k}:{window_h * k}:force_original_aspect_ratio=increase,crop={window_w * k}:{window_h * k}[f];[b][f]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[l]"
    if crop == "fit_blur":
        return blur + f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[f];[b][f]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[l]"
    return f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,setsar=1[l]"


def wrap_width_for(size: int, width: int = 1080) -> int:
    """Characters per caption line so subtitles fit inside the output frame."""
    return max(8, int((width - 180) / (int(size) * 0.52)))


def caption_chunks(text: str, max_chars: int) -> list[str]:
    """Group words into caption chunks of at most max_chars characters."""
    chunks, current = [], ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > max_chars:
            chunks.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    return chunks + [current] if current else chunks


def _stamp(seconds: float) -> str:
    whole = int(seconds)
    return f"{whole // 3600}:{(whole // 60) % 60:02d}:{whole % 60:02d}.{int((seconds - whole) * 100):02d}"


def _media_info(ffmpeg: str, media: Path) -> tuple[bool, float]:
    """Whether a media file has an audio track, and its duration in seconds."""
    text = run([ffmpeg, "-hide_banner", "-i", str(media)], capture_output=True, text=True, timeout=60).stderr
    match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", text)
    seconds = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3)) if match else 2.0
    return "Audio:" in text, seconds


def _write_concat_list(target: Path, files: list[Path]) -> None:
    """Write an FFmpeg concat-demuxer list, escaping paths with spaces or quotes."""
    entries = []
    for path in files:
        escaped = str(path.resolve()).replace("\\", "/").replace("'", "'\\''")
        entries.append(f"file '{escaped}'\n")
    target.write_text("".join(entries), encoding="utf-8")


def _chapter_timestamp(seconds: float) -> str:
    value = max(0, int(seconds))
    hours, remainder = divmod(value, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def write_youtube_metadata(folder: Path, project: dict, chapters: list[tuple[float, str]], duration: float) -> Path:
    """Write editable YouTube title, description, tags and eligible chapter markers beside the render."""
    youtube = project.get("youtube", {})
    title = (youtube.get("title") or project["name"]).strip()
    description = (youtube.get("description") or "").strip()
    tags = youtube.get("tags") or []
    valid = []
    for start, label in chapters:
        if not label or (valid and start - valid[-1][0] < 10):
            continue
        valid.append((start, label))
    while len(valid) > 1 and duration - valid[-1][0] < 10:
        valid.pop()
    chapter_text = "\n".join(f"{_chapter_timestamp(start)} {label}" for start, label in valid) if len(valid) >= 3 else "No hay suficientes capítulos elegibles. YouTube requiere al menos 3 marcas, empezando en 0:00 y con segmentos de 10 segundos o más."
    description_with_chapters = "\n\n".join(part for part in (description, chapter_text if len(valid) >= 3 else "") if part)
    lines = ["DATOS PARA YOUTUBE", "", "Título:", title, "", "Descripción para pegar en YouTube:", description_with_chapters or "(sin descripción)", "", "Etiquetas:", ", ".join(str(tag).strip() for tag in tags if str(tag).strip()) or "(sin etiquetas)", "", "Capítulos:", chapter_text]
    target = folder / "youtube_metadata.txt"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def _image_motion_graph(motion: str, amount: float, width: int, height: int, frames: int) -> str:
    """Build a smooth perspective animation; all coordinates stay inside the fitted frame."""
    if motion in {"zoom_in", "zoom_out"}:
        z = f"(1+{amount}*in/{frames})" if motion == "zoom_in" else f"({1 + amount}-{amount}*in/{frames})"
        x0, y0 = f"({width}-{width}/{z})/2", f"({height}-{height}/{z})/2"
        x1, y2 = f"{width}-{x0}", f"{height}-{y0}"
    else:
        z = f"(1+{amount})"
        progress = f"(1-cos(PI*min(1,in/{max(1, frames - 1)})))/2"
        travel_x, travel_y = f"({width}-{width}/{z})", f"({height}-{height}/{z})"
        center_x, center_y = f"({width}-{width}/{z})/2", f"({height}-{height}/{z})/2"
        x0, y0 = center_x, center_y
        if motion in {"pan_right", "zoom_right"}:
            x0 = f"{travel_x}*{progress}"
        elif motion in {"pan_left", "zoom_left"}:
            x0 = f"{travel_x}*(1-{progress})"
        elif motion == "pan_down":
            y0 = f"{travel_y}*{progress}"
        elif motion == "pan_up":
            y0 = f"{travel_y}*(1-{progress})"
        x1, y2 = f"{x0}+{width}/{z}", f"{y0}+{height}/{z}"
    return f"perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y2}':x3='{x1}':y3='{y2}':eval=frame:interpolation=cubic"


def _fill_pan_graph(motion: str, amount: float, width: int, height: int, frames: int) -> str:
    """Pan across the full overfilled still, anchoring vertical pans to its true edges."""
    progress = f"(1-cos(PI*min(1,n/{max(1, frames - 1)})))/2"
    # The still retains the complete image plus a restrained overscan. Cropping it
    # dynamically means a portrait source can travel from its actual bottom/top,
    # instead of animating inside an already center-cropped landscape frame.
    x = "(iw-ow)/2"
    y = "(ih-oh)/2"
    if motion == "pan_up":
        y = f"(ih-oh)*(1-{progress})"
    elif motion == "pan_down":
        y = f"(ih-oh)*{progress}"
    elif motion in {"pan_left", "zoom_left"}:
        x = f"(iw-ow)*(1-{progress})"
    elif motion in {"pan_right", "zoom_right"}:
        x = f"(iw-ow)*{progress}"
    return f"crop={width}:{height}:x='{x}':y='{y}':exact=1,fps=30,scale={width // 2}:{height // 2}:flags=lanczos,setsar=1"


def render_project(folder: Path, ffmpeg_explicit: str | None = None, progress=None, only_scene: int | None = None, only_scenes: list[int] | None = None, force_preview: bool = False) -> dict:
    """Render the project into render/video.mp4, or a quick low-resolution scene preview."""
    project = load_project(folder)
    preview = only_scene is not None or only_scenes is not None
    indices = only_scenes if only_scenes is not None else [only_scene] if only_scene is not None else None
    if indices is not None and any(index < 0 or index >= len(project["scenes"]) for index in indices):
        raise IndexError("Una de las escenas solicitadas para la vista previa no existe.")
    scenes = [project["scenes"][index] for index in indices] if indices is not None else project["scenes"]
    if not scenes:
        raise ValueError("El proyecto no tiene escenas.")
    for number, scene in enumerate(scenes, start=1):
        if not scene.get("media") or not (folder / scene["media"]["path"]).is_file():
            raise FileNotFoundError(f"La escena {number} no tiene un recurso visual válido.")

    channel = CHANNELS[project["channel"]]
    preview_cache = None
    if preview:
        asset_paths = [folder / scene["media"]["path"] for scene in scenes]
        music_ref = project["music"].get("path")
        music_path = resolve_asset(folder, music_ref) if music_ref else channel["music"]
        if music_path:
            asset_paths.append(Path(music_path))
        asset_paths += [resolve_asset(folder, fx["path"]) for scene in scenes for fx in scene.get("sfx", [])]
        assets = []
        for path in asset_paths:
            try:
                stat = path.stat()
                assets.append((str(path.resolve()), stat.st_size, stat.st_mtime_ns))
            except OSError:
                assets.append((str(path), None, None))
        cache_data = {
            "version": 1,
            "orientation": project.get("orientation", "portrait"),
            "voice": project["voice"],
            "voice_settings": project["voice_settings"],
            "subtitles": project["subtitles"],
            "music": project["music"],
            "scenes": scenes,
            "assets": assets,
        }
        cache_key = hashlib.sha256(json.dumps(cache_data, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        cache_dir = folder / "render" / "preview" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        preview_cache = cache_dir / f"{cache_key}.mp4"
        if preview_cache.is_file() and preview_cache.stat().st_size and not force_preview:
            return {"status": "preview", "output": str(preview_cache), "duration_seconds": None, "cache_hit": True}

    ffmpeg = ffmpeg_explicit or _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("No encuentro FFmpeg; instálalo o agrégalo al PATH.")
    preset = VOICES[project["voice"]]
    if any(s["dialogue"].strip() for s in scenes) and not EDGE_TTS_PACKAGES.is_dir():
        raise RuntimeError(f"Falta edge-tts en {EDGE_TTS_PACKAGES}.")

    out_dir = folder / "render" / "preview" if preview else folder / "render"
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir / f".work-{uuid.uuid4().hex[:8]}"
    (work_dir / "scenes").mkdir(parents=True)
    (folder / "voice").mkdir(exist_ok=True)
    sub = project["subtitles"]
    orientation = project.get("orientation", "portrait")
    frame_width, frame_height = (1920, 1080) if orientation == "landscape" else (1080, 1920)
    subtitle_settings = dict(sub)
    if orientation == "landscape":
        subtitle_settings["size"] = round(int(sub["size"]) * 0.72)
        subtitle_settings["margin_v"] = 120
    style_line = "\n".join([subtitle_style_line(subtitle_settings), subtitle_style_line(subtitle_settings, "Middle", 5, 0), subtitle_style_line(subtitle_settings, "Top", 8, 146 if orientation == "landscape" else 260)])
    wrap_width = wrap_width_for(subtitle_settings["size"], frame_width)
    overlay_styles, overlay_data = [], {}
    for scene_number, scene in enumerate(scenes, start=1):
        overlay = {**TEXT_OVERLAY_DEFAULTS, **scene.get("text_overlay", {})}
        text = str(overlay["text"]).strip()
        if not text:
            continue
        style_name = f"SceneText{scene_number}"
        position = overlay["position"]
        alignment = {"top": 8, "middle": 5, "bottom": 2}.get(position, 8)
        margin_v = (146 if orientation == "landscape" else 260) if position == "top" else 0 if position == "middle" else (120 if orientation == "landscape" else int(sub.get("margin_v", 420)))
        overlay_style = dict(subtitle_settings)
        overlay_style.update({"size": round(int(overlay["size"]) * (0.72 if orientation == "landscape" else 1)), "color": overlay["color"], "bold": True})
        overlay_styles.append(subtitle_style_line(overlay_style, style_name, alignment, margin_v))
        overlay_size = overlay_style["size"]
        overlay_width = wrap_width_for(overlay_size, frame_width)
        safe_text = text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")
        lines = []
        for paragraph in safe_text.splitlines() or [safe_text]:
            lines.extend(textwrap.wrap(paragraph, width=overlay_width, break_long_words=False) or [""])
        overlay_data[scene_number] = (style_name, "\\N".join(lines))
    k = 1 if preview else 2
    ass_lines, scene_videos, scene_audios, records, cursor = [_ASS_HEADER.format(width=frame_width, height=frame_height, style="\n".join([style_line, *overlay_styles]))], [], [], [], 0.0
    chapter_starts = [(0.0, (project.get("youtube", {}).get("title") or project["name"]).strip())]
    warnings, muted_spans = [], []
    for number, scene in enumerate(scenes, start=1):
        if progress:
            progress(number, len(scenes))
        chapter = (scene.get("chapter") or "").strip().replace("\n", " ")
        if chapter:
            chapter_starts.append((cursor, chapter))
        dialogue = scene["dialogue"].strip()
        if dialogue:
            try:
                wav = synthesize_voice(folder, dialogue, project["voice"], project["voice_settings"], ffmpeg)
            except RuntimeError as exc:
                raise RuntimeError(f"Escena {number}: {exc}") from exc
            with wave.open(str(wav), "rb") as audio:
                length = audio.getnframes() / audio.getframerate() + SCENE_PAUSE + max(0.0, float(scene.get("extra_seconds", 0)))
            audio_input = ["-i", str(wav)]
        else:
            length = float(scene.get("duration") or EMPTY_SCENE_SECONDS) + max(0.0, float(scene.get("extra_seconds", 0)))
            audio_input = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        audio_out = work_dir / "scenes" / f"scene-{number:04d}.wav"
        sfx_input, sfx_graph = [], []
        for fx in scene.get("sfx", []):
            sfx_file = resolve_asset(folder, fx["path"])
            if not sfx_file.is_file() or not 0 <= float(fx["at"]) < length:
                warnings.append(f"Escena {number}: se omitió el efecto {Path(fx['path']).name} (falta el archivo o su segundo cae fuera de la escena).")
                continue
            sfx_input += ["-i", str(sfx_file)]
            delay = round(float(fx["at"]) * 1000)
            sfx_graph.append(f"[{len(sfx_graph) + 1}:a]{_AUDIO_FMT},adelay={delay}|{delay},volume={float(fx.get('gain', 1.0))}[s{len(sfx_graph)}]")
        clip_volume = float(scene.get("clip_volume") or 0)
        if clip_volume > 0 and scene["media"].get("type") != "image":
            clip_file = folder / scene["media"]["path"]
            if _media_info(ffmpeg, clip_file)[0]:
                sfx_input += ["-stream_loop", "-1", "-ss", f"{float(scene.get('start') or 0):.3f}", "-i", str(clip_file)]
                sfx_graph.append(f"[{len(sfx_graph) + 1}:a:0]{_AUDIO_FMT},volume={clip_volume}[s{len(sfx_graph)}]")
            else:
                warnings.append(f"Escena {number}: el clip de video no tiene audio.")
        mix = "".join(f"[s{i}]" for i in range(len(sfx_graph)))
        audio_graph = ";".join([f"[0:a]{_AUDIO_FMT},apad=whole_dur={length:.4f}[voice]", *sfx_graph, f"[voice]{mix}amix=inputs={len(sfx_graph) + 1}:duration=first:dropout_transition=0:normalize=0[out]"])
        proc = run([ffmpeg, "-y", *audio_input, *sfx_input, "-filter_complex", audio_graph, "-map", "[out]", "-t", f"{length:.4f}", str(audio_out)], capture_output=True, text=True, timeout=max(120, int(length * 10)))
        if proc.returncode or not audio_out.is_file():
            raise RuntimeError(f"Falló el audio de la escena {number}: {proc.stderr[-800:]}")
        scene_audios.append(audio_out)

        media = folder / scene["media"]["path"]
        is_image = scene["media"].get("type") == "image"
        motion = scene.get("motion")
        if motion not in IMAGE_MOTIONS:
            motion = "none" if scene["zoom"].get("speed") == "none" else "zoom_out" if scene["zoom"].get("direction") == "out" else "zoom_in"
        speed = ZOOM_SPEEDS.get(scene["zoom"].get("speed", "slow"), ZOOM_SPEEDS["slow"])
        if is_image and motion != "none" and speed:
            # perspective interpolates at sub-pixel positions; zoompan rounds to whole pixels and shakes.
            frames = max(1, round(length * 30))
            motion_k = max(k, 2) if scene["crop"] == "fill_9_16" and motion.startswith("pan_") else k
            motion_w, motion_h = frame_width * motion_k, frame_height * motion_k
            fitted = work_dir / "scenes" / f"scene-{number:04d}-frame.png"
            if scene["crop"] == "fill_9_16" and motion.startswith("pan_"):
                # Keep all source content at the output width. The animated crop
                # later moves through the true overfill (e.g. portrait top to bottom).
                overscan = 1 + speed
                if orientation == "landscape" and motion in {"pan_up", "pan_down"}:
                    prepare_graph = f"[0:v]scale={motion_w}:-2:flags=lanczos,scale='ceil(iw*{overscan}/2)*2':'ceil(ih*{overscan}/2)*2':flags=lanczos,setsar=1[o]"
                else:
                    prepare_graph = f"[0:v]scale='ceil(iw*max({motion_w}/iw,{motion_h}/ih)*{overscan}/2)*2':'ceil(ih*max({motion_w}/iw,{motion_h}/ih)*{overscan}/2)*2':flags=lanczos,setsar=1[o]"
                motion_graph = _fill_pan_graph(motion, speed, motion_w, motion_h, frames)
            else:
                # Fit the photo once into the frame; the zoom then only resamples that small still.
                prepare_graph = _frame_graph(scene["crop"], k, orientation).replace("fps=30,", "").replace("[l]", "[o]")
                motion_graph = _image_motion_graph(motion, speed, frame_width * k, frame_height * k, frames)
            proc = run([ffmpeg, "-y", "-i", str(media), "-filter_complex", prepare_graph, "-map", "[o]", "-frames:v", "1", str(fitted)], capture_output=True, text=True, timeout=300)
            if proc.returncode or not fitted.is_file():
                raise RuntimeError(f"No se pudo preparar la imagen de la escena {number}: {proc.stderr[-800:]}")
            media = fitted
            if scene["crop"] == "fill_9_16" and motion.startswith("pan_"):
                graph = f"[0:v]{motion_graph}[v]"
            else:
                graph = f"[0:v]{motion_graph},scale={frame_width}:{frame_height}:flags=lanczos,setsar=1[v]"
        else:
            graph = _frame_graph(scene["crop"], orientation=orientation) + ";[l]null[v]"
        input_args = ["-loop", "1", "-framerate", "30", "-i", str(media)] if is_image else ["-stream_loop", "-1", "-ss", f"{float(scene.get('start') or 0):.3f}", "-i", str(media)]
        video_out = work_dir / "scenes" / f"scene-{number:04d}.mp4"
        # Mixed color tags between scenes make FFmpeg rebuild the final filter graph mid-video, dropping frames.
        graph += ";[v]setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv[vt]"
        proc = run([ffmpeg, "-y", *input_args, "-t", f"{length:.4f}", "-an", "-filter_complex", graph, "-map", "[vt]", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "28" if preview else "18", "-pix_fmt", "yuv420p", str(video_out)], capture_output=True, text=True, timeout=max(300, int(length * 60)))
        if proc.returncode or not video_out.is_file():
            raise RuntimeError(f"Falló el video de la escena {number}: {proc.stderr[-1200:]}")
        scene_videos.append(video_out)

        spoken = length - SCENE_PAUSE if dialogue else 0
        chunks = caption_chunks(dialogue, wrap_width * 2)
        total_words = max(1, sum(len(c.split()) for c in chunks))
        offset = cursor
        if number in overlay_data:
            style_name, overlay_text = overlay_data[number]
            ass_lines.append(f"Dialogue: 0,{_stamp(cursor)},{_stamp(cursor + length)},{style_name},,0,0,0,,{overlay_text}\n")
        for chunk in chunks if scene.get("show_subtitles", True) else []:
            span = spoken * len(chunk.split()) / total_words
            text = "\\N".join(textwrap.wrap(chunk.replace("{", "(").replace("}", ")"), width=wrap_width, break_long_words=False))
            ass_lines.append(f"Dialogue: 0,{_stamp(offset)},{_stamp(offset + span)},{SUBTITLE_POSITIONS.get(scene.get('subtitle_pos'), SUBTITLE_POSITIONS['bottom'])[0]},,0,0,0,,{text}\n")
            offset += span
        if scene.get("mute_music"):
            muted_spans.append((cursor, cursor + length))
        cursor += length
        records.append({"scene": number, "seconds": round(length, 2), "media": scene["media"]["path"], "crop": scene["crop"], "zoom": scene["zoom"] if is_image else None})

    total = cursor
    if progress:
        progress(0, len(scenes))
    video_list = work_dir / "video-concat.txt"
    audio_list = work_dir / "audio-concat.txt"
    _write_concat_list(video_list, scene_videos)
    _write_concat_list(audio_list, scene_audios)
    joined_video = work_dir / "joined-video.mp4"
    proc = run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(video_list), "-c", "copy", str(joined_video)], capture_output=True, text=True, timeout=max(600, int(total * 5)))
    if proc.returncode or not joined_video.is_file() or joined_video.stat().st_size == 0:
        raise RuntimeError(f"No se pudieron concatenar las escenas de video: {proc.stderr[-1200:]}")
    for video in scene_videos:
        video.unlink(missing_ok=True)

    ass = work_dir / "captions.ass"
    ass.write_text("".join(ass_lines), encoding="utf-8-sig")
    ass_filter = str(ass.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    music = resolve_asset(folder, project["music"]["path"]) if project["music"]["path"] else channel["music"]
    outro = resolve_asset(folder, project["outro_file"]) if project["outro_file"] else channel["outro"]
    use_music = bool(project["music"]["enabled"] and music and music.is_file())
    use_outro = bool(not preview and project["outro"] and outro and outro.is_file())
    cmd = [ffmpeg, "-y", "-i", str(joined_video), "-f", "concat", "-safe", "0", "-i", str(audio_list)]
    preview_scale = ",scale=960:540" if orientation == "landscape" else ",scale=540:960"
    graph = [f"[0:v:0]tpad=stop_mode=clone:stop_duration=1,trim=duration={total:.6f},setpts=PTS-STARTPTS,subtitles='{ass_filter}'{preview_scale if preview else ''}[main_video]", f"[1:a:0]apad=pad_dur=1,atrim=duration={total:.6f},asetpts=PTS-STARTPTS[voice]"]
    next_input = 2
    if use_music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        silence = "".join(f",volume=0:enable='between(t,{start:.3f},{end:.3f})'" for start, end in muted_spans)
        graph += [f"[{next_input}:a:0]atrim=duration={total:.6f},asetpts=PTS-STARTPTS,{_AUDIO_FMT},volume={project['music']['gain']}{silence},afade=t=out:st={max(0.0, total - 3):.3f}:d=3[bed]", "[voice][bed]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[main_audio]"]
        next_input += 1
    else:
        graph.append("[voice]anull[main_audio]")
    if use_outro:
        cmd += ["-i", str(outro)]
        has_audio, outro_seconds = _media_info(ffmpeg, outro)
        outro_audio = f"[{next_input}:a:0]{_AUDIO_FMT}[outro_a]" if has_audio else f"anullsrc=r=48000:cl=stereo:d={outro_seconds:.3f},{_AUDIO_FMT}[outro_a]"
        graph += [f"[{next_input}:v:0]scale={frame_width}:{frame_height}:force_original_aspect_ratio=increase,crop={frame_width}:{frame_height},fps=30,setsar=1[outro_v]", outro_audio, "[main_video][outro_v]concat=n=2:v=1:a=0[final_video]", "[main_audio][outro_a]concat=n=2:v=0:a=1[final_audio]"]
        maps = ["-map", "[final_video]", "-map", "[final_audio]"]
    else:
        maps = ["-map", "[main_video]", "-map", "[main_audio]"]
    output = preview_cache if preview else out_dir / "video.mp4"
    partial = output.with_name(output.stem + ".part.mp4")
    cmd += ["-filter_complex", ";".join(graph), *maps, "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "2M" if preview else "8M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(partial)]
    try:
        proc = run(cmd, capture_output=True, text=True, timeout=max(1800, int(total * 30)))
        if proc.returncode or not partial.is_file():
            raise RuntimeError("Falló el render final: " + proc.stderr[-3000:])
        os.replace(partial, output)
    finally:
        partial.unlink(missing_ok=True)
    if preview:
        shutil.copy2(ass, out_dir / "captions.ass")
        shutil.rmtree(work_dir, ignore_errors=True)
        return {"status": "preview", "output": str(output), "duration_seconds": round(total, 2), "cache_hit": False}

    shutil.copy2(write_credits(folder, project), out_dir / "creditos.txt")
    shutil.copy2(ass, out_dir / "captions.ass")
    metadata = write_youtube_metadata(out_dir, project, chapter_starts, total)
    if orientation == "portrait" and abs(total - TARGET_SECONDS) > 5:
        warnings.append(f"La duración del guion ({total:.1f} s) se aleja del objetivo de {TARGET_SECONDS} s.")
    if project["music"]["enabled"] and not use_music:
        warnings.append(f"Sin música de fondo: no existe {music}.")
    if project["outro"] and not use_outro:
        warnings.append(f"Sin outro: no existe {outro}.")
    report = {"status": "rendered", "output": str(output), "youtube_metadata": str(metadata), "orientation": orientation, "resolution": f"{frame_width}x{frame_height}", "duration_seconds": round(total, 2), "target_seconds": TARGET_SECONDS, "scenes": records, "warnings": warnings, "rendered_at": now_iso()}
    save_json(out_dir / "render.json", report)
    shutil.rmtree(work_dir, ignore_errors=True)
    return report
