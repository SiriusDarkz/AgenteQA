# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: login.spec.ts >> Inicio de sesión (R1) >> CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4)
- Location: tests/login.spec.ts:30:7

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByTestId('email-error')
Expected pattern: /required/i
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "soft toContainText" getByTestId('email-error') with timeout 5000ms
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
- heading "Login" [level=3]
- textbox "Your E-mail *"
- textbox "Your password *"
- button ""
- button "Login"
- text: Invalid email or password
- paragraph:
  - text: Not yet an account?
  - link "Register your account":
    - /url: "#/auth/register"
  - link "Forgot your Password?":
    - /url: "#/auth/forgot-password"
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

```
Error: expect(locator).toContainText(expected) failed

Locator: getByTestId('password-error')
Expected pattern: /required/i
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "soft toContainText" getByTestId('password-error') with timeout 5000ms
  - waiting for getByTestId('password-error')

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
- heading "Login" [level=3]
- textbox "Your E-mail *"
- textbox "Your password *"
- button ""
- button "Login"
- text: Invalid email or password
- paragraph:
  - text: Not yet an account?
  - link "Register your account":
    - /url: "#/auth/register"
  - link "Forgot your Password?":
    - /url: "#/auth/forgot-password"
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
  2  | import { CLIENTES, CONTRASENA_INCORRECTA } from './datos';
  3  | 
  4  | test.describe('Inicio de sesión (R1)', () => {
  5  |   test('CP-01 · Inicio de sesión válido (R1)', async ({ page }) => {
  6  |     await page.goto('/');
  7  |     await page.getByTestId('nav-sign-in').click();
  8  |     await page.getByPlaceholder('Your E-mail *').fill(CLIENTES.principal.correo);
  9  |     // El placeholder se repite en el componente envoltorio y en el input: se usa data-test.
  10 |     await page.getByTestId('password').fill(CLIENTES.principal.contrasena);
  11 |     await page.getByTestId('login-submit').click();
  12 | 
  13 |     await expect(page).toHaveURL(/#\/account/);
  14 |     await expect(page.getByTestId('page-title')).toHaveText('My account');
  15 |     await expect(page.getByTestId('nav-user-menu')).toBeVisible();
  16 |     await expect(page.getByTestId('nav-sign-in')).toBeHidden();
  17 |   });
  18 | 
  19 |   test('CP-02 · Inicio de sesión con contraseña incorrecta (R1 · Esc. 4)', async ({ page }) => {
  20 |     await page.goto('/#/auth/login');
  21 |     await page.getByTestId('email').fill(CLIENTES.principal.correo);
  22 |     await page.getByTestId('password').fill(CONTRASENA_INCORRECTA);
  23 |     await page.getByTestId('login-submit').click();
  24 | 
  25 |     await expect(page.getByTestId('login-error')).toContainText('Invalid email or password');
  26 |     await expect(page).toHaveURL(/#\/auth\/login/);
  27 |     await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  28 |   });
  29 | 
  30 |   test('CP-03 · Inicio de sesión con campos vacíos (R1 · Esc. 4)', async ({ page }) => {
  31 |     await page.goto('/#/auth/login');
  32 |     await expect(page.getByTestId('email')).toHaveValue('');
  33 |     await expect(page.getByTestId('password')).toHaveValue('');
  34 |     await page.getByTestId('login-submit').click();
  35 | 
  36 |     await expect.soft(page.getByTestId('email-error')).toContainText(/required/i);
> 37 |     await expect.soft(page.getByTestId('password-error')).toContainText(/required/i);
     |                                                           ^ Error: expect(locator).toContainText(expected) failed
  38 |     await expect(page).toHaveURL(/#\/auth\/login/);
  39 |     await expect(page.getByTestId('nav-user-menu')).toBeHidden();
  40 |   });
  41 | });
  42 | 
```