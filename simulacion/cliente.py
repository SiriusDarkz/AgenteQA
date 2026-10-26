"""Valor para el cliente: ¿cuándo se paga solo el plan? (simulación Monte Carlo).

La mejora de productividad que logra un cliente es incierta. El World Quality Report 2025
reporta 19 % en promedio y que un tercio de las organizaciones obtuvo mejoras mínimas; la meta
de diseño del producto es 35 %. Modelamos la mejora como una mezcla:

- con probabilidad 1/3, una mejora mínima, uniforme entre 0 % y 5 %;
- con probabilidad 2/3, una normal truncada (5 % a 60 %) con media 27.25 % y desviación 8 %,
  de modo que el promedio general sea 19 %.

El beneficio del primer año es la capacidad liberada del equipo de QA (mejora × costo anual
del equipo); el costo es la suscripción de 12 meses más la implementación. Igual que el caso
de negocio, deja fuera el valor de publicar antes y el de los defectos evitados.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

PLANES = {"Inicial": (490.0, 0.0), "Profesional": (1490.0, 2500.0), "Empresarial": (4900.0, 12000.0)}


@dataclass(frozen=True)
class SupuestosCliente:
    costo_persona_mes: float = 3000.0      # ingeniero de QA de nivel medio, con cargas (South, 2026)
    prob_minima: float = 1 / 3
    minima: tuple = (0.0, 0.05)
    resto_media: float = 0.2725
    resto_desv: float = 0.08
    resto_limites: tuple = (0.05, 0.60)
    meta: float = 0.35
    promedio_wqr: float = 0.19


def sortear_mejora(sc: SupuestosCliente, n: int, rng: np.random.Generator) -> np.ndarray:
    minima = rng.random(n) < sc.prob_minima
    a, b = [(x - sc.resto_media) / sc.resto_desv for x in sc.resto_limites]
    resto = stats.truncnorm.rvs(a, b, loc=sc.resto_media, scale=sc.resto_desv, size=n, random_state=rng)
    return np.where(minima, rng.uniform(*sc.minima, n), resto)


def costo_primer_anio(plan: str) -> float:
    precio, impl = PLANES[plan]
    return 12 * precio + impl


def evaluar(personas: int, plan: str, mejora, sc: SupuestosCliente = SupuestosCliente()) -> dict:
    """ROI y meses para recuperar el costo del primer año, para una o varias mejoras."""
    mejora = np.asarray(mejora, float)
    equipo = personas * sc.costo_persona_mes * 12
    costo = costo_primer_anio(plan)
    beneficio = mejora * equipo
    roi = (beneficio - costo) / costo
    meses = np.where(beneficio > 0, costo / np.maximum(beneficio / 12, 1e-9), np.inf)
    return {"equipo_anual": equipo, "costo_primer_anio": costo, "beneficio": beneficio, "roi": roi,
            "meses_recuperacion": meses, "mejora_minima": costo / equipo}


def analizar(n: int = 10_000, semilla: int = 20261026, sc: SupuestosCliente = SupuestosCliente()) -> dict:
    rng = np.random.default_rng(semilla)
    mejora = sortear_mejora(sc, n, rng)
    tabla = []
    for plan in ("Inicial", "Profesional"):
        for personas in (1, 2, 3, 4, 6):
            r = evaluar(personas, plan, mejora, sc)
            tabla.append(dict(plan=plan, personas=personas, mejora_minima=float(r["mejora_minima"]),
                              prob_se_paga=float((r["roi"] > 0).mean()),
                              roi_p10=float(np.percentile(r["roi"], 10)), roi_p50=float(np.percentile(r["roi"], 50)),
                              roi_p90=float(np.percentile(r["roi"], 90)),
                              prob_recupera_12_meses=float((r["meses_recuperacion"] <= 12).mean())))
    ref = evaluar(4, "Profesional", mejora, sc)
    det = {etq: {k: float(v) if np.ndim(v) == 0 else float(v[()]) for k, v in evaluar(4, "Profesional", m, sc).items()}
           for etq, m in (("promedio_wqr", sc.promedio_wqr), ("meta", sc.meta))}
    cuentas, bordes = np.histogram(ref["roi"], bins=40)
    return {
        "mejora": {"media": float(mejora.mean()), "p10": float(np.percentile(mejora, 10)),
                   "p50": float(np.percentile(mejora, 50)), "p90": float(np.percentile(mejora, 90)),
                   "prob_bajo_12_4": float((mejora < 0.124).mean())},
        "referencia": {"personas": 4, "plan": "Profesional", "prob_se_paga": float((ref["roi"] > 0).mean()),
                       "roi_p10": float(np.percentile(ref["roi"], 10)), "roi_p50": float(np.percentile(ref["roi"], 50)),
                       "roi_p90": float(np.percentile(ref["roi"], 90)), "roi_media": float(ref["roi"].mean()),
                       "histograma_roi": {"cuentas": cuentas.tolist(), "bordes": bordes.round(3).tolist()}},
        "deterministico": det,
        "tabla": tabla,
    }
