"""Proyectos por escenas: guion libre, un recurso visual por escena y render con voz por escena.

Un proyecto vive en data/projects/<slug>/ con project.json, assets/, voice/ y render/.
La duración de cada escena la fija su diálogo (voz sintetizada) más una pausa corta.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import textwrap
import uuid
import wave
from pathlib import Path

from .channels import _AUDIO_FMT, CHANNELS, TARGET_SECONDS, VOICES
from .pipeline import EDGE_TTS_PACKAGES, _find_ffmpeg
from .storage import APP_ROOT, load_json, now_iso, save_json, slug

PROJECTS_DIR = APP_ROOT / "data" / "projects"
SCENE_PAUSE = 0.35
EMPTY_SCENE_SECONDS = 3.0
CROPS = {
    "fill_9_16": "9:16 relleno",
    "4_3_blur": "4:3 sobre fondo difuminado",
    "fit_blur": "Completo sobre fondo difuminado",
}
ZOOM_SPEEDS = {"none": 0.0, "slow": 0.08, "medium": 0.16, "fast": 0.28}
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
    "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
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
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "synthesize_neural_voice.py"), "--text", text, "--output", str(wav.with_suffix(".mp3")), "--ffmpeg", ffmpeg, "--voice", preset["voice"], "--rate", rate, "--pitch", pitch, "--volume", volume], capture_output=True, text=True, timeout=180)
        if proc.returncode or not wav.is_file():
            raise RuntimeError(f"No se pudo generar la voz: {(proc.stderr or proc.stdout)[-800:]}")
    return wav


def new_scene(dialogue: str = "") -> dict:
    return {"id": uuid.uuid4().hex[:8], "dialogue": dialogue, "media": None, "crop": "fill_9_16", "zoom": {"speed": "slow", "direction": "in"}, "start": 0.0, "duration": EMPTY_SCENE_SECONDS, "subtitle_pos": "bottom", "show_subtitles": True}


def create_project(name: str, channel: str = "que-curioso", root: Path | None = None) -> Path:
    if channel not in CHANNELS:
        raise ValueError(f"Canal desconocido: {channel}")
    folder = (root or PROJECTS_DIR) / f"{slug(name)}-{uuid.uuid4().hex[:4]}"
    (folder / "assets").mkdir(parents=True)
    save_json(folder / "project.json", {
        "schema_version": 1, "name": name, "channel": channel, "voice": CHANNELS[channel]["default_voice"], "voice_settings": voice_defaults(CHANNELS[channel]["default_voice"]),
        "music": {"enabled": True, "gain": CHANNELS[channel]["music_gain"], "path": None}, "outro": CHANNELS[channel]["outro"] is not None,
        "subtitles": dict(CHANNELS[channel]["subtitles"]), "scenes": [new_scene()], "created_at": now_iso(),
    })
    return folder


def load_project(folder: Path) -> dict:
    project = load_json(folder / "project.json")
    project.pop("subtitle_style", None)
    project.setdefault("voice_settings", voice_defaults(project["voice"]))
    project.setdefault("subtitles", dict(CHANNELS[project["channel"]]["subtitles"]))
    project["music"].setdefault("path", None)
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


def make_thumbnail(ffmpeg: str, media: Path, target: Path) -> Path:
    """Write a small JPEG preview (first frame for videos) and return its path."""
    proc = subprocess.run([ffmpeg, "-y", "-ss", "0.5" if media.suffix.casefold() in {".mp4", ".mov", ".mkv", ".webm"} else "0", "-i", str(media), "-frames:v", "1", "-vf", "scale=320:-2", str(target)], capture_output=True, text=True, timeout=60)
    if proc.returncode or not target.is_file():
        proc = subprocess.run([ffmpeg, "-y", "-i", str(media), "-frames:v", "1", "-vf", "scale=320:-2", str(target)], capture_output=True, text=True, timeout=60)
    return target


def estimate_seconds(dialogue: str, fallback: float = EMPTY_SCENE_SECONDS) -> float:
    """Rough scene length before the voice exists: ~2.6 spoken words per second plus the pause."""
    words = len(dialogue.split())
    return round(words / 2.6 + SCENE_PAUSE, 1) if words else fallback


def split_script(text: str) -> list[str]:
    """Split a pasted script into scene dialogues: one per blank-line separated paragraph."""
    paragraphs = [" ".join(p.split()) for p in text.replace("\r", "").split("\n\n")]
    return [p for p in paragraphs if p]


def _frame_graph(crop: str, k: int = 1) -> str:
    """Filter graph that turns input 0 into a (1080k)x(1920k) frame labelled [l]."""
    w, h = 1080 * k, 1920 * k
    blur = f"[0:v]split[bg][fg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur={28 * k}:{10 * k},eq=brightness=-0.18:saturation=0.78[b];"
    if crop == "4_3_blur":
        return blur + f"[fg]scale={w}:{810 * k}:force_original_aspect_ratio=increase,crop={w}:{810 * k}[f];[b][f]overlay=0:(H-h)/2,fps=30,setsar=1[l]"
    if crop == "fit_blur":
        return blur + f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[f];[b][f]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[l]"
    return f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,setsar=1[l]"


def _caption_chunks(text: str, max_chars: int) -> list[str]:
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


def render_project(folder: Path, ffmpeg_explicit: str | None = None, progress=None, only_scene: int | None = None) -> dict:
    """Render the project into render/video.mp4, or a quick low-resolution preview of one scene."""
    project = load_project(folder)
    preview = only_scene is not None
    scenes = [project["scenes"][only_scene]] if preview else project["scenes"]
    if not scenes:
        raise ValueError("El proyecto no tiene escenas.")
    channel = CHANNELS[project["channel"]]
    preset = VOICES[project["voice"]]
    ffmpeg = ffmpeg_explicit or _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("No encuentro FFmpeg; instálalo o agrégalo al PATH.")
    for number, scene in enumerate(scenes, start=1):
        if not scene.get("media") or not (folder / scene["media"]["path"]).is_file():
            raise FileNotFoundError(f"La escena {number} no tiene un recurso visual válido.")
    if any(s["dialogue"].strip() for s in scenes) and not EDGE_TTS_PACKAGES.is_dir():
        raise RuntimeError(f"Falta edge-tts en {EDGE_TTS_PACKAGES}.")

    out_dir = folder / "render" / "preview" if preview else folder / "render"
    (out_dir / "scenes").mkdir(parents=True, exist_ok=True)
    (folder / "voice").mkdir(exist_ok=True)
    sub = project["subtitles"]
    style_line = "\n".join([subtitle_style_line(sub), subtitle_style_line(sub, "Middle", 5, 0), subtitle_style_line(sub, "Top", 8, 260)])
    wrap_width = max(8, int(900 / (int(project["subtitles"]["size"]) * 0.52)))
    k = 1 if preview else 2
    ass_lines, scene_videos, scene_audios, records, cursor = [_ASS_HEADER.format(style=style_line)], [], [], [], 0.0
    for number, scene in enumerate(scenes, start=1):
        if progress:
            progress(number, len(scenes))
        dialogue = scene["dialogue"].strip()
        if dialogue:
            try:
                wav = synthesize_voice(folder, dialogue, project["voice"], project["voice_settings"], ffmpeg)
            except RuntimeError as exc:
                raise RuntimeError(f"Escena {number}: {exc}") from exc
            with wave.open(str(wav), "rb") as audio:
                length = audio.getnframes() / audio.getframerate() + SCENE_PAUSE
            audio_input = ["-i", str(wav)]
        else:
            length = float(scene.get("duration") or EMPTY_SCENE_SECONDS)
            audio_input = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        audio_out = out_dir / "scenes" / f"scene-{number:02d}.wav"
        proc = subprocess.run([ffmpeg, "-y", *audio_input, "-af", f"{_AUDIO_FMT},apad=whole_dur={length:.4f}", "-t", f"{length:.4f}", str(audio_out)], capture_output=True, text=True, timeout=120)
        if proc.returncode or not audio_out.is_file():
            raise RuntimeError(f"Falló el audio de la escena {number}: {proc.stderr[-800:]}")
        scene_audios.append(audio_out)

        media = folder / scene["media"]["path"]
        is_image = scene["media"].get("type") == "image"
        speed = ZOOM_SPEEDS[scene["zoom"]["speed"]]
        if is_image and speed:
            # perspective interpolates at sub-pixel positions; zoompan rounds to whole pixels and shakes.
            frames = max(1, round(length * 30))
            z = f"(1+{speed}*in/{frames})" if scene["zoom"]["direction"] == "in" else f"({1 + speed}-{speed}*in/{frames})"
            x0, y0 = f"({1080 * k}-{1080 * k}/{z})/2", f"({1920 * k}-{1920 * k}/{z})/2"
            x1, y2 = f"{1080 * k}-{x0}", f"{1920 * k}-{y0}"
            # Fit the photo once into a 2x frame; the zoom then only resamples that small still.
            fitted = out_dir / "scenes" / f"scene-{number:02d}-frame.png"
            proc = subprocess.run([ffmpeg, "-y", "-i", str(media), "-filter_complex", _frame_graph(scene["crop"], k).replace("fps=30,", "") .replace("[l]", "[o]"), "-map", "[o]", "-frames:v", "1", str(fitted)], capture_output=True, text=True, timeout=300)
            if proc.returncode or not fitted.is_file():
                raise RuntimeError(f"No se pudo preparar la imagen de la escena {number}: {proc.stderr[-800:]}")
            media = fitted
            graph = f"[0:v]perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y2}':x3='{x1}':y3='{y2}':eval=frame:interpolation=cubic,scale=1080:1920:flags=lanczos,setsar=1[v]"
        else:
            graph = _frame_graph(scene["crop"]) + ";[l]null[v]"
        input_args = ["-loop", "1", "-framerate", "30", "-i", str(media)] if is_image else ["-stream_loop", "-1", "-ss", f"{float(scene.get('start') or 0):.3f}", "-i", str(media)]
        video_out = out_dir / "scenes" / f"scene-{number:02d}.mp4"
        proc = subprocess.run([ffmpeg, "-y", *input_args, "-t", f"{length:.4f}", "-an", "-filter_complex", graph, "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "28" if preview else "18", "-pix_fmt", "yuv420p", str(video_out)], capture_output=True, text=True, timeout=300)
        if proc.returncode or not video_out.is_file():
            raise RuntimeError(f"Falló el video de la escena {number}: {proc.stderr[-1200:]}")
        scene_videos.append(video_out)

        spoken = length - SCENE_PAUSE if dialogue else 0
        chunks = _caption_chunks(dialogue, wrap_width * 2)
        total_words = max(1, sum(len(c.split()) for c in chunks))
        offset = cursor
        for chunk in chunks if scene.get("show_subtitles", True) else []:
            span = spoken * len(chunk.split()) / total_words
            text = "\\N".join(textwrap.wrap(chunk.replace("{", "(").replace("}", ")"), width=wrap_width, break_long_words=False))
            ass_lines.append(f"Dialogue: 0,{_stamp(offset)},{_stamp(offset + span)},{SUBTITLE_POSITIONS.get(scene.get('subtitle_pos'), SUBTITLE_POSITIONS['bottom'])[0]},,0,0,0,,{text}\n")
            offset += span
        cursor += length
        records.append({"scene": number, "seconds": round(length, 2), "media": scene["media"]["path"], "crop": scene["crop"], "zoom": scene["zoom"] if is_image else None})

    ass = out_dir / "captions.ass"
    ass.write_text("".join(ass_lines), encoding="utf-8-sig")
    ass_filter = str(ass.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    total = cursor
    music = folder / project["music"]["path"] if project["music"]["path"] else channel["music"]
    outro = channel["outro"]
    use_music = bool(project["music"]["enabled"] and music and music.is_file())
    use_outro = bool(not preview and project["outro"] and outro and outro.is_file())
    cmd = [ffmpeg, "-y"]
    for f in scene_videos + scene_audios:
        cmd += ["-i", str(f)]
    n = len(scenes)
    graph = ["".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0,subtitles='{ass_filter}'{',scale=540:960' if preview else ''}[main_video]", "".join(f"[{n + i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[voice]"]
    next_input = 2 * n
    if use_music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        graph += [f"[{next_input}:a:0]atrim=duration={total:.6f},asetpts=PTS-STARTPTS,{_AUDIO_FMT},volume={project['music']['gain']},afade=t=out:st={max(0.0, total - 3):.3f}:d=3[bed]", "[voice][bed]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[main_audio]"]
        next_input += 1
    else:
        graph.append("[voice]anull[main_audio]")
    if use_outro:
        cmd += ["-i", str(outro)]
        graph += [f"[{next_input}:v:0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[outro_v]", f"[{next_input}:a:0]{_AUDIO_FMT}[outro_a]", "[main_video][outro_v]concat=n=2:v=1:a=0[final_video]", "[main_audio][outro_a]concat=n=2:v=0:a=1[final_audio]"]
        maps = ["-map", "[final_video]", "-map", "[final_audio]"]
    else:
        maps = ["-map", "[main_video]", "-map", "[main_audio]"]
    output = out_dir / ("scene.mp4" if preview else "video.mp4")
    cmd += ["-filter_complex", ";".join(graph), *maps, "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "2M" if preview else "8M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(output)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if proc.returncode or not output.is_file():
        raise RuntimeError("Falló el render final: " + proc.stderr[-3000:])
    if preview:
        return {"status": "preview", "output": str(output), "duration_seconds": round(total, 2)}

    shutil.copy2(write_credits(folder, project), out_dir / "creditos.txt")
    warnings = []
    if abs(total - TARGET_SECONDS) > 5:
        warnings.append(f"La duración del guion ({total:.1f} s) se aleja del objetivo de {TARGET_SECONDS} s.")
    if project["music"]["enabled"] and not use_music:
        warnings.append(f"Sin música de fondo: no existe {music}.")
    if project["outro"] and not use_outro:
        warnings.append(f"Sin outro: no existe {outro}.")
    report = {"status": "rendered", "output": str(output), "duration_seconds": round(total, 2), "target_seconds": TARGET_SECONDS, "scenes": records, "warnings": warnings, "rendered_at": now_iso()}
    save_json(out_dir / "render.json", report)
    return report
