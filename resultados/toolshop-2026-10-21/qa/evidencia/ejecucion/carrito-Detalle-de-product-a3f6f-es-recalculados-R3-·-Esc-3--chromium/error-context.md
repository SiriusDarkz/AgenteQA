# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: carrito.spec.ts >> Detalle de producto y carrito (R3) >> CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3)
- Location: tests/carrito.spec.ts:12:7

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator:  getByTestId('line-price')
Expected: "$28.30"
Received: "$00.00"
Timeout:  5000ms

Call log:
  - Expect "soft toHaveText" getByTestId('line-price') with timeout 5000ms
  - waiting for getByTestId('line-price')
    14 × locator resolved to <td data-test="line-price" _ngcontent-ng-c1226357352="" class="col-md-2 align-middle">$00.00</td>
       - unexpected value "$00.00"

```

```yaml
- cell "$00.00"
```

```
Error: expect(locator).toHaveText(expected) failed

Locator:  getByTestId('line-price')
Expected: "$42.45"
Received: "$00.00"
Timeout:  5000ms

Call log:
  - Expect "soft toHaveText" getByTestId('line-price') with timeout 5000ms
  - waiting for getByTestId('line-price')
    14 × locator resolved to <td data-test="line-price" _ngcontent-ng-c1226357352="" class="col-md-2 align-middle">$00.00</td>
       - unexpected value "$00.00"

```

```yaml
- cell "$00.00"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { CLIENTES, PRODUCTO_CARRITO } from './datos';
  3  | import { iniciarSesion } from './ayudas';
  4  | 
  5  | test.describe('Detalle de producto y carrito (R3)', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
  8  |     // Precondición: carrito vacío (contexto de navegador nuevo, sin contador en la barra).
  9  |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  10 |   });
  11 | 
  12 |   test('CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3)', async ({ page }) => {
  13 |     await page.goto(PRODUCTO_CARRITO.ruta);
  14 |     await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
  15 |     await expect(page.getByTestId('unit-price')).toHaveText(PRODUCTO_CARRITO.precio);
  16 |     await expect(page.getByTestId('product-description')).not.toBeEmpty();
  17 | 
  18 |     await page.getByTestId('quantity').fill('2');
  19 |     await page.getByTestId('add-to-cart').click();
  20 |     await expect(page.getByTestId('cart-quantity')).toHaveText('2');
  21 | 
  22 |     await page.getByTestId('nav-cart').click();
  23 |     await expect(page).toHaveURL(/#\/checkout/);
  24 |     await expect(page.getByTestId('product-title')).toContainText(PRODUCTO_CARRITO.nombre);
  25 |     await expect(page.getByTestId('product-quantity')).toHaveValue('2');
  26 |     await expect.soft(page.getByTestId('product-price')).toHaveText(PRODUCTO_CARRITO.precioMostrado);
  27 |     await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total2);
  28 |     await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total2);
  29 | 
  30 |     await page.getByTestId('product-quantity').fill('3');
  31 |     await page.getByTestId('product-quantity').press('Enter');
> 32 |     await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total3);
     |                                                       ^ Error: expect(locator).toHaveText(expected) failed
  33 |     await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total3);
  34 |     await expect.soft(page.getByTestId('cart-quantity')).toHaveText('3');
  35 |   });
  36 | 
  37 |   test('CP-07 · Quitar un producto del carrito (R3)', async ({ page }) => {
  38 |     await page.goto(PRODUCTO_CARRITO.ruta);
  39 |     await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
  40 |     await expect(page.getByTestId('quantity')).toHaveValue('1');
  41 |     await page.getByTestId('add-to-cart').click();
  42 |     await expect(page.getByTestId('cart-quantity')).toHaveText('1');
  43 | 
  44 |     await page.getByTestId('nav-cart').click();
  45 |     const fila = page.getByRole('row').filter({ hasText: PRODUCTO_CARRITO.nombre });
  46 |     await expect(fila).toBeVisible();
  47 |     // El botón de quitar no tiene data-test ni nombre accesible (exploración, checkout paso 1).
  48 |     await fila.locator('a.btn-danger').click();
  49 | 
  50 |     await expect(fila).toHaveCount(0);
  51 |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  52 |   });
  53 | });
  54 | 
```