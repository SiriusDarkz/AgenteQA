// Datos de prueba de la aplicación bajo prueba (ver qa/requisitos.md).
// El agente importa estos valores en cada prueba; si el plan usa otros, los agrega aquí.

export const CONTRASENA = 'secret_sauce';

export const USUARIOS = {
  estandar: 'standard_user',
  bloqueado: 'locked_out_user',
  problema: 'problem_user',
  lento: 'performance_glitch_user',
} as const;

export const DATOS_CHECKOUT = {
  nombre: 'Ana',
  apellido: 'Pérez',
  codigoPostal: '10101',
} as const;
