---
name: disenar-plan
description: Paso 2 del Agente de QA. Diseña el plan y los casos de prueba a partir de qa/requisitos.md, qa/exploracion.md y, si existe, la historia de usuario de qa/historia-de-usuario.md, y los deja en qa/plan-de-pruebas.md para que una persona los apruebe.
argument-hint: [a partir de la historia de usuario] opcional
disable-model-invocation: true
allowed-tools: Read Edit(qa/**)
---

# Paso 2 · Diseña

Lee `qa/requisitos.md` y `qa/exploracion.md`. Si no existe la exploración, pide ejecutar `/explorar-app` primero y detente.

Mira si existe `qa/historia-de-usuario.md`. Si existe (o la persona lo pide en $ARGUMENTS), el plan parte de esa historia: ve «Cuando hay una historia de usuario».

## Qué hacer

Diseña entre 6 y 10 casos de prueba. Cubre:

- el camino feliz de cada requisito funcional;
- al menos dos casos negativos (credenciales inválidas, usuario bloqueado, campos obligatorios vacíos);
- todos los escenarios marcados como obligatorios en los requisitos, incluidos los que se ejecutan con usuarios de comportamiento anómalo. Esos casos llevan exactamente las mismas expectativas que con el usuario estándar: el requisito no cambia según el usuario.

## Cuando hay una historia de usuario

La historia («Como…, quiero…, para…») y sus criterios de aceptación mandan sobre el alcance:

- Cada criterio de aceptación produce al menos un caso que lo verifica de forma literal, y uno negativo cuando el criterio tiene una condición que puede no cumplirse (campo vacío, dato inválido, usuario sin permiso).
- La exploración aporta las pantallas, los localizadores y los datos reales para escribir los pasos; los requisitos generales se usan solo para no contradecir el comportamiento esperado de la aplicación.
- En la columna «Precondición» escribe entre corchetes qué criterio cubre cada caso, por ejemplo `[Criterio 2]`, y en «Objetivo y alcance» resume la historia en una línea y lista los criterios numerados.
- Si un criterio no se puede verificar con la aplicación explorada (pantalla inexistente, dato que no se puede crear), no inventes un caso: anótalo en «Riesgos y supuestos» como criterio no verificable y por qué.

Prioridad: **Alta** si el fallo impediría publicar (comprar, iniciar sesión), **Media** si degrada un flujo, **Baja** si es cosmético.

## Formato de `qa/plan-de-pruebas.md`

1. **Objetivo y alcance**: qué se prueba y qué queda fuera.
2. **Datos de prueba**: usuarios, contraseña, productos que se usarán.
3. **Casos de prueba**, en una tabla con exactamente estas columnas:

| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |
|----|--------|-----------|---------|--------------|-------|--------------------|
| CP-01 | Inicio de sesión válido | Alta | standard_user | Sesión cerrada | 1. Abrir /  2. Escribir usuario y contraseña  3. Pulsar Login | La URL contiene /inventory.html y se ve el título «Products» |

4. **Riesgos y supuestos**.
5. Última línea: `Estado: PENDIENTE DE APROBACIÓN`.

## Reglas

- Cada resultado esperado debe poder comprobarse con una aserción concreta: un texto visible, una URL, una cantidad, el estado de un control. Nada de «funciona correctamente».
- Los pasos se escriben para que otra persona pueda ejecutarlos a mano sin preguntar nada.
- No escribas código ni ejecutes pruebas en este paso.
- Guarda también una copia intacta del plan en `qa/plan-de-pruebas.generado.md`. Esa copia no se edita nunca: en el paso 5 se compara con la versión aprobada para medir cuántos casos aceptó la persona sin cambios.

Al terminar, muestra la tabla de casos en el chat y pregunta:

«¿Apruebas el plan? Puedes editar `qa/plan-de-pruebas.md` (quitar, cambiar o añadir casos) antes de continuar. Cuando esté listo, cambia la última línea a `Estado: APROBADO` o dímelo aquí, y ejecuta /ejecutar-pruebas».
