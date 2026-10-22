# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: favoritos.spec.ts >> Favoritos (R5) >> CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5)
- Location: tests/favoritos.spec.ts:6:7

# Error details

```
Error: No debe aparecer aviso de error

expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 3

- Array []
+ Array [
+   "Oeps, something went wrong.",
+ ]
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
            - button "User Data not found" [active] [ref=e23] [cursor=pointer]
  - generic [ref=e26]:
    - heading "Favorites" [level=1] [ref=e27]
    - generic [ref=e29]:
      - img "Combination Pliers" [ref=e31]
      - generic [ref=e33]:
        - heading "Combination Pliers" [level=5] [ref=e34]
        - paragraph [ref=e35]: Versatile combination pliers designed for gripping, bending, and cutting wire with ease. Featuring chrome vanadium steel construction with induction-hardened cutting edges, these pliers deliver excellent grip and leverage for a wide range of tasks. T...
      - button "" [ref=e37] [cursor=pointer]
    - generic [ref=e40]:
      - img "Bolt Cutters" [ref=e42]
      - generic [ref=e44]:
        - heading "Bolt Cutters" [level=5] [ref=e45]
        - paragraph [ref=e46]: Heavy-duty bolt cutters engineered to slice through hardened bolts, chains, padlocks, and wire fencing with minimal effort. The compound leverage mechanism multiplies your cutting force by a factor of 30, enabling clean cuts through materials up to 1...
      - button "" [ref=e48] [cursor=pointer]
    - generic [ref=e51]:
      - img "Slip Joint Pliers" [ref=e53]
      - generic [ref=e55]:
        - heading "Slip Joint Pliers" [level=5] [ref=e56]
        - paragraph [ref=e57]: Adjustable slip joint pliers that feature a two-position pivot mechanism for switching between regular and wide jaw openings to accommodate different fastener sizes. The PVC-coated handles offer a comfortable, non-slip grip while the precisely machin...
      - button "" [ref=e59] [cursor=pointer]
    - generic [ref=e62]:
      - img "Belt Sander" [ref=e64]
      - generic [ref=e66]:
        - heading "Belt Sander" [level=5] [ref=e67]
        - paragraph [ref=e68]: Powerful 800W belt sander engineered for aggressive material removal on large flat surfaces including tabletops, doors, hardwood flooring, and timber decking. The 76x533mm sanding belt travels at an impressive 380 meters per minute, enabling rapid st...
      - button "" [ref=e70] [cursor=pointer]
  - contentinfo [ref=e73]:
    - generic [ref=e75]:
      - generic [ref=e76]: Learn & Explore
      - generic [ref=e77]:
        - link "Learn Test Automation Hands-on courses for Playwright, Robot Framework, APIs and more" [ref=e79] [cursor=pointer]:
          - /url: https://onlinecourses.testsmith.io
          - generic [ref=e82]:
            - generic [ref=e83]: Learn Test Automation
            - text: Hands-on courses for Playwright, Robot Framework, APIs and more
        - link "API Spector Open-source API testing, mocking and contract testing" [ref=e85] [cursor=pointer]:
          - /url: https://api-spector.dev
          - generic [ref=e88]:
            - generic [ref=e89]: API Spector
            - text: Open-source API testing, mocking and contract testing
        - link "GitHub Source code, issues and contributions" [ref=e91] [cursor=pointer]:
          - /url: https://github.com/testsmith-io/practice-software-testing
          - generic [ref=e94]:
            - generic [ref=e95]: GitHub
            - text: Source code, issues and contributions
    - paragraph [ref=e97]:
      - text: This is a DEMO application, used for software testing training purpose. | Banner photo by
      - link "Barn Images" [ref=e98] [cursor=pointer]:
        - /url: https://unsplash.com/@barnimages
      - text: "on"
      - link "Unsplash" [ref=e99] [cursor=pointer]:
        - /url: https://unsplash.com/photos/t5YUoHW6zRo
      - text: .
  - alert [ref=e100]:
    - generic [ref=e101]: Oeps, something went wrong.
  - button "Open chat" [ref=e103] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { CLIENTES, PRODUCTO_FAVORITOS } from './datos';
  3  | import { iniciarSesion } from './ayudas';
  4  | 
  5  | test.describe('Favoritos (R5)', () => {
  6  |   test('CP-09 · Favoritos: aviso sin sesión y alta con sesión (R5)', async ({ page }) => {
  7  |     // 1. Sin sesión
  8  |     await page.goto(PRODUCTO_FAVORITOS.ruta);
  9  |     const nombre = ((await page.getByTestId('product-name').textContent()) ?? '').trim();
  10 |     expect(nombre).not.toBe('');
  11 |     console.log('CP-09 producto 3:', nombre);
  12 |     await page.getByTestId('add-to-favorites').click();
  13 |     const avisoSesion = page.getByRole('alert').filter({ hasText: /Unauthorized|log in/i });
  14 |     await expect(avisoSesion).toBeVisible();
  15 |     await expect(avisoSesion).toBeHidden({ timeout: 15_000 });
  16 | 
  17 |     // 2. Iniciar sesión y asegurar la precondición: el producto 3 no está en favoritos
  18 |     await iniciarSesion(page, CLIENTES.principal.correo, CLIENTES.principal.contrasena);
  19 |     const carga = page.waitForResponse((r) => r.url().includes('/favorites') && r.request().method() === 'GET');
  20 |     await page.goto('/#/account/favorites');
  21 |     await carga;
  22 |     await expect(page.getByTestId('page-title')).toHaveText('Favorites');
  23 |     const previo = page.getByTestId(/^favorite-/).filter({ hasText: nombre });
  24 |     if ((await previo.count()) > 0) {
  25 |       await previo.getByTestId('delete').first().click();
  26 |       await expect(previo).toHaveCount(0);
  27 |     }
  28 | 
  29 |     // 3. Con sesión, agregar a favoritos
  30 |     await page.goto(PRODUCTO_FAVORITOS.ruta);
  31 |     await expect(page.getByTestId('product-name')).toHaveText(nombre);
  32 |     await page.getByTestId('add-to-favorites').click();
  33 |     // Se lee el aviso en cuanto aparece (los toasts desaparecen solos a los pocos segundos).
  34 |     await page.getByRole('alert').first().waitFor({ state: 'visible', timeout: 5_000 }).catch(() => {});
  35 |     const avisos = (await page.getByRole('alert').allTextContents()).map((t) => t.trim()).filter(Boolean);
  36 |     console.log('CP-09 avisos tras agregar con sesión:', avisos);
  37 |     expect
  38 |       .soft(avisos.filter((t) => /wrong|error|unauthorized/i.test(t)), 'No debe aparecer aviso de error')
> 39 |       .toEqual([]);
     |        ^ Error: No debe aparecer aviso de error
  40 | 
  41 |     // 4. My account → Favorites
  42 |     await page.getByTestId('nav-user-menu').click();
  43 |     await page.getByTestId('nav-my-favorites').click();
  44 |     await expect(page.getByTestId(/^favorite-/).filter({ hasText: nombre })).toBeVisible();
  45 |   });
  46 | });
  47 | 
```