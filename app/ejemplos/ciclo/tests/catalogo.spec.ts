import { test, expect, type Page } from '@playwright/test';
import { CONTRASENA, USUARIOS } from './datos';

// Pruebas generadas a partir de qa/plan-de-pruebas.md (R2 · catálogo).
// CP-04 y CP-05 tienen exactamente las mismas expectativas: el requisito no cambia según el usuario.

async function iniciarSesion(page: Page, usuario: string) {
  await page.goto('/');
  await page.getByTestId('username').fill(usuario);
  await page.getByTestId('password').fill(CONTRASENA);
  await page.getByTestId('login-button').click();
  await expect(page).toHaveURL(/inventory\.html/);
}

async function verificarCatalogo(page: Page) {
  const tarjetas = page.getByTestId('inventory-item');
  await expect(tarjetas).toHaveCount(6);

  const fuentes = await page.locator('[data-test$="-img"]').evaluateAll((imgs) =>
    imgs.map((img) => img.getAttribute('src')),
  );
  expect(fuentes).toHaveLength(6);
  expect(new Set(fuentes).size).toBe(6); // seis imágenes distintas

  await page.getByTestId('product-sort-container').selectOption('za');
  await expect(page.getByTestId('inventory-item-name').first()).toHaveText('Test.allTheThings() T-Shirt (Red)');

  await page.getByTestId('product-sort-container').selectOption('lohi');
  await expect(page.getByTestId('inventory-item-price').first()).toHaveText('$7.99');
}

test.describe('Catálogo', () => {
  test('CP-04 · Catálogo con seis productos, imágenes propias y orden', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.estandar);
    await verificarCatalogo(page);
  });

  test('CP-05 · Catálogo con problem_user: imágenes propias y orden', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.problema);
    await verificarCatalogo(page);
  });
});
