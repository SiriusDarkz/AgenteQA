# Resultados de la ejecución · Toolshop (with bugs)

## 1. Resumen

| Dato | Valor |
|---|---|
| Aplicación | https://with-bugs.practicesoftwaretesting.com |
| Plan | `qa/plan-de-pruebas.md` (Estado: APROBADO, 2026-10-22 20:55) |
| Fecha y hora | 2026-10-22 20:57:23 (corrida completa); 20:59 (nueva corrida de CP-03) |
| Navegador | Chromium · `@playwright/test` 1.64.1 · 1 worker, sin reintentos |
| Casos planificados | 10 |
| Casos ejecutados | 10 |
| Pasaron | **5** (CP-01, CP-02, CP-06, CP-08, CP-09) |
| Fallaron | **5** (CP-03, CP-04, CP-05, CP-07, CP-10) |
| Duración total | 1.3 min (corrida completa, según Playwright) |
| Comando | `QA_BASE_URL=https://with-bugs.practicesoftwaretesting.com npx playwright test tests/login.spec.ts tests/catalogo.spec.ts tests/carrito.spec.ts tests/checkout.spec.ts tests/favoritos.spec.ts tests/contacto.spec.ts --reporter=list,html --output=qa/evidencia/ejecucion` |
| Reporte HTML | `qa/reporte-html/index.html` → `npx playwright show-report qa/reporte-html` |

Notas de ejecución:
- `playwright.config.ts` apunta por defecto a saucedemo.com. La URL de Toolshop se pasó con la variable `QA_BASE_URL`, que la propia configuración admite. No se modificó la configuración.
- `--output=qa/evidencia/ejecucion` hace que Playwright no borre las capturas de la exploración que están en `qa/evidencia/` (Playwright vacía su carpeta de salida al empezar cada corrida).
- `tests/ejemplo.spec.ts` (prueba de humo de SauceDemo) no se ejecutó porque no es de esta aplicación.
- Con `--reporter=html` en la línea de comandos, Playwright dejó el reporte en `playwright-report/`; se movió a `qa/reporte-html/`. Ese reporte corresponde a la corrida completa, así que muestra la primera versión de CP-03 (ver sección 3).
- CP-08 creó un pedido real en el ambiente compartido. La prueba pasó y no imprime el número de factura; Playwright solo guarda trazas cuando una prueba falla, así que aquí no queda constancia del número.
- `tests/datos.ts` se reemplazó: tenía datos de SauceDemo y ahora tiene los de la sección 2 del plan, más la función `iniciarSesion`.
- En algunas pruebas se usan aserciones `expect.soft` para que un fallo intermedio no oculte los pasos siguientes: CP-03 (mensajes de obligatorio), CP-05 (orden A–Z), CP-07 (`line-price`) y CP-10 (errores de los demás campos en el paso 3). Una aserción soft que falla también hace fallar la prueba.

## 2. Tabla de resultados

