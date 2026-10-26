import { test, expect } from '@playwright/test';
import { CONTRASENA, CONTRASENA_INCORRECTA, USUARIOS } from './datos';

test.describe('Inicio de sesión (R1)', () => {
  test('CP-01 · Inicio de sesión válido', async ({ page }) => {
    await page.goto('/#/auth/login');
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
    await expect(page.getByTestId('nav-sign-in')).toBeVisible();
  });

  test('CP-03 · Inicio de sesión con campos vacíos', async ({ page }) => {
    await page.goto('/#/auth/login');
    await expect(page.getByTestId('email')).toHaveValue('');
    await expect(page.getByTestId('password')).toHaveValue('');
    await page.getByTestId('login-submit').click();

    await expect(page.getByTestId('email-error')).toBeVisible();
    await expect(page.getByTestId('password-error')).toBeVisible();
    await expect(page).toHaveURL(/#\/auth\/login/);
  });

  test('CP-10 · El administrador entra al panel', async ({ page }) => {
    await page.goto('/#/auth/login');
    await page.getByTestId('email').fill(USUARIOS.admin);
    await page.getByTestId('password').fill(CONTRASENA);
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/#\/admin\/dashboard/);
    await expect(page.getByText('Sales over the years')).toBeVisible();

    await page.getByTestId('nav-admin-menu').click();
    await page.getByTestId('nav-sign-out').click();
    await expect(page).toHaveURL(/#\/auth\/login/);
  });
});
