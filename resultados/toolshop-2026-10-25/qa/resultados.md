# Resultados de la ejecución · Toolshop (with bugs)

- URL: https://with-bugs.practicesoftwaretesting.com (pasada con `QA_BASE_URL`, porque la URL base por defecto de `playwright.config.ts` es `https://www.saucedemo.com`)
- Plan: `qa/plan-de-pruebas.md` (Estado: APROBADO, 2026-10-25 10:05)
- Comando de la corrida final: `QA_BASE_URL=https://with-bugs.practicesoftwaretesting.com npx playwright test -g "CP-" --reporter=list,html`
  (`-g "CP-"` deja fuera `tests/ejemplo.spec.ts`, la prueba de humo de saucedemo, que no forma parte del plan)
- Navegador: Chromium, 1 worker, sin reintentos

## 1. Resumen

| Dato | Valor |
|---|---|
| Casos planificados | 10 |
| Casos ejecutados | 10 |
| Pasaron | 4 |
| Fallaron | 6 |
| Duración total (corrida final) | 53.5 s (según Playwright) |
| Fecha y hora de la corrida final | 2026-10-25, de 10:11:14 a 10:12:08 |

## 2. Tabla de resultados

| ID | Título | Usuario | Resultado | Duración | Archivo de prueba | Evidencia (si falló) |
|---|---|---|---|---|---|---|
| CP-01 | Inicio de sesión válido | customer@practicesoftwaretesting.com | PASÓ | 1.8 s | `tests/login.spec.ts` | — |
| CP-02 | Inicio de sesión con contraseña incorrecta | customer@practicesoftwaretesting.com | PASÓ | 1.9 s | `tests/login.spec.ts` | — |
| CP-03 | Inicio de sesión con campos vacíos | — (sin usuario) | FALLÓ | 6.0 s | `tests/login.spec.ts` | `qa/evidencia/login-Inicio-de-sesión-R1--ef8b8-de-sesión-con-campos-vacíos-chromium/` |
| CP-04 | Búsqueda «hammer» ordenada por precio de menor a mayor | — (sin sesión) | FALLÓ | 2.3 s | `tests/catalogo.spec.ts` | `qa/evidencia/catalogo-Catálogo-búsqueda-db994-por-precio-de-menor-a-mayor-chromium/` |
| CP-05 | Catálogo y filtro por categoría Hammer | — (sin sesión) | FALLÓ | 6.7 s | `tests/catalogo.spec.ts` | `qa/evidencia/catalogo-Catálogo-búsqueda-75c22-filtro-por-categoría-Hammer-chromium/` |
| CP-06 | Carrito: cantidad 2, cambio a 3 y quitar producto | — (sin sesión) | FALLÓ | 7.0 s | `tests/carrito.spec.ts` | `qa/evidencia/carrito-Detalle-de-product-7e459-ambio-a-3-y-quitar-producto-chromium/` |
| CP-07 | Compra completa con Cash on Delivery hasta la factura | customer@practicesoftwaretesting.com | FALLÓ | 8.3 s | `tests/checkout.spec.ts` | `qa/evidencia/checkout-Checkout-R4-CP-07-86fd6-n-Delivery-hasta-la-factura-chromium/` |
| CP-08 | Favoritos sin sesión y con sesión | customer2@practicesoftwaretesting.com | PASÓ | 6.0 s | `tests/favoritos.spec.ts` | — |
| CP-09 | Contacto: campo obligatorio vacío y luego envío válido | — (sin sesión) | FALLÓ | 7.8 s | `tests/contacto.spec.ts` | `qa/evidencia/contacto-Contacto-R6-CP-09-573a2--vacío-y-luego-envío-válido-chromium/` |
| CP-10 | El administrador entra al panel | admin@practicesoftwaretesting.com | PASÓ | 3.3 s | `tests/login.spec.ts` | — |

Cada carpeta de evidencia contiene `test-failed-1.png` (captura), `error-context.md` (snapshot de accesibilidad de la página al fallar) y `trace.zip` (traza: `npx playwright show-trace <carpeta>/trace.zip`).

### Lo que muestra cada fallo (del mensaje de Playwright y de `error-context.md`)

