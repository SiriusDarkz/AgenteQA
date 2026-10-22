import { test, expect, Locator } from '@playwright/test';
import { CLIENTES, DIRECCION_FACTURACION, PRODUCTO_CARRITO } from './datos';
import { iniciarSesion } from './ayudas';

async function completar(campo: Locator, valor: string) {
  const etiqueta = await campo.evaluate((el) => el.tagName.toLowerCase());
  if (etiqueta === 'select') await campo.selectOption({ label: valor });
  else await campo.fill(valor);
}

test.describe('Checkout (R4)', () => {
  test('CP-08 · Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1)', async ({ page }) => {
    await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
    await expect(page.getByTestId('cart-quantity')).toBeHidden();

    // 1. Producto con cantidad 2
    await page.goto(PRODUCTO_CARRITO.ruta);
    await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
    await page.getByTestId('quantity').fill('2');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('2');

    // 2. Carrito → Proceed to checkout
    await page.getByTestId('nav-cart').click();
    await page.getByTestId('proceed-1').click();

    // 3. Paso Sign in
    await expect(page.getByText(`Hello ${CLIENTES.principal.nombre}, you are already logged in`)).toBeVisible();
    await page.getByTestId('proceed-2').click();

    // 4. Paso Address
    const d = DIRECCION_FACTURACION;
    await expect(page.getByTestId('address')).toBeVisible();
    await completar(page.getByTestId('address'), d.address);
    await completar(page.getByTestId('city'), d.city);
    await completar(page.getByTestId('state'), d.state);
    await completar(page.getByTestId('country'), d.country);
    await completar(page.getByTestId('postcode'), d.postcode);
    await expect(page.getByTestId('proceed-3')).toBeEnabled();
    await page.getByTestId('proceed-3').click();

    // 5. Paso Payment: Cash on Delivery no debe pedir datos de otro método
    await page.getByTestId('payment-method').selectOption({ label: 'Cash on Delivery' });
    await expect(page.getByTestId('finish')).toBeEnabled();

    // 6. Confirmar
    await page.getByTestId('finish').click();
    const pagoExitoso = page.getByText('Payment was successful');
    if (await pagoExitoso.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await page.getByTestId('finish').click();
    }
    const confirmacion = page.locator('#order-confirmation');
    await expect(confirmacion).toContainText('Thanks for your order! Your invoice number is INV-');
    await expect(page.getByTestId('cart-quantity')).toBeHidden();

    // 7. Número de factura
    const factura = ((await confirmacion.textContent()) ?? '').match(/INV-\d+/)?.[0] ?? '';
    console.log('CP-08 factura:', factura);
    expect(factura).not.toBe('');

    // 8. My account → Invoices
    await page.getByTestId('nav-user-menu').click();
    await page.getByTestId('nav-my-invoices').click();
    const filaFactura = page.getByRole('row').filter({ hasText: factura });
    await expect(filaFactura).toBeVisible();
    await expect(filaFactura).toContainText(PRODUCTO_CARRITO.total2);
  });
});
