# Requisitos de la aplicación bajo prueba

- Aplicación: Toolshop
- URL: https://with-bugs.practicesoftwaretesting.com
- Qué es: una ferretería en línea de demostración (Practice Software Testing, de Testsmith), creada para practicar pruebas y automatización. Esta versión «with bugs» tiene defectos intencionales. Es pública, no maneja datos ni pagos reales y está pensada para ser probada. Muchos controles llevan el atributo `data-test`; úsalo como localizador cuando exista.

## Usuarios de prueba

Las cuentas están publicadas en la documentación del proyecto. Es un ambiente compartido: usar solo estas cuentas, no registrar usuarios nuevos y no modificar ni borrar datos desde el panel de administración.

| Usuario | Contraseña | Comportamiento esperado |
|---------|------------|-------------------------|
| customer@practicesoftwaretesting.com | welcome01 | Cliente normal (Jane Doe): todos los flujos de compra deben funcionar |
| customer2@practicesoftwaretesting.com | welcome01 | Segundo cliente (Jack Howe), por si el primero queda con datos de otra prueba |
| admin@practicesoftwaretesting.com | welcome01 | Administrador: solo para comprobar que entra al panel; no usarlo para cambiar nada |

## Requisitos funcionales

**R1 · Inicio de sesión.** Desde «Sign in», con correo y contraseña válidos se entra a la cuenta del cliente («My account»). Con contraseña incorrecta se muestra un mensaje de error y no se entra. Con los campos vacíos se indican como obligatorios.

**R2 · Catálogo, búsqueda y orden.** La página principal lista los productos con nombre, precio e imagen. El cuadro de búsqueda filtra por nombre: al buscar «hammer» solo quedan productos cuyo nombre contiene esa palabra. El selector de orden ordena por nombre (A a Z, Z a A) y por precio (de menor a mayor y de mayor a menor), y el orden mostrado corresponde al elegido. Los filtros por categoría y por marca dejan solo los productos de esa categoría o marca.

**R3 · Detalle de producto y carrito.** La página de un producto muestra su nombre, precio y descripción, y permite elegir la cantidad. «Add to cart» agrega el producto y el contador del carrito en la barra superior refleja las unidades. En el carrito aparecen el producto, la cantidad (editable), el precio unitario y el total, y el total es cantidad × precio unitario. Al cambiar la cantidad o quitar el producto, el total y el contador se actualizan.

**R4 · Checkout.** Desde el carrito, «Proceed to checkout» lleva a un proceso por pasos: inicio de sesión (si no se ha iniciado), dirección de facturación (con los datos del perfil; los campos obligatorios no pueden ir vacíos) y método de pago. Con «Cash on Delivery» se confirma el pedido y se muestra un mensaje de agradecimiento con un número de factura. El pedido aparece después en «My account → Invoices».

**R5 · Favoritos.** Un cliente con sesión iniciada puede agregar un producto a favoritos desde su página y verlo en «My account → Favorites». Sin sesión, al intentarlo se muestra un mensaje que indica que hay que iniciar sesión.

**R6 · Contacto.** El formulario de «Contact» pide nombre, apellido, correo, asunto y mensaje. Si falta un campo obligatorio, se indica el error junto al campo y no se envía. Con todos los campos válidos, al enviar se muestra un mensaje de confirmación.

## Escenarios obligatorios para este ciclo

1. Compra completa con `customer@practicesoftwaretesting.com` pagando con «Cash on Delivery», hasta ver el número de factura (prioridad Alta).
2. Búsqueda de «hammer» y orden por precio de menor a mayor: verificar que los resultados son solo martillos y que los precios quedan ascendentes (prioridad Alta).
3. Carrito: agregar un producto con cantidad 2, verificar contador y total, cambiar la cantidad a 3 y verificar que el total se recalcula (prioridad Alta).
4. Inicio de sesión con contraseña incorrecta y con campos vacíos (prioridad Alta).
5. Formulario de contacto: enviar con un campo obligatorio vacío y luego con todos válidos (prioridad Media).

## Fuera de alcance

Panel de administración (solo comprobar que el admin entra), registro de usuarios nuevos, pago con tarjeta u otros métodos distintos de «Cash on Delivery», la API, rendimiento, accesibilidad, dispositivos móviles y navegadores distintos de Chromium.
