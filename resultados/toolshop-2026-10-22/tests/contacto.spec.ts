import { test, expect } from '@playwright/test';
import { CONTACTO } from './datos';

test.describe('Contacto (R6)', () => {
  test('CP-10 · Contacto con campo vacío y con todos los campos válidos', async ({ page }) => {
    await page.goto('/#/contact');
    await page.getByTestId('first-name').fill(CONTACTO.nombre);
    await page.getByTestId('email').fill(CONTACTO.correo);
    await page.getByTestId('subject').selectOption({ label: CONTACTO.asunto });
    await page.getByTestId('message').fill(CONTACTO.mensaje);

    // 3. Enviar con apellido vacío
    await page.getByTestId('contact-submit').click();
    await expect(page.getByTestId('last-name-error')).toContainText('Last name is required');
    await expect(page.getByText(/thanks for your message/i)).toHaveCount(0);
    for (const campo of ['first-name', 'email', 'subject', 'message']) {
      await expect.soft(page.getByTestId(`${campo}-error`), `sin error en ${campo}`).toBeHidden();
    }

    // 4–5. Completar apellido y enviar
    await page.getByTestId('last-name').fill(CONTACTO.apellido);
    await page.getByTestId('contact-submit').click();
    await expect(page.locator('[data-test$="-error"]:visible')).toHaveCount(0);
    await expect(page.getByText(/thanks for your message/i)).toBeVisible();
  });
});
