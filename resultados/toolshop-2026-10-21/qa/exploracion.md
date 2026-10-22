# Exploración de Toolshop (with bugs)

- URL: https://with-bugs.practicesoftwaretesting.com
- Fecha: 2026-10-22 (UTC) · Navegador: Chromium del servidor MCP `playwright`
- Usuarios usados: `customer@practicesoftwaretesting.com` (Jane Doe) y `admin@practicesoftwaretesting.com` (solo entrar al panel y salir)

## 1. Resumen

Toolshop es una ferretería en línea de demostración (Angular, rutas con `#/`) con catálogo filtrable, detalle de producto, carrito y checkout en cuatro pasos (Cart → Sign in → Address → Payment), más cuenta del cliente (favoritos, facturas) y formulario de contacto.
Casi todos los controles tienen atributo `data-test`, lo que permite localizadores estables con `getByTestId`; varias pantallas cargan los datos de forma asíncrona desde `api-with-bugs.practicesoftwaretesting.com`, así que hay que esperar a que aparezcan los elementos.
Se completó una compra con «Cash on Delivery» (factura `INV-2026000005`), pero en el camino se vieron varios comportamientos que no coinciden con los requisitos (ver sección 5).

## 2. Mapa de pantallas

| Pantalla | URL | Propósito |
|---|---|---|
| Inicio / catálogo | `/#/` | Listar productos (nombre, precio, imagen), buscar, ordenar y filtrar por categoría, marca, precio y eco |
| Detalle de producto | `/#/product/{id}` | Ver nombre, precio, descripción; elegir cantidad; agregar al carrito o a favoritos |
| Inicio de sesión | `/#/auth/login` | Autenticar con correo y contraseña |
| Mi cuenta | `/#/account` | Portada de la cuenta del cliente con accesos a Favorites, Profile, Invoices, Messages |
| Favoritos | `/#/account/favorites` | Lista de productos favoritos del cliente |
| Facturas | `/#/account/invoices` | Lista de pedidos/facturas del cliente |
| Checkout (carrito y pasos) | `/#/checkout` | Asistente de 4 pasos en la misma URL: Cart → Sign in → Address → Payment → confirmación |
| Contacto | `/#/contact` | Formulario de contacto |
| Panel de administración | `/#/admin/dashboard` | Panel del administrador (fuera de alcance; solo se comprobó el acceso) |

## 3. Inventario de elementos

Notación: `testId=` equivale a `page.getByTestId('…')` (atributo `data-test`).

### Barra superior (todas las pantallas)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Logo | `getByRole('link', { name: 'Practice Software Testing - Toolshop' })` | Lleva a `/` |
| Home | `testId=nav-home` | En el snapshot su `href` es `#/contact` (ver observación O-11) |
| Categories (menú) | `testId=nav-categories` | Submenú: `nav-hand-tools`, `nav-power-tools`, `nav-robotic-tools` (texto «UNDEFINED»), `nav-special-tools` (texto «Chainsaws»), `nav-rentals` |
| Contact | `testId=nav-contact` | Texto visible «Contakt» |
| Sign in | `testId=nav-sign-in` | Solo sin sesión |
| Carrito | `testId=nav-cart` | Solo aparece cuando hay productos; va a `#/checkout` |
| Contador del carrito | `testId=cart-quantity` (id `lblCartCount`) | Unidades en el carrito |
| Menú de usuario | `testId=nav-user-menu` | Con sesión; contiene `nav-my-account`, `nav-my-favorites`, `nav-my-profile`, `nav-my-invoices`, `nav-my-messages`, `nav-sign-out` |
| Menú de admin | `testId=nav-admin-menu` | Solo admin; contiene `nav-sign-out` |

