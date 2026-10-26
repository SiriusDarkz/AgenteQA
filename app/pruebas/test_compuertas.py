"""Pruebas del control de acciones irreversibles del MVP (app/agente.py).

Correr desde la raíz del repositorio:  python -m pytest app/pruebas -q
"""
import pytest

from app.agente import es_irreversible

CLIC = "mcp__playwright__browser_click"


@pytest.mark.parametrize("elemento", [
    "Confirm button", "button «Confirm»", "Place order", "Pay now", "Pagar ahora", "Finish button",
    "Send", "Enviar mensaje", "Comprar", "Buy now", "Transferir fondos", "Delete account", "Eliminar cuenta",
])
def test_detiene_acciones_irreversibles(elemento):
    assert es_irreversible(CLIC, {"element": elemento, "ref": "e12"})


@pytest.mark.parametrize("elemento", [
    "Proceed to checkout", "Add to cart", "Login button", "Search", "Payment method select",
    "Remove product from cart", "Category Hammer", "Next", "Sort by price", "Contact link",
])
def test_deja_pasar_acciones_normales(elemento):
    assert es_irreversible(CLIC, {"element": elemento, "ref": "e12"}) is None


def test_escribir_y_enviar_con_enter():
    tipo = "mcp__playwright__browser_type"
    assert es_irreversible(tipo, {"element": "Send message box", "text": "hola", "submit": True})
    assert es_irreversible(tipo, {"element": "Send message box", "text": "hola", "submit": False}) is None
    assert es_irreversible(tipo, {"element": "Search box", "text": "hammer", "submit": True}) is None


def test_tecla_enter_solo_con_descripcion_irreversible():
    tecla = "mcp__playwright__browser_press_key"
    assert es_irreversible(tecla, {"key": "Tab"}) is None
    assert es_irreversible(tecla, {"key": "Enter"}) is None
    assert es_irreversible(tecla, {"key": "Enter", "element": "Confirm order"})


def test_patron_configurable(monkeypatch):
    monkeypatch.setenv("QA_ACCIONES_IRREVERSIBLES", r"\bborrar\b")
    assert es_irreversible(CLIC, {"element": "Borrar producto"})
    assert es_irreversible(CLIC, {"element": "Confirm button"}) is None
