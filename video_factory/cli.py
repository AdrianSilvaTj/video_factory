"""Command line entry point."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import create_demo_job, create_job, create_source_video_job, list_ideas, render_job, run_job
from .storage import jobs_root, load_job


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="video-factory", description="Fábrica local de videos verticales para Que curioso...¿no?")
    p.add_argument("--data-dir", type=Path, help="Carpeta para trabajos (por defecto: ./data)")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("ideas", help="Ver ideas iniciales con respaldo documental")
    new = sub.add_parser("new", help="Crear un trabajo a partir de una idea conocida")
    new.add_argument("--topic", required=True, help="Tema; usa el nombre de una idea del catálogo")
    run = sub.add_parser("run", help="Generar artefactos editoriales desde una idea")
    run.add_argument("job_id")
    run.add_argument("--refresh-voice", action="store_true", help="Volver a sintetizar la narración después de editar el guion")
    sub.add_parser("demo", help="Crear y procesar el trabajo de demostración del pulpo de anillos azules")
    source = sub.add_parser("from-videos", help="Crear y renderizar un video mezclando clips e imágenes de una carpeta")
    source.add_argument("--topic", required=True, help="Tema con dossier factual en el catálogo")
    source.add_argument("--source-dir", required=True, type=Path, help="Carpeta con videos y/o imágenes fuente")
    source.add_argument("--output-dir", type=Path, help="Destino (por defecto, la carpeta fuente)")
    source.add_argument("--ffmpeg", help="Ruta a ffmpeg.exe si no está en PATH")
    render = sub.add_parser("render", help="Renderizar un trabajo a MP4 vertical con FFmpeg")
    render.add_argument("job_id")
    render.add_argument("--ffmpeg", help="Ruta a ffmpeg.exe si no está en PATH")
    qc = sub.add_parser("show", help="Mostrar estado y rutas de un trabajo")
    qc.add_argument("job_id")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = jobs_root(args.data_dir)
    try:
        if args.command == "ideas":
            for idea in list_ideas():
                print(f"• {idea['title']} — {idea['hook']}")
                print(f"  Fuentes: {len(idea['sources'])} | Estado: listo para guion demo")
            return 0
        if args.command == "new":
            job = create_job(args.topic, root)
            print(job["job_id"])
            print(f"Trabajo creado: {root / job['job_id']}")
            return 0
        if args.command == "demo":
            job = create_demo_job(root)
            print(f"Trabajo demo generado: {job['job_id']}")
            print(f"Artefactos: {root / job['job_id']}")
            print("Render MP4: python -m video_factory render " + job["job_id"])
            return 0
        if args.command == "from-videos":
            job = create_source_video_job(args.topic, args.source_dir, root, args.output_dir)
            result = render_job(job["job_id"], root, args.ffmpeg)
            print(f"Trabajo: {job['job_id']}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("status") == "rendered" else 2
        if args.command == "run":
            job = run_job(args.job_id, root, refresh_voice=args.refresh_voice)
            print(f"Listo: {root / job['job_id']}")
            return 0
        if args.command == "render":
            result = render_job(args.job_id, root, args.ffmpeg)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("status") == "rendered" else 2
        if args.command == "show":
            print(json.dumps(load_job(args.job_id, root), ensure_ascii=False, indent=2))
            return 0
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 1
