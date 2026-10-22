# Resultados de la ejecución · Toolshop (with bugs)

## 1. Resumen

| Dato | Valor |
|---|---|
| Aplicación | https://with-bugs.practicesoftwaretesting.com |
| Plan | `qa/plan-de-pruebas.md` (Estado: APROBADO, 2026-10-21 21:07) |
| Casos planificados | 10 (CP-01 a CP-10) |
| Casos ejecutados | 10 |
| Pasaron | 2 (CP-01, CP-02) |
| Fallaron | 8 (CP-03 a CP-10) |
| Duración total | 1.3 min (según Playwright) |
| Fecha y hora | 2026-10-21, de 21:13:26 a 21:14:46 (hora local) |
| Navegador | Chromium (`@playwright/test` 1.64.1), 1 worker, sin reintentos |
| Comando | `QA_BASE_URL=https://with-bugs.practicesoftwaretesting.com npx playwright test tests/login.spec.ts tests/catalogo.spec.ts tests/carrito.spec.ts tests/checkout.spec.ts tests/favoritos.spec.ts tests/contacto.spec.ts --reporter=list,html --output=qa/evidencia/ejecucion` |

Notas de ejecución:
- `playwright.config.ts` apunta por defecto a saucedemo.com. Por eso la URL de Toolshop se pasó con la variable `QA_BASE_URL`, que la propia configuración prevé. No se modificó la configuración.
- Se usó `--output=qa/evidencia/ejecucion` porque Playwright vacía la carpeta de salida antes de cada corrida, y con `qa/evidencia` se habrían borrado las capturas de la exploración.
- Con `--reporter=list,html` en la línea de comandos, Playwright ignora la carpeta de la configuración y escribió el reporte HTML en `playwright-report/`. Se movió a `qa/reporte-html/`.
- `tests/ejemplo.spec.ts` (humo de saucedemo) no se ejecutó porque no corresponde a esta aplicación.
- CP-08 falló antes de confirmar, así que esta corrida **no** creó ninguna factura.

## 2. Tabla de resultados

