# Reporte del ciclo de QA · Toolshop (with bugs)

- Aplicación: https://with-bugs.practicesoftwaretesting.com
- Fecha: 2026-10-22
- Fuentes: `qa/plan-de-pruebas.md` (APROBADO 2026-10-22 20:55), `qa/plan-de-pruebas.generado.md`, `qa/resultados.md`, `qa/defectos/DEF-001.md` a `DEF-004.md`

## 1. Resumen ejecutivo

1. Se probaron de principio a fin los requisitos R1–R6 de Toolshop: inicio de sesión, catálogo (búsqueda, orden y filtros), carrito, checkout con «Cash on Delivery», favoritos y contacto.
2. Se ejecutaron los 10 casos del plan aprobado en Chromium: 5 pasaron y 5 fallaron.
3. Se confirmaron 3 defectos: 1 Crítico (el formulario de contacto no se puede enviar), 1 Alto (los órdenes ascendentes salen invertidos) y 1 Medio (el total de la línea del carrito muestra «$00.00»). Se descartó 1.
4. El flujo principal de compra (login → carrito → checkout → factura) funciona: CP-01 y CP-08 pasaron.
5. **Recomendación: no publicar** esta versión hasta corregir DEF-001 y volver a ejecutar las pruebas.

## 2. Semáforo de la versión

### 🔴 No publicar

Regla aplicada: 🔴 si hay al menos un defecto Crítico confirmado; 🟡 si hay Altos; 🟢 en cualquier otro caso.
Hay un defecto Crítico confirmado (DEF-001), así que el semáforo es rojo. Además hay un Alto confirmado (DEF-002).

## 3. Cobertura

| Prioridad | Planificados | Ejecutados | Pasaron | Fallaron | Bloqueados |
|---|---|---|---|---|---|
| Alta | 6 (CP-01, CP-02, CP-03, CP-04, CP-07, CP-08) | 6 | 3 (CP-01, CP-02, CP-08) | 3 (CP-03, CP-04, CP-07) | 0 |
| Media | 4 (CP-05, CP-06, CP-09, CP-10) | 4 | 2 (CP-06, CP-09) | 2 (CP-05, CP-10) | 0 |
| **Total** | **10** | **10** | **5** | **5** | **0** |

Por requisito: R1 (login) 2 de 3 pasaron · R2 (catálogo) 1 de 3 · R3 (carrito) 0 de 1 · R4 (checkout) 1 de 1 · R5 (favoritos) 1 de 1 · R6 (contacto) 0 de 1.

## 4. Defectos confirmados

| ID | Título | Severidad | Casos | Evidencia |
|---|---|---|---|---|
| DEF-001 | El formulario de contacto no se envía: «Subject is required» con el asunto elegido | Crítica | CP-10 | `qa/evidencia/ejecucion/contacto-Contacto-R6-CP-10-e31f0-on-todos-los-campos-válidos-chromium/test-failed-1.png` |
| DEF-002 | El orden ascendente sale invertido: «Price (Low - High)» y «Name (A - Z)» ordenan de mayor a menor | Alta | CP-04, CP-05 | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-600d9-por-precio-de-menor-a-mayor-chromium/test-failed-1.png` · `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-a110b--Orden-por-nombre-A–Z-y-Z–A-chromium/test-failed-1.png` |
| DEF-003 | En el carrito, el total de la línea muestra «$00.00» | Media | CP-07 | `qa/evidencia/ejecucion/carrito-Detalle-de-product-4fb10-contador-total-y-cambio-a-3-chromium/test-failed-1.png` |

Cada carpeta de evidencia contiene además `trace.zip` y `error-context.md`.

## 5. Defectos descartados

- **DEF-004** · Login con campos vacíos: no se indica que el correo y la contraseña son obligatorios (CP-03, severidad propuesta Media). Motivo de la persona: «No es de impacto para el producto.» (decidido 2026-10-22 21:49). CP-03 sigue contando como fallado en la cobertura, porque la prueba falló.

## 6. Métricas del ciclo

| Métrica | Valor |
|---|---|
| Casos generados por el agente | 10 (CP-01 a CP-10, en `qa/plan-de-pruebas.generado.md`) |
| Aceptados sin edición | 10 |
| Editados | 0 |
| Rechazados | 0 |
| Añadidos por la persona | 0 |
| **% aceptados sin edición** | **100 %** (10 / 10) |
| Pruebas corregidas por localizador o espera | 1 de 10 (CP-03, localizador: `getByTestId('email-error')`/`password-error`, supuestos, se cambiaron por `getByText(/required/i)`; ver `qa/resultados.md` §3). 9 de 10 funcionaron a la primera |
| Inicio del ciclo | ≈ 2026-10-22 20:31 (aprox.) |
| Fin del ciclo | 2026-10-22 22:23 (última decisión sobre defectos, DEF-002) |
| **Tiempo total** | **≈ 1 h 52 min** |

Sobre la comparación de planes: las 10 filas de casos de `qa/plan-de-pruebas.md` son idénticas a las de `qa/plan-de-pruebas.generado.md`. La única diferencia entre los dos archivos es la línea de estado (`PENDIENTE DE APROBACIÓN` → `Aprobado desde la interfaz el 2026-10-22 20:55` / `Estado: APROBADO`).

Sobre el tiempo: `qa/exploracion.md` solo registra la fecha, no la hora de inicio. La hora de inicio sale de la primera captura de la exploración (`qa/evidencia/exploracion-login-campos-vacios.png`, 20:31 según el sistema de archivos) y coincide con la factura creada durante la exploración (`2026-10-23 00:33:36` hora del servidor, 20:33 hora local). Hitos registrados en los archivos: plan aprobado 20:55 · corrida completa 20:57:23 · nueva corrida de CP-03 20:59 · decisiones sobre defectos 21:43, 21:49, 22:22 y 22:23. Buena parte del tiempo entre 21:00 y 22:23 corresponde a la revisión de defectos por la persona.

## 7. Las pruebas quedan en el repositorio

Las pruebas están en `tests/` (`login.spec.ts`, `catalogo.spec.ts`, `carrito.spec.ts`, `checkout.spec.ts`, `favoritos.spec.ts`, `contacto.spec.ts`) con los datos en `tests/datos.ts`. Se pueden correr sin el agente:

```bash
QA_BASE_URL=https://with-bugs.practicesoftwaretesting.com npx playwright test tests/login.spec.ts tests/catalogo.spec.ts tests/carrito.spec.ts tests/checkout.spec.ts tests/favoritos.spec.ts tests/contacto.spec.ts
```

`QA_BASE_URL` es necesaria porque `playwright.config.ts` apunta por defecto a otra aplicación (ver `qa/resultados.md`). Ojo: CP-08 crea un pedido real en el ambiente compartido.

Reporte HTML: `npx playwright show-report qa/reporte-html`

## 8. Próximos pasos

1. Corregir DEF-001 (validación del asunto en contacto) y DEF-002 (valores de orden cruzados, según O-05 de la exploración), y volver a correr CP-10, CP-04 y CP-05.
2. Corregir DEF-003 (cálculo de `line-price` en el carrito) y repetir CP-07.
3. Fijar `QA_BASE_URL` de Toolshop en `playwright.config.ts` o en el entorno de CI para que `npx playwright test` funcione sin parámetros, y añadir un caso para «Price (High - Low)», que no se probó en este ciclo.
