import { test, expect } from '@playwright/test';
import { PRODUCTOS } from './datos';

test.describe('Detalle de producto y carrito (R3)', () => {
  test('CP-06 · Carrito: cantidad 2, cambio a 3 y quitar producto', async ({ page }) => {
    const producto = PRODUCTOS.clawHammer;

    // 1. Detalle del producto
    await page.goto(`/#/product/${producto.id}`);
    await expect(page.getByTestId('unit-price')).toHaveText(producto.precio);

    // 2–4. Cantidad 2 y agregar
    await page.getByTestId('quantity').fill('2');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('2');

    // 5–6. Carrito
    await page.getByTestId('nav-cart').click();
    await expect(page.getByTestId('product-title')).toHaveText(producto.nombre);
    await expect(page.getByTestId('product-quantity')).toHaveValue('2');
    await expect(page.getByTestId('product-price')).toHaveText('$11.48');
    await expect(page.getByTestId('cart-total')).toHaveText('$22.96');

    // 7. Cambiar a 3
    await page.getByTestId('product-quantity').fill('3');
    await page.getByTestId('product-quantity').press('Tab');
    await expect(page.getByTestId('cart-total')).toHaveText('$34.44');
    await expect(page.getByTestId('cart-quantity')).toHaveText('3');

    // 8. Quitar el producto: el botón no tiene data-test ni rol «link» (<a> sin href);
    //    está en la última celda de la fila del producto.
    const fila = page.getByRole('row').filter({ has: page.getByTestId('product-title') });
    await fila.getByRole('cell').last().locator('a').click();
    await expect(page.getByTestId('product-title')).toHaveCount(0);
    await expect(page.getByTestId('cart-quantity').filter({ hasText: /[1-9]/ })).toHaveCount(0);
  });
});