- **CP-03:** tras pulsar «Login» con los campos vacíos no existe `email-error` («element(s) not found»); la página solo muestra «Invalid email or password». Coincide con O3 de la exploración.
- **CP-04:** después de elegir «Price (Low - High)» los precios salen `$20.14, $18.63, $13.41, $12.58, $11.48, $11.14` (descendentes). En la traza de una corrida anterior se ve que al elegir esa opción la aplicación pide `products?q=hammer&sort=price,desc`. Coincide con O1.
- **CP-05:** las 9 tarjetas tienen nombre y precio `$n.nn`, pero la imagen de «Slip Joint Pliers» no carga (ancho natural 0 después de esperar 5 s). El filtro Hammer (pasos 3 y 4) no llegó a ejecutarse. Coincide con O13.
- **CP-06:** los pasos 1 a 7 pasaron: contador 2, total $22.96, y tras cambiar a 3, total $34.44 y contador 3. En el paso 8, después de pulsar el botón de quitar de la fila, «Claw Hammer» sigue en el carrito (`product-title`: se esperaba 0 y hay 1). Lo comprobé a mano en el navegador MCP: el clic va al botón correcto (`<a class="btn btn-danger"><i class="fa fa-remove">`) y después de 3 s el producto sigue ahí y el contador sigue en 1.
- **CP-07:** la dirección y el pago con «Cash on Delivery» se completaron (se pidieron los datos de cuenta y se llenaron, como dice el plan). Después de **un** clic en «Confirm» no aparece `#order-confirmation`: la página se queda en el paso Payment con el texto «Payment was successful» y el botón «Confirm» visible, sin número de factura. Coincide con O9 (en la exploración hicieron falta dos clics).
- **CP-09:** al enviar con el apellido vacío aparecen 2 errores visibles en vez de 1: «Last name is required» y además «Subject is required», aunque el asunto «Customer service» estaba elegido. El envío válido (pasos 3 y 4) no llegó a evaluarse. Coincide con O10.

### Datos que dejó la ejecución en el ambiente compartido

- CP-08 dejó «Cordless Drill 20V» en los favoritos de customer2 (Jack Howe), como prevé el plan.
- CP-07 no generó factura (el pedido no se confirmó con un solo clic).

## 3. Pruebas corregidas

| Caso | Intentos de corrección | Motivo (error mío, no de la aplicación) | Resultado tras corregir |
|---|---|---|---|
| CP-04 | 2 | 1) Usé `expect.poll(...).toSatisfy`, que no existe en `@playwright/test` (`TypeError: ... toSatisfy is not a function`). Lo cambié por una espera con `expect.poll` que devuelve un objeto. 2) Ese mensaje no mostraba la lista de precios; lo reemplacé por `waitForLoadState('networkidle')` más una comparación directa con la lista ordenada, para que el error muestre los precios reales. | Falla por la aplicación (O1). Límite de intentos alcanzado. **Ojo:** `networkidle` no garantiza que el orden ya se haya aplicado. En la corrida de verificación se leyó la lista de búsqueda todavía sin ordenar; en la corrida final se leyó la lista ya ordenada (descendente). Habría que esperar la respuesta `sort=` del servidor; no se cambió porque ya se habían usado los dos intentos. |
| CP-05 | 2 | 1) La imagen se buscaba con `getByRole('img')`, pero las imágenes de las tarjetas no tienen rol accesible «img», así que la prueba agotaba los 30 s. Se cambió a `tarjeta.locator('img')` (etiqueta HTML, sin clase CSS). 2) `scrollIntoViewIfNeeded()` agotaba los 30 s con la imagen rota porque Playwright no la considera visible. Se quitó y se lee `naturalWidth` directamente. | Falla por la aplicación (O13). |
| CP-06 | 1 | El botón de quitar se buscaba con `getByRole('link')`, pero es un `<a>` sin `href` y no tiene rol «link». Se cambió a `getByRole('cell').last().locator('a')` dentro de la fila del producto. | Falla por la aplicación (el producto no se quita; verificado a mano). |

Ninguna corrección cambió un resultado esperado del plan. Calidad de la generación: 7 de 10 pruebas funcionaron al primer intento, sin correcciones (CP-01, 02, 03, 07, 08, 09 y 10).

Otros ajustes (no son correcciones de pruebas):
- `tests/datos.ts`: alineé los valores con la sección 2 del plan. `CONTRASENA_INCORRECTA` pasó a `incorrecta123`, `DIRECCION.estado` a `Wien`, `CUENTA_COD.numero` a `12345678` y `CONTACTO` a Ana Pérez / ana.perez@example.com con el mensaje del plan. También agregué `PRODUCTOS.cordlessDrill` (id 23) y `FILTROS.categoriaHammer` (`category-3`).
- Playwright vacía `qa/evidencia/` (su `outputDir`) en cada corrida. Respaldé las 7 capturas `exploracion-*.png` y las restauré después de la corrida final.

