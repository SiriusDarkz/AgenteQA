import { test, expect } from '@playwright/test';
import { CUENTA_COD, DIRECCION, PRODUCTOS, iniciarSesion } from './datos';

test.describe('Checkout (R4)', () => {
  test('CP-07 · Compra completa con Cash on Delivery hasta la factura', async ({ page }) => {
    await iniciarSesion(page);

    // 1. Agregar Claw Hammer con cantidad 1
    await page.goto(`/#/product/${PRODUCTOS.clawHammer.id}`);
    await expect(page.getByTestId('quantity')).toHaveValue('1');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toBeVisible();

    // 2. Carrito → Proceed to checkout
    await page.getByTestId('nav-cart').click();
    await page.getByTestId('proceed-1').click();

    // 3. Sign in
    await page.getByTestId('proceed-2').click();

    // 4. Address: completar State / Postcode solo si vienen vacíos o con «missing value»
    const state = page.getByTestId('state');
    const postcode = page.getByTestId('postcode');
    await expect(page.getByTestId('address')).toHaveValue(/.+/);
    const incompleto = (v: string) => v.trim() === '' || /missing value/i.test(v);
    if (incompleto(await state.inputValue())) await state.fill(DIRECCION.estado);
    if (incompleto(await postcode.inputValue())) await postcode.fill(DIRECCION.codigoPostal);
    await page.getByTestId('proceed-3').click();

    // 5. Payment: Cash on Delivery (datos de cuenta solo si se piden)
    await page.getByTestId('payment-method').selectOption({ label: 'Cash on Delivery' });
    if (await page.getByTestId('account-name').isVisible()) {
      await page.getByTestId('account-name').fill(CUENTA_COD.nombre);
      await page.getByTestId('account-number').fill(CUENTA_COD.numero);
    }

    // 6. Confirm una sola vez
    await page.getByTestId('finish').click();
    await expect(page.locator('#order-confirmation')).toContainText('Thanks for your order!');
    await expect(page.locator('#invoice-number')).toHaveText(/^\s*INV-\d+\s*$/);

    // 7. Número de factura
    const factura = (await page.locator('#invoice-number').innerText()).trim();

    // 8. My account → Invoices
    await page.goto('/#/account/invoices');
    const fila = page.getByRole('row', { name: new RegExp(factura) });
    await expect(fila).toBeVisible();
    await expect(fila).toContainText('$11.48');
  });
});
