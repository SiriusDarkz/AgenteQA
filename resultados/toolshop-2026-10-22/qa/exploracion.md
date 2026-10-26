# Exploración · Toolshop (with bugs)

- URL explorada: https://with-bugs.practicesoftwaretesting.com
- Fecha: 2026-10-23 (hora del servidor; 2026-10-22 hora local)
- Herramienta: navegador del servidor MCP `playwright` (Chromium), snapshots de accesibilidad y lectura del DOM
- Usuarios usados: `customer@practicesoftwaretesting.com` (Jane Doe) y `admin@practicesoftwaretesting.com` (solo para comprobar el acceso al panel)

## 1. Resumen

Toolshop es una ferretería en línea de demostración hecha en Angular (SPA con rutas `#/...`) sobre una API en `api-with-bugs.practicesoftwaretesting.com`.
Ofrece catálogo con búsqueda, orden y filtros; detalle de producto con carrito y favoritos; checkout en 4 pasos (Cart → Sign in → Address → Payment); cuenta del cliente con facturas y favoritos; y un formulario de contacto.
Casi todos los controles llevan `data-test`; esta versión «with bugs» muestra varias diferencias visibles respecto a los requisitos, anotadas en la sección 5.

## 2. Mapa de pantallas

| Pantalla | URL | Propósito |
|---|---|---|
| Inicio / catálogo | `#/` | Listar productos con nombre, precio e imagen; buscar, ordenar y filtrar |
| Detalle de producto | `#/product/{id}` (ej. `#/product/8` Claw Hammer) | Ver nombre, precio, descripción; elegir cantidad; agregar al carrito o a favoritos |
| Login | `#/auth/login` | Iniciar sesión con correo y contraseña |
| My account | `#/account` | Panel del cliente con accesos a Favorites, Profile, Invoices, Messages |
| Favorites | `#/account/favorites` | Productos favoritos del cliente |
| Invoices | `#/account/invoices` | Facturas (pedidos) del cliente |
| Checkout | `#/checkout` | Carrito y proceso por pasos: Cart (1), Sign in (2), Address (3), Payment (4) y confirmación |
| Contact | `#/contact` | Formulario de contacto |
| Panel de administración | `#/admin/dashboard` | Dashboard del admin («Sales over the years»); fuera de alcance salvo el acceso |

## 3. Inventario de elementos

### Barra de navegación (todas las pantallas)

| Elemento | Localizador recomendado | Destino / nota |
|---|---|---|
| Logo | `getByRole('link', { name: 'Practice Software Testing - Toolshop' })` | `/` |
| Home | `getByTestId('nav-home')` | `href="#/contact"` (ver O-01) |
| Categories (menú) | `getByTestId('nav-categories')` | Despliega Hand Tools, Power Tools, «UNDEFINED», Chainsaws, Rentals |
| Contact | `getByTestId('nav-contact')` | `#/contact`; texto visible «Contakt» |
| Sign in | `getByTestId('nav-sign-in')` | `#/auth/login` (solo sin sesión) |
| Carrito | `getByTestId('nav-cart')` | `#/checkout`; aparece solo cuando hay productos |
| Contador del carrito | `getByTestId('cart-quantity')` | Muestra unidades totales |
| Menú de usuario | `getByTestId('nav-user-menu')` | Con sesión; texto visible «User Data not found» (ver O-02) |
| My account / favorites / profile / invoices / messages | `getByTestId('nav-my-account')`, `nav-my-favorites`, `nav-my-profile`, `nav-my-invoices`, `nav-my-messages` | Dentro del menú de usuario |
| Sign out | `getByTestId('nav-sign-out')` | Cierra sesión y lleva a `#/auth/login` |

### Inicio / catálogo (`#/`)

