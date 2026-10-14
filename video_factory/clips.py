"""Búsqueda, selección sugerida y descarga aprobada de clips Pexels/Pixabay.

Las claves se leen desde variables de entorno o desde .env en la raíz del proyecto.
No se descargan archivos hasta llamar explícitamente a download_approved_clips().
"""
from __future__ import annotations
import json, os, re, time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

APP_ROOT = Path(__file__).resolve().parent
ENV_FILE = APP_ROOT / ".env"
TARGET_SECONDS = 45


def load_env_file(path: Path = ENV_FILE) -> None:
    """Carga pares KEY=VALUE desde .env sin sobrescribir variables ya definidas."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _request_json(url: str, headers: dict[str, str] | None = None) -> dict:
    req = Request(url, headers={"User-Agent": "VideoFactory/1.0 (aplicacion de escritorio personal)", **(headers or {})})
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"API respondió HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"No se pudo conectar con el banco de clips: {exc}") from exc


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return value[:60] or "clip"


def _rank(item: dict) -> tuple:
    # Prioriza clips verticales, pero conserva horizontales si la búsqueda no ofrece suficientes.
    ratio = item.get("width", 0) / max(item.get("height", 1), 1)
    vertical_penalty = 0 if 0.48 <= ratio <= 0.72 else (1 if ratio < 1 else 2)
    duration = item.get("duration", 0)
    duration_penalty = 0 if 3 <= duration <= 25 else 1
    return vertical_penalty, duration_penalty, abs(ratio - (9 / 16))


def search_pexels(query: str, per_page: int = 20) -> list[dict]:
    load_env_file()
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta PEXELS_API_KEY. Configúrala en el archivo .env de la raíz del proyecto.")
    from urllib.parse import urlencode
    url = "https://api.pexels.com/v1/videos/search?" + urlencode({"query": query, "per_page": min(max(per_page, 1), 80), "orientation": "portrait"})
    data = _request_json(url, {"Authorization": key})
    results = []
    for video in data.get("videos", []):
        files = video.get("video_files", [])
        files = [f for f in files if f.get("link") and f.get("file_type", "video/mp4") in ("video/mp4", "video/webm")]
        if not files:
            continue
        # Evita archivos 4K excesivos cuando hay alternativas de calidad media.
        chosen = sorted(files, key=lambda f: (abs((f.get("width") or 0) - 1080), (f.get("width") or 0) > 1920))[0]
        results.append({"id": f"pexels-{video.get('id')}", "provider": "Pexels", "provider_id": str(video.get("id")),
            "query": query, "title": f"Video de {video.get('user', {}).get('name', 'Pexels')}",
            "duration": int(video.get("duration") or 0), "width": int(chosen.get("width") or video.get("width") or 0),
            "height": int(chosen.get("height") or video.get("height") or 0), "download_url": chosen["link"],
            "page_url": video.get("url", "https://www.pexels.com/videos/"),
            "author": video.get("user", {}).get("name", "Autor no informado"),
            "author_url": video.get("user", {}).get("url", "https://www.pexels.com/"),
            "attribution": "Video de Pexels; enlazar a Pexels y al perfil del autor cuando se publique.",
            "license_url": "https://www.pexels.com/license/", "preview_url": video.get("image", ""),
            "preview_video_url": min(files, key=lambda f: f.get("width") or 10**6)["link"]})
    return sorted(results, key=_rank)


def search_pixabay(query: str, per_page: int = 20) -> list[dict]:
    load_env_file()
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta PIXABAY_API_KEY. Configúrala en el archivo .env de la raíz del proyecto.")
    from urllib.parse import urlencode
    url = "https://pixabay.com/api/videos/?" + urlencode({"key": key, "q": query, "per_page": min(max(per_page, 3), 200), "safesearch": "true", "video_type": "film"})
    data = _request_json(url)
    results = []
    for video in data.get("hits", []):
        variants = video.get("videos", {})
        # 'medium' suele equilibrar resolución y tamaño; usa la variante disponible.
        chosen = variants.get("medium") or variants.get("small") or variants.get("large") or variants.get("tiny")
        if not chosen or not chosen.get("url"):
            continue
        results.append({"id": f"pixabay-{video.get('id')}", "provider": "Pixabay", "provider_id": str(video.get("id")),
            "query": query, "title": f"Video de {video.get('user', 'Pixabay')}", "duration": int(video.get("duration") or 0),
            "width": int(chosen.get("width") or 0), "height": int(chosen.get("height") or 0), "download_url": chosen["url"],
            "page_url": video.get("pageURL", "https://pixabay.com/videos/"), "author": video.get("user", "Autor no informado"),
            "author_url": "https://pixabay.com/users/" + re.sub(r"[^a-zA-Z0-9_-]+", "-", str(video.get("user", ""))).strip("-") + "-" + str(video.get("user_id", "")) + "/",
            "attribution": "Revisar los términos vigentes de Pixabay; se recomienda conservar y mostrar el crédito y el enlace.",
            "license_url": "https://pixabay.com/service/license/", "preview_url": (chosen.get("thumbnail") or variants.get("medium", {}).get("thumbnail") or ""),
            "preview_video_url": (variants.get("tiny") or variants.get("small") or chosen).get("url", "")})
    return sorted(results, key=_rank)


def search_clips(query: str, providers: tuple[str, ...] = ("Pexels", "Pixabay"), per_provider: int = 20, vertical_only: bool = False) -> list[dict]:
    query = query.strip()
    if not query:
        raise ValueError("Escribe un tema o palabras clave para buscar clips.")
    if vertical_only:
        per_provider = max(per_provider, 80)
    all_results, errors = [], []
    for provider in providers:
        try:
            if provider.lower() == "pexels": all_results.extend(search_pexels(query, per_provider))
            elif provider.lower() == "pixabay": all_results.extend(search_pixabay(query, per_provider))
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    if vertical_only:
        all_results = [r for r in all_results if r["height"] > r["width"]]
    all_results.sort(key=_rank)
    if not all_results and errors:
        raise RuntimeError("No se encontraron resultados. " + " | ".join(errors))
    if not all_results and vertical_only:
        raise RuntimeError("No hay clips verticales para esa búsqueda; desactiva el filtro o prueba otras palabras.")
    # Exponer errores parciales en la metadata para que la interfaz no oculte fallos de una API.
    for item in all_results: item["search_warnings"] = errors
    return all_results


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".ogv"}


def search_pexels_images(query: str, per_page: int = 20) -> list[dict]:
    load_env_file()
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta PEXELS_API_KEY. Configúrala en el archivo .env de la raíz del proyecto.")
    from urllib.parse import urlencode
    data = _request_json("https://api.pexels.com/v1/search?" + urlencode({"query": query, "per_page": min(max(per_page, 1), 80), "orientation": "portrait"}), {"Authorization": key})
    return [{"id": f"pexels-img-{p['id']}", "provider": "Pexels", "provider_id": str(p["id"]), "media_type": "image", "query": query,
             "title": p.get("alt") or "Foto de Pexels", "duration": 0, "width": int(p.get("width") or 0), "height": int(p.get("height") or 0),
             "download_url": p["src"].get("large2x") or p["src"]["original"], "page_url": p.get("url", "https://www.pexels.com/"),
             "author": p.get("photographer", "Autor no informado"), "author_url": p.get("photographer_url", "https://www.pexels.com/"),
             "attribution": "Foto de Pexels; enlazar a Pexels y al perfil del autor cuando se publique.", "license_url": "https://www.pexels.com/license/",
             "preview_url": p["src"].get("medium", ""), "preview_video_url": ""} for p in data.get("photos", []) if p.get("src")]


def search_pixabay_images(query: str, per_page: int = 20) -> list[dict]:
    load_env_file()
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta PIXABAY_API_KEY. Configúrala en el archivo .env de la raíz del proyecto.")
    from urllib.parse import urlencode
    data = _request_json("https://pixabay.com/api/?" + urlencode({"key": key, "q": query, "per_page": min(max(per_page, 3), 200), "safesearch": "true", "image_type": "photo"}))
    return [{"id": f"pixabay-img-{h['id']}", "provider": "Pixabay", "provider_id": str(h["id"]), "media_type": "image", "query": query,
             "title": h.get("tags", "Foto de Pixabay"), "duration": 0, "width": int(h.get("imageWidth") or 0), "height": int(h.get("imageHeight") or 0),
             "download_url": h.get("largeImageURL") or h["webformatURL"], "page_url": h.get("pageURL", "https://pixabay.com/"),
             "author": h.get("user", "Autor no informado"), "author_url": "https://pixabay.com/users/" + re.sub(r"[^a-zA-Z0-9_-]+", "-", str(h.get("user", ""))).strip("-") + "-" + str(h.get("user_id", "")) + "/",
             "attribution": "Revisar los términos vigentes de Pixabay; se recomienda conservar y mostrar el crédito y el enlace.", "license_url": "https://pixabay.com/service/license/",
             "preview_url": h.get("webformatURL", ""), "preview_video_url": ""} for h in data.get("hits", [])]


def _load_manifest(destination: Path, job_id: str, target_seconds: int) -> tuple[Path, dict]:
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "clips_manifest.json"
    if manifest_path.is_file():
        return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))
    return manifest_path, {"job_id": job_id, "target_seconds": target_seconds, "aspect_ratio": "9:16", "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "clips": []}


def _download_file(url: str, path: Path) -> None:
    """Stream a https URL to disk (retrying on HTTP 429), removing the partial file on failure."""
    if urlparse(url).scheme != "https":
        raise ValueError("URL de descarga no válida.")
    req = Request(url, headers={"User-Agent": "VideoFactory/1.0 (aplicacion de escritorio personal; descarga manual de recursos aprobados)"})
    for attempt in range(3):
        try:
            with urlopen(req, timeout=60) as response, path.open("wb") as output:
                total = 0
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk: break
                    total += len(chunk)
                    if total > 500 * 1024 * 1024:
                        raise RuntimeError("El archivo supera el límite de seguridad de 500 MB.")
                    output.write(chunk)
            return
        except HTTPError as exc:
            path.unlink(missing_ok=True)
            if exc.code != 429 or attempt == 2:
                raise
            time.sleep(4 * (attempt + 1))
        except Exception:
            path.unlink(missing_ok=True)
            raise


def download_media(item: dict, destination: Path) -> Path:
    """Download one chosen search result into destination (trying fallback URLs) and return the local path."""
    destination.mkdir(parents=True, exist_ok=True)
    default = ".jpg" if item.get("media_type") == "image" else ".mp4"
    last_error = None
    for url in [item.get("download_url", ""), *item.get("fallback_urls", [])]:
        suffix = Path(urlparse(url).path).suffix.casefold()
        path = destination / f"{_safe_name(item.get('id', 'clip'))}{suffix if suffix in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS else default}"
        if path.is_file():
            return path
        try:
            _download_file(url.replace("http://", "https://"), path)
            return path
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"No se pudo descargar el recurso: {last_error}")


def download_approved_clips(items: list[dict], destination: Path, job_id: str, target_seconds: int = TARGET_SECONDS) -> dict:
    """Descarga únicamente los elementos aprobados y los suma a clips_manifest.json."""
    if not items:
        raise ValueError("No hay clips aprobados para descargar.")
    manifest_path, manifest = _load_manifest(destination, job_id, target_seconds)
    known = {c["id"] for c in manifest["clips"]}
    downloaded = 0
    for item in items:
        if item["id"] in known:
            continue
        url = item.get("download_url", "")
        if urlparse(url).scheme != "https":
            raise ValueError(f"URL de descarga no válida para {item.get('id')}.")
        is_image = item.get("media_type") == "image"
        filename = f"{len(manifest['clips']) + 1:02d}_{_safe_name(item.get('provider_id') or item.get('id', 'clip'))}{'.jpg' if is_image else '.mp4'}"
        path = destination / filename
        _download_file(url, path)
        saved = {k: v for k, v in item.items() if k not in ("download_url", "search_warnings")}
        saved.update({"media_type": "image" if is_image else "video", "filename": filename, "local_path": str(path), "download_url": url, "bytes": path.stat().st_size, "approved_by_user": True})
        manifest["clips"].append(saved)
        downloaded += 1
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"manifest": str(manifest_path), "downloaded": downloaded, "total_in_manifest": len(manifest["clips"]), "target_seconds": target_seconds, "clips": manifest["clips"]}


def add_local_files(paths: list[str], destination: Path, job_id: str, target_seconds: int = TARGET_SECONDS) -> dict:
    """Copia imágenes o videos del usuario a la carpeta del trabajo y los registra en el manifiesto."""
    import shutil
    manifest_path, manifest = _load_manifest(destination, job_id, target_seconds)
    added = 0
    for raw in paths:
        source = Path(raw)
        ext = source.suffix.casefold()
        if ext not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            raise ValueError(f"Formato no admitido: {source.name}. Usa JPG, PNG, WEBP, MP4, MOV, MKV o WEBM.")
        filename = f"{len(manifest['clips']) + 1:02d}_local_{_safe_name(source.stem)}{ext}"
        target = destination / filename
        shutil.copy2(source, target)
        manifest["clips"].append({"id": f"local-{_safe_name(source.stem)}-{len(manifest['clips']) + 1}", "provider": "Archivo propio", "provider_id": source.name, "media_type": "image" if ext in IMAGE_EXTENSIONS else "video",
            "title": source.name, "author": "Aportado por el usuario", "page_url": "", "license_url": "", "attribution": "Archivo del usuario; confirmar derechos de uso antes de publicar.",
            "filename": filename, "local_path": str(target), "bytes": target.stat().st_size, "approved_by_user": True})
        added += 1
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"manifest": str(manifest_path), "added": added, "total_in_manifest": len(manifest["clips"])}
