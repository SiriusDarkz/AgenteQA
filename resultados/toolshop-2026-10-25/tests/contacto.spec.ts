import { test, expect } from '@playwright/test';
import { CONTACTO } from './datos';

test.describe('Contacto (R6)', () => {
  test('CP-09 · Contacto: campo obligatorio vacío y luego envío válido', async ({ page }) => {
    const erroresVisibles = page.getByTestId(/-error$/).filter({ visible: true });

    await page.goto('/#/contact');

    // 1. Todo lleno menos el apellido
    await page.getByTestId('first-name').fill(CONTACTO.nombre);
    await page.getByTestId('email').fill(CONTACTO.correo);
    await page.getByTestId('subject').selectOption({ label: CONTACTO.asunto });
    await page.getByTestId('message').fill(CONTACTO.mensaje);

    // 2. Enviar
    await page.getByTestId('contact-submit').click();
    await expect(page.getByTestId('last-name-error')).toContainText('Last name is required');
    await expect(erroresVisibles, 'solo debe aparecer el error del apellido').toHaveCount(1);
    await expect(page.getByTestId('contact-submit')).toBeVisible();

    // 3–4. Completar apellido y enviar
    await page.getByTestId('last-name').fill(CONTACTO.apellido);
    await page.getByTestId('contact-submit').click();
    await expect(erroresVisibles, 'no debe quedar ningún error visible').toHaveCount(0);
    await expect(page.getByTestId('contact-submit')).toBeHidden();
    await expect(page.getByText(/thanks for your message|message has been sent|successfully/i)).toBeVisible();
  });
});