| Elemento | Localizador recomendado | Nota |
|---|---|---|
| Selector de orden | `getByTestId('sort')` | Opciones: Name (A - Z), Name (Z - A), Price (High - Low), Price (Low - High), CO₂ Rating (Best/Worst First). Título visible «Sorth» |
| Cuadro de búsqueda | `getByTestId('search-query')` | Sin placeholder ni etiqueta accesible |
| Botón buscar | `getByTestId('search-submit')` | Texto visible «Serch» |
| Limpiar búsqueda | `getByTestId('search-reset')` | Botón «X» |
| Texto de búsqueda activa | `getByTestId('search-caption')` | «Searched for: hammer» |
| Filtro por categoría | `getByTestId('category-{id}')` | 3 Hammer, 4 Hand Saw, 5 Wrench, 6 Screwdriver, 7 Pliers, 8 Grinder, 9 Sander, 10 Saw, 11 Drill, 12 Other |
| Filtro por marca | `getByTestId('brand-{id}')` | brand-1 … brand-10 («Brand name 1» … «Brand name 10») |
| Solo ecológicos | `getByTestId('eco-friendly-filter')` | Checkbox |
| Rango de precio | `getByRole('slider', { name: 'ngx-slider' })` / `'ngx-slider-max'` | 0 a 200 |
| Tarjeta de producto | `getByTestId('product-{id}')` | Enlace a `#/product/{id}` |
| Nombre / precio en tarjeta | `getByTestId('product-name')`, `getByTestId('product-price')` | Precio con formato `$12.58` |
| Sin stock | `getByTestId('out-of-stock')` | Ej. Long Nose Pliers |
| Paginación | `getByRole('navigation', { name: 'Pagination' })` | page 2, page 3, Next page |

### Detalle de producto (`#/product/{id}`)

| Elemento | Localizador recomendado | Nota |
|---|---|---|
| Nombre | `getByTestId('product-name')` | `h1` |
| Precio unitario | `getByTestId('unit-price')` | Sin símbolo: `11.48` |
| Descripción | `getByTestId('product-description')` | |
| Disminuir cantidad | `getByTestId('decrease-quantity')` | |
| Cantidad | `getByTestId('quantity')` | Spinbutton, valor inicial 1 |
| Aumentar cantidad | `getByTestId('increase-quantity')` | Ver O-07 |
| Add to cart | `getByTestId('add-to-cart')` | |
| Add to favourites | `getByTestId('add-to-favorites')` | |
| Avisos (toast) | `getByRole('alert')` | Mensajes emergentes temporales |

### Login (`#/auth/login`)

| Elemento | Localizador recomendado | Nota |
|---|---|---|
| Correo | `getByTestId('email')` | placeholder «Your E-mail *», id `email` |
| Contraseña | `getByTestId('password')` | placeholder «Your password *», id `password` |
| Login | `getByTestId('login-submit')` | |
| Error de login | `getByTestId('login-error')` | «Invalid email or password» |
| Registrarse / olvidé contraseña | `getByTestId('register-link')`, `getByTestId('forgot-password-link')` | Fuera de alcance |

### My account / Favorites / Invoices

| Elemento | Localizador recomendado | Nota |
|---|---|---|
| Título de página | `getByTestId('page-title')` | «My account», «Favorites», «Invoices» |
| Accesos de la cuenta | `getByTestId('nav-favorites')`, `nav-profile`, `nav-invoices`, `nav-messages` | |
| Favorito | `getByTestId('favorite-{id}')` | Contiene `product-name`, `product-description` y botón `delete` |
| Tabla de facturas | `getByRole('row', { name: /INV-\d+/ })` | Columnas: Invoice Number, Billing Address, Invoice Date, Total, Details. Las filas no tienen `data-test` |

### Checkout (`#/checkout`)

