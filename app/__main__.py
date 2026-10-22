"""Arranca la interfaz del MVP.

  python3 -m app            # agente real (Claude Agent SDK) sobre este repo
  python3 -m app --demo     # ciclo de ejemplo, sin API ni navegador
  python3 -m app --puerto 9000
"""

from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from pathlib import Path


def cargar_env() -> None:
    """Lee app/.env (una variable por línea, CLAVE=valor) sin pisar las que ya existen.

    Así la llave de la API se escribe una sola vez en vez de exportarla en cada terminal.
    """
    ruta = Path(__file__).resolve().parent / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip().removeprefix("export ").strip()
        valor = valor.strip().strip("'\"")
        if clave:
            os.environ.setdefault(clave, valor)


def main() -> None:
    cargar_env()
    parser = argparse.ArgumentParser(prog="python3 -m app", description="Interfaz web del Agente Virtual de QA")
    parser.add_argument("--demo", action="store_true", help="modo demo: ciclo de ejemplo sin llamar a la API")
    parser.add_argument("--puerto", type=int, default=int(os.environ.get("QA_PUERTO", "8765")))
    parser.add_argument("--sin-navegador", action="store_true", help="no abrir el navegador al arrancar")
    args = parser.parse_args()

    os.environ["QA_MODO"] = "demo" if args.demo else "sdk"
    if not args.demo and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Aviso: no encontré ANTHROPIC_API_KEY. Escríbela en app/.env (ANTHROPIC_API_KEY=sk-ant-...)"
              " o arranca con --demo para ver la interfaz con el ciclo de ejemplo.")

    try:
        import uvicorn
    except ImportError:
        sys.exit("Falta uvicorn. Instala las dependencias: pip install -r app/requirements.txt")

    from . import estado  # noqa: WPS433 — después de fijar el modo

    url = f"http://localhost:{args.puerto}"
    print(f"Agente Virtual de QA · modo {'DEMO' if args.demo else 'AGENTE REAL'} · repo {estado.RAIZ}")
    print(f"Abre {url}  (Ctrl+C para detener)")
    if not args.sin_navegador:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    uvicorn.run("app.servidor:app", host="127.0.0.1", port=args.puerto, log_level="warning")


if __name__ == "__main__":
    main()
