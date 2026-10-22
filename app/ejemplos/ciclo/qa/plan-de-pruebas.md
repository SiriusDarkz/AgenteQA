# Plan de pruebas · Swag Labs

## Objetivo y alcance

Verificar los cinco requisitos funcionales de `qa/requisitos.md` sobre https://www.saucedemo.com en Chromium: inicio de sesión (R1), catálogo (R2), carrito (R3), checkout (R4) y cierre de sesión (R5), incluidos los cuatro escenarios obligatorios del ciclo. Los casos con `problem_user` llevan las mismas expectativas que con `standard_user`: el requisito no cambia según el usuario.

Fuera de alcance: rendimiento, accesibilidad, dispositivos móviles y otros navegadores.

## Datos de prueba

- Contraseña de todos los usuarios: `secret_sauce` (en `tests/datos.ts`).
- Usuarios: `standard_user`, `locked_out_user`, `problem_user`.
- Producto de referencia: Sauce Labs Backpack, $29.99 (subtotal $29.99, impuesto $2.40, total $32.39).
- Datos de checkout: nombre «Ana», apellido «Pérez», código postal «10101».

## Casos de prueba

| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |
|----|--------|-----------|---------|--------------|-------|--------------------|
| CP-01 | Inicio de sesión válido | Alta | standard_user | Sesión cerrada | 1. Abrir /  2. Escribir usuario y contraseña  3. Pulsar Login | La URL contiene /inventory.html y se ve el título «Products» |
| CP-02 | Inicio de sesión con contraseña incorrecta | Alta | standard_user | Sesión cerrada | 1. Abrir /  2. Escribir usuario y la contraseña «otra»  3. Pulsar Login | Sigue en / y se ve el mensaje «Epic sadface: Username and password do not match any user in this service» |
| CP-03 | Usuario bloqueado no puede entrar | Alta | locked_out_user | Sesión cerrada | 1. Abrir /  2. Escribir usuario y contraseña  3. Pulsar Login | Sigue en / y se ve el mensaje «Epic sadface: Sorry, this user has been locked out.» |
| CP-04 | Catálogo con seis productos, imágenes propias y orden | Media | standard_user | Sesión iniciada en /inventory.html | 1. Contar las tarjetas  2. Leer el src de cada imagen  3. Ordenar por «za»  4. Ordenar por «lohi» | Hay 6 tarjetas; las 6 imágenes tienen src distinto; con «za» el primer nombre es «Test.allTheThings() T-Shirt (Red)»; con «lohi» el primer precio es «$7.99» |
| CP-05 | Catálogo con problem_user: imágenes propias y orden | Media | problem_user | Sesión iniciada en /inventory.html | 1. Contar las tarjetas  2. Leer el src de cada imagen  3. Ordenar por «za»  4. Ordenar por «lohi» | Hay 6 tarjetas; las 6 imágenes tienen src distinto; con «za» el primer nombre es «Test.allTheThings() T-Shirt (Red)»; con «lohi» el primer precio es «$7.99» |
| CP-06 | Agregar y quitar un producto del carrito | Alta | standard_user | Sesión iniciada en /inventory.html | 1. Pulsar «Add to cart» de Sauce Labs Backpack  2. Abrir el carrito  3. Pulsar «Remove» | Tras agregar: el botón dice «Remove» y el contador muestra «1»; en /cart.html se ve «Sauce Labs Backpack» y «$29.99»; tras quitar: no hay filas y el contador no se ve |
| CP-07 | Checkout completo | Alta | standard_user | Sauce Labs Backpack en el carrito | 1. Pulsar Checkout  2. Escribir nombre, apellido y código postal  3. Pulsar Continue  4. Pulsar Finish | Resumen con «Item total: $29.99», «Tax: $2.40» y «Total: $32.39»; confirmación «Thank you for your order!» en /checkout-complete.html |
| CP-08 | Checkout completo con problem_user | Alta | problem_user | Sauce Labs Backpack en el carrito | 1. Pulsar Checkout  2. Escribir nombre, apellido y código postal  3. Pulsar Continue  4. Pulsar Finish | El campo Apellido conserva «Pérez»; resumen con «Item total: $29.99», «Tax: $2.40» y «Total: $32.39»; confirmación «Thank you for your order!» en /checkout-complete.html |
| CP-09 | Checkout con campos vacíos muestra el error | Media | standard_user | Sauce Labs Backpack en el carrito, en /checkout-step-one.html | 1. Pulsar Continue sin escribir nada  2. Escribir solo el nombre y pulsar Continue | Primero «Error: First Name is required»; después «Error: Last Name is required»; sigue en /checkout-step-one.html |
| CP-10 | Cierre de sesión | Media | standard_user | Sesión iniciada en /inventory.html | 1. Abrir el menú lateral  2. Pulsar Logout | La URL es / y se ve el botón Login |

## Riesgos y supuestos

- Swag Labs es un portal público: si está lento, los casos pueden exceder el tiempo de espera de 30 s; se reintenta una vez antes de marcar BLOQUEADO.
- El impuesto se asume de 8% sobre el subtotal, según lo observado en la exploración.
- Las imágenes se comparan por el atributo `src`, no por su contenido visual.

Estado: PENDIENTE DE APROBACIÓN
