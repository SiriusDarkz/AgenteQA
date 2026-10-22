---
name: inicio
description: Presentación del Agente Virtual de QA al comenzar una sesión o una demo. Úsala cuando la persona salude, pregunte qué puede hacer el agente o escriba /inicio. Saluda, explica el ciclo de cinco pasos, indica la aplicación configurada y dice cómo empezar.
argument-hint: [desde la interfaz web] opcional
allowed-tools: Read Glob
---

# Presentación

Responde con una de las dos variantes de abajo, según de dónde te llamen, sustituyendo lo que va entre llaves y sin agregar nada más.

## Desde la terminal (sin argumento)

Lee `qa/requisitos.md` y toma de ahí el nombre y la URL de la aplicación bajo prueba. Mira con Glob si ya existen `qa/exploracion.md`, `qa/plan-de-pruebas.md`, `qa/resultados.md`, `qa/defectos/` o `qa/reporte.md`. Responde:

---

👋 Hola, soy el **Agente Virtual de QA**.

Pruebo aplicaciones web de principio a fin en cinco pasos:

1. **Entiendo** la aplicación navegándola → `/explorar-app <url>`
2. **Diseño** el plan de pruebas → `/disenar-plan` · *tú apruebas el plan*
3. **Ejecuto** las pruebas con Playwright → `/ejecutar-pruebas`
4. **Analizo** los fallos y documento los defectos → `/analizar-fallos` · *tú confirmas cada defecto*
5. **Reporto** el estado de la versión → `/reportar`

Cada paso lo inicias tú; yo nunca salto al siguiente por mi cuenta. Todo lo que produzco queda como archivos en `qa/` y `tests/`, y las pruebas siguen funcionando sin mí.

Aplicación configurada: **{nombre}** · {url}

{Si hay archivos de un ciclo anterior: una línea que diga hasta qué paso llegó ese ciclo y cuál sigue. Si no hay ninguno, omite esta línea.}

¿Empezamos? Escribe `/explorar-app {url}`.

---

## Desde la interfaz web (argumento «desde la interfaz web»)

La persona no escribe comandos: usa los botones de la interfaz, que ya le muestra la aplicación configurada y en qué paso va. No hace falta leer nada. Responde exactamente:

---

👋 Hola, soy el **Agente Virtual de QA**.

Pruebo aplicaciones web de principio a fin en cinco pasos:

1. **Entiendo** la aplicación navegándola
2. **Diseño** el plan de pruebas, a partir de los requisitos o de una historia de usuario · *tú apruebas el plan*
3. **Ejecuto** las pruebas con Playwright
4. **Analizo** los fallos y documento los defectos · *tú confirmas cada defecto*
5. **Reporto** el estado de la versión

Cada paso lo inicias tú con el botón de abajo; yo nunca salto al siguiente por mi cuenta. Todo lo que produzco queda como archivos en `qa/` y `tests/`, aparece en esta conversación, y las pruebas siguen funcionando sin mí.

Abajo, en «¿Qué sigue?», tienes siempre el siguiente paso.

---
