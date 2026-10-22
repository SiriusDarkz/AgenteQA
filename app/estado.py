"""Estado del ciclo de QA, derivado de los archivos de qa/ y tests/.

La interfaz no tiene estado propio: todo lo que muestra sale de los archivos que
dejan las skills del agente, y las dos decisiones humanas (aprobar el plan y
confirmar cada defecto) se escriben en esos mismos archivos, igual que si la
persona los editara a mano desde Claude Code.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import shutil
from pathlib import Path

RAIZ = Path(os.environ.get("QA_REPO") or Path(__file__).resolve().parents[1])
QA = RAIZ / "qa"
TESTS = RAIZ / "tests"
DEFECTOS = QA / "defectos"
EVIDENCIA = QA / "evidencia"
REPORTE_HTML = QA / "reporte-html"
HISTORIAL = QA / "historial"

DOCUMENTOS = {
    "requisitos": QA / "requisitos.md",
    "historia": QA / "historia-de-usuario.md",
    "exploracion": QA / "exploracion.md",
    "plan": QA / "plan-de-pruebas.md",
    "plan-generado": QA / "plan-de-pruebas.generado.md",
    "resultados": QA / "resultados.md",
    "reporte": QA / "reporte.md",
}

# Los cinco pasos del ciclo, en el orden de la diapositiva 5 del caso de negocio.
PASOS = [
    {"id": "explorar-app", "numero": 1, "nombre": "Entiende", "accion": "Explorar la aplicación",
     "comando": "/explorar-app", "descripcion": "Navega la aplicación y documenta pantallas, flujos y elementos.",
     "salida": "qa/exploracion.md", "decision": None},
    {"id": "disenar-plan", "numero": 2, "nombre": "Diseña", "accion": "Diseñar el plan",
     "comando": "/disenar-plan", "descripcion": "Propone el plan y los casos de prueba.",
     "salida": "qa/plan-de-pruebas.md", "decision": "Tú apruebas el plan"},
    {"id": "ejecutar-pruebas", "numero": 3, "nombre": "Ejecuta", "accion": "Ejecutar las pruebas",
     "comando": "/ejecutar-pruebas", "descripcion": "Convierte el plan en pruebas de Playwright y las corre.",
     "salida": "tests/*.spec.ts · qa/resultados.md", "decision": None},
    {"id": "analizar-fallos", "numero": 4, "nombre": "Analiza", "accion": "Analizar los fallos",
     "comando": "/analizar-fallos", "descripcion": "Clasifica cada fallo y documenta los defectos con evidencia.",
     "salida": "qa/defectos/DEF-*.md", "decision": "Tú confirmas cada defecto"},
    {"id": "reportar", "numero": 5, "nombre": "Reporta", "accion": "Generar el reporte",
     "comando": "/reportar", "descripcion": "Semáforo de la versión, defectos confirmados y métricas del ciclo.",
     "salida": "qa/reporte.md", "decision": None},
]
IDS_PASOS = [p["id"] for p in PASOS]

ESTADOS_DEFECTO = ("PENDIENTE DE CONFIRMACIÓN", "CONFIRMADO", "DESCARTADO")


# ---------------------------------------------------------------- utilidades

def ahora() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def leer(nombre: str) -> str | None:
    ruta = DOCUMENTOS[nombre]
    return ruta.read_text(encoding="utf-8") if ruta.exists() else None


def escribir(nombre: str, texto: str) -> None:
    ruta = DOCUMENTOS[nombre]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def relativa(ruta: Path) -> str:
    try:
        return str(ruta.relative_to(RAIZ))
    except ValueError:
        return str(ruta)


def _mtime(ruta: Path) -> str | None:
    if not ruta.exists():
        return None
    return dt.datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- aplicación

def aplicacion() -> dict:
    texto = leer("requisitos") or ""
    nombre = re.search(r"^- Aplicación:\s*(.+)$", texto, re.M)
    url = re.search(r"^- URL:\s*(\S+)", texto, re.M)
    return {
        "nombre": nombre.group(1).strip() if nombre else "Aplicación sin nombre",
        "url": url.group(1).strip() if url else "",
        "requisitos_existen": bool(texto),
    }


# ---------------------------------------------------------------- historia de usuario

def historia_info() -> dict:
    """La historia de usuario (opcional) de la que puede partir el plan."""
    texto = leer("historia")
    if texto is None:
        return {"existe": False}
    titulo = re.search(r"^#\s*(.+)$", texto, re.M)
    criterios = [l.strip()[1:].strip() for l in texto.splitlines() if re.match(r"^\s*[-*]\s+\S", l)]
    return {"existe": True, "titulo": titulo.group(1).strip() if titulo else (texto.strip().splitlines() or ["Historia de usuario"])[0][:80],
            "criterios": len(criterios), "modificado": _mtime(DOCUMENTOS["historia"])}


def guardar_historia(titulo: str, texto: str, criterios: list[str]) -> dict:
    """Guarda la historia en qa/historia-de-usuario.md con el formato que lee la skill disenar-plan."""
    lineas = [f"# {titulo.strip() or 'Historia de usuario'}", "", texto.strip(), ""]
    limpios = [c.strip() for c in criterios if c.strip()]
    if limpios:
        lineas += ["## Criterios de aceptación", ""] + [f"- {c}" for c in limpios] + [""]
    escribir("historia", "\n".join(lineas))
    return historia_info()


def borrar_historia() -> None:
    if DOCUMENTOS["historia"].exists():
        DOCUMENTOS["historia"].unlink()


def criterios_de_historia() -> list[str]:
    texto = leer("historia") or ""
    return [l.strip()[1:].strip() for l in texto.splitlines() if re.match(r"^\s*[-*]\s+\S", l)]


# ---------------------------------------------------------------- plan

ENCABEZADO_CASOS = ["id", "titulo", "prioridad", "usuario", "precondicion", "pasos", "resultado"]


def _fila_caso(linea: str) -> dict | None:
    """Convierte una fila `| CP-01 | ... |` de la tabla del plan en un dict."""
    if not re.match(r"^\|\s*CP-\d+", linea):
        return None
    celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
    if len(celdas) < 3:
        return None
    celdas += [""] * (len(ENCABEZADO_CASOS) - len(celdas))
    return dict(zip(ENCABEZADO_CASOS, celdas[: len(ENCABEZADO_CASOS)]))


def casos_de(texto: str | None) -> list[dict]:
    if not texto:
        return []
    casos = []
    for linea in texto.splitlines():
        fila = _fila_caso(linea)
        if fila:
            casos.append(fila)
    return casos


def _linea_estado(texto: str) -> str | None:
    for linea in reversed(texto.strip().splitlines()):
        if linea.strip():
            return linea.strip()
    return None


def plan_info() -> dict:
    texto = leer("plan")
    if texto is None:
        return {"existe": False, "aprobado": False, "casos": [], "por_prioridad": {}}
    ultima = _linea_estado(texto) or ""
    casos = casos_de(texto)
    por_prioridad: dict[str, int] = {}
    for c in casos:
        por_prioridad[c["prioridad"] or "Sin prioridad"] = por_prioridad.get(c["prioridad"] or "Sin prioridad", 0) + 1
    aprobado = ultima.upper().startswith("ESTADO: APROBADO")
    return {
        "existe": True,
        "aprobado": aprobado,
        "estado": ultima,
        "casos": casos,
        "por_prioridad": por_prioridad,
        "generado_existe": DOCUMENTOS["plan-generado"].exists(),
        "modificado": _mtime(DOCUMENTOS["plan"]),
        "comparacion": comparar_planes() if aprobado else None,
    }


def comparar_planes() -> dict | None:
    """Métrica del hito 1: casos aceptados sin edición (plan aprobado vs. generado)."""
    generado = casos_de(leer("plan-generado"))
    aprobado = casos_de(leer("plan"))
    if not generado:
        return None
    gen = {c["id"]: c for c in generado}
    apr = {c["id"]: c for c in aprobado}
    aceptados = [i for i in gen if i in apr and apr[i] == gen[i]]
    editados = [i for i in gen if i in apr and apr[i] != gen[i]]
    rechazados = [i for i in gen if i not in apr]
    anadidos = [i for i in apr if i not in gen]
    return {
        "generados": len(gen),
        "aceptados": aceptados,
        "editados": editados,
        "rechazados": rechazados,
        "anadidos": anadidos,
        "porcentaje_aceptados": round(100 * len(aceptados) / len(gen)) if gen else 0,
    }


def guardar_plan(markdown: str) -> dict:
    escribir("plan", markdown.rstrip() + "\n")
    return plan_info()


def aprobar_plan(markdown: str | None = None, excluir: list[str] | None = None) -> dict:
    texto = markdown if markdown is not None else leer("plan")
    if texto is None:
        raise FileNotFoundError("No hay plan que aprobar; ejecuta primero el paso 2.")
    excluir = set(excluir or [])
    lineas = [l for l in texto.rstrip().splitlines()
              if not (excluir and (fila := _fila_caso(l)) and fila["id"] in excluir)]
    # Quita la línea de estado anterior (y una marca de aprobación previa) y escribe la nueva.
    while lineas and (lineas[-1].strip() == "" or lineas[-1].strip().upper().startswith("ESTADO:")
                      or lineas[-1].startswith("Aprobado desde la interfaz")):
        lineas.pop()
    lineas += ["", f"Aprobado desde la interfaz el {ahora()}", "Estado: APROBADO"]
    escribir("plan", "\n".join(lineas) + "\n")
    return plan_info()


def desaprobar_plan() -> dict:
    texto = leer("plan")
    if texto is None:
        return plan_info()
    lineas = texto.rstrip().splitlines()
    while lineas and (lineas[-1].strip() == "" or lineas[-1].strip().upper().startswith("ESTADO:")
                      or lineas[-1].startswith("Aprobado desde la interfaz")):
        lineas.pop()
    lineas += ["", "Estado: PENDIENTE DE APROBACIÓN"]
    escribir("plan", "\n".join(lineas) + "\n")
    return plan_info()


# ---------------------------------------------------------------- resultados

def resultados_info() -> dict:
    texto = leer("resultados")
    if texto is None:
        return {"existe": False}
    filas = []
    for linea in texto.splitlines():
        fila = _fila_caso(linea)
        if not fila:
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        resultado = next((c for c in celdas if c.upper() in ("PASÓ", "PASO", "FALLÓ", "FALLO", "BLOQUEADO")), "")
        filas.append({"id": celdas[0], "titulo": celdas[1] if len(celdas) > 1 else "",
                      "resultado": resultado.upper().replace("PASO", "PASÓ").replace("FALLO", "FALLÓ")})
    conteo = {"pasaron": sum(f["resultado"] == "PASÓ" for f in filas),
              "fallaron": sum(f["resultado"] == "FALLÓ" for f in filas),
              "bloqueados": sum(f["resultado"] == "BLOQUEADO" for f in filas),
              "ejecutados": len(filas)}
    return {"existe": True, "filas": filas, **conteo, "modificado": _mtime(DOCUMENTOS["resultados"]),
            "reporte_html": (REPORTE_HTML / "index.html").exists()}


# ---------------------------------------------------------------- defectos

def _campo(texto: str, nombre: str) -> str:
    m = re.search(rf"^- {re.escape(nombre)}:\s*(.*)$", texto, re.M)
    return m.group(1).strip() if m else ""


def defecto_de(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    titulo = re.search(r"^#\s*(.+)$", texto, re.M)
    estado = _campo(texto, "Estado").upper()
    for e in ESTADOS_DEFECTO:
        if estado.startswith(e):
            estado = e
            break
    else:
        estado = "PENDIENTE DE CONFIRMACIÓN" if not estado else estado
    severidad = _campo(texto, "Severidad")
    nivel = next((n for n in ("Crítica", "Alta", "Media", "Baja") if severidad.startswith(n)), severidad)
    evidencia = _campo(texto, "Evidencia")
    capturas = [c.strip() for c in re.findall(r"(qa/evidencia/[^\s·|)]+\.(?:png|jpg|jpeg))", texto)]
    return {
        "id": ruta.stem,
        "archivo": relativa(ruta),
        "titulo": re.sub(r"^DEF-\d+\s*·\s*", "", titulo.group(1).strip()) if titulo else ruta.stem,
        "severidad": nivel,
        "severidad_detalle": severidad,
        "casos": _campo(texto, "Casos de prueba"),
        "estado": estado,
        "motivo": _campo(texto, "Motivo"),
        "resultado_esperado": _campo(texto, "Resultado esperado"),
        "resultado_obtenido": _campo(texto, "Resultado obtenido"),
        "evidencia": evidencia,
        "capturas": capturas,
        "markdown": texto,
    }


def defectos_info() -> dict:
    if not DEFECTOS.exists():
        return {"existe": False, "lista": [], "pendientes": 0, "confirmados": 0, "descartados": 0, "sin_defectos": False}
    lista = [defecto_de(r) for r in sorted(DEFECTOS.glob("DEF-*.md"))]
    sin_defectos = not lista and (DEFECTOS / "README.md").exists()
    return {
        "existe": bool(lista) or sin_defectos,
        "lista": lista,
        "pendientes": sum(d["estado"] == "PENDIENTE DE CONFIRMACIÓN" for d in lista),
        "confirmados": sum(d["estado"] == "CONFIRMADO" for d in lista),
        "descartados": sum(d["estado"] == "DESCARTADO" for d in lista),
        "sin_defectos": sin_defectos,
        "nota": (DEFECTOS / "README.md").read_text(encoding="utf-8") if sin_defectos else None,
    }


def cambiar_estado_defecto(id_defecto: str, estado: str, motivo: str = "") -> dict:
    estado = estado.upper().strip()
    if estado not in ESTADOS_DEFECTO:
        raise ValueError(f"Estado no válido: {estado}")
    ruta = DEFECTOS / f"{id_defecto}.md"
    if not ruta.exists() or not re.fullmatch(r"DEF-\d+", id_defecto):
        raise FileNotFoundError(f"No existe el defecto {id_defecto}")
    texto = ruta.read_text(encoding="utf-8")
    texto = re.sub(r"^- Motivo:.*\n?", "", texto, flags=re.M)
    texto = re.sub(r"^- Decidido desde la interfaz:.*\n?", "", texto, flags=re.M)
    nueva = f"- Estado: {estado}"
    if motivo.strip():
        nueva += f"\n- Motivo: {motivo.strip()}"
    if estado != "PENDIENTE DE CONFIRMACIÓN":
        nueva += f"\n- Decidido desde la interfaz: {ahora()}"
    if re.search(r"^- Estado:.*$", texto, re.M):
        texto = re.sub(r"^- Estado:.*$", nueva, texto, count=1, flags=re.M)
    else:
        texto = texto.rstrip() + "\n" + nueva + "\n"
    ruta.write_text(texto, encoding="utf-8")
    return defecto_de(ruta)


# ---------------------------------------------------------------- reporte

def reporte_info() -> dict:
    texto = leer("reporte")
    if texto is None:
        return {"existe": False}
    semaforo = None
    for simbolo, nombre in (("🔴", "rojo"), ("🟡", "amarillo"), ("🟢", "verde")):
        pos = texto.find(simbolo)
        if pos != -1 and (semaforo is None or pos < semaforo[0]):
            semaforo = (pos, nombre)
    return {"existe": True, "semaforo": semaforo[1] if semaforo else None,
            "modificado": _mtime(DOCUMENTOS["reporte"])}


# ---------------------------------------------------------------- pruebas y evidencia

def pruebas() -> list[dict]:
    salida = []
    if TESTS.exists():
        for ruta in sorted(TESTS.glob("*.spec.ts")):
            salida.append({"archivo": relativa(ruta), "nombre": ruta.name,
                           "contenido": ruta.read_text(encoding="utf-8"),
                           "casos": sorted(set(re.findall(r"\b(CP-\d+)\b", ruta.read_text(encoding="utf-8"))))})
    return salida


def evidencias() -> list[str]:
    if not EVIDENCIA.exists():
        return []
    return [relativa(r) for r in sorted(EVIDENCIA.rglob("*.png"))]


# ---------------------------------------------------------------- estado del ciclo

MARCA_EJEMPLO = "ejemplo del modo demo"


def ciclo_de_ejemplo() -> bool:
    """True si los archivos del ciclo vienen del modo demo (llevan su nota de ejemplo), no de un ciclo real."""
    for nombre in ("exploracion", "plan", "resultados", "reporte"):
        texto = leer(nombre) or ""
        if MARCA_EJEMPLO in texto[:600]:
            return True
    return False


def estado(paso_en_curso: str | None = None) -> dict:
    plan = plan_info()
    resultados = resultados_info()
    defectos = defectos_info()
    reporte = reporte_info()
    exploracion_existe = DOCUMENTOS["exploracion"].exists()

    hechos = {
        "explorar-app": exploracion_existe,
        "disenar-plan": plan["existe"],
        "ejecutar-pruebas": resultados["existe"],
        "analizar-fallos": defectos["existe"],
        "reportar": reporte["existe"],
    }
    decisiones = {
        "disenar-plan": plan["existe"] and not plan["aprobado"],
        "analizar-fallos": defectos["pendientes"] > 0,
    }
    disponibles = {
        "explorar-app": True,
        "disenar-plan": exploracion_existe,
        "ejecutar-pruebas": plan["aprobado"],
        "analizar-fallos": resultados["existe"],
        "reportar": defectos["existe"] and defectos["pendientes"] == 0,
    }
    pasos = []
    for p in PASOS:
        if paso_en_curso == p["id"]:
            est = "en_curso"
        elif decisiones.get(p["id"]):
            est = "decision"
        elif hechos[p["id"]]:
            est = "hecho"
        else:
            est = "pendiente"
        pasos.append({**p, "estado": est, "hecho": hechos[p["id"]], "disponible": disponibles[p["id"]] and not paso_en_curso})

    actual = next((p["id"] for p in pasos if p["estado"] in ("decision", "en_curso")), None) \
        or next((p["id"] for p in pasos if not p["hecho"]), "reportar")

    return {
        "aplicacion": aplicacion(),
        "repo": str(RAIZ),
        "pasos": pasos,
        "paso_actual": actual,
        "paso_en_curso": paso_en_curso,
        "exploracion": {"existe": exploracion_existe, "modificado": _mtime(DOCUMENTOS["exploracion"])},
        "ciclo_ejemplo": ciclo_de_ejemplo(),
        "historia": historia_info(),
        "plan": {k: v for k, v in plan.items() if k != "casos"} | {"n_casos": len(plan["casos"])},
        "casos": plan["casos"],
        "resultados": resultados,
        "defectos": {k: v for k, v in defectos.items() if k != "lista"} | {
            "lista": [{k: v for k, v in d.items() if k != "markdown"} for d in defectos["lista"]]},
        "reporte": reporte,
        "pruebas": [{"archivo": p["archivo"], "nombre": p["nombre"], "casos": p["casos"]} for p in pruebas()],
        "evidencias": evidencias(),
        "historial": sorted((r.name for r in HISTORIAL.iterdir() if r.is_dir()), reverse=True) if HISTORIAL.exists() else [],
    }


def reiniciar_ciclo() -> dict:
    """Archiva el ciclo actual en qa/historial/<fecha>/ y deja el repo listo para otro.

    Conserva qa/requisitos.md, tests/datos.ts y tests/ejemplo.spec.ts.
    """
    sello = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = HISTORIAL / sello
    movidos: list[str] = []

    def mover(ruta: Path) -> None:
        if ruta.exists():
            objetivo = destino / relativa(ruta)
            objetivo.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(ruta), str(objetivo))
            movidos.append(relativa(ruta))

    for nombre in ("exploracion", "plan", "plan-generado", "resultados", "reporte", "historia"):
        mover(DOCUMENTOS[nombre])
    for carpeta in (DEFECTOS, EVIDENCIA, REPORTE_HTML, RAIZ / "test-results"):
        mover(carpeta)
    if TESTS.exists():
        for ruta in TESTS.glob("*.spec.ts"):
            if ruta.name != "ejemplo.spec.ts":
                mover(ruta)
    return {"archivado_en": relativa(destino) if movidos else None, "movidos": movidos}
