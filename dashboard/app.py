"""Cuadro de mando del Agente Virtual de QA (Streamlit).

Cinco vistas para la junta directiva y el equipo:
  1. Junta directiva: la decisión y las cifras que la sostienen.
  2. Monitoreo del agente: métricas de los ciclos reales y la regresión nocturna (se actualiza sola).
  3. Simulación Monte Carlo: cambie un supuesto y vea cómo se mueve el riesgo.
  4. Valor para el cliente: cuándo se paga solo el plan.
  5. Gobernanza: decisiones humanas, incidentes, datos que salen del perímetro y sesgos.

Correr desde la raíz del repositorio:  streamlit run dashboard/app.py
Las cifras fijas salen de simulacion/resultados/resultados.json (python -m simulacion.generar).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from simulacion import cliente as mod_cliente  # noqa: E402
from simulacion import montecarlo  # noqa: E402
from simulacion.montecarlo import Incertidumbre  # noqa: E402

st.set_page_config(page_title="Agente Virtual de QA · Cuadro de mando", page_icon="🧪", layout="wide")

# ------------------------------------------------------------------ estilo (paleta validada)
AZUL, NARANJA, AQUA, ROJO = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
AZUL_100, AZUL_250, AZUL_550 = "#cde2fb", "#86b6ef", "#1c5cab"
TINTA, SECUNDARIA, TENUE = "#0b0b0b", "#52514e", "#898781"
REJILLA, EJE, SUPERFICIE, GRIS = "#e1e0d9", "#c3c2b7", "#fcfcfb", "#e9e8e3"
FUENTE = "system-ui, -apple-system, 'Segoe UI', sans-serif"

st.markdown("""
<style>
  .block-container {padding-top: 1.6rem; max-width: 1280px;}
  h1, h2, h3 {letter-spacing: -0.01em;}
  [data-testid="stMetricValue"] {font-size: 1.75rem;}
  [data-testid="stMetricLabel"] p {color: #52514e;}
  .nota {color: #52514e; font-size: 0.9rem;}
  .decision {border-left: 4px solid #2a78d6; background: #f3f7fd; padding: 0.9rem 1.1rem; border-radius: 6px; margin-bottom: 0.6rem;}
</style>
""", unsafe_allow_html=True)


def estilo(fig: go.Figure, alto: int = 360, eje_y: str | None = None, eje_x: str | None = None, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        height=alto, margin=dict(l=8, r=12, t=36 if leyenda else 16, b=8), paper_bgcolor=SUPERFICIE, plot_bgcolor=SUPERFICIE,
        font=dict(family=FUENTE, color=TINTA, size=13), showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=SECUNDARIA)),
        hoverlabel=dict(bgcolor="white", font=dict(family=FUENTE, color=TINTA)), separators=".,",
    )
    fig.update_xaxes(gridcolor=REJILLA, linecolor=EJE, tickfont=dict(color=TENUE), title=eje_x, zeroline=False)
    fig.update_yaxes(gridcolor=REJILLA, linecolor=EJE, tickfont=dict(color=TENUE), title=eje_y, zeroline=False)
    return fig


def usd(x: float, decimales: int = 0) -> str:
    if x is None:
        return "—"
    if abs(x) >= 1e6:
        return f"USD {x / 1e6:,.2f} M"
    return f"USD {x:,.{decimales}f}"


def usd_m(x: float) -> str:
    """Montos de tablas y comparaciones, siempre en millones para que se lean en la misma unidad."""
    return "—" if x is None else f"USD {x / 1e6:,.2f} M"


def pct(x: float, decimales: int = 0) -> str:
    return "—" if x is None else f"{100 * x:.{decimales}f}%"


def ic(d: dict) -> str:
    return f"{pct(d['ic_bajo'])} a {pct(d['ic_alto'])}"


@st.cache_data
def resultados() -> dict:
    return json.loads((RAIZ / "simulacion" / "resultados" / "resultados.json").read_text(encoding="utf-8"))


R = resultados()
MC = R["montecarlo"]
AG = R["agente"]

st.title("Agente Virtual de QA · Cuadro de mando")
st.markdown(f"<span class='nota'>Grupo 2 · Maestría en Ciencias de Datos e IA · UASD · "
            f"Simulación Monte Carlo de {MC['resumen']['corridas']:,} corridas · tres ciclos reales del agente · "
            f"resultados generados el {R['generado']}</span>", unsafe_allow_html=True)

tab_junta, tab_agente, tab_sim, tab_cliente, tab_gob = st.tabs(
    ["Junta directiva", "Monitoreo del agente", "Simulación Monte Carlo", "Valor para el cliente", "Gobernanza"])


# ------------------------------------------------------------------ gráficos reutilizables
def grafico_abanico(bandas: dict, base: list | None, titulo_y: str = "Caja acumulada (millones de USD)") -> go.Figure:
    meses = list(range(1, len(bandas["p50"]) + 1))
    m = lambda v: [x / 1e6 for x in v]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=meses, y=m(bandas["p95"]), line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=meses, y=m(bandas["p5"]), fill="tonexty", fillcolor=AZUL_100, line=dict(width=0),
                             name="90% de los casos (P5 a P95)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=meses, y=m(bandas["p75"]), line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=meses, y=m(bandas["p25"]), fill="tonexty", fillcolor=AZUL_250, line=dict(width=0),
                             name="50% central (P25 a P75)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=meses, y=m(bandas["p50"]), line=dict(color=AZUL_550, width=2), name="Mediana del Monte Carlo",
                             hovertemplate="Mes %{x}<br>Mediana: USD %{y:.2f} M<extra></extra>"))
    if base:
        fig.add_trace(go.Scatter(x=meses, y=m(base), line=dict(color=NARANJA, width=2), name="Escenario base del caso",
                                 hovertemplate="Mes %{x}<br>Base: USD %{y:.2f} M<extra></extra>"))
    fig.add_hline(y=0, line=dict(color=EJE, width=1))
    for mes, etiqueta in ((6, "Hito 1"), (12, "Hito 2"), (24, "Hito 3"), (36, "Hito 4")):
        fig.add_vline(x=mes, line=dict(color=REJILLA, width=1))
        fig.add_annotation(x=mes, y=1.0, yref="paper", text=etiqueta, showarrow=False, yanchor="bottom",
                           font=dict(color=TENUE, size=11))
    fig.add_hline(y=-1.19, line=dict(color=TENUE, width=1))
    fig.add_annotation(x=1, y=-1.19, text="Financiamiento con reserva: USD 1.19 M", showarrow=False, xanchor="left",
                       yanchor="top", font=dict(color=SECUNDARIA, size=11))
    estilo(fig, 460, titulo_y, "Mes")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0), margin=dict(t=28, b=8))
    return fig


def barras_hitos(p_hito: list, p_cond: list) -> go.Figure:
    etiquetas = ["Hito 1<br>mes 6", "Hito 2<br>mes 12", "Hito 3<br>mes 24", "Hito 4<br>mes 36"]
    criterios = ["Dos de tres pilotos pagan y 70% de casos sin edición", "ARR de USD 100 mil", "ARR de USD 500 mil", "ARR de USD 1.2 millones"]
    fig = go.Figure(go.Bar(x=etiquetas, y=p_hito, marker_color=AZUL, width=0.45,
                           text=[pct(p) for p in p_hito], textposition="outside", textfont=dict(color=TINTA),
                           customdata=list(zip(p_cond, criterios)),
                           hovertemplate="%{customdata[1]}<br>Probabilidad: %{y:.1%}<br>Si se cumplieron los anteriores: %{customdata[0]:.1%}<extra></extra>"))
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
    fig.update_xaxes(tickangle=0)
    return estilo(fig, 320, "Probabilidad de cumplirlo", leyenda=False)


def histograma(h: dict, marcas: list, titulo_x: str, escala: float = 1e6, formato: str = "USD %{x:.2f} M") -> go.Figure:
    bordes = np.array(h["bordes"]) / escala
    centros = (bordes[:-1] + bordes[1:]) / 2
    total = sum(h["cuentas"])
    fig = go.Figure(go.Bar(x=centros, y=np.array(h["cuentas"]) / total, width=(bordes[1] - bordes[0]) * 0.92,
                           marker_color=AZUL, hovertemplate=f"{formato}<br>%{{y:.1%}} de las corridas<extra></extra>"))
    for i, (valor, texto) in enumerate(marcas):
        fig.add_vline(x=valor / escala, line=dict(color=TINTA if "P50" in texto else TENUE, width=1))
        fig.add_annotation(x=valor / escala, y=1.0 - 0.09 * i, yref="paper", text=texto, showarrow=False, yanchor="bottom",
                           xanchor="left", xshift=3, font=dict(size=11, color=SECUNDARIA), bgcolor=SUPERFICIE)
    fig.update_yaxes(tickformat=".0%")
    return estilo(fig, 300, "Corridas", titulo_x, leyenda=False)


def tornado(t: dict) -> go.Figure:
    # Cada barra va del VAN con el valor desfavorable al VAN con el favorable (P10 o P90 según la variable).
    # El tramo bajo el escenario base va en naranja y el tramo sobre él, en azul: en el precio, hasta el
    # valor favorable queda bajo la base, porque la base supone que no hay descuentos.
    filas = t["filas"][::-1]
    base = t["van_base"] / 1e6
    fig = go.Figure()
    nombres = [f["variable"] for f in filas]
    bajo_ini, bajo_largo, sobre_ini, sobre_largo, datos = [], [], [], [], []
    for f in filas:
        lo, hi = f["van_desfavorable"] / 1e6, f["van_favorable"] / 1e6
        a, z = min(lo, hi), max(lo, hi)
        bajo_ini.append(a); bajo_largo.append(max(0.0, min(z, base) - a))
        sobre_ini.append(max(a, base)); sobre_largo.append(max(0.0, z - max(a, base)))
        datos.append([f["valor_desfavorable"], lo, f["valor_favorable"], hi])
    ayuda = ("%{y}<br>Desfavorable (%{customdata[0]:.2f}): USD %{customdata[1]:.2f} M"
             "<br>Favorable (%{customdata[2]:.2f}): USD %{customdata[3]:.2f} M<extra></extra>")
    fig.add_trace(go.Bar(y=nombres, x=bajo_largo, base=bajo_ini, orientation="h", marker_color=NARANJA, width=0.5,
                         name="Por debajo del escenario base", customdata=datos, hovertemplate=ayuda))
    fig.add_trace(go.Bar(y=nombres, x=sobre_largo, base=sobre_ini, orientation="h", marker_color=AZUL, width=0.5,
                         name="Por encima del escenario base", customdata=datos, hovertemplate=ayuda))
    fig.add_vline(x=base, line=dict(color=TINTA, width=1))
    fig.add_annotation(x=base, y=1.0, yref="paper", text=f"Base: USD {base:.2f} M", showarrow=False, yanchor="bottom",
                       font=dict(size=11, color=SECUNDARIA))
    fig.update_layout(barmode="overlay")
    estilo(fig, 320, None, "VAN con valor terminal (millones de USD)")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="left", x=0))
    return fig


def tabla_politicas(politicas: list) -> pd.DataFrame:
    return pd.DataFrame([{
        "Regla de inversión": p["regla"],
        "VAN esperado con valor terminal": usd_m(p["van_con_vt_esperado"]),
        "VAN esperado a 5 años": usd_m(p["van_sin_vt_esperado"]),
        "Capital expuesto promedio": usd_m(p["capital_expuesto_medio"]),
        "Capital expuesto P90": usd_m(p["capital_expuesto_p90"]),
        "Supera los USD 1.19 M": pct(p["prob_capital_mayor_119m"]),
        "Negocios buenos detenidos": pct(p["buenos_detenidos"]),
        "Negocios malos detenidos": pct(p["malos_detenidos"]),
    } for p in politicas])


# ================================================================== 1. JUNTA DIRECTIVA
with tab_junta:
    r = MC["resumen"]
    etapas = {p["regla"]: p for p in MC["politicas"]}
    caso = etapas["Etapas del caso: hitos 1 a 4"]
    todo = etapas["Todo de una vez (sin compuertas)"]
    reco = etapas["Recomendada: hito 1 con un piloto que pague y hito 3"]
    st.markdown(
        f"<div class='decision'><b>Decisión que se pide:</b> aprobar solo la etapa 1 (USD 188,400, seis meses) y seguir con dos "
        f"compuertas: un piloto pagado en el mes 6 y el ARR del mes 24. Con esa regla el VAN esperado es "
        f"USD {reco['van_con_vt_esperado'] / 1e6:.2f} M y el financiamiento de USD 1.19 M alcanza en "
        f"{pct(1 - reco['prob_capital_mayor_119m'])} de los futuros. Si se compromete todo de una vez, "
        f"no alcanza en {pct(todo['prob_capital_mayor_119m'])}.</div>",
        unsafe_allow_html=True)
    c = st.columns(5)
    c[0].metric("Cumplir el hito 1 (mes 6)", pct(r["prob_hito"][0]), help="Dos de tres pilotos pasan a pago y 70% de los casos se acepta sin edición.")
    c[1].metric("Recupera la inversión en 60 meses", pct(r["prob_recupera_60"]), help="Fracción de las corridas con caja acumulada positiva al mes 60.")
    c[2].metric("Necesidad de caja (mediana)", usd(r["necesidad_maxima"]["p50"]), help=f"P90: {usd(r['necesidad_maxima']['p90'])}")
    c[3].metric("VAN con valor terminal > 0", pct(r["prob_van_con_vt_positivo"]), help="Tasa de descuento de 20% anual; perpetuidad con 3% de crecimiento.")
    c[4].metric("Precisión del agente", pct(AG["agregado"]["precision"]["valor"]),
                help=f"15 de 18 defectos reportados son reales. Intervalo creíble 95%: {ic(AG['agregado']['precision'])}.")

    izq, der = st.columns([3, 2])
    with izq:
        st.subheader("Caja acumulada: 10,000 futuros posibles")
        st.plotly_chart(grafico_abanico(MC["bandas_caja"], R["serie_base"]["caja"]), width="stretch", key="grafico_1")
        st.caption(f"El escenario base recupera la inversión justo en el mes 60, con USD 88 mil de margen. En la mitad de "
                   f"las corridas la necesidad de caja supera {usd(r['necesidad_maxima']['p50'])}; en el 10% más difícil, "
                   f"{usd(r['necesidad_maxima']['p90'])}.")
    with der:
        st.subheader("Probabilidad de cada hito")
        st.plotly_chart(barras_hitos(r["prob_hito"], r["prob_hito_condicional"]), width="stretch", key="grafico_2")
        st.caption(f"Los cuatro hitos juntos: {pct(r['prob_todos_los_hitos'])}. Si se cumplen todos, la inversión se "
                   f"recupera en 60 meses en {pct(r['recupera_si_pasa_todos'])} de los casos.")

    st.subheader("¿Conviene invertir por etapas?")
    st.dataframe(tabla_politicas(MC["politicas"]), hide_index=True, width="stretch")
    st.markdown(
        f"- **Negocio bueno** = recupera la inversión en 60 meses si se invierte todo; **malo** = no la recupera "
        f"(aunque {pct(r['prob_van_con_vt_positivo_si_no_recupera'])} de esos aún tiene VAN con valor terminal positivo).\n"
        f"- **Las etapas protegen el capital:** en los negocios malos, el capital expuesto promedio baja de "
        f"{usd_m(todo['perdida_media_mundos_malos'])} a {usd_m(reco['perdida_media_mundos_malos'])} con la regla recomendada.\n"
        f"- **El hito 1 del caso es muy estricto:** las etapas del caso detienen {pct(caso['buenos_detenidos'])} de los negocios buenos, "
        f"{pct(caso['buenos_detenidos_por_mes']['6'])} ya en el mes 6. La regla recomendada detiene {pct(reco['buenos_detenidos'])} "
        f"y sube el VAN esperado de {usd_m(caso['van_con_vt_esperado'])} a {usd_m(reco['van_con_vt_esperado'])}.\n"
        f"- **El hito 3 es la mejor señal:** el ARR del mes 24 anticipa {pct(MC['clasificador']['hito3']['actual']['sensibilidad'])} "
        f"de los negocios buenos y descarta {pct(MC['clasificador']['hito3']['actual']['especificidad'])} de los malos; el hito 2, "
        f"{pct(MC['clasificador']['hito2']['actual']['sensibilidad'])} y {pct(MC['clasificador']['hito2']['actual']['especificidad'])}, "
        f"por eso queda como alerta y no como compuerta.")
    with st.expander("Por qué la mediana del Monte Carlo queda por debajo del escenario base"):
        st.dataframe(pd.DataFrame([{"Paso": f["paso"], "Recupera en 60 meses": pct(f["prob_recupera"]),
                                    "Necesidad de caja (mediana)": usd(f["necesidad_p50"]),
                                    "VAN con valor terminal (mediana)": usd(f["van_con_vt_p50"])} for f in MC["descomposicion"]]),
                     hide_index=True, width="stretch")
        st.caption("Cada fila agrega una incertidumbre a la anterior. El solo azar de qué clientes firman cada mes ya baja la "
                   "probabilidad de recuperar en 60 meses a 58%, porque el escenario base lo logra con un margen mínimo; los "
                   "descuentos de precio son el supuesto que más la baja.")


# ================================================================== 2. MONITOREO DEL AGENTE
with tab_agente:
    ag = AG["agregado"]
    mc = R["mcmc"]
    c = st.columns(6)
    c[0].metric("Precisión", pct(ag["precision"]["valor"]), help=f"Intervalo creíble 95%: {ic(ag['precision'])}")
    c[1].metric("Cobertura por ciclo", pct(ag["recall_por_ciclo"]["valor"]), help=f"Intervalo creíble 95%: {ic(ag['recall_por_ciclo'])}")
    c[2].metric("Cobertura con 3 ciclos", pct(mc["cobertura_k_ciclos"]["3"]["media"]),
                help=f"Intervalo creíble 95%: {ic(mc['cobertura_k_ciclos']['3'])}")
    c[3].metric("Pruebas al primer intento", pct(ag["pruebas_primer_intento"]["valor"]), help=ic(ag["pruebas_primer_intento"]))
    c[4].metric("Plan aceptado sin editar", pct(ag["aceptacion_plan"]["valor"]), help="Meta del hito 1: 70%. " + ic(ag["aceptacion_plan"]))
    c[5].metric("Costo por ciclo (tope)", usd(AG["costo"]["tope_por_ciclo_usd"], 2),
                help="Consola de Anthropic al 22-10-2026: incluye un ciclo completo y las pruebas de desarrollo.")

    izq, der = st.columns(2)
    with izq:
        st.subheader("Precisión y cobertura por ciclo")
        fig = go.Figure()
        for serie, clave, color, desplaza in (("Precisión", "precision", AZUL, -0.08), ("Cobertura (recall)", "recall_funcional", NARANJA, 0.08)):
            v = [x[clave] for x in AG["por_ciclo"]]
            fig.add_trace(go.Scatter(
                x=[i + desplaza for i in range(len(v))], y=[d["valor"] for d in v], mode="markers", name=serie,
                marker=dict(color=color, size=11, line=dict(color=SUPERFICIE, width=2)),
                error_y=dict(type="data", symmetric=False, array=[d["ic_alto"] - d["valor"] for d in v],
                             arrayminus=[d["valor"] - d["ic_bajo"] for d in v], color=color, thickness=2, width=0),
                customdata=[[d["exitos"], d["total"], d["ic_bajo"], d["ic_alto"]] for d in v],
                hovertemplate=serie + ": %{y:.0%} (%{customdata[0]} de %{customdata[1]})<br>IC 95%: %{customdata[2]:.0%} a %{customdata[3]:.0%}<extra></extra>"))
        fig.update_xaxes(tickvals=list(range(len(AG["por_ciclo"]))),
                         ticktext=[f"Ciclo {x['ciclo']} · {x['fecha']}" for x in AG["por_ciclo"]])
        fig.update_yaxes(range=[0, 1.02], tickformat=".0%")
        fig.update_xaxes(range=[-0.5, len(AG["por_ciclo"]) - 0.5])
        st.plotly_chart(estilo(fig, 340), width="stretch", key="grafico_3")
        st.caption("Cada punto lleva su intervalo creíble de 95% (prior uniforme). Con 4 a 8 defectos por ciclo, la incertidumbre es grande: "
                   "por eso el informe no da un solo número.")
    with der:
        st.subheader("Cobertura si se corre varias veces")
        k = [int(x) for x in mc["cobertura_k_ciclos"]]
        v = [mc["cobertura_k_ciclos"][str(x)] for x in k]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=k + k[::-1], y=[d["ic_alto"] for d in v] + [d["ic_bajo"] for d in v][::-1], fill="toself",
                                 fillcolor=AZUL_100, line=dict(width=0), mode="lines", name="Intervalo creíble 95%", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=k, y=[d["media"] for d in v], mode="lines+markers", line=dict(color=AZUL, width=2),
                                 marker=dict(size=9, line=dict(color=SUPERFICIE, width=2)), name="Cobertura esperada",
                                 hovertemplate="%{x} ciclos: %{y:.0%}<extra></extra>"))
        fig.update_xaxes(dtick=1, title="Ciclos independientes")
        fig.update_yaxes(range=[0, 1], tickformat=".0%")
        st.plotly_chart(estilo(fig, 340, "Defectos conocidos encontrados"), width="stretch", key="grafico_4")
        d = mc["diagnostico"]
        st.caption(f"Modelo jerárquico estimado con MCMC (PyMC, NUTS): {d['cadenas']} cadenas × {d['muestras_por_cadena']:,} muestras, "
                   f"R-hat máximo {d['r_hat_max']:.3f}, ESS mínimo {d['ess_bulk_min']:,.0f}, {d['divergencias']} divergencias.")

    st.subheader("Qué defectos encontró cada ciclo")
    ids = AG["matriz"]["defectos"]
    valores = np.array(AG["matriz"]["valores"])
    fig = go.Figure(go.Heatmap(
        z=valores.T, x=[f"#{i}" if not i.startswith("X") else i for i in ids], y=[f"Ciclo {c}" for c in AG["matriz"]["ciclos"]],
        colorscale=[[0, GRIS], [1, AZUL]], showscale=False, xgap=2, ygap=2,
        hovertemplate="%{y} · defecto %{x}: %{z}<extra>1 = encontrado</extra>"))
    fig.update_xaxes(type="category", tickangle=0)
    fig.update_yaxes(type="category")
    st.plotly_chart(estilo(fig, 200, leyenda=False), width="stretch", key="grafico_5")
    st.caption("Azul: el ciclo lo reportó. #n es el número del defecto en la lista oficial de Testsmith; X1 a X3 se verificaron en el código. "
               f"{int((valores.max(axis=1) == 0).sum())} de {len(ids)} defectos funcionales del alcance no aparecieron en ningún ciclo: "
               "repetir el agente no basta, hay que cambiar qué casos diseña.")

    st.subheader("Detalle por ciclo")
    st.dataframe(pd.DataFrame([{
        "Ciclo": f"{x['ciclo']} · {x['fecha']}", "Estado": x["estado"], "Defectos reportados": x["defectos_reportados"],
        "Reales": x["verdaderos"], "Falsos positivos": x["falsos_positivos"],
        "Precisión": f"{pct(x['precision']['valor'])} ({ic(x['precision'])})",
        "Cobertura": f"{pct(x['recall_funcional']['valor'])} ({ic(x['recall_funcional'])})",
        "F1": f"{x['f1']['valor']:.2f}", "Pruebas al primer intento": f"{x['pruebas_primer_intento']['exitos']} de {x['casos']}",
        "Ejecución de Playwright": f"{x['segundos_ejecucion']:.0f} s", "Revisión humana del plan": f"{x['revision_plan_seg']} s",
    } for x in AG["por_ciclo"]]), hide_index=True, width="stretch")

    @st.fragment(run_every="60s")
    def regresion_nocturna():
        st.subheader("Regresión nocturna: las pruebas del agente corren sin el agente")
        archivos = sorted((RAIZ / "metricas" / "regresion").glob("*.json"))
        filas = []
        for a in archivos:
            try:
                filas.append(json.loads(a.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        if not filas:
            st.info("Todavía no hay corridas nocturnas. El flujo de GitHub Actions (.github/workflows/regresion-nocturna.yml) "
                    "deja aquí un resumen cada noche.")
            return
        df = pd.DataFrame(filas).sort_values("fecha")
        df["dia"] = pd.to_datetime(df["fecha"], utc=True).dt.strftime("%d-%m-%Y")
        ultima = df.iloc[-1]
        c = st.columns(4)
        c[0].metric("Última corrida", str(ultima["fecha"])[:16].replace("T", " "))
        c[1].metric("Pasaron / fallaron", f"{int(ultima['pasaron'])} / {int(ultima['fallaron'])}")
        c[2].metric("Duración", f"{ultima['segundos']:.0f} s")
        c[3].metric("Costo de IA", "USD 0", help="Las pruebas son código de Playwright: no llaman al modelo.")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["dia"], y=df["pasaron"], name="Pasaron", marker_color=AZUL))
        fig.add_trace(go.Bar(x=df["dia"], y=df["fallaron"], name="Fallaron (defectos conocidos)", marker_color=NARANJA))
        fig.update_layout(barmode="stack", bargap=0.55)
        fig.update_xaxes(type="category")
        st.plotly_chart(estilo(fig, 260, "Pruebas"), width="stretch", key="grafico_6")
        estables = df["fallaron"].nunique() == 1
        st.caption(f"{len(df)} {'corrida registrada' if len(df) == 1 else 'corridas registradas'}. "
                   + ("El resultado se repite en todas: las pruebas son estables (sin falsos fallos intermitentes)." if estables else
                      "El número de fallos cambió entre corridas: revisar si hay pruebas inestables o si la aplicación cambió."))

    regresion_nocturna()

    st.subheader("Señales de alerta")
    alertas = [
        ("Casos aceptados sin edición", "≥ 70% (hito 1)", ag["aceptacion_plan"]["valor"], ag["aceptacion_plan"]["valor"] >= 0.70),
        ("Precisión de los defectos", "≥ 80%", ag["precision"]["valor"], ag["precision"]["valor"] >= 0.80),
        ("Cobertura de defectos conocidos por ciclo", "≥ 50% (meta propia)", ag["recall_por_ciclo"]["valor"], ag["recall_por_ciclo"]["valor"] >= 0.50),
        ("Decisiones humanas correctas", "≥ 90%", ag["decisiones_humanas_correctas"]["valor"], ag["decisiones_humanas_correctas"]["valor"] >= 0.90),
    ]
    st.dataframe(pd.DataFrame([{"Señal": a, "Umbral": u, "Valor": pct(v), "Estado": "✅ En rango" if ok else "⚠️ Revisar"}
                               for a, u, v, ok in alertas]), hide_index=True, width="stretch")


# ================================================================== 3. SIMULACIÓN MONTE CARLO
@st.cache_data(show_spinner=False, max_entries=20)
def simular(n, semilla, ventas_media, ventas_banda, bajas_p90, cv, descuento, conversion, rho):
    z90 = stats.norm.ppf(0.90)
    inc = Incertidumbre(
        n=n, semilla=semilla, ventas_media=ventas_media, ventas_desv=ventas_banda / z90,
        bajas_mu=float((np.log(0.8) + np.log(bajas_p90)) / 2), bajas_sigma=float((np.log(bajas_p90) - np.log(0.8)) / (2 * z90)),
        costo_variable=tuple(cv), precio=(1 - descuento, 1.0, 1.0),
        pilotos_beta=(10 * conversion, 10 * (1 - conversion)), rho_ventas=rho, rho_bajas=0.6 * rho, rho_pilotos=rho)
    res = montecarlo.correr(inc)
    a = montecarlo.analizar(res)
    a["csv"] = pd.DataFrame({
        "ritmo_ventas": res["sorteos"]["m_altas"], "bajas": res["sorteos"]["m_bajas"], "costo_variable": res["sorteos"]["costo_variable"],
        "precio": res["sorteos"]["precio"], "pilotos_pagan": res["sorteos"]["pilotos_pagan"],
        "necesidad_maxima": res["indicadores"]["necesidad_maxima"], "caja_m60": res["indicadores"]["caja_m60"],
        "van_con_vt": res["indicadores"]["van_con_vt"], "hito1": res["hitos"][:, 0], "hito2": res["hitos"][:, 1],
        "hito3": res["hitos"][:, 2], "hito4": res["hitos"][:, 3]}).round(4).to_csv(index=False)
    return a


with tab_sim:
    st.markdown("Cambie los supuestos y vea cómo se mueve el riesgo. Con los valores iniciales la simulación reproduce las cifras "
                "del informe; todo corre aquí mismo en un par de segundos y **no llama a ninguna API**.")
    with st.form("supuestos"):
        f1, f2, f3, f4 = st.columns(4)
        ventas_media = f1.slider("Ritmo de ventas esperado", 0.50, 1.50, 1.00, 0.05,
                                 help="1 = el plan de clientes nuevos del caso. 0.70 equivale a su escenario conservador.")
        ventas_banda = f2.slider("Incertidumbre del ritmo de ventas (±)", 0.0, 0.60, 0.30, 0.05,
                                 help="Distancia entre lo esperado y el P10/P90. 0.30 reproduce los escenarios conservador y optimista del caso.")
        bajas_p90 = f3.slider("Bajas en el 10% peor de los casos", 1.05, 2.0, 1.30, 0.05, help="1 = el plan. 1.30 = 30% más bajas.")
        descuento = f4.slider("Descuento máximo sobre el precio de lista", 0.0, 0.40, 0.20, 0.05, format="%.2f")
        g0, g1, g2, g3, g4 = st.columns(5)
        conversion = g0.slider("Conversión media de cada piloto", 0.20, 0.90, 0.50, 0.05)
        cv = g1.slider("Costo variable de IA: mínimo y máximo", 0.05, 0.50, (0.22, 0.35), 0.01)
        cv_moda = g2.slider("Costo variable más probable", 0.05, 0.50, 0.25, 0.01)
        rho = g3.slider("Vínculo entre pilotos, ventas y bajas", 0.0, 0.9, 0.5, 0.1,
                        help="Correlación con un factor común de ajuste producto-mercado.")
        n = g4.select_slider("Corridas", options=[1_000, 2_000, 5_000, 10_000, 20_000], value=10_000)
        semilla = st.number_input("Semilla (fija para que el resultado sea reproducible)", value=20261026, step=1)
        st.form_submit_button("Correr simulación", type="primary")
    cv_tri = (min(cv[0], cv_moda), cv_moda, max(cv[1], cv_moda))
    with st.spinner("Simulando 60 meses en cada corrida…"):
        a = simular(int(n), int(semilla), ventas_media, ventas_banda, bajas_p90, cv_tri, descuento, conversion, rho)
    r, r0 = a["resumen"], MC["resumen"]
    delta = lambda x, y: f"{100 * (x - y):+.0f} pts vs informe" if abs(x - y) >= 0.005 else None
    c = st.columns(5)
    c[0].metric("Recuperar en 60 meses", pct(r["prob_recupera_60"]), delta(r["prob_recupera_60"], r0["prob_recupera_60"]))
    c[1].metric("Los cuatro hitos", pct(r["prob_todos_los_hitos"]), delta(r["prob_todos_los_hitos"], r0["prob_todos_los_hitos"]))
    c[2].metric("Necesidad de caja P50", usd(r["necesidad_maxima"]["p50"]))
    c[3].metric("Necesidad de caja P90", usd(r["necesidad_maxima"]["p90"]))
    c[4].metric("VAN con valor terminal > 0", pct(r["prob_van_con_vt_positivo"]), delta(r["prob_van_con_vt_positivo"], r0["prob_van_con_vt_positivo"]))

    izq, der = st.columns([3, 2])
    with izq:
        st.plotly_chart(grafico_abanico(a["bandas_caja"], R["serie_base"]["caja"]), width="stretch", key="grafico_7")
    with der:
        st.plotly_chart(barras_hitos(r["prob_hito"], r["prob_hito_condicional"]), width="stretch", key="grafico_8")
    izq, der = st.columns(2)
    with izq:
        st.markdown("**Necesidad máxima de caja**")
        st.plotly_chart(histograma(a["histogramas"]["necesidad_maxima"],
                                   [(r["necesidad_maxima"]["p50"], "P50"), (r["necesidad_maxima"]["p90"], "P90"), (1.19e6, "Financiamiento")],
                                   "Millones de USD"), width="stretch", key="grafico_histograma_caja")
    with der:
        st.markdown("**Qué supuesto pesa más** (cada uno en su P10 y su P90; los demás, en el plan)")
        st.plotly_chart(tornado(a["tornado"]), width="stretch", key="grafico_9")
    st.markdown("**Riesgos del caso de negocio, con probabilidad e impacto**")
    st.dataframe(pd.DataFrame([{
        "Riesgo": f["riesgo"], "Probabilidad": pct(f["probabilidad"]),
        "Recupera en 60 meses si ocurre": pct(f["recupera_si_ocurre"]), "Recupera si no ocurre": pct(f["recupera_si_no"]),
        "Cumple el hito 2 si ocurre": pct(f["hito2_si_ocurre"]), "Hito 2 si no ocurre": pct(f["hito2_si_no"]),
        "Necesidad de caja (mediana) si ocurre": usd(f["necesidad_p50_si_ocurre"]),
    } for f in a["riesgos"]]), hide_index=True, width="stretch")
    izq, der = st.columns(2)
    with izq:
        st.markdown("**Convergencia:** la estimación se estabiliza a partir de unas 2,000 corridas")
        cv_df = pd.DataFrame(a["convergencia"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(cv_df["n"]) + list(cv_df["n"])[::-1],
                                 y=list(cv_df["prob_recupera"] + cv_df["ic95_prob"]) + list(cv_df["prob_recupera"] - cv_df["ic95_prob"])[::-1],
                                 fill="toself", fillcolor=AZUL_100, line=dict(width=0), mode="lines", name="Intervalo de 95%", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=cv_df["n"], y=cv_df["prob_recupera"], mode="lines+markers", line=dict(color=AZUL, width=2),
                                 marker=dict(size=8), name="Probabilidad de recuperar en 60 meses",
                                 hovertemplate="%{x:,} corridas: %{y:.1%}<extra></extra>"))
        fig.update_xaxes(type="log", tickvals=list(cv_df["n"]), ticktext=[f"{v:,}" for v in cv_df["n"]])
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(estilo(fig, 280, None, "Corridas"), width="stretch", key="grafico_10")
    with der:
        st.markdown("**Correlación de rangos (Spearman) con el VAN**")
        st.dataframe(pd.DataFrame([{"Supuesto": f["variable"], "Con el VAN": f"{f['con_van']:+.2f}",
                                    "Con la necesidad de caja": f"{f['con_necesidad']:+.2f}"} for f in a["correlaciones"]]),
                     hide_index=True, width="stretch")
        st.download_button("Descargar las corridas (CSV)", a["csv"], file_name="corridas_montecarlo.csv", mime="text/csv")


# ================================================================== 4. VALOR PARA EL CLIENTE
with tab_cliente:
    st.markdown("¿Cuándo se paga solo el plan? El beneficio es la capacidad que libera el equipo de QA; la mejora de productividad "
                "es incierta: el World Quality Report 2025 reporta 19% en promedio y que un tercio de las organizaciones obtuvo mejoras mínimas.")
    f1, f2, f3, f4 = st.columns(4)
    personas = f1.slider("Personas en QA", 1, 10, 4)
    costo_persona = f2.number_input("Costo por persona al mes (USD, con cargas)", 1500, 8000, 3000, 250)
    plan = f3.selectbox("Plan", ["Inicial", "Profesional", "Empresarial"], index=1)
    prob_minima = f4.slider("Clientes con mejora mínima", 0.0, 0.6, 1 / 3, 0.05, format="%.2f")
    sc = mod_cliente.SupuestosCliente(costo_persona_mes=float(costo_persona), prob_minima=prob_minima)
    mejora = mod_cliente.sortear_mejora(sc, 20_000, np.random.default_rng(20261026))
    ev = mod_cliente.evaluar(personas, plan, mejora, sc)
    roi = ev["roi"]
    c = st.columns(4)
    c[0].metric("El plan se paga solo el primer año", pct(float((roi > 0).mean())))
    c[1].metric("Mejora mínima necesaria", pct(ev["mejora_minima"], 1))
    c[2].metric("Retorno mediano", pct(float(np.median(roi))))
    c[3].metric("Costo del primer año", usd(ev["costo_primer_anio"]))
    cuentas, bordes = np.histogram(np.clip(roi, -1, 6), bins=40)
    centros = (bordes[:-1] + bordes[1:]) / 2
    fig = go.Figure(go.Bar(x=centros, y=cuentas / cuentas.sum(), width=(bordes[1] - bordes[0]) * 0.92,
                           marker_color=[NARANJA if x < 0 else AZUL for x in centros],
                           hovertemplate="Retorno %{x:.0%}<br>%{y:.1%} de los clientes<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=TINTA, width=1))
    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(estilo(fig, 300, "Clientes simulados", "Retorno del primer año sobre el costo del plan", leyenda=False), width="stretch", key="grafico_11")
    st.caption("Rojo: el plan no se paga solo el primer año. La capacidad liberada no incluye el valor de publicar antes ni el de los "
               "defectos evitados, que cada cliente debe medir en su piloto con una línea base.")
    st.markdown("**Por tamaño de equipo** (supuestos del informe: USD 3,000 por persona al mes)")
    st.dataframe(pd.DataFrame([{"Plan": f["plan"], "Personas en QA": f["personas"], "Mejora mínima": pct(f["mejora_minima"], 1),
                                "Se paga solo el primer año": pct(f["prob_se_paga"]), "Retorno mediano": pct(f["roi_p50"])}
                               for f in R["cliente"]["tabla"]]), hide_index=True, width="stretch")


# ================================================================== 5. GOBERNANZA
with tab_gob:
    st.markdown("El agente hace el trabajo; las personas deciden en dos compuertas (aprobar el plan y confirmar cada defecto) y el "
                "programa impone límites que el modelo no puede saltarse.")
    izq, der = st.columns(2)
    with izq:
        st.subheader("Las compuertas humanas, medidas")
        st.dataframe(pd.DataFrame([{"Ciclo": f"{x['ciclo']} · {x['fecha']}", "Revisión del plan": f"{x['revision_plan_seg']} s",
                                    "Casos editados": 10 - x["aceptacion_plan"]["exitos"],
                                    "Decisiones sobre defectos": x["decisiones_humanas"],
                                    "Correctas": x["decisiones_correctas"]} for x in AG["por_ciclo"]]),
                     hide_index=True, width="stretch")
        st.markdown(
            "- En tres ciclos nadie editó un caso del plan y la revisión duró entre 54 s y 2 min: la aprobación tiende a ser automática "
            "(sesgo de automatización).\n"
            "- En el ciclo B se **confirmó un falso positivo** (el asunto del formulario de contacto) y se **descartó un defecto real** "
            "(el login con campos vacíos, defecto 17 de la lista oficial) «por no ser de impacto»: la compuerta mezcló *¿es real?* con *¿importa?*.\n"
            "- Respuesta de diseño: abrir la evidencia antes de confirmar, exigir un motivo al descartar, separar validez y severidad, y "
            "registrar el tiempo de revisión.")
    with der:
        st.subheader("Incidentes y controles")
        incidentes = RAIZ / "qa" / "incidentes.md"
        st.markdown(
            "- **Compra real durante la exploración** (21-10-2026, factura INV-2026000005): el agente pulsó «Confirm» al explorar.\n"
            "- **Control nuevo:** `app/agente.py` detiene en el navegador del agente los clics en pagar, confirmar, comprar, enviar o "
            "transferir y los anota en `qa/incidentes.md`; solo una persona puede habilitarlos (`QA_PERMITIR_IRREVERSIBLES=1`).\n"
            "- **Controles que ya existían:** el navegador solo abre el dominio de la aplicación bajo prueba; en conversación el agente "
            "solo lee; cada paso tiene tope de turnos y de gasto; la llave de la API nunca se sube al repositorio.")
        if incidentes.exists():
            st.markdown(incidentes.read_text(encoding="utf-8"))
        else:
            st.caption("Todavía no hay acciones detenidas en este repositorio.")

    st.subheader("Qué datos salen del perímetro del cliente")
    st.dataframe(pd.DataFrame([
        {"Dato": "Requisitos, plan y defectos (texto)", "Hoy (MVP)": "Al proveedor del modelo (API de Anthropic)",
         "Despliegue para pilotos": "Modelo consumido desde la nube del cliente (Amazon Bedrock, Google Cloud o Microsoft Foundry)"},
        {"Dato": "Capturas y árbol de accesibilidad de la aplicación", "Hoy (MVP)": "Al proveedor del modelo",
         "Despliegue para pilotos": "Filtro de datos personales antes de enviarlas; solo ambientes de prueba"},
        {"Dato": "Datos de prueba (usuarios, tarjetas, cuentas)", "Hoy (MVP)": "Usuarios públicos de demostración",
         "Despliegue para pilotos": "Solo datos sintéticos o enmascarados; nunca datos de producción"},
        {"Dato": "Pruebas generadas y resultados", "Hoy (MVP)": "Repositorio del equipo", "Despliegue para pilotos": "Repositorio del cliente"},
    ]), hide_index=True, width="stretch")
    st.caption("Por defecto, Anthropic no usa las entradas ni las salidas de su API comercial para entrenar modelos.")

    st.subheader("Dónde falla el agente: desempeño por requisito (posibles sesgos)")
    req = AG["por_requisito"]
    nombres = {"R1": "R1 · Inicio de sesión", "R2": "R2 · Catálogo y búsqueda", "R3": "R3 · Carrito", "R4": "R4 · Compra y factura",
               "R5": "R5 · Favoritos", "R6": "R6 · Contacto"}
    st.dataframe(pd.DataFrame([{"Requisito": nombres.get(k, k), "Defectos conocidos": v["defectos"],
                                "Encontrados por algún ciclo": v["detectados_union"],
                                "Detecciones / oportunidades": f"{v['detecciones']} de {v['oportunidades']}",
                                "Tasa": pct(v["detecciones"] / v["oportunidades"])} for k, v in req.items()]),
                 hide_index=True, width="stretch")
    st.markdown(
        "- **Sesgo de percepción:** el agente «ve» la aplicación por el árbol de accesibilidad y capturas; los flujos largos (compra y "
        "factura, R4) y los controles sin nombre accesible son donde menos encuentra.\n"
        "- **Sesgo hacia el camino feliz:** los defectos nunca vistos están en caminos poco usados (botones + y −, más de 10 unidades, "
        "bloqueo tras un intento fallido).\n"
        "- **Artefactos de automatización:** 2 de los 3 falsos positivos vienen de una interacción que un usuario no hace "
        "(el asunto elegido sin quitar el foco).\n"
        "- **Contexto:** todo se probó en tiendas en inglés; falta medirlo en aplicaciones en español con formatos dominicanos.")
