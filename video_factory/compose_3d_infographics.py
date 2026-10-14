"""Add accurate Spanish infographic typography to generated 3D animal art."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 1080, 1920
YELLOW = (255, 190, 20, 255)
WHITE = (248, 250, 252, 255)
CYAN = (46, 218, 232, 255)
MUTED = (210, 224, 236, 255)
BLACK = (1, 8, 18, 232)
FONT_REG = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def ft(size: int, bold: bool = False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)


def measure(draw, text, f):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f, stroke_width=1)
    return x1 - x0, y1 - y0


def draw_center(draw, xy, text, f, fill, stroke=3):
    draw.text(xy, text, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 250))


def brush_title(draw, lines: list[tuple[str, tuple]], y=52):
    max_text_width = 950
    sizes = [60 if len(text) < 20 else 50 for text, _ in lines]
    while max(measure(draw, text, ft(size, True))[0] for (text, _), size in zip(lines, sizes)) > max_text_width:
        sizes = [s - 2 for s in sizes]
    h = 72 * len(lines) + 42
    # Uneven silhouette gives the dark backing a painted-brush edge.
    pts = [(43, y+15), (165, y+4), (332, y+13), (486, y+2), (703, y+12), (1016, y+5),
           (1002, y+h-12), (826, y+h-2), (631, y+h-13), (407, y+h-3), (229, y+h-10), (53, y+h-4)]
    draw.polygon(pts, fill=BLACK)
    draw.line([(58, y+22), (283, y+13), (482, y+21), (755, y+13), (1004, y+18)], fill=(0,0,0,255), width=17)
    yy = y + 32
    for (text, color), size in zip(lines, sizes):
        draw_center(draw, (540, yy + size//2), text, ft(size, True), color, stroke=4)
        yy += 72


def label(draw, box, title: str, value: str | None = None, accent=YELLOW, value_size=38):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=23, fill=BLACK, outline=(255, 255, 255, 155), width=2)
    draw.rounded_rectangle((x0+10, y0+12, x0+20, y1-12), radius=5, fill=accent)
    if value:
        draw.text((x0+42, (y0+y1)//2), title.upper(), font=ft(22, True), fill=MUTED, anchor="lm", stroke_width=1, stroke_fill=(0,0,0,230))
        draw.text((x1-26, (y0+y1)//2), value, font=ft(value_size, True), fill=accent, anchor="rm", stroke_width=2, stroke_fill=(0,0,0,240))
    else:
        draw.text((x0+42, (y0+y1)//2), title.upper(), font=ft(26, True), fill=WHITE, anchor="lm", stroke_width=1, stroke_fill=(0,0,0,230))


def base_image(name: str) -> Image.Image:
    path = ROOT / "data" / "jobs" / name / "ilustracion-3d-base.png"
    with Image.open(path) as im:
        return ImageOps.fit(im.convert("RGB"), (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")


def vignette(im: Image.Image, top: int, bottom: int):
    shade = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(shade)
    d.rectangle((0, 0, W, top), fill=(0,0,0,95))
    d.rectangle((0, H-bottom, W, H), fill=(0,5,14,150))
    im.alpha_composite(shade)


def finalize(name: str, title: list[tuple[str,tuple]], labels, question: str, title_y=52, label_top=1390):
    im = base_image(name)
    vignette(im, 350, 450)
    over = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(over)
    brush_title(d, title, title_y)
    for i, item in enumerate(labels):
        label(d, (72, label_top+i*102, 1008, label_top+82+i*102), item[0], item[1], item[2] if len(item)>2 else YELLOW, item[3] if len(item)>3 else 38)
    # Short closing prompt remains in the lower safe area.
    draw_center(d, (540, 1850), question, ft(29, True), WHITE, stroke=3)
    im.alpha_composite(over)
    target = ROOT / "data" / "jobs" / name / "apertura-infografica.png"
    im.convert("RGB").save(target, "PNG", optimize=True)
    print(f"{name}: {target} ({target.stat().st_size} bytes)")


def main():
    finalize("Colibri", [("¿ALAS CASI INVISIBLES?", WHITE), ("75 ALETEOS / SEGUNDO", YELLOW)],
             [("Aleteos máximos", "75 / s", YELLOW, 40), ("Puede quedarse suspendido", None, CYAN), ("Vuelo de alto consumo energético", None, YELLOW)],
             "¿Cómo puede quedarse quieto en el aire?", label_top=1450)
    finalize("Casuario", [("¿MÁS ALTA QUE TÚ?", WHITE), ("HEMBRA HASTA 2 m", YELLOW)],
             [("Altura máxima de una hembra", "2 m", YELLOW, 42), ("Estatura de referencia", "1,70 m", WHITE, 35), ("Puede superarla por 30 cm", None, CYAN)],
             "Mira la comparación de escala", title_y=48, label_top=1440)
    finalize("Perezoso", [("UN ALMUERZO LENTÍSIMO", WHITE), ("HASTA 1 MES", YELLOW)],
             [("Para digerir una comida", "≈ 1 mes", YELLOW, 36), ("Baja del árbol aprox. 1 vez por semana", None, WHITE), ("También es capaz de nadar", None, CYAN)],
             "¿Te imaginas esperar tanto para digerir?", title_y=52, label_top=1420)
    finalize("TortugaLaud", [("LA BUCEADORA DEL ABISMO", WHITE), ("HASTA 1.200 m", CYAN)],
             [("Profundidad de inmersión", "1.200 m", CYAN, 36), ("Puede permanecer sumergida", "85 min", WHITE, 34), ("Migraciones de miles de kilómetros", None, YELLOW)],
             "¿Qué encontraría a esa profundidad?", title_y=52, label_top=1420)


if __name__ == "__main__":
    main()
