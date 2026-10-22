---
name: analizar-fallos
description: Paso 4 del Agente de QA. Clasifica cada prueba fallida como defecto de la aplicación, prueba frágil o problema de ambiente, y documenta los defectos con evidencia en qa/defectos/ para que una persona los confirme.
disable-model-invocation: true
allowed-tools: Read Edit(tests/**) Edit(qa/**) Bash(npx playwright test *)
---

# Paso 4 · Analiza

Lee `qa/resultados.md`. Si no hay pruebas fallidas, escribe `qa/defectos/README.md` indicando que no se encontraron defectos en este ciclo y termina con: «Siguiente paso: /reportar».

## Para cada prueba fallida

1. Lee el mensaje de error de Playwright en `qa/resultados.md` y la captura de pantalla en su carpeta de `qa/evidencia/`. La traza (`trace.zip`) es para que una persona la abra con `npx playwright show-trace`; tú trabajas con el mensaje y la captura.
2. Clasifica el fallo en una de tres categorías:
   - **Defecto de la aplicación**: la aplicación no cumple el requisito (un campo que no acepta texto, un botón que no responde, un mensaje incorrecto, un dato que no cambia cuando debería).
   - **Prueba frágil**: el localizador o la espera estaban mal y la aplicación sí se comporta bien. Corrige la prueba y vuelve a correr solo ese caso con `npx playwright test -g "<ID>"`. Si pasa, actualiza su fila en `qa/resultados.md` y anótalo en la sección de pruebas corregidas.
   - **Ambiente**: tiempo de espera de red, portal caído, navegador. Reintenta una vez; si persiste, márcalo como BLOQUEADO en `qa/resultados.md`.
3. Si varias pruebas fallan por la misma causa, abre un solo defecto que las referencie a todas.

## Formato de cada defecto: `qa/defectos/DEF-NNN.md`

```
# DEF-001 · <título corto y concreto>

- Casos de prueba: CP-xx, CP-yy
- Severidad: Crítica | Alta | Media | Baja — <una línea de justificación>
- Usuario y datos: <usuario, producto, valores usados>
- Pasos para reproducir:
  1. ...
  2. ...
- Resultado esperado: <del plan>
- Resultado obtenido: <lo que pasó, citando el mensaje real de Playwright o el texto visto en pantalla>
- Evidencia: <ruta de la captura> · <archivo de prueba>
- Estado: PENDIENTE DE CONFIRMACIÓN
```

Severidad: **Crítica** si impide completar un flujo de negocio (comprar, iniciar sesión); **Alta** si lo degrada pero hay una salida alternativa; **Media** si es un fallo funcional menor; **Baja** si es cosmético.

## Reglas

- No reportes como defecto nada que no hayas reproducido en la ejecución.
- Un defecto describe lo que ve el usuario, no la línea de código de la prueba.
- Si una prueba frágil no pasa después de corregirla una vez, no sigas ajustándola: déjala como FALLÓ con la nota de que la causa no está clara.

Al terminar, lista en el chat cada defecto en una línea (ID, título, severidad) y pregunta:

«¿Confirmas estos defectos? Marca `Estado: CONFIRMADO` o `Estado: DESCARTADO` en cada archivo (o dímelo aquí) y ejecuta /reportar».
