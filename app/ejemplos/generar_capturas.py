"""Genera las capturas de ejemplo del modo demo (wireframes etiquetados, no capturas reales).

Uso: python3 -m app.ejemplos.generar_capturas
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
EVIDENCIA = AQUI / "ciclo" / "qa" / "evidencia"

CAPTURAS = {
    "checkout-Checkout-CP-08-Checkout-completo-con-problem-user-chromium": {
        "url": "https://www.saucedemo.com/checkout-step-one.html",
        "titulo": "Checkout: Your Information",
        "campos": [("First Name", "Ana"), ("Last Name", ""), ("Zip/Postal Code", "10101")],
        "error": "Error: Last Name is required",
        "pie": "CP-08 · problem_user · el campo Last Name quedó vacío después de escribir «Pérez»",
    },
    "catalogo-Catalogo-CP-05-Catalogo-con-problem-user-imagenes-propias-y-orden-chromium": {
        "url": "https://www.saucedemo.com/inventory.html",
        "titulo": "Products",
        "tarjetas": ["Sauce Labs Backpack · $29.99", "Sauce Labs Bike Light · $9.99", "Sauce Labs Bolt T-Shirt · $15.99",
                     "Sauce Labs Fleece Jacket · $49.99", "Sauce Labs Onesie · $7.99", "Test.allTheThings() T-Shirt (Red) · $15.99"],
        "pie": "CP-05 · problem_user · las seis tarjetas muestran la misma imagen (sl-404.jpg)",
    },
}


def fuente(tamano: int, negrita: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for nombre in (["DejaVuSans-Bold.ttf"] if negrita else ["DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    return ImageFont.load_default()


def dibujar(nombre: str, datos: dict) -> Path:
    ancho, alto = 1280, 720
    img = Image.new("RGB", (ancho, alto), "#f4f5f7")
    d = ImageDraw.Draw(img)
    # Barra de navegador
    d.rectangle([0, 0, ancho, 48], fill="#e3e6ea")
    d.rounded_rectangle([120, 10, ancho - 120, 38], radius=8, fill="white", outline="#c9ced6")
    d.text((136, 16), datos["url"], fill="#30363d", font=fuente(15))
    # Página
    d.rectangle([0, 48, ancho, 112], fill="#1f2a37")
    d.text((40, 68), "Swag Labs (wireframe)", fill="white", font=fuente(20, True))
    d.text((40, 132), datos["titulo"], fill="#1f2a37", font=fuente(26, True))

    if "campos" in datos:
        y = 190
        for etiqueta, valor in datos["campos"]:
            d.rounded_rectangle([40, y, 520, y + 46], radius=6, fill="white", outline="#c9ced6")
            d.text((52, y + 13), valor if valor else etiqueta, fill="#1f2a37" if valor else "#9aa3ad", font=fuente(16))
            y += 62
        d.rounded_rectangle([40, y, 520, y + 46], radius=6, fill="#e2231a")
        d.text((52, y + 13), datos["error"], fill="white", font=fuente(16, True))
        y += 70
        d.rounded_rectangle([40, y, 200, y + 44], radius=6, fill="#3ddc91")
        d.text((80, y + 12), "Continue", fill="#1f2a37", font=fuente(16, True))

    if "tarjetas" in datos:
        x0, y0 = 40, 180
        for i, nombre_tarjeta in enumerate(datos["tarjetas"]):
            x = x0 + (i % 3) * 400
            y = y0 + (i // 3) * 230
            d.rounded_rectangle([x, y, x + 370, y + 210], radius=8, fill="white", outline="#c9ced6")
            d.rectangle([x + 16, y + 16, x + 136, y + 136], fill="#dfe3e8", outline="#c9ced6")
            d.text((x + 28, y + 60), "sl-404.jpg", fill="#6b7480", font=fuente(14))
            d.text((x + 152, y + 24), nombre_tarjeta, fill="#1f2a37", font=fuente(14, True))
            d.rounded_rectangle([x + 152, y + 150, x + 330, y + 190], radius=6, outline="#1f2a37")
            d.text((x + 192, y + 161), "Add to cart", fill="#1f2a37", font=fuente(14))

    # Etiqueta de ejemplo
    d.rectangle([0, alto - 60, ancho, alto], fill="#ffd166")
    d.text((24, alto - 48), "CAPTURA DE EJEMPLO · MODO DEMO · no es una captura real de Playwright", fill="#1f2a37", font=fuente(15, True))
    d.text((24, alto - 26), datos["pie"], fill="#1f2a37", font=fuente(14))

    carpeta = EVIDENCIA / nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / "test-failed-1.png"
    img.save(ruta, optimize=True)
    return ruta


if __name__ == "__main__":
    for nombre, datos in CAPTURAS.items():
        print("→", dibujar(nombre, datos))
