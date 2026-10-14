"""Rebuild four opening infographics from the existing high-resolution footage stills."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 1080, 1920
NAVY = (7, 17, 28)
BLUE = (33, 104, 175)
YELLOW = (255, 190, 24)
WHITE = (245, 247, 250)
MUTED = (190, 210, 224)
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT), size)


def gradient() -> Image.Image:
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / H
        col = tuple(round(NAVY[i] * (1 - t) + (BLUE[i] * 0.35) * t) for i in range(3))
        for x in range(W):
            glow = max(0, 1 - abs(x - W * 0.5) / (W * 0.7)) * 11
            px[x, y] = tuple(min(255, int(c + glow)) for c in col)
    return im


def centered(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill, anchor="mm", stroke=0, stroke_fill=NAVY):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def round_panel(draw: ImageDraw.ImageDraw, box, fill=(3, 12, 21), outline=YELLOW, radius=24, width=4):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def person(draw: ImageDraw.ImageDraw, x: int, ground: int, height: int, color=WHITE):
    head = max(14, height // 9)
    cy = ground - height + head // 2
    draw.ellipse((x - head // 2, cy - head // 2, x + head // 2, cy + head // 2), fill=color)
    torso_top = cy + head // 2 + 5
    torso_bottom = ground - height // 3
    draw.rounded_rectangle((x - height // 11, torso_top, x + height // 11, torso_bottom), radius=height // 18, fill=color)
    draw.line((x - height // 11, torso_top + 8, x - height // 3, ground - height // 8), fill=color, width=max(10, height // 15))
    draw.line((x + height // 11, torso_top + 8, x + height // 3, ground - height // 8), fill=color, width=max(10, height // 15))
    draw.line((x - height // 24, torso_bottom, x - height // 9, ground), fill=color, width=max(12, height // 14))
    draw.line((x + height // 24, torso_bottom, x + height // 9, ground), fill=color, width=max(12, height // 14))


def cassowary(draw: ImageDraw.ImageDraw, x: int, ground: int, height: int):
    blue = (40, 115, 213)
    purple = (147, 69, 164)
    orange = (235, 83, 30)
    body_w = int(height * 0.40)
    draw.ellipse((x - body_w // 2, ground - int(height * .68), x + body_w // 2, ground - int(height * .12)), fill=(13, 20, 24))
    draw.ellipse((x - int(height * .08), ground - int(height * .92), x + int(height * .08), ground - int(height * .60)), fill=(12, 19, 22))
    draw.polygon([(x - int(height*.075), ground-height*.91), (x, ground-height), (x+int(height*.095), ground-height*.90), (x+int(height*.07), ground-height*.82)], fill=(162, 133, 83))
    draw.polygon([(x, ground-height*.84), (x+int(height*.18), ground-height*.81), (x+int(height*.07), ground-height*.78)], fill=(23, 27, 27))
    draw.ellipse((x - int(height*.07), ground-height*.79, x + int(height*.07), ground-height*.54), fill=blue)
    draw.polygon([(x-int(height*.04), ground-height*.65), (x+int(height*.10), ground-height*.64), (x+int(height*.03), ground-height*.39), (x-int(height*.09), ground-height*.44)], fill=purple)
    draw.line((x-int(height*.11), ground-height*.50, x-int(height*.14), ground-height*.24, x-int(height*.20), ground-height*.05), fill=orange, width=max(9, height//21))
    draw.line((x+int(height*.07), ground-height*.50, x+int(height*.12), ground-height*.23, x+int(height*.20), ground-height*.05), fill=orange, width=max(9, height//21))
    draw.line((x-int(height*.20), ground-height*.05, x-int(height*.26), ground-height*.03), fill=orange, width=max(8, height//24))
    draw.line((x+int(height*.20), ground-height*.05, x+int(height*.26), ground-height*.03), fill=orange, width=max(8, height//24))


def turtle_icon(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color=YELLOW):
    r = int(31*scale)
    draw.ellipse((x-r, y-r//2, x+r, y+r//2), fill=color)
    draw.ellipse((x+r-2, y-r//3, x+r+int(16*scale), y+r//4), fill=color)
    for dx, dy in [(-.65, -.45), (.35, -.5), (-.65, .35), (.35, .35)]:
        xx, yy = x+int(dx*r), y+int(dy*r)
        draw.ellipse((xx-int(18*scale), yy-int(7*scale), xx+int(12*scale), yy+int(9*scale)), fill=color)


def add_photo(canvas: Image.Image, folder: Path):
    original = folder / "apertura-infografica-original.png"
    old = original if original.exists() else folder / "apertura-infografica.png"
    with Image.open(old) as source:
        source = source.convert("RGB")
        # The previous opener's photograph is framed inside this rectangle.
        photo = source.crop((43, 344, 1037, 1223))
        photo = ImageOps.fit(photo, (1080, 810), method=Image.Resampling.LANCZOS, centering=(0.5, 0.47))
    photo = photo.filter(ImageFilter.UnsharpMask(radius=1.5, percent=115, threshold=3))
    # Bleed the landscape still edge-to-edge, like the reference poster, so it
    # reads as one scene rather than a framed thumbnail card.
    canvas.paste(photo, (0, 390))


def create_colibri(folder: Path):
    im = gradient(); d = ImageDraw.Draw(im)
    round_panel(d, (90, 82, 990, 335), fill=(3, 12, 21), outline=YELLOW, radius=20, width=3)
    centered(d, (540, 145), "EL VUELO EN UN SEGUNDO", font(38, True), WHITE)
    centered(d, (540, 242), "75 ALETEOS", font(74, True), YELLOW)
    add_photo(im, folder); d = ImageDraw.Draw(im)
    round_panel(d, (72, 1202, 1008, 1672), fill=(3, 12, 21), outline=YELLOW, radius=26, width=4)
    centered(d, (540, 1280), "HASTA", font(33, True), MUTED)
    centered(d, (540, 1400), "75", font(130, True), YELLOW)
    centered(d, (540, 1505), "ALETEOS POR SEGUNDO", font(48, True), WHITE)
    d.rounded_rectangle((177, 1570, 903, 1604), radius=15, fill=(22, 54, 69))
    for i in range(15):
        x = 190 + i * 49
        d.line((x, 1575, x, 1598), fill=YELLOW if i % 3 == 0 else MUTED, width=4)
    centered(d, (540, 1736), "Un movimiento demasiado rápido para seguirlo a simple vista", font(27), MUTED)
    centered(d, (540, 1840), "DATO VERIFICADO • FUENTE EN LA DESCRIPCIÓN", font(25, True), WHITE)
    return im


def create_casuario(folder: Path):
    im = gradient(); d = ImageDraw.Draw(im)
    round_panel(d, (90, 80, 990, 335), fill=(3, 12, 21), outline=YELLOW, radius=20, width=3)
    centered(d, (540, 145), "¿MÁS ALTO QUE UNA PERSONA?", font(36, True), WHITE)
    centered(d, (540, 244), "EL GIGANTE DE LA SELVA", font(45, True), YELLOW)
    add_photo(im, folder); d = ImageDraw.Draw(im)
    round_panel(d, (72, 1202, 1008, 1700), fill=(3, 12, 21), outline=YELLOW, radius=26, width=4)
    centered(d, (540, 1262), "ALTURA A ESCALA", font(34, True), WHITE)
    ground = 1610
    d.line((190, ground, 890, ground), fill=MUTED, width=4)
    person(d, 365, ground, 245, color=(213, 223, 231))
    cassowary(d, 710, ground, 290)
    centered(d, (365, 1653), "PERSONA", font(25, True), MUTED)
    centered(d, (365, 1682), "1,70 m", font(31, True), WHITE)
    centered(d, (710, 1653), "CASUARIO", font(25, True), YELLOW)
    centered(d, (710, 1682), "hasta 2 m", font(31, True), WHITE)
    centered(d, (540, 1775), "Puede superar la estatura de muchas personas", font(29), MUTED)
    centered(d, (540, 1845), "DATO VERIFICADO • FUENTE EN LA DESCRIPCIÓN", font(25, True), WHITE)
    return im


def create_perezoso(folder: Path):
    im = gradient(); d = ImageDraw.Draw(im)
    round_panel(d, (90, 80, 990, 335), fill=(3, 12, 21), outline=YELLOW, radius=20, width=3)
    centered(d, (540, 145), "SU DIGESTIÓN VA A OTRO RITMO", font(37, True), WHITE)
    centered(d, (540, 244), "UN MES PARA UN ALMUERZO", font(43, True), YELLOW)
    add_photo(im, folder); d = ImageDraw.Draw(im)
    round_panel(d, (72, 1202, 1008, 1700), fill=(3, 12, 21), outline=YELLOW, radius=26, width=4)
    centered(d, (540, 1270), "HASTA", font(34, True), MUTED)
    centered(d, (540, 1376), "1 MES", font(92, True), YELLOW)
    centered(d, (540, 1465), "PARA DIGERIR UNA COMIDA", font(39, True), WHITE)
    x0, x1, y = 180, 900, 1552
    d.line((x0, y, x1, y), fill=MUTED, width=5)
    for n in range(5):
        x = x0 + n * (x1 - x0) // 4
        d.ellipse((x-13, y-13, x+13, y+13), fill=YELLOW if n in (0, 4) else WHITE)
        centered(d, (x, y+49), "INICIO" if n == 0 else ("30 DÍAS" if n == 4 else f"SEM. {n}"), font(22, True), MUTED)
    centered(d, (540, 1747), "Una comida puede tardar semanas en procesarse", font(28), MUTED)
    centered(d, (540, 1845), "DATO VERIFICADO • FUENTE EN LA DESCRIPCIÓN", font(25, True), WHITE)
    return im


def create_turtle(folder: Path):
    im = gradient(); d = ImageDraw.Draw(im)
    round_panel(d, (90, 80, 990, 335), fill=(3, 12, 21), outline=YELLOW, radius=20, width=3)
    centered(d, (540, 145), "UNA BUCEADORA EXTREMA", font(39, True), WHITE)
    centered(d, (540, 244), "HASTA 1.200 m DE PROFUNDIDAD", font(41, True), YELLOW)
    add_photo(im, folder); d = ImageDraw.Draw(im)
    round_panel(d, (72, 1202, 1008, 1700), fill=(3, 12, 21), outline=YELLOW, radius=26, width=4)
    centered(d, (540, 1260), "DESCIENDE CASI", font(34, True), MUTED)
    centered(d, (540, 1365), "1.200 m", font(94, True), YELLOW)
    centered(d, (540, 1450), "BAJO LA SUPERFICIE", font(42, True), WHITE)
    x = 240
    d.line((x, 1510, x, 1640), fill=(105, 188, 224), width=7)
    for i, label in enumerate(["0 m", "400 m", "800 m", "1.200 m"]):
        y = 1510 + i * 42
        d.line((x-18, y, x+18, y), fill=WHITE, width=4)
        centered(d, (x+93, y), label, font(22, True), MUTED, anchor="lm")
    turtle_icon(d, 705, 1636, 0.85)
    d.ellipse((696, 1627, 714, 1645), outline=WHITE, width=3)
    centered(d, (540, 1746), "Imagina apilar doce edificios de 100 m", font(28), MUTED)
    centered(d, (540, 1845), "DATO VERIFICADO • FUENTE EN LA DESCRIPCIÓN", font(25, True), WHITE)
    return im


CREATORS = {"Colibri": create_colibri, "Casuario": create_casuario, "Perezoso": create_perezoso, "TortugaLaud": create_turtle}


def main():
    for name, creator in CREATORS.items():
        folder = ROOT / "data" / "jobs" / name
        target = folder / "apertura-infografica.png"
        original = folder / "apertura-infografica-original.png"
        if not original.exists():
            target.replace(original)
        creator(folder).save(target, format="PNG", optimize=True)
        print(f"{name}: {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
