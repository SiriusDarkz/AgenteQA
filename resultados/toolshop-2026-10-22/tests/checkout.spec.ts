import { test, expect } from '@playwright/test';
import { CUENTA_COD, DIRECCION, PRODUCTOS, iniciarSesion } from './datos';

test.describe('Checkout (R4)', () => {
  test('CP-08 · Compra completa con Cash on Delivery hasta la factura', async ({ page }) => {
    await iniciarSesion(page);
    await page.goto(`/#/product/${PRODUCTOS.clawHammer.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(PRODUCTOS.clawHammer.nombre);
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('1');

    // 1. Carrito → Proceed to checkout
    await page.getByTestId('nav-cart').click();
    await page.getByTestId('proceed-1').click();

    // 2. Sign in
    await expect(page.getByText(/Hello Jane Doe, you are already logged in/)).toBeVisible();
    await page.getByTestId('proceed-2').click();

    // 3. Address
    const address = page.getByTestId('address');
    const city = page.getByTestId('city');
    const state = page.getByTestId('state');
    const postcode = page.getByTestId('postcode');
    await expect(address).toHaveValue(/.+/);
    await expect(page.getByTestId('country')).toBeVisible();
    if ((await state.inputValue()).trim() === '') await state.fill(DIRECCION.estado);
    if (!/^\d+$/.test((await postcode.inputValue()).trim())) await postcode.fill(DIRECCION.codigoPostal);

    // 4. Obligatorios: con ciudad vacía no se puede continuar
    await city.fill('');
    await expect(page.getByTestId('proceed-3')).toBeDisabled();
    await city.fill(DIRECCION.ciudad);
    await expect(page.getByTestId('proceed-3')).toBeEnabled();

    // 5.
    await page.getByTestId('proceed-3').click();

    // 6. Payment: Cash on Delivery
    await page.getByTestId('payment-method').selectOption({ label: 'Cash on Delivery' });
    if (await page.getByTestId('account-name').isVisible()) {
      await page.getByTestId('account-name').fill(CUENTA_COD.nombre);
      await page.getByTestId('account-number').fill(CUENTA_COD.numero);
    }

    // 7. Confirm (y otra vez si aparece «Payment was successful»)
    await page.getByTestId('finish').click();
    const pagoOk = page.getByText('Payment was successful');
    const confirmacion = page.locator('#order-confirmation');
    await expect(pagoOk.or(confirmacion)).toBeVisible();
    if (await pagoOk.isVisible()) await page.getByTestId('finish').click();

    await expect(confirmacion).toContainText(/Thanks for your order! Your invoice number is INV-\d+/);
    const texto = await confirmacion.innerText();
    const factura = texto.match(/INV-\d+/)![0];
    await expect(page.getByTestId('cart-quantity')).toBeHidden();

    // 8. Invoices
    await page.goto('/#/account/invoices');
    const primeraFila = page.getByRole('row', { name: /INV-\d+/ }).first();
    await expect(primeraFila).toContainText(factura);
    await expect(primeraFila).toContainText('$11.48');
  });
});
