import { test, expect } from '@playwright/test';
import { CONTRASENA, CONTRASENA_INCORRECTA, USUARIOS } from './datos';

test.describe('Inicio de sesión (R1)', () => {
  test('CP-01 · Inicio de sesión válido', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-sign-in').click();
    await page.getByTestId('email').fill(USUARIOS.cliente);
    await page.getByTestId('password').fill(CONTRASENA);
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/#\/account/);
    await expect(page.getByTestId('page-title')).toHaveText('My account');
    await expect(page.getByTestId('nav-sign-in')).toBeHidden();
  });

  test('CP-02 · Inicio de sesión con contraseña incorrecta', async ({ page }) => {
    await page.goto('/#/auth/login');
    await page.getByTestId('email').fill(USUARIOS.cliente);
    await page.getByTestId('password').fill(CONTRASENA_INCORRECTA);
    await page.getByTestId('login-submit').click();

    await expect(page.getByTestId('login-error')).toContainText('Invalid email or password');
    await expect(page).toHaveURL(/#\/auth\/login/);
    await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  });

  test('CP-03 · Inicio de sesión con campos vacíos', async ({ page }) => {
    await page.goto('/#/auth/login');
    await page.getByTestId('login-submit').click();

    // Un mensaje de campo obligatorio («required») junto al correo y otro junto a la contraseña.
    // La exploración no documenta un data-test para estos mensajes: se buscan por texto.
    await expect.soft(page.getByText(/required/i)).toHaveCount(2);
    await expect(page).toHaveURL(/#\/auth\/login/);
    await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  });
});
