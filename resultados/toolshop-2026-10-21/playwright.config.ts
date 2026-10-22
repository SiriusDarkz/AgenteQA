import { defineConfig, devices } from '@playwright/test';

// Configuración para volver a correr las pruebas del ciclo real de Toolshop (2026-10-21)
// sin tocar tests/ ni playwright.config.ts de la raíz. Desde la raíz del repositorio:
//
//   npx playwright test --config resultados/toolshop-2026-10-21/playwright.config.ts
//
// Las rutas son relativas a esta carpeta. Las salidas van a carpetas que .gitignore excluye.

export default defineConfig({
  testDir: './tests',
  outputDir: '../../qa/evidencia/toolshop-rerun',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  reporter: [
    ['list'],
    ['html', { outputFolder: '../../qa/reporte-html/toolshop-rerun', open: 'never' }],
  ],
  use: {
    baseURL: 'https://with-bugs.practicesoftwaretesting.com',
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
