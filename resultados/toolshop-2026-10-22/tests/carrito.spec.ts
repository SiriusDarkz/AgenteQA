import { test, expect } from '@playwright/test';
import { PRODUCTOS, iniciarSesion } from './datos';

test.describe('Detalle de producto y carrito (R3)', () => {
  test('CP-07 · Carrito: cantidad 2, contador, total y cambio a 3', async ({ page }) => {
    await iniciarSesion(page);
    const producto = PRODUCTOS.clawHammer;

    await page.goto(`/#/product/${producto.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(producto.nombre);
    await expect(page.getByTestId('unit-price')).toHaveText(producto.precio);
    await expect(page.getByTestId('product-description')).toBeVisible();

    await page.getByTestId('quantity').fill('2');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('2');

    await page.getByTestId('nav-cart').click();
    await expect(page.getByTestId('product-title')).toHaveText(producto.nombre);
    await expect(page.getByTestId('product-quantity')).toHaveValue('2');
    await expect(page.getByTestId('product-price')).toHaveText('$11.48');
    await expect.soft(page.getByTestId('line-price')).toHaveText('$22.96');
    await expect(page.getByTestId('cart-total')).toHaveText('$22.96');

    await page.getByTestId('product-quantity').fill('3');
    await page.getByTestId('product-quantity').press('Tab');
    await expect.soft(page.getByTestId('line-price')).toHaveText('$34.44');
    await expect(page.getByTestId('cart-total')).toHaveText('$34.44');
    await expect(page.getByTestId('cart-quantity')).toHaveText('3');
  });
});
