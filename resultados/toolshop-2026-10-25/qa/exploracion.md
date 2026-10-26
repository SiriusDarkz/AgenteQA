# Exploración · Toolshop (with bugs)

- URL: https://with-bugs.practicesoftwaretesting.com
- Fecha: 2026-10-25
- Herramienta: navegador del servidor MCP `playwright` (Chromium)
- Usuarios usados: `customer@practicesoftwaretesting.com` (Jane Doe) para todos los flujos de cliente; `admin@practicesoftwaretesting.com` solo para comprobar la entrada al panel.
- Nota sobre usuarios: `qa/requisitos.md` no marca ningún usuario con «comportamiento anómalo», así que no hubo checkout repetido con otros usuarios. `customer2` no fue necesario.
- Localizadores: `playwright.config.ts` define `testIdAttribute: 'data-test'`, por lo que `getByTestId('x')` equivale a `[data-test="x"]`.

## 1. Resumen

Toolshop es una ferretería en línea de demostración (Angular, rutas con `#/`) con catálogo filtrable, detalle de producto, carrito, checkout por pasos y área de cuenta del cliente.
Los flujos de compra funcionan de punta a punta para Jane Doe: el pedido se confirmó con la factura `INV-2026000005` y apareció en «Invoices».
Se observaron varias anomalías en orden, búsqueda, carrito, pago contra entrega, formulario de contacto e inicio de sesión con campos vacíos (sección 5).

## 2. Mapa de pantallas

| Pantalla | URL | Propósito |
|---|---|---|
| Inicio / catálogo | `#/` | Lista de productos (9 por página) con orden, rango de precio, búsqueda y filtros por categoría, marca y eco |
| Detalle de producto | `#/product/{id}` (p. ej. `#/product/8` Claw Hammer, `#/product/23` Cordless Drill 20V) | Nombre, precio, descripción, cantidad, «Add to cart», «Add to favourites» |
| Inicio de sesión | `#/auth/login` | Correo y contraseña; enlaces a registro y recuperar contraseña |
| Mi cuenta | `#/account` | Panel del cliente con accesos a Favorites, Profile, Invoices, Messages |
| Favoritos | `#/account/favorites` | Productos favoritos del cliente con botón para quitar |
| Facturas | `#/account/invoices` | Tabla de pedidos: número, dirección, fecha, total, «Details» |
| Carrito / Checkout | `#/checkout` | Asistente de 4 pasos: Cart → Sign in → Address → Payment, y confirmación con número de factura |
| Contacto | `#/contact` | Formulario de contacto (nombre, apellido, correo, asunto, mensaje, adjunto) |
| Panel de administración | `#/admin/dashboard` | Solo se comprobó la entrada del admin (título «Sales over the years») |

## 3. Inventario de elementos

### 3.1 Barra superior (todas las pantallas)

| Elemento | Localizador recomendado | Observado |
|---|---|---|
| Home | `getByTestId('nav-home')` | Texto «Home», `href="#/contact"` |
| Categories (menú) | `getByTestId('nav-categories')` | Submenú: `nav-hand-tools` «Hand Tools», `nav-power-tools` «Power Tools», `nav-robotic-tools` «UNDEFINED», `nav-special-tools` «Chainsaws», `nav-rentals` «Rentals» |
| Contact | `getByTestId('nav-contact')` | Texto «Contakt» |
| Sign in | `getByTestId('nav-sign-in')` | Lleva a `#/auth/login` (solo sin sesión) |
| Menú de usuario | `getByTestId('nav-user-menu')` | Con sesión de Jane Doe muestra «User Data not found» |
| Opciones del menú de usuario | `nav-my-account`, `nav-my-favorites`, `nav-my-profile`, `nav-my-invoices`, `nav-my-messages`, `nav-sign-out` | `nav-sign-out` cierra sesión y lleva a `#/auth/login` |
| Carrito | `getByTestId('nav-cart')` (enlace a `#/checkout`) | Aparece al tener productos |
| Contador del carrito | `getByTestId('cart-quantity')` | Número de unidades |
| Menú admin | `getByTestId('nav-admin-menu')` | «John Doe»; contiene `nav-sign-out` |

