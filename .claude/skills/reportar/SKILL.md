---
name: reportar
description: Paso 5 del Agente de QA. Consolida resultados y defectos confirmados en qa/reporte.md, con el riesgo de la versión, una recomendación de publicación y las métricas del ciclo.
disable-model-invocation: true
allowed-tools: Read Edit(qa/**)
---

# Paso 5 · Reporta

Lee `qa/plan-de-pruebas.md`, `qa/plan-de-pruebas.generado.md`, `qa/resultados.md` y todos los `qa/defectos/DEF-*.md`.

Si algún defecto sigue en `PENDIENTE DE CONFIRMACIÓN`, pregunta por él antes de continuar. Solo los `CONFIRMADO` cuentan para el riesgo; los `DESCARTADO` se listan aparte.

## Salida: `qa/reporte.md`

1. **Resumen ejecutivo** (cinco líneas): qué se probó, resultado global y recomendación.
2. **Semáforo de la versión**: 🟢 publicar, 🟡 publicar con riesgo conocido, 🔴 no publicar. Regla: 🔴 si hay al menos un defecto Crítico confirmado; 🟡 si hay Altos; 🟢 en cualquier otro caso. Escribe la regla aplicada.
3. **Cobertura**: casos planificados, ejecutados, pasaron, fallaron, bloqueados, desglosados por prioridad.
4. **Defectos confirmados**: tabla con ID, título, severidad, casos relacionados y evidencia.
5. **Defectos descartados**: una línea por cada uno con el motivo que dio la persona.
6. **Métricas del ciclo** (son las del hito 1 del caso de negocio):
   - casos generados por el agente;
   - casos aceptados sin edición: compara fila por fila `qa/plan-de-pruebas.md` con `qa/plan-de-pruebas.generado.md`. Un caso cuenta como editado si cambió cualquier celda de su fila; uno que ya no está cuenta como rechazado; uno nuevo cuenta como añadido por la persona. Reporta aceptados / editados / rechazados / añadidos y el porcentaje de aceptados sin edición;
   - pruebas que el agente tuvo que corregir por localizador o espera;
   - tiempo total del ciclo, con las horas de inicio y fin que aparecen en los archivos.
7. **Las pruebas quedan en el repositorio**: cómo correrlas sin el agente (`npx playwright test`) y dónde está el reporte HTML (`npx playwright show-report qa/reporte-html`).
8. **Próximos pasos** sugeridos: tres como máximo.

Muestra en el chat el semáforo, la tabla de defectos confirmados y las métricas. Si la persona pide abrir un ticket por cada defecto en GitHub, hazlo solo si ella lo pide y la herramienta `gh` está disponible; nunca por iniciativa propia.
