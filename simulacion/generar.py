"""Genera todos los resultados de la entrega 3 en un solo archivo: simulacion/resultados/resultados.json.

Es la única fuente de cifras para el informe, el deck y el tablero: si cambia un supuesto,
se vuelve a correr este script y todo queda consistente.

Uso, desde la raíz del repositorio:
    python -m simulacion.generar            # todo, con el MCMC (unos 40 s)
    python -m simulacion.generar --sin-mcmc # reutiliza el MCMC guardado (sin PyMC)
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from . import agente, cliente, montecarlo
from .modelo import BASE, correr_escenario

SALIDA = Path(__file__).parent / "resultados"
ESCENARIOS = ["base", "conservador", "optimista", "precio -20%", "clientes nuevos -20%", "costo variable 35%",
              "bajas +50%", "clientes nuevos +20%", "precio +20%"]
PUBLICADO = {  # necesidad máxima, mes de equilibrio, mes de recuperación (caso de negocio)
    "base": (991_523, 35, 60), "conservador": (1_498_616, 53, None), "optimista": (685_568, 29, 44),
    "precio -20%": (1_288_747, 45, None), "clientes nuevos -20%": (1_236_876, 43, None),
    "costo variable 35%": (1_136_683, 39, None), "bajas +50%": (1_040_135, 37, None),
    "clientes nuevos +20%": (800_803, 32, 50), "precio +20%": (791_213, 31, 49),
}


def _limpio(x):
    """Convierte arreglos y números de numpy en tipos de JSON; NaN pasa a null."""
    if isinstance(x, dict):
        return {str(k): _limpio(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpio(v) for v in x]
    if isinstance(x, np.ndarray):
        return _limpio(x.tolist())
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def escenarios_deterministas() -> list:
    filas = []
    for nombre in ESCENARIOS:
        r = correr_escenario(nombre)
        i, s = r["indicadores"], r["simulacion"]
        pub = PUBLICADO[nombre]
        filas.append(dict(
            escenario=nombre, necesidad_maxima=i["necesidad_maxima"], mes_necesidad=i["mes_necesidad"],
            mes_equilibrio=i["mes_equilibrio"], mes_recuperacion=i["mes_recuperacion"],
            van_sin_vt=i["van_sin_vt"], van_con_vt=i["van_con_vt"], tir_con_vt=i["tir_con_vt"],
            arr_m12=s["arr"][0][11], arr_m24=s["arr"][0][23], arr_m36=s["arr"][0][35], clientes_m36=s["clientes"][0][35],
            resultados_anuales=i["resultados_anuales"], ingresos_anuales=i["ingresos_anuales"], caja_m60=i["caja_m60"],
            publicado_necesidad=pub[0], publicado_equilibrio=pub[1], publicado_recuperacion=pub[2],
            diferencia_necesidad=(i["necesidad_maxima"] - pub[0]) / pub[0],
        ))
    return filas


def serie_base() -> dict:
    s = correr_escenario("base")["simulacion"]
    return {k: s[k][0] for k in ("ingresos", "costo_variable", "gasto_fijo", "resultado", "caja", "arr", "clientes")}


def main(sin_mcmc: bool = False) -> dict:
    t0 = time.perf_counter()
    SALIDA.mkdir(parents=True, exist_ok=True)
    res = montecarlo.correr()
    mc = montecarlo.analizar(res)
    mc["descomposicion"] = montecarlo.descomposicion()
    ag = agente.analizar()
    ruta_mcmc = SALIDA / "mcmc.json"
    if sin_mcmc and ruta_mcmc.exists():
        mcmc_res = json.loads(ruta_mcmc.read_text(encoding="utf-8"))
    else:
        from . import mcmc
        mcmc_res = _limpio(mcmc.ajustar(np.array(ag["matriz"]["valores"])))
        ruta_mcmc.write_text(json.dumps(mcmc_res, ensure_ascii=False, indent=1), encoding="utf-8")
    resultados = _limpio({
        "generado": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "semilla": res["incertidumbre"].semilla,
        "escenarios": escenarios_deterministas(),
        "serie_base": serie_base(),
        "montecarlo": mc,
        "cliente": cliente.analizar(),
        "agente": ag,
        "mcmc": mcmc_res,
    })
    (SALIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")
    # tablas en CSV para quien prefiera abrirlas en una hoja de cálculo
    with open(SALIDA / "escenarios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "necesidad_maxima", "mes_necesidad", "mes_equilibrio", "mes_recuperacion", "van_con_vt", "publicado_necesidad"])
        for e in resultados["escenarios"]:
            w.writerow([e["escenario"], round(e["necesidad_maxima"]), e["mes_necesidad"], e["mes_equilibrio"],
                        e["mes_recuperacion"], round(e["van_con_vt"]), e["publicado_necesidad"]])
    ind = res["indicadores"]
    with open(SALIDA / "corridas_montecarlo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cols = ["m_altas", "m_bajas", "costo_variable", "precio", "pilotos_pagan"]
        w.writerow(cols + ["necesidad_maxima", "mes_equilibrio", "mes_recuperacion", "caja_m60", "van_con_vt", "arr_m12", "arr_m24", "arr_m36"]
                   + [f"hito{k}" for k in range(1, 5)])
        for i in range(res["hitos"].shape[0]):
            w.writerow([round(float(res["sorteos"][c][i]), 4) for c in cols]
                       + [round(float(ind[k][i]), 0) if not np.isnan(ind[k][i]) else "" for k in
                          ("necesidad_maxima", "mes_equilibrio", "mes_recuperacion", "caja_m60", "van_con_vt", "arr_m12", "arr_m24", "arr_m36")]
                       + [int(v) for v in res["hitos"][i]])
    print(f"Resultados en {SALIDA} ({time.perf_counter() - t0:.1f} s)")
    return resultados


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sin-mcmc", action="store_true", help="reutiliza simulacion/resultados/mcmc.json")
    main(ap.parse_args().sin_mcmc)
