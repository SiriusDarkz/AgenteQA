"""Modo demo: reproduce un ciclo de ejemplo sobre Swag Labs sin llamar a la API ni abrir un navegador.

Sirve para mostrar la interfaz (y como plan B el día de la demo). Los archivos que deja
en qa/ y tests/ vienen de app/demo/ciclo/ y están marcados como ejemplo; los resultados,
defectos y el reporte se generan a partir del plan que la persona aprobó, de modo que
las dos decisiones humanas (aprobar el plan, confirmar cada defecto) sí tienen efecto.

Para reemplazar el ejemplo con un ensayo real: python3 -m app.guardar_ejemplos
"""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Callable

from . import estado

CICLO = Path(__file__).resolve().parent / "ejemplos" / "ciclo"
VELOCIDAD = float(os.environ.get("QA_DEMO_VELOCIDAD", "1"))

NOTA_EJEMPLO = ("> Archivo de ejemplo del modo demo: no es una ejecución real de Playwright. "
                "Corre `python3 -m app` (sin `--demo`) para un ciclo real con el agente.\n\n")

# Resultado de cada caso del plan de ejemplo: (resultado, segundos, archivo de prueba).
RESULTADOS = {
    "CP-01": ("PASÓ", 2.1, "tests/login.spec.ts"),
    "CP-02": ("PASÓ", 1.4, "tests/login.spec.ts"),
    "CP-03": ("PASÓ", 1.3, "tests/login.spec.ts"),
    "CP-04": ("PASÓ", 3.0, "tests/catalogo.spec.ts"),
    "CP-05": ("FALLÓ", 6.2, "tests/catalogo.spec.ts"),
    "CP-06": ("PASÓ", 2.8, "tests/carrito.spec.ts"),
    "CP-07": ("PASÓ", 4.1, "tests/checkout.spec.ts"),
    "CP-08": ("FALLÓ", 5.5, "tests/checkout.spec.ts"),
    "CP-09": ("PASÓ", 1.9, "tests/checkout.spec.ts"),
    "CP-10": ("PASÓ", 1.7, "tests/login.spec.ts"),
}

ERRORES = {
    "CP-05": {
        "evidencia": "qa/evidencia/catalogo-Catalogo-CP-05-Catalogo-con-problem-user-imagenes-propias-y-orden-chromium",
        "ubicacion": "catalogo.spec.ts:38:7 › Catálogo › CP-05 · Catálogo con problem_user: imágenes propias y orden",
        "mensaje": (
            "Error: expect(received).toBe(expected) // Object.is equality\n\n"
            "Expected: 6\nReceived: 1\n\n"
            "  20 |   expect(fuentes).toHaveLength(6);\n"
            "> 21 |   expect(new Set(fuentes).size).toBe(6); // seis imágenes distintas\n"
            "     |                                 ^\n"
            "    at verificarCatalogo (tests/catalogo.spec.ts:21:35)"
        ),
    },
    "CP-08": {
        "evidencia": "qa/evidencia/checkout-Checkout-CP-08-Checkout-completo-con-problem-user-chromium",
        "ubicacion": "checkout.spec.ts:43:7 › Checkout › CP-08 · Checkout completo con problem_user",
        "mensaje": (
            "Error: expect(locator).toHaveValue(expected)\n\n"
            "Locator: getByTestId('lastName')\n"
            "Expected string: \"Pérez\"\nReceived string: \"\"\n"
            "Call log:\n  - expect.toHaveValue with timeout 5000ms\n"
            "  - waiting for getByTestId('lastName')\n"
            "    8 × locator resolved to <input type=\"text\" id=\"last-name\" data-test=\"lastName\" name=\"lastName\" placeholder=\"Last Name\" value=\"\"/>\n"
            "      - unexpected value \"\"\n\n"
            "  22 |   await page.getByTestId('postalCode').fill(DATOS_CHECKOUT.codigoPostal);\n"
            "> 23 |   await expect(page.getByTestId('lastName')).toHaveValue(DATOS_CHECKOUT.apellido);\n"
            "     |                                              ^\n"
            "    at checkoutCompleto (tests/checkout.spec.ts:23:46)"
        ),
    },
}