## 4. Salida de Playwright (corrida final, fragmentos literales)

```
Running 10 tests using 1 worker

  ✘   1 [chromium] › tests/carrito.spec.ts:5:7 › Detalle de producto y carrito (R3) › CP-06 · Carrito: cantidad 2, cambio a 3 y quitar producto (7.0s)
  ✘   2 [chromium] › tests/catalogo.spec.ts:12:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» ordenada por precio de menor a mayor (2.3s)
  ✘   3 [chromium] › tests/catalogo.spec.ts:36:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Catálogo y filtro por categoría Hammer (6.7s)
  ✘   4 [chromium] › tests/checkout.spec.ts:5:7 › Checkout (R4) › CP-07 · Compra completa con Cash on Delivery hasta la factura (8.3s)
  ✘   5 [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-09 · Contacto: campo obligatorio vacío y luego envío válido (7.8s)
  ✓   6 [chromium] › tests/favoritos.spec.ts:5:7 › Favoritos (R5) › CP-08 · Favoritos sin sesión y con sesión (6.0s)
  ✓   7 [chromium] › tests/login.spec.ts:5:7 › Inicio de sesión (R1) › CP-01 · Inicio de sesión válido (1.8s)
  ✓   8 [chromium] › tests/login.spec.ts:16:7 › Inicio de sesión (R1) › CP-02 · Inicio de sesión con contraseña incorrecta (1.9s)
  ✘   9 [chromium] › tests/login.spec.ts:27:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (6.0s)
  ✓  10 [chromium] › tests/login.spec.ts:38:7 › Inicio de sesión (R1) › CP-10 · El administrador entra al panel (3.3s)
```

CP-06:
```
    Error: expect(locator).toHaveCount(expected) failed
    Locator:  getByTestId('product-title')
    Expected: 0
    Received: 1
    > 34 |     await expect(page.getByTestId('product-title')).toHaveCount(0);
```

CP-04:
```
    Error: los precios quedan en orden ascendente
    expect(received).toEqual(expected) // deep equality
    - Expected  - 5
    + Received  + 5
      Array [
    -   "$11.14",
    -   "$11.48",
    -   "$12.58",
    -   "$13.41",
    -   "$18.63",
        "$20.14",
    +   "$18.63",
    +   "$13.41",
    +   "$12.58",
    +   "$11.48",
    +   "$11.14",
      ]
```

CP-05:
```
    Error: la imagen de «Slip Joint Pliers» se carga (ancho natural > 0)
    expect(received).toBe(expected) // Object.is equality
    Expected: true
    Received: false
    - Timeout 5000ms exceeded while waiting on the predicate
```

CP-07:
```
    Error: expect(locator).toContainText(expected) failed
    Locator: locator('#order-confirmation')
    Expected substring: "Thanks for your order!"
    Timeout: 5000ms
    Error: element(s) not found
    > 39 |     await expect(page.locator('#order-confirmation')).toContainText('Thanks for your order!');
```

CP-09:
```
    Error: solo debe aparecer el error del apellido
    expect(locator).toHaveCount(expected) failed
    Locator:  getByTestId(/-error$/).visible()
    Expected: 1
    Received: 2
```

CP-03:
```
    Error: expect(locator).toBeVisible() failed
    Locator: getByTestId('email-error')
    Expected: visible
    Timeout: 5000ms
    Error: element(s) not found
```

Resumen final:
```
  6 failed
    [chromium] › tests/carrito.spec.ts:5:7 › Detalle de producto y carrito (R3) › CP-06 · Carrito: cantidad 2, cambio a 3 y quitar producto
    [chromium] › tests/catalogo.spec.ts:12:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» ordenada por precio de menor a mayor
    [chromium] › tests/catalogo.spec.ts:36:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Catálogo y filtro por categoría Hammer
    [chromium] › tests/checkout.spec.ts:5:7 › Checkout (R4) › CP-07 · Compra completa con Cash on Delivery hasta la factura
    [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-09 · Contacto: campo obligatorio vacío y luego envío válido
    [chromium] › tests/login.spec.ts:27:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos
  4 passed (53.5s)
```

Reporte HTML: `qa/reporte-html/` (abrir con `npx playwright show-report qa/reporte-html`).
