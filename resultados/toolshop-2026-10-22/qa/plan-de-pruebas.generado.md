# Plan de pruebas · Toolshop (with bugs)

- Aplicación: https://with-bugs.practicesoftwaretesting.com
- Fuentes: `qa/requisitos.md` (R1–R6 y escenarios obligatorios 1–5) y `qa/exploracion.md` (2026-10-22)
- No hay `qa/historia-de-usuario.md`: el plan parte de los requisitos generales.
- Navegador: Chromium (`@playwright/test`)

## 1. Objetivo y alcance

**Objetivo:** comprobar de principio a fin que el cliente de Toolshop puede iniciar sesión, buscar, ordenar y filtrar el catálogo, armar el carrito, comprar con «Cash on Delivery», gestionar favoritos y escribir por el formulario de contacto, como dicen los requisitos R1–R6.

**Dentro del alcance:**

| Requisito | Casos |
|---|---|
| R1 · Inicio de sesión | CP-01, CP-02, CP-03 |
| R2 · Catálogo, búsqueda y orden | CP-04, CP-05, CP-06 |
| R3 · Detalle de producto y carrito | CP-07 |
| R4 · Checkout | CP-08 |
| R5 · Favoritos | CP-09 |
| R6 · Contacto | CP-10 |

| Escenario obligatorio | Caso |
|---|---|
| 1 · Compra completa con Cash on Delivery hasta el número de factura | CP-08 |
| 2 · Búsqueda «hammer» + orden por precio ascendente | CP-04 |
| 3 · Carrito con cantidad 2 → 3 | CP-07 |
| 4 · Login con contraseña incorrecta y con campos vacíos | CP-02, CP-03 |
| 5 · Contacto con un campo vacío y luego todos válidos | CP-10 |

**Fuera del alcance** (según `qa/requisitos.md`): panel de administración (salvo el acceso del admin, ver Riesgos), registro de usuarios, pagos distintos de «Cash on Delivery», la API, rendimiento, accesibilidad, móviles y navegadores distintos de Chromium. Los errores de texto (O-04) y el enlace «Home» (O-01) no están en ningún requisito y no tienen caso propio.

## 2. Datos de prueba

| Dato | Valor |
|---|---|
| Cliente principal | `customer@practicesoftwaretesting.com` / `welcome01` (Jane Doe) |
| Cliente de reserva | `customer2@practicesoftwaretesting.com` / `welcome01` (Jack Howe), solo si el principal queda con datos de otra prueba |
| Contraseña incorrecta | `wrongpass123` |
| Producto para carrito y compra | Claw Hammer · `#/product/8` · precio unitario $11.48 |
| Producto para favoritos | Thor Hammer · `#/product/9` · $11.14 |
| Búsqueda | `hammer` → 6 productos: Thor Hammer $11.14, Claw Hammer $11.48, Hammer $12.58, Claw Hammer with Shock Reduction Grip $13.41, Court Hammer $18.63, Claw Hammer with Fiberglass Handle $20.14 |
| Filtro de categoría | Pliers (`category-7`) → Combination Pliers, Pliers, Long Nose Pliers, Bolt Cutters, Slip Joint Pliers |
| Filtro de marca | Brand name 2 (`brand-2`) sobre Pliers → Bolt Cutters, Slip Joint Pliers |
| Dirección de facturación | Test street 98, Vienna, estado «Vienna», Austria, código postal «1010» |
| Datos de cuenta (si la app los pide con COD) | Nombre «Jane Doe», número «123456789» |
| Contacto | Nombre «Jane», apellido «Doe», correo `customer@practicesoftwaretesting.com`, asunto «Customer service», mensaje «Quisiera saber el plazo de entrega de mi pedido de martillos, gracias.» (más de 50 caracteres) |
| Factura | Se valida con el patrón `INV-\d+`, nunca con un número fijo (ambiente compartido) |

## 3. Casos de prueba

| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |
|----|--------|-----------|---------|--------------|-------|--------------------|
| CP-01 | Inicio de sesión válido | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/`  2. Pulsar «Sign in» (`nav-sign-in`)  3. Escribir el correo en `email` y `welcome01` en `password`  4. Pulsar «Login» (`login-submit`) | La URL contiene `#/account`, `page-title` muestra «My account» y ya no se ve «Sign in» en la barra |
| CP-02 | Inicio de sesión con contraseña incorrecta | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `#/auth/login`  2. Escribir el correo en `email` y `wrongpass123` en `password`  3. Pulsar «Login» | `login-error` muestra «Invalid email or password», la URL sigue en `#/auth/login` y no aparece el menú de usuario (`nav-user-menu`) |
| CP-03 | Inicio de sesión con campos vacíos | Alta | (ninguno) | Sesión cerrada | 1. Abrir `#/auth/login`  2. Dejar vacíos correo y contraseña  3. Pulsar «Login» | Junto al campo de correo y junto al de contraseña se ve un mensaje de campo obligatorio (texto con «required»), la URL sigue en `#/auth/login` y no aparece `nav-user-menu` |
| CP-04 | Búsqueda «hammer» con orden por precio de menor a mayor | Alta | (ninguno) | Sesión cerrada, página principal cargada | 1. Abrir `/`  2. Escribir `hammer` en `search-query`  3. Pulsar «Search» (`search-submit`)  4. En `sort` elegir «Price (Low - High)»  5. Leer nombres (`product-name`) y precios (`product-price`) de las tarjetas | `search-caption` muestra «Searched for: hammer»; se ven 6 productos y todos los nombres contienen «hammer» (sin distinguir mayúsculas); los precios quedan en orden ascendente: el primero es $11.14 (Thor Hammer) y el último $20.14 (Claw Hammer with Fiberglass Handle) |
| CP-05 | Orden por nombre A–Z y Z–A | Media | (ninguno) | Sesión cerrada | 1. Abrir `/` y buscar `hammer` como en CP-04  2. En `sort` elegir «Name (A - Z)» y leer los nombres  3. Elegir «Name (Z - A)» y leer los nombres | Con A–Z el orden es: Claw Hammer, Claw Hammer with Fiberglass Handle, Claw Hammer with Shock Reduction Grip, Court Hammer, Hammer, Thor Hammer. Con Z–A es exactamente el orden inverso (primero Thor Hammer, último Claw Hammer) |
| CP-06 | Filtros por categoría y por marca | Media | (ninguno) | Sesión cerrada, sin búsqueda activa | 1. Abrir `/`  2. Marcar la categoría Pliers (`category-7`)  3. Leer los nombres  4. Marcar además la marca «Brand name 2» (`brand-2`)  5. Leer los nombres | Tras el paso 2 se ven exactamente 5 productos: Combination Pliers, Pliers, Long Nose Pliers, Bolt Cutters, Slip Joint Pliers. Tras el paso 4 se ven exactamente 2: Bolt Cutters y Slip Joint Pliers |
| CP-07 | Carrito: cantidad 2, contador, total y cambio a 3 | Alta | customer@practicesoftwaretesting.com | Sesión iniciada, carrito vacío | 1. Abrir `#/product/8` (Claw Hammer)  2. Comprobar nombre, precio (`unit-price` 11.48) y descripción visibles  3. Escribir 2 en `quantity`  4. Pulsar «Add to cart»  5. Pulsar el carrito (`nav-cart`)  6. Cambiar `product-quantity` a 3 y salir del campo (Tab) | Tras el paso 4, `cart-quantity` muestra 2. En el carrito: `product-title` «Claw Hammer», `product-quantity` 2, `product-price` $11.48, `line-price` $22.96 y `cart-total` $22.96. Tras el paso 6: `line-price` $34.44, `cart-total` $34.44 y `cart-quantity` 3 |
| CP-08 | Compra completa con Cash on Delivery hasta la factura | Alta | customer@practicesoftwaretesting.com | Sesión iniciada, carrito con 1 Claw Hammer (añadido desde `#/product/8`) | 1. Pulsar `nav-cart` y luego «Proceed to checkout» (`proceed-1`)  2. En el paso Sign in, pulsar `proceed-2`  3. En Address, revisar `address`, `city`, `state`, `country`, `postcode`; si `state` está vacío escribir «Vienna» y si `postcode` está vacío o no es válido escribir «1010»  4. Vaciar `city` y comprobar el botón `proceed-3`; volver a escribir «Vienna»  5. Pulsar `proceed-3`  6. En `payment-method` elegir «Cash on Delivery»; si aparecen `account-name` y `account-number`, llenarlos con «Jane Doe» y «123456789»  7. Pulsar «Confirm» (`finish`) y, si aparece «Payment was successful», pulsarlo otra vez  8. Abrir `#/account/invoices` | Paso 2: se ve «Hello Jane Doe, you are already logged in». Paso 4: con `city` vacío `proceed-3` está deshabilitado; con todos los obligatorios llenos está habilitado. Paso 7: se ve «Thanks for your order! Your invoice number is INV-…» con un número que cumple `INV-\d+` y el contador del carrito desaparece. Paso 8: la primera fila de la tabla contiene ese mismo número de factura y el total $11.48 |
| CP-09 | Favoritos sin sesión y con sesión | Media | (ninguno) y luego customer@practicesoftwaretesting.com | Sesión cerrada. Thor Hammer no está en Favorites de Jane Doe (si está, quitarlo antes con su botón `delete` en `#/account/favorites`) | 1. Sin sesión, abrir `#/product/9` (Thor Hammer) y pulsar «Add to favourites» (`add-to-favorites`)  2. Leer el aviso (`role=alert`)  3. Iniciar sesión con customer@  4. Abrir `#/product/9` y pulsar «Add to favourites»  5. Leer el aviso  6. Abrir `#/account/favorites` | Paso 2: el aviso indica que hay que iniciar sesión (contiene «Unauthorized»). Paso 5: no aparece ningún aviso de error («something went wrong»). Paso 6: `page-title` «Favorites» y hay una tarjeta `favorite-*` con `product-name` «Thor Hammer» |
| CP-10 | Contacto con campo vacío y con todos los campos válidos | Media | (ninguno) | Sesión cerrada | 1. Abrir `#/contact`  2. Llenar nombre, correo, asunto «Customer service» y mensaje con los datos de prueba; dejar vacío el apellido  3. Pulsar «Send» (`contact-submit`)  4. Escribir «Doe» en `last-name`  5. Pulsar «Send» | Paso 3: `last-name-error` muestra «Last name is required», no aparece mensaje de confirmación y no hay error en los demás campos llenos. Paso 5: no se ve ningún mensaje `*-error` y aparece un mensaje de confirmación de envío (texto visible del tipo «Thanks for your message») |

