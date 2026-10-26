import { test, expect, type Page } from '@playwright/test';
import { BUSQUEDA, FILTROS } from './datos';

async function buscar(page: Page, termino: string) {
  await page.goto('/');
  await page.getByTestId('search-query').fill(termino);
  await page.getByTestId('search-submit').click();
  await expect(page.getByTestId('search-caption')).toContainText(`Searched for: ${termino}`);
}

async function nombresOrdenados(page: Page) {
  const nombres = await page.getByTestId('product-name').allInnerTexts();
  return nombres.map((n) => n.trim()).sort();
}

test.describe('Catálogo, búsqueda y orden (R2)', () => {
  test('CP-04 · Búsqueda «hammer» con orden por precio de menor a mayor', async ({ page }) => {
    await buscar(page, BUSQUEDA.termino);
    await expect(page.getByTestId('product-name')).toHaveCount(6);

    await page.getByTestId('sort').selectOption({ label: 'Price (Low - High)' });

    const nombres = await page.getByTestId('product-name').allInnerTexts();
    for (const nombre of nombres) {
      expect(nombre.toLowerCase()).toContain(BUSQUEDA.termino);
    }
    // Precios en orden ascendente: primero $11.14 (Thor Hammer), último $20.14.
    await expect(page.getByTestId('product-price')).toHaveText([...BUSQUEDA.preciosAscendentes]);
  });

  test('CP-05 · Orden por nombre A–Z y Z–A', async ({ page }) => {
    await buscar(page, BUSQUEDA.termino);
    await expect(page.getByTestId('product-name')).toHaveCount(6);

    await page.getByTestId('sort').selectOption({ label: 'Name (A - Z)' });
    await expect.soft(page.getByTestId('product-name')).toHaveText([...BUSQUEDA.nombresAZ]);

    await page.getByTestId('sort').selectOption({ label: 'Name (Z - A)' });
    await expect(page.getByTestId('product-name')).toHaveText([...BUSQUEDA.nombresAZ].reverse());
  });

  test('CP-06 · Filtros por categoría y por marca', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('product-name').first()).toBeVisible();

    await page.getByTestId(FILTROS.categoriaPliers).check();
    await expect.poll(() => nombresOrdenados(page)).toEqual([...FILTROS.productosPliers].sort());

    await page.getByTestId(FILTROS.marca2).check();
    await expect.poll(() => nombresOrdenados(page)).toEqual([...FILTROS.productosPliersMarca2].sort());
  });
});
