import { test, expect } from '@playwright/test';
import { PRODUCTOS, USUARIOS, CONTRASENA, iniciarSesion } from './datos';

test.describe('Favoritos (R5)', () => {
  test('CP-08 · Favoritos sin sesión y con sesión', async ({ page }) => {
    const producto = PRODUCTOS.cordlessDrill;
    const tarjetaFavorito = page
      .getByTestId(/^favorite-/)
      .filter({ has: page.getByTestId('product-name').filter({ hasText: producto.nombre }) });

    // 1–2. Sin sesión
    await page.goto(`/#/product/${producto.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(producto.nombre);
    await page.getByTestId('add-to-favorites').click();
    await expect(page.getByRole('alert')).toContainText(/unauthorized|log ?in|sign ?in/i);

    // 3. Iniciar sesión como customer2
    await iniciarSesion(page, USUARIOS.cliente2, CONTRASENA);

    // 4. Limpiar el favorito si ya estaba
    await page.goto('/#/account/favorites');
    await expect(page.getByTestId('page-title')).toHaveText('Favorites');
    await page.waitForLoadState('networkidle');
    if ((await tarjetaFavorito.count()) > 0) {
      await tarjetaFavorito.getByTestId('delete').click();
      await expect(tarjetaFavorito).toHaveCount(0);
    }

    // 5. Agregar con sesión
    await page.goto(`/#/product/${producto.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(producto.nombre);
    await page.getByTestId('add-to-favorites').click();
    await page.waitForLoadState('networkidle');

    // 6. My account → Favorites
    await page.getByTestId('nav-user-menu').click();
    await page.getByTestId('nav-my-favorites').click();
    await expect(page.getByTestId('page-title')).toHaveText('Favorites');
    await expect(tarjetaFavorito).toBeVisible();
  });
});
