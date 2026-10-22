# Reporte del ciclo de QA · Toolshop (with bugs)

- Aplicación: https://with-bugs.practicesoftwaretesting.com
- Fuentes: `qa/plan-de-pruebas.md`, `qa/plan-de-pruebas.generado.md`, `qa/resultados.md`, `qa/defectos/DEF-001.md` a `DEF-008.md`
- Fecha del reporte: 2026-10-21

## 1. Resumen ejecutivo

1. Se probó de punta a punta la tienda Toolshop: inicio de sesión, catálogo (búsqueda, orden, categoría), carrito, checkout con «Cash on Delivery», favoritos y contacto (requisitos R1 a R6 y los 5 escenarios obligatorios).
2. Se ejecutaron los 10 casos del plan aprobado: 2 pasaron (CP-01, CP-02) y 8 fallaron (CP-03 a CP-10).
3. La persona confirmó los 8 defectos: 1 Crítico, 1 Alto y 6 Medios. No se descartó ninguno.
4. El defecto Crítico (DEF-001) impide terminar una compra con «Cash on Delivery», el único método de pago del alcance.
5. **Recomendación: no publicar** esta versión hasta corregir DEF-001 y, de preferencia, DEF-002.

## 2. Semáforo de la versión

### 🔴 No publicar

Regla aplicada: 🔴 si hay al menos un defecto Crítico confirmado; 🟡 si hay Altos; 🟢 en cualquier otro caso.
Hay **1 defecto Crítico confirmado (DEF-001)**, así que corresponde 🔴. Además hay 1 Alto (DEF-002).

## 3. Cobertura

| Prioridad | Planificados | Ejecutados | Pasaron | Fallaron | Bloqueados |
|---|---|---|---|---|---|
| Alta | 6 (CP-01, 02, 03, 04, 06, 08) | 6 | 2 (CP-01, CP-02) | 4 (CP-03, CP-04, CP-06, CP-08) | 0 |
| Media | 4 (CP-05, 07, 09, 10) | 4 | 0 | 4 (CP-05, CP-07, CP-09, CP-10) | 0 |
| **Total** | **10** | **10** | **2 (20 %)** | **8 (80 %)** | **0** |

Notas (de `qa/resultados.md`):
- Ningún caso quedó bloqueado, pero CP-08 se detuvo en el paso 5 («Confirm» deshabilitado): los pasos 6 a 8 (confirmación, factura e «Invoices») no se llegaron a ejecutar. Esa parte de R4 queda **sin verificar** en esta corrida.
- Dentro de casos fallidos hubo comprobaciones que sí cumplieron: el filtro por categoría Hammer (CP-05), el precio unitario, total del carrito y contador (CP-06), el aviso sin sesión y la presencia en Favorites (CP-09).
- Corrida: 2026-10-21, de 21:13:26 a 21:14:46, Chromium, 1 worker, sin reintentos, 1.3 min.

## 4. Defectos confirmados

| ID | Título | Severidad | Casos | Evidencia |
|---|---|---|---|---|
| DEF-001 | Con «Cash on Delivery» el botón «Confirm» queda deshabilitado y no se puede terminar la compra | Crítica | CP-08 | `qa/evidencia/ejecucion/checkout-Checkout-R4-CP-08-57dd9-asta-la-factura-R4-·-Esc-1--chromium/test-failed-1.png` |
| DEF-002 | El botón de quitar (✕) no elimina el producto del carrito | Alta | CP-07 | `qa/evidencia/ejecucion/carrito-Detalle-de-product-fb900-un-producto-del-carrito-R3--chromium/test-failed-1.png` |
| DEF-003 | El selector de orden invierte el sentido: «Price (Low - High)» y «Name (A - Z)» ordenan al revés | Media | CP-04, CP-05 | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-2fe93-ecio-ascendente-R2-·-Esc-2--chromium/test-failed-1.png` · `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-856eb-ro-por-categoría-Hammer-R2--chromium/test-failed-1.png` |
| DEF-004 | La búsqueda «hammer» no devuelve «Sledgehammer» | Media | CP-04 | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-2fe93-ecio-ascendente-R2-·-Esc-2--chromium/test-failed-1.png` · `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-856eb-ro-por-categoría-Hammer-R2--chromium/test-failed-1.png` |
| DEF-005 | El total de la línea del carrito muestra «$00.00» | Media | CP-06 | `qa/evidencia/ejecucion/carrito-Detalle-de-product-a3f6f-es-recalculados-R3-·-Esc-3--chromium/test-failed-1.png` |
| DEF-006 | El formulario de contacto se envía con el Email vacío | Media | CP-10 | `qa/evidencia/ejecucion/contacto-Contacto-R6-CP-10-4ee28-go-envío-válido-R6-·-Esc-5--chromium/test-failed-1.png` |
| DEF-007 | Con correo y contraseña vacíos el login no indica que son obligatorios | Media | CP-03 | `qa/evidencia/ejecucion/login-Inicio-de-sesión-R1--1f368-n-campos-vacíos-R1-·-Esc-4--chromium/test-failed-1.png` |
| DEF-008 | Al agregar un producto a favoritos con sesión aparece «Oeps, something went wrong.» | Media | CP-09 | `qa/evidencia/ejecucion/favoritos-Favoritos-R5-CP--ccdef-esión-y-alta-con-sesión-R5--chromium/test-failed-1.png` |