## 4. Riesgos y supuestos

- **Ambiente compartido.** Otros usuarios crean pedidos, favoritos y carritos con las mismas cuentas. Las facturas se validan con `INV-\d+` y comparando el número mostrado con la primera fila de Invoices; si el carrito o los favoritos de Jane Doe no están limpios, se limpian antes o se usa `customer2@`.
- **Cada compra de CP-08 crea un pedido real** en el ambiente de demostración (está permitido: la app es pública y sin pagos reales). Se ejecuta una sola vez por corrida.
- **Diferencias ya vistas en la exploración** que harán fallar casos si siguen presentes (no se ajustan las expectativas): O-03 (CP-03, sin mensajes por campo), O-05 (CP-04 y CP-05, orden invertido), O-07 (botón «+» no cambia la cantidad; CP-07 escribe la cantidad, no usa «+»), O-08 (CP-07, `line-price` «$00.00»), O-12 (CP-09, «Oeps, something went wrong.» al agregar con sesión), O-13 (CP-10, «Subject is required» con asunto elegido).
- **Supuesto sobre Cash on Delivery (O-11).** El requisito R4 no dice qué datos pide COD ni cuántos clics hacen falta. Para poder llegar a la factura (escenario obligatorio 1), CP-08 llena nombre y número de cuenta si la app los pide y pulsa «Confirm» dos veces si hace falta. Si la persona considera que COD no debe pedir datos de cuenta, debe cambiar el paso 6 de CP-08 antes de aprobar.
- **Supuesto sobre la dirección (O-09).** El perfil llega con estado vacío y código postal «missing value». CP-08 completa esos campos con datos válidos; la dirección incompleta del perfil se registra como observación, no como fallo de CP-08.
- **Mensajes no especificados.** Los requisitos no dan el texto exacto del aviso de favoritos con sesión, de los obligatorios del login ni de la confirmación de contacto. Las aserciones usan fragmentos («required», ausencia de «something went wrong», un mensaje de confirmación visible); el texto real se citará en los resultados.
- **Filtros (CP-06).** Las tarjetas no muestran categoría ni marca; la lista esperada sale de la exploración del 2026-10-22. Si el catálogo cambia, hay que actualizarla.
- **Acceso del administrador.** Se comprobó en la exploración (F8, `#/admin/dashboard`) y no se incluye como caso para mantener el plan en 10 casos; puede añadirse si la persona lo pide.
- **Quitar producto del carrito (R3)** no tiene caso propio: el botón no tiene `data-test` ni nombre accesible y solo se localiza por clase CSS. Queda cubierto el recálculo al cambiar la cantidad.
- **Usuarios con comportamiento anómalo.** `qa/requisitos.md` no define ninguno; no hay casos adicionales por ese motivo.
- **Datos de prueba en código.** `tests/datos.ts` contiene todavía valores de otra aplicación (SauceDemo); se actualizarán con los datos de la sección 2 en el paso 3.

Estado: PENDIENTE DE APROBACIÓN
