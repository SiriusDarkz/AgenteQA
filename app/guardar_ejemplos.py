"""Guarda el ciclo actual de qa/ y tests/ como el ejemplo que reproduce el modo demo.

Úsalo después de un ensayo real completo (los cinco pasos), para que la demo
muestre tu exploración, tu plan, tus pruebas y tus defectos reales en vez del
ejemplo escrito a mano:

    python3 -m app.guardar_ejemplos

Qué copia a app/ejemplos/ciclo/: qa/exploracion.md, qa/plan-de-pruebas.md,
tests/*.spec.ts (menos ejemplo.spec.ts), qa/defectos/DEF-*.md y las capturas de
qa/evidencia/. Los resultados y el reporte del modo demo se generan a partir del
plan aprobado, así que no se copian; ajusta app/demo.py (RESULTADOS, ERRORES y
DEFECTOS) con los IDs de tus casos si cambiaron.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from . import estado

CICLO = Path(__file__).resolve().parent / "ejemplos" / "ciclo"


def main() -> None:
    faltan = [n for n in ("exploracion", "plan") if not estado.DOCUMENTOS[n].exists()]
    if faltan:
        sys.exit(f"Faltan archivos del ciclo: {', '.join(faltan)}. Corre primero los pasos 1 y 2.")

    copiados: list[str] = []

    def copiar(origen: Path, destino: Path) -> None:
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origen.is_dir():
            if destino.exists():
                shutil.rmtree(destino)
            shutil.copytree(origen, destino)
        else:
            shutil.copy2(origen, destino)
        copiados.append(estado.relativa(origen))

    copiar(estado.DOCUMENTOS["exploracion"], CICLO / "qa" / "exploracion.md")
    # El plan del ejemplo debe quedar sin aprobar: la persona lo aprueba en la demo.
    texto = estado.DOCUMENTOS["plan-generado"].read_text(encoding="utf-8") if estado.DOCUMENTOS["plan-generado"].exists() \
        else estado.DOCUMENTOS["plan"].read_text(encoding="utf-8")
    lineas = texto.rstrip().splitlines()
    while lineas and (lineas[-1].strip() == "" or lineas[-1].strip().upper().startswith("ESTADO:")
                      or lineas[-1].startswith("Aprobado desde la interfaz")):
        lineas.pop()
    (CICLO / "qa").mkdir(parents=True, exist_ok=True)
    (CICLO / "qa" / "plan-de-pruebas.md").write_text("\n".join(lineas) + "\n\nEstado: PENDIENTE DE APROBACIÓN\n", encoding="utf-8")
    copiados.append("qa/plan-de-pruebas.md")

    for ruta in sorted(estado.TESTS.glob("*.spec.ts")):
        if ruta.name != "ejemplo.spec.ts":
            copiar(ruta, CICLO / "tests" / ruta.name)
    if estado.DEFECTOS.exists():
        for ruta in sorted(estado.DEFECTOS.glob("DEF-*.md")):
            copiar(ruta, CICLO / "qa" / "defectos" / ruta.name)
    if estado.EVIDENCIA.exists():
        for ruta in sorted(estado.EVIDENCIA.rglob("*.png")):
            copiar(ruta, CICLO / estado.relativa(ruta))

    print("Guardado en app/ejemplos/ciclo/:")
    for c in copiados:
        print("  ·", c)
    print("\nRevisa app/demo.py: RESULTADOS, ERRORES y DEFECTOS deben usar los IDs de tus casos (CP-xx) y defectos (DEF-xxx).")


if __name__ == "__main__":
    main()
