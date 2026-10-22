import { test, expect } from '@playwright/test';
import { CONTRASENA, USUARIOS } from './datos';

// Pruebas generadas a partir de qa/plan-de-pruebas.md (R3 · carrito).

test.describe('Carrito', () => {
  test('CP-06 · Agregar y quitar un producto del carrito', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('username').fill(USUARIOS.estandar);
    await page.getByTestId('password').fill(CONTRASENA);
    await page.getByTestId('login-button').click();
    await expect(page).toHaveURL(/inventory\.html/);

    await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
    await expect(page.getByTestId('remove-sauce-labs-backpack')).toHaveText('Remove');
    await expect(page.getByTestId('shopping-cart-badge')).toHaveText('1');

    await page.getByTestId('shopping-cart-link').click();
    await expect(page).toHaveURL(/cart\.html/);
    const fila = page.getByTestId('inventory-item');
    await expect(fila).toHaveCount(1);
    await expect(fila.getByTestId('inventory-item-name')).toHaveText('Sauce Labs Backpack');
    await expect(fila.getByTestId('inventory-item-price')).toHaveText('$29.99');

    await page.getByTestId('remove-sauce-labs-backpack').click();
    await expect(page.getByTestId('inventory-item')).toHaveCount(0);
    await expect(page.getByTestId('shopping-cart-badge')).toBeHidden();
  });
});
