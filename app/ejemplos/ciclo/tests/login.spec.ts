import { test, expect, type Page } from '@playwright/test';
import { CONTRASENA, USUARIOS } from './datos';

// Pruebas generadas a partir de qa/plan-de-pruebas.md (R1 · inicio de sesión, R5 · cierre de sesión).

async function iniciarSesion(page: Page, usuario: string, contrasena = CONTRASENA) {
  await page.goto('/');
  await page.getByTestId('username').fill(usuario);
  await page.getByTestId('password').fill(contrasena);
  await page.getByTestId('login-button').click();
}

test.describe('Inicio de sesión', () => {
  test('CP-01 · Inicio de sesión válido', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.estandar);
    await expect(page).toHaveURL(/inventory\.html/);
    await expect(page.getByTestId('title')).toHaveText('Products');
  });

  test('CP-02 · Inicio de sesión con contraseña incorrecta', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.estandar, 'otra');
    await expect(page).not.toHaveURL(/inventory\.html/);
    await expect(page.getByTestId('error')).toHaveText(
      'Epic sadface: Username and password do not match any user in this service',
    );
  });

  test('CP-03 · Usuario bloqueado no puede entrar', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.bloqueado);
    await expect(page).not.toHaveURL(/inventory\.html/);
    await expect(page.getByTestId('error')).toHaveText('Epic sadface: Sorry, this user has been locked out.');
  });
});

test.describe('Cierre de sesión', () => {
  test('CP-10 · Cierre de sesión', async ({ page }) => {
    await iniciarSesion(page, USUARIOS.estandar);
    await page.getByRole('button', { name: 'Open Menu' }).click();
    await page.getByTestId('logout-sidebar-link').click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByTestId('login-button')).toBeVisible();
  });
});