| ID | Título | Usuario | Resultado | Duración | Archivo de prueba | Evidencia |
|---|---|---|---|---|---|---|
| CP-01 | Inicio de sesión válido | customer@practicesoftwaretesting.com | PASÓ | 2.1s | `tests/login.spec.ts` | — |
| CP-02 | Inicio de sesión con contraseña incorrecta | customer@practicesoftwaretesting.com | PASÓ | 1.8s | `tests/login.spec.ts` | — |
| CP-03 | Inicio de sesión con campos vacíos | (ninguno) | FALLÓ | 11.1s (corrida completa) · 6.1s (nueva corrida) | `tests/login.spec.ts` | `qa/evidencia/ejecucion-cp03/login-Inicio-de-sesión-R1--ef8b8-de-sesión-con-campos-vacíos-chromium/` (versión final) · `qa/evidencia/ejecucion/login-Inicio-de-sesión-R1--ef8b8-de-sesión-con-campos-vacíos-chromium/` (primera versión) |
| CP-04 | Búsqueda «hammer» con orden por precio de menor a mayor | (ninguno) | FALLÓ | 7.6s | `tests/catalogo.spec.ts` | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-600d9-por-precio-de-menor-a-mayor-chromium/` |
| CP-05 | Orden por nombre A–Z y Z–A | (ninguno) | FALLÓ | 7.7s | `tests/catalogo.spec.ts` | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-a110b--Orden-por-nombre-A–Z-y-Z–A-chromium/` |
| CP-06 | Filtros por categoría y por marca | (ninguno) | PASÓ | 3.2s | `tests/catalogo.spec.ts` | — |
| CP-07 | Carrito: cantidad 2, contador, total y cambio a 3 | customer@practicesoftwaretesting.com | FALLÓ | 16.0s | `tests/carrito.spec.ts` | `qa/evidencia/ejecucion/carrito-Detalle-de-product-4fb10-contador-total-y-cambio-a-3-chromium/` |
| CP-08 | Compra completa con Cash on Delivery hasta la factura | customer@practicesoftwaretesting.com | PASÓ | 6.3s | `tests/checkout.spec.ts` | — |
| CP-09 | Favoritos sin sesión y con sesión | (ninguno) y customer@practicesoftwaretesting.com | PASÓ | 8.6s | `tests/favoritos.spec.ts` | — |
| CP-10 | Contacto con campo vacío y con todos los campos válidos | (ninguno) | FALLÓ | 12.2s | `tests/contacto.spec.ts` | `qa/evidencia/ejecucion/contacto-Contacto-R6-CP-10-e31f0-on-todos-los-campos-válidos-chromium/` |

Cada carpeta de evidencia contiene `test-failed-1.png` (captura), `trace.zip` (traza; se abre con `npx playwright show-trace <ruta>/trace.zip`) y `error-context.md` (snapshot de accesibilidad de la página en el momento del fallo).

Qué falló, según la salida de Playwright:
- **CP-03**: después de pulsar «Login» con los campos vacíos no aparece ningún texto «required» (`getByText(/required/i)`: esperado 2, recibido 0). El snapshot solo muestra «Invalid email or password». Coincide con O-03.
- **CP-04**: con «Price (Low - High)» los precios salen de mayor a menor: `$20.14, $18.63, $13.41, $12.58, $11.48, $11.14`. Coincide con O-05.
- **CP-05**: con «Name (A - Z)» los nombres salen de Z a A: `Thor Hammer, Hammer, Court Hammer, Claw Hammer with Shock Reduction Grip, Claw Hammer with Fiberglass Handle, Claw Hammer`. La aserción con Z–A (no soft) no aparece entre los errores, así que pasó. Coincide con O-05.
- **CP-07**: `line-price` muestra `$00.00` con 2 unidades (se esperaba `$22.96`) y con 3 (se esperaba `$34.44`). `cart-total` y `cart-quantity` sí dieron lo esperado, porque esas aserciones (no soft) no fallaron. Coincide con O-08.
- **CP-10**: en el paso 3, `subject-error` está visible aunque el asunto «Customer service» está elegido. En el paso 5, con todos los campos llenos, sigue visible un mensaje `*-error` (`locator('[data-test$="-error"]:visible')`: esperado 0, recibido 1), así que no se llega a ver la confirmación. Coincide con O-13.

## 3. Pruebas corregidas

| ID | Intentos | Motivo de la corrección | Resultado tras corregir |
|---|---|---|---|
| CP-03 | 1 corrección (2 corridas) | La primera versión usaba `getByTestId('email-error')` y `getByTestId('password-error')`. Esos `data-test` los supuse yo y no salen de `qa/exploracion.md`, así que el fallo «element(s) not found» no bastaba para atribuirlo a la aplicación. Se cambió por `getByText(/required/i)` con 2 apariciones esperadas, que no depende de un localizador inventado. El resultado esperado del plan no cambió. | Sigue fallando, ahora por la aplicación: 0 mensajes «required» en la página (O-03) |

Las otras 9 pruebas no necesitaron correcciones: 9 de 10 funcionaron bien a la primera.

## 4. Salida de Playwright

Corrida completa (extracto literal):

