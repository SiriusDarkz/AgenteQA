# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: checkout.spec.ts >> Checkout (R4) >> CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1)
- Location: tests/checkout.spec.ts:12:7

# Error details

```
Error: expect(locator).toBeEnabled() failed

Locator:  getByTestId('finish')
Expected: enabled
Received: disabled
Timeout:  5000ms

Call log:
  - Expect "toBeEnabled" getByTestId('finish') with timeout 5000ms
  - waiting for getByTestId('finish')
    14 × locator resolved to <button disabled type="button" data-test="finish" class="btn btn-success" _ngcontent-ng-c1226357352=""> Confirm </button>
       - unexpected value "disabled"

```

```yaml
- button "Confirm" [disabled]
```

# Test source

```ts
  1  | import { test, expect, Locator } from '@playwright/test';
  2  | import { CLIENTES, DIRECCION_FACTURACION, PRODUCTO_CARRITO } from './datos';
  3  | import { iniciarSesion } from './ayudas';
  4  | 
  5  | async function completar(campo: Locator, valor: string) {
  6  |   const etiqueta = await campo.evaluate((el) => el.tagName.toLowerCase());
  7  |   if (etiqueta === 'select') await campo.selectOption({ label: valor });
  8  |   else await campo.fill(valor);
  9  | }
  10 | 
  11 | test.describe('Checkout (R4)', () => {
  12 |   test('CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1)', async ({ page }) => {
  13 |     await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
  14 |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  15 | 
  16 |     // 1. Producto con cantidad 2
  17 |     await page.goto(PRODUCTO_CARRITO.ruta);
  18 |     await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
  19 |     await page.getByTestId('quantity').fill('2');
  20 |     await page.getByTestId('add-to-cart').click();
  21 |     await expect(page.getByTestId('cart-quantity')).toHaveText('2');
  22 | 
  23 |     // 2. Carrito → Proceed to checkout
  24 |     await page.getByTestId('nav-cart').click();
  25 |     await page.getByTestId('proceed-1').click();
  26 | 
  27 |     // 3. Paso Sign in
  28 |     await expect(page.getByText(`Hello ${CLIENTES.principal.nombre}, you are already logged in`)).toBeVisible();
  29 |     await page.getByTestId('proceed-2').click();
  30 | 
  31 |     // 4. Paso Address
  32 |     const d = DIRECCION_FACTURACION;
  33 |     await expect(page.getByTestId('address')).toBeVisible();
  34 |     await completar(page.getByTestId('address'), d.address);
  35 |     await completar(page.getByTestId('city'), d.city);
  36 |     await completar(page.getByTestId('state'), d.state);
  37 |     await completar(page.getByTestId('country'), d.country);
  38 |     await completar(page.getByTestId('postcode'), d.postcode);
  39 |     await expect(page.getByTestId('proceed-3')).toBeEnabled();
  40 |     await page.getByTestId('proceed-3').click();
  41 | 
  42 |     // 5. Paso Payment: Cash on Delivery no debe pedir datos de otro método
  43 |     await page.getByTestId('payment-method').selectOption({ label: 'Cash on Delivery' });
> 44 |     await expect(page.getByTestId('finish')).toBeEnabled();
     |                                              ^ Error: expect(locator).toBeEnabled() failed
  45 | 
  46 |     // 6. Confirmar
  47 |     await page.getByTestId('finish').click();
  48 |     const pagoExitoso = page.getByText('Payment was successful');
  49 |     if (await pagoExitoso.isVisible({ timeout: 3_000 }).catch(() => false)) {
  50 |       await page.getByTestId('finish').click();
  51 |     }
  52 |     const confirmacion = page.locator('#order-confirmation');
  53 |     await expect(confirmacion).toContainText('Thanks for your order! Your invoice number is INV-');
  54 |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  55 | 
  56 |     // 7. Número de factura
  57 |     const factura = ((await confirmacion.textContent()) ?? '').match(/INV-\d+/)?.[0] ?? '';
  58 |     console.log('CP-08 factura:', factura);
  59 |     expect(factura).not.toBe('');
  60 | 
  61 |     // 8. My account → Invoices
  62 |     await page.getByTestId('nav-user-menu').click();
  63 |     await page.getByTestId('nav-my-invoices').click();
  64 |     const filaFactura = page.getByRole('row').filter({ hasText: factura });
  65 |     await expect(filaFactura).toBeVisible();
  66 |     await expect(filaFactura).toContainText(PRODUCTO_CARRITO.total2);
  67 |   });
  68 | });
  69 | 
```