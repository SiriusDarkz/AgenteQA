"""Métricas técnicas del agente en los tres ciclos reales sobre Toolshop «with bugs».

El paso 4 del agente clasifica cada fallo como defecto de la aplicación o problema de la
prueba: es un clasificador, así que lo medimos con precisión, exhaustividad (recall) y F1
contra una verdad de referencia, la lista oficial de defectos de Testsmith más los defectos
verificados en el código fuente. RMSE no aplica porque el agente no predice valores continuos.

Con tan pocos casos, cada proporción se reporta con su intervalo creíble bayesiano del 95 %
(prior uniforme Beta(1, 1)): con 8 defectos, «87.5 %» puede ser cualquier valor entre 52 % y 97 %.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

DATOS = Path(__file__).parent / "datos" / "ciclos.json"


def cargar(ruta: Path = DATOS) -> dict:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def intervalo(exitos: int, total: int, nivel: float = 0.95) -> dict:
    """Proporción observada e intervalo creíble con prior uniforme."""
    post = stats.beta(1 + exitos, 1 + total - exitos)
    a = (1 - nivel) / 2
    return {"exitos": int(exitos), "total": int(total), "valor": exitos / total if total else None,
            "media_posterior": float(post.mean()), "ic_bajo": float(post.ppf(a)), "ic_alto": float(post.ppf(1 - a))}


def f1_con_incertidumbre(vp: int, fp: int, fn: int, n: int = 200_000, semilla: int = 1) -> dict:
    rng = np.random.default_rng(semilla)
    p = rng.beta(1 + vp, 1 + fp, n)
    r = rng.beta(1 + vp, 1 + fn, n)
    f1 = 2 * p * r / (p + r)
    prec, rec = vp / (vp + fp), vp / (vp + fn)
    return {"valor": 2 * prec * rec / (prec + rec), "ic_bajo": float(np.percentile(f1, 2.5)),
            "ic_alto": float(np.percentile(f1, 97.5))}


def matriz_deteccion(d: dict) -> tuple:
    """Matriz defectos × ciclos: 1 si el ciclo reportó ese defecto del universo funcional."""
    ids = [u["id"] for u in d["universo_funcional"]]
    m = np.zeros((len(ids), len(d["ciclos"])), dtype=int)
    for j, c in enumerate(d["ciclos"]):
        for df in c["defectos"]:
            if df["veredicto"] == "VP" and df["detecta"] in ids:
                m[ids.index(df["detecta"]), j] = 1
    return ids, m


def analizar(d: dict | None = None) -> dict:
    d = d or cargar()
    ids, m = matriz_deteccion(d)
    universo = len(ids)
    requisitos = {u["id"]: u["requisito"] for u in d["universo_funcional"]}
    por_ciclo = []
    vp_t = fp_t = fn_t = 0
    for j, c in enumerate(d["ciclos"]):
        vp = sum(1 for x in c["defectos"] if x["veredicto"] == "VP")
        fp = sum(1 for x in c["defectos"] if x["veredicto"] == "FP")
        vp_func = int(m[:, j].sum())
        fn = universo - vp_func
        vp_t += vp; fp_t += fp
        decisiones = [x for x in c["defectos"] if x["humano"] in ("CONFIRMADO", "DESCARTADO")]
        acierto = sum(1 for x in decisiones if (x["humano"] == "CONFIRMADO") == (x["veredicto"] == "VP"))
        ej = c["ejecucion"]
        por_ciclo.append({
            "ciclo": c["id"], "fecha": c["fecha"], "estado": c["estado"],
            "defectos_reportados": vp + fp, "verdaderos": vp, "falsos_positivos": fp,
            "precision": intervalo(vp, vp + fp),
            "recall_funcional": intervalo(vp_func, universo),
            "f1": f1_con_incertidumbre(vp_func, fp, fn),
            "aceptacion_plan": intervalo(c["plan"]["aceptados_sin_edicion"], c["plan"]["generados"]),
            "pruebas_primer_intento": intervalo(ej["correctas_primer_intento"], ej["casos"]),
            "casos": ej["casos"], "pasaron": ej["pasaron"], "fallaron": ej["fallaron"],
            "segundos_ejecucion": ej["segundos"], "revision_plan_seg": c["plan"]["revision_humana_seg"],
            "duracion_ciclo_min": c["duracion_ciclo_min"], "duracion_nota": c["duracion_nota"],
            "decisiones_humanas": len(decisiones), "decisiones_correctas": acierto,
            "costo_usd_tope": c["costo_usd_tope"],
            "detectados": [ids[i] for i in range(universo) if m[i, j]],
        })
    union = m.max(axis=1)
    aceptados = sum(c["plan"]["aceptados_sin_edicion"] for c in d["ciclos"])
    generados = sum(c["plan"]["generados"] for c in d["ciclos"])
    primer = sum(c["ejecucion"]["correctas_primer_intento"] for c in d["ciclos"])
    casos = sum(c["ejecucion"]["casos"] for c in d["ciclos"])
    dec = sum(x["decisiones_humanas"] for x in por_ciclo)
    dec_ok = sum(x["decisiones_correctas"] for x in por_ciclo)
    por_requisito = {}
    for r in sorted(set(requisitos.values())):
        filas = [i for i, k in enumerate(ids) if requisitos[k] == r]
        por_requisito[r] = {"defectos": len(filas), "detectados_union": int(union[filas].sum()),
                            "detecciones": int(m[filas].sum()), "oportunidades": len(filas) * m.shape[1]}
    tope = d["ciclos"][0]["costo_usd_tope"]
    planes = {"Inicial": 490, "Profesional": 1490, "Empresarial": 4900}
    return {
        "universo_funcional": universo,
        "por_ciclo": por_ciclo,
        "agregado": {
            "precision": intervalo(vp_t, vp_t + fp_t),
            "recall_por_ciclo": intervalo(int(m.sum()), m.size),
            "recall_union": intervalo(int(union.sum()), universo),
            "aceptacion_plan": intervalo(aceptados, generados),
            "prob_aceptacion_70": float(1 - stats.beta(1 + aceptados, 1 + generados - aceptados).cdf(0.70)),
            "pruebas_primer_intento": intervalo(primer, casos),
            "decisiones_humanas_correctas": intervalo(dec_ok, dec),
        },
        "por_requisito": por_requisito,
        "matriz": {"defectos": ids, "ciclos": [c["id"] for c in d["ciclos"]], "valores": m.tolist()},
        "costo": {"tope_por_ciclo_usd": tope,
                  "ciclos_que_cubre_el_25_por_ciento": {p: int(0.25 * v // tope) for p, v in planes.items()}},
        "falsos_positivos": [dict(ciclo=c["id"], defecto=x["id"], motivo=x.get("motivo_fp"))
                             for c in d["ciclos"] for x in c["defectos"] if x["veredicto"] == "FP"],
        "notas_humanas": [dict(ciclo=c["id"], defecto=x["id"], nota=x["nota_humana"])
                          for c in d["ciclos"] for x in c["defectos"] if x.get("nota_humana")],
    }
