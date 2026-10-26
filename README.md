# Agente Virtual de QA

Un agente de inteligencia artificial que prueba una aplicación web de principio a fin y deja todo su trabajo como archivos en este repositorio. Trabaja en cinco pasos: **entiende** la aplicación, **diseña** el plan de pruebas, **ejecuta** las pruebas, **analiza** los fallos y **escribe** el reporte. Una persona toma dos decisiones en el camino: aprueba el plan y confirma cada defecto que el agente encuentra.

Las pruebas que genera son de [Playwright](https://playwright.dev) y siguen funcionando aunque se apague el agente. Viene configurado para probar [Swag Labs](https://www.saucedemo.com), una tienda de demostración pública con errores a propósito, así que la demo siempre encuentra algo.

Prototipo (MVP) del proyecto capstone de la Maestría en Ciencias de Datos e Inteligencia Artificial (UASD). El caso de negocio, el canvas y la presentación están en la carpeta del proyecto; aquí está el código.

**Entrega 3 (despliegue, KPIs, ética y pitch):** el repositorio incluye además el modelo financiero del caso de negocio con su simulación Monte Carlo, las métricas de los tres ciclos reales del agente con un modelo bayesiano (MCMC), un tablero en Streamlit y una regresión nocturna en GitHub Actions. Todo eso está en la [sección 12](#12-tablero-simulación-monte-carlo-y-regresión-nocturna) y nada de eso llama a la API de Anthropic.

---

## Para evaluarlo en diez minutos

Con Node.js 20+ y Python 3.10+ instalados (sección 2), en una terminal:

```bash
git clone https://github.com/SiriusDarkz/AgenteQA.git
cd AgenteQA
npm run setup                          # instala Playwright y Chromium (2–3 min)
npx playwright test                    # → debe terminar en:  1 passed
python3 -m venv app/.venv && source app/.venv/bin/activate
pip install -r app/requirements.txt
python3 -m app --demo                  # abre http://localhost:8765 con la interfaz
```

En la interfaz, recorre los cinco pasos con los botones de **¿Qué sigue?** (sección 4.1 dice qué debe salir en cada uno). Este modo no necesita llave de API ni internet y da siempre el mismo resultado.

Para ver lo que produce el **agente de verdad**, no hace falta correrlo: la carpeta [`resultados/toolshop-2026-10-21/`](resultados/toolshop-2026-10-21/) contiene, sin retoques, un ciclo completo real (exploración, plan, 10 pruebas, resultados, 8 defectos y reporte) y las pruebas que generó se pueden volver a correr con un comando (sección 4.3). Correr el agente real con tu propia llave está en la sección 4.2.

---

## 1. Qué hace el proyecto

| Paso | Lo hace | Entrada | Salida |
|---|---|---|---|
| 1 · Entiende | el agente, navegando la aplicación con un navegador real | `qa/requisitos.md` (la aplicación, sus usuarios y requisitos) | `qa/exploracion.md` + capturas |
| 2 · Diseña | el agente | requisitos + exploración (o una historia de usuario) | `qa/plan-de-pruebas.md`: tabla de casos de prueba |
| **Decisión 1** | **la persona** aprueba el plan (puede quitar o editar casos) | | `Estado: APROBADO` al final del plan |
| 3 · Ejecuta | el agente escribe las pruebas y las corre con `@playwright/test` | plan aprobado | `tests/*.spec.ts`, `qa/resultados.md`, `qa/evidencia/` |
| 4 · Analiza | el agente, leyendo la salida de Playwright y las capturas | resultados + evidencia | `qa/defectos/DEF-xxx.md`, uno por hallazgo |
| **Decisión 2** | **la persona** confirma o descarta cada defecto | | `Estado: CONFIRMADO` / `DESCARTADO` en cada defecto |
| 5 · Reporta | el agente | todo lo anterior | `qa/reporte.md` con el semáforo de la versión (publicar o no) |

Cómo está hecho, en cinco líneas:

- **El agente** es [Claude](https://www.anthropic.com/claude) corriendo sobre esta carpeta con el [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk). Sus instrucciones son texto plano: `CLAUDE.md` (reglas generales) y una *skill* por paso en `.claude/skills/`. Cada paso es un comando (`/explorar-app`, `/disenar-plan`, …).
- **Para navegar** usa el servidor MCP de Playwright (`.mcp.json`), que le da un navegador Chromium real; **para ejecutar** escribe pruebas de `@playwright/test` y las corre con `npx playwright test` (`playwright.config.ts`).
- **La interfaz web** (`app/`, FastAPI + HTML/JS sin frameworks) no tiene estado propio: muestra lo que hay en `qa/` y `tests/`, y los botones de la persona escriben en esos mismos archivos. Lo que se hace en pantalla y lo que se haría editando los archivos desde Claude Code es lo mismo.
- **Modo demo** (`--demo`): la misma interfaz reproduce un ciclo de ejemplo sin llamar a la API ni abrir un navegador. Sirve para ver el producto sin gastar y como plan B.
- **Límites**: en un mensaje libre el agente solo puede leer el repositorio; el navegador solo puede abrir el dominio de la aplicación bajo prueba y no ejecuta acciones irreversibles (pagar, confirmar un pedido, enviar) sin aprobación humana; cada paso tiene tope de turnos y de gasto.

---

## 2. Lo que necesitas antes de empezar

- **Git**, para clonar el repositorio.
- **Node.js** 20 o más nuevo: https://nodejs.org (la opción LTS).
- **Python** 3.10 o más nuevo: en Mac suele venir instalado; si no, https://www.python.org/downloads.

Para comprobarlo:

```bash
git --version
node --version      # v20.x o más
python3 --version   # 3.10 o más (en Windows prueba con: python --version)
```

No hace falta tener Claude Code instalado. La llave de la API solo se necesita para correr el agente de verdad (sección 4.2); para la demo y para releer el ciclo real no.

---

## 3. Instalación, paso a paso

Se hace una sola vez y toma unos cinco minutos.

**Paso 1. Clona el repositorio y entra en la carpeta.**

```bash
git clone https://github.com/SiriusDarkz/AgenteQA.git
cd AgenteQA
```

**Paso 2. Instala Playwright y el navegador que usa para probar.**

```bash
npm run setup
```

Descarga el navegador Chromium, así que puede tardar dos o tres minutos. Al terminar no muestra errores en rojo.

**Paso 3. Comprueba que las pruebas funcionan.**

```bash
npx playwright test
```

Abre Swag Labs en un navegador invisible e inicia sesión. Debe terminar con `1 passed` (es la prueba de humo `tests/ejemplo.spec.ts`). Si dice eso, Playwright y la aplicación de prueba están bien.

**Paso 4. Instala lo que usa la interfaz.**

Mac o Linux:

```bash
python3 -m venv app/.venv
source app/.venv/bin/activate
pip install -r app/requirements.txt
```

Windows:

```bat
python -m venv app\.venv
app\.venv\Scripts\activate
pip install -r app\requirements.txt
```

Cuando el entorno está activo, la terminal muestra `(.venv)` al inicio de la línea. Hay que activarlo cada vez que se abre una terminal nueva (solo la línea de `activate`).

Listo. Ya está todo instalado.

---

## 4. Cómo correrlo

### 4.1 Modo demo: la interfaz con un ciclo de ejemplo (sin llave, sin internet)

```bash
python3 -m app --demo
```

(En Windows: `python -m app --demo`.) Se abre el navegador en http://localhost:8765; si no se abre solo, entra tú a esa dirección. Para detenerlo, Ctrl + C en la terminal.

Lo que vas a ver es una conversación con el agente. Lo primero que hace es presentarse. Arriba hay una barra con los cinco pasos y la etiqueta **Modo demo**; al final de la conversación siempre está el bloque **¿Qué sigue?** con el botón del siguiente paso. Recórrelo así, y esto es lo que debe salir:

| Pulsa | Qué debe aparecer |
|---|---|
| **Explorar la aplicación** | El agente «navega» la tienda y deja la exploración de Swag Labs como una tarjeta. |
| **Diseñar el plan** | Una tabla con **10 casos de prueba** (CP-01 a CP-10). Desmarca uno si quieres y pulsa **Aprobar el plan** (tu primera decisión: nada se ejecuta hasta aprobar). Al aprobar se muestra la métrica *casos aceptados sin edición*. |
| **Ejecutar las pruebas** | Con los 10 casos aprobados: **8 pasaron, 2 fallaron** (CP-05 y CP-08), con la salida de Playwright. |
| **Analizar los fallos** | Dos tarjetas: **DEF-001** (crítico, el checkout con `problem_user`) y **DEF-002** (medio, el catálogo con `problem_user`), cada una con su captura. **Confirmar** o **Descartar** cada una (tu segunda decisión). |
| **Generar el reporte** | El semáforo de la versión y el reporte completo, descargable. Con los dos defectos confirmados: **🔴 No publicar**. Si descartas DEF-001 y confirmas solo DEF-002: **🟢 Publicar**. |

En este modo los textos son un ejemplo escrito a mano (están en `app/ejemplos/ciclo/` y llevan una nota que lo dice); los resultados, los defectos y el reporte sí se generan a partir de lo que apruebes, así que las dos decisiones tienen efecto. Lo que escribe queda en `qa/` y `tests/` como archivos nuevos: puedes mirarlos, borrarlos o pulsar **Nuevo ciclo** (los archiva en `qa/historial/`).

### 4.2 El agente de verdad

Aquí el agente sí abre el navegador, navega la aplicación, escribe las pruebas y las corre. Para eso llama a la API de Anthropic, que se cobra por uso.

**Paso 1. Consigue una llave de la API.** Entra a https://platform.claude.com, crea una cuenta si no la tienes, ve a *API keys* y crea una. Empieza por `sk-ant-`. Guárdala; solo se muestra una vez. Hay que cargar saldo en esa cuenta: con unos pocos dólares alcanza para varios ciclos (un paso cuesta entre centavos y un dólar; la interfaz muestra el costo de cada uno al terminar).

La suscripción de claude.ai (Pro o Max) no sirve para esto: Anthropic no permite usarla desde aplicaciones hechas con el Agent SDK; hace falta la llave de la Consola.

**Paso 2. Guarda la llave en `app/.env`.** Copia el archivo de ejemplo y pega tu llave en la línea `ANTHROPIC_API_KEY=`:

```bash
cp app/.env.example app/.env        # Windows: copy app\.env.example app\.env
```

`app/.env` está en `.gitignore`: **nunca se sube al repositorio**. `app/.env.example` documenta todas las variables (modelo, puerto, otra aplicación, topes de turnos y de gasto); solo la llave es obligatoria.

**Paso 3. Arranca la interfaz sin `--demo`.**

```bash
python3 -m app
```

Si la terminal dice «Aviso: no encontré ANTHROPIC_API_KEY», revisa el paso 2. Arriba la etiqueta dice **Agente real** y lo primero que verás es al agente presentándose de verdad (corre su skill `/inicio`). Si antes usaste el modo demo verás su ciclo de ejemplo y un aviso amarillo: pulsa **Empezar ciclo nuevo** y el agente real parte de cero.

El flujo es el mismo de 4.1, con estas diferencias:

- Cada paso tarda más: la exploración, dos a tres minutos; la ejecución depende de cuántos casos aprobaste; el ciclo completo de referencia tomó una hora y media con las dos decisiones humanas incluidas. Mientras trabaja ves sus acciones una por una y puedes pararlo con **Detener**.
- En el paso 1 se abre una ventana de Chromium en tu computadora: es el agente navegando la aplicación.
- En el paso 3 las pruebas corren de verdad, en un navegador invisible. Si quieres verlas, arranca con `QA_HEADED=1 python3 -m app`.
- Al terminar cada paso, debajo de su mensaje aparece cuánto tardó y cuánto costó.
- **El resultado no es idéntico en cada corrida.** El agente es un modelo de lenguaje: el plan puede tener 9 u 11 casos en vez de 10, redactados distinto, y las pruebas pueden tomar caminos diferentes. Lo que sí se repite es lo que describe el caso de negocio: un plan trazable a los requisitos, pruebas que describen el requisito y no lo que hace la aplicación, defectos con pasos y evidencia, y un reporte con el semáforo. Con Swag Labs, un ciclo que cubra los escenarios obligatorios de `qa/requisitos.md` llega a los defectos conocidos de `problem_user` (imágenes repetidas en el catálogo y el apellido que se borra en el checkout).

### 4.3 Volver a correr las pruebas del ciclo real (sin agente, sin llave)

El ciclo de referencia de `resultados/toolshop-2026-10-21/` se corrió contra [Toolshop «with bugs»](https://with-bugs.practicesoftwaretesting.com), otra tienda de demostración pública. Las 10 pruebas que escribió el agente se pueden ejecutar hoy, desde la raíz del repositorio, con la instalación de la sección 3 ya hecha:

```bash
npx playwright test --config resultados/toolshop-2026-10-21/playwright.config.ts
```

Resultado esperado: **`2 passed`, `8 failed`**, los mismos 8 fallos que documentan `qa/defectos/DEF-001.md` a `DEF-008.md` de esa carpeta. Su README explica qué es cada archivo y cómo se produjo la corrida.

### 4.4 La misma demo desde la terminal, con Claude Code (opcional)

Si tienes Claude Code instalado y con sesión iniciada, puedes correr los mismos pasos sin la interfaz. Abre `claude` dentro de la carpeta, acepta la confianza del proyecto y el servidor `playwright` cuando te pregunte, y usa:

```
/inicio                                  el agente se presenta
/explorar-app https://www.saucedemo.com  paso 1
/disenar-plan                            paso 2 (luego deja la última línea de qa/plan-de-pruebas.md en: Estado: APROBADO)
/ejecutar-pruebas                        paso 3
/analizar-fallos                         paso 4 (luego cambia el estado de cada qa/defectos/DEF-xxx.md a CONFIRMADO o DESCARTADO)
/reportar                                paso 5
```

Es la forma más directa de ver qué hace cada paso por dentro: las instrucciones están en `.claude/skills/`, en texto plano.

---

## 5. De dónde salen los datos

Este proyecto no usa un conjunto de datos: sus «datos» son una aplicación web pública y lo que el agente observa y produce al probarla.

| Dato | De dónde sale |
|---|---|
| **La aplicación bajo prueba** | [Swag Labs](https://www.saucedemo.com), tienda de demostración de Sauce Labs creada para practicar automatización de pruebas. Es pública, no tiene datos reales ni pagos, y tiene defectos intencionales (el usuario `problem_user`). Los usuarios y la contraseña están publicados en su propia pantalla de inicio de sesión. |
| **`qa/requisitos.md`** | Lo escribió el equipo a mano: describe la aplicación, sus usuarios de prueba publicados, cinco requisitos funcionales y los escenarios obligatorios del ciclo. Es la entrada del agente y el único archivo que una persona escribe antes de empezar. |
| **Exploración, plan, pruebas, resultados, defectos y reporte** (`qa/`, `tests/`) | Los genera el agente en cada ciclo, navegando la aplicación con el navegador del MCP de Playwright y ejecutando las pruebas con `@playwright/test`. Nada viene precargado: los resultados citan la salida literal de Playwright y las rutas reales de las capturas, y la regla del agente es no inventar resultados ni ajustar una prueba para que pase. |
| **El ciclo de ejemplo del modo demo** (`app/ejemplos/ciclo/`) | Lo escribió el equipo a mano a partir de los defectos conocidos de Swag Labs, para mostrar la interfaz sin gastar. Cada archivo lleva la nota «ejemplo del modo demo» y las dos capturas son esquemas dibujados con `app/ejemplos/generar_capturas.py`, no capturas reales. Se puede reemplazar por un ciclo real con `python3 -m app.guardar_ejemplos`. |
| **El ciclo real de referencia** (`resultados/toolshop-2026-10-21/`) | Salida íntegra de una corrida real del agente, el 2026-10-21, contra [Toolshop «with bugs»](https://with-bugs.practicesoftwaretesting.com) (Practice Software Testing, de Testsmith, también pública y creada para practicar pruebas). Sus requisitos se escribieron a partir de la [documentación pública del proyecto](https://github.com/testsmith-io/practice-software-testing). |
| **Las métricas del reporte** (casos aceptados sin edición, pruebas corregidas, tiempos) | Se calculan comparando archivos del propio ciclo: el plan aprobado contra la copia intacta `qa/plan-de-pruebas.generado.md`, la sección de correcciones de `qa/resultados.md` y las horas de los archivos. El reporte dice de qué archivo sale cada número. |

No se usan datos personales. Las dos aplicaciones son ambientes públicos pensados para ser probados; nunca apuntes el agente a una aplicación real de terceros sin permiso, porque navega y hace clic como una persona.

---

## 6. Qué significa «reproducible» aquí

| Comando | Qué debe salir | ¿Idéntico en cada corrida? |
|---|---|---|
| `npx playwright test` | `1 passed` | Sí, mientras Swag Labs esté en línea |
| `python3 -m app --demo` y los cinco botones | Plan de 10 casos → 8 pasaron / 2 fallaron → DEF-001 y DEF-002 → 🔴 con ambos confirmados | Sí, siempre (no llama a la API) |
| `npx playwright test --config resultados/toolshop-2026-10-21/playwright.config.ts` | `2 passed`, `8 failed` | Sí, mientras la versión «with bugs» de Toolshop siga publicada igual; es un ambiente compartido y algún detalle puede variar |
| `python3 -m app` (agente real) | Un ciclo completo con plan, pruebas, defectos y reporte sobre Swag Labs | No al pie de la letra: es un modelo de lenguaje. Se repiten la estructura, la trazabilidad y los defectos conocidos de `problem_user` |

---

## 7. Partir de una historia de usuario

Funciona en los dos modos. Cuando toque el paso 2, en vez de **Diseñar el plan** pulsa **Partir de una historia de usuario**. Se abre un formulario con tres campos: **título** («Compra con tarjeta»), **historia** («Como cliente, quiero…, para…») y **criterios de aceptación**, uno por línea. Guarda y pulsa **Diseñar el plan desde la historia**: el plan sale de esos criterios, con al menos un caso por cada uno y un caso negativo cuando haga falta, y cada caso indica de qué criterio viene. Si un criterio no se puede comprobar en la aplicación, el agente lo anota en los riesgos del plan en vez de inventarse una prueba. La historia queda en `qa/historia-de-usuario.md`.

---

## 8. Conversar con el agente

Abajo del todo hay un cuadro de mensaje. Sirve para preguntarle al agente por la aplicación y por lo que encontró: «¿por qué falló CP-05?», «¿qué cubre el plan?», «¿cuántos defectos críticos quedan?». Responde leyendo los archivos de `qa/` y `tests/` y dice de cuál sale cada dato.

Debajo hay un modelo de lenguaje, así que en principio podría hablar de cualquier cosa. El MVP lo limita en tres capas, de la más fuerte a la más débil:

1. **Sin herramientas para hacer daño.** En un mensaje libre el agente solo tiene lectura del repositorio (`Read`, `Glob`, `Grep`): sin terminal, sin escritura y sin navegador. Los pasos del ciclo, en cambio, sí corren con todo lo que necesitan.
2. **El navegador solo abre la aplicación bajo prueba.** Un control del programa (no del modelo) revisa cada navegación y bloquea cualquier dominio que no sea el de `qa/requisitos.md` o el de la URL que escribiste en el paso 1.
3. **Instrucciones de alcance.** En modo conversación recibe reglas explícitas: solo habla de la aplicación y de los hallazgos, lee los archivos antes de afirmar algo y, ante cualquier otro tema, responde con una sola frase. Esas reglas se arman en cada mensaje con el nombre y la URL de `qa/requisitos.md`, así que valen para cualquier aplicación.

Además, cada mensaje libre tiene un tope de turnos y de gasto (`QA_MAX_TURNOS_CONVERSACION`, por defecto 12, y `QA_PRESUPUESTO_CONVERSACION_USD`, por defecto 1.0), y cada paso del ciclo también (`QA_MAX_TURNOS`, por defecto 80, y `QA_PRESUPUESTO_PASO_USD`, por defecto 5.0).

En los pasos del ciclo hay un cuarto control, agregado después de que el agente completara una compra real al explorar Toolshop (factura INV-2026000005): el programa detiene en el navegador del agente cualquier clic o envío que parezca irreversible (pagar, confirmar un pedido, comprar, enviar un mensaje, transferir, borrar una cuenta) y lo anota en `qa/incidentes.md`. Las pruebas del paso 3 no pasan por ese control porque corren con `npx playwright test`. Solo una persona puede habilitar esas acciones, con `QA_PERMITIR_IRREVERSIBLES=1` en `app/.env`; la expresión que las reconoce se puede ajustar con `QA_ACCIONES_IRREVERSIBLES`. El control y sus pruebas están en `app/agente.py` y `app/pruebas/test_compuertas.py`.

---

## 9. Probar otra aplicación

1. En la interfaz, pulsa el nombre de la aplicación en la parte de arriba. Se abre `qa/requisitos.md`: cambia el nombre, la URL, los usuarios de prueba y los requisitos, y guarda.
2. Agrega `QA_BASE_URL=https://la-direccion-de-tu-app` a `app/.env` (o cambia `baseURL` en `playwright.config.ts`) y vuelve a arrancar la interfaz.
3. Pulsa **Nuevo ciclo** y empieza desde la exploración.

Así se hizo el ciclo de Toolshop de `resultados/`. Nunca apuntes el agente a una aplicación real de terceros sin permiso.

---

## 10. Si algo falla

- **`npm run setup` o `npx playwright test` fallan.** Casi siempre es la red o un Node viejo. Revisa `node --version` (20 o más) y vuelve a intentar. Si el error menciona el navegador, ejecuta `npx playwright install chromium`.
- **`python3: command not found` (Windows).** Usa `python` en lugar de `python3` en todos los comandos.
- **`No module named uvicorn` o `fastapi`.** No está activo el entorno. Ejecuta la línea de `activate` de la sección 3 y vuelve a arrancar.
- **La página no abre.** Entra a mano a http://localhost:8765. Si el puerto está ocupado, arranca con `python3 -m app --puerto 9000` y entra a http://localhost:9000.
- **«Error de la API: authentication_failed».** La llave está mal copiada o no se está leyendo. Abre `app/.env`, comprueba que la línea `ANTHROPIC_API_KEY=sk-ant-...` está completa y vuelve a arrancar.
- **La exploración (paso 1) dice que no encuentra el navegador.** Ejecuta `npx playwright install chromium` dentro de la carpeta y repite el paso.
- **El agente se detiene antes de terminar un paso.** Mira su último mensaje y vuelve a pulsar el botón del paso; lo que ya escribió se conserva. Si dice que se quedó sin turnos, agrega `QA_MAX_TURNOS=150` a `app/.env` y vuelve a arrancar; si llegó al tope de gasto, sube `QA_PRESUPUESTO_PASO_USD`.
- **Un paso se queda colgado.** Pulsa **Detener** en la interfaz y repítelo.
- **Aparece «workspace has not been trusted».** No afecta. Si quieres quitarlo, abre `claude` una vez dentro de la carpeta (si tienes Claude Code) y acepta la confianza.
- **`git status` muestra archivos nuevos en `qa/` o `tests/` después de correr la demo.** Es normal: son los archivos del ciclo que acabas de correr. Puedes borrarlos, versionarlos o pulsar **Nuevo ciclo**, que los archiva en `qa/historial/` (fuera de git).

---

## 11. Qué hay en la carpeta

```
README.md               este archivo
CLAUDE.md               las reglas generales del agente (las lee en cada sesión)
.claude/skills/         las instrucciones del agente: inicio + una por paso del ciclo
.claude/settings.json   permisos pre-aprobados para que el agente corra sin pedir confirmación
.mcp.json               el servidor MCP de Playwright (el navegador con el que explora)
playwright.config.ts    configuración de las pruebas: URL de la aplicación, capturas, reporte
package.json            scripts (npm run setup, npm test) y dependencias de Node

qa/requisitos.md        la aplicación que se prueba, sus usuarios y requisitos (la entrada)
qa/                     aquí deja el agente la exploración, el plan, los resultados, los defectos y el reporte
tests/                  las pruebas de Playwright que genera el agente (+ tests/datos.ts y la prueba de humo)

app/                    la interfaz web y el programa que corre el agente
  __main__.py           arranque: python3 -m app [--demo] [--puerto N]
  servidor.py           la API (FastAPI) que sirve la interfaz y ejecuta los pasos
  agente.py             corre las skills con el Agent SDK y publica lo que hace
  estado.py             lee y escribe los archivos de qa/ y tests/ (la interfaz no tiene otro estado)
  demo.py               el modo demo
  ui/                   la interfaz (HTML, CSS y JS sin frameworks)
  ejemplos/ciclo/       el ciclo de ejemplo del modo demo (marcado como tal)
  ejemplos/demo-web.html  la interfaz con el ciclo de ejemplo dentro, para abrir con doble clic sin instalar nada
  requirements.txt      dependencias de Python
  .env.example          plantilla de configuración; cópiala como app/.env y pon tu llave (app/.env no se sube)

resultados/toolshop-2026-10-21/   ciclo real de referencia, con su README y una configuración para re-ejecutar sus pruebas
resultados/toolshop-2026-10-22/   segundo ciclo real (textos y pruebas, sin la evidencia pesada)
resultados/toolshop-2026-10-25/   tercer ciclo real, pendiente de la segunda decisión humana y del reporte

simulacion/             modelo financiero, Monte Carlo, valor para el cliente, métricas del agente y MCMC
  datos/ciclos.json     los tres ciclos reales cruzados con la lista oficial de defectos
  resultados/           resultados.json (todas las cifras), tablas CSV y el MCMC guardado
  pruebas/              comprueban que el modelo reproduce el caso de negocio
dashboard/app.py        el tablero de Streamlit (cinco vistas)
metricas/regresion/     un resumen por corrida de la regresión nocturna
notebooks/              la simulación Monte Carlo para abrir en Google Colab
docs/                   protocolo y hoja de registro de la línea base manual
.github/workflows/      la regresión nocturna
app/pruebas/            pruebas del control de acciones irreversibles
```

No está en el repositorio (lo excluye `.gitignore`): `app/.env` con la llave, `node_modules/`, `app/.venv/`, y las salidas pesadas de cada corrida (`qa/evidencia/`, `qa/reporte-html/`, `qa/historial/`).

---

---

## 12. Tablero, simulación Monte Carlo y regresión nocturna

Esta parte responde a la entrega 3 del capstone. Ninguna de estas piezas llama a la API de Anthropic: son cálculos que corren en tu computadora en segundos.

| Pieza | Dónde | Para qué |
|---|---|---|
| Modelo financiero | `simulacion/modelo.py` | Reconstruye el modelo de 60 meses del caso de negocio. `simulacion/pruebas/test_modelo.py` comprueba que reproduce sus cifras publicadas |
| Monte Carlo | `simulacion/montecarlo.py` | 10,000 futuros posibles en unos 2 s: probabilidad de cada hito, necesidad de caja, VAN, reglas de inversión y riesgos |
| Valor para el cliente | `simulacion/cliente.py` | Cuándo se paga solo el plan para el cliente |
| Métricas del agente | `simulacion/agente.py` y `simulacion/datos/ciclos.json` | Precisión, cobertura y F1 de los tres ciclos reales, con intervalos bayesianos |
| MCMC | `simulacion/mcmc.py` | Modelo jerárquico de detección de defectos, estimado con PyMC |
| Todas las cifras | `simulacion/resultados/resultados.json` | La fuente única del informe, el deck y el tablero |
| Tablero | `dashboard/app.py` | Junta directiva, monitoreo del agente, simulación, valor para el cliente y gobernanza |
| Regresión nocturna | `.github/workflows/regresion-nocturna.yml` | Corre cada noche las pruebas del agente sin el agente y guarda el resumen en `metricas/regresion/` |

### 12.1 Abrir el tablero en tu computadora

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py                          # abre http://localhost:8501
```

En la pestaña **Simulación Monte Carlo** puedes cambiar los supuestos (ritmo de ventas, bajas, costo variable, descuentos, conversión de los pilotos) y volver a correr las 10,000 corridas. Con los valores iniciales reproduce las cifras del informe.

### 12.2 Regenerar las cifras y correr las pruebas

```bash
pip install -r simulacion/requirements.txt              # incluye PyMC para el MCMC
python3 -m simulacion.generar                           # unos 40 s; con --sin-mcmc reutiliza el MCMC guardado
python3 -m pytest simulacion/pruebas app/pruebas -q     # 37 pruebas
```

Si cambias un supuesto en el código, vuelve a correr `python3 -m simulacion.generar` para que el tablero, el informe y el deck queden con las mismas cifras. La semilla es fija (20261026): el resultado se repite al dólar.

### 12.3 Publicar el tablero en Streamlit Community Cloud (gratis)

1. Entra a https://share.streamlit.io con la cuenta de GitHub dueña del repositorio.
2. Crea una app nueva: repositorio `SiriusDarkz/AgenteQA`, rama `main`, archivo principal `dashboard/app.py`.
3. Publica. La dirección queda del tipo `https://<nombre>.streamlit.app`.

**Tablero publicado:** (https://agente-grupo2.streamlit.app/)

Las apps gratuitas se duermen si nadie las visita; ábrela unos minutos antes de presentar.

### 12.4 Regresión nocturna

Cada noche, a las 03:17 de Santo Domingo, GitHub Actions instala Chromium y corre sin el agente las 10 pruebas que el agente escribió en el ciclo del 21-10-2026, más la prueba de humo de Swag Labs. El resumen queda en `metricas/regresion/AAAA-MM-DD.json` y el tablero lo muestra en **Monitoreo del agente**. Se esperan 2 pruebas que pasan y 8 que fallan, porque son defectos conocidos de Toolshop «with bugs»; si el resultado cambia, el resumen lo marca para revisarlo.

Para lanzarla a mano: pestaña **Actions** del repositorio → **Regresión nocturna** → **Run workflow**. Así se desplegaría en un cliente: las pruebas viven en su repositorio y su integración continua las corre en cada cambio.

### 12.5 Los tres ciclos reales

| Ciclo | Fecha | Casos | Pasaron / fallaron | Defectos reportados | Reales | Estado |
|---|---|---|---|---|---|---|
| A | 2026-10-21 | 10 | 2 / 8 | 8 | 7 | Completo |
| B | 2026-10-22 | 10 | 5 / 5 | 4 | 3 | Completo |
| C | 2026-10-25 | 10 | 4 / 6 | 6 | 5 | Falta la segunda decisión humana y el reporte |

Cada defecto se cruzó con la [lista oficial de Testsmith](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/testSessions/listOfBugs.md) y, si no figuraba, con el código fuente de la versión con errores frente a la versión sin errores. El cruce completo está en `simulacion/datos/ciclos.json`.

### 12.6 Línea base manual

`docs/linea-base-manual.md` explica cómo medir cuánto tarda una persona en hacer a mano lo que hace el agente: ejecutar los 10 casos del plan y documentar dos defectos. Esa línea base es la cifra de trabajo repetitivo que el agente libera.

