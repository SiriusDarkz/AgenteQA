# Ciclo real B · Toolshop «with bugs» · 22-10-2026

Segundo ciclo completo del agente sobre https://with-bugs.practicesoftwaretesting.com, con los mismos requisitos que el ciclo A (ver `../toolshop-2026-10-21/qa/requisitos.md`). Se corrió desde la interfaz del MVP y quedó archivado en `qa/historial/2026-10-25_08-51-48/` de la copia local del equipo; aquí están sus textos y pruebas, sin la evidencia pesada (capturas y trazas).

| Dato | Valor |
|---|---|
| Plan | 10 casos, aprobado sin cambios el 22-10-2026 a las 20:55, tras 1 min 45 s de revisión |
| Ejecución | 5 pasaron, 5 fallaron · 9 de 10 pruebas funcionaron al primer intento |
| Defectos | 4 reportados: DEF-001, DEF-002 y DEF-003 confirmados; DEF-004 descartado |
| Reporte | `qa/reporte.md` |

Cruce con la lista oficial de Testsmith (detalle en `simulacion/datos/ciclos.json`):

- DEF-002 (orden invertido) es el defecto 2; DEF-003 (total de línea en $00.00), el 8; DEF-004 (login con campos vacíos), el 17.
- DEF-001 (el formulario de contacto exige el asunto aunque esté elegido) es un **falso positivo**: la versión con errores registra el formulario al perder el foco (`updateOn: 'blur'`) y `selectOption` de Playwright no le da el foco al campo; un usuario que elige el asunto con el mouse o el teclado sí lo registra.
- La persona **descartó DEF-004 «por no ser de impacto»**, aunque es un defecto real de la lista oficial: la compuerta mezcló «¿es real?» con «¿importa?». Es uno de los hallazgos de gobernanza del informe.

Las pruebas importan `./datos`, que en la copia local fue reemplazado por el del ciclo C; por eso esta carpeta documenta el ciclo pero no trae una configuración para volver a correrlo.
