import { defineConfig, devices } from '@playwright/test';

// Configuración de ejecución del Agente Virtual de QA.
// - baseURL: la aplicación bajo prueba (cámbiala con QA_BASE_URL si pruebas otra).
// - Capturas y trazas solo cuando una prueba falla, en qa/evidencia/.
// - Reporte HTML en qa/reporte-html/ (ábrelo con: npx playwright show-report qa/reporte-html).
// - Un solo worker y sin reintentos: el resultado debe ser determinista y fácil de seguir en vivo.

export default defineConfig({
  testDir: './tests',
  outputDir: './qa/evidencia',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  reporter: [
    ['list'],
    ['html', { outputFolder: 'qa/reporte-html', open: 'never' }],
  ],
  use: {
    baseURL: process.env.QA_BASE_URL ?? 'https://www.saucedemo.com',
    testIdAttribute: 'data-test',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'off',
    headless: !process.env.QA_HEADED,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