| Paso | Elemento | Localizador recomendado | Nota |
|---|---|---|---|
| 1 Cart | Nombre del producto | `getByTestId('product-title')` | |
| 1 Cart | Cantidad (editable) | `getByTestId('product-quantity')` | Se actualiza al salir del campo |
| 1 Cart | Precio unitario | `getByTestId('product-price')` | |
| 1 Cart | Total de la línea | `getByTestId('line-price')` | Ver O-08 |
| 1 Cart | Total del carrito | `getByTestId('cart-total')` | |
| 1 Cart | Quitar producto | `getByRole('row', { name: /Claw Hammer/ }).locator('a.btn-danger')` | Sin `data-test` ni nombre accesible; única alternativa por clase |
| 1 Cart | Continuar | `getByTestId('proceed-1')` | |
| 2 Sign in | Continuar | `getByTestId('proceed-2')` | Con sesión: «Hello Jane Doe, you are already logged in…» |
| 3 Address | Dirección, ciudad, estado, país, código postal | `getByTestId('address')`, `city`, `state`, `country`, `postcode` | Precargados desde el perfil |
| 3 Address | Continuar | `getByTestId('proceed-3')` | Botón sin texto (ver O-10); deshabilitado si falta un campo obligatorio |
| 4 Payment | Método de pago | `getByTestId('payment-method')` | Bank Transfer, Cash on Delivery, Credit Card, Buy Now Pay Later, Gift Card, «Errror 304 - Missing Payment Gateway» |
| 4 Payment | Nombre / número de cuenta | `getByTestId('account-name')`, `getByTestId('account-number')` | Aparecen al elegir Cash on Delivery (ver O-11) |
| 4 Payment | Confirm | `getByTestId('finish')` | Se pulsa dos veces: pago y luego pedido |
| 4 Payment | Mensaje de pago | `getByText('Payment was successful')` | Sin `data-test` |
| Confirmación | Mensaje con factura | `locator('#order-confirmation')` | «Thanks for your order! Your invoice number is INV-…». Sin `data-test` |

### Contact (`#/contact`)

| Elemento | Localizador recomendado | Nota |
|---|---|---|
| First name | `getByTestId('first-name')` | label «First name», id `first_name` |
| Last name | `getByTestId('last-name')` | label «Last name», id `last_name` |
| Email | `getByTestId('email')` | label «Email address» |
| Subject | `getByTestId('subject')` | Opciones: Customer service, Webmaster, Return, «Error 101: Subject not found», Payments, Warranty, Status of my order, «Error 202: Translation error» |
| Message | `getByTestId('message')` | placeholder «Massage» |
| Attachment | `getByTestId('attachment')` | Opcional |
| Enviar | `getByTestId('contact-submit')` | |
| Errores por campo | `getByTestId('{campo}-error')` | Ej. `last-name-error` «Last name is required», `subject-error` «Subject is required» |

## 4. Flujos observados

### F1 · Catálogo, búsqueda y orden (sin sesión)
1. Abrir `#/`: se listan 9 productos por página con nombre, precio e imagen (Combination Pliers $14.15, Pliers $12.01, …, Thor Hammer $11.14).
2. Escribir «hammer» en `search-query` y pulsar `search-submit`: aparece «Searched for: hammer» y 6 resultados: Thor Hammer $11.14, Hammer $12.58, Claw Hammer with Fiberglass Handle $20.14, Court Hammer $18.63, Claw Hammer with Shock Reduction Grip $13.41, Claw Hammer $11.48. Todos contienen «Hammer».
3. Elegir «Price (Low - High)» en `sort`: el orden mostrado es $20.14, $18.63, $13.41, $12.58, $11.48, $11.14 (de mayor a menor). Ver O-05.
4. Elegir «Name (A - Z)»: el orden mostrado es Thor Hammer, Hammer, Court Hammer, Claw Hammer with Shock Reduction Grip, Claw Hammer with Fiberglass Handle, Claw Hammer (de Z a A). Ver O-05.
5. Limpiar búsqueda; marcar `category-7` (Pliers): quedan Combination Pliers, Pliers, Long Nose Pliers, Bolt Cutters, Slip Joint Pliers.
6. Marcar `brand-2`: quedan Bolt Cutters y Slip Joint Pliers.