```
Running 10 tests using 1 worker

  ✘   1 [chromium] › tests/carrito.spec.ts:5:7 › Detalle de producto y carrito (R3) › CP-07 · Carrito: cantidad 2, contador, total y cambio a 3 (16.0s)
  ✘   2 [chromium] › tests/catalogo.spec.ts:17:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» con orden por precio de menor a mayor (7.6s)
  ✘   3 [chromium] › tests/catalogo.spec.ts:31:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Orden por nombre A–Z y Z–A (7.7s)
  ✓   4 [chromium] › tests/catalogo.spec.ts:42:7 › Catálogo, búsqueda y orden (R2) › CP-06 · Filtros por categoría y por marca (3.2s)
  ✓   5 [chromium] › tests/checkout.spec.ts:5:7 › Checkout (R4) › CP-08 · Compra completa con Cash on Delivery hasta la factura (6.3s)
  ✘   6 [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-10 · Contacto con campo vacío y con todos los campos válidos (12.2s)
  ✓   7 [chromium] › tests/favoritos.spec.ts:5:7 › Favoritos (R5) › CP-09 · Favoritos sin sesión y con sesión (8.6s)
  ✓   8 [chromium] › tests/login.spec.ts:5:7 › Inicio de sesión (R1) › CP-01 · Inicio de sesión válido (2.1s)
  ✓   9 [chromium] › tests/login.spec.ts:17:7 › Inicio de sesión (R1) › CP-02 · Inicio de sesión con contraseña incorrecta (1.8s)
  ✘  10 [chromium] › tests/login.spec.ts:28:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (11.1s)
```

CP-07:
```
    Error: expect(locator).toHaveText(expected) failed

    Locator:  getByTestId('line-price')
    Expected: "$22.96"
    Received: "$00.00"
...
    Error: expect(locator).toHaveText(expected) failed

    Locator:  getByTestId('line-price')
    Expected: "$34.44"
    Received: "$00.00"
```

CP-04:
```
    Error: expect(locator).toHaveText(expected) failed

    Locator: getByTestId('product-price')
    Timeout: 5000ms
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
    Error: expect(locator).toHaveText(expected) failed

    Locator: getByTestId('product-name')
    Timeout: 5000ms
    - Expected  - 6
    + Received  + 6

      Array [
    -   "Claw Hammer",
    -   "Claw Hammer with Fiberglass Handle",
    -   "Claw Hammer with Shock Reduction Grip",
    -   "Court Hammer",
    -   "Hammer",
    -   "Thor Hammer",
    +   " Thor Hammer ",
    +   " Hammer ",
    +   " Court Hammer ",
    +   " Claw Hammer with Shock Reduction Grip ",
    +   " Claw Hammer with Fiberglass Handle ",
    +   " Claw Hammer ",
      ]
```

CP-10:
```
    Error: sin error en subject

    expect(locator).toBeHidden() failed

    Locator:  getByTestId('subject-error')
    Expected: hidden
    Received: visible
...
    Error: expect(locator).toHaveCount(expected) failed

    Locator:  locator('[data-test$="-error"]:visible')
    Expected: 0
    Received: 1
```

CP-03 (primera versión, localizador supuesto):
```
    Error: expect(locator).toContainText(expected) failed

    Locator: getByTestId('email-error')
    Expected pattern: /required/i
    Timeout: 5000ms
    Error: element(s) not found
```

Resumen final de la corrida completa:
```
  5 failed
    [chromium] › tests/carrito.spec.ts:5:7 › Detalle de producto y carrito (R3) › CP-07 · Carrito: cantidad 2, contador, total y cambio a 3 
    [chromium] › tests/catalogo.spec.ts:17:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» con orden por precio de menor a mayor 
    [chromium] › tests/catalogo.spec.ts:31:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Orden por nombre A–Z y Z–A 
    [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-10 · Contacto con campo vacío y con todos los campos válidos 
    [chromium] › tests/login.spec.ts:28:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos 
  5 passed (1.3m)
```

Nueva corrida de CP-03 (`npx playwright test tests/login.spec.ts -g "CP-03" --reporter=list --output=qa/evidencia/ejecucion-cp03`):
```
Running 1 test using 1 worker

  ✘  1 [chromium] › tests/login.spec.ts:28:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (6.1s)

    Error: expect(locator).toHaveCount(expected) failed

    Locator:  getByText(/required/i)
    Expected: 2
    Received: 0
    Timeout:  5000ms
```
