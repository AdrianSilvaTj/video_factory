"""Canales (plantillas de música, outro y subtítulos) y voces disponibles."""
from __future__ import annotations

from .pipeline import APP_ROOT, BACKGROUND_MUSIC, BACKGROUND_MUSIC_GAIN, SYNCHRONIZED_OUTRO

TARGET_SECONDS = 45
VOICES = {
    "male": {"label": "Masculina (Gonzalo, Colombia)", "voice": "es-CO-GonzaloNeural", "rate": "-4%", "pitch": "-1Hz", "gender": "male"},
    "female": {"label": "Femenina (Dalia, México — Canal Belleza)", "voice": "es-MX-DaliaNeural", "rate": "+9%", "pitch": "+4Hz", "gender": "female"},
}
CHANNELS = {
    "que-curioso": {"label": "Qué curioso…¿no?", "music": BACKGROUND_MUSIC, "music_gain": BACKGROUND_MUSIC_GAIN, "outro": SYNCHRONIZED_OUTRO, "subtitles": {"font": "Arial", "size": 128, "color": "#FFFFFF", "outline": "#241B10", "bold": True}, "default_voice": "male"},
    "belleza": {
        "label": "Belleza con evidencia (Canal Belleza)",
        "music": APP_ROOT / "Canal" / "belleza_fondo.mp3",
        "music_gain": 0.14,
        "outro": None,
        "subtitles": {"font": "Segoe UI", "size": 76, "color": "#D7B9FF", "outline": "#361B49", "bold": True},
        "default_voice": "female",
    },
}
_AUDIO_FMT = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
