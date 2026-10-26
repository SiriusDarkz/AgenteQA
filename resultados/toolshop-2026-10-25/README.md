# Ciclo real C · Toolshop «with bugs» · 25-10-2026

Tercer ciclo del agente sobre https://with-bugs.practicesoftwaretesting.com, con los mismos requisitos que los ciclos A y B. Copia de los textos y las pruebas que estaban en `qa/` y `tests/` de la copia local del equipo, sin la evidencia pesada.

| Dato | Valor |
|---|---|
| Duración de los pasos 1 a 4 | 40.5 min (de 09:51:56 a 10:32:24), con 54 s de revisión humana del plan |
| Plan | 10 casos, aprobado sin cambios a las 10:05 |
| Ejecución | 4 pasaron, 6 fallaron en 53.5 s · 7 de 10 pruebas funcionaron al primer intento |
| Defectos | 6 reportados, **pendientes de la segunda decisión humana**; el paso 5 (reporte) no se corrió |

Cruce con la lista oficial de Testsmith (detalle en `simulacion/datos/ciclos.json`):

- DEF-002 (orden invertido) es el defecto 2; DEF-003 (no se puede quitar un producto del carrito), el 7; DEF-005 (login con campos vacíos), el 17; DEF-006 (imagen de «Slip Joint Pliers» que no carga), el 26, que es visual.
- DEF-001 (un clic en «Confirm» no genera el pedido) se verificó en el código: en la versión sin errores el primer botón dice «Check payment» y cambia a «Confirm»; en la versión con errores dice «Confirm» en los dos pasos.
- DEF-004 (el formulario de contacto exige el asunto) es el mismo falso positivo de automatización del ciclo B.