### Inicio / catálogo (`/#/`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Selector de orden | `testId=sort` | Opciones (valor ⇒ texto): `name,desc` ⇒ «Name (A - Z)», `name,asc` ⇒ «Name (Z - A)», `price,asc` ⇒ «Price (High - Low)», `price,desc` ⇒ «Price (Low - High)», `co2_rating,desc/asc`. Seleccionar por texto (etiqueta) |
| Cuadro de búsqueda | `testId=search-query` | Sin placeholder ni etiqueta |
| Botón buscar | `testId=search-submit` | Texto «Serch» |
| Limpiar búsqueda | `testId=search-reset` | Texto «X» |
| Leyenda de búsqueda | `testId=search-caption` | «Searched for: hammer» |
| Filtros de categoría | `testId=category-3` … `category-12` | 3 Hammer, 4 Hand Saw, 5 Wrench, 6 Screwdriver, 7 Pliers, 8 Grinder, 9 Sander, 10 Saw, 11 Drill, 12 Other |
| Filtros de marca | `testId=brand-1` … `brand-10` | «Brand name 1» … «Brand name 10» |
| Filtro eco | `testId=eco-friendly-filter` | Casilla «Show only eco-friendly products» |
| Rango de precio | `getByRole('slider', { name: 'ngx-slider' })` / `'ngx-slider-max'` | Sin `data-test` |
| Tarjeta de producto | `testId=product-{id}` (enlace a `#/product/{id}`) | Dentro: `product-name`, `product-price`, `eco-badge`, `co2-rating-badge`, `out-of-stock` |
| Paginación | `getByRole('navigation', { name: 'Pagination' })` | Se vio vacía en esta sesión; la página muestra 9 productos |

### Detalle de producto (`/#/product/{id}`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Nombre | `testId=product-name` (h1) | |
| Precio unitario | `testId=unit-price` | Solo el número, p. ej. «14.15» |
| Descripción | `testId=product-description` | |
| Disminuir cantidad | `testId=decrease-quantity` | |
| Cantidad | `testId=quantity` | Campo editable, valor inicial 1 |
| Aumentar cantidad | `testId=increase-quantity` | Ver O-4 |
| Add to cart | `testId=add-to-cart` | |
| Add to favourites | `testId=add-to-favorites` | |
| Aviso (toast) | `#toast-container` / `getByRole('alert')` | Mensajes de favoritos |

### Inicio de sesión (`/#/auth/login`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Correo | `testId=email` | Placeholder «Your E-mail *» |
| Contraseña | `testId=password` | Placeholder «Your password *» |
| Login | `testId=login-submit` | `input type=submit` |
| Error de login | `testId=login-error` | «Invalid email or password» |
| Registro / Olvidé contraseña | `testId=register-link`, `testId=forgot-password-link` | Fuera de alcance |

### Mi cuenta, favoritos y facturas

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Título de página | `testId=page-title` | «My account», «Favorites»; en facturas el h1 es «Invoices» |
| Accesos de cuenta | `testId=nav-favorites`, `nav-profile`, `nav-invoices`, `nav-messages` | |
| Favorito | `testId=favorite-{id}` con `product-name`, `product-description`, botón `delete` | |
| Tabla de facturas | `getByRole('row').filter({ hasText: 'INV-…' })` | Columnas: Invoice Number, Billing Address, Invoice Date, Total; enlace «Details». Sin `data-test` en filas |

### Checkout (`/#/checkout`)

