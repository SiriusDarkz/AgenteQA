// Datos de prueba de Toolshop (ver qa/requisitos.md y qa/plan-de-pruebas.md · sección 2).
// Los generó el agente en el ciclo real del 2026-10-21; cada prueba los importa desde aquí.

export const URL_TOOLSHOP = 'https://with-bugs.practicesoftwaretesting.com';

export const CLIENTES = {
  principal: {
    correo: 'customer@practicesoftwaretesting.com',
    contrasena: 'welcome01',
    nombre: 'Jane Doe',
  },
  respaldo: {
    correo: 'customer2@practicesoftwaretesting.com',
    contrasena: 'welcome01',
    nombre: 'Jack Howe',
  },
} as const;

export const CONTRASENA_INCORRECTA = 'contrasena-incorrecta';

export const BUSQUEDA = 'hammer';

export const PRODUCTO_CARRITO = {
  ruta: '/#/product/1',
  nombre: 'Combination Pliers',
  precio: '14.15',
  precioMostrado: '$14.15',
  total2: '$28.30',
  total3: '$42.45',
} as const;

export const PRODUCTO_FAVORITOS = { ruta: '/#/product/3' } as const;

export const DIRECCION_FACTURACION = {
  address: 'Test street 98',
  city: 'Vienna',
  state: 'Vienna',
  country: 'Austria',
  postcode: '1010',
} as const;

export const CONTACTO = {
  nombre: 'Ana',
  apellido: 'Pérez',
  correo: 'ana.perez@example.com',
  asunto: 'Customer service',
  mensaje: 'Consulta de prueba del agente de QA sobre un pedido.',
} as const;