### F2 · Inicio de sesión inválido y válido (customer@…)
1. Ir a `#/auth/login` y pulsar `login-submit` con los campos vacíos: aparece solo «Invalid email or password» (`login-error`); no hay mensaje de obligatorio por campo. Ver O-03.
2. Correo `customer@practicesoftwaretesting.com` y contraseña incorrecta: «Invalid email or password»; se queda en `#/auth/login`.
3. Contraseña `welcome01`: entra a `#/account`, título «My account».

### F3 · Detalle de producto y carrito (customer@…)
1. Desde `#/`, abrir `product-8` → `#/product/8` (Claw Hammer, precio 11.48).
2. Pulsar `increase-quantity` dos veces: la cantidad se queda en 1. Ver O-07.
3. Escribir 2 en `quantity` y pulsar `add-to-cart`: el contador `cart-quantity` muestra 2.
4. Pulsar `nav-cart` → `#/checkout`: Claw Hammer, cantidad 2, precio $11.48, total de la línea «$00.00», total del carrito $22.96. Ver O-08.
5. Cambiar `product-quantity` a 3 y salir del campo: total del carrito $34.44, contador 3; total de la línea sigue «$00.00».

### F4 · Checkout completo con Cash on Delivery (customer@…)
1. En el carrito (3 × Claw Hammer, $34.44) pulsar `proceed-1`.
2. Paso Sign in: «Hello Jane Doe, you are already logged in. You can proceed to checkout.» Pulsar `proceed-2`.
3. Paso Address (título «Blliling Adress»): precargado Test street 98, Vienna, estado vacío, Austria, código postal «missing value»; `proceed-3` deshabilitado. Ver O-09 y O-10.
4. Completar estado «Vienna» y código postal «1010»: `proceed-3` se habilita. Al vaciar ciudad se deshabilita de nuevo (los obligatorios no pueden ir vacíos). Pulsar `proceed-3`.
5. Paso Payment: elegir «Cash on Delivery». Aparecen «Your Account name *» y «Your Account number *» y `finish` queda deshabilitado. Ver O-11.
6. Llenar cuenta «Jane Doe» / «123456789»: `finish` se habilita. Pulsar `finish`: «Payment was successful».
7. Pulsar `finish` otra vez: «Thanks for your order! Your invoice number is INV-2026000005.» El carrito se vacía.
8. Ir a `#/account/invoices`: primera fila INV-2026000005 | Test street 98 | 2026-10-23 00:33:36 | $34.44.

### F5 · Favoritos (customer@… y sin sesión)
1. Con sesión, en `#/product/7` (Hammer) pulsar `add-to-favorites`: aviso «Oeps, something went wrong.» Ver O-12.
2. En `#/account/favorites` aparecen Combination Pliers, Slip Joint Pliers, Hammer y Belt Sander.
3. Sin sesión, en `#/product/9` (Thor Hammer) pulsar `add-to-favorites`: aviso «Unauthorized, can not add product to your favorite list.»

### F6 · Cierre de sesión (customer@…)
1. Abrir `nav-user-menu` y pulsar `nav-sign-out`: lleva a `#/auth/login`, vuelve a verse `nav-sign-in` y el `localStorage` queda vacío.

### F7 · Contacto (sin sesión)
1. En `#/contact` llenar nombre «Jane», correo, asunto «Customer service» y un mensaje de más de 50 caracteres; dejar apellido vacío; pulsar `contact-submit`.
2. Aparecen «Last name is required» y también «Subject is required» (el selector vale `customer-service`). No se envía.
3. Llenar apellido «Doe» y enviar: sigue «Subject is required»; no se envía. Igual con «Webmaster». No apareció mensaje de confirmación. Ver O-13.

### F8 · Acceso del administrador (admin@…)
1. Login con `admin@practicesoftwaretesting.com` / `welcome01` → `#/admin/dashboard`, título «Sales over the years». No se tocó nada; se cerró la sesión.

### Usuarios con «comportamiento anómalo»
`qa/requisitos.md` no marca a ningún usuario como «comportamiento anómalo» (los tres son cliente normal, segundo cliente y administrador), así que no hubo checkout adicional por ese motivo. `customer2@` queda de reserva, como dicen los requisitos.

