import { test, expect } from '@playwright/test';
import { PRODUCTOS, iniciarSesion } from './datos';

test.describe('Favoritos (R5)', () => {
  test('CP-09 · Favoritos sin sesión y con sesión', async ({ page }) => {
    const thor = PRODUCTOS.thorHammer;

    // 1–2. Sin sesión
    await page.goto(`/#/product/${thor.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(thor.nombre);
    await page.getByTestId('add-to-favorites').click();
    await expect(page.getByRole('alert').filter({ hasText: 'Unauthorized' })).toBeVisible();

    // 3. Iniciar sesión
    await iniciarSesion(page);

    // Precondición: Thor Hammer no está en Favorites (se quita si está)
    const listaFavoritos = page.waitForResponse(
      (r) => r.url().includes('/favorites') && r.request().method() === 'GET',
    );
    await page.goto('/#/account/favorites');
    await listaFavoritos;
    await expect(page.getByTestId('page-title')).toHaveText('Favorites');
    const tarjetaThor = page
      .locator('[data-test^="favorite-"]')
      .filter({ has: page.getByTestId('product-name').filter({ hasText: thor.nombre }) });
    if ((await tarjetaThor.count()) > 0) {
      await tarjetaThor.first().getByTestId('delete').click();
      await expect(tarjetaThor).toHaveCount(0);
    }

    // 4–5. Con sesión
    await page.goto(`/#/product/${thor.id}`);
    await expect(page.getByTestId('product-name')).toHaveText(thor.nombre);
    await page.getByTestId('add-to-favorites').click();
    await expect(page.getByRole('alert').filter({ hasNotText: 'Unauthorized' }).first()).toBeVisible();
    await expect(page.getByRole('alert').filter({ hasText: /something went wrong/i })).toHaveCount(0);

    // 6. Favorites
    await page.goto('/#/account/favorites');
    await expect(page.getByTestId('page-title')).toHaveText('Favorites');
    await expect(tarjetaThor).toHaveCount(1);
  });
});
