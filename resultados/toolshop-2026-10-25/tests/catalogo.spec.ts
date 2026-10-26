import { test, expect, type Page } from '@playwright/test';
import { BUSQUEDA, FILTROS } from './datos';

/** Precio «$11.48» → 11.48 */
const aNumero = (precio: string) => Number(precio.replace(/[^0-9.]/g, ''));

async function nombres(page: Page) {
  return (await page.getByTestId('product-name').allInnerTexts()).map((n) => n.trim());
}

test.describe('Catálogo, búsqueda y orden (R2)', () => {
  test('CP-04 · Búsqueda «hammer» ordenada por precio de menor a mayor', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('search-query').fill(BUSQUEDA.termino);
    await page.getByTestId('search-submit').click();
    await expect(page.getByTestId('search-term')).toHaveText(BUSQUEDA.termino);

    await page.getByTestId('sort').selectOption({ label: 'Price (Low - High)' });

    // Al menos 1 resultado y todos contienen «hammer».
    await expect(page.getByTestId('product-name').first()).toBeVisible();
    await expect
      .poll(async () => (await nombres(page)).every((n) => n.toLowerCase().includes(BUSQUEDA.termino)), {
        message: 'todos los resultados contienen «hammer»',
      })
      .toBe(true);

    // Precios en orden ascendente (cada precio ≥ al anterior).
    await page.waitForLoadState('networkidle');
    const precios = (await page.getByTestId('product-price').allInnerTexts()).map((p) => p.trim());
    expect(precios.length).toBeGreaterThan(0);
    const ordenados = [...precios].sort((a, b) => aNumero(a) - aNumero(b));
    expect(precios, 'los precios quedan en orden ascendente').toEqual(ordenados);
  });

  test('CP-05 · Catálogo y filtro por categoría Hammer', async ({ page }) => {
    await page.goto('/');

    // Paso 2: 9 tarjetas con nombre, precio $n.nn e imagen cargada.
    const tarjetas = page.getByTestId(/^product-\d+$/);
    await expect(tarjetas).toHaveCount(9);
    for (let i = 0; i < 9; i++) {
      const tarjeta = tarjetas.nth(i);
      await expect(tarjeta.getByTestId('product-name')).toHaveText(/\S+/);
      await expect(tarjeta.getByTestId('product-price')).toHaveText(/^\s*\$\d+\.\d{2}\s*$/);
      // Las imágenes de las tarjetas no exponen rol «img» accesible (alt vacío): se ubica por etiqueta.
      const imagen = tarjeta.locator('img').first();
      const nombre = (await tarjeta.getByTestId('product-name').innerText()).trim();
      await expect
        .poll(() => imagen.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0), {
          message: `la imagen de «${nombre}» se carga (ancho natural > 0)`,
        })
        .toBe(true);
    }

    // Pasos 3–4: filtro por categoría Hammer.
    await page.getByTestId(FILTROS.categoriaHammer).check();
    await expect
      .poll(async () => {
        const lista = await nombres(page);
        return lista.length > 0 && lista.every((n) => n.toLowerCase().includes('hammer'));
      }, { message: 'con la categoría Hammer solo quedan productos con «hammer» en el nombre' })
      .toBe(true);
  });
});
