"""Resume un reporte JSON de Playwright en metricas/regresion/AAAA-MM-DD.json.

Lo usa el flujo .github/workflows/regresion-nocturna.yml. Uso:
    python3 metricas/resumir_regresion.py regresion-toolshop.json [regresion-humo.json]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CARPETA = Path(__file__).parent / "regresion"
ESPERADO = {"pasaron": 2, "fallaron": 8}   # ciclo del 21-10-2026: 8 defectos conocidos de Toolshop «with bugs»


def pruebas(reporte: dict) -> list:
    """Recorre las suites del reporte y devuelve título, estado y duración de cada prueba."""
    salida = []

    def recorrer(suite):
        for spec in suite.get("specs", []):
            for t in spec.get("tests", []):
                resultados = t.get("results", [])
                ultimo = resultados[-1] if resultados else {}
                salida.append({"titulo": spec.get("title"), "estado": t.get("status"),
                               "resultado": ultimo.get("status"), "segundos": round(ultimo.get("duration", 0) / 1000, 1)})
        for s in suite.get("suites", []):
            recorrer(s)

    for s in reporte.get("suites", []):
        recorrer(s)
    return salida


def resumir(ruta: Path) -> dict:
    reporte = json.loads(ruta.read_text(encoding="utf-8"))
    st = reporte.get("stats", {})
    pasaron, fallaron = st.get("expected", 0), st.get("unexpected", 0)
    return {"total": pasaron + fallaron + st.get("skipped", 0) + st.get("flaky", 0), "pasaron": pasaron,
            "fallaron": fallaron, "omitidas": st.get("skipped", 0), "inestables": st.get("flaky", 0),
            "segundos": round(st.get("duration", 0) / 1000, 1), "pruebas": pruebas(reporte)}


def main(rutas: list) -> Path:
    principal = resumir(Path(rutas[0]))
    ahora = datetime.now(timezone.utc)
    resumen = {
        "fecha": ahora.isoformat(timespec="seconds"),
        "origen": "Regresión nocturna en GitHub Actions (sin el agente y sin IA)",
        "suite": "resultados/toolshop-2026-10-21",
        "aplicacion": "https://with-bugs.practicesoftwaretesting.com",
        **principal,
        "esperado": ESPERADO,
        "coincide_con_lo_esperado": principal["pasaron"] == ESPERADO["pasaron"] and principal["fallaron"] == ESPERADO["fallaron"],
    }
    if len(rutas) > 1 and Path(rutas[1]).exists():
        humo = resumir(Path(rutas[1]))
        resumen["humo_swag_labs"] = {k: humo[k] for k in ("pasaron", "fallaron", "segundos")}
    CARPETA.mkdir(parents=True, exist_ok=True)
    destino = CARPETA / f"{ahora:%Y-%m-%d}.json"
    destino.write_text(json.dumps(resumen, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{destino}: {resumen['pasaron']} pasaron, {resumen['fallaron']} fallaron, {resumen['segundos']} s"
          + ("" if resumen["coincide_con_lo_esperado"] else " · NO coincide con lo esperado: revisar"))
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