# Defectos de ejemplo y los casos que los provocan.
DEFECTOS = {"DEF-001": ["CP-08"], "DEF-002": ["CP-05"]}


def _texto(texto: str, retraso: float = 0.9) -> tuple[float, dict]:
    return retraso, {"tipo": "texto", "texto": texto}


def _herr(resumen: str, nombre: str = "demo", retraso: float = 0.6) -> tuple[float, dict]:
    return retraso, {"tipo": "herramienta", "nombre": nombre, "resumen": resumen}


def _guion(paso: str, app: dict) -> list[tuple[float, dict]]:
    url = app["url"]
    if paso == "explorar-app":
        return [
            _herr("Lee qa/requisitos.md", "Read", 0.5),
            _texto("Leo los requisitos: cinco requisitos funcionales, cuatro escenarios obligatorios y cuatro usuarios de prueba. Abro la aplicación."),
            _herr(f"Navega a {url}", "mcp__playwright__browser_navigate"),
            _herr("Lee la pantalla (snapshot de accesibilidad)", "mcp__playwright__browser_snapshot"),
            _herr("Escribe «standard_user» en «Username»", "mcp__playwright__browser_type"),
            _herr("Escribe «secret_sauce» en «Password»", "mcp__playwright__browser_type"),
            _herr("Clic en «Login»", "mcp__playwright__browser_click"),
            _herr("Lee la pantalla (snapshot de accesibilidad)", "mcp__playwright__browser_snapshot"),
            _texto("Catálogo con seis productos, selector de orden y carrito. Los controles tienen atributo `data-test`; los uso como localizadores."),
            _herr("Clic en «Add to cart» (Sauce Labs Backpack)", "mcp__playwright__browser_click"),
            _herr("Clic en el ícono del carrito", "mcp__playwright__browser_click"),
            _herr("Clic en «Checkout»", "mcp__playwright__browser_click"),
            _herr("Rellena el formulario", "mcp__playwright__browser_fill_form"),
            _herr("Clic en «Continue»", "mcp__playwright__browser_click"),
            _herr("Clic en «Finish»", "mcp__playwright__browser_click"),
            _texto("Checkout completo con standard_user: subtotal $29.99, impuesto $2.40, total $32.39 y confirmación «Thank you for your order!». Repito el recorrido con problem_user."),
            _herr("Clic en «Open Menu» → «Logout»", "mcp__playwright__browser_click"),
            _herr("Escribe «problem_user» en «Username»", "mcp__playwright__browser_type"),
            _herr("Clic en «Login»", "mcp__playwright__browser_click"),
            _herr("Lee la pantalla (snapshot de accesibilidad)", "mcp__playwright__browser_snapshot"),
            _herr("Toma una captura de pantalla", "mcp__playwright__browser_take_screenshot"),
            _texto("Con problem_user las seis tarjetas muestran la misma imagen y el selector de orden no reordena. Lo anoto como «por verificar en el paso 3», no como defecto."),
            _herr("Rellena el formulario de checkout", "mcp__playwright__browser_fill_form"),
            _herr("Clic en «Continue»", "mcp__playwright__browser_click"),
            _texto("El campo Apellido quedó vacío después de escribir y aparece «Error: Last Name is required». Lo anoto también. Cierro el navegador y escribo la exploración."),
            _herr("Cierra el navegador", "mcp__playwright__browser_close"),
            _herr("Escribe qa/exploracion.md", "Write"),
        ]
    if paso == "disenar-plan":
        return [
            _herr("Lee qa/requisitos.md", "Read", 0.5),
            _herr("Lee qa/exploracion.md", "Read", 0.5),
            _texto("Diseño un caso por camino feliz de cada requisito, dos negativos de inicio de sesión, uno de campos vacíos en el checkout y los cuatro escenarios obligatorios. Los casos con problem_user llevan las mismas expectativas que con standard_user."),
            _herr("Escribe qa/plan-de-pruebas.md", "Write"),
            _herr("Escribe qa/plan-de-pruebas.generado.md (copia intacta para medir las ediciones)", "Write"),
        ]
    if paso == "ejecutar-pruebas":
        return [
            _herr("Lee qa/plan-de-pruebas.md", "Read", 0.5),
            _texto("El plan dice `Estado: APROBADO`. Leo la exploración para los localizadores y genero un archivo de prueba por flujo."),
            _herr("Lee qa/exploracion.md", "Read", 0.4),
            _herr("Lee tests/ejemplo.spec.ts", "Read", 0.4),
            _herr("Escribe tests/login.spec.ts", "Write"),
            _herr("Escribe tests/catalogo.spec.ts", "Write"),
            _herr("Escribe tests/carrito.spec.ts", "Write"),
            _herr("Escribe tests/checkout.spec.ts", "Write"),
            _herr("Ejecuta: npx playwright test --reporter=list,html", "Bash", 0.8),
        ]
    if paso == "analizar-fallos":
        return [
            _herr("Lee qa/resultados.md", "Read", 0.5),
            _texto("Reviso cada prueba fallida: el mensaje de Playwright y la captura de su carpeta de evidencia."),
            _herr("Lee qa/evidencia/…/test-failed-1.png", "Read"),
            _texto("Las dos fallas son defectos de la aplicación, no pruebas frágiles: las mismas pruebas pasan con standard_user y los localizadores resolvieron bien. No hay nada que corregir en las pruebas."),
            _herr("Escribe qa/defectos/DEF-001.md", "Write"),
            _herr("Escribe qa/defectos/DEF-002.md", "Write"),
        ]
    if paso == "reportar":
        return [
            _herr("Lee qa/plan-de-pruebas.md y qa/plan-de-pruebas.generado.md", "Read", 0.5),
            _herr("Lee qa/resultados.md", "Read", 0.4),
            _herr("Lee qa/defectos/DEF-*.md", "Read", 0.4),
            _texto("Comparo el plan aprobado con el generado fila por fila para la métrica del hito 1, cuento la cobertura por prioridad y aplico la regla del semáforo sobre los defectos confirmados."),
            _herr("Escribe qa/reporte.md", "Write"),
        ]
    return []