| ID | Título | Usuario | Resultado | Duración | Archivo de prueba | Evidencia (si falló) |
|----|--------|---------|-----------|----------|-------------------|----------------------|
| CP-01 | Inicio de sesión válido (R1) | customer@practicesoftwaretesting.com | PASÓ | 2.1 s | `tests/login.spec.ts` | — |
| CP-02 | Inicio de sesión con contraseña incorrecta (R1 · Esc. 4) | customer@practicesoftwaretesting.com | PASÓ | 2.1 s | `tests/login.spec.ts` | — |
| CP-03 | Inicio de sesión con campos vacíos (R1 · Esc. 4) | — | FALLÓ | 11.3 s | `tests/login.spec.ts` | `qa/evidencia/ejecucion/login-Inicio-de-sesión-R1--1f368-n-campos-vacíos-R1-·-Esc-4--chromium/` |
| CP-04 | Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2) | — | FALLÓ | 4.6 s | `tests/catalogo.spec.ts` | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-2fe93-ecio-ascendente-R2-·-Esc-2--chromium/` |
| CP-05 | Orden por nombre A-Z y filtro por categoría Hammer (R2) | — | FALLÓ | 2.8 s | `tests/catalogo.spec.ts` | `qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-856eb-ro-por-categoría-Hammer-R2--chromium/` |
| CP-06 | Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3) | customer@practicesoftwaretesting.com | FALLÓ | 21.8 s | `tests/carrito.spec.ts` | `qa/evidencia/ejecucion/carrito-Detalle-de-product-a3f6f-es-recalculados-R3-·-Esc-3--chromium/` |
| CP-07 | Quitar un producto del carrito (R3) | customer@practicesoftwaretesting.com | FALLÓ | 8.3 s | `tests/carrito.spec.ts` | `qa/evidencia/ejecucion/carrito-Detalle-de-product-fb900-un-producto-del-carrito-R3--chromium/` |
| CP-08 | Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1) | customer@practicesoftwaretesting.com | FALLÓ | 8.4 s | `tests/checkout.spec.ts` | `qa/evidencia/ejecucion/checkout-Checkout-R4-CP-08-57dd9-asta-la-factura-R4-·-Esc-1--chromium/` |
| CP-09 | Favoritos: aviso sin sesión y alta con sesión (R5) | customer@practicesoftwaretesting.com | FALLÓ | 9.7 s | `tests/favoritos.spec.ts` | `qa/evidencia/ejecucion/favoritos-Favoritos-R5-CP--ccdef-esión-y-alta-con-sesión-R5--chromium/` |
| CP-10 | Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5) | — | FALLÓ | 6.0 s | `tests/contacto.spec.ts` | `qa/evidencia/ejecucion/contacto-Contacto-R6-CP-10-4ee28-go-envío-válido-R6-·-Esc-5--chromium/` |

Cada carpeta de evidencia contiene `test-failed-1.png` (captura), `error-context.md` (snapshot de accesibilidad de la página al fallar) y `trace.zip` (ábrelo con `npx playwright show-trace <ruta>/trace.zip`).

Qué falló en cada caso (de la salida de Playwright):

| ID | Punto de fallo | Esperado | Obtenido |
|----|----------------|----------|----------|
| CP-03 | Aviso de obligatorio junto a correo y contraseña | Mensaje con «required» en `email-error` y `password-error` | Esos elementos no existen. La página solo muestra «Invalid email or password» (`error-context.md`) |
| CP-04 | Resultados de la búsqueda y orden por precio | Incluye «Sledgehammer»; precios ascendentes | Sin «Sledgehammer»; precios 20.14, 18.63, 13.41, 12.58, 11.48, 11.14 (descendentes). Los 6 nombres sí contienen «hammer» |
| CP-05 | Orden «Name (A - Z)» | Orden alfabético ascendente | Wood Saw, Thor Hammer, …, Open-end Spanners (Set) (Z → A). El filtro Hammer sí cumplió: 7 productos, todos con «hammer» |
| CP-06 | Total de línea en el carrito | $28.30 (2 u.) y $42.45 (3 u.) | «$00.00» en ambos casos. Precio unitario, total del carrito y contador sí correctos (esas aserciones blandas pasaron) |
| CP-07 | Fila tras pulsar quitar | 0 filas con «Combination Pliers» | 1 fila; el producto sigue en el carrito |
| CP-08 | Botón «Confirm» con «Cash on Delivery» | Habilitado | `<button disabled … data-test="finish"> Confirm </button>`. La prueba se detiene aquí (pasos 6–8 no se ejecutaron) |
| CP-09 | Aviso al agregar a favoritos con sesión | Ningún aviso de error | «Oeps, something went wrong.». El aviso sin sesión (paso 1) y la presencia de «Bolt Cutters» en Favorites (paso 4) sí cumplieron |
| CP-10 | Envío con Email vacío | «Email is required» junto a Email y sin confirmación | No aparece `email-error`; el formulario se envía y muestra «Thanks for your message! We will contact you shortly.» con el Email vacío |

Observaciones para el análisis (sin conclusiones de defecto, eso es el paso 4):
- CP-05 compara sin distinguir mayúsculas: el plan pide «contienen Hammer», y «Sledgehammer» lo contiene en minúscula. Se interpretó igual que en CP-04.
- CP-10 se comporta distinto que en la exploración (O-9). Allí el asunto puesto por programa quedaba inválido y se mostraban «Email is required» y «Subject is required». Aquí el asunto se eligió con el teclado, quedó válido, y el formulario se envió sin Email.
- CP-09: el producto 3 es «Bolt Cutters». Antes del paso 3 la prueba lo quita de Favorites si ya estaba (precondición del plan).

## 3. Pruebas corregidas

| ID | Intentos | Motivo de la corrección | Cambio |
|----|----------|-------------------------|--------|
| CP-01 | 2 (pasó en el 2.º) | Localizador ambiguo: `getByPlaceholder('Your password *')` encontraba 2 elementos (el componente `app-password-input` y el `input`), violación de modo estricto | Se usa `getByTestId('password')` |
| CP-09 | 2 (falla por la aplicación en el 2.º) | Aserción mal construida: `toHaveCount(0)` sobre los avisos de error reintentaba hasta que el toast desaparecía solo, así que la prueba **pasó en falso** con «Oeps, something went wrong.» en pantalla | Se capturan los textos de los avisos en cuanto aparecen y se comprueba esa lista |
| CP-10 | 2 (falla por la aplicación en el 2.º) | Interacción incorrecta con el select Subject: `ArrowDown` + `Tab` en Chromium headless no cambiaba la opción (quedaba «Select a subject») | Se enfoca el select, se teclea «Cus» y se sale con Tab. Una sonda aparte confirmó `customer-service` con clase `ng-dirty ng-valid` |

Se revisaron y **no** se corrigieron porque el fallo es de la aplicación:
- CP-03: el snapshot no tiene ningún texto «required», solo «Invalid email or password».
- CP-07: se hizo una sonda aparte (fuera de `tests/`). El único control de quitar es `<a class="btn btn-danger"><i class="fa fa-remove"></i></a>` y, tras un clic real, la fila y el contador siguieron igual. El localizador usa la clase CSS `btn-danger` porque el botón no tiene `data-test` ni nombre accesible (ver `qa/exploracion.md`).

Métrica: 10 pruebas generadas, 7 correctas al primer intento y 3 corregidas (2 por localizador o interacción, 1 por una aserción que daba un falso positivo). Ningún resultado esperado se cambió.

## 4. Salida de Playwright (corrida definitiva, extracto literal)

```
Running 10 tests using 1 worker
  ✘   1 [chromium] › tests/carrito.spec.ts:12:7 › Detalle de producto y carrito (R3) › CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3) (21.8s)
  ✘   2 [chromium] › tests/carrito.spec.ts:37:7 › Detalle de producto y carrito (R3) › CP-07 · Quitar un producto del carrito (R3) (8.3s)
