import { expect, Page } from '@playwright/test';

// Inicio de sesión reutilizable: cada prueba lo llama para ser independiente.
export async function iniciarSesion(page: Page, correo: string, contrasena: string) {
  await page.goto('/#/auth/login');
  await page.getByTestId('email').fill(correo);
  await page.getByTestId('password').fill(contrasena);
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/#\/account/);
}

// Elige una opción del selector de orden por su texto visible y espera la recarga del catálogo.
export async function ordenarPor(page: Page, etiqueta: string) {
  const respuesta = page.waitForResponse((r) => r.url().includes('/products') && r.url().includes('sort='));
  await page.getByTestId('sort').selectOption({ label: etiqueta });
  await respuesta;
  await expect(page.getByTestId('product-name').first()).toBeVisible();
}

export async function nombresDeProductos(page: Page) {
  return (await page.getByTestId('product-name').allTextContents()).map((t) => t.trim());
}

export async function preciosDeProductos(page: Page) {
  return (await page.getByTestId('product-price').allTextContents()).map((t) =>
    Number(t.replace(/[^0-9.]/g, '')),
  );
}
