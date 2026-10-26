"""Modelo financiero del caso de negocio del Agente Virtual de QA (60 meses).

Reconstruye, mes a mes, el modelo propio del caso de negocio (octubre de 2026) a partir de
los supuestos que el documento publica, y sirve de motor para la simulación Monte Carlo.

Cómo funciona
-------------
- Tres planes de suscripción (Inicial, Profesional y Empresarial) con precio mensual, cargo
  único de implementación y baja mensual propios.
- Los clientes nuevos de cada año se reparten por igual entre sus meses. La venta empieza en
  el mes 7, así que los del año 1 entran entre los meses 7 y 12.
- Cada mes primero se aplican las bajas sobre los clientes del mes anterior y después entran
  los nuevos. La suscripción se cobra por mes adelantado y la implementación, al firmar.
- El costo variable (inferencia de IA e infraestructura) es un porcentaje de la suscripción
  de lista, no del precio cobrado.
- El gasto fijo (equipo y otros gastos) sube por «olas». Cada ola se activa el mes siguiente
  a que el ingreso recurrente anual (ARR) supera su umbral, pero nunca antes del año previsto.
  Desde el año 4, el gasto de cada ola se incorpora de forma gradual durante 12 meses
  (contrataciones escalonadas).
- La caja acumulada es el resultado operativo acumulado, sin capital de trabajo ni impuestos.

Validación
----------
`simulacion/pruebas/test_modelo.py` comprueba que el escenario base reproduce las cifras
publicadas: ingresos, costo variable, resultado y ARR de cada año, necesidad máxima de caja
de USD 991,523 en el mes 34, equilibrio en el mes 35, recuperación en el mes 60, valor
terminal y VAN con valor terminal. También reproduce los años 1 a 3 de los escenarios
conservador y optimista y queda a menos de 0.1 % de la necesidad de caja publicada en todas
las sensibilidades.

Los dos parámetros de la rampa de los años 4 y 5 no aparecen en el caso de negocio; se
calibraron para que el gasto fijo sume USD 1,321,600 en el año 4 y USD 1,635,900 en el año 5,
que es lo que implican sus resultados publicados.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

import numpy as np

PLANES = ("Inicial", "Profesional", "Empresarial")


@dataclass(frozen=True)
class Supuestos:
    """Supuestos del escenario base del caso de negocio. Todos los montos en USD."""

    precios: tuple = (490.0, 1490.0, 4900.0)            # suscripción mensual por plan
    implementacion: tuple = (0.0, 2500.0, 12000.0)       # cargo único al firmar
    bajas_mensuales: tuple = (0.030, 0.015, 0.0075)      # baja mensual de clientes por plan
    # clientes nuevos por año (Inicial, Profesional, Empresarial), años 1 a 5
    nuevos_por_anio: tuple = ((4, 3, 1), (15, 12, 3), (26, 23, 7), (34, 30, 9), (41, 36, 11))
    mes_inicio_ventas: int = 7
    costo_variable: float = 0.25                         # sobre la suscripción de lista

    # gasto fijo mensual (equipo + otros gastos operativos) por etapa
    gasto_desarrollo: float = 31_400.0                   # meses 1 a 6
    gasto_lanzamiento: float = 36_900.0                  # desde el mes 7 hasta la ola 1
    gasto_ola1: float = 62_100.0                         # equipo de 11 personas
    gasto_ola2: float = 93_100.0                         # equipo de 17 personas
    # olas 3 (23 personas) y 4 (27 personas): rampa de 12 meses desde la activación
    ola3_base: float = 98_065.0
    ola3_pendiente: float = 111_400.0 / 60.0             # USD 1,856.67 más cada mes
    ola4_base: float = 129_825.0
    ola4_pendiente: float = 1_000.0
    meses_rampa: int = 12

    umbrales_ola: tuple = (100_000.0, 500_000.0, 1_200_000.0, 2_000_000.0)  # ARR que activa cada ola
    mes_minimo_ola: tuple = (13, 25, 37, 49)            # mes más temprano de cada ola

    tasa_descuento: float = 0.20                         # anual
    crecimiento_terminal: float = 0.03                   # perpetuidad del valor terminal
    meses: int = 60


BASE = Supuestos()


def _vector(valor, n: int) -> np.ndarray:
    """Convierte un escalar o un arreglo en un vector de n corridas."""
    v = np.asarray(valor, dtype=float)
    return np.broadcast_to(v, (n,)).astype(float) if v.ndim == 0 else v.astype(float)


def simular(s: Supuestos = BASE, n: int = 1, *, m_altas=1.0, m_bajas=1.0, costo_variable=None,
            m_precio=1.0, discreto: bool = False, rng: Optional[np.random.Generator] = None) -> dict:
    """Simula n corridas de 60 meses a la vez.

    Parámetros por corrida (escalar o vector de largo n):
      m_altas         multiplicador del ritmo de clientes nuevos (1 = plan)
      m_bajas         multiplicador de las bajas mensuales (1 = plan)
      costo_variable  fracción de la suscripción de lista (None = el del supuesto)
      m_precio        precio cobrado frente al de lista (1 = sin descuento)
    discreto=False usa clientes fraccionarios (el modelo determinista del caso);
    discreto=True sortea clientes enteros: altas Poisson y bajas binomiales.

    Devuelve un diccionario con series mensuales de forma (n, meses) y los meses de
    activación de cada ola, de forma (n, 4) (0 = no se activó).
    """
    if discreto and rng is None:
        rng = np.random.default_rng()
    T = s.meses
    m_altas = _vector(m_altas, n)
    m_bajas = _vector(m_bajas, n)
    cv = _vector(s.costo_variable if costo_variable is None else costo_variable, n)
    m_precio = _vector(m_precio, n)

    precios = np.array(s.precios)
    impl = np.array(s.implementacion)
    bajas = np.array(s.bajas_mensuales)
    nuevos = np.array(s.nuevos_por_anio, dtype=float)

    clientes = np.zeros((n, 3))
    activacion = np.zeros((n, 4), dtype=int)
    salida = {k: np.zeros((n, T)) for k in
              ("clientes", "ingresos", "suscripcion", "implementacion", "costo_variable",
               "contribucion", "gasto_fijo", "resultado", "arr")}
    salida["clientes_plan"] = np.zeros((n, T, 3))
    salida["empresariales_firmados_m12"] = np.zeros(n)

    for m in range(1, T + 1):
        anio = (m - 1) // 12
        if m < s.mes_inicio_ventas:
            tasa = np.zeros(3)
        else:
            meses_venta = 12 - (s.mes_inicio_ventas - 1) if anio == 0 else 12
            tasa = nuevos[min(anio, len(nuevos) - 1)] / meses_venta
        lam = np.outer(m_altas, tasa)                              # altas esperadas (n, 3)
        p_baja = np.clip(np.outer(m_bajas, bajas), 0.0, 1.0)

        if discreto:
            altas = rng.poisson(lam).astype(float)
            salidas = rng.binomial(clientes.astype(int), p_baja).astype(float)
            clientes = clientes - salidas + altas
        else:
            altas = lam
            clientes = clientes * (1 - p_baja) + altas
        if m <= 12:
            salida["empresariales_firmados_m12"] += altas[:, 2]

        lista = clientes @ precios
        suscripcion = lista * m_precio
        implementacion = altas @ impl
        variable = cv * lista
        contribucion = suscripcion + implementacion - variable

        # gasto fijo según las olas activas este mes
        activas = (activacion > 0) & (activacion <= m)
        k = activas.sum(axis=1)
        fijo = np.where(m <= 6, s.gasto_desarrollo, s.gasto_lanzamiento)
        fijo = np.where(k == 1, s.gasto_ola1, fijo)
        fijo = np.where(k == 2, s.gasto_ola2, fijo)
        d3 = np.minimum(m - activacion[:, 2] + 1, s.meses_rampa)
        fijo = np.where(k == 3, s.ola3_base + s.ola3_pendiente * d3, fijo)
        d4 = np.minimum(m - activacion[:, 3] + 1, s.meses_rampa)
        fijo = np.where(k == 4, s.ola4_base + s.ola4_pendiente * d4, fijo)
        fijo = np.broadcast_to(fijo, (n,)).astype(float)

        arr = 12 * suscripcion
        for i in range(4):
            previa = activacion[:, i - 1] > 0 if i > 0 else np.ones(n, bool)
            nueva = (activacion[:, i] == 0) & (arr >= s.umbrales_ola[i]) & previa
            activacion[nueva, i] = max(s.mes_minimo_ola[i], m + 1)

        j = m - 1
        salida["clientes"][:, j] = clientes.sum(axis=1)
        salida["clientes_plan"][:, j] = clientes
        salida["ingresos"][:, j] = suscripcion + implementacion
        salida["suscripcion"][:, j] = suscripcion
        salida["implementacion"][:, j] = implementacion
        salida["costo_variable"][:, j] = variable
        salida["contribucion"][:, j] = contribucion
        salida["gasto_fijo"][:, j] = fijo
        salida["resultado"][:, j] = contribucion - fijo
        salida["arr"][:, j] = arr

    salida["caja"] = np.cumsum(salida["resultado"], axis=1)
    salida["activacion_olas"] = activacion
    return salida


def _tir_mensual(flujos: np.ndarray) -> np.ndarray:
    """TIR mensual por bisección, vectorizada por corrida; NaN si no hay cambio de signo."""
    meses = np.arange(1, flujos.shape[1] + 1)

    def van(tasa):
        return (flujos / (1 + tasa[:, None]) ** meses).sum(axis=1)

    lo = np.full(flujos.shape[0], -0.05)
    hi = np.full(flujos.shape[0], 0.50)
    f_lo, f_hi = van(lo), van(hi)
    valida = np.sign(f_lo) != np.sign(f_hi)
    for _ in range(80):
        mid = (lo + hi) / 2
        f_mid = van(mid)
        izquierda = np.sign(f_mid) == np.sign(f_lo)
        lo = np.where(izquierda, mid, lo)
        f_lo = np.where(izquierda, f_mid, f_lo)
        hi = np.where(izquierda, hi, mid)
    return np.where(valida, (lo + hi) / 2, np.nan)


def indicadores(sim: dict, s: Supuestos = BASE, tir: bool = True) -> dict:
    """Indicadores del caso de negocio para cada corrida (vectores de largo n)."""
    caja = sim["caja"]
    r = sim["resultado"]
    n, T = r.shape
    meses = np.arange(1, T + 1)

    i_min = caja.argmin(axis=1)
    necesidad = -caja[np.arange(n), i_min]
    mes_necesidad = i_min + 1

    positivo = (r >= 0) & (meses >= 7)
    mes_equilibrio = np.where(positivo.any(axis=1), positivo.argmax(axis=1) + 1, np.nan)

    recupera = (caja >= 0) & (meses[None, :] > mes_necesidad[:, None])
    mes_recuperacion = np.where(recupera.any(axis=1), recupera.argmax(axis=1) + 1, np.nan)

    anual = r.reshape(n, T // 12, 12).sum(axis=2)
    tasa_m = (1 + s.tasa_descuento) ** (1 / 12) - 1
    van_sin_vt = (r / (1 + tasa_m) ** meses).sum(axis=1)
    resultado_a5 = anual[:, -1]
    # perpetuidad del resultado del año 5; si el año 5 cierra con pérdida no se asigna valor terminal
    valor_terminal = np.maximum(resultado_a5, 0) * (1 + s.crecimiento_terminal) / (s.tasa_descuento - s.crecimiento_terminal)
    van_con_vt = van_sin_vt + valor_terminal / (1 + s.tasa_descuento) ** (T / 12)

    out = dict(
        necesidad_maxima=necesidad, mes_necesidad=mes_necesidad, mes_equilibrio=mes_equilibrio,
        mes_recuperacion=mes_recuperacion, caja_m60=caja[:, -1], resultados_anuales=anual,
        ingresos_anuales=sim["ingresos"].reshape(n, T // 12, 12).sum(axis=2),
        arr_m12=sim["arr"][:, 11], arr_m24=sim["arr"][:, 23], arr_m36=sim["arr"][:, 35],
        clientes_m36=sim["clientes"][:, 35], van_sin_vt=van_sin_vt, valor_terminal=valor_terminal,
        van_con_vt=van_con_vt, activacion_olas=sim["activacion_olas"],
    )
    if tir:
        out["tir_sin_vt"] = (1 + _tir_mensual(r)) ** 12 - 1
        flujos_vt = r.copy()
        flujos_vt[:, -1] += valor_terminal
        out["tir_con_vt"] = (1 + _tir_mensual(flujos_vt)) ** 12 - 1
    return out


def escenario(nombre: str) -> dict:
    """Parámetros de los escenarios y sensibilidades publicados en el caso de negocio."""
    tabla = {
        "base": dict(),
        "conservador": dict(m_altas=0.7, m_bajas=1.3, costo_variable=0.30),
        "optimista": dict(m_altas=1.3, m_bajas=0.8, costo_variable=0.22),
        "precio -20%": dict(m_precio=0.8),
        "clientes nuevos -20%": dict(m_altas=0.8),
        "costo variable 35%": dict(costo_variable=0.35),
        "bajas +50%": dict(m_bajas=1.5),
        "clientes nuevos +20%": dict(m_altas=1.2),
        "precio +20%": dict(m_precio=1.2),
    }
    return tabla[nombre]


def correr_escenario(nombre: str, s: Supuestos = BASE) -> dict:
    """Corre un escenario determinista y devuelve la simulación y sus indicadores (corrida única)."""
    sim = simular(s, 1, **escenario(nombre))
    ind = indicadores(sim, s)
    return {"simulacion": sim, "indicadores": {k: (v[0] if np.ndim(v) else v) for k, v in ind.items()}}


def con(s: Supuestos = BASE, **cambios) -> Supuestos:
    """Copia de los supuestos con algunos valores cambiados."""
    return replace(s, **cambios)
