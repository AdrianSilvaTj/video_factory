"""Versioned JSON job storage."""
from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = APP_ROOT / "data"


def now_iso() -> str:
    return datetime.now(ZoneInfo("America/Bogota")).isoformat(timespec="seconds")


def slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return value[:48] or "video"


def jobs_root(data_dir: Path | None = None) -> Path:
    root = (data_dir or DEFAULT_DATA) / "jobs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def job_dir(job_id: str, root: Path) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,80}", job_id):
        raise ValueError("ID de trabajo inválido")
    path = (root / job_id).resolve()
    if path.parent != root.resolve():
        raise ValueError("ID fuera de la carpeta de trabajos")
    return path


def load_job(job_id: str, root: Path) -> dict:
    return load_json(job_dir(job_id, root) / "idea.json")
