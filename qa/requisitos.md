# Requisitos de la aplicación bajo prueba

- Aplicación: Swag Labs
- URL: https://www.saucedemo.com
- Qué es: una tienda en línea de demostración, creada por Sauce Labs para practicar automatización de pruebas. Es pública, no tiene datos reales y está pensada para ser probada.

## Usuarios de prueba

Los usuarios y la contraseña están publicados en la propia pantalla de inicio de sesión.

| Usuario | Contraseña | Comportamiento esperado |
|---------|------------|-------------------------|
| standard_user | secret_sauce | Usuario normal: todos los flujos deben funcionar |
| locked_out_user | secret_sauce | No debe poder entrar; ve un mensaje que indica que está bloqueado |
| problem_user | secret_sauce | Usuario de comportamiento anómalo: tiene defectos intencionales, pero los requisitos de abajo aplican igual |
| performance_glitch_user | secret_sauce | Igual que standard_user, pero responde lento |

## Requisitos funcionales

**R1 · Inicio de sesión.** Con credenciales válidas se llega al catálogo (`/inventory.html`). Con contraseña incorrecta o con campos vacíos se muestra un mensaje de error y no se entra. El usuario bloqueado recibe un mensaje que dice que está bloqueado.

**R2 · Catálogo.** Se listan seis productos, cada uno con nombre, descripción, precio, imagen propia (distinta en cada producto) y un botón «Add to cart». El selector de orden reordena los productos por nombre (A a Z, Z a A) y por precio (menor a mayor, mayor a menor).

**R3 · Carrito.** Al agregar un producto, el ícono del carrito muestra la cantidad y el botón del producto cambia a «Remove». El producto aparece en `/cart.html` con su nombre y precio. Al quitarlo, desaparece del carrito y el contador se actualiza.

**R4 · Checkout.** Desde el carrito, «Checkout» abre un formulario con nombre, apellido y código postal; los tres son obligatorios y falta alguno aparece un mensaje de error que lo indica. Al continuar, el resumen muestra los productos, el subtotal, el impuesto y el total. «Finish» muestra la confirmación «Thank you for your order!».

**R5 · Cierre de sesión.** Desde el menú lateral, «Logout» vuelve a la pantalla de inicio de sesión.

## Escenarios obligatorios para este ciclo

1. Checkout completo con `standard_user` (prioridad Alta).
2. Checkout completo con `problem_user` (prioridad Alta): los mismos pasos y las mismas expectativas que con `standard_user`.
3. Catálogo con `problem_user`: imágenes distintas por producto y orden por nombre y precio (prioridad Media).
4. Inicio de sesión con `locked_out_user` y con contraseña incorrecta (prioridad Alta).

## Fuera de alcance

Rendimiento, accesibilidad, dispositivos móviles y navegadores distintos de Chromium.
