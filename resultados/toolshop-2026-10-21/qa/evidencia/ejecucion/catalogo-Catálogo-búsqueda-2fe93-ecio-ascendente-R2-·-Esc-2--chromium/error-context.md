# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: catalogo.spec.ts >> Catálogo, búsqueda y orden (R2) >> CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2)
- Location: tests/catalogo.spec.ts:6:7

# Error details

```
Error: Los resultados deben incluir «Sledgehammer»

expect(received).toContain(expected) // indexOf

Expected value: "Sledgehammer"
Received array: ["Claw Hammer with Fiberglass Handle", "Court Hammer", "Claw Hammer with Shock Reduction Grip", "Hammer", "Claw Hammer", "Thor Hammer"]
```

```
Error: Los precios deben quedar de menor a mayor

expect(received).toEqual(expected) // deep equality

- Expected  - 5
+ Received  + 5

  Array [
-   11.14,
-   11.48,
-   12.58,
-   13.41,
-   18.63,
    20.14,
+   18.63,
+   13.41,
+   12.58,
+   11.48,
+   11.14,
  ]
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
            - link "Sign in" [ref=e23] [cursor=pointer]:
              - /url: "#/auth/login"
  - generic [ref=e25]:
    - generic [ref=e26]:
      - paragraph [ref=e27]
      - separator [ref=e29]
    - generic [ref=e30]:
      - generic [ref=e31]:
        - heading " Sorth" [level=4] [ref=e32]:
          - generic [ref=e33]: 
          - text: Sorth
        - separator [ref=e34]
        - combobox [ref=e37]:
          - option
          - option "Name (A - Z)"
          - option "Name (Z - A)"
          - option "Price (High - Low)"
          - option "Price (Low - High)" [selected]
          - option "CO₂ Rating (Best First)"
          - option "CO₂ Rating (Worst First)"
        - heading " Price Range" [level=4] [ref=e38]:
          - generic [ref=e39]: 
          - text: Price Range
        - separator [ref=e40]
        - generic "ngx-slider" [ref=e42]:
          - slider "ngx-slider" [ref=e47] [cursor=pointer]
          - slider "ngx-slider-max" [ref=e48] [cursor=pointer]
          - generic [ref=e49]: "0"
          - generic [ref=e50]: "200"
          - generic [ref=e51]: "1"
          - generic [ref=e52]: "100"
        - heading "Search" [level=4] [ref=e54]
        - separator [ref=e56]
        - generic [ref=e58]:
          - textbox [ref=e59]
          - button "X" [ref=e60] [cursor=pointer]
          - button "Serch" [active] [ref=e61] [cursor=pointer]
        - heading " Filters" [level=4] [ref=e62]:
          - generic [ref=e63]: 
          - text: Filters
        - separator [ref=e64]
        - heading "By category:" [level=4] [ref=e65]
        - generic [ref=e66]:
          - generic [ref=e67]: Hand Tools
          - list [ref=e68]:
            - generic [ref=e70]:
              - checkbox "Hammer" [ref=e71]
              - text: Hammer
            - generic [ref=e73]:
              - checkbox "Hand Saw" [ref=e74]
              - text: Hand Saw
            - generic [ref=e76]:
              - checkbox "Wrench" [ref=e77]
              - text: Wrench
            - generic [ref=e79]:
              - checkbox "Screwdriver" [ref=e80]
              - text: Screwdriver
            - generic [ref=e82]:
              - checkbox "Pliers" [ref=e83]
              - text: Pliers
        - generic [ref=e84]:
          - generic [ref=e85]: Power Tools
          - list [ref=e86]:
            - generic [ref=e88]:
              - checkbox "Grinder" [ref=e89]
              - text: Grinder
            - generic [ref=e91]:
              - checkbox "Sander" [ref=e92]
              - text: Sander
            - generic [ref=e94]:
              - checkbox "Saw" [ref=e95]
              - text: Saw
            - generic [ref=e97]:
              - checkbox "Drill" [ref=e98]
              - text: Drill
        - generic [ref=e100]:
          - checkbox "Other" [ref=e101]
          - text: Other
        - heading "By brand:" [level=4] [ref=e103]
        - generic [ref=e105]:
          - checkbox "Brand name 1" [ref=e106]
          - text: Brand name 1
        - generic [ref=e108]:
          - checkbox "Brand name 2" [ref=e109]
          - text: Brand name 2
        - generic [ref=e111]:
          - checkbox "Brand name 3" [ref=e112]
          - text: Brand name 3
        - generic [ref=e114]:
          - checkbox "Brand name 4" [ref=e115]
          - text: Brand name 4
        - generic [ref=e117]:
          - checkbox "Brand name 5" [ref=e118]
          - text: Brand name 5
        - generic [ref=e120]:
          - checkbox "Brand name 6" [ref=e121]
          - text: Brand name 6
        - generic [ref=e123]:
          - checkbox "Brand name 7" [ref=e124]
          - text: Brand name 7
        - generic [ref=e126]:
          - checkbox "Brand name 8" [ref=e127]
          - text: Brand name 8
        - generic [ref=e129]:
          - checkbox "Brand name 9" [ref=e130]
          - text: Brand name 9
        - generic [ref=e132]:
          - checkbox "Brand name 10" [ref=e133]
          - text: Brand name 10
        - heading "Sustainability:" [level=4] [ref=e135]
        - generic [ref=e137]:
          - checkbox "Show only eco-friendly products" [ref=e138]
          - text: Show only eco-friendly products
      - generic [ref=e139]:
        - text: 
        - 'heading "Searched for: hammer" [level=3] [ref=e140]'
        - paragraph [ref=e141]: 6 products found for 'hammer'
        - generic [ref=e142]:
          - 'link "ECO Claw Hammer with Fiberglass Handle CO₂: A B C D E $20.14" [ref=e143] [cursor=pointer]':
            - /url: "#/product/11"
            - generic [ref=e144]: ECO
            - generic [ref=e147]:
              - heading "Claw Hammer with Fiberglass Handle" [level=5] [ref=e148]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e149]:
                - text: "CO₂:"
                - generic [ref=e150]: A
                - generic [ref=e151]: B
                - generic [ref=e152]: C
                - generic [ref=e153]: D
                - generic [ref=e154]: E
            - generic [ref=e155]: $20.14
          - 'link "ECO Court Hammer CO₂: A B C D E $18.63" [ref=e157] [cursor=pointer]':
            - /url: "#/product/12"
            - generic [ref=e158]: ECO
            - generic [ref=e161]:
              - heading "Court Hammer" [level=5] [ref=e162]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e163]:
                - text: "CO₂:"
                - generic [ref=e164]: A
                - generic [ref=e165]: B
                - generic [ref=e166]: C
                - generic [ref=e167]: D
                - generic [ref=e168]: E
            - generic [ref=e169]: $18.63
          - 'link "ECO Claw Hammer with Shock Reduction Grip CO₂: A B C D E $13.41" [ref=e171] [cursor=pointer]':
            - /url: "#/product/6"
            - generic [ref=e172]: ECO
            - generic [ref=e175]:
              - heading "Claw Hammer with Shock Reduction Grip" [level=5] [ref=e176]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e177]:
                - text: "CO₂:"
                - generic [ref=e178]: A
                - generic [ref=e179]: B
                - generic [ref=e180]: C
                - generic [ref=e181]: D
                - generic [ref=e182]: E
            - generic [ref=e183]: $13.41
          - 'link "ECO Hammer CO₂: A B C D E $12.58" [ref=e185] [cursor=pointer]':
            - /url: "#/product/7"
            - generic [ref=e186]: ECO
            - generic [ref=e189]:
              - heading "Hammer" [level=5] [ref=e190]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e191]:
                - text: "CO₂:"
                - generic [ref=e192]: A
                - generic [ref=e193]: B
                - generic [ref=e194]: C
                - generic [ref=e195]: D
                - generic [ref=e196]: E
            - generic [ref=e197]: $12.58
          - 'link "ECO Claw Hammer CO₂: A B C D E $11.48" [ref=e199] [cursor=pointer]':
            - /url: "#/product/8"
            - generic [ref=e200]: ECO
            - generic [ref=e203]:
              - heading "Claw Hammer" [level=5] [ref=e204]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e205]:
                - text: "CO₂:"
                - generic [ref=e206]: A
                - generic [ref=e207]: B
                - generic [ref=e208]: C
                - generic [ref=e209]: D
                - generic [ref=e210]: E
            - generic [ref=e211]: $11.48
          - 'link "ECO Thor Hammer CO₂: A B C D E $11.14" [ref=e213] [cursor=pointer]':
            - /url: "#/product/9"
            - generic [ref=e214]: ECO
            - generic [ref=e217]:
              - heading "Thor Hammer" [level=5] [ref=e218]
              - generic "Environmental impact rating (A=lowest, E=highest)" [ref=e219]:
                - text: "CO₂:"
                - generic [ref=e220]: A
                - generic [ref=e221]: B
                - generic [ref=e222]: C
                - generic [ref=e223]: D
                - generic [ref=e224]: E
            - generic [ref=e225]: $11.14
        - generic:
          - generic:
            - generic:
              - navigation "Pagination"
  - contentinfo [ref=e228]:
    - generic [ref=e230]:
      - generic [ref=e231]: Learn & Explore
      - generic [ref=e232]:
        - link "Learn Test Automation Hands-on courses for Playwright, Robot Framework, APIs and more" [ref=e234] [cursor=pointer]:
          - /url: https://onlinecourses.testsmith.io
          - generic [ref=e237]:
            - generic [ref=e238]: Learn Test Automation
            - text: Hands-on courses for Playwright, Robot Framework, APIs and more
        - link "API Spector Open-source API testing, mocking and contract testing" [ref=e240] [cursor=pointer]:
          - /url: https://api-spector.dev
          - generic [ref=e243]:
            - generic [ref=e244]: API Spector
            - text: Open-source API testing, mocking and contract testing
        - link "GitHub Source code, issues and contributions" [ref=e246] [cursor=pointer]:
          - /url: https://github.com/testsmith-io/practice-software-testing
          - generic [ref=e249]:
            - generic [ref=e250]: GitHub
            - text: Source code, issues and contributions
    - paragraph [ref=e252]:
      - text: This is a DEMO application, used for software testing training purpose. | Banner photo by
      - link "Barn Images" [ref=e253] [cursor=pointer]:
        - /url: https://unsplash.com/@barnimages
      - text: "on"
      - link "Unsplash" [ref=e254] [cursor=pointer]:
        - /url: https://unsplash.com/photos/t5YUoHW6zRo
      - text: .
  - button "Open chat" [ref=e256] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { BUSQUEDA } from './datos';
  3  | import { nombresDeProductos, ordenarPor, preciosDeProductos } from './ayudas';
  4  | 
  5  | test.describe('Catálogo, búsqueda y orden (R2)', () => {
  6  |   test('CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2)', async ({ page }) => {
  7  |     await page.goto('/');
  8  |     await expect(page.getByTestId('product-name').first()).toBeVisible();
  9  | 
  10 |     const busqueda = page.waitForResponse((r) => r.url().includes('/products/search'));
  11 |     await page.getByTestId('search-query').fill(BUSQUEDA);
  12 |     await page.getByTestId('search-submit').click();
  13 |     await busqueda;
  14 |     await expect(page.getByTestId('search-caption')).toContainText(`Searched for: ${BUSQUEDA}`);
  15 | 
  16 |     await ordenarPor(page, 'Price (Low - High)');
  17 |     const nombres = await nombresDeProductos(page);
  18 |     const precios = await preciosDeProductos(page);
  19 |     console.log('CP-04 resultados:', nombres.map((n, i) => `${n} $${precios[i]}`).join(' | '));
  20 | 
  21 |     expect(nombres.length).toBeGreaterThan(0);
  22 |     for (const nombre of nombres) {
  23 |       expect.soft(nombre.toLowerCase(), `«${nombre}» debe contener «hammer»`).toContain(BUSQUEDA);
  24 |     }
  25 |     expect.soft(nombres, 'Los resultados deben incluir «Sledgehammer»').toContain('Sledgehammer');
  26 |     const ascendentes = [...precios].sort((a, b) => a - b);
> 27 |     expect.soft(precios, 'Los precios deben quedar de menor a mayor').toEqual(ascendentes);
     |                                                                       ^ Error: Los precios deben quedar de menor a mayor
  28 |   });
  29 | 
  30 |   test('CP-05 · Orden por nombre A-Z y filtro por categoría Hammer (R2)', async ({ page }) => {
  31 |     await page.goto('/');
  32 |     await expect(page.getByTestId('product-name').first()).toBeVisible();
  33 | 
  34 |     await ordenarPor(page, 'Name (A - Z)');
  35 |     const nombres = await nombresDeProductos(page);
  36 |     console.log('CP-05 orden A-Z:', nombres.join(' | '));
  37 |     const alfabetico = [...nombres].sort((a, b) => a.localeCompare(b));
  38 |     expect.soft(nombres, 'Los nombres deben quedar en orden alfabético ascendente').toEqual(alfabetico);
  39 | 
  40 |     const filtro = page.waitForResponse((r) => r.url().includes('/products') && r.url().includes('by_category'));
  41 |     await page.getByTestId('category-3').check();
  42 |     await filtro;
  43 |     await expect(page.getByTestId('product-name').first()).toBeVisible();
  44 |     const filtrados = await nombresDeProductos(page);
  45 |     console.log('CP-05 categoría Hammer:', filtrados.join(' | '));
  46 | 
  47 |     expect(filtrados.length).toBeGreaterThan(0);
  48 |     for (const nombre of filtrados) {
  49 |       expect.soft(nombre.toLowerCase(), `«${nombre}» debe contener «Hammer»`).toContain('hammer');
  50 |     }
  51 |   });
  52 | });
  53 | 
```