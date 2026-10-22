import { test, expect, type Page } from '@playwright/test';
import { CONTRASENA, DATOS_CHECKOUT, USUARIOS } from './datos';

// Pruebas generadas a partir de qa/plan-de-pruebas.md (R4 · checkout).
// CP-07 y CP-08 tienen las mismas expectativas: el requisito no cambia según el usuario.

async function llegarAlCheckout(page: Page, usuario: string) {
  await page.goto('/');
  await page.getByTestId('username').fill(usuario);
  await page.getByTestId('password').fill(CONTRASENA);
  await page.getByTestId('login-button').click();
  await expect(page).toHaveURL(/inventory\.html/);

  await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
  await page.getByTestId('shopping-cart-link').click();
  await page.getByTestId('checkout').click();
  await expect(page).toHaveURL(/checkout-step-one\.html/);
}

async function checkoutCompleto(page: Page) {
  await page.getByTestId('firstName').fill(DATOS_CHECKOUT.nombre);
  await page.getByTestId('lastName').fill(DATOS_CHECKOUT.apellido);
  await page.getByTestId('postalCode').fill(DATOS_CHECKOUT.codigoPostal);
  await expect(page.getByTestId('lastName')).toHaveValue(DATOS_CHECKOUT.apellido);
  await page.getByTestId('continue').click();

  await expect(page).toHaveURL(/checkout-step-two\.html/);
  await expect(page.getByTestId('subtotal-label')).toHaveText('Item total: $29.99');
  await expect(page.getByTestId('tax-label')).toHaveText('Tax: $2.40');
  await expect(page.getByTestId('total-label')).toHaveText('Total: $32.39');

  await page.getByTestId('finish').click();
  await expect(page).toHaveURL(/checkout-complete\.html/);
  await expect(page.getByTestId('complete-header')).toHaveText('Thank you for your order!');
}

test.describe('Checkout', () => {
  test('CP-07 · Checkout completo', async ({ page }) => {
    await llegarAlCheckout(page, USUARIOS.estandar);
    await checkoutCompleto(page);
  });

  test('CP-08 · Checkout completo con problem_user', async ({ page }) => {
    await llegarAlCheckout(page, USUARIOS.problema);
    await checkoutCompleto(page);
  });

  test('CP-09 · Checkout con campos vacíos muestra el error', async ({ page }) => {
    await llegarAlCheckout(page, USUARIOS.estandar);

    await page.getByTestId('continue').click();
    await expect(page.getByTestId('error')).toHaveText('Error: First Name is required');

    await page.getByTestId('firstName').fill(DATOS_CHECKOUT.nombre);
    await page.getByTestId('continue').click();
    await expect(page.getByTestId('error')).toHaveText('Error: Last Name is required');
    await expect(page).toHaveURL(/checkout-step-one\.html/);
  });
});
