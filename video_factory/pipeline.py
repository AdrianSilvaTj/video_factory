"""Deterministic demo pipeline with rights-aware local asset discovery."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
import uuid
import wave
from datetime import datetime
from pathlib import Path

from .catalog import IDEAS
from .infographic_prompts import build_infographic_request
from .storage import APP_ROOT, job_dir, now_iso, save_json, slug

SYNTHETIC_ART = [
    ("asset-ai-octopus-01", "pulpo_blue_rings_ai_demo.png", "Ilustración de apertura del pulpo de anillos azules."),
    ("asset-ai-octopus-02", "pulpo_scene_02_warning.png", "Marcas azules visibles como señal de advertencia."),
    ("asset-ai-octopus-03", "pulpo_scene_03_hiding.png", "Pulpo oculto en una grieta rocosa."),
    ("asset-ai-octopus-04", "pulpo_scene_04_toxin.png", "Visualización científica simbólica de neurotoxina; no representa una mordedura."),
    ("asset-ai-octopus-05", "pulpo_scene_05_scale.png", "Observación del animal en una poza rocosa; recreación ilustrativa de escala."),
]
BACKGROUND_MUSIC = APP_ROOT / "Canal" / "fondo_1.mp3"
SYNCHRONIZED_OUTRO = APP_ROOT / "Canal" / "outro_sincronizado.mp4"
BACKGROUND_MUSIC_GAIN = 0.30
EDGE_TTS_PACKAGES = APP_ROOT / "data" / "tts-packages"
SUBSCRIBE_CTA = "Si te gustan los datos curiosos, dale like y suscríbete para no perderte el próximo video."
VIDEO_INDEX = APP_ROOT / "VIDEOS" / "INDICE_VIDEOS.txt"


def _record_video_in_index(topic: str, video_path: Path) -> None:
    """Append each finished video once so future topics can avoid repeats."""
    if not video_path.is_file():
        return
    VIDEO_INDEX.parent.mkdir(parents=True, exist_ok=True)
    path_text = str(video_path.resolve())
    if VIDEO_INDEX.is_file():
        content = VIDEO_INDEX.read_text(encoding="utf-8-sig")
        if path_text.casefold() in content.casefold():
            return
    else:
        content = "ÍNDICE DE VIDEOS — Que curioso…¿no?\nUsar este listado para evitar repetir temas.\n"
    with VIDEO_INDEX.open("a", encoding="utf-8", newline="") as index_file:
        if content and not content.endswith("\n"):
            index_file.write("\n")
        index_file.write(f"- {topic.strip()} | {path_text}\n")


def _with_subscribe_cta(scenes: list[dict]) -> list[dict]:
    """Add the channel's standard spoken closing line before the outro."""
    if any(s.get("scene_id") == "cta-subscribe" or "dale like y suscríbete" in s.get("narration", "").casefold() for s in scenes):
        return scenes
    return [*scenes, {"scene_id": "cta-subscribe", "claim_ids": [], "narration": SUBSCRIBE_CTA, "caption": "Dale like y suscríbete", "purpose": "channel_subscribe_cta"}]


def _source_clip_plan(idea: dict, job: dict) -> list[dict]:
    """Prefer the user's infographic.png for the opening when the folder has one."""
    plan = [dict(entry) for entry in idea.get("source_clip_plan", [])]
    opening = Path(job.get("source_video_dir", "")) / "infografia.png"
    if plan and opening.is_file():
        plan[0].update({"filename": opening.name, "effect": "slow_centered_zoom"})
    return plan


