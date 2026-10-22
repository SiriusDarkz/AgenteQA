import { test, expect } from '@playwright/test';
import { CLIENTES, CONTRASENA_INCORRECTA } from './datos';

test.describe('Inicio de sesión (R1)', () => {
  test('CP-01 · Inicio de sesión válido (R1)', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('nav-sign-in').click();
    await page.getByPlaceholder('Your E-mail *').fill(CLIENTES.principal.correo);
    // El placeholder se repite en el componente envoltorio y en el input: se usa data-test.
    await page.getByTestId('password').fill(CLIENTES.principal.contrasena);
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/#\/account/);
    await expect(page.getByTestId('page-title')).toHaveText('My account');
    await expect(page.getByTestId('nav-user-menu')).toBeVisible();
    await expect(page.getByTestId('nav-sign-in')).toBeHidden();
  });

  test('CP-02 · Inicio de sesión con contraseña incorrecta (R1 · Esc. 4)', async ({ page }) => {
    await page.goto('/#/auth/login');
    await page.getByTestId('email').fill(CLIENTES.principal.correo);
    await page.getByTestId('password').fill(CONTRASENA_INCORRECTA);
    await page.getByTestId('login-submit').click();

    await expect(page.getByTestId('login-error')).toContainText('Invalid email or password');
    await expect(page).toHaveURL(/#\/auth\/login/);
    await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  });

  test('CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4)', async ({ page }) => {
    await page.goto('/#/auth/login');
    await expect(page.getByTestId('email')).toHaveValue('');
    await expect(page.getByTestId('password')).toHaveValue('');
    await page.getByTestId('login-submit').click();

    await expect.soft(page.getByTestId('email-error')).toContainText(/required/i);
    await expect.soft(page.getByTestId('password-error')).toContainText(/required/i);
    await expect(page).toHaveURL(/#\/auth\/login/);
    await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  });
});