| Paso | Elemento | Localizador recomendado | Notas |
|---|---|---|---|
| 1 Cart | Nombre del producto | `testId=product-title` | |
| 1 Cart | Cantidad (editable) | `testId=product-quantity` | Se actualiza al cambiar (Enter) |
| 1 Cart | Precio unitario | `testId=product-price` | «$14.15» |
| 1 Cart | Total de línea | `testId=line-price` | Ver O-5 |
| 1 Cart | Total del carrito | `testId=cart-total` | |
| 1 Cart | Quitar producto | `getByRole('row', …).locator('a.btn-danger')` | Sin `data-test` ni nombre accesible (icono `fa-remove`) |
| 1 Cart | Proceed to checkout | `testId=proceed-1` | |
| 2 Sign in | Mensaje con sesión | `getByText('you are already logged in')` | «Hello Jane Doe, you are already logged in…» |
| 2 Sign in | Proceed to checkout | `testId=proceed-2` | |
| 3 Address | Address, City, State, Country, Postcode | `testId=address`, `city`, `state`, `country`, `postcode` | Prellenados del perfil (ver O-6). Encabezado «Blliling Adress» |
| 3 Address | Continuar | `testId=proceed-3` | Botón sin texto visible (solo espacios); deshabilitado si falta un obligatorio |
| 4 Payment | Método de pago | `testId=payment-method` | Opciones: Bank Transfer, Cash on Delivery, Credit Card, Buy Now Pay Later, Gift Card, «Errror 304 - Missing Payment Gateway» |
| 4 Payment | Account name / Account number | `testId=account-name`, `testId=account-number` | Visibles incluso con Cash on Delivery (ver O-7) |
| 4 Payment | Confirm | `testId=finish` | Primer clic: «Payment was successful»; segundo clic: confirmación |
| Fin | Confirmación | `#order-confirmation` | «Thanks for your order! Your invoice number is INV-2026000005.» |

### Contacto (`/#/contact`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| First name | `testId=first-name` (o `getByLabel('First name')`) | |
| Last name | `testId=last-name` | |
| Email | `testId=email` | |
| Subject | `testId=subject` | Opciones: customer-service, webmaster, return, «Error 101: Subject not found», payments, warranty, status-of-order, «Error 202: Translation error». Ver O-9 |
| Message | `testId=message` | Placeholder «Massage» |
| Attachment | `testId=attachment` | Opcional |
| Send | `testId=contact-submit` | |
| Errores por campo | `testId=email-error`, `testId=subject-error` (patrón `{campo}-error`) | «Email is required», «Subject is required» |
| Confirmación | `getByRole('alert')` / `.alert-success` | «Thanks for your message! We will contact you shortly.» |

## 4. Flujos observados

### F1 · Catálogo, búsqueda y orden (sin sesión)
1. Abrir `/#/` → se listan 9 productos con nombre, precio e imagen.
2. Escribir «hammer» en `search-query` y pulsar `search-submit` → leyenda «Searched for: hammer»; 6 resultados: Thor Hammer $11.14, Hammer $12.58, Claw Hammer with Fiberglass Handle $20.14, Court Hammer $18.63, Claw Hammer with Shock Reduction Grip $13.41, Claw Hammer $11.48.
3. Elegir «Price (Low - High)» en `sort` → orden obtenido: $20.14, $18.63, $13.41, $12.58, $11.48, $11.14 (descendente). Evidencia: `qa/evidencia/exploracion-orden-precio-low-high.png`.
4. Pulsar `search-reset` y elegir «Name (A - Z)» → orden obtenido: Wood Saw, Thor Hammer, Slip Joint Pliers, Sledgehammer, Sheet Sander, Random Orbit Sander, Pliers, Phillips Screwdriver, Open-end Spanners (Set) (Z → A).
5. Marcar `category-3` (Hammer) → 7 productos, todos martillos: Thor Hammer, Sledgehammer, Hammer, Court Hammer, Claw Hammer with Shock Reduction Grip, Claw Hammer with Fiberglass Handle, Claw Hammer.

### F2 · Inicio de sesión inválido y válido (customer)
1. Ir a `/#/auth/login` y pulsar `login-submit` con los campos vacíos → se queda en el login y aparece `login-error` «Invalid email or password»; no hay indicación de campos obligatorios. Evidencia: `qa/evidencia/exploracion-login-campos-vacios.png`.
2. Correo `customer@…` + contraseña incorrecta → `login-error` «Invalid email or password»; no entra (la API `/users/login` respondió 401).
3. Correo `customer@…` + `welcome01` → redirige a `/#/account`, título «My account».
4. El menú de usuario muestra «User Data not found» (la consola registra 401 en `/users/me` justo después del login).