### 3.2 Inicio / catálogo (`#/`)

| Elemento | Localizador recomendado |
|---|---|
| Selector de orden | `getByTestId('sort')` — opciones: «Name (A - Z)», «Name (Z - A)», «Price (High - Low)», «Price (Low - High)», «CO₂ Rating (Best First)», «CO₂ Rating (Worst First)» |
| Cuadro de búsqueda | `getByTestId('search-query')` |
| Botón buscar | `getByTestId('search-submit')` (texto «Serch») |
| Limpiar búsqueda | `getByTestId('search-reset')` (texto «X») |
| Texto de búsqueda realizada | `getByTestId('search-caption')` → «Searched for: hammer»; `getByTestId('search-term')` → «hammer» |
| Filtros de categoría | `getByTestId('category-3')` Hammer, `category-4` Hand Saw, `category-5` Wrench, `category-6` Screwdriver, `category-7` Pliers, `category-8` Grinder, `category-9` Sander, `category-10` Saw, `category-11` Drill, `category-12` Other |
| Filtros de marca | `getByTestId('brand-1')` … `getByTestId('brand-10')` («Brand name 1» … «Brand name 10») |
| Solo eco | `getByTestId('eco-friendly-filter')` |
| Rango de precio | `getByRole('slider', { name: 'ngx-slider' })` y `ngx-slider-max` (0–200) |
| Tarjeta de producto | `getByTestId('product-{id}')` (enlace a `#/product/{id}`); contenedor de la lista `getByTestId('filter_completed')` tras filtrar/ordenar |
| Nombre / precio en tarjeta | `getByTestId('product-name')`, `getByTestId('product-price')` (formato «$11.48») |
| Insignias | `eco-badge`, `co2-rating-badge`, `out-of-stock` |
| Paginación | `getByRole('navigation', { name: 'Pagination' })` |

### 3.3 Detalle de producto (`#/product/{id}`)

| Elemento | Localizador recomendado |
|---|---|
| Nombre | `getByTestId('product-name')` (h1) |
| Precio unitario | `getByTestId('unit-price')` (sin símbolo, p. ej. «11.48») |
| Descripción | `getByTestId('product-description')` |
| Disminuir / aumentar cantidad | `getByTestId('decrease-quantity')`, `getByTestId('increase-quantity')` |
| Cantidad | `getByTestId('quantity')` (valor inicial 1) |
| Agregar al carrito | `getByTestId('add-to-cart')` («Add to cart») |
| Agregar a favoritos | `getByTestId('add-to-favorites')` («Add to favourites») |
| Mensajes (toasts) | `getByRole('alert')` |

### 3.4 Inicio de sesión (`#/auth/login`)

| Elemento | Localizador recomendado |
|---|---|
| Correo | `getByTestId('email')` (placeholder «Your E-mail *», id `email`) |
| Contraseña | `getByTestId('password')` (placeholder «Your password *», id `password`) |
| Enviar | `getByTestId('login-submit')` (input submit) |
| Error general | `getByTestId('login-error')` |
| Errores por campo (si existen) | `getByTestId('email-error')`, `getByTestId('password-error')` — no aparecieron en la exploración |
| Enlaces | `getByTestId('register-link')`, `getByTestId('forgot-password-link')` |

### 3.5 Mi cuenta, Favoritos, Facturas

| Elemento | Localizador recomendado |
|---|---|
| Título de página | `getByTestId('page-title')` («My account», «Favorites») |
| Accesos de la cuenta | `getByTestId('nav-favorites')`, `nav-profile`, `nav-invoices`, `nav-messages` |
| Favorito | `getByTestId('favorite-{id}')` con `product-name`, `product-description` y `delete` |
| Tabla de facturas | `getByRole('table')`; filas con número (`INV-…`), dirección, fecha, total y enlace «Details». No hay `data-test` en la tabla, usar `getByRole('row', { name: /INV-2026000005/ })` |

### 3.6 Carrito y checkout (`#/checkout`)