# ---------------------------------------------------------------- generadores

def _copiar(origen: Path, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.is_dir():
        shutil.copytree(origen, destino, dirs_exist_ok=True)
    else:
        shutil.copy2(origen, destino)


def _resultado_de(caso: dict) -> tuple[str, float, str]:
    if caso["id"] in RESULTADOS:
        return RESULTADOS[caso["id"]]
    if "[Criterio" in caso.get("precondicion", ""):
        # Caso derivado de una historia de usuario: el modo demo simula que pasa.
        return ("PASÓ", 1.6, "tests/historia.spec.ts (simulado)")
    return ("BLOQUEADO", 0.0, "—")


def generar_plan_desde_historia() -> str:
    """Modo demo: un caso por criterio de aceptación de qa/historia-de-usuario.md (más uno negativo cuando aplica)."""
    historia = estado.historia_info()
    criterios = estado.criterios_de_historia() or ["La funcionalidad descrita en la historia se completa sin errores"]
    app = estado.aplicacion()
    filas = []
    n = 0
    negativos = ("obligatorio", "requerido", "vacío", "vacio", "inválid", "invalid", "incorrect", "error", "sin permiso", "bloquead")
    for i, criterio in enumerate(criterios, 1):
        n += 1
        titulo = criterio if len(criterio) <= 70 else criterio[:67].rstrip() + "…"
        filas.append(f"| CP-{n:02d} | {titulo} | {'Alta' if i <= 2 else 'Media'} | standard_user | [Criterio {i}] Sesión iniciada en {app['url']} "
                     f"| 1. Ir a la pantalla que cubre el criterio  2. Ejecutar la acción descrita  3. Observar el resultado | {criterio} |")
        if any(p in criterio.lower() for p in negativos):
            n += 1
            filas.append(f"| CP-{n:02d} | {titulo} (caso negativo) | Media | standard_user | [Criterio {i}] Sesión iniciada "
                         f"| 1. Ir a la pantalla que cubre el criterio  2. Provocar la condición contraria  3. Observar el mensaje | Se muestra un mensaje de error y no se completa la acción |")
    lista_criterios = "\n".join(f"{i}. {c}" for i, c in enumerate(criterios, 1))
    return (f"# Plan de pruebas · {app['nombre']} · historia «{historia['titulo']}»\n\n"
            "> Plan de ejemplo del modo demo, derivado de la historia con una regla simple (un caso por criterio). "
            "En modo real el agente usa la exploración para escribir pasos y localizadores concretos.\n\n"
            "## Objetivo y alcance\n\n"
            f"Verificar la historia «{historia['titulo']}» sobre {app['nombre']} ({app['url']}) a través de sus criterios de aceptación:\n\n{lista_criterios}\n\n"
            "## Datos de prueba\n\n- Usuario: `standard_user` / `secret_sauce`.\n\n"
            "## Casos de prueba\n\n"
            "| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |\n"
            "|----|--------|-----------|---------|--------------|-------|--------------------|\n" + "\n".join(filas) + "\n\n"
            "## Riesgos y supuestos\n\n- Los criterios que no se puedan verificar en la aplicación se anotan aquí al ejecutar.\n\n"
            "Estado: PENDIENTE DE APROBACIÓN\n")


def _salida_playwright(casos: list[dict]) -> str:
    lineas = [f"Running {len(casos)} tests using 1 worker", ""]
    fallidos = []
    total = 0.0
    for i, caso in enumerate(casos, 1):
        resultado, segundos, archivo = _resultado_de(caso)
        total += segundos
        nombre = f"{caso['id']} · {caso['titulo']}"
        if resultado == "FALLÓ":
            err = ERRORES.get(caso["id"], {})
            ubicacion = err.get("ubicacion", f"{Path(archivo).name} › {nombre}")
            lineas.append(f"  ✘  {i} [chromium] › {ubicacion} ({segundos:.1f}s)")
            fallidos.append((ubicacion, err.get("mensaje", "")))
        elif resultado == "BLOQUEADO":
            lineas.append(f"  -  {i} [chromium] › {nombre} (caso añadido por la persona; el modo demo no lo ejecuta)")
        else:
            lineas.append(f"  ✓  {i} [chromium] › {Path(archivo).name} › {nombre} ({segundos:.1f}s)")
    lineas.append("")
    for ubicacion, mensaje in fallidos:
        lineas += [f"  1) [chromium] › {ubicacion}", ""]
        lineas += ["    " + l for l in mensaje.splitlines()]
        lineas.append("")
    pasados = sum(_resultado_de(c)[0] == "PASÓ" for c in casos)
    if fallidos:
        lineas.append(f"  {len(fallidos)} failed")
        for ubicacion, _ in fallidos:
            lineas.append(f"    [chromium] › {ubicacion}")
    bloqueados = sum(_resultado_de(c)[0] == "BLOQUEADO" for c in casos)
    if bloqueados:
        lineas.append(f"  {bloqueados} skipped")
    lineas.append(f"  {pasados} passed ({total:.1f}s)")
    lineas.append("")
    lineas.append("To open last HTML report run:\n\n  npx playwright show-report qa/reporte-html")
    return "\n".join(lineas)


def generar_resultados(casos: list[dict], salida: str) -> str:
    pasaron = sum(_resultado_de(c)[0] == "PASÓ" for c in casos)
    fallaron = sum(_resultado_de(c)[0] == "FALLÓ" for c in casos)
    bloqueados = sum(_resultado_de(c)[0] == "BLOQUEADO" for c in casos)
    total = sum(_resultado_de(c)[1] for c in casos)
    md = [NOTA_EJEMPLO.rstrip(), "", "# Resultados de la ejecución", "", "## Resumen", "",
          f"- Casos planificados: {len(casos)}",
          f"- Casos ejecutados: {len(casos) - bloqueados}",
          f"- Pasaron: {pasaron}", f"- Fallaron: {fallaron}", f"- Bloqueados: {bloqueados}",
          f"- Duración total: {total:.1f} s", f"- Fecha y hora: {estado.ahora()}", "",
          "## Tabla de resultados", "",
          "| ID | Título | Usuario | Resultado | Duración | Archivo de prueba | Evidencia |",
          "|----|--------|---------|-----------|----------|-------------------|-----------|"]
    for caso in casos:
        resultado, segundos, archivo = _resultado_de(caso)
        evidencia = ERRORES.get(caso["id"], {}).get("evidencia", "—") if resultado == "FALLÓ" else "—"
        md.append(f"| {caso['id']} | {caso['titulo']} | {caso['usuario']} | {resultado} | {segundos:.1f} s | {archivo} | {evidencia} |")
    md += ["", "## Pruebas corregidas", "",
           f"Ninguna: las {len(casos)} pruebas corrieron con los localizadores de la exploración sin ajustes.", "",
           "## Salida de Playwright", "", "```", salida, "```", ""]
    return "\n".join(md)


def generar_defectos(casos: list[dict]) -> list[str]:
    ids_fallidos = {c["id"] for c in casos if _resultado_de(c)[0] == "FALLÓ"}
    estado.DEFECTOS.mkdir(parents=True, exist_ok=True)
    creados = []
    for id_defecto, relacionados in DEFECTOS.items():
        if ids_fallidos & set(relacionados):
            _copiar(CICLO / "qa" / "defectos" / f"{id_defecto}.md", estado.DEFECTOS / f"{id_defecto}.md")
            creados.append(id_defecto)
    if not creados:
        (estado.DEFECTOS / "README.md").write_text(
            "# Defectos\n\nNo se encontraron defectos en este ciclo: todas las pruebas ejecutadas pasaron.\n",
            encoding="utf-8")
    return creados


def generar_reporte() -> str:
    plan = estado.plan_info()
    casos = plan["casos"]
    resultados = estado.resultados_info()
    defectos = estado.defectos_info()
    app = estado.aplicacion()
    comparacion = estado.comparar_planes() or {}
    confirmados = [d for d in defectos["lista"] if d["estado"] == "CONFIRMADO"]
    descartados = [d for d in defectos["lista"] if d["estado"] == "DESCARTADO"]

    if any(d["severidad"] == "Crítica" for d in confirmados):
        semaforo, regla = "🔴 No publicar", "hay al menos un defecto Crítico confirmado"
    elif any(d["severidad"] == "Alta" for d in confirmados):
        semaforo, regla = "🟡 Publicar con riesgo conocido", "hay defectos Altos confirmados y ninguno Crítico"
    else:
        semaforo, regla = "🟢 Publicar", "no hay defectos Críticos ni Altos confirmados"

    por_prioridad: dict[str, dict[str, int]] = {}
    for caso in casos:
        p = por_prioridad.setdefault(caso["prioridad"] or "Sin prioridad", {"planificados": 0, "pasaron": 0, "fallaron": 0, "bloqueados": 0})
        p["planificados"] += 1
        r = _resultado_de(caso)[0]
        p["pasaron" if r == "PASÓ" else "fallaron" if r == "FALLÓ" else "bloqueados"] += 1

    md = [NOTA_EJEMPLO.rstrip(), "", f"# Reporte del ciclo · {app['nombre']}", "", "## Resumen ejecutivo", "",
          f"Se probaron los cinco requisitos funcionales de {app['nombre']} ({app['url']}) con {len(casos)} casos "
          f"aprobados por la persona: {resultados.get('pasaron', 0)} pasaron, {resultados.get('fallaron', 0)} fallaron"
          + (f" y {resultados.get('bloqueados', 0)} quedaron bloqueados" if resultados.get("bloqueados") else "") + ". "
          f"La persona confirmó {len(confirmados)} defecto(s) y descartó {len(descartados)}. "
          f"Recomendación: {semaforo.split(' ', 1)[1].lower()}.", "",
          "## Semáforo de la versión", "", f"**{semaforo}** — regla aplicada: {regla}.", "",
          "## Cobertura", "",
          "| Prioridad | Planificados | Pasaron | Fallaron | Bloqueados |", "|---|---|---|---|---|"]
    for prioridad in ("Alta", "Media", "Baja"):
        if prioridad in por_prioridad:
            p = por_prioridad[prioridad]
            md.append(f"| {prioridad} | {p['planificados']} | {p['pasaron']} | {p['fallaron']} | {p['bloqueados']} |")
    for prioridad, p in por_prioridad.items():
        if prioridad not in ("Alta", "Media", "Baja"):
            md.append(f"| {prioridad} | {p['planificados']} | {p['pasaron']} | {p['fallaron']} | {p['bloqueados']} |")
    md += ["", "## Defectos confirmados", ""]
    if confirmados:
        md += ["| ID | Título | Severidad | Casos | Evidencia |", "|---|---|---|---|---|"]
        for d in confirmados:
            md.append(f"| {d['id']} | {d['titulo']} | {d['severidad']} | {d['casos']} | {d['evidencia']} |")
    else:
        md.append("Ninguno.")
    md += ["", "## Defectos descartados", ""]
    if descartados:
        for d in descartados:
            md.append(f"- {d['id']} · {d['titulo']} — motivo: {d['motivo'] or 'sin motivo registrado'}")
    else:
        md.append("Ninguno.")
    md += ["", "## Métricas del ciclo", "",
           f"- Casos generados por el agente: {comparacion.get('generados', len(casos))}",
           f"- Casos aceptados sin edición: {len(comparacion.get('aceptados', []))} "
           f"({comparacion.get('porcentaje_aceptados', 0)}%) · editados: {len(comparacion.get('editados', []))} · "
           f"rechazados: {len(comparacion.get('rechazados', []))} · añadidos por la persona: {len(comparacion.get('anadidos', []))}",
           "- Pruebas que el agente tuvo que corregir por localizador o espera: 0",
           f"- Fin del ciclo: {estado.ahora()} (inicio: ver la hora de qa/exploracion.md)", "",
           "## Las pruebas quedan en el repositorio", "",
           "Las pruebas de `tests/` corren sin el agente: `npx playwright test`. "
           "El reporte HTML de la última ejecución se abre con `npx playwright show-report qa/reporte-html`.", "",
           "## Próximos pasos", ""]
    if confirmados:
        md.append(f"1. Corregir {', '.join(d['id'] for d in confirmados)} y volver a correr solo esos casos: "
                  f"`npx playwright test -g \"{'|'.join(c.strip() for d in confirmados for c in d['casos'].split(','))}\"`.")
    md += ["2. Añadir al plan el caso del botón «Add to cart» que no responde con problem_user, observado en la exploración.",
           "3. Incluir `performance_glitch_user` en el próximo ciclo para medir tiempos de carga.", ""]
    return "\n".join(md)


# ---------------------------------------------------------------- ejecución

async def _reproducir(guion: list[tuple[float, dict]], publicar: Callable[[dict], dict]) -> None:
    for retraso, evento in guion:
        await asyncio.sleep(retraso * VELOCIDAD)
        publicar(evento)


def _saludo() -> str:
    """La presentación de la skill /inicio, en su variante para la interfaz web (ver .claude/skills/inicio/SKILL.md)."""
    return (
        "👋 Hola, soy el **Agente Virtual de QA**.\n\n"
        "Pruebo aplicaciones web de principio a fin en cinco pasos:\n\n"
        "1. **Entiendo** la aplicación navegándola\n"
        "2. **Diseño** el plan de pruebas, a partir de los requisitos o de una historia de usuario · *tú apruebas el plan*\n"
        "3. **Ejecuto** las pruebas con Playwright\n"
        "4. **Analizo** los fallos y documento los defectos · *tú confirmas cada defecto*\n"
        "5. **Reporto** el estado de la versión\n\n"
        "Cada paso lo inicias tú con el botón de abajo; yo nunca salto al siguiente por mi cuenta. Todo lo que produzco "
        "queda como archivos en `qa/` y `tests/`, aparece en esta conversación, y las pruebas siguen funcionando sin mí.\n\n"
        "Abajo, en «¿Qué sigue?», tienes siempre el siguiente paso."
    )


async def correr(paso: str | None, prompt: str, publicar: Callable[[dict], dict]) -> str:
    """Ejecuta un paso del ciclo en modo demo y devuelve el resumen final del «agente»."""
    app = estado.aplicacion()
    publicar({"tipo": "sistema", "texto": "Modo demo: ciclo de ejemplo, sin llamadas a la API ni navegador."})

    if paso == "inicio":
        await asyncio.sleep(0.6 * VELOCIDAD)
        return _saludo()

    if paso is None:
        await asyncio.sleep(0.6 * VELOCIDAD)
        if prompt.strip().startswith("/inicio") or prompt.strip().lower() in ("hola", "hola!", "¿qué haces?", "que haces"):
            return _saludo()
        return ("En modo demo solo ejecuto los cinco pasos del ciclo desde los botones de la interfaz. "
                "Para conversar con el agente real, arranca la aplicación sin `--demo`.")

    await _reproducir(_guion(paso, app), publicar)

    if paso == "explorar-app":
        _copiar(CICLO / "qa" / "exploracion.md", estado.DOCUMENTOS["exploracion"])
        return ("Exploré Swag Labs con standard_user y problem_user: 7 pantallas, 3 flujos de inicio de sesión, catálogo, "
                "carrito y checkout completo.\n"
                "Todos los controles tienen atributo `data-test`; los localizadores quedaron en `qa/exploracion.md`.\n"
                "Con problem_user vi tres cosas distintas: la misma imagen en los seis productos, el selector de orden sin "
                "efecto y el campo Apellido del checkout que no conserva el texto.\n"
                "Las dejé como «por verificar en el paso 3», no como defectos.\n"
                "Siguiente paso: /disenar-plan")

    if paso == "disenar-plan":
        historia = estado.historia_info()
        if historia["existe"]:
            publicar({"tipo": "herramienta", "nombre": "Read", "resumen": "Lee qa/historia-de-usuario.md"})
            texto = generar_plan_desde_historia()
            estado.escribir("plan", texto)
            estado.escribir("plan-generado", texto)
        else:
            texto = (CICLO / "qa" / "plan-de-pruebas.md").read_text(encoding="utf-8")
            texto = texto.replace("\n", "\n\n" + NOTA_EJEMPLO.rstrip() + "\n", 1) if texto.startswith("# ") else NOTA_EJEMPLO + texto
            estado.escribir("plan", texto)
            estado.escribir("plan-generado", texto)
        casos = estado.plan_info()["casos"]
        tabla = "\n".join(f"| {c['id']} | {c['titulo']} | {c['prioridad']} | {c['usuario']} |" for c in casos)
        origen = (f"Partí de la historia de usuario «{historia['titulo']}» y de sus {historia['criterios']} criterios de aceptación"
                  if historia["existe"] else "Partí de los requisitos y de la exploración")
        return (f"{origen}. Diseñé {len(casos)} casos de prueba:\n\n| ID | Título | Prioridad | Usuario |\n|---|---|---|---|\n{tabla}\n\n"
                "¿Apruebas el plan? Puedes quitar casos o editar el texto antes de continuar. Nada se ejecuta hasta que apruebes.")

    if paso == "ejecutar-pruebas":
        plan = estado.plan_info()
        if not plan["aprobado"]:
            return "El plan no dice `Estado: APROBADO`. Apruébalo antes de ejecutar las pruebas."
        for ruta in sorted((CICLO / "tests").glob("*.spec.ts")):
            _copiar(ruta, estado.TESTS / ruta.name)
        casos = plan["casos"]
        salida = _salida_playwright(casos)
        await asyncio.sleep(1.2 * VELOCIDAD)
        publicar({"tipo": "salida", "nombre": "Bash", "ok": not any(_resultado_de(c)[0] == "FALLÓ" for c in casos), "texto": salida})
        for caso in casos:
            if _resultado_de(caso)[0] == "FALLÓ" and caso["id"] in ERRORES:
                carpeta = ERRORES[caso["id"]]["evidencia"]
                _copiar(CICLO / carpeta, estado.RAIZ / carpeta)
        estado.escribir("resultados", generar_resultados(casos, salida))
        publicar({"tipo": "herramienta", "nombre": "Write", "resumen": "Escribe qa/resultados.md"})
        pasaron = sum(_resultado_de(c)[0] == "PASÓ" for c in casos)
        fallaron = sum(_resultado_de(c)[0] == "FALLÓ" for c in casos)
        return (f"Ejecuté {len(casos)} casos: {pasaron} pasaron y {fallaron} fallaron"
                + (" (los dos con problem_user, como anticipaba la exploración)" if fallaron == 2 else "") + ". "
                "La evidencia de cada fallo quedó en `qa/evidencia/` y los resultados en `qa/resultados.md`. "
                "Reporte HTML: `npx playwright show-report qa/reporte-html`.\nSiguiente paso: /analizar-fallos")

    if paso == "analizar-fallos":
        casos = estado.plan_info()["casos"]
        creados = generar_defectos(casos)
        if not creados:
            return "No hubo pruebas fallidas en este ciclo; dejé la nota en `qa/defectos/README.md`.\nSiguiente paso: /reportar"
        lineas = "\n".join(f"- {d['id']} · {d['titulo']} · {d['severidad']}" for d in estado.defectos_info()["lista"])
        return (f"Documenté {len(creados)} defecto(s) con evidencia:\n\n{lineas}\n\n"
                "¿Confirmas estos defectos? Marca `Estado: CONFIRMADO` o `Estado: DESCARTADO` en cada archivo (o dímelo aquí) y ejecuta /reportar")

    if paso == "reportar":
        defectos = estado.defectos_info()
        if defectos["pendientes"]:
            return f"Hay {defectos['pendientes']} defecto(s) pendientes de confirmación. Decide cada uno antes del reporte."
        estado.escribir("reporte", generar_reporte())
        info = estado.reporte_info()
        semaforo = {"rojo": "🔴 No publicar", "amarillo": "🟡 Publicar con riesgo conocido", "verde": "🟢 Publicar"}.get(info["semaforo"] or "", "")
        comp = estado.comparar_planes() or {}
        return (f"Reporte listo en `qa/reporte.md`. Semáforo: **{semaforo}**. "
                f"Defectos confirmados: {defectos['confirmados']}; descartados: {defectos['descartados']}. "
                f"Casos aceptados sin edición: {len(comp.get('aceptados', []))} de {comp.get('generados', 0)} "
                f"({comp.get('porcentaje_aceptados', 0)}%). Las pruebas quedan en `tests/` y corren con `npx playwright test`.")

    return "Paso desconocido."
