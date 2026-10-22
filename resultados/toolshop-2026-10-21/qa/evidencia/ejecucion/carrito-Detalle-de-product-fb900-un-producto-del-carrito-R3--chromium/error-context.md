# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: carrito.spec.ts >> Detalle de producto y carrito (R3) >> CP-07 · Quitar un producto del carrito (R3)
- Location: tests/carrito.spec.ts:37:7

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('row').filter({ hasText: 'Combination Pliers' })
Expected: 0
Received: 1
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" getByRole('row').filter({ hasText: 'Combination Pliers' }) with timeout 5000ms
  - waiting for getByRole('row').filter({ hasText: 'Combination Pliers' })
    14 × locator resolved to 1 element
       - unexpected value "1"

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - text: View the
    - link "Documentation" [ref=e4] [cursor=pointer]:
      - /url: https://testsmith-io.github.io/practice-software-testing/#/
    - text: for this application.
  - generic [ref=e5]:
    - generic [ref=e7]:
      - generic [ref=e8]: 🐛 Bug Hunting Mode - Find & Report Bugs!
      - button "Bug Hunting Guide" [ref=e9] [cursor=pointer]
    - navigation [ref=e10]:
      - generic [ref=e11]:
        - link "Practice Software Testing - Toolshop" [ref=e12] [cursor=pointer]:
          - /url: /
        - menubar "Main menu" [ref=e15]:
          - menuitem [ref=e16]:
            - link "Home" [ref=e17] [cursor=pointer]:
              - /url: "#/contact"
          - menuitem [ref=e18]:
            - button "Categories" [ref=e19] [cursor=pointer]
          - menuitem [ref=e20]:
            - link "Contakt" [ref=e21] [cursor=pointer]:
              - /url: "#/contact"
          - menuitem [ref=e22]:
            - button "User Data not found" [ref=e23] [cursor=pointer]
          - menuitem [ref=e24]:
            - link "cart" [ref=e25] [cursor=pointer]:
              - /url: "#/checkout"
              - generic [ref=e26]: 
              - generic [ref=e27]: "1"
  - generic [ref=e30]:
    - list [ref=e32]:
      - listitem:
        - generic:
          - generic: Cart
          - generic: "1"
      - listitem:
        - generic:
          - generic: Sign in
          - generic: "2"
      - listitem:
        - generic:
          - generic: Address
          - generic: "3"
      - listitem:
        - generic:
          - generic: Payment
          - generic: "4"
    - generic [ref=e35]:
      - table [ref=e36]:
        - rowgroup [ref=e37]:
          - row [ref=e38]:
            - columnheader "Item" [ref=e39]
            - columnheader [ref=e40]
            - columnheader "Quantity" [ref=e41]
            - columnheader "Price" [ref=e42]
            - columnheader "Total" [ref=e43]
            - columnheader "Total" [ref=e44]
        - rowgroup [ref=e45]:
          - row [ref=e46]:
            - cell "Combination Pliers" [ref=e47]
            - cell [ref=e48]
            - cell [ref=e49]:
              - spinbutton [ref=e50]: "1"
            - cell "$14.15" [ref=e51]
            - cell "$00.00" [ref=e52]
            - cell "" [ref=e53]
        - rowgroup [ref=e56]:
          - row [ref=e57]:
            - cell [ref=e58]
            - cell [ref=e59]
            - cell [ref=e60]
            - cell [ref=e61]:
              - strong [ref=e62]: Total
            - cell "$14.15" [ref=e63]
            - cell [ref=e64]
      - button "Proceed to checkout" [ref=e66] [cursor=pointer]
  - contentinfo [ref=e68]:
    - generic [ref=e70]:
      - generic [ref=e71]: Learn & Explore
      - generic [ref=e72]:
        - link "Learn Test Automation Hands-on courses for Playwright, Robot Framework, APIs and more" [ref=e74] [cursor=pointer]:
          - /url: https://onlinecourses.testsmith.io
          - generic [ref=e77]:
            - generic [ref=e78]: Learn Test Automation
            - text: Hands-on courses for Playwright, Robot Framework, APIs and more
        - link "API Spector Open-source API testing, mocking and contract testing" [ref=e80] [cursor=pointer]:
          - /url: https://api-spector.dev
          - generic [ref=e83]:
            - generic [ref=e84]: API Spector
            - text: Open-source API testing, mocking and contract testing
        - link "GitHub Source code, issues and contributions" [ref=e86] [cursor=pointer]:
          - /url: https://github.com/testsmith-io/practice-software-testing
          - generic [ref=e89]:
            - generic [ref=e90]: GitHub
            - text: Source code, issues and contributions
    - paragraph [ref=e92]:
      - text: This is a DEMO application, used for software testing training purpose. | Banner photo by
      - link "Barn Images" [ref=e93] [cursor=pointer]:
        - /url: https://unsplash.com/@barnimages
      - text: "on"
      - link "Unsplash" [ref=e94] [cursor=pointer]:
        - /url: https://unsplash.com/photos/t5YUoHW6zRo
      - text: .
  - button "Open chat" [ref=e96] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { CLIENTES, PRODUCTO_CARRITO } from './datos';
  3  | import { iniciarSesion } from './ayudas';
  4  | 
  5  | test.describe('Detalle de producto y carrito (R3)', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
  8  |     // Precondición: carrito vacío (contexto de navegador nuevo, sin contador en la barra).
  9  |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  10 |   });
  11 | 
  12 |   test('CP-06 · Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3)', async ({ page }) => {
  13 |     await page.goto(PRODUCTO_CARRITO.ruta);
  14 |     await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
  15 |     await expect(page.getByTestId('unit-price')).toHaveText(PRODUCTO_CARRITO.precio);
  16 |     await expect(page.getByTestId('product-description')).not.toBeEmpty();
  17 | 
  18 |     await page.getByTestId('quantity').fill('2');
  19 |     await page.getByTestId('add-to-cart').click();
  20 |     await expect(page.getByTestId('cart-quantity')).toHaveText('2');
  21 | 
  22 |     await page.getByTestId('nav-cart').click();
  23 |     await expect(page).toHaveURL(/#\/checkout/);
  24 |     await expect(page.getByTestId('product-title')).toContainText(PRODUCTO_CARRITO.nombre);
  25 |     await expect(page.getByTestId('product-quantity')).toHaveValue('2');
  26 |     await expect.soft(page.getByTestId('product-price')).toHaveText(PRODUCTO_CARRITO.precioMostrado);
  27 |     await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total2);
  28 |     await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total2);
  29 | 
  30 |     await page.getByTestId('product-quantity').fill('3');
  31 |     await page.getByTestId('product-quantity').press('Enter');
  32 |     await expect.soft(page.getByTestId('line-price')).toHaveText(PRODUCTO_CARRITO.total3);
  33 |     await expect.soft(page.getByTestId('cart-total')).toHaveText(PRODUCTO_CARRITO.total3);
  34 |     await expect.soft(page.getByTestId('cart-quantity')).toHaveText('3');
  35 |   });
  36 | 
  37 |   test('CP-07 · Quitar un producto del carrito (R3)', async ({ page }) => {
  38 |     await page.goto(PRODUCTO_CARRITO.ruta);
  39 |     await expect(page.getByTestId('product-name')).toHaveText(PRODUCTO_CARRITO.nombre);
  40 |     await expect(page.getByTestId('quantity')).toHaveValue('1');
  41 |     await page.getByTestId('add-to-cart').click();
  42 |     await expect(page.getByTestId('cart-quantity')).toHaveText('1');
  43 | 
  44 |     await page.getByTestId('nav-cart').click();
  45 |     const fila = page.getByRole('row').filter({ hasText: PRODUCTO_CARRITO.nombre });
  46 |     await expect(fila).toBeVisible();
  47 |     // El botón de quitar no tiene data-test ni nombre accesible (exploración, checkout paso 1).
  48 |     await fila.locator('a.btn-danger').click();
  49 | 
> 50 |     await expect(fila).toHaveCount(0);
     |                        ^ Error: expect(locator).toHaveCount(expected) failed
  51 |     await expect(page.getByTestId('cart-quantity')).toBeHidden();
  52 |   });
  53 | });
  54 | 
```