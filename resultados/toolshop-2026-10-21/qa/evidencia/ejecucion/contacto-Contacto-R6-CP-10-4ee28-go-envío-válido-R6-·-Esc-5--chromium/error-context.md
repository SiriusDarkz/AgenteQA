# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: contacto.spec.ts >> Contacto (R6) >> CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5)
- Location: tests/contacto.spec.ts:5:7

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByTestId('email-error')
Expected substring: "Email is required"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" getByTestId('email-error') with timeout 5000ms
  - waiting for getByTestId('email-error')

```

```yaml
- text: View the
- link "Documentation":
  - /url: https://testsmith-io.github.io/practice-software-testing/#/
- text: for this application. 🐛 Bug Hunting Mode - Find & Report Bugs!
- button "Bug Hunting Guide"
- navigation:
  - link "Practice Software Testing - Toolshop":
    - /url: /
    - img
  - menubar "Main menu":
    - menuitem "Home":
      - link "Home":
        - /url: "#/contact"
    - menuitem "Categories":
      - button "Categories"
    - menuitem "Contakt":
      - link "Contakt":
        - /url: "#/contact"
    - menuitem "Sign in":
      - link "Sign in":
        - /url: "#/auth/login"
- heading "Contact" [level=3]
- alert: Thanks for your message! We will contact you shortly.
- contentinfo:
  - text: Learn & Explore
  - link "Learn Test Automation Hands-on courses for Playwright, Robot Framework, APIs and more":
    - /url: https://onlinecourses.testsmith.io
  - link "API Spector Open-source API testing, mocking and contract testing":
    - /url: https://api-spector.dev
  - link "GitHub Source code, issues and contributions":
    - /url: https://github.com/testsmith-io/practice-software-testing
  - paragraph:
    - text: This is a DEMO application, used for software testing training purpose. | Banner photo by
    - link "Barn Images":
      - /url: https://unsplash.com/@barnimages
    - text: "on"
    - link "Unsplash":
      - /url: https://unsplash.com/photos/t5YUoHW6zRo
    - text: .
- button "Open chat":
  - img
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { CONTACTO } from './datos';
  3  | 
  4  | test.describe('Contacto (R6)', () => {
  5  |   test('CP-10 · Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5)', async ({ page }) => {
  6  |     await page.goto('/#/contact');
  7  | 
  8  |     // 2. Todo lleno menos Email
  9  |     await page.getByTestId('first-name').fill(CONTACTO.nombre);
  10 |     await page.getByTestId('last-name').fill(CONTACTO.apellido);
  11 |     // Asunto elegido como lo haría una persona: teclado y salir con Tab (plan, Riesgos · CP-10).
  12 |     const asunto = page.getByTestId('subject');
  13 |     await asunto.focus();
  14 |     await page.keyboard.type(CONTACTO.asunto.slice(0, 3));
  15 |     await page.keyboard.press('Tab');
  16 |     await expect(asunto.locator('option:checked')).toHaveText(CONTACTO.asunto);
  17 |     await page.getByTestId('message').fill(CONTACTO.mensaje);
  18 | 
  19 |     // 3. Enviar sin Email
  20 |     await page.getByTestId('contact-submit').click();
> 21 |     await expect(page.getByTestId('email-error')).toContainText('Email is required');
     |                                                   ^ Error: expect(locator).toContainText(expected) failed
  22 |     for (const campo of ['first-name', 'last-name', 'subject', 'message']) {
  23 |       await expect.soft(page.getByTestId(`${campo}-error`), `Sin error en ${campo}`).toBeHidden();
  24 |     }
  25 |     await expect(page.getByText('Thanks for your message!')).toBeHidden();
  26 | 
  27 |     // 4-5. Completar Email y enviar
  28 |     await page.getByTestId('email').fill(CONTACTO.correo);
  29 |     await page.getByTestId('contact-submit').click();
  30 |     await expect(page.getByText('Thanks for your message! We will contact you shortly.')).toBeVisible();
  31 |   });
  32 | });
  33 | 
```