### F3 · Detalle y carrito (customer)
1. En `/#/` pulsar `product-1` → `/#/product/1` «Combination Pliers», precio 14.15, descripción y cantidad 1.
2. Pulsar `increase-quantity` dos veces → la cantidad sigue en 1. Evidencia: `qa/evidencia/exploracion-detalle-boton-mas-no-incrementa.png`.
3. Escribir 2 en `quantity` y pulsar `add-to-cart` → `cart-quantity` = 2.
4. Pulsar `nav-cart` → `/#/checkout` paso Cart: producto Combination Pliers, cantidad 2, precio $14.15, total de línea «$00.00», `cart-total` $28.30.
5. Cambiar `product-quantity` a 3 y Enter → `cart-total` $42.45, contador 3, total de línea sigue «$00.00». Evidencia: `qa/evidencia/exploracion-carrito-total-linea.png`.

### F4 · Checkout completo con Cash on Delivery (customer)
1. Desde el paso Cart pulsar `proceed-1` → paso Sign in: «Hello Jane Doe, you are already logged in. You can proceed to checkout.»
2. Pulsar `proceed-2` → paso Address con Address «Test street 98», City «Vienna», State vacío, Country «Austria», Postcode «missing value»; `proceed-3` deshabilitado. Evidencia: `qa/evidencia/exploracion-checkout-direccion-prellenada.png`.
3. Escribir State «Vienna» y Postcode «1010» → `proceed-3` se habilita. Al vaciar City se vuelve a deshabilitar (sin mensaje de error visible); se repuso «Vienna».
4. Pulsar `proceed-3` → paso Payment. Elegir «Cash on Delivery» en `payment-method` → `finish` sigue deshabilitado; se ven los campos Account name y Account number. Evidencia: `qa/evidencia/exploracion-checkout-pago-contra-entrega.png`.
5. Llenar Account name «Jane Doe» y Account number «123456» → `finish` se habilita.
6. Pulsar `finish` → «Payment was successful». Pulsar `finish` otra vez → `#order-confirmation`: «Thanks for your order! Your invoice number is INV-2026000005.»; el contador del carrito desaparece.
7. Ir a `/#/account/invoices` → primera fila: «INV-2026000005 · Test street 98 · 2026-10-22 00:23:46 · $42.45».

### F5 · Favoritos (customer y sin sesión)
1. Con sesión, en `/#/product/2` (Pliers) pulsar `add-to-favorites` → toast «Oeps, something went wrong.».
2. `/#/account/favorites` lista Combination Pliers, Pliers, Slip Joint Pliers y Belt Sander: Pliers ya estaba en favoritos (ambiente compartido).
3. Sin sesión, en `/#/product/3` pulsar `add-to-favorites` → toast «Unauthorized, can not add product to your favorite list.».

### F6 · Cierre de sesión (customer)
1. `nav-user-menu` → `nav-sign-out` → redirige a `/#/auth/login`, vuelve a verse `nav-sign-in` y desaparece el menú de usuario.

### F7 · Contacto (sin sesión)
1. `nav-contact` → `/#/contact`.
2. Llenar First name, Last name, Subject «Customer service» (con `selectOption`) y Message, dejando Email vacío; pulsar `contact-submit` → `email-error` «Email is required» y además `subject-error` «Subject is required», aunque el select tenía el valor `customer-service`. Evidencia: `qa/evidencia/exploracion-contacto-email-vacio.png`.
3. Llenar Email y volver a elegir asunto con `selectOption` → sigue «Subject is required» (el select queda `ng-pristine ng-invalid`).
4. Enfocar el select, cambiar la opción con la flecha abajo y salir con Tab, luego `contact-submit` → «Thanks for your message! We will contact you shortly.»

### F8 · Acceso del administrador
1. Login con `admin@…` / `welcome01` → `/#/admin/dashboard`, h1 «Sales over the years», menú `nav-admin-menu`. No se tocó nada; se cerró sesión con `nav-sign-out`.

