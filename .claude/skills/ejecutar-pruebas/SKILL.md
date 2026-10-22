---
name: ejecutar-pruebas
description: Paso 3 del Agente de QA. Convierte el plan aprobado en pruebas de Playwright en tests/, las ejecuta y registra resultados y evidencia en qa/resultados.md.
argument-hint: [CP-01 CP-02 ...] opcional, para ejecutar solo esos casos
disable-model-invocation: true
allowed-tools: Read Edit(tests/**) Edit(qa/**) Bash(npx playwright test *) Bash(npx playwright show-report *) Bash(npx playwright install *)
---

# Paso 3 · Ejecuta

Casos a ejecutar: $ARGUMENTS (vacío = todos los del plan).

## Antes de empezar

1. Lee `qa/plan-de-pruebas.md`. Si la última línea no dice `Estado: APROBADO` y la persona no lo confirmó en el chat, detente y pide la aprobación.
2. Lee `qa/exploracion.md` para los localizadores y `tests/ejemplo.spec.ts` como referencia de estilo.
3. Revisa `tests/datos.ts`; si el plan usa usuarios o datos que no están ahí, agrégalos.

## Generar las pruebas

- Un archivo por flujo en `tests/` (por ejemplo `tests/login.spec.ts`, `tests/catalogo.spec.ts`, `tests/carrito.spec.ts`, `tests/checkout.spec.ts`), con un `test.describe` por flujo y un `test` por caso, titulado `CP-01 · <título del plan>`.
- Usa `@playwright/test`. Localizadores en este orden: `getByTestId` (el proyecto usa `data-test`), `getByRole` con nombre accesible, `getByPlaceholder` / `getByLabel`, id. Sin XPath ni clases CSS si hay alternativa.
- La URL base viene de `playwright.config.ts`; usa rutas relativas (`page.goto('/')`).
- Las credenciales se importan de `tests/datos.ts`; no las repitas en cada prueba.
- Cada prueba es independiente: hace su propio inicio de sesión y no depende del orden.
- Las aserciones son las del «resultado esperado» del plan, aunque sospeches que van a fallar. La prueba describe el comportamiento correcto, no el observado.
- Los casos asignados a usuarios anómalos se escriben con ese usuario. Si hay un defecto, la prueba debe fallar: eso es lo que queremos ver.

## Ejecutar

- Corre `npx playwright test --reporter=list,html`. Si recibiste IDs como argumento, filtra con `-g "CP-01|CP-02"`.
- Si una prueba falla por un error tuyo (localizador equivocado, sintaxis, una espera que faltaba) y no por la aplicación, corrígela y vuelve a correr solo esa prueba con `npx playwright test -g "CP-03"`. Máximo dos intentos por prueba; después déjala fallar y anótalo.
- No cambies un resultado esperado para que una prueba pase.
- Si el navegador no está instalado, ejecuta `npx playwright install chromium` y reintenta.

## Salida: `qa/resultados.md`

1. **Resumen**: casos planificados, ejecutados, pasaron, fallaron, duración total, fecha y hora.
2. **Tabla de resultados**: ID, título, usuario, resultado (PASÓ / FALLÓ), duración, archivo de prueba, ruta de la evidencia si falló (carpeta dentro de `qa/evidencia/`).
3. **Pruebas corregidas**: cuáles tuviste que corregir por localizador o espera y por qué. Este dato alimenta la métrica de calidad de la generación.
4. **Salida de Playwright**: pega las líneas relevantes de la salida real (resumen final y mensajes de error). No la inventes ni la resumas de memoria.

Termina diciendo en el chat cuántas pasaron, cuántas fallaron y dónde está el reporte HTML (`npx playwright show-report qa/reporte-html`). Cierra con: «Siguiente paso: /analizar-fallos».
