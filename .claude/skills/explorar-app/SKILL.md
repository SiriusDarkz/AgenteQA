---
name: explorar-app
description: Paso 1 del Agente de QA. Explora la aplicación web con el navegador del MCP de Playwright y documenta pantallas, flujos y elementos en qa/exploracion.md.
argument-hint: [url]
disable-model-invocation: true
allowed-tools: mcp__playwright Read Edit(qa/**)
---

# Paso 1 · Entiende

URL objetivo: $ARGUMENTS (si viene vacía, usa la URL de `qa/requisitos.md`).

Lee `qa/requisitos.md` completo antes de abrir el navegador: ahí están los usuarios de prueba, los requisitos y los escenarios obligatorios.

## Qué hacer

1. Abre la URL con el navegador del servidor MCP `playwright`. Lee cada pantalla con snapshots de accesibilidad; toma una captura solo cuando algo se vea raro y quieras dejar evidencia.
2. Recorre con el usuario estándar todos los flujos que mencionan los requisitos: inicio de sesión válido e inválido, catálogo, carrito, checkout completo y cierre de sesión.
3. Repite el checkout completo con cada usuario marcado como «comportamiento anómalo» en los requisitos. Anota qué cambia respecto al usuario estándar, pero no lo califiques todavía como defecto.
4. En cada pantalla registra: URL, propósito, elementos interactivos con su localizador más estable (atributo `data-test`, rol con nombre accesible, placeholder o id), mensajes de error observados y a qué pantalla lleva cada acción.
5. No diseñes casos de prueba en este paso; eso es `/disenar-plan`.

## Salida: `qa/exploracion.md`

1. **Resumen** de la aplicación en tres líneas.
2. **Mapa de pantallas**: tabla con pantalla, URL y propósito.
3. **Inventario de elementos** por pantalla, con el localizador recomendado de cada uno.
4. **Flujos observados**: pasos numerados de cada flujo, con el usuario usado.
5. **Observaciones**: cosas que se vieron distintas entre usuarios o que parecen incorrectas, marcadas como «por verificar en el paso 3».

Al terminar, resume en el chat en cinco líneas lo que encontraste y cierra con: «Siguiente paso: /disenar-plan».