### Usuarios con comportamiento anómalo
`qa/requisitos.md` no marca ningún usuario como «comportamiento anómalo» (los tres tienen comportamiento esperado normal), así que no hubo un checkout adicional por esa causa. `customer2@…` queda de respaldo y no se usó.

## 5. Observaciones (todas «por verificar en el paso 3»)

| # | Pantalla | Observación | Requisito | Evidencia |
|---|---|---|---|---|
| O-1 | Catálogo | «Price (Low - High)» ordena de mayor a menor (el valor de la opción es `price,desc`); «Price (High - Low)» tiene `price,asc` | R2 | `qa/evidencia/exploracion-orden-precio-low-high.png` |
| O-2 | Catálogo | «Name (A - Z)» ordena de Z a A (valor `name,desc`) y viceversa | R2 | Flujo F1 paso 4 |
| O-3 | Catálogo | La búsqueda «hammer» devuelve 6 productos y no incluye «Sledgehammer», que sí aparece en la categoría Hammer y cuyo nombre contiene «hammer» | R2 | Flujo F1 pasos 2 y 5 |
| O-4 | Detalle | El botón `increase-quantity` no aumenta la cantidad (sigue en 1) | R3 | `qa/evidencia/exploracion-detalle-boton-mas-no-incrementa.png` |
| O-5 | Carrito | El total de línea (`line-price`) muestra «$00.00» con cantidad 2 y 3; el total del carrito sí es correcto ($28.30 y $42.45) | R3 | `qa/evidencia/exploracion-carrito-total-linea.png` |
| O-6 | Checkout · Address | Prellenado incompleto: State vacío y Postcode con el texto literal «missing value». El botón de continuar no tiene texto. No se muestra mensaje junto al campo vacío; solo se deshabilita el botón | R4 | `qa/evidencia/exploracion-checkout-direccion-prellenada.png` |
| O-7 | Checkout · Payment | Con «Cash on Delivery» el botón Confirm queda deshabilitado hasta llenar Account name y Account number (campos de transferencia bancaria) | R4 | `qa/evidencia/exploracion-checkout-pago-contra-entrega.png` |
| O-8 | Login | Con campos vacíos no se indican como obligatorios: se envía al servidor y aparece «Invalid email or password» | R1 | `qa/evidencia/exploracion-login-campos-vacios.png` |
| O-9 | Contacto | El asunto elegido con `selectOption` no se registra («Subject is required» con valor seleccionado); con teclado + Tab sí. En el paso 3 hay que decidir cómo interactuar con este select | R6 | `qa/evidencia/exploracion-contacto-email-vacio.png` |
| O-10 | Cuenta | Tras el login el menú de usuario dice «User Data not found» (401 en `/users/me`), aunque el checkout sí saluda a «Jane Doe» | R1 | Flujo F2 paso 4 |
| O-11 | Barra superior | El enlace «Home» (`nav-home`) apunta a `#/contact` según el snapshot; textos con erratas: «Contakt», «Sorth», «Serch», «Blliling Adress», «Massage»; categoría «UNDEFINED» en el menú | — (no hay requisito explícito) | Snapshots del MCP |
| O-12 | Catálogo | La consola registra un 404 de `broken.png` en la portada | — | Consola del navegador |
| O-13 | Favoritos | Al agregar un producto que ya es favorito sale un error genérico «Oeps, something went wrong.»; en el paso 3 conviene usar un producto que no esté en la lista o quitarlo antes | R5 | Flujo F5 |

### Notas para el diseño y la ejecución
- El checkout deja datos en el ambiente compartido (cada compra crea una factura); el perfil de Jane Doe tiene State vacío y Postcode «missing value», así que las pruebas deben llenar esos campos.
- Las listas cargan de forma asíncrona: esperar a `product-name` o al texto del botón antes de interactuar.
- El selector de orden se elige por texto visible; los valores internos están invertidos (O-1, O-2).
