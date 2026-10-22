# Exploración de Swag Labs

> Archivo de ejemplo del modo demo. Un ciclo real lo escribe el agente con el navegador del MCP de Playwright; reemplázalo con tu ensayo real con `python3 -m app.guardar_ejemplos`.

## Resumen

Swag Labs (https://www.saucedemo.com) es una tienda en línea de demostración con un solo flujo de compra: inicio de sesión, catálogo de seis productos, carrito y checkout en tres pantallas. La aplicación identifica sus controles con el atributo `data-test`, lo que permite localizadores estables en todas las pantallas. Los usuarios de prueba están publicados en la pantalla de inicio de sesión; `problem_user` muestra diferencias visibles respecto a `standard_user` en el catálogo y en el checkout.

## Mapa de pantallas

| Pantalla | URL | Propósito |
|---|---|---|
| Inicio de sesión | `/` | Autenticar con usuario y contraseña |
| Catálogo | `/inventory.html` | Listar los seis productos, ordenarlos y agregarlos al carrito |
| Detalle de producto | `/inventory-item.html?id=N` | Ver un producto y agregarlo o quitarlo |
| Carrito | `/cart.html` | Revisar los productos elegidos y pasar al checkout |
| Checkout · datos | `/checkout-step-one.html` | Capturar nombre, apellido y código postal |
| Checkout · resumen | `/checkout-step-two.html` | Mostrar productos, subtotal, impuesto y total |
| Confirmación | `/checkout-complete.html` | Confirmar la orden |

## Inventario de elementos

### Inicio de sesión (`/`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Campo usuario | `getByTestId('username')` | placeholder «Username» |
| Campo contraseña | `getByTestId('password')` | placeholder «Password» |
| Botón Login | `getByTestId('login-button')` | también `getByRole('button', { name: 'Login' })` |
| Mensaje de error | `getByTestId('error')` | aparece bajo el formulario; texto empieza por «Epic sadface:» |

Mensajes de error observados:
- Contraseña incorrecta: «Epic sadface: Username and password do not match any user in this service».
- Usuario vacío: «Epic sadface: Username is required».
- Contraseña vacía: «Epic sadface: Password is required».
- Usuario bloqueado: «Epic sadface: Sorry, this user has been locked out.».

### Catálogo (`/inventory.html`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Título «Products» | `getByTestId('title')` | |
| Tarjetas de producto | `getByTestId('inventory-item')` | seis tarjetas |
| Nombre de producto | `getByTestId('inventory-item-name')` | enlace al detalle |
| Precio | `getByTestId('inventory-item-price')` | formato `$29.99` |
| Imagen de producto | `getByTestId('inventory-item-sauce-labs-backpack-img')` y similares | el sufijo cambia por producto; patrón `[data-test$="-img"]` |
| Botón Add to cart | `getByTestId('add-to-cart-sauce-labs-backpack')` | cambia a `remove-sauce-labs-backpack` al agregar |
| Selector de orden | `getByTestId('product-sort-container')` | opciones `az`, `za`, `lohi`, `hilo` |
| Ícono del carrito | `getByTestId('shopping-cart-link')` | lleva a `/cart.html` |
| Contador del carrito | `getByTestId('shopping-cart-badge')` | solo visible con productos |
| Menú lateral | `getByRole('button', { name: 'Open Menu' })` | id `react-burger-menu-btn` |
| Logout | `getByTestId('logout-sidebar-link')` | dentro del menú lateral |

Productos (orden inicial, A a Z): Sauce Labs Backpack ($29.99), Sauce Labs Bike Light ($9.99), Sauce Labs Bolt T-Shirt ($15.99), Sauce Labs Fleece Jacket ($49.99), Sauce Labs Onesie ($7.99), Test.allTheThings() T-Shirt (Red) ($15.99).

### Carrito (`/cart.html`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Filas del carrito | `getByTestId('inventory-item')` | |
| Nombre y precio | `getByTestId('inventory-item-name')`, `getByTestId('inventory-item-price')` | |
| Botón Remove | `getByTestId('remove-sauce-labs-backpack')` | |
| Continue Shopping | `getByTestId('continue-shopping')` | vuelve al catálogo |
| Checkout | `getByTestId('checkout')` | lleva a `/checkout-step-one.html` |

### Checkout · datos (`/checkout-step-one.html`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Nombre | `getByTestId('firstName')` | placeholder «First Name» |
| Apellido | `getByTestId('lastName')` | placeholder «Last Name» |
| Código postal | `getByTestId('postalCode')` | placeholder «Zip/Postal Code» |
| Continue | `getByTestId('continue')` | |
| Cancel | `getByTestId('cancel')` | vuelve al carrito |
| Mensaje de error | `getByTestId('error')` | «Error: First Name is required», «Error: Last Name is required», «Error: Postal Code is required» |

### Checkout · resumen (`/checkout-step-two.html`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Subtotal | `getByTestId('subtotal-label')` | «Item total: $29.99» |
| Impuesto | `getByTestId('tax-label')` | «Tax: $2.40» |
| Total | `getByTestId('total-label')` | «Total: $32.39» |
| Finish | `getByTestId('finish')` | |
| Cancel | `getByTestId('cancel')` | |

### Confirmación (`/checkout-complete.html`)

| Elemento | Localizador recomendado | Notas |
|---|---|---|
| Encabezado | `getByTestId('complete-header')` | «Thank you for your order!» |
| Back Home | `getByTestId('back-to-products')` | vuelve al catálogo |

## Flujos observados

### Inicio de sesión válido · standard_user
1. Abrir `/`.
2. Escribir `standard_user` y `secret_sauce`.
3. Pulsar Login → `/inventory.html` con el título «Products».

### Inicio de sesión inválido · standard_user con contraseña incorrecta
1. Abrir `/`, escribir `standard_user` y `otra`.
2. Pulsar Login → sigue en `/` y aparece «Epic sadface: Username and password do not match any user in this service».

### Inicio de sesión · locked_out_user
1. Abrir `/`, escribir `locked_out_user` y `secret_sauce`.
2. Pulsar Login → sigue en `/` y aparece «Epic sadface: Sorry, this user has been locked out.».

### Catálogo y orden · standard_user
1. En `/inventory.html` se ven seis productos, cada uno con imagen distinta.
2. Seleccionar `za` en el selector de orden → el primer producto es «Test.allTheThings() T-Shirt (Red)».
3. Seleccionar `lohi` → el primer precio es «$7.99»; con `hilo`, «$49.99».

### Carrito · standard_user
1. Pulsar «Add to cart» de Sauce Labs Backpack → el botón cambia a «Remove» y el contador del carrito muestra «1».
2. Abrir el carrito → una fila con «Sauce Labs Backpack» y «$29.99».
3. Pulsar «Remove» → la fila desaparece y el contador deja de verse.

### Checkout completo · standard_user
1. Agregar Sauce Labs Backpack y abrir el carrito.
2. Pulsar Checkout → `/checkout-step-one.html`.
3. Escribir nombre, apellido y código postal; pulsar Continue → `/checkout-step-two.html` con «Item total: $29.99», «Tax: $2.40» y «Total: $32.39».
4. Pulsar Finish → `/checkout-complete.html` con «Thank you for your order!».

### Checkout con campos vacíos · standard_user
1. En `/checkout-step-one.html`, pulsar Continue sin escribir nada → «Error: First Name is required».

### Checkout completo · problem_user
1. Iniciar sesión como `problem_user` y agregar Sauce Labs Backpack: el botón cambia a «Remove» y el contador muestra «1».
2. Abrir el carrito y pulsar Checkout.
3. Escribir nombre «Ana», apellido «Pérez» y código postal «10101». El campo Apellido se ve vacío después de escribir.
4. Pulsar Continue → sigue en `/checkout-step-one.html` con «Error: Last Name is required».

### Cierre de sesión · standard_user
1. Abrir el menú lateral y pulsar Logout → `/` con el formulario de inicio de sesión.

## Observaciones

- Con `problem_user`, las seis tarjetas del catálogo muestran la misma imagen (`/static/media/sl-404.168b1cce.jpg`), mientras que con `standard_user` cada producto tiene la suya. Por verificar en el paso 3.
- Con `problem_user`, cambiar el selector de orden a `za`, `lohi` o `hilo` no altera el orden de los productos. Por verificar en el paso 3.
- Con `problem_user`, el campo Apellido del checkout no conserva lo que se escribe; al continuar aparece «Error: Last Name is required». Por verificar en el paso 3.
- Con `problem_user`, el botón «Add to cart» de algunos productos (Sauce Labs Bolt T-Shirt, Sauce Labs Fleece Jacket, Test.allTheThings() T-Shirt) no cambia a «Remove» ni actualiza el contador. Por verificar en el paso 3.
- Con `performance_glitch_user`, el inicio de sesión tarda varios segundos pero el resto de los flujos se comporta como `standard_user`.
