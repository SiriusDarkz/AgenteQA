"""Modelo bayesiano jerárquico de detección de defectos, estimado con MCMC (PyMC, NUTS).

Pregunta: ¿qué probabilidad tiene el agente de encontrar un defecto conocido en un ciclo, y
cuánto sube la cobertura si se corre varias veces?

Datos: la matriz de 21 defectos funcionales × 3 ciclos reales (1 = el ciclo reportó ese defecto).
Modelo (parametrización no centrada):

    logit P(detecta defecto d en ciclo c) = mu + sd_defecto · z_d + sd_ciclo · w_c
    z_d, w_c ~ Normal(0, 1);  mu ~ Normal(0, 1.5);  sd_defecto ~ HalfNormal(1.5);  sd_ciclo ~ HalfNormal(1)

El efecto por defecto recoge que algunos defectos son fáciles (el orden invertido aparece en los
tres ciclos) y otros nunca aparecen; el efecto por ciclo, que cada corrida del modelo de lenguaje
es distinta. Con la posterior se simula un ciclo nuevo y k ciclos independientes.
"""
from __future__ import annotations

import numpy as np


def ajustar(matriz: np.ndarray, semilla: int = 20261026, draws: int = 2000, tune: int = 2000, chains: int = 4) -> dict:
    import arviz as az
    import pymc as pm

    n_def, n_cic = matriz.shape
    d_idx = np.repeat(np.arange(n_def), n_cic)
    c_idx = np.tile(np.arange(n_cic), n_def)
    y = matriz.reshape(-1)
    with pm.Model():
        mu = pm.Normal("mu", 0.0, 1.5)
        sd_def = pm.HalfNormal("sd_defecto", 1.5)
        sd_cic = pm.HalfNormal("sd_ciclo", 1.0)
        z = pm.Normal("z", 0.0, 1.0, shape=n_def)
        w = pm.Normal("w", 0.0, 1.0, shape=n_cic)
        pm.Bernoulli("y", logit_p=mu + sd_def * z[d_idx] + sd_cic * w[c_idx], observed=y)
        idata = pm.sample(draws=draws, tune=tune, chains=chains, cores=1, target_accept=0.95, random_seed=semilla,
                          progressbar=False, compute_convergence_checks=True)

    resumen = az.summary(idata, var_names=["mu", "sd_defecto", "sd_ciclo"])
    todos = az.summary(idata, var_names=["mu", "sd_defecto", "sd_ciclo", "z", "w"])   # incluye los 24 efectos aleatorios
    post = idata.posterior
    mu = post["mu"].values.reshape(-1)
    sd_def = post["sd_defecto"].values.reshape(-1)
    sd_cic = post["sd_ciclo"].values.reshape(-1)
    z = post["z"].values.reshape(-1, n_def)
    rng = np.random.default_rng(semilla)
    S = mu.size

    def p_ciclo_nuevo():
        w_nuevo = rng.standard_normal(S)
        return 1 / (1 + np.exp(-(mu[:, None] + sd_def[:, None] * z + (sd_cic * w_nuevo)[:, None])))

    recall_nuevo = p_ciclo_nuevo().mean(axis=1)            # cobertura esperada de un ciclo nuevo
    cobertura_k = {}
    no_detectado = np.ones((S, n_def))
    for k in range(1, 6):
        no_detectado *= 1 - p_ciclo_nuevo()
        cobertura_k[k] = 1 - no_detectado.mean(axis=1)
    p_def = 1 / (1 + np.exp(-(mu[:, None] + sd_def[:, None] * z)))   # facilidad de cada defecto (ciclo típico)

    def ic(v):
        return {"media": float(v.mean()), "ic_bajo": float(np.percentile(v, 2.5)), "ic_alto": float(np.percentile(v, 97.5))}

    divergencias = int(idata.sample_stats["diverging"].values.sum())
    return {
        "diagnostico": {
            "cadenas": chains, "muestras_por_cadena": draws, "calentamiento": tune, "divergencias": divergencias,
            "r_hat_max": float(resumen["r_hat"].max()), "ess_bulk_min": float(resumen["ess_bulk"].min()),
            "parametros_revisados": int(len(todos)),
            "r_hat_max_todos": float(todos["r_hat"].max()), "ess_bulk_min_todos": float(todos["ess_bulk"].min()),
            "parametros": {k: {"media": float(resumen.loc[k, "mean"]), "sd": float(resumen.loc[k, "sd"]),
                               "r_hat": float(resumen.loc[k, "r_hat"]), "ess_bulk": float(resumen.loc[k, "ess_bulk"])}
                           for k in ("mu", "sd_defecto", "sd_ciclo")},
        },
        "recall_ciclo_nuevo": ic(recall_nuevo),
        "cobertura_k_ciclos": {str(k): ic(v) for k, v in cobertura_k.items()},
        "prob_por_defecto": [ic(p_def[:, i]) for i in range(n_def)],
    }
