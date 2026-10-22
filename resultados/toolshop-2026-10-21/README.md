# Ciclo real de referencia · Toolshop · 2026-10-21

Esta carpeta es la **salida íntegra de una corrida real del agente** (modo real, con la API de Anthropic y el navegador de Playwright), sin retoques. Se guarda aparte de `qa/` para que el repositorio se pueda clonar y recorrer desde cero, y para que cualquiera pueda leer lo que el agente produjo sin necesitar una llave de API.

**Aplicación probada:** [Toolshop «with bugs»](https://with-bugs.practicesoftwaretesting.com) (Practice Software Testing, de Testsmith), una ferretería en línea pública creada para practicar pruebas, con defectos intencionales.

**Resultado:** 10 casos de prueba generados y aprobados sin edición · 2 pasaron · 8 fallaron · 8 defectos confirmados por la persona (1 crítico, 1 alto, 6 medios) · semáforo 🔴 *No publicar*.

## Qué hay aquí

| Archivo | Quién lo escribió | Qué es |
|---|---|---|
| `qa/requisitos.md` | el equipo (a mano) | La entrada: aplicación, usuarios de prueba publicados, requisitos R1–R6 y 5 escenarios obligatorios |
| `qa/exploracion.md` | el agente (paso 1) | Lo que vio al navegar la tienda con el navegador del MCP de Playwright: mapa de pantallas, inventario de elementos, flujos y observaciones |
| `qa/evidencia/exploracion-*.png` | el agente (paso 1) | Capturas que tomó durante la exploración |
| `qa/plan-de-pruebas.generado.md` | el agente (paso 2) | El plan tal como lo propuso, intacto |
| `qa/plan-de-pruebas.md` | el agente + la persona | El mismo plan con la decisión humana al final: `Estado: APROBADO` (2026-10-21 21:07) |
| `tests/*.spec.ts`, `tests/datos.ts`, `tests/ayudas.ts` | el agente (paso 3) | Las 10 pruebas de `@playwright/test` que escribió a partir del plan |
| `qa/resultados.md` | el agente (paso 3) | Resultado por caso, salida literal de Playwright y las 3 pruebas que tuvo que corregir (y por qué) |
| `qa/evidencia/ejecucion/*/test-failed-1.png` | Playwright | Captura automática de cada prueba fallida (más `error-context.md`, el snapshot de accesibilidad en el momento del fallo) |
| `qa/defectos/DEF-001.md` … `DEF-008.md` | el agente (paso 4) + la persona | Un defecto por hallazgo, con pasos, esperado vs. obtenido y evidencia; la persona dejó cada uno en `Estado: CONFIRMADO` |
| `qa/reporte.md` | el agente (paso 5) | Reporte final: resumen ejecutivo, semáforo, cobertura, defectos, métricas del hito 1 y próximos pasos |

Las rutas que citan los archivos (`qa/evidencia/...`, `tests/...`) son relativas a **esta carpeta**, que conserva la estructura que tenían en el repositorio en el momento de la corrida. No se incluyen las trazas (`trace.zip`) ni el reporte HTML de Playwright por su tamaño.

## Volver a correr estas pruebas (sin el agente, sin llave de API)

Las pruebas que generó el agente son archivos normales de Playwright y se pueden ejecutar hoy contra la misma aplicación. Desde la raíz del repositorio, con la instalación de la sección 2 del README principal ya hecha:

```bash
npx playwright test --config resultados/toolshop-2026-10-21/playwright.config.ts
```

Resultado esperado mientras la aplicación «with bugs» siga publicada tal como estaba el 2026-10-21: `2 passed`, `8 failed` (fallan CP-03 a CP-10; pasan CP-01 y CP-02). Es un ambiente público compartido, así que un detalle puede variar entre corridas (por ejemplo, si otro usuario dejó datos en la cuenta `customer`); la lectura importante es que los 8 fallos corresponden a los defectos documentados en `qa/defectos/`.

Las capturas de la nueva corrida quedan en `qa/evidencia/toolshop-rerun/` y el reporte HTML en `qa/reporte-html/toolshop-rerun/` (ambas carpetas están fuera de git). Para abrir el reporte:

```bash
npx playwright show-report qa/reporte-html/toolshop-rerun
```

Atención: si en algún momento se corrige el defecto DEF-001, el caso CP-08 llegará hasta confirmar la compra y **creará una factura real** en ese ambiente de demostración en cada corrida.

## Cómo se produjo esta corrida

1. Se escribió `qa/requisitos.md` a partir de la documentación pública del proyecto ([testsmith-io/practice-software-testing](https://github.com/testsmith-io/practice-software-testing)) y se cargó desde la interfaz (botón con el nombre de la aplicación).
2. Se pulsó **Nuevo ciclo** y, uno a uno, los cinco pasos del ciclo desde la interfaz web (`python3 -m app`), con el agente real.
3. La persona aprobó el plan sin cambios (10/10 casos aceptados sin edición, la métrica del hito 1 del caso de negocio) y confirmó los 8 defectos uno por uno desde sus tarjetas.
4. Duración total del ciclo: ≈ 1 h 28 min, de 20:21 a 21:49 hora local (detalle en la sección 6 de `qa/reporte.md`).
