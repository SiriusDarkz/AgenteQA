"""Arma la demo web autocontenida: la interfaz real con un servidor simulado dentro del propio HTML.

    python3 -m app.ejemplos.armar_demo_web [--artifact RUTA]

Genera app/ejemplos/demo-web.html (se abre en cualquier navegador, sin instalar nada) y, con
--artifact, un fragmento sin <html>/<head>/<body> para publicarlo como vista previa en claude.ai.
Reúne app/ui/* (la misma interfaz que sirve el backend), el ciclo de ejemplo de app/ejemplos/ciclo/
y app/ejemplos/demo_web/servidor_simulado.js, que reproduce en JavaScript el modo demo.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
RAIZ = APP.parent
UI = APP / "ui"
CICLO = APP / "ejemplos" / "ciclo"


def datos() -> tuple[str, str]:
    archivos = {
        "requisitos": (RAIZ / "qa" / "requisitos.md").read_text(encoding="utf-8"),
        "ejemplos": {
            "exploracion.md": (CICLO / "qa" / "exploracion.md").read_text(encoding="utf-8"),
            "plan-de-pruebas.md": (CICLO / "qa" / "plan-de-pruebas.md").read_text(encoding="utf-8"),
            **{r.name: r.read_text(encoding="utf-8") for r in sorted((CICLO / "qa" / "defectos").glob("DEF-*.md"))},
        },
        "tests": {
            "datos.ts": (RAIZ / "tests" / "datos.ts").read_text(encoding="utf-8"),
            "ejemplo.spec.ts": (RAIZ / "tests" / "ejemplo.spec.ts").read_text(encoding="utf-8"),
            **{r.name: r.read_text(encoding="utf-8") for r in sorted((CICLO / "tests").glob("*.spec.ts"))},
        },
    }
    evidencia = {}
    for png in sorted((CICLO / "qa" / "evidencia").rglob("*.png")):
        rel = png.relative_to(CICLO / "qa" / "evidencia").as_posix()
        evidencia[rel] = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
    return json.dumps(archivos, ensure_ascii=False), json.dumps(evidencia)


def cuerpo_html() -> str:
    html = (UI / "index.html").read_text(encoding="utf-8")
    cuerpo = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    cuerpo = re.sub(r"\s*<script src=\"/ui/[^\"]+\"></script>", "", cuerpo)
    return cuerpo.strip()


def armar(para_artifact: bool) -> str:
    archivos, evidencia = datos()
    simulado = (APP / "ejemplos" / "demo_web" / "servidor_simulado.js").read_text(encoding="utf-8")
    simulado = simulado.replace("__ARCHIVOS__", archivos).replace("__EVIDENCIA__", evidencia)
    css = (UI / "estilos.css").read_text(encoding="utf-8")
    app_js = (UI / "app.js").read_text(encoding="utf-8")
    marked = (UI / "marked.umd.js").read_text(encoding="utf-8")
    fuentes = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
               '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
               '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">')
    extra_css = "a[download] { display: none !important; }" if para_artifact else ""
    scripts = (f"<script>{'window.QA_SIN_TEMA = true;' if para_artifact else ''}window.QA_DEMO_VELOCIDAD = 0.45;</script>\n"
               f"<script>{marked}</script>\n<script>{simulado}</script>\n<script>{app_js}</script>")
    if para_artifact:
        return (f"<title>Agente Virtual de QA</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n{fuentes}\n"
                f"<style>\n{css}\n{extra_css}\n</style>\n{cuerpo_html()}\n{scripts}\n")
    return ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>Agente Virtual de QA · demo</title>\n"
            "<script>try { var t = localStorage.getItem('qa-tema'); if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t; } catch (e) {}</script>\n"
            f"{fuentes}\n<style>\n{css}\n</style>\n</head>\n<body>\n{cuerpo_html()}\n{scripts}\n</body>\n</html>\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", help="ruta del fragmento para publicar como vista previa")
    args = parser.parse_args()
    salida = APP / "ejemplos" / "demo-web.html"
    salida.write_text(armar(False), encoding="utf-8")
    print(f"→ {salida} ({salida.stat().st_size // 1024} KB)")
    if args.artifact:
        Path(args.artifact).write_text(armar(True), encoding="utf-8")
        print(f"→ {args.artifact}")


if __name__ == "__main__":
    main()