CP-04 resultados: Claw Hammer with Fiberglass Handle $20.14 | Court Hammer $18.63 | Claw Hammer with Shock Reduction Grip $13.41 | Hammer $12.58 | Claw Hammer $11.48 | Thor Hammer $11.14
  ✘   3 [chromium] › tests/catalogo.spec.ts:6:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2) (4.6s)
CP-05 orden A-Z: Wood Saw | Thor Hammer | Slip Joint Pliers | Sledgehammer | Sheet Sander | Random Orbit Sander | Pliers | Phillips Screwdriver | Open-end Spanners (Set)
CP-05 categoría Hammer: Thor Hammer | Sledgehammer | Hammer | Court Hammer | Claw Hammer with Shock Reduction Grip | Claw Hammer with Fiberglass Handle | Claw Hammer
  ✘   4 [chromium] › tests/catalogo.spec.ts:30:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Orden por nombre A-Z y filtro por categoría Hammer (R2) (2.8s)
  ✘   5 [chromium] › tests/checkout.spec.ts:12:7 › Checkout (R4) › CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1) (8.4s)
  ✘   6 [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5) (6.0s)
CP-09 producto 3: Bolt Cutters
CP-09 avisos tras agregar con sesión: [ 'Oeps, something went wrong.' ]
  ✘   7 [chromium] › tests/favoritos.spec.ts:6:7 › Favoritos (R5) › CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5) (9.7s)
  ✓   8 [chromium] › tests/login.spec.ts:5:7 › Inicio de sesión (R1) › CP-01 · Inicio de sesión válido (R1) (2.1s)
  ✓   9 [chromium] › tests/login.spec.ts:19:7 › Inicio de sesión (R1) › CP-02 · Inicio de sesión con contraseña incorrecta (R1 · Esc. 4) (2.1s)
  ✘  10 [chromium] › tests/login.spec.ts:30:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4) (11.3s)
  1) [chromium] › tests/carrito.spec.ts:12:7 › Detalle de producto y carrito (R3) › CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3) 
    Error: expect(locator).toHaveText(expected) failed
    Locator:  getByTestId('line-price')
    Expected: "$28.30"
    Received: "$00.00"
      - Expect "soft toHaveText" getByTestId('line-price') with timeout 5000ms
      - waiting for getByTestId('line-price')
        14 × locator resolved to <td data-test="line-price" _ngcontent-ng-c1226357352="" class="col-md-2 align-middle">$00.00</td>
           - unexpected value "$00.00"
    Error: expect(locator).toHaveText(expected) failed
    Locator:  getByTestId('line-price')
    Expected: "$42.45"
    Received: "$00.00"
      - Expect "soft toHaveText" getByTestId('line-price') with timeout 5000ms
      - waiting for getByTestId('line-price')
        14 × locator resolved to <td data-test="line-price" _ngcontent-ng-c1226357352="" class="col-md-2 align-middle">$00.00</td>
           - unexpected value "$00.00"
    Error Context: qa/evidencia/ejecucion/carrito-Detalle-de-product-a3f6f-es-recalculados-R3-·-Esc-3--chromium/error-context.md
  2) [chromium] › tests/carrito.spec.ts:37:7 › Detalle de producto y carrito (R3) › CP-07 · Quitar un producto del carrito (R3) 
    Error: expect(locator).toHaveCount(expected) failed
    Locator:  getByRole('row').filter({ hasText: 'Combination Pliers' })
    Expected: 0
    Received: 1
      - Expect "toHaveCount" getByRole('row').filter({ hasText: 'Combination Pliers' }) with timeout 5000ms
      - waiting for getByRole('row').filter({ hasText: 'Combination Pliers' })
           - unexpected value "1"
    Error Context: qa/evidencia/ejecucion/carrito-Detalle-de-product-fb900-un-producto-del-carrito-R3--chromium/error-context.md
  3) [chromium] › tests/catalogo.spec.ts:6:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2) 
    Error: Los resultados deben incluir «Sledgehammer»
    Expected value: "Sledgehammer"
    Received array: ["Claw Hammer with Fiberglass Handle", "Court Hammer", "Claw Hammer with Shock Reduction Grip", "Hammer", "Claw Hammer", "Thor Hammer"]
    Error: Los precios deben quedar de menor a mayor
    - Expected  - 5
    + Received  + 5
      Array [
    -   11.14,
    -   11.48,
    -   12.58,
    -   13.41,
    -   18.63,
        20.14,
    +   18.63,
    +   13.41,
    +   12.58,
    +   11.48,
    +   11.14,
      ]
    Error Context: qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-2fe93-ecio-ascendente-R2-·-Esc-2--chromium/error-context.md
  4) [chromium] › tests/catalogo.spec.ts:30:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Orden por nombre A-Z y filtro por categoría Hammer (R2) 
    Error: Los nombres deben quedar en orden alfabético ascendente
    - Expected  - 8
    + Received  + 8
      Array [
    -   "Open-end Spanners (Set)",
    -   "Phillips Screwdriver",
    -   "Pliers",
    -   "Random Orbit Sander",
    -   "Sheet Sander",
    -   "Sledgehammer",
    -   "Slip Joint Pliers",
    -   "Thor Hammer",
        "Wood Saw",
    +   "Thor Hammer",
    +   "Slip Joint Pliers",
    +   "Sledgehammer",
    +   "Sheet Sander",
    +   "Random Orbit Sander",
    +   "Pliers",
    +   "Phillips Screwdriver",
    +   "Open-end Spanners (Set)",
      ]
    Error Context: qa/evidencia/ejecucion/catalogo-Catálogo-búsqueda-856eb-ro-por-categoría-Hammer-R2--chromium/error-context.md
  5) [chromium] › tests/checkout.spec.ts:12:7 › Checkout (R4) › CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1) 
    Error: expect(locator).toBeEnabled() failed
    Locator:  getByTestId('finish')
    Expected: enabled
    Received: disabled
      - Expect "toBeEnabled" getByTestId('finish') with timeout 5000ms
      - waiting for getByTestId('finish')
        14 × locator resolved to <button disabled type="button" data-test="finish" class="btn btn-success" _ngcontent-ng-c1226357352=""> Confirm </button>
           - unexpected value "disabled"
    Error Context: qa/evidencia/ejecucion/checkout-Checkout-R4-CP-08-57dd9-asta-la-factura-R4-·-Esc-1--chromium/error-context.md
  6) [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5) 
    Error: expect(locator).toContainText(expected) failed
    Locator: getByTestId('email-error')
    Expected substring: "Email is required"
    Error: element(s) not found
      - Expect "toContainText" getByTestId('email-error') with timeout 5000ms
      - waiting for getByTestId('email-error')
    Error Context: qa/evidencia/ejecucion/contacto-Contacto-R6-CP-10-4ee28-go-envío-válido-R6-·-Esc-5--chromium/error-context.md
  7) [chromium] › tests/favoritos.spec.ts:6:7 › Favoritos (R5) › CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5) 
    Error: No debe aparecer aviso de error
    - Expected  - 1
    + Received  + 3
    - Array []
    + Array [
    +   "Oeps, something went wrong.",
    + ]
    Error Context: qa/evidencia/ejecucion/favoritos-Favoritos-R5-CP--ccdef-esión-y-alta-con-sesión-R5--chromium/error-context.md
  8) [chromium] › tests/login.spec.ts:30:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4) 
    Error: expect(locator).toContainText(expected) failed
    Locator: getByTestId('email-error')
    Expected pattern: /required/i
    Error: element(s) not found
      - Expect "soft toContainText" getByTestId('email-error') with timeout 5000ms
      - waiting for getByTestId('email-error')
    Error: expect(locator).toContainText(expected) failed
    Locator: getByTestId('password-error')
    Expected pattern: /required/i
    Error: element(s) not found
      - Expect "soft toContainText" getByTestId('password-error') with timeout 5000ms
      - waiting for getByTestId('password-error')
    Error Context: qa/evidencia/ejecucion/login-Inicio-de-sesión-R1--1f368-n-campos-vacíos-R1-·-Esc-4--chromium/error-context.md
  8 failed
    [chromium] › tests/carrito.spec.ts:12:7 › Detalle de producto y carrito (R3) › CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3) 
    [chromium] › tests/carrito.spec.ts:37:7 › Detalle de producto y carrito (R3) › CP-07 · Quitar un producto del carrito (R3) 
    [chromium] › tests/catalogo.spec.ts:6:7 › Catálogo, búsqueda y orden (R2) › CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2) 
    [chromium] › tests/catalogo.spec.ts:30:7 › Catálogo, búsqueda y orden (R2) › CP-05 · Orden por nombre A-Z y filtro por categoría Hammer (R2) 
    [chromium] › tests/checkout.spec.ts:12:7 › Checkout (R4) › CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1) 
    [chromium] › tests/contacto.spec.ts:5:7 › Contacto (R6) › CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5) 
    [chromium] › tests/favoritos.spec.ts:6:7 › Favoritos (R5) › CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5) 
    [chromium] › tests/login.spec.ts:30:7 › Inicio de sesión (R1) › CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4) 
  2 passed (1.3m)
```
