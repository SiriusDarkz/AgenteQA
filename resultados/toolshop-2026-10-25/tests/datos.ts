// Datos de prueba de la aplicación bajo prueba: Toolshop (with bugs).
// Fuente: qa/requisitos.md y sección 2 de qa/plan-de-pruebas.md.
// El agente importa estos valores en cada prueba; si el plan usa otros, los agrega aquí.

import { expect, type Page } from '@playwright/test';

export const CONTRASENA = 'welcome01';
export const CONTRASENA_INCORRECTA = 'incorrecta123'; // plan, sección 2

export const USUARIOS = {
  cliente: 'customer@practicesoftwaretesting.com', // Jane Doe
  cliente2: 'customer2@practicesoftwaretesting.com', // Jack Howe (reserva)
  admin: 'admin@practicesoftwaretesting.com',
} as const;

export const PRODUCTOS = {
  clawHammer: { id: 8, nombre: 'Claw Hammer', precio: '11.48' },
  thorHammer: { id: 9, nombre: 'Thor Hammer', precio: '11.14' },
  cordlessDrill: { id: 23, nombre: 'Cordless Drill 20V' },
} as const;

export const BUSQUEDA = {
  termino: 'hammer',
  preciosAscendentes: ['$11.14', '$11.48', '$12.58', '$13.41', '$18.63', '$20.14'],
  nombresAZ: [
    'Claw Hammer',
    'Claw Hammer with Fiberglass Handle',
    'Claw Hammer with Shock Reduction Grip',
    'Court Hammer',
    'Hammer',
    'Thor Hammer',
  ],
} as const;

export const FILTROS = {
  categoriaHammer: 'category-3',
  categoriaPliers: 'category-7',
  marca2: 'brand-2',
  productosPliers: ['Combination Pliers', 'Pliers', 'Long Nose Pliers', 'Bolt Cutters', 'Slip Joint Pliers'],
  productosPliersMarca2: ['Bolt Cutters', 'Slip Joint Pliers'],
} as const;

export const DIRECCION = {
  ciudad: 'Vienna',
  estado: 'Wien',
  codigoPostal: '1010',
} as const;

export const CUENTA_COD = { nombre: 'Jane Doe', numero: '12345678' } as const;

export const CONTACTO = {
  nombre: 'Ana',
  apellido: 'Pérez',
  correo: 'ana.perez@example.com',
  asunto: 'Customer service',
  mensaje: 'Mensaje de prueba del agente de QA para verificar el formulario de contacto.',
} as const;

/** Inicia sesión desde la pantalla de login y espera a entrar a «My account». */
export async function iniciarSesion(page: Page, correo: string = USUARIOS.cliente, contrasena: string = CONTRASENA) {
  await page.goto('/#/auth/login');
  await page.getByTestId('email').fill(correo);
  await page.getByTestId('password').fill(contrasena);
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/#\/account/);
}