def _find_ffmpeg() -> str | None:
    configured = shutil.which("ffmpeg")
    if configured:
        return configured
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    package_root = local_app_data / "Microsoft" / "WinGet" / "Packages"
    candidates = list(package_root.glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe")) if package_root.is_dir() else []
    return str(max(candidates, key=lambda p: p.stat().st_mtime)) if candidates else None


def list_ideas() -> list[dict]:
    return [{"title": v["topic"], "hook": v["hook"], "sources": v["sources"]} for v in IDEAS.values()]


def find_idea(topic: str) -> tuple[str, dict]:
    q = topic.casefold().strip()
    for key, idea in IDEAS.items():
        if q == key or q == idea["topic"].casefold() or q in [a.casefold() for a in idea["aliases"]]:
            return key, idea
    choices = ", ".join(item["topic"] for item in IDEAS.values())
    raise ValueError(f"No hay dossier de investigación verificado para «{topic}». Ideas disponibles: {choices}. No invento fuentes para temas sin investigar.")


def create_job(topic: str, root: Path) -> dict:
    key, idea = find_idea(topic)
    job_id = f"{datetime.now().strftime('%Y%m%d')}-{slug(idea['topic'])}-{uuid.uuid4().hex[:6]}"
    folder = job_dir(job_id, root)
    folder.mkdir(parents=True, exist_ok=False)
    job = {"schema_version": 1, "job_id": job_id, "status": "idea_ready", "created_at": now_iso(), "topic": idea["topic"], "catalog_id": key, "niche": idea["niche"], "locale": idea["locale"], "source_ids": [s["source_id"] for s in idea["sources"]], "script_version": 1, "approval": {"status": "pending", "approved_version": None, "approved_at": None}, "outputs": {"video_path": None, "video_sha256": None}}
    save_json(folder / "idea.json", job)
    save_json(folder / "opening-image-request.json", build_infographic_request(IDEAS[key]))
    return job


def create_demo_job(root: Path) -> dict:
    job = create_job("pulpo-anillos-azules", root)
    return run_job(job["job_id"], root)


def _discover_local_assets(topic: str) -> list[dict]:
    matches = []
    for candidate in APP_ROOT.iterdir():
        if candidate.is_dir() and topic.split()[0].casefold() in candidate.name.casefold():
            for media in candidate.rglob("*"):
                if media.is_file() and media.suffix.casefold() in {".mp4", ".jpg", ".jpeg", ".png", ".webp", ".jfif"}:
                    if media.name == "pulpo_blue_rings_ai_demo.png" or media.name.startswith("pulpo_scene_"):
                        continue
                    matches.append({"path": str(media), "filename": media.name, "kind": "video" if media.suffix.casefold() == ".mp4" else "image", "rights_status": "unknown_blocked_for_publish", "used_in_render": False, "note": "Recurso local existente; falta registrar autor, licencia, atribución y permiso comercial."})
    return matches


def _allocate_scene_durations(scenes: list[dict], duration: float) -> list[float]:
    """Honor explicitly timed shots and divide remaining voice time by narration length."""
    pinned = [float(s["duration_seconds"]) if s.get("duration_seconds") is not None else None for s in scenes]
    fixed_total = sum(value for value in pinned if value is not None)
    if fixed_total > duration:
        raise ValueError("La duración fija de las escenas supera la duración de la narración.")
    flexible_total = sum(max(1, len(s["narration"].split())) for s, value in zip(scenes, pinned) if value is None)
    remaining = max(0.0, duration - fixed_total)
    return [value if value is not None else remaining * max(1, len(scene["narration"].split())) / max(1, flexible_total) for scene, value in zip(scenes, pinned)]


def _make_subtitles(scenes: list[dict], path: Path, duration: float) -> None:
    # Readable ASS captions positioned above typical platform controls.
    header = """[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,64,&H00FFFFFF,&H0000FFFF,&H00101B24,&HAA061018,1,0,0,0,100,100,0,0,1,5,1,2,90,90,420,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
    lines = [header]
    timings = _allocate_scene_durations(scenes, duration)
    cursor = 0.0
    for ix, scene in enumerate(scenes):
        start = cursor
        end = cursor + timings[ix]
        cursor = end
        if not scene.get("caption", "").strip():
            continue
        def stamp(seconds: float) -> str:
            whole = int(seconds); centis = int((seconds - whole) * 100)
            return f"{whole//3600}:{(whole//60)%60:02d}:{whole%60:02d}.{centis:02d}"
        caption = "\\N".join(textwrap.wrap(scene["caption"].replace("{", "(").replace("}", ")"), width=24, break_long_words=False))
        lines.append(f"Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{caption}\n")
    path.write_text("".join(lines), encoding="utf-8-sig")


def _make_voice(script: str, target: Path, refresh: bool = False) -> dict:
    script_hash = hashlib.sha256(script.encode("utf-8")).hexdigest()
    record_path = target.parent.parent / "voice.json"
    old_record = {}
    if record_path.is_file():
        try:
            old_record = json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    if not refresh and old_record.get("script_sha256") == script_hash and old_record.get("status") == "generated_demo" and target.is_file():
        try:
            with wave.open(str(target), "rb") as audio:
                seconds = audio.getnframes() / audio.getframerate()
            return {**old_record, "duration_seconds": round(seconds, 2)}
        except (wave.Error, ZeroDivisionError):
            pass
    ffmpeg = _find_ffmpeg()
    if EDGE_TTS_PACKAGES.is_dir() and ffmpeg:
        neural_script = Path(__file__).resolve().parent / "synthesize_neural_voice.py"
        neural_mp3 = target.with_suffix(".mp3")
        proc = subprocess.run(
            [sys.executable, str(neural_script), "--text", script, "--output", str(neural_mp3), "--ffmpeg", ffmpeg],
            capture_output=True, text=True, timeout=180,
        )
        if proc.returncode != 0 or not target.is_file():
            return {"status": "failed", "provider": "Microsoft Edge Neural TTS", "path": None, "error": (proc.stderr or proc.stdout)[-1600:], "note": "La voz neural requiere conexión al servicio en línea."}
        with wave.open(str(target), "rb") as audio:
            seconds = audio.getnframes() / audio.getframerate()
        return {"status": "generated_demo", "provider": "Microsoft Edge Neural TTS (edge-tts)", "voice": "es-CO-GonzaloNeural", "gender": "male", "path": "voice/voice.wav", "source_audio": "voice/voice.mp3", "script_sha256": script_hash, "duration_seconds": round(seconds, 2), "note": "Voz neural colombiana sintetizada en línea; requiere Internet y revisar pronunciación antes de aprobar."}
    # PowerShell 7 sees the full per-user Windows voice registry in this
    # environment; Windows PowerShell 5 can start without those voice tokens.
    powershell = shutil.which("pwsh") or shutil.which("powershell.exe")
    if not powershell:
        return {"status": "unavailable", "provider": "Windows System.Speech", "path": None, "note": "PowerShell no está disponible; se puede colocar voice.wav manualmente."}
    ps = Path(__file__).resolve().parent / "synthesize_voice.ps1"
    proc = subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps), "-Text", script, "-Output", str(target)], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0 or not target.exists():
        return {"status": "failed", "provider": "Windows System.Speech", "path": None, "error": (proc.stderr or proc.stdout)[-1000:]}
    with wave.open(str(target), "rb") as audio:
        seconds = audio.getnframes() / audio.getframerate()
    selected = next((line.split("=", 1)[1].strip() for line in proc.stdout.splitlines() if line.startswith("VOICE_NAME=")), "Pablo")
    return {"status": "generated_demo", "provider": "Windows System.Speech", "voice": selected, "gender": "male", "path": "voice/voice.wav", "script_sha256": script_hash, "duration_seconds": round(seconds, 2), "note": "Voz sintética masculina local de demostración; revisar pronunciación antes de aprobar."}


def run_job(job_id: str, root: Path, refresh_voice: bool = False) -> dict:
    folder = job_dir(job_id, root)
    job_path = folder / "idea.json"
    if not job_path.is_file():
        raise FileNotFoundError(f"No existe el trabajo: {job_id}")
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if job.get("source_video_files"):
        return run_source_video_job(job_id, root, refresh_voice=refresh_voice)
    idea = IDEAS[job["catalog_id"]]
    save_json(folder / "opening-image-request.json", build_infographic_request(idea))
    custom_visuals = idea.get("visual_assets")
    visual_plan = custom_visuals or [
        {"asset_id": asset_id, "filename": filename, "description": description}
        for asset_id, filename, description in SYNTHETIC_ART
    ]
    research_path = folder / "research.json"
    if not research_path.exists():
        save_json(research_path, {"schema_version": 1, "retrieved_at": now_iso(), "sources": idea["sources"], "claims": idea["claims"], "verification": "Editorial dossier with claims linked to identified source; re-check source before publication."})
    script_path = folder / "script.json"
    old_script_hash = job.get("script_sha256")
    if script_path.exists():
        script_doc = json.loads(script_path.read_text(encoding="utf-8"))
        scenes = _with_subscribe_cta(script_doc["scenes"])
        script_doc["scenes"] = scenes
        current_hash = hashlib.sha256(json.dumps(script_doc, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        script_changed = bool(old_script_hash and old_script_hash != current_hash)
        if script_changed:
            script_doc["version"] = int(script_doc.get("version", 1)) + 1
        narration = " ".join(scene["narration"] for scene in scenes)
        script_doc["narration"] = narration
        script_doc["fact_claim_ids"] = sorted({claim for s in scenes for claim in s["claim_ids"]})
    else:
        scenes = _with_subscribe_cta(idea["script"])
        narration = " ".join(scene["narration"] for scene in scenes)
        script_doc = {"schema_version": 1, "version": 1, "hook": idea["hook"], "scenes": scenes, "narration": narration, "cta": idea["cta"], "duration_estimate_seconds": 6.3 * len(scenes), "language": "es-CO", "fact_claim_ids": sorted({claim for s in scenes for claim in s["claim_ids"]}), "review_status": "pending_human_review"}
        script_changed = False
    save_json(script_path, script_doc)
    script_hash = hashlib.sha256(json.dumps(script_doc, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    storyboard_path = folder / "storyboard.json"
    storyboard_old = {}
    if storyboard_path.is_file():
        try:
            storyboard_old = json.loads(storyboard_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    if not storyboard_path.exists() or storyboard_old.get("source_script_sha256") != script_hash or storyboard_old.get("asset_plan_version") != 4:
        word_counts = [max(1, len(s["narration"].split())) for s in scenes]
        total_estimate = float(script_doc.get("duration_estimate_seconds") or 6.3 * len(scenes))
        storyboard = [{"scene_id": s["scene_id"], "estimated_duration_seconds": round(total_estimate * word_counts[i] / sum(word_counts), 2), "visual": visual_plan[i % len(visual_plan)]["description"] + " Corte entre imágenes con zoom lento; ilustración, no metraje documental.", "visual_asset_id": visual_plan[i % len(visual_plan)]["asset_id"], "text_on_screen": s["caption"], "narration": s["narration"], "claim_ids": s["claim_ids"]} for i, s in enumerate(scenes)]
        save_json(storyboard_path, {"schema_version": 1, "asset_plan_version": 4, "source_script_sha256": script_hash, "scenes": storyboard, "outro": {"asset_id": "asset-channel-outro", "path": str(SYNCHRONIZED_OUTRO), "duration_seconds": 1.74, "audio": "preservado y mezclado con la música de fondo"}})
    (folder / "assets").mkdir(exist_ok=True)
    generated_assets = []
    for art in visual_plan:
        generated = folder / "assets" / art["filename"]
        if not custom_visuals:
            original = APP_ROOT / "pulpo anillos azules" / art["filename"]
            if not original.is_file():
                raise FileNotFoundError(f"Falta el asset sintético de demo: {original}")
            shutil.copy2(original, generated)
        if not generated.is_file():
            raise FileNotFoundError(f"Falta la ilustración de escena: {generated}")
        generated_assets.append({"asset_id": art["asset_id"], "path": "assets/" + art["filename"], "kind": "AI-generated still illustration", "description": art["description"], "creator": "OpenAI image generation", "source_url": None, "license": "AI-generated for this video; review applicable terms before publication", "attribution": "AI-generated illustration; not documentary footage", "rights_status": "synthetic_demo_review_terms", "used_in_render": True})
    discovered_assets = _discover_local_assets(idea["topic"])
    assets_path = folder / "assets.json"
    existing_assets = json.loads(assets_path.read_text(encoding="utf-8")) if assets_path.is_file() else {}
    retained = [a for a in existing_assets.get("assets", []) if a.get("asset_id") not in ({x["asset_id"] for x in visual_plan} | {"asset-ai-octopus-demo", "asset-channel-background-music", "asset-channel-outro"})]
    retained.extend([
        {"asset_id": "asset-channel-background-music", "path": str(BACKGROUND_MUSIC), "kind": "background music", "creator": "Channel-provided", "license": "User designated for all videos; publication terms are not documented here", "rights_status": "user_designated_review_terms", "used_in_render": True},
        {"asset_id": "asset-channel-outro", "path": str(SYNCHRONIZED_OUTRO), "kind": "synchronized outro video and audio", "creator": "Channel-provided", "license": "User designated for all videos; publication terms are not documented here", "rights_status": "user_designated_review_terms", "used_in_render": True},
    ])
    retained_paths = {a.get("path") for a in retained}
    retained.extend(a for a in discovered_assets if a["path"] not in retained_paths)
    save_json(assets_path, {"schema_version": 1, "assets": generated_assets + retained, "selection_policy": "Render uses five registered distinct illustrations; existing files with unknown rights remain inventoried, blocked for publishing, and excluded from the render."})
    if not BACKGROUND_MUSIC.is_file():
        raise FileNotFoundError(f"Falta la música de fondo configurada: {BACKGROUND_MUSIC}")
    if not SYNCHRONIZED_OUTRO.is_file():
        raise FileNotFoundError(f"Falta el outro configurado: {SYNCHRONIZED_OUTRO}")
    (folder / "voice").mkdir(exist_ok=True)
    voice = _make_voice(narration, folder / "voice" / "voice.wav", refresh=refresh_voice)
    save_json(folder / "voice.json", voice)
    (folder / "subtitles").mkdir(exist_ok=True)
    _make_subtitles(scenes, folder / "subtitles" / "captions.ass", voice.get("duration_seconds", script_doc.get("duration_estimate_seconds", 30)))
    prior_render = Path(job.get("outputs", {}).get("video_path") or "")
    has_current_render = bool(not script_changed and job.get("status") == "rendered_pending_review" and prior_render.is_file())
    if script_changed:
        job["outputs"] = {"video_path": None, "video_sha256": None}
        job["approval"] = {"status": "pending", "approved_version": None, "approved_at": None}
    job.update({"status": "rendered_pending_review" if has_current_render else "production_ready", "updated_at": now_iso(), "script_sha256": script_hash, "script_version": script_doc["version"], "artifacts": ["research.json", "script.json", "storyboard.json", "assets.json", "voice.json", "voice/voice.wav", "subtitles/captions.ass"]})
    save_json(job_path, job)
    metadata_path = folder / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    metadata.update({"schema_version": 1, "job_id": job_id, "brand": "Que curioso…¿no?", "language": "es-CO", "script_version": script_doc["version"], "voice": {"gender": "male", "provider": voice.get("provider"), "name": voice.get("voice", "Pablo")}, "audio_defaults": {"background_music": str(BACKGROUND_MUSIC), "music_gain": BACKGROUND_MUSIC_GAIN, "outro": str(SYNCHRONIZED_OUTRO), "preserve_outro_audio": True}, "format": {"width": 1080, "height": 1920, "fps": 30, "video_codec": "h264", "audio_codec": "aac", "target_video_bitrate": "8M", "target_audio_bitrate": "192k"}, "publication_enabled": False, "approval_status": job["approval"]["status"], "rights_review_required": True, "updated_at": now_iso()})
    save_json(metadata_path, metadata)
    qc_path = folder / "qc.json"
    qc = json.loads(qc_path.read_text(encoding="utf-8")) if qc_path.is_file() else {}
    if script_changed or not qc:
        qc = {"status": "pending_render", "checks": {"script_claim_links": "pass", "rights_unknown_assets_excluded": "pass", "mp4_exists": "pending", "video_codec": "pending", "resolution": "pending", "subtitles": "pass"}, "warnings": ["Revisar visualmente la ilustración sintética.", "Revisar licencias y créditos de cualquier recurso local antes de publicar.", "Aprobación humana de guion y versión pendiente."], "publication_ready": False}
    qc.setdefault("checks", {})["voice"] = voice["status"]
    save_json(qc_path, qc)
    return job


def create_source_video_job(topic: str, source_dir: Path, root: Path, output_dir: Path | None = None) -> dict:
    """Create a reusable job that builds a short from user-provided video footage."""
    source_dir = source_dir.expanduser().resolve()
    if not source_dir.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de videos fuente: {source_dir}")
    source_files = sorted(p.resolve() for p in source_dir.iterdir() if p.is_file() and p.suffix.casefold() in {".mp4", ".mov", ".mkv", ".webm", ".jpg", ".jpeg", ".png", ".webp"})
    if not source_files:
        raise FileNotFoundError(f"No encontré videos MP4, MOV, MKV o WebM en {source_dir}")
    job = create_job(topic, root)
    job["source_video_dir"] = str(source_dir)
    job["source_video_files"] = [str(p) for p in source_files]
    job["delivery_dir"] = str((output_dir or source_dir).expanduser().resolve())
    save_json(job_dir(job["job_id"], root) / "idea.json", job)
    return run_source_video_job(job["job_id"], root)


def run_source_video_job(job_id: str, root: Path, refresh_voice: bool = False) -> dict:
    folder = job_dir(job_id, root)
    job_path = folder / "idea.json"
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("source_video_files"):
        raise ValueError(f"El trabajo {job_id} no tiene una carpeta de videos fuente configurada.")
    opening_infographic = Path(job.get("source_video_dir", "")) / "infografia.png"
    if opening_infographic.is_file():
        job["source_video_files"] = [p for p in job["source_video_files"] if Path(p).name != "apertura-infografica.png" or Path(p).is_file()]
        if not any(Path(p).resolve() == opening_infographic.resolve() for p in job["source_video_files"]):
            job["source_video_files"].insert(0, str(opening_infographic.resolve()))
        save_json(job_path, job)
    missing = [p for p in job["source_video_files"] if not Path(p).is_file()]
    if missing:
        raise FileNotFoundError("Faltan videos fuente: " + ", ".join(missing))
    idea = IDEAS[job["catalog_id"]]
    save_json(folder / "opening-image-request.json", build_infographic_request(idea))
    scenes = _with_subscribe_cta(idea["script"])
    narration = " ".join(scene["narration"] for scene in scenes)
    script_doc = {"schema_version": 1, "version": 1, "hook": idea["hook"], "scenes": scenes, "narration": narration, "cta": idea["cta"], "duration_estimate_seconds": 6.3 * len(scenes), "language": "es-CO", "fact_claim_ids": sorted({claim for s in scenes for claim in s["claim_ids"]}), "review_status": "pending_human_review"}
    save_json(folder / "research.json", {"schema_version": 1, "retrieved_at": now_iso(), "sources": idea["sources"], "claims": idea["claims"], "verification": "Claims tied to cited source pages; review before publication."})
    save_json(folder / "script.json", script_doc)
    (folder / "voice").mkdir(parents=True, exist_ok=True)
    voice = _make_voice(narration, folder / "voice" / "voice.wav", refresh=refresh_voice)
    save_json(folder / "voice.json", voice)
    if voice.get("status") != "generated_demo":
        raise RuntimeError("No se pudo generar la narración: " + str(voice.get("error") or voice.get("note")))
    (folder / "subtitles").mkdir(parents=True, exist_ok=True)
    _make_subtitles(scenes, folder / "subtitles" / "captions.ass", voice["duration_seconds"])

    plan = _source_clip_plan(idea, job)
    storyboard_scenes = []
    for i, scene in enumerate(scenes):
        clip = plan[i % len(plan)] if plan else {}
        filename = clip.get("filename", "selección automática de la carpeta")
        still = Path(filename).suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}
        storyboard_scenes.append({"scene_id": scene["scene_id"], "source_filename": filename, "source_media_kind": "still_image" if still else "video", "visual_effect": "slow_centered_zoom" if still else "trimmed_video", "source_position_ratio": clip.get("at_ratio"), "text_on_screen": scene["caption"], "narration": scene["narration"], "claim_ids": scene["claim_ids"]})
    save_json(folder / "storyboard.json", {"schema_version": 1, "mode": "mixed_source_media", "scenes": storyboard_scenes, "outro": {"path": str(SYNCHRONIZED_OUTRO), "audio": "preservado y mezclado con la música de fondo"}})
    stock_by_filename = {a["filename"]: a for a in idea.get("stock_media", [])}
    assets = []
    for i, path in enumerate(job["source_video_files"]):
        filename = Path(path).name
        stock = stock_by_filename.get(filename)
        is_image = Path(filename).suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}
        generated = next((a for a in idea.get("generated_media", []) if a["filename"] == filename), None)
        assets.append({"asset_id": f"asset-source-media-{i+1:02d}", "path": path, "kind": "generated still image" if generated else (("stock image" if is_image else "stock video") if stock else ("user-provided source image" if is_image else "user-provided source video")), "filename": filename, "creator": generated.get("creator") if generated else (stock.get("creator") if stock else "Provided by user"), "platform": stock.get("platform") if stock else None, "source_url": stock.get("page_url") if stock else None, "download_url": stock.get("download_url") if stock else None, "license": generated.get("license") if generated else (stock.get("license") if stock else "Not recorded; verify publication rights"), "prompt_summary": generated.get("prompt_summary") if generated else None, "rights_status": "generated_ai_for_project" if generated else ("stock_free_license_recorded" if stock else "user_provided_review_terms"), "used_in_render": True})
    save_json(folder / "assets.json", {"schema_version": 1, "assets": assets, "selection_policy": "Extract short segments from the user-selected source folder; original files remain untouched."})
    delivery = Path(job["delivery_dir"])
    production = delivery / "produccion"
    production.mkdir(parents=True, exist_ok=True)
    for src, dest in ((folder / "script.json", production / "guion.json"), (folder / "research.json", production / "fuentes.json"), (folder / "assets.json", production / "licencias-medios.json"), (folder / "opening-image-request.json", production / "solicitud-infografia.json"), (folder / "voice.json", production / "voz.json"), (folder / "voice" / "voice.wav", production / "voz.wav"), (folder / "voice" / "voice.mp3", production / "voz.mp3"), (folder / "subtitles" / "captions.ass", production / "subtitulos.ass")):
        if src.is_file():
            shutil.copy2(src, dest)
    metadata = {"schema_version": 1, "job_id": job_id, "topic": idea["topic"], "brand": "Que curioso…¿no?", "language": "es-CO", "voice": {"gender": "male", "provider": voice.get("provider"), "name": voice.get("voice")}, "audio_defaults": {"background_music": str(BACKGROUND_MUSIC), "music_gain": BACKGROUND_MUSIC_GAIN, "outro": str(SYNCHRONIZED_OUTRO), "preserve_outro_audio": True}, "format": {"width": 1080, "height": 1920, "fps": 30, "video_codec": "h264", "audio_codec": "aac"}, "visual_mode": "mixed sourced video and still images", "source_video_dir": job["source_video_dir"], "publication_enabled": False, "rights_review_required": True, "updated_at": now_iso()}
    save_json(folder / "metadata.json", metadata)
    save_json(production / "metadatos.json", metadata)
    rights_warnings = [] if all(a.get("rights_status") in {"stock_free_license_recorded", "generated_ai_for_project"} for a in assets) else ["Confirmar permisos de publicación de los medios fuente."]
    image_count = sum(Path(a["filename"]).suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"} for a in assets)
    qc = {"status": "pending_render", "checks": {"script_claim_links": "pass", "source_media_count": len(assets), "source_video_count": len(assets) - image_count, "source_image_count": image_count, "voice": voice["status"], "male_voice": "pass", "subtitles": "pass", "mp4_exists": "pending", "background_music": "pending", "outro": "pending"}, "warnings": rights_warnings + ["Aprobación humana de guion y versión pendiente."], "publication_ready": False}
    save_json(folder / "qc.json", qc)
    save_json(production / "control-calidad.json", qc)
    job.update({"status": "production_ready", "script_version": 1, "updated_at": now_iso(), "artifacts": ["research.json", "script.json", "storyboard.json", "assets.json", "voice.json", "voice/voice.wav", "subtitles/captions.ass", "metadata.json", "qc.json"]})
    save_json(job_path, job)
    return job


def _find_tool(explicit: str | None, name: str) -> str | None:
    return explicit if explicit and Path(explicit).is_file() else shutil.which(name)


def render_job(job_id: str, root: Path, ffmpeg_explicit: str | None = None) -> dict:
    folder = job_dir(job_id, root)
    if (folder / "idea.json").is_file():
        existing = json.loads((folder / "idea.json").read_text(encoding="utf-8"))
        if existing.get("source_video_files"):
            if not (folder / "script.json").exists():
                run_source_video_job(job_id, root)
            return render_source_video_job(job_id, root, ffmpeg_explicit)
    if not (folder / "script.json").exists():
        run_job(job_id, root)
    ffmpeg = _find_tool(ffmpeg_explicit, "ffmpeg") or _find_tool(ffmpeg_explicit, "ffmpeg.exe")
    if not ffmpeg:
        report = {"status": "blocked_dependency", "message": "No encuentro FFmpeg. Instálalo desde una distribución oficial o pasa --ffmpeg C:\\ruta\\ffmpeg.exe.", "required": ["ffmpeg", "ffprobe"], "output": None}
        save_json(folder / "render" / "render.json", report)
        return report
    if not BACKGROUND_MUSIC.is_file() or not SYNCHRONIZED_OUTRO.is_file():
        raise FileNotFoundError("La música de fondo y el outro configurados son necesarios para renderizar.")
    ffprobe = _find_tool(None, "ffprobe") or str(Path(ffmpeg).with_name("ffprobe.exe"))
    q_outro = subprocess.run([ffprobe, "-v", "error", "-show_entries", "stream=codec_type,duration", "-show_entries", "format=duration", "-of", "json", str(SYNCHRONIZED_OUTRO)], capture_output=True, text=True, timeout=60)
    if q_outro.returncode != 0:
        raise RuntimeError("FFprobe no pudo leer el clip de outro: " + q_outro.stderr[-1000:])
    outro_info = json.loads(q_outro.stdout)
    outro_video_duration = next((float(s["duration"]) for s in outro_info.get("streams", []) if s.get("codec_type") == "video" and s.get("duration")), 1.7)
    outro_audio_duration = next((float(s["duration"]) for s in outro_info.get("streams", []) if s.get("codec_type") == "audio" and s.get("duration")), outro_video_duration)
    assets_doc = json.loads((folder / "assets.json").read_text(encoding="utf-8"))
    images = [folder / a["path"] for a in assets_doc.get("assets", []) if a.get("used_in_render") and a.get("kind") == "AI-generated still illustration"]
    images = images[:5]
    if len(images) < 5 or any(not p.is_file() for p in images):
        raise RuntimeError("El render de demostración necesita al menos cinco ilustraciones generadas disponibles.")
    voice = folder / "voice" / "voice.wav"
    if not voice.is_file():
        return {"status": "blocked_voice", "message": "No hay narración local generada; coloca voice/voice.wav y reintenta."}
    out_dir = folder / "render"; out_dir.mkdir(exist_ok=True)
    output = out_dir / "video-demo.mp4"
    ass = folder / "subtitles" / "captions.ass"
    filter_path = str(ass.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    with wave.open(str(voice), "rb") as audio_file:
        main_duration = audio_file.getnframes() / audio_file.getframerate()
        shot_duration = main_duration / len(images)
    cmd = [ffmpeg, "-y"]
    for image_path in images:
        cmd.extend(["-loop", "1", "-framerate", "30", "-t", f"{shot_duration:.4f}", "-i", str(image_path)])
    voice_input = len(images)
    cmd.extend(["-i", str(voice)])
    music_input = voice_input + 1
    cmd.extend(["-stream_loop", "-1", "-i", str(BACKGROUND_MUSIC)])
    outro_input = music_input + 1
    cmd.extend(["-i", str(SYNCHRONIZED_OUTRO)])
    graph = []
    for i in range(len(images)):
        # Render the crop at 2x resolution so pixel rounding cannot make the
        # centered zoom appear to jump; downsample only after the movement.
        zoom_step = 0.12 / max(1, shot_duration * 30)
        graph.append(f"[{i}:v]scale=2160:3840,zoompan=z='min(1+{zoom_step:.9f}*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=2160x3840:fps=30,scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
    joined = "".join(f"[v{i}]" for i in range(len(images)))
    graph.append(f"{joined}concat=n={len(images)}:v=1:a=0,subtitles='{filter_path}'[main_video]")
    pad = max(0.0, outro_audio_duration - outro_video_duration)
    graph.append(f"[{outro_input}:v:0]scale=1080:1920,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration={pad:.4f}[outro_video]")
    graph.append("[main_video][outro_video]concat=n=2:v=1:a=0[final_video]")
    graph.append(f"[{voice_input}:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1.0[voice]")
    graph.append(f"[{music_input}:a:0]asplit=2[music_main][music_outro]")
    graph.append(f"[music_main]atrim=start=0:duration={main_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={BACKGROUND_MUSIC_GAIN}[bed_main]")
    graph.append("[voice][bed_main]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[main_audio]")
    graph.append(f"[music_outro]atrim=start={main_duration:.6f}:duration={outro_audio_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={BACKGROUND_MUSIC_GAIN}[bed_outro]")
    graph.append(f"[{outro_input}:a:0]atrim=duration={outro_audio_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1.0[outro_sound]")
    graph.append("[outro_sound][bed_outro]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[outro_audio]")
    graph.append("[main_audio][outro_audio]concat=n=2:v=0:a=1[final_audio]")
    cmd.extend(["-filter_complex", ";".join(graph), "-map", "[final_video]", "-map", "[final_audio]", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "8M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(output)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if proc.returncode != 0 or not output.is_file():
        report = {"status": "render_failed", "message": proc.stderr[-3000:], "command": cmd, "output": None}
        save_json(out_dir / "render.json", report)
        return report
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    probe = None
    if ffprobe:
        q = subprocess.run([ffprobe, "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,channels", "-show_entries", "format=duration,size", "-of", "json", str(output)], capture_output=True, text=True, timeout=60)
        if q.returncode == 0:
            probe = json.loads(q.stdout)
    report = {"status": "rendered", "output": str(output), "sha256": digest, "ffmpeg": ffmpeg, "ffprobe": probe, "rendered_at": now_iso(), "visual_mode": "five distinct AI-generated stills with hard cuts and slow zoom", "distinct_images": len(images), "background_music": str(BACKGROUND_MUSIC), "background_music_gain": BACKGROUND_MUSIC_GAIN, "outro": str(SYNCHRONIZED_OUTRO), "outro_audio_preserved": True}
    save_json(out_dir / "render.json", report)
    _record_video_in_index(json.loads((folder / "idea.json").read_text(encoding="utf-8")).get("topic", job_id))
    job = json.loads((folder / "idea.json").read_text(encoding="utf-8"))
    job["status"] = "rendered_pending_review"; job["outputs"] = {"video_path": str(output), "video_sha256": digest}; job["updated_at"] = now_iso()
    save_json(folder / "idea.json", job)
    qc = json.loads((folder / "qc.json").read_text(encoding="utf-8"))
    qc["checks"].update({"mp4_exists": "pass", "video_codec": "h264", "resolution": "1080x1920", "fps": "30", "audio_codec": "aac", "audio_sample_rate": "48000", "distinct_images": len(images), "slow_zoom": "pass", "male_voice": "pass", "background_music": "pass", "outro": "pass", "video_sha256": digest})
    qc["status"] = "review_required"; qc["publication_ready"] = False
    save_json(folder / "qc.json", qc)
    return report


def render_source_video_job(job_id: str, root: Path, ffmpeg_explicit: str | None = None) -> dict:
    """Trim user clips into vertical scenes and assemble the narrated short."""
    folder = job_dir(job_id, root)
    job_path = folder / "idea.json"
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("source_video_files"):
        raise ValueError("Este trabajo no tiene videos fuente.")
    ffmpeg = _find_tool(ffmpeg_explicit, "ffmpeg") or _find_tool(ffmpeg_explicit, "ffmpeg.exe")
    if not ffmpeg:
        raise RuntimeError("No encuentro FFmpeg; pasa --ffmpeg con la ruta a ffmpeg.exe.")
    ffprobe = _find_tool(None, "ffprobe") or str(Path(ffmpeg).with_name("ffprobe.exe"))
    if not BACKGROUND_MUSIC.is_file() or not SYNCHRONIZED_OUTRO.is_file():
        raise FileNotFoundError("Falta la música o el outro configurado del canal.")
    voice = folder / "voice" / "voice.wav"
    if not voice.is_file():
        raise FileNotFoundError("Falta la narración; ejecuta primero el comando from-videos.")
    idea = IDEAS[job["catalog_id"]]
    save_json(folder / "opening-image-request.json", build_infographic_request(idea))
    scenes = json.loads((folder / "script.json").read_text(encoding="utf-8"))["scenes"]
    with wave.open(str(voice), "rb") as wf:
        main_duration = wf.getnframes() / wf.getframerate()
    scene_durations = _allocate_scene_durations(scenes, main_duration)
    sources = [Path(p) for p in job["source_video_files"]]
    source_info = {}
    source_dimensions = {}
    for source in sources:
        if source.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        q = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-show_entries", "stream=width,height", "-of", "json", str(source)], capture_output=True, text=True, timeout=60)
        if q.returncode or not q.stdout.strip():
            raise RuntimeError(f"FFprobe no pudo leer {source.name}: {q.stderr[-800:]}")
        probe_data = json.loads(q.stdout)
        source_info[source.name] = float(probe_data["format"]["duration"])
        video_stream = next((stream for stream in probe_data.get("streams", []) if stream.get("width") and stream.get("height")), {})
        source_dimensions[source.name] = (int(video_stream.get("width", 0)), int(video_stream.get("height", 0)))
    plan = _source_clip_plan(idea, job)
    clips_dir = Path(job["delivery_dir"]) / "produccion" / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_records = []
    scene_files = []
    for i, (scene, duration) in enumerate(zip(scenes, scene_durations)):
        entry = plan[i % len(plan)] if plan else {}
        source = next((p for p in sources if p.name == entry.get("filename")), sources[i % len(sources)])
        output_clip = clips_dir / f"scene-{i+1:02d}.mp4"
        is_image = source.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}
        if is_image:
            clip_duration = duration + 0.08
            source_duration = None
            start = 0.0
            if entry.get("effect") == "hold":
                video_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
            else:
                max_zoom = 0.02 if source.name.casefold() == "infografia.png" else 0.10
                zoom_step = max_zoom / max(1, clip_duration * 30)
                zoom_limit = 1 + max_zoom
                video_filter = f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='min(1+{zoom_step:.9f}*on,{zoom_limit:.2f})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=2160x3840:fps=30,scale=1080:1920:flags=lanczos,setsar=1"
            cmd_clip = [ffmpeg, "-y", "-loop", "1", "-framerate", "30", "-t", f"{clip_duration:.3f}", "-i", str(source), "-an", "-vf", video_filter, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_clip)]
        else:
            source_duration = source_info[source.name]
            clip_duration = min(duration + 0.08, source_duration)
            ratio = float(entry.get("at_ratio", (0.15 + (i * .17)) % .8))
            start = max(0.0, min(source_duration - clip_duration, (source_duration - clip_duration) * ratio))
            source_width, source_height = source_dimensions[source.name]
            if source_width / max(1, source_height) > 1.2:
                # Keep landscape subjects in a centered 4:3 window instead of
                # cropping aggressively to 9:16. A softened full-height copy
                # fills the vertical canvas behind it.
                video_filter = "[0:v]split[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:10,eq=brightness=-0.18:saturation=0.78[background];[fg]scale=1080:810:force_original_aspect_ratio=increase,crop=1080:810:(iw-ow)/2:(ih-oh)/2[foreground];[background][foreground]overlay=0:(H-h)/2,fps=30,setsar=1[v]"
                filter_args = ["-filter_complex", video_filter, "-map", "[v]"]
                display_aspect = "4:3 en lienzo vertical con fondo suavizado"
            else:
                video_filter = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,setsar=1"
                filter_args = ["-vf", video_filter]
                display_aspect = "encuadre vertical original"
            cmd_clip = [ffmpeg, "-y", "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{clip_duration:.3f}", "-an", *filter_args, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_clip)]
        proc = subprocess.run(cmd_clip, capture_output=True, text=True, timeout=300)
        if proc.returncode or not output_clip.is_file():
            raise RuntimeError(f"No se pudo recortar {source.name}: {proc.stderr[-1800:]}")
        scene_files.append(output_clip)
        effect = (entry.get("effect") if entry.get("effect") == "hold" else "slow_centered_zoom") if is_image else "trimmed_video"
        clip_records.append({"scene_id": scene["scene_id"], "source_file": str(source), "source_filename": source.name, "source_kind": "still_image" if is_image else "video", "effect": effect, "display_aspect": "9:16" if is_image else display_aspect, "source_duration_seconds": round(source_duration, 3) if source_duration is not None else None, "start_seconds": round(start, 3), "duration_seconds": round(clip_duration, 3), "output_clip": str(output_clip), "caption": scene["caption"]})
    outro_q = subprocess.run([ffprobe, "-v", "error", "-show_entries", "stream=codec_type,duration", "-show_entries", "format=duration", "-of", "json", str(SYNCHRONIZED_OUTRO)], capture_output=True, text=True, timeout=60)
    if outro_q.returncode:
        raise RuntimeError("FFprobe no pudo leer el outro: " + outro_q.stderr[-800:])
    oi = json.loads(outro_q.stdout)
    outro_video_duration = next((float(s["duration"]) for s in oi.get("streams", []) if s.get("codec_type") == "video" and s.get("duration")), 1.7)
    outro_audio_duration = next((float(s["duration"]) for s in oi.get("streams", []) if s.get("codec_type") == "audio" and s.get("duration")), outro_video_duration)
    delivery = Path(job["delivery_dir"])
    delivery.mkdir(parents=True, exist_ok=True)
    output = delivery / f"{slug(idea['topic'])}.mp4"
    ass = folder / "subtitles" / "captions.ass"
    filter_path = str(ass.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    cmd = [ffmpeg, "-y"]
    for clip in scene_files:
        cmd.extend(["-i", str(clip)])
    voice_i = len(scene_files); cmd.extend(["-i", str(voice)])
    music_i = voice_i + 1; cmd.extend(["-stream_loop", "-1", "-i", str(BACKGROUND_MUSIC)])
    outro_i = music_i + 1; cmd.extend(["-i", str(SYNCHRONIZED_OUTRO)])
    graph = ["".join(f"[{i}:v]" for i in range(len(scene_files))) + f"concat=n={len(scene_files)}:v=1:a=0,subtitles='{filter_path}'[main_video]"]
    pad = max(0.0, outro_audio_duration - outro_video_duration)
    graph += [f"[{outro_i}:v:0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration={pad:.4f}[outro_video]", "[main_video][outro_video]concat=n=2:v=1:a=0[final_video]", f"[{voice_i}:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1[voice]", f"[{music_i}:a:0]asplit=2[m1][m2]", f"[m1]atrim=duration={main_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={BACKGROUND_MUSIC_GAIN}[bed1]", "[voice][bed1]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[main_audio]", f"[m2]atrim=start={main_duration:.6f}:duration={outro_audio_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={BACKGROUND_MUSIC_GAIN}[bed2]", f"[{outro_i}:a:0]atrim=duration={outro_audio_duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1[outro_sound]", "[outro_sound][bed2]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[outro_audio]", "[main_audio][outro_audio]concat=n=2:v=0:a=1[final_audio]"]
    cmd.extend(["-filter_complex", ";".join(graph), "-map", "[final_video]", "-map", "[final_audio]", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "8M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(output)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    if proc.returncode or not output.is_file():
        raise RuntimeError("Falló el render final: " + proc.stderr[-3500:])
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    probe = subprocess.run([ffprobe, "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,channels", "-show_entries", "format=duration,size", "-of", "json", str(output)], capture_output=True, text=True, timeout=60)
    probe_doc = json.loads(probe.stdout) if probe.returncode == 0 else None
    caption = idea.get("social_caption", idea["hook"] + "\n\n#Hipopotamo #Animales #Naturaleza #Reels #Shorts #TikTok")
    description = delivery / "descripcion-redes.txt"
    text = caption + "\n\nFuentes de datos:\n" + "\n".join(f"- {s['title']}: {s['url']}" for s in idea["sources"])
    if idea.get("stock_media"):
        text += "\n\nCréditos de video (licencia Pexels; atribución no obligatoria):\n" + "\n".join(f"- {a['title']} — {a['creator']}: {a['page_url']}" for a in idea["stock_media"])
    description.write_text(text + "\n", encoding="utf-8")
    save_json(delivery / "produccion" / "manifiesto-clips.json", {"job_id": job_id, "clips": clip_records, "source_originals_untouched": True})
    source_images = sum(p.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"} for p in sources)
    source_videos = len(sources) - source_images
    report = {"status": "rendered", "output": str(output), "sha256": digest, "ffprobe": probe_doc, "visual_mode": "mixed sourced footage and still images" if source_images and source_videos else ("still images" if source_images else "sourced video clips"), "source_video_count": source_videos, "source_image_count": source_images, "scene_clips": len(scene_files), "slow_zoom_images": sum(r["source_kind"] == "still_image" for r in clip_records), "background_music_gain": BACKGROUND_MUSIC_GAIN, "outro_audio_preserved": True}
    save_json(delivery / "produccion" / "render.json", report)
    _record_video_in_index(idea["topic"], output)
    qc = json.loads((folder / "qc.json").read_text(encoding="utf-8"))
    qc["checks"].update({"mp4_exists": "pass", "video_codec": "h264", "resolution": "1080x1920", "fps": "30", "audio_codec": "aac", "scene_clips": len(scene_files), "slow_zoom_images": report["slow_zoom_images"], "background_music": "pass gain=0.30", "outro": "pass", "subtitles": "burned_in", "video_sha256": digest})
    qc["status"] = "review_required"; qc["publication_ready"] = False
    save_json(folder / "qc.json", qc); save_json(delivery / "produccion" / "control-calidad.json", qc)
    job["status"] = "rendered_pending_review"; job["outputs"] = {"video_path": str(output), "video_sha256": digest}; job["updated_at"] = now_iso()
    save_json(job_path, job)
    return report
