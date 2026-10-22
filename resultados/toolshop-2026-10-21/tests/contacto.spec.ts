import { test, expect } from '@playwright/test';
import { CONTACTO } from './datos';

test.describe('Contacto (R6)', () => {
  test('CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5)', async ({ page }) => {
    await page.goto('/#/contact');

    // 2. Todo lleno menos Email
    await page.getByTestId('first-name').fill(CONTACTO.nombre);
    await page.getByTestId('last-name').fill(CONTACTO.apellido);
    // Asunto elegido como lo haría una persona: teclado y salir con Tab (plan, Riesgos · CP-10).
    const asunto = page.getByTestId('subject');
    await asunto.focus();
    await page.keyboard.type(CONTACTO.asunto.slice(0, 3));
    await page.keyboard.press('Tab');
    await expect(asunto.locator('option:checked')).toHaveText(CONTACTO.asunto);
    await page.getByTestId('message').fill(CONTACTO.mensaje);

    // 3. Enviar sin Email
    await page.getByTestId('contact-submit').click();
    await expect(page.getByTestId('email-error')).toContainText('Email is required');
    for (const campo of ['first-name', 'last-name', 'subject', 'message']) {
      await expect.soft(page.getByTestId(`${campo}-error`), `Sin error en ${campo}`).toBeHidden();
    }
    await expect(page.getByText('Thanks for your message!')).toBeHidden();

    // 4-5. Completar Email y enviar
    await page.getByTestId('email').fill(CONTACTO.correo);
    await page.getByTestId('contact-submit').click();
    await expect(page.getByText('Thanks for your message! We will contact you shortly.')).toBeVisible();
  });
});
