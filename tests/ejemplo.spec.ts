import { test, expect } from '@playwright/test';
import { CONTRASENA, USUARIOS } from './datos';

// Prueba de humo. Sirve para dos cosas:
// 1. Comprobar que el proyecto y el portal responden antes de la demo (npx playwright test).
// 2. Darle al agente una referencia de estilo: un describe por flujo, un test por caso,
//    título con el ID del plan, localizadores por rol/placeholder/test id, rutas relativas.
// El agente puede reemplazarla cuando genere las pruebas del plan.

test.describe('Humo', () => {
  test('HUMO-01 · Inicio de sesión con usuario estándar', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder('Username').fill(USUARIOS.estandar);
    await page.getByPlaceholder('Password').fill(CONTRASENA);
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page).toHaveURL(/inventory\.html/);
    await expect(page.getByText('Products')).toBeVisible();
  });
});