| Paso | Elemento | Localizador recomendado |
|---|---|---|
| 1 Cart | Nombre del producto | `getByTestId('product-title')` |
| 1 Cart | Cantidad (editable) | `getByTestId('product-quantity')` |
| 1 Cart | Precio unitario | `getByTestId('product-price')` |
| 1 Cart | Subtotal de línea | `getByTestId('line-price')` |
| 1 Cart | Total | `getByTestId('cart-total')` |
| 1 Cart | Quitar producto | Sin `data-test`: enlace `a.btn-danger` con icono `fa-remove` en la fila (`getByRole('row').getByRole('link')`) |
| 1 Cart | Continuar | `getByTestId('proceed-1')` |
| 2 Sign in | Mensaje con sesión | Texto «Hello Jane Doe, you are already logged in. You can proceed to checkout.» |
| 2 Sign in | Continuar | `getByTestId('proceed-2')` |
| 3 Address | Campos | `getByTestId('address')`, `city`, `state`, `country`, `postcode` (placeholders «Your Address *», «Your City *», «Your State *», «Your Country *», «Your Postcode *») |
| 3 Address | Continuar | `getByTestId('proceed-3')` (botón sin texto visible; deshabilitado si falta un obligatorio) |
| 4 Payment | Método de pago | `getByTestId('payment-method')` — Bank Transfer, Cash on Delivery, Credit Card, Buy Now Pay Later, Gift Card, «Errror 304 - Missing Payment Gateway» |
| 4 Payment | Datos de cuenta | `getByTestId('account-name')`, `getByTestId('account-number')` |
| 4 Payment | Confirmar | `getByTestId('finish')` («Confirm») |
| Confirmación | Mensaje | `#order-confirmation` («Thanks for your order! Your invoice number is …») |
| Confirmación | Número de factura | `#invoice-number` |

### 3.7 Contacto (`#/contact`)

| Elemento | Localizador recomendado |
|---|---|
| Nombre | `getByTestId('first-name')` (label «First name», id `first_name`) |
| Apellido | `getByTestId('last-name')` (label «Last name») |
| Correo | `getByTestId('email')` (label «Email address») |
| Asunto | `getByTestId('subject')` — opciones: Customer service, Webmaster, Return, «Error 101: Subject not found», Payments, Warranty, Status of my order, «Error 202: Translation error» (esta última con valor vacío) |
| Mensaje | `getByTestId('message')` (placeholder «Massage») |
| Adjunto | `getByTestId('attachment')` |
| Enviar | `getByTestId('contact-submit')` |
| Errores por campo | `first-name-error`, `last-name-error`, `email-error`, `subject-error`, `message-error` |

## 4. Flujos observados

### 4.1 Catálogo, búsqueda y orden (sin sesión)
1. Abrir `#/`: 9 productos en la primera página (Combination Pliers $14.15, Pliers $12.01, Bolt Cutters $48.41, Long Nose Pliers $14.24, Slip Joint Pliers $9.17, Claw Hammer with Shock Reduction Grip $13.41, Hammer $12.58, Claw Hammer $11.48, Thor Hammer $11.14).
2. Escribir «hammer» en `search-query` y pulsar `search-submit`: aparece «Searched for: hammer» y 6 resultados: Thor Hammer $11.14, Hammer $12.58, Claw Hammer with Fiberglass Handle $20.14, Court Hammer $18.63, Claw Hammer with Shock Reduction Grip $13.41, Claw Hammer $11.48.
3. Elegir «Price (Low - High)»: el orden mostrado es $20.14, $18.63, $13.41, $12.58, $11.48, $11.14 (descendente).
4. `search-reset` vuelve al listado completo.
5. Orden sin búsqueda (primeros 9):
   - «Name (A - Z)»: Wood Saw, Thor Hammer, Slip Joint Pliers, Sledgehammer, … (Z→A).
   - «Name (Z - A)»: Adjustable Wrench, Angled Spanner, Belt Sander, … (A→Z).
   - «Price (High - Low)»: $4.92, $9.17, $11.14, … (ascendente).
   - «Price (Low - High)»: $125.23, $119.24, $100.79, … (descendente). Evidencia: `qa/evidencia/exploracion-orden-precio-menor-mayor.png`.
