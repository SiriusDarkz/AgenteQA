"""API y servidor web del MVP del Agente Virtual de QA.

Arranque: python3 -m app [--demo] [--puerto 8765]
Todo lo que la interfaz muestra sale de los archivos de qa/ y tests/ (ver estado.py);
los pasos corren en segundo plano (agente.py) y su actividad llega por SSE (/api/eventos).
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agente, estado

MODO = os.environ.get("QA_MODO", "sdk")
UI = Path(__file__).resolve().parent / "ui"

app = FastAPI(title="Agente Virtual de QA", docs_url="/api/docs", redoc_url=None)
bus = agente.Bus()
corredor = agente.Corredor(MODO, bus)


def _estado() -> dict:
    datos = estado.estado(corredor.actual["paso"] if corredor.ocupado and corredor.actual else None)
    datos["modo"] = MODO
    datos["agente"] = {
        "ocupado": corredor.ocupado,
        "actual": corredor.actual if corredor.ocupado else None,
        "ultimo": corredor.ultimo,
    }
    datos["presentacion"] = corredor.presentacion_actual()
    return datos


# ---------------------------------------------------------------- modelos

class Markdown(BaseModel):
    markdown: str


class Aprobacion(BaseModel):
    markdown: str | None = None
    excluir: list[str] = []


class EstadoDefecto(BaseModel):
    estado: str
    motivo: str = ""


class Paso(BaseModel):
    argumentos: str = ""


class Mensaje(BaseModel):
    prompt: str


class Historia(BaseModel):
    titulo: str = ""
    texto: str = ""
    criterios: list[str] = []


# ---------------------------------------------------------------- páginas y estáticos

@app.get("/", include_in_schema=False)
async def inicio() -> FileResponse:
    return FileResponse(UI / "index.html")


app.mount("/ui", StaticFiles(directory=UI), name="ui")


@app.middleware("http")
async def sin_cache_en_la_interfaz(request: Request, call_next):
    """La página y sus archivos (/ui/*) se revalidan en cada carga: tras actualizar el código basta con recargar."""
    respuesta = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/ui/"):
        respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta

# Las capturas de qa/evidencia/ se sirven tal cual; la carpeta puede no existir hasta la primera ejecución.
estado.EVIDENCIA.mkdir(parents=True, exist_ok=True)
app.mount("/evidencia", StaticFiles(directory=estado.EVIDENCIA, check_dir=False), name="evidencia")


@app.get("/reporte-html/{ruta:path}", include_in_schema=False)
async def reporte_html(ruta: str):
    base = estado.REPORTE_HTML
    if not (base / "index.html").exists():
        return HTMLResponse("<p>Todavía no hay reporte HTML de Playwright: ejecuta primero las pruebas.</p>", status_code=404)
    objetivo = (base / (ruta or "index.html")).resolve()
    if base.resolve() not in objetivo.parents and objetivo != base.resolve():
        raise HTTPException(404)
    if objetivo.is_dir():
        objetivo = objetivo / "index.html"
    if not objetivo.exists():
        raise HTTPException(404)
    return FileResponse(objetivo)


# ---------------------------------------------------------------- estado y documentos

@app.get("/api/estado")
async def api_estado() -> dict:
    return _estado()


@app.get("/api/documento/{nombre}")
async def api_documento(nombre: str) -> dict:
    if nombre not in estado.DOCUMENTOS:
        raise HTTPException(404, "Documento desconocido")
    texto = estado.leer(nombre)
    return {"nombre": nombre, "existe": texto is not None, "markdown": texto or "",
            "ruta": estado.relativa(estado.DOCUMENTOS[nombre])}


@app.put("/api/documento/{nombre}")
async def api_guardar_documento(nombre: str, cuerpo: Markdown) -> dict:
    if nombre not in ("requisitos", "plan", "historia"):
        raise HTTPException(400, "Solo se editan los requisitos, la historia de usuario y el plan desde la interfaz")
    if nombre == "plan":
        estado.guardar_plan(cuerpo.markdown)
    else:
        estado.escribir(nombre, cuerpo.markdown.rstrip() + "\n")
    bus.publicar({"tipo": "estado"})
    return await api_documento(nombre)


# ---------------------------------------------------------------- historia de usuario (entrada opcional del plan)

@app.post("/api/historia")
async def api_guardar_historia(cuerpo: Historia) -> dict:
    if not (cuerpo.texto.strip() or any(c.strip() for c in cuerpo.criterios)):
        raise HTTPException(400, "Escribe la historia o al menos un criterio de aceptación")
    info = estado.guardar_historia(cuerpo.titulo, cuerpo.texto, cuerpo.criterios)
    bus.publicar({"tipo": "decision", "texto": f"Historia de usuario guardada: {info['titulo']} ({info['criterios']} criterios). El plan partirá de ella."})
    bus.publicar({"tipo": "estado"})
    return info


@app.delete("/api/historia")
async def api_borrar_historia() -> dict:
    estado.borrar_historia()
    bus.publicar({"tipo": "estado"})
    return {"existe": False}


@app.get("/api/documento/{nombre}/descargar")
async def api_descargar(nombre: str) -> FileResponse:
    if nombre not in estado.DOCUMENTOS or not estado.DOCUMENTOS[nombre].exists():
        raise HTTPException(404)
    return FileResponse(estado.DOCUMENTOS[nombre], media_type="text/markdown",
                        filename=estado.DOCUMENTOS[nombre].name)


# ---------------------------------------------------------------- plan (decisión 1)

@app.post("/api/plan/aprobar")
async def api_aprobar_plan(cuerpo: Aprobacion) -> dict:
    try:
        plan = estado.aprobar_plan(cuerpo.markdown, cuerpo.excluir)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    bus.publicar({"tipo": "decision", "texto": f"Plan aprobado desde la interfaz con {len(plan['casos'])} casos."})
    bus.publicar({"tipo": "estado"})
    return {"plan": {k: v for k, v in plan.items() if k != "casos"}, "casos": plan["casos"]}


@app.post("/api/plan/desaprobar")
async def api_desaprobar_plan() -> dict:
    plan = estado.desaprobar_plan()
    bus.publicar({"tipo": "estado"})
    return {"plan": {k: v for k, v in plan.items() if k != "casos"}, "casos": plan["casos"]}


# ---------------------------------------------------------------- defectos (decisión 2)

@app.get("/api/defectos")
async def api_defectos() -> dict:
    return estado.defectos_info()


@app.get("/api/defectos/{id_defecto}")
async def api_defecto(id_defecto: str) -> dict:
    for d in estado.defectos_info()["lista"]:
        if d["id"] == id_defecto:
            return d
    raise HTTPException(404)


@app.post("/api/defectos/{id_defecto}/estado")
async def api_estado_defecto(id_defecto: str, cuerpo: EstadoDefecto) -> dict:
    try:
        defecto = estado.cambiar_estado_defecto(id_defecto, cuerpo.estado, cuerpo.motivo)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    bus.publicar({"tipo": "decision", "texto": f"{id_defecto} marcado como {defecto['estado']} desde la interfaz"
                  + (f": {cuerpo.motivo}" if cuerpo.motivo else ".")})
    bus.publicar({"tipo": "estado"})
    return defecto


# ---------------------------------------------------------------- pruebas

@app.get("/api/pruebas")
async def api_pruebas() -> dict:
    return {"pruebas": estado.pruebas()}


# ---------------------------------------------------------------- el agente

@app.post("/api/pasos/{paso}")
async def api_correr_paso(paso: str, cuerpo: Paso | None = None) -> JSONResponse:
    if paso not in estado.IDS_PASOS:
        raise HTTPException(404, "Paso desconocido")
    est = estado.estado()
    info = next(p for p in est["pasos"] if p["id"] == paso)
    if corredor.ocupado:
        raise HTTPException(409, "El agente ya está trabajando; espera a que termine o cancélalo.")
    if not info["disponible"]:
        raise HTTPException(409, f"El paso {info['numero']} todavía no está disponible: falta lo anterior o una decisión tuya.")
    argumentos = (cuerpo.argumentos if cuerpo else "").strip()
    if paso == "explorar-app" and not argumentos:
        argumentos = est["aplicacion"]["url"]
    if paso == "disenar-plan" and not argumentos and est["historia"]["existe"]:
        argumentos = "a partir de la historia de usuario de qa/historia-de-usuario.md"
    prompt = f"{info['comando']} {argumentos}".strip()
    corredor.iniciar(paso, prompt)
    return JSONResponse({"ok": True, "paso": paso, "prompt": prompt}, status_code=202)


@app.post("/api/presentacion")
async def api_presentacion() -> JSONResponse:
    """El agente se presenta (skill /inicio). La interfaz lo pide al abrirse si no hay una presentación guardada."""
    if corredor.ocupado:
        raise HTTPException(409, "El agente ya está trabajando; espera a que termine o cancélalo.")
    corredor.iniciar("inicio", agente.PROMPT_PRESENTACION)
    return JSONResponse({"ok": True, "paso": "inicio", "prompt": agente.PROMPT_PRESENTACION}, status_code=202)


@app.post("/api/agente/mensaje")
async def api_mensaje(cuerpo: Mensaje) -> JSONResponse:
    prompt = cuerpo.prompt.strip()
    if not prompt:
        raise HTTPException(400, "Mensaje vacío")
    if corredor.ocupado:
        raise HTTPException(409, "El agente ya está trabajando; espera a que termine o cancélalo.")
    if prompt == "/inicio":
        prompt = agente.PROMPT_PRESENTACION  # desde la interfaz, la variante con botones en vez de comandos
    paso = next((p for p in estado.IDS_PASOS if prompt.startswith("/" + p)), None)
    if paso:
        # Un comando escrito a mano sigue las mismas reglas que el botón: respeta el orden y las decisiones.
        info = next(p for p in estado.estado()["pasos"] if p["id"] == paso)
        if not info["disponible"]:
            raise HTTPException(409, f"El paso {info['numero']} todavía no está disponible: falta lo anterior o una decisión tuya.")
    elif len(prompt) > 2000:
        raise HTTPException(400, "El mensaje es demasiado largo (máximo 2000 caracteres).")
    corredor.iniciar(paso, prompt)
    return JSONResponse({"ok": True, "paso": paso, "prompt": prompt}, status_code=202)


@app.post("/api/agente/cancelar")
async def api_cancelar() -> dict:
    return {"cancelado": await corredor.cancelar()}


@app.get("/api/eventos")
async def api_eventos(request: Request) -> StreamingResponse:
    """Actividad del agente en vivo (SSE). Primero el historial reciente, luego lo nuevo."""

    async def flujo():
        cola = bus.suscribir()
        try:
            for evento in list(bus.historial):
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
            yield "event: listo\ndata: {}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    evento = await asyncio.wait_for(cola.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": latido\n\n"
                    continue
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
        finally:
            bus.cancelar(cola)

    return StreamingResponse(flujo(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------------------------------------------------------- ciclo

@app.post("/api/ciclo/reiniciar")
async def api_reiniciar() -> dict:
    if corredor.ocupado:
        raise HTTPException(409, "El agente está trabajando; cancélalo antes de reiniciar el ciclo.")
    resultado = estado.reiniciar_ciclo()
    bus.historial.clear()
    bus.publicar({"tipo": "sistema", "texto": "Ciclo reiniciado desde la interfaz"
                  + (f"; el anterior quedó en {resultado['archivado_en']}." if resultado["archivado_en"] else ".")})
    bus.publicar({"tipo": "estado"})
    return resultado


@app.get("/api/salud", response_class=PlainTextResponse)
async def api_salud() -> str:
    return f"ok · modo {MODO} · repo {estado.RAIZ}"
