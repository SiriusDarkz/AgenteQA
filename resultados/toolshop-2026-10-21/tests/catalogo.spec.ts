import { test, expect } from '@playwright/test';
import { BUSQUEDA } from './datos';
import { nombresDeProductos, ordenarPor, preciosDeProductos } from './ayudas';

test.describe('Catálogo, búsqueda y orden (R2)', () => {
  test('CP-04 · Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2)', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('product-name').first()).toBeVisible();

    const busqueda = page.waitForResponse((r) => r.url().includes('/products/search'));
    await page.getByTestId('search-query').fill(BUSQUEDA);
    await page.getByTestId('search-submit').click();
    await busqueda;
    await expect(page.getByTestId('search-caption')).toContainText(`Searched for: ${BUSQUEDA}`);

    await ordenarPor(page, 'Price (Low - High)');
    const nombres = await nombresDeProductos(page);
    const precios = await preciosDeProductos(page);
    console.log('CP-04 resultados:', nombres.map((n, i) => `${n} $${precios[i]}`).join(' | '));

    expect(nombres.length).toBeGreaterThan(0);
    for (const nombre of nombres) {
      expect.soft(nombre.toLowerCase(), `«${nombre}» debe contener «hammer»`).toContain(BUSQUEDA);
    }
    expect.soft(nombres, 'Los resultados deben incluir «Sledgehammer»').toContain('Sledgehammer');
    const ascendentes = [...precios].sort((a, b) => a - b);
    expect.soft(precios, 'Los precios deben quedar de menor a mayor').toEqual(ascendentes);
  });

  test('CP-05 · Orden por nombre A-Z y filtro por categoría Hammer (R2)', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('product-name').first()).toBeVisible();

    await ordenarPor(page, 'Name (A - Z)');
    const nombres = await nombresDeProductos(page);
    console.log('CP-05 orden A-Z:', nombres.join(' | '));
    const alfabetico = [...nombres].sort((a, b) => a.localeCompare(b));
    expect.soft(nombres, 'Los nombres deben quedar en orden alfabético ascendente').toEqual(alfabetico);

    const filtro = page.waitForResponse((r) => r.url().includes('/products') && r.url().includes('by_category'));
    await page.getByTestId('category-3').check();
    await filtro;
    await expect(page.getByTestId('product-name').first()).toBeVisible();
    const filtrados = await nombresDeProductos(page);
    console.log('CP-05 categoría Hammer:', filtrados.join(' | '));

    expect(filtrados.length).toBeGreaterThan(0);
    for (const nombre of filtrados) {
      expect.soft(nombre.toLowerCase(), `«${nombre}» debe contener «Hammer»`).toContain('hammer');
    }
  });
});
