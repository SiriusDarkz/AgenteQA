import { test, expect } from '@playwright/test';
import { CLIENTES, PRODUCTO_FAVORITOS } from './datos';
import { iniciarSesion } from './ayudas';

test.describe('Favoritos (R5)', () => {
  test('CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5)', async ({ page }) => {
    // 1. Sin sesión
    await page.goto(PRODUCTO_FAVORITOS.ruta);
    const nombre = ((await page.getByTestId('product-name').textContent()) ?? '').trim();
    expect(nombre).not.toBe('');
    console.log('CP-09 producto 3:', nombre);
    await page.getByTestId('add-to-favorites').click();
    const avisoSesion = page.getByRole('alert').filter({ hasText: /Unauthorized|log in/i });
    await expect(avisoSesion).toBeVisible();
    await expect(avisoSesion).toBeHidden({ timeout: 15_000 });

    // 2. Iniciar sesión y asegurar la precondición: el producto 3 no está en favoritos
    await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
    const carga = page.waitForResponse((r) => r.url().includes('/favorites') && r.request().method() === 'GET');
    await page.goto('/#/account/favorites');
    await carga;
    await expect(page.getByTestId('page-title')).toHaveText('Favorites');
    const previo = page.getByTestId(/^favorite-/).filter({ hasText: nombre });
    if ((await previo.count()) > 0) {
      await previo.getByTestId('delete').first().click();
      await expect(previo).toHaveCount(0);
    }

    // 3. Con sesión, agregar a favoritos
    await page.goto(PRODUCTO_FAVORITOS.ruta);
    await expect(page.getByTestId('product-name')).toHaveText(nombre);
    await page.getByTestId('add-to-favorites').click();
    // Se lee el aviso en cuanto aparece (los toasts desaparecen solos a los pocos segundos).
    await page.getByRole('alert').first().waitFor({ state: 'visible', timeout: 5_000 }).catch(() => {});
    const avisos = (await page.getByRole('alert').allTextContents()).map((t) => t.trim()).filter(Boolean);
    console.log('CP-09 avisos tras agregar con sesión:', avisos);
    expect
      .soft(avisos.filter((t) => /wrong|error|unauthorized/i.test(t)), 'No debe aparecer aviso de error')
      .toEqual([]);

    // 4. My account → Favorites
    await page.getByTestId('nav-user-menu').click();
    await page.getByTestId('nav-my-favorites').click();
    await expect(page.getByTestId(/^favorite-/).filter({ hasText: nombre })).toBeVisible();
  });
});
