"""Simulación Monte Carlo del caso de negocio del Agente Virtual de QA.

Cada corrida sortea un «mundo» posible con estas incertidumbres y lo simula 60 meses con el
modelo de `modelo.py`, con clientes enteros (altas Poisson y bajas binomiales):

| Variable                        | Distribución                                  | Calibración                                  |
|---------------------------------|-----------------------------------------------|----------------------------------------------|
| Ritmo de clientes nuevos        | normal truncada, media 1                      | P10 = 0.70 y P90 = 1.30 (escenarios del caso)|
| Bajas mensuales                 | lognormal                                     | P10 = 0.80 y P90 = 1.30 (escenarios del caso)|
| Costo variable                  | triangular 22 % – 25 % – 35 %                 | escenarios y sensibilidad del caso           |
| Precio cobrado frente a lista   | triangular 80 % – 100 % – 100 %               | descuentos de 0 a 20 %                       |
| Conversión de cada piloto       | beta(5, 5), media 50 %                        | supuesto explícito del equipo                |
| Aceptación de casos sin edición | beta(31, 1)                                   | 30 de 30 casos aceptados en tres ciclos      |

Un factor común de «ajuste producto-mercado» liga la conversión de los pilotos con el ritmo de
ventas (correlación 0.5) y, en sentido contrario, con las bajas (0.3). Así, un piloto que no
convierte también anticipa ventas más lentas, que es lo que justifica invertir por etapas.

Todo corre en segundos en una computadora normal y no llama a ninguna API.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy import stats

from .modelo import BASE, Supuestos, indicadores, simular

Z90 = stats.norm.ppf(0.90)


@dataclass(frozen=True)
class Incertidumbre:
    n: int = 10_000
    semilla: int = 20261026
    ventas_media: float = 1.0                            # 1 = el plan de clientes nuevos
    ventas_desv: float = 0.30 / Z90                      # P10/P90 = 0.70 / 1.30
    bajas_mu: float = float((np.log(0.8) + np.log(1.3)) / 2)
    bajas_sigma: float = float((np.log(1.3) - np.log(0.8)) / (2 * Z90))
    costo_variable: tuple = (0.22, 0.25, 0.35)            # triangular: mínimo, moda, máximo
    precio: tuple = (0.80, 1.00, 1.00)
    rho_ventas: float = 0.5
    rho_bajas: float = 0.3
    rho_pilotos: float = 0.5
    pilotos: int = 3
    pilotos_beta: tuple = (5.0, 5.0)
    aceptacion_beta: tuple = (31.0, 1.0)
    casos_por_piloto: int = 10
    umbral_aceptacion: float = 0.70
    umbrales_hitos: tuple = (100_000.0, 500_000.0, 1_200_000.0)   # ARR exigido en los meses 12, 24 y 36
    discreto: bool = True


def _triangular(rng, n, minimo, moda, maximo):
    """Triangular; si mínimo y máximo coinciden, el valor queda fijo (sirve para apagar una incertidumbre)."""
    if maximo <= minimo:
        return np.full(n, float(minimo))
    return rng.triangular(minimo, moda, maximo, n)


def sortear(inc: Incertidumbre, rng: np.random.Generator) -> dict:
    """Sortea los supuestos inciertos de cada corrida."""
    n = inc.n
    z = rng.standard_normal(n)                            # ajuste producto-mercado
    e = rng.standard_normal((3, n))
    mezcla = lambda rho, ruido: rho * z + np.sqrt(1 - rho ** 2) * ruido
    m_altas = np.clip(inc.ventas_media + inc.ventas_desv * mezcla(inc.rho_ventas, e[0]), 0.2, 2.5)
    m_bajas = np.exp(inc.bajas_mu + inc.bajas_sigma * -mezcla(inc.rho_bajas, e[1]))
    costo_var = _triangular(rng, n, *inc.costo_variable)
    precio = _triangular(rng, n, *inc.precio)
    p_piloto = stats.beta.ppf(stats.norm.cdf(mezcla(inc.rho_pilotos, e[2])), *inc.pilotos_beta)
    pilotos_pagan = rng.binomial(inc.pilotos, p_piloto)
    theta = rng.beta(*inc.aceptacion_beta, n)
    casos = inc.pilotos * inc.casos_por_piloto
    aceptados = rng.binomial(casos, theta)
    return dict(ajuste=z, m_altas=m_altas, m_bajas=m_bajas, costo_variable=costo_var, precio=precio,
                p_piloto=p_piloto, pilotos_pagan=pilotos_pagan, aceptacion=theta,
                aceptados=aceptados, casos_piloto=np.full(n, casos))


def correr(inc: Incertidumbre = Incertidumbre(), s: Supuestos = BASE) -> dict:
    """Corre la simulación completa y devuelve los sorteos, las series y los indicadores."""
    rng = np.random.default_rng(inc.semilla)
    x = sortear(inc, rng)
    sim = simular(s, inc.n, m_altas=x["m_altas"], m_bajas=x["m_bajas"], costo_variable=x["costo_variable"],
                  m_precio=x["precio"], discreto=inc.discreto, rng=rng)
    ind = indicadores(sim, s)
    hito1 = (x["pilotos_pagan"] >= 2) & (x["aceptados"] >= inc.umbral_aceptacion * x["casos_piloto"])
    hitos = np.column_stack([hito1,
                             ind["arr_m12"] >= inc.umbrales_hitos[0],
                             ind["arr_m24"] >= inc.umbrales_hitos[1],
                             ind["arr_m36"] >= inc.umbrales_hitos[2]])
    return dict(incertidumbre=inc, supuestos=s, sorteos=x, simulacion=sim, indicadores=ind, hitos=hitos)


# ---------------------------------------------------------------- análisis de resultados

def _pct(v, q):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return float(np.percentile(v, q)) if v.size else None


def _prob(mascara):
    return float(np.mean(mascara))


def _resumen_variable(v):
    return {"p5": _pct(v, 5), "p10": _pct(v, 10), "p50": _pct(v, 50), "p90": _pct(v, 90),
            "p95": _pct(v, 95), "media": float(np.nanmean(v))}


def resumen(res: dict) -> dict:
    """Probabilidades y percentiles principales."""
    ind, h = res["indicadores"], res["hitos"]
    recupera = ~np.isnan(ind["mes_recuperacion"])
    todos = h.all(axis=1)
    return {
        "corridas": int(h.shape[0]),
        "prob_hito": [_prob(h[:, k]) for k in range(4)],
        "prob_hito_condicional": [_prob(h[:, 0])] + [float(h[h[:, :k].all(axis=1), k].mean()) for k in range(1, 4)],
        "prob_todos_los_hitos": _prob(todos),
        "prob_recupera_60": _prob(recupera),
        "prob_van_con_vt_positivo": _prob(ind["van_con_vt"] > 0),
        "prob_van_sin_vt_positivo": _prob(ind["van_sin_vt"] > 0),
        "prob_equilibrio_36": _prob(ind["mes_equilibrio"] <= 36),
        "prob_necesidad_mayor_119m": _prob(ind["necesidad_maxima"] > 1.19e6),
        "necesidad_maxima": _resumen_variable(ind["necesidad_maxima"]),
        "mes_necesidad": _resumen_variable(ind["mes_necesidad"]),
        "mes_equilibrio": _resumen_variable(np.where(np.isnan(ind["mes_equilibrio"]), 61, ind["mes_equilibrio"])),
        "mes_recuperacion_si_recupera": _resumen_variable(ind["mes_recuperacion"][recupera]),
        "caja_m60": _resumen_variable(ind["caja_m60"]),
        "van_sin_vt": _resumen_variable(ind["van_sin_vt"]),
        "van_con_vt": _resumen_variable(ind["van_con_vt"]),
        "tir_con_vt": _resumen_variable(ind["tir_con_vt"]),
        "arr_m12": _resumen_variable(ind["arr_m12"]),
        "arr_m24": _resumen_variable(ind["arr_m24"]),
        "arr_m36": _resumen_variable(ind["arr_m36"]),
        "clientes_m36": _resumen_variable(ind["clientes_m36"]),
        "recupera_si_pasa_hito2": float(recupera[h[:, 1]].mean()),
        "recupera_si_falla_hito2": float(recupera[~h[:, 1]].mean()),
        "recupera_si_pasa_todos": float(recupera[todos].mean()) if todos.any() else None,
    }


def bandas(res: dict, serie: str = "caja") -> dict:
    """Percentiles mes a mes de una serie (para el gráfico de abanico)."""
    v = res["simulacion"][serie]
    return {f"p{q}": np.percentile(v, q, axis=0).round(0).tolist() for q in (5, 25, 50, 75, 95)}


def _evaluar_politica(res: dict, compuertas: list) -> dict:
    """Evalúa una regla de inversión: lista de (mes, aprobado) que se revisan en orden.

    Si una compuerta no se aprueba, el proyecto se detiene en ese mes y lo invertido hasta
    ahí es la pérdida. Sin compuertas, el proyecto sigue hasta el mes 60.
    """
    ind, sim, s = res["indicadores"], res["simulacion"], res["supuestos"]
    n = sim["caja"].shape[0]
    mes_parada = np.full(n, 60)
    for mes, aprobado in reversed(compuertas):
        mes_parada = np.where(~aprobado, mes, mes_parada)
    # la primera compuerta que falla manda: recorrer en orden
    mes_parada = np.full(n, 60)
    detenido = np.zeros(n, bool)
    for mes, aprobado in compuertas:
        nueva = ~detenido & ~aprobado
        mes_parada = np.where(nueva, mes, mes_parada)
        detenido |= nueva
    caja = sim["caja"]
    tasa_m = (1 + s.tasa_descuento) ** (1 / 12) - 1
    vp = np.cumsum(sim["resultado"] / (1 + tasa_m) ** np.arange(1, caja.shape[1] + 1), axis=1)
    idx = (np.arange(n), mes_parada - 1)
    van_con = np.where(detenido, vp[idx], ind["van_con_vt"])
    van_sin = np.where(detenido, vp[idx], ind["van_sin_vt"])
    perdida = np.where(detenido, -caja[idx], ind["necesidad_maxima"])     # capital expuesto
    bueno = ~np.isnan(ind["mes_recuperacion"])
    malo = ~bueno
    return {
        "prob_detenerse": _prob(detenido),
        "van_con_vt_esperado": float(van_con.mean()),
        "van_sin_vt_esperado": float(van_sin.mean()),
        "capital_expuesto_medio": float(perdida.mean()),
        "capital_expuesto_p90": _pct(perdida, 90),
        "perdida_media_mundos_malos": float(perdida[malo].mean()) if malo.any() else None,
        "malos_detenidos": float(detenido[malo].mean()) if malo.any() else None,
        "buenos_detenidos": float(detenido[bueno].mean()) if bueno.any() else None,
        "prob_detenerse_por_mes": {str(m): _prob(detenido & (mes_parada == m)) for m, _ in compuertas},
    }


def politicas(res: dict) -> list:
    """Compara reglas de inversión: todo de una vez, las etapas del caso y variantes."""
    ind, h, x = res["indicadores"], res["hitos"], res["sorteos"]
    inc = res["incertidumbre"]
    tecnico = x["aceptados"] >= inc.umbral_aceptacion * x["casos_piloto"]
    reglas = [
        ("Todo de una vez (sin compuertas)", []),
        ("Etapas del caso: hitos 1 a 4", [(6, h[:, 0]), (12, h[:, 1]), (24, h[:, 2]), (36, h[:, 3])]),
        ("Hito 1 con un piloto que pague, hitos 2 a 4", [(6, (x["pilotos_pagan"] >= 1) & tecnico), (12, h[:, 1]), (24, h[:, 2]), (36, h[:, 3])]),
        ("Solo los hitos de ARR (2 a 4)", [(12, h[:, 1]), (24, h[:, 2]), (36, h[:, 3])]),
        ("Solo el hito 3 (ARR del mes 24)", [(24, h[:, 2])]),
    ]
    return [dict(regla=nombre, **_evaluar_politica(res, compuertas)) for nombre, compuertas in reglas]


def hito_como_clasificador(res: dict) -> dict:
    """¿Qué tan bien anticipan los hitos 2 y 3 si el negocio recupera la inversión en 60 meses?"""
    ind = res["indicadores"]
    bueno = ~np.isnan(ind["mes_recuperacion"])
    salida = {}
    for nombre, arr, umbral, rejilla in (("hito2", ind["arr_m12"], 100_000, np.arange(40_000, 220_001, 5_000)),
                                         ("hito3", ind["arr_m24"], 500_000, np.arange(250_000, 800_001, 10_000))):
        def matriz(u):
            pasa = arr >= u
            vp, fp = int((pasa & bueno).sum()), int((pasa & ~bueno).sum())
            fn, vn = int((~pasa & bueno).sum()), int((~pasa & ~bueno).sum())
            sens = vp / max(vp + fn, 1); fpr = fp / max(fp + vn, 1)
            return dict(umbral=float(u), vp=vp, fp=fp, fn=fn, vn=vn, sensibilidad=sens,
                        especificidad=1 - fpr, precision=vp / max(vp + fp, 1), youden=sens - fpr)
        curva = [matriz(u) for u in rejilla]
        mejor = max(curva, key=lambda c: c["youden"])
        salida[nombre] = {"actual": matriz(umbral), "mejor_youden": mejor,
                          "curva": [{k: c[k] for k in ("umbral", "sensibilidad", "especificidad", "precision", "youden")} for c in curva]}
    return salida


def tornado(s: Supuestos = BASE, inc: Incertidumbre = Incertidumbre()) -> list:
    """Sensibilidad determinista: cada variable en su P10 y su P90, las demás en el plan."""
    rng = np.random.default_rng(7)
    cv = _triangular(rng, 200_000, *inc.costo_variable)
    pr = _triangular(rng, 200_000, *inc.precio)
    variables = [
        ("Ritmo de clientes nuevos", "m_altas", 0.70, 1.30),
        ("Precio cobrado", "m_precio", float(np.percentile(pr, 10)), float(np.percentile(pr, 90))),
        ("Bajas de clientes", "m_bajas", 1.30, 0.80),
        ("Costo variable de IA", "costo_variable", float(np.percentile(cv, 90)), float(np.percentile(cv, 10))),
    ]
    base = indicadores(simular(s, 1), s, tir=False)
    filas = []
    for etiqueta, clave, malo, bueno in variables:
        r_malo = indicadores(simular(s, 1, **{clave: malo}), s, tir=False)
        r_bueno = indicadores(simular(s, 1, **{clave: bueno}), s, tir=False)
        filas.append(dict(variable=etiqueta, valor_desfavorable=malo, valor_favorable=bueno,
                          van_desfavorable=float(r_malo["van_con_vt"][0]), van_favorable=float(r_bueno["van_con_vt"][0]),
                          necesidad_desfavorable=float(r_malo["necesidad_maxima"][0]),
                          necesidad_favorable=float(r_bueno["necesidad_maxima"][0])))
    for f in filas:
        f["rango_van"] = f["van_favorable"] - f["van_desfavorable"]
    filas.sort(key=lambda f: -f["rango_van"])
    return {"van_base": float(base["van_con_vt"][0]), "necesidad_base": float(base["necesidad_maxima"][0]), "filas": filas}


def correlaciones(res: dict) -> list:
    """Correlación de rangos (Spearman) entre cada supuesto y los resultados."""
    x, ind = res["sorteos"], res["indicadores"]
    nombres = {"m_altas": "Ritmo de clientes nuevos", "precio": "Precio cobrado", "m_bajas": "Bajas de clientes",
               "costo_variable": "Costo variable de IA", "p_piloto": "Conversión de pilotos"}
    filas = []
    for k, etiqueta in nombres.items():
        filas.append(dict(variable=etiqueta,
                          con_van=float(stats.spearmanr(x[k], ind["van_con_vt"]).statistic),
                          con_necesidad=float(stats.spearmanr(x[k], ind["necesidad_maxima"]).statistic)))
    filas.sort(key=lambda f: -abs(f["con_van"]))
    return filas


def riesgos(res: dict) -> list:
    """Evaluación estocástica de la tabla de riesgos del caso: probabilidad e impacto de cada evento."""
    x, ind, h, sim = res["sorteos"], res["indicadores"], res["hitos"], res["simulacion"]
    recupera = ~np.isnan(ind["mes_recuperacion"])
    eventos = [
        ("Ventas más lentas que el plan (20% o más)", x["m_altas"] < 0.8),
        ("Ningún cliente Empresarial firmado al mes 12", sim["empresariales_firmados_m12"] == 0),
        ("Menos de dos pilotos pasan a pago", x["pilotos_pagan"] < 2),
        ("Menos de 70% de casos aceptados sin edición", x["aceptados"] < 0.7 * x["casos_piloto"]),
        ("Costo variable sobre 30% de la suscripción", x["costo_variable"] > 0.30),
        ("Bajas 30% o más sobre el plan", x["m_bajas"] > 1.3),
        ("Descuento promedio de 10% o más", x["precio"] < 0.90),
    ]
    filas = []
    for nombre, ev in eventos:
        filas.append(dict(
            riesgo=nombre, probabilidad=_prob(ev),
            recupera_si_ocurre=float(recupera[ev].mean()) if ev.any() else None,
            recupera_si_no=float(recupera[~ev].mean()) if (~ev).any() else None,
            hito2_si_ocurre=float(h[ev, 1].mean()) if ev.any() else None,
            hito2_si_no=float(h[~ev, 1].mean()) if (~ev).any() else None,
            necesidad_p50_si_ocurre=_pct(ind["necesidad_maxima"][ev], 50),
            necesidad_p50_si_no=_pct(ind["necesidad_maxima"][~ev], 50),
        ))
    return filas


def convergencia(res: dict) -> list:
    """Estabilidad de las estimaciones a medida que crece el número de corridas."""
    ind = res["indicadores"]
    recupera = ~np.isnan(ind["mes_recuperacion"])
    van = ind["van_con_vt"]
    filas = []
    for n in (250, 500, 1_000, 2_000, 5_000, len(van)):
        p = recupera[:n].mean()
        filas.append(dict(n=int(n), prob_recupera=float(p), ic95_prob=float(1.96 * np.sqrt(p * (1 - p) / n)),
                          van_media=float(van[:n].mean()), ic95_van=float(1.96 * van[:n].std(ddof=1) / np.sqrt(n))))
    return filas


def histograma(v, bins=40) -> dict:
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    cuentas, bordes = np.histogram(v, bins=bins)
    return {"cuentas": cuentas.tolist(), "bordes": bordes.round(2).tolist()}


def analizar(res: dict) -> dict:
    """Todo el análisis en un diccionario serializable (lo usan el informe, el deck y el tablero)."""
    return {
        "configuracion": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(res["incertidumbre"]).items()},
        "resumen": resumen(res),
        "bandas_caja": bandas(res, "caja"),
        "bandas_arr": bandas(res, "arr"),
        "histogramas": {
            "necesidad_maxima": histograma(res["indicadores"]["necesidad_maxima"]),
            "van_con_vt": histograma(res["indicadores"]["van_con_vt"]),
            "mes_equilibrio": histograma(res["indicadores"]["mes_equilibrio"], bins=np.arange(6.5, 61.5, 1)),
        },
        "politicas": politicas(res),
        "clasificador": hito_como_clasificador(res),
        "tornado": tornado(res["supuestos"], res["incertidumbre"]),
        "correlaciones": correlaciones(res),
        "riesgos": riesgos(res),
        "convergencia": convergencia(res),
    }


def descomposicion(s: Supuestos = BASE, n: int = 10_000, semilla: int = 20261026) -> list:
    """Explica por qué la mediana del Monte Carlo difiere del escenario base: agrega una
    incertidumbre a la vez, desde el modelo determinista hasta la simulación completa."""
    det = indicadores(simular(s, 1), s, tir=False)
    filas = [dict(paso="Escenario base del caso (determinista)", prob_recupera=1.0 if not np.isnan(det["mes_recuperacion"][0]) else 0.0,
                  necesidad_p50=float(det["necesidad_maxima"][0]), van_con_vt_p50=float(det["van_con_vt"][0]))]
    apagado = dict(ventas_desv=0.0, bajas_mu=0.0, bajas_sigma=0.0, costo_variable=(0.25, 0.25, 0.25),
                   precio=(1.0, 1.0, 1.0), rho_ventas=0.0, rho_bajas=0.0, rho_pilotos=0.0)
    pasos = [
        ("Clientes enteros (altas y bajas al azar)", dict()),
        ("+ ritmo de ventas incierto", dict(ventas_desv=Incertidumbre.ventas_desv)),
        ("+ bajas inciertas", dict(bajas_mu=Incertidumbre.bajas_mu, bajas_sigma=Incertidumbre.bajas_sigma)),
        ("+ costo variable incierto", dict(costo_variable=Incertidumbre.costo_variable)),
        ("+ descuentos de precio (0 a 20%)", dict(precio=Incertidumbre.precio)),
        ("+ factor común de ajuste producto-mercado", dict(rho_ventas=0.5, rho_bajas=0.3, rho_pilotos=0.5)),
    ]
    acumulado = dict(apagado)
    for nombre, cambios in pasos:
        acumulado.update(cambios)
        inc = Incertidumbre(n=n, semilla=semilla, **acumulado)
        r = correr(inc, s)
        ind = r["indicadores"]
        filas.append(dict(paso=nombre, prob_recupera=_prob(~np.isnan(ind["mes_recuperacion"])),
                          necesidad_p50=_pct(ind["necesidad_maxima"], 50), van_con_vt_p50=_pct(ind["van_con_vt"], 50)))
    return filas
