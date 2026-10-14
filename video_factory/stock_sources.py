"""Búsqueda unificada en bancos de recursos gratuitos: Pexels, Pixabay, NASA, Wikimedia Commons y Openverse.

Pexels y Pixabay necesitan clave (.env). NASA, Wikimedia Commons y Openverse funcionan sin clave.
Cada resultado conserva autor, enlace y licencia para los créditos del video.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote, urlencode

from .clips import _rank, _request_json, search_pexels, search_pexels_images, search_pixabay, search_pixabay_images

SOURCES = {
    "Pexels": ("video", "image"),
    "Pixabay": ("video", "image"),
    "NASA": ("video", "image"),
    "Wikimedia Commons": ("video", "image"),
    "Openverse": ("image",),
}
_NASA_LICENSE = "Dominio público (NASA); verifica créditos si aparecen personas, logos o material de terceros"
_COMMONS_FILE = re.compile(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/(.+)")


def _item(provider: str, kind: str, provider_id: str, **fields) -> dict:
    base = {"id": f"{provider.lower().replace(' ', '')}-{'img-' if kind == 'image' else ''}{provider_id}", "provider": provider, "provider_id": provider_id, "media_type": kind,
            "duration": 0, "width": 0, "height": 0, "author_url": "", "attribution": "", "license": "", "license_url": "", "preview_url": "", "preview_video_url": ""}
    base.update(fields)
    return base


def search_nasa(query: str, kind: str, vertical_only: bool = False) -> list[dict]:
    data = _request_json("https://images-api.nasa.gov/search?" + urlencode({"q": query, "media_type": kind, "page_size": 30}))
    results = []
    for entry in data["collection"]["items"]:
        info = entry["data"][0]
        nasa_id = info["nasa_id"]
        base = f"https://images-assets.nasa.gov/{kind}/{quote(nasa_id)}/{quote(nasa_id)}"
        thumb = next((link["href"] for link in entry.get("links", []) if link.get("render") == "image"), "")
        fields = {"query": query, "title": info.get("title", "NASA"), "author": info.get("photographer") or info.get("secondary_creator") or info.get("center") or "NASA",
                  "page_url": f"https://images.nasa.gov/details/{quote(nasa_id)}", "license": _NASA_LICENSE, "license_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
                  "attribution": "Crédito: NASA", "preview_url": thumb.replace("http://", "https://")}
        if kind == "video":
            fields.update({"download_url": base + "~medium.mp4", "fallback_urls": [base + "~mobile.mp4", base + "~large.mp4"], "preview_video_url": base + "~preview.mp4"})
        else:
            fields.update({"download_url": base + "~large.jpg", "fallback_urls": [base + "~medium.jpg", base + "~orig.jpg"]})
        results.append(_item("NASA", kind, nasa_id, **fields))
    return results


def search_wikimedia(query: str, kind: str, vertical_only: bool = False) -> list[dict]:
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"filetype:{'video' if kind == 'video' else 'bitmap'} {query}", "gsrnamespace": 6,
              "gsrlimit": 30, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 320}
    pages = _request_json("https://commons.wikimedia.org/w/api.php?" + urlencode(params)).get("query", {}).get("pages", {})
    results = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        mime, url = info.get("mime", ""), info.get("url", "")
        if not url or (kind == "video" and not mime.startswith(("video/", "application/ogg"))) or (kind == "image" and mime not in ("image/jpeg", "image/png", "image/webp")):
            continue
        if kind == "image" and info.get("size", 0) > 60 * 1024 * 1024:
            continue
        meta = info.get("extmetadata", {})
        clean = lambda key: re.sub(r"<[^>]+>", "", meta.get(key, {}).get("value", "")).strip()
        license_name = clean("LicenseShortName") or "Ver página del archivo"
        fields = {"query": query, "title": page.get("title", "").removeprefix("File:"), "width": int(info.get("width") or 0), "height": int(info.get("height") or 0),
                  "duration": int(info.get("duration") or 0), "download_url": url, "page_url": info.get("descriptionurl", ""), "author": clean("Artist") or "Autor no informado",
                  "license": license_name, "license_url": clean("LicenseUrl"), "attribution": f"{clean('Artist')}, {license_name}, vía Wikimedia Commons", "preview_url": info.get("thumburl", "")}
        match = _COMMONS_FILE.match(url)
        if kind == "video" and match:
            host, folder, name = match.groups()
            fields.update({"download_url": f"{host}/transcoded/{folder}/{name}/{name}.720p.vp9.webm", "fallback_urls": [f"{host}/transcoded/{folder}/{name}/{name}.480p.vp9.webm", url],
                           "preview_video_url": f"{host}/transcoded/{folder}/{name}/{name}.360p.vp9.webm"})
        results.append(_item("Wikimedia Commons", kind, str(page["pageid"]), **fields))
    return results


def search_openverse(query: str, kind: str, vertical_only: bool = False) -> list[dict]:
    params = {"q": query, "page_size": 20}
    if vertical_only:
        params["aspect_ratio"] = "tall"
    data = _request_json("https://api.openverse.org/v1/images/?" + urlencode(params))
    results = []
    for hit in data.get("results", []):
        if not hit.get("url", "").startswith("https://"):
            continue
        license_name = f"CC {hit.get('license', '').upper()} {hit.get('license_version', '')}".strip()
        results.append(_item("Openverse", "image", hit["id"], query=query, title=hit.get("title", ""), width=int(hit.get("width") or 0), height=int(hit.get("height") or 0),
                             download_url=hit["url"], page_url=hit.get("foreign_landing_url", ""), author=hit.get("creator") or "Autor no informado", author_url=hit.get("creator_url") or "",
                             license=license_name, license_url=hit.get("license_url", ""), attribution=f"{hit.get('creator', '')}, {license_name}, vía Openverse ({hit.get('source', '')})",
                             preview_url=hit.get("thumbnail") or hit["url"]))
    return results


_SEARCHERS = {
    ("Pexels", "video"): lambda q, v: search_pexels(q, 80 if v else 20),
    ("Pexels", "image"): lambda q, v: search_pexels_images(q, 80 if v else 20),
    ("Pixabay", "video"): lambda q, v: search_pixabay(q, 80 if v else 20),
    ("Pixabay", "image"): lambda q, v: search_pixabay_images(q, 80 if v else 20),
    ("NASA", "video"): lambda q, v: search_nasa(q, "video"),
    ("NASA", "image"): lambda q, v: search_nasa(q, "image"),
    ("Wikimedia Commons", "video"): lambda q, v: search_wikimedia(q, "video"),
    ("Wikimedia Commons", "image"): lambda q, v: search_wikimedia(q, "image"),
    ("Openverse", "image"): lambda q, v: search_openverse(q, "image", v),
}


def search_media(query: str, providers: tuple[str, ...] = tuple(SOURCES), media: str = "video", vertical_only: bool = False) -> list[dict]:
    """Search the chosen banks in parallel for videos, photos or both ('video', 'image', 'both')."""
    kinds = ("video", "image") if media == "both" else (media,)
    jobs = [(provider, kind) for provider in providers for kind in kinds if (provider, kind) in _SEARCHERS]
    if not jobs:
        raise ValueError("Ninguno de los bancos elegidos ofrece ese tipo de recurso.")

    def run(job):
        try:
            return job, _SEARCHERS[job](query, vertical_only), None
        except Exception as exc:
            return job, [], f"{job[0]} ({'videos' if job[1] == 'video' else 'imágenes'}): {exc}"

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        outcomes = list(pool.map(run, jobs))
    warnings = [error for _, _, error in outcomes if error]
    results = []
    for job, found, _ in outcomes:
        for item in found:
            item.setdefault("license", f"Licencia de {item['provider']}")
            item.setdefault("media_type", "video")
        results.extend(found)
    if vertical_only:
        results = [r for r in results if r["width"] == 0 or r["height"] > r["width"]]
    if not results:
        raise RuntimeError("No se encontraron resultados. " + " | ".join(warnings))
    results.sort(key=lambda r: _rank(r)[0] if r["width"] else 3)
    for item in results:
        item["search_warnings"] = warnings
    return results