6. Filtro `category-3` (Hammer): Claw Hammer with Fiberglass Handle, Court Hammer, Sledgehammer, Claw Hammer with Shock Reduction Grip, Hammer, Claw Hammer, Thor Hammer (7).
7. Filtro `category-7` (Pliers): Bolt Cutters, Long Nose Pliers, Combination Pliers, Pliers, Slip Joint Pliers.
8. Filtro `brand-2`: Bolt Cutters, Slip Joint Pliers. Filtro `brand-1`: lista de herramientas eléctricas y Crane, Bulldozer, Excavator.

### 4.2 Detalle de producto y favoritos sin sesión
1. Abrir una tarjeta → `#/product/23` muestra nombre, CO₂, precio, descripción, cantidad 1, «Add to cart», «Add to favourites».
2. «Add to favourites» sin sesión → toast «Unauthorized, can not add product to your favorite list.»

### 4.3 Inicio de sesión (customer)
1. `#/auth/login`, pulsar `login-submit` con campos vacíos → solo `login-error`: «Invalid email or password». No aparecen mensajes de campo obligatorio.
2. Correo válido + contraseña «incorrecta123» → `login-error`: «Invalid email or password»; se queda en `#/auth/login`.
3. `customer@…` / `welcome01` → `#/account`, `page-title` «My account». El menú de usuario muestra «User Data not found».

### 4.4 Favoritos y carrito (customer, con sesión)
1. Abrir Claw Hammer (`#/product/8`, `unit-price` 11.48). «Add to favourites» → no se vio toast (el producto ya figuraba después en Favorites).
2. Pulsar `increase-quantity`: la cantidad sigue en 1 (probado dos veces).
3. «Add to cart» con cantidad 1 → `cart-quantity` = 1.
4. Escribir 2 en `quantity` y «Add to cart» → toast «Oeps, something went wrong.» y `cart-quantity` = 2 (se esperaban 3 unidades en total). Evidencia: `qa/evidencia/exploracion-detalle-agregar-carrito.png`.
5. Ir al carrito (`nav-cart` → `#/checkout`): Claw Hammer, cantidad 2, precio $11.48, `line-price` **$00.00**, `cart-total` $22.96.
6. Cambiar `product-quantity` a 3 → `cart-total` $34.44, `cart-quantity` 3, `line-price` sigue en $00.00. Evidencia: `qa/evidencia/exploracion-carrito-subtotal-linea.png`.
7. No se probó quitar el producto (se mantuvo para el checkout).

### 4.5 Checkout completo con Cash on Delivery (customer)
1. `proceed-1` → paso Sign in: «Hello Jane Doe, you are already logged in…». `proceed-2`.
2. Paso Address precargado: Test street 98, Vienna, State vacío, Austria, Postcode «missing value». `proceed-3` deshabilitado. Evidencia: `qa/evidencia/exploracion-checkout-direccion.png`.
3. Al llenar State «Wien» se habilita `proceed-3`; al vaciar City se deshabilita de nuevo. Se cambió Postcode a «1010» y se continuó.
4. Paso Payment: elegir «Cash on Delivery» muestra los campos «Your Account name *» y «Your Account number *» (los mismos que Bank Transfer) y `finish` queda deshabilitado. Evidencia: `qa/evidencia/exploracion-checkout-pago-cod.png`.
5. Solo tras llenar account-name «Jane Doe» y account-number «12345678» se habilita «Confirm». Hicieron falta dos clics en `finish` (el primero dejó el formulario visible con los campos vacíos).
6. Confirmación: «Thanks for your order! Your invoice number is INV-2026000005.» Evidencia: `qa/evidencia/exploracion-checkout-confirmacion.png`. El contador del carrito desaparece.
7. `#/account/invoices`: primera fila «INV-2026000005 · Test street 98 · 2026-10-25 13:58:16 · $34.44».
8. `#/account/favorites`: aparecen Combination Pliers, Slip Joint Pliers, Claw Hammer, Belt Sander (ambiente compartido: algunos pueden venir de otras sesiones).

### 4.6 Cierre de sesión (customer)
1. `nav-user-menu` → `nav-sign-out` → `#/auth/login`; la barra vuelve a mostrar `nav-sign-in`.

