"""Build image-generation requests from the fixed visual guide and verified topic data."""
from __future__ import annotations

import hashlib
from pathlib import Path


STYLE_GUIDE_PATH = Path(__file__).with_name("estilo_infografia_3d.md")
STYLE_TEMPLATE_HEADING = "## Plantilla de contenido para cada video"
REUSABLE_INSTRUCTION_HEADING = "## Instrucción reutilizable para el generador"


def load_fixed_visual_style() -> tuple[str, str]:
    """Read the non-topic-specific guide once and omit the blank topic template."""
    source = STYLE_GUIDE_PATH.read_text(encoding="utf-8-sig")
    style = source.split(STYLE_TEMPLATE_HEADING, 1)[0].strip()
    # The last section repeats the preceding visual rules. Excluding it keeps
    # each request complete without appending a second copy of the same brief.
    style = style.split(REUSABLE_INSTRUCTION_HEADING, 1)[0].strip()
    if not style:
        raise ValueError(f"La guía visual no contiene instrucciones: {STYLE_GUIDE_PATH}")
    return style, hashlib.sha256(source.encode("utf-8")).hexdigest()


def _ordered_verified_claims(idea: dict) -> list[dict]:
    by_id = {claim.get("claim_id"): claim for claim in idea.get("claims", []) if claim.get("status") == "verified"}
    ordered_ids = []
    for scene in idea.get("script", []):
        for claim_id in scene.get("claim_ids", []):
            if claim_id in by_id and claim_id not in ordered_ids:
                ordered_ids.append(claim_id)
    return [by_id[claim_id] for claim_id in ordered_ids]


def build_infographic_request(idea: dict) -> dict:
    """Keep channel style fixed while supplying each video's separate facts/visual brief."""
    visual_style, style_hash = load_fixed_visual_style()
    claims = _ordered_verified_claims(idea)
    if not claims:
        raise ValueError(f"No hay datos verificados para la infografía de {idea.get('topic', 'este tema')}.")

    brief = idea.get("opening_visual", {})
    claim_by_id = {claim["claim_id"]: claim for claim in claims}
    primary_id = brief.get("main_claim_id")
    if primary_id not in claim_by_id:
        primary_id = claims[0]["claim_id"]
    primary = claim_by_id[primary_id]
    secondary = [claim for claim in claims if claim["claim_id"] != primary_id][:5]
    facts = [{"claim_id": c["claim_id"], "text": c["text"]} for c in [primary, *secondary]]

    video_data = {
        "topic": idea.get("topic", ""),
        "protagonist": brief.get("protagonist") or idea.get("topic", "").split(":", 1)[0],
        "title": brief.get("title") or idea.get("hook", ""),
        "main_verified_fact": {"claim_id": primary["claim_id"], "text": primary["text"]},
        "other_verified_facts": [{"claim_id": c["claim_id"], "text": c["text"]} for c in secondary],
        "comparison": brief.get("comparison"),
        "environment": brief.get("environment") or idea.get("niche", "hábitat natural relacionado con el tema"),
        "closing_question": brief.get("question") or idea.get("hook", ""),
        "verified_claim_ids": [c["claim_id"] for c in facts],
    }
    secondary_lines = "\n".join(f"- [{c['claim_id']}] {c['text']}" for c in secondary) or "- Sin datos secundarios adicionales."
    comparison_line = video_data["comparison"] or "No añadir una comparación de escala, salvo que esté respaldada por estos datos verificados."
    prompt = "\n\n".join([
        "ESTILO VISUAL FIJO — FUENTE: video_factory/estilo_infografia_3d.md\n" + visual_style,
        "DATOS Y DIRECCIÓN ESPECÍFICOS DE ESTE VIDEO\n"
        f"Tema: {video_data['topic']}\n"
        f"Protagonista: {video_data['protagonist']}\n"
        f"Título sugerido: {video_data['title']}\n"
        f"Entorno: {video_data['environment']}\n"
        f"Dato principal verificado: [{primary['claim_id']}] {primary['text']}\n"
        f"Otros datos verificados candidatos (elige solo los que quepan con claridad):\n{secondary_lines}\n"
        f"Comparación visual: {comparison_line}\n"
        f"Pregunta de cierre sugerida: {video_data['closing_question']}\n"
        "Usa exclusivamente las afirmaciones con ID incluidas aquí; no agregues números, capacidades, especies ni relaciones de escala no verificadas. "
        "Genera una sola escena 3D integrada, sin texto ni letras dentro de la imagen. Deja espacio seguro para colocar con código el título y 3–4 etiquetas en español, sin tapar al protagonista.",
    ])
    return {
        "schema_version": 1,
        "style_guide": str(STYLE_GUIDE_PATH),
        "style_guide_sha256": style_hash,
        "visual_style_fixed": visual_style,
        "video_data": video_data,
        "prompt": prompt,
        "text_overlay": "Añadir títulos, cifras, unidades y etiquetas por código después de generar la escena base.",
    }
