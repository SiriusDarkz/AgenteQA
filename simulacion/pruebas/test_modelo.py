"""Valida el modelo reconstruido contra las cifras publicadas en el caso de negocio.

Correr desde la raíz del repositorio:  python -m pytest simulacion/pruebas -q
"""
import numpy as np
import pytest

from simulacion.modelo import BASE, correr_escenario, indicadores, simular


def _base():
    return correr_escenario("base")


def test_anios_1_a_3_del_escenario_base():
    r = _base()
    sim, ind = r["simulacion"], r["indicadores"]
    ingresos = sim["ingresos"][0].reshape(5, 12).sum(axis=1)
    variable = sim["costo_variable"][0].reshape(5, 12).sum(axis=1)
    assert ingresos[:3] == pytest.approx([58_224, 431_798, 1_148_172], abs=1)
    assert variable[:3] == pytest.approx([9_681, 91_449, 251_668], abs=1)
    assert ind["resultados_anuales"][:3] == pytest.approx([-361_257, -404_851, -220_696], abs=1)
    arr = sim["arr"][0]
    assert [arr[11], arr[23], arr[35]] == pytest.approx([131_202, 552_991, 1_370_276], abs=1)
    clientes = sim["clientes"][0]
    assert [round(clientes[11]), round(clientes[23]), round(clientes[35])] == [8, 33, 75]


def test_caja_e_hitos_del_escenario_base():
    ind = _base()["indicadores"]
    caja = _base()["simulacion"]["caja"][0]
    assert round(ind["necesidad_maxima"]) == 991_523 and ind["mes_necesidad"] == 34
    assert ind["mes_equilibrio"] == 35 and ind["mes_recuperacion"] == 60
    # inversión acumulada en cada hito: meses 6, 12, 24 y 36
    assert [-caja[5], -caja[11], -caja[23], -caja[35]] == pytest.approx([188_400, 361_257, 766_108, 986_804], abs=1)


def test_anios_4_y_5_y_retorno():
    ind = _base()["indicadores"]
    assert ind["resultados_anuales"][3:] == pytest.approx([290_867, 784_033], abs=1)
    assert ind["caja_m60"] == pytest.approx(88_096, abs=1)
    assert ind["ingresos_anuales"][4] == pytest.approx(3.15e6, rel=0.002)
    assert ind["valor_terminal"] == pytest.approx(4.75e6, rel=0.001)
    assert ind["van_con_vt"] == pytest.approx(1.61e6, rel=0.003)
    assert ind["tir_con_vt"] == pytest.approx(0.62, abs=0.005)
    assert ind["van_sin_vt"] == pytest.approx(-294_876, rel=0.005)   # 0.16 % de diferencia
    assert ind["tir_sin_vt"] == pytest.approx(0.029, abs=0.001)


def test_escenarios_conservador_y_optimista():
    cons = correr_escenario("conservador")
    s, i = cons["simulacion"], cons["indicadores"]
    assert [s["arr"][0][11], s["arr"][0][23], s["arr"][0][35]] == pytest.approx([90_874, 375_452, 920_479], abs=1)
    assert round(s["clientes"][0][35]) == 50
    assert -s["caja"][0][23] == pytest.approx(875_860, abs=1)
    assert i["resultados_anuales"][2] == pytest.approx(-449_092, abs=1)
    assert i["necesidad_maxima"] == pytest.approx(1_498_616, rel=0.001)
    assert np.isnan(i["mes_recuperacion"])

    opt = correr_escenario("optimista")
    s, i = opt["simulacion"], opt["indicadores"]
    assert s["arr"][0][35] == pytest.approx(1_832_535, abs=1)
    assert round(s["clientes"][0][35]) == 102
    assert i["resultados_anuales"][2] == pytest.approx(112_670, abs=1)
    assert round(i["necesidad_maxima"]) == 685_568 and i["mes_necesidad"] == 28
    assert i["mes_equilibrio"] == 29 and i["mes_recuperacion"] == 44


@pytest.mark.parametrize("nombre, necesidad, equilibrio, recuperacion", [
    ("precio -20%", 1_288_747, 45, None),
    ("clientes nuevos -20%", 1_236_876, 43, None),
    ("costo variable 35%", 1_136_683, 39, None),
    ("bajas +50%", 1_040_135, 37, None),
    ("clientes nuevos +20%", 800_803, 32, 50),
    ("precio +20%", 791_213, 31, 49),
])
def test_sensibilidades(nombre, necesidad, equilibrio, recuperacion):
    i = correr_escenario(nombre)["indicadores"]
    assert i["necesidad_maxima"] == pytest.approx(necesidad, rel=0.001)      # a menos de 0.1 %
    assert abs(i["mes_equilibrio"] - equilibrio) <= 1                          # a un mes como máximo
    if recuperacion is None:
        assert np.isnan(i["mes_recuperacion"])
    else:
        assert i["mes_recuperacion"] == recuperacion


def test_modo_discreto_promedia_cerca_del_determinista():
    rng = np.random.default_rng(1)
    sim = simular(BASE, 4000, discreto=True, rng=rng)
    det = simular(BASE, 1)
    # el ARR medio al mes 36 de clientes enteros sorteados queda a menos de 2 % del determinista
    assert sim["arr"][:, 35].mean() == pytest.approx(det["arr"][0, 35], rel=0.02)