Todos fueron confirmados desde la interfaz el 2026-10-21 21:49. Cada carpeta de evidencia tiene además `error-context.md` y `trace.zip`.

Observación sobre DEF-008: el propio defecto advierte que no se puede descartar del todo que el aviso venga de un borrado previo que no se guardó en el servidor (O-13 de la exploración). La traza permite revisarlo.

## 5. Defectos descartados

Ninguno. Los 8 defectos quedaron en `Estado: CONFIRMADO`.

## 6. Métricas del ciclo (hito 1)

| Métrica | Valor |
|---|---|
| Casos generados por el agente | 10 (CP-01 a CP-10) |
| Aceptados sin edición | 10 |
| Editados | 0 |
| Rechazados | 0 |
| Añadidos por la persona | 0 |
| **% aceptados sin edición** | **100 % (10/10)** |
| Pruebas generadas / correctas al primer intento | 10 / 7 |
| Pruebas que el agente tuvo que corregir | 3: CP-01 (localizador ambiguo en modo estricto → `getByTestId('password')`), CP-10 (interacción con el select Subject), CP-09 (aserción con espera mal construida: `toHaveCount(0)` reintentaba hasta que el aviso desaparecía y daba un falso positivo) |
| Resultados esperados cambiados para que pasen | 0 |
| Tiempo total del ciclo | ≈ 1 h 28 min (de ≈ 20:21 a 21:49 del 2026-10-21, hora local) |

Cómo se obtuvo cada dato:
- **Aceptación del plan:** se comparó la tabla de casos de `qa/plan-de-pruebas.md` con la de `qa/plan-de-pruebas.generado.md`. Las 10 filas son idénticas; la única diferencia entre los archivos es la línea de estado («Aprobado desde la interfaz el 2026-10-21 21:07 · Estado: APROBADO» frente a «Estado: PENDIENTE DE APROBACIÓN»).
- **Pruebas corregidas:** sección 3 de `qa/resultados.md`. Estrictamente por localizador o interacción son 2 (CP-01, CP-10); la de CP-09 fue por una espera/aserción que no detectaba el error. CP-03 y CP-07 se revisaron y no se corrigieron porque el fallo es de la aplicación.
- **Tiempo:**
  - Inicio: `qa/exploracion.md` solo da la fecha («2026-10-22 (UTC)») y la hora de la factura de exploración, «2026-10-22 00:23:46» en hora del servidor (UTC), que equivale a las 20:23 hora local. La primera captura de la exploración (`qa/evidencia/exploracion-login-campos-vacios.png`) tiene hora de archivo 20:21; se toma esa como inicio aproximado.
  - Hitos: plan aprobado 21:07 · ejecución 21:13:26–21:14:46 · defectos confirmados 21:49.
  - Fin: 21:49, última decisión registrada en los archivos (sin contar este reporte).
  - La diferencia de fecha (22 en UTC, 21 en hora local) es solo de zona horaria.

## 7. Las pruebas quedan en el repositorio

Las pruebas están en `tests/` (`login.spec.ts`, `catalogo.spec.ts`, `carrito.spec.ts`, `checkout.spec.ts`, `favoritos.spec.ts`, `contacto.spec.ts`, con datos en `tests/datos.ts` y utilidades en `tests/ayudas.ts`), y se pueden correr sin el agente.

`playwright.config.ts` apunta por defecto a otra URL (saucedemo.com), así que hay que indicar la de Toolshop con la variable `QA_BASE_URL`, que la configuración ya contempla:

```bash
QA_BASE_URL=https://with-bugs.practicesoftwaretesting.com npx playwright test \
  tests/login.spec.ts tests/catalogo.spec.ts tests/carrito.spec.ts \
  tests/checkout.spec.ts tests/favoritos.spec.ts tests/contacto.spec.ts
```

(`npx playwright test` sin argumentos correría también `tests/ejemplo.spec.ts`, el humo de saucedemo, que no es de esta aplicación.)

Reporte HTML de la corrida:

```bash
npx playwright show-report qa/reporte-html
```

Para ver la traza de un fallo: `npx playwright show-trace <carpeta de evidencia>/trace.zip`.

Atención: si DEF-001 se corrige, CP-08 llegará hasta confirmar y **creará una factura real** en el ambiente de demostración en cada corrida.

## 8. Próximos pasos sugeridos

1. Corregir DEF-001 (Crítico) y DEF-002 (Alto) y volver a correr las pruebas; con DEF-001 corregido, CP-08 verificará por fin la factura y su aparición en «Invoices», que hoy siguen sin verificar.
2. Corregir los 6 defectos Medios, empezando por las validaciones (DEF-006, DEF-007) y el orden y la búsqueda del catálogo (DEF-003, DEF-004), y revisar la traza de DEF-008 para descartar la causa de datos compartidos.
3. Ampliar el plan con lo que quedó fuera para no pasar de 10 casos: el botón «+» de cantidad (O-4), orden Z-A y precio descendente, y el acceso del administrador.