## 5. Observaciones (todas por verificar en el paso 3)

| Id | Pantalla | Observación | Evidencia |
|---|---|---|---|
| O-01 | Navegación | El enlace «Home» (`nav-home`) apunta a `#/contact`. | DOM: `href="#/contact"` |
| O-02 | Navegación | Con sesión iniciada, el menú de usuario muestra «User Data not found» en vez del nombre (en el checkout sí sale «Jane Doe»). | Snapshot de `#/account` |
| O-03 | Login | Con campos vacíos no se marcan como obligatorios; solo sale «Invalid email or password» (R1). | `qa/evidencia/exploracion-login-campos-vacios.png` |
| O-04 | Varias | Errores de texto: «Contakt», «Sorth», «Serch», «Blliling Adress», placeholder «Massage», categoría «UNDEFINED» en el menú (`#/category/undefined`), opciones «Errror 304 - Missing Payment Gateway», «Error 101/202» en el asunto. | Snapshots |
| O-05 | Catálogo | El orden sale invertido: «Price (Low - High)» ordena de mayor a menor y «Name (A - Z)» ordena de Z a A. Los valores internos de las opciones están cruzados (`price,desc` = «Low - High», `name,desc` = «A - Z») (R2, escenario 2). | `qa/evidencia/exploracion-orden-precio-low-high.png` |
| O-06 | Catálogo | La imagen de Slip Joint Pliers (`pliers05.jpeg`) no había cargado (`naturalWidth` 0) al leerla; la consola registra un 404 de `/broken.png`. Puede ser carga diferida. | Consola del navegador |
| O-07 | Detalle | El botón «+» (`increase-quantity`) no cambia la cantidad; se queda en 1 (R3). | `qa/evidencia/exploracion-boton-mas-cantidad.png` |
| O-08 | Carrito | El total de la línea (`line-price`) muestra «$00.00» con 2 y con 3 unidades, aunque el total del carrito sí es cantidad × precio ($22.96, $34.44) (R3, escenario 3). | `qa/evidencia/exploracion-carrito-cantidad-2.png` |
| O-09 | Checkout · Address | La dirección precargada del perfil llega incompleta: estado vacío y código postal con el texto «missing value». | `qa/evidencia/exploracion-checkout-direccion.png` |
| O-10 | Checkout · Address | El botón para continuar (`proceed-3`) no tiene texto visible. | `qa/evidencia/exploracion-checkout-direccion.png` |
| O-11 | Checkout · Payment | Con «Cash on Delivery» se piden nombre y número de cuenta, y «Confirm» queda deshabilitado hasta llenarlos. Además, la confirmación necesita dos clics en «Confirm» (R4, escenario 1). | `qa/evidencia/exploracion-checkout-pago-cod.png` |
| O-12 | Favoritos | Al agregar Hammer con sesión salió «Oeps, something went wrong.», pero Hammer aparece en Favorites. No se puede saber si ya estaba ahí (ambiente compartido) (R5). | Toast leído del DOM |
| O-13 | Contacto | Con todos los campos válidos el formulario no se envía: sale «Subject is required» aunque el asunto esté elegido (probado con «Customer service» y «Webmaster») (R6, escenario 5). | `qa/evidencia/exploracion-contacto-apellido-vacio.png`, `qa/evidencia/exploracion-contacto-todos-validos.png` |
| O-14 | Consola | En cada carga de página: 401 en `/users/me` sin sesión, 500 en `/users/refresh` después del cierre de sesión y 404 en `/broken.png`. | Consola del navegador |

### Datos para el plan
- Productos útiles: `product-8` Claw Hammer ($11.48), `product-7` Hammer ($12.58), `product-9` Thor Hammer ($11.14).
- Ambiente compartido: el número de factura y la lista de favoritos cambian por la actividad de otros usuarios; las pruebas deben buscar el patrón `INV-\d+`, no un número fijo.
- Pedido real creado en esta exploración: INV-2026000005 (Jane Doe, $34.44).
