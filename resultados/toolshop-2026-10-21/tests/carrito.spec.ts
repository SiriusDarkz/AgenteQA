import { test, expect } from '@playwright/test';
import { CLIENTES, PRODUCTO_CARRITO } from './datos';
import { iniciarSesion } from './ayudas';

test.describe('Detalle de producto y carrito (R3)', () => {
  test.beforeEach(async ({ page }) => {
    await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
    // Precondición: carrito vacío (contexto de navegador nuevo, sin contador en la barra).
    await expect(page.getByTestId('cart-quantity')).toBeHidden();
  });

  test('CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3)', async ({ page }) => {
    await page.goto(PRODUCTO_CARRITO.ruta);
    await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
    await expect(page.getByTestId('unit-price')).toHaveText(PRODUCTO_CARRITO.precio);
    await expect(page.getByTestId('product-description')).not.toBeEmpty();

    await page.getByTestId('quantity').fill('2');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('2');

    await page.getByTestId('nav-cart').click();
    await expect(page).toHaveURL(/#\/checkout/);
    await expect(page.getByTestId('product-title')).toContainText(PRODUCTO_CARRITO.nombre);
    await expect(page.getByTestId('product-quantity')).toHaveValue('2');
    await expect.soft(page.getByTestId('product-price')).toHaveText(PRODUCTO_CARRITO.precioMostrado);
    await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total2);
    await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total2);

    await page.getByTestId('product-quantity').fill('3');
    await page.getByTestId('product-quantity').press('Enter');
    await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total3);
    await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total3);
    await expect.soft(page.getByTestId('cart-quantity')).toHaveText('3');
  });

  test('CP-07 · Quitar un producto del carrito (R3)', async ({ page }) => {
    await page.goto(PRODUCTO_CARRITO.ruta);
    await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
    await expect(page.getByTestId('quantity')).toHaveValue('1');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-quantity')).toHaveText('1');

    await page.getByTestId('nav-cart').click();
    const fila = page.getByRole('row').filter({ hasText: PRODUCTO_CARRITO.nombre });
    await expect(fila).toBeVisible();
    // El botón de quitar no tiene data-test ni nombre accesible (exploración, checkout paso 1).
    await fila.locator('a.btn-danger').click();

    await expect(fila).toHaveCount(0);
    await expect(page.getByTestId('cart-quantity')).toBeHidden();
  });
});