### 4.7 Contacto (sin sesión)
1. Enviar vacío → errores junto a cada campo: «First name is required», «Last name is required», «Email is required», «Subject is required», «Message is required».
2. Con apellido vacío y el resto lleno (asunto «Customer service») → «Last name is required» y además «Subject is required».
3. Con todos los campos llenos → sigue «Subject is required» y no se envía. Se probó también con «Webmaster» y «Return»: mismo resultado; el `select` tiene valor `customer-service`/`webmaster`/`return`. Evidencia: `qa/evidencia/exploracion-contacto-envio.png`.

### 4.8 Administrador
1. `admin@…` / `welcome01` → `#/admin/dashboard`, título «Sales over the years», menú «John Doe». Se cerró sesión con `nav-admin-menu` → `nav-sign-out` sin tocar nada más.

## 5. Observaciones (por verificar en el paso 3)

| # | Requisito | Observación | Evidencia |
|---|---|---|---|
| O1 | R2 | Todos los órdenes salen invertidos: «Price (Low - High)» muestra precios descendentes, «Price (High - Low)» ascendentes, «Name (A - Z)» muestra Z→A y viceversa. También con la búsqueda «hammer». — por verificar en el paso 3 | `qa/evidencia/exploracion-orden-precio-menor-mayor.png` |
| O2 | R2 | La búsqueda «hammer» devuelve 6 productos y no incluye «Sledgehammer», que sí aparece en la categoría Hammer y contiene la palabra. — por verificar en el paso 3 | Flujo 4.1 |
| O3 | R1 | Con campos vacíos el login no marca los campos como obligatorios; solo muestra «Invalid email or password». — por verificar en el paso 3 | Flujo 4.3 |
| O4 | R1 | Tras iniciar sesión, el menú de usuario muestra «User Data not found» en vez del nombre (el checkout sí saluda a «Jane Doe»). — por verificar en el paso 3 | Flujo 4.3 |
| O5 | R3 | El botón `increase-quantity` no cambia la cantidad (sigue en 1). — por verificar en el paso 3 | Flujo 4.4 |
| O6 | R3 | Al agregar un producto que ya está en el carrito sale «Oeps, something went wrong.» y el contador queda en 2 en vez de 3. — por verificar en el paso 3 | `qa/evidencia/exploracion-detalle-agregar-carrito.png` |
| O7 | R3 | En el carrito el subtotal de línea (`line-price`) es siempre «$00.00»; el total sí es cantidad × precio ($22.96 con 2, $34.44 con 3). — por verificar en el paso 3 | `qa/evidencia/exploracion-carrito-subtotal-linea.png` |
| O8 | R4 | La dirección del perfil viene incompleta (State vacío, Postcode «missing value»); hay que completarla para continuar. — por verificar en el paso 3 | `qa/evidencia/exploracion-checkout-direccion.png` |
| O9 | R4 | Con «Cash on Delivery» se piden nombre y número de cuenta y «Confirm» queda deshabilitado hasta llenarlos; además se necesitaron dos clics en «Confirm». — por verificar en el paso 3 | `qa/evidencia/exploracion-checkout-pago-cod.png` |
| O10 | R6 | El formulario de contacto no se puede enviar: «Subject is required» persiste con cualquier asunto elegido. — por verificar en el paso 3 | `qa/evidencia/exploracion-contacto-envio.png` |
| O11 | R5 | Con sesión, «Add to favourites» no mostró confirmación visible, aunque el producto aparece en Favorites (ambiente compartido; no se pudo asegurar que lo agregó esta sesión). — por verificar en el paso 3 | Flujo 4.4 |
| O12 | General | Textos erróneos en la interfaz: «Contakt», «Sorth», «Serch», placeholder «Massage», categoría «UNDEFINED», «Errror 304»; el enlace «Home» apunta a `#/contact`. | Flujo 4.1 |
| O13 | R2 | La imagen de Slip Joint Pliers (`pliers05.jpeg`) no carga (ancho natural 0) y la consola registra 404 de `/broken.png`. — por verificar en el paso 3 | Consola del navegador |

Datos que dejó la exploración en el ambiente compartido: pedido `INV-2026000005` de Jane Doe (3 × Claw Hammer, $34.44) y posiblemente Claw Hammer en sus favoritos.
