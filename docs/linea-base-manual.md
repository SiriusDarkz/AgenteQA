# Línea base manual: cuánto trabajo repetitivo libera el agente

**Para qué sirve.** El caso de negocio y la consigna piden demostrar cuánta carga de trabajo libera la automatización. Para eso hace falta medir cuánto tarda una persona en hacer a mano lo que el agente hizo en un ciclo, con cronómetro y en las mismas condiciones. Es la misma «línea base medida» que el caso de negocio exige a cada piloto.

**Quién lo hace.** Una persona del equipo, idealmente la que menos conozca el plan. Toma entre una y dos horas. No se usa ninguna IA durante la medición.

## Qué se mide

1. **Ejecutar a mano los 10 casos** del plan del ciclo A (`resultados/toolshop-2026-10-21/qa/plan-de-pruebas.md`) en https://with-bugs.practicesoftwaretesting.com, siguiendo los pasos tal como están escritos y anotando si cada caso pasa o falla.
2. **Documentar dos defectos** con la misma estructura de `resultados/toolshop-2026-10-21/qa/defectos/DEF-002.md`: título, pasos para reproducir, resultado esperado, resultado obtenido, captura y severidad.
3. **Opcional: automatizar un caso** con Playwright (por ejemplo CP-01, el inicio de sesión válido) para estimar cuánto cuesta escribir una prueba sin el agente.

## Reglas

- Cronometrar cada tarea por separado y anotar inicio y fin en `docs/linea-base-registro.csv`.
- Si hay una interrupción, pausar el cronómetro y anotarla en «observaciones».
- No mirar los resultados del agente antes de terminar: el punto es medir el trabajo desde cero.
- Usar los usuarios públicos de la aplicación (están en `qa/requisitos.md`). Es un ambiente de práctica: no hay datos reales ni pagos.

## Cómo se usa el resultado

| Comparación | Con el agente (ciclo A) | A mano |
|---|---|---|
| Tiempo de una persona | 2 min 01 s de revisión del plan + 18 s para confirmar 8 defectos | lo que mida el cronómetro |
| Repetir la regresión | 1.3 min de máquina, sin IA y sin persona | el tiempo de la tarea 1, otra vez |

La diferencia, multiplicada por el número de regresiones al mes de un cliente, es el trabajo repetitivo que el agente libera. Esa cifra entra en el informe y en el pitch, y en el tablero cuando se agregue a `simulacion/datos/ciclos.json`.
