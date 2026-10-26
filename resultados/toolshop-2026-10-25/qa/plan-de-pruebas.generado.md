# Plan de pruebas · Toolshop (with bugs)

- URL: https://with-bugs.practicesoftwaretesting.com
- Fecha: 2026-10-25
- Fuentes: `qa/requisitos.md` (R1–R6 y escenarios obligatorios 1–5) y `qa/exploracion.md`. No existe `qa/historia-de-usuario.md`.

## 1. Objetivo y alcance

Verificar de principio a fin los flujos de cliente de Toolshop según los requisitos R1–R6, con foco en los cinco escenarios obligatorios del ciclo: compra completa con «Cash on Delivery», búsqueda «hammer» con orden por precio ascendente, recálculo del carrito, inicio de sesión inválido y formulario de contacto.

**Dentro del alcance:** inicio de sesión (R1), catálogo, búsqueda, orden y filtro por categoría (R2), detalle de producto y carrito (R3), checkout con «Cash on Delivery» y factura en «Invoices» (R4), favoritos con y sin sesión (R5), formulario de contacto (R6) y la comprobación de que el administrador entra al panel.

**Fuera del alcance** (según `qa/requisitos.md`): uso del panel de administración más allá de la entrada, registro de usuarios, pagos distintos de «Cash on Delivery», API, rendimiento, accesibilidad, móviles y navegadores distintos de Chromium. Tampoco se verifican textos mal escritos de la interfaz (O12 de la exploración), por no estar en ningún requisito.

| Requisito | Casos |
|---|---|
| R1 · Inicio de sesión | CP-01, CP-02, CP-03, CP-10 |
| R2 · Catálogo, búsqueda y orden | CP-04, CP-05 |
| R3 · Detalle de producto y carrito | CP-06 |
| R4 · Checkout | CP-07 |
| R5 · Favoritos | CP-08 |
| R6 · Contacto | CP-09 |

| Escenario obligatorio | Caso |
|---|---|
| 1 · Compra completa con Cash on Delivery | CP-07 |
| 2 · Búsqueda «hammer» + precio ascendente | CP-04 |
| 3 · Carrito cantidad 2 → 3 | CP-06 |
| 4 · Login con contraseña incorrecta y campos vacíos | CP-02, CP-03 |
| 5 · Contacto con campo vacío y luego válido | CP-09 |

## 2. Datos de prueba

| Dato | Valor | Uso |
|---|---|---|
| Cliente principal | `customer@practicesoftwaretesting.com` / `welcome01` (Jane Doe) | CP-01, CP-07 |
| Segundo cliente | `customer2@practicesoftwaretesting.com` / `welcome01` (Jack Howe) | CP-08 (para no mezclar favoritos con la compra de Jane Doe) |
| Administrador | `admin@practicesoftwaretesting.com` / `welcome01` | CP-10 (solo entrar y cerrar sesión) |
| Contraseña incorrecta | `incorrecta123` | CP-02 |
| Producto para carrito y checkout | Claw Hammer, `#/product/8`, precio unitario 11.48 | CP-06, CP-07 |
| Producto para favoritos | Cordless Drill 20V, `#/product/23` | CP-08 |
| Búsqueda | `hammer` | CP-04 |
| Categoría | Hammer (`category-3`) | CP-05 |
| Dirección (solo si algún campo viene vacío) | State «Wien», Postcode «1010» | CP-07 |
| Datos de cuenta (solo si el pago los pide) | Account name «Jane Doe», Account number «12345678» | CP-07 |
| Contacto | First name «Ana», Last name «Pérez», Email «ana.perez@example.com», Subject «Customer service», Message «Mensaje de prueba del agente de QA para verificar el formulario de contacto.» | CP-09 |

## 3. Casos de prueba

| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |
|----|--------|-----------|---------|--------------|-------|--------------------|
| CP-01 | Inicio de sesión válido | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Escribir el correo en «Your E-mail *» (`email`)  3. Escribir `welcome01` en «Your password *» (`password`)  4. Pulsar «Login» (`login-submit`) | La URL contiene `#/account`, `page-title` muestra «My account» y `nav-sign-in` ya no está visible |
| CP-02 | Inicio de sesión con contraseña incorrecta | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Escribir el correo del cliente  3. Escribir `incorrecta123` como contraseña  4. Pulsar «Login» | `login-error` muestra «Invalid email or password»; la URL sigue conteniendo `#/auth/login`; `nav-sign-in` sigue visible |
| CP-03 | Inicio de sesión con campos vacíos | Alta | — (sin usuario) | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Dejar vacíos correo y contraseña  3. Pulsar «Login» | Se muestran los mensajes de campo obligatorio junto a cada campo: `email-error` visible y `password-error` visible; la URL sigue conteniendo `#/auth/login` |
| CP-04 | Búsqueda «hammer» ordenada por precio de menor a mayor | Alta | — (sin sesión) | Página principal cargada | 1. Abrir `/`  2. Escribir `hammer` en el cuadro de búsqueda (`search-query`)  3. Pulsar el botón de buscar (`search-submit`)  4. En el selector de orden (`sort`) elegir «Price (Low - High)»  5. Leer nombres y precios de las tarjetas resultantes | `search-term` muestra «hammer»; hay al menos 1 resultado; todos los `product-name` contienen «hammer» (sin distinguir mayúsculas); la lista de `product-price` está en orden ascendente (cada precio ≥ al anterior) |
| CP-05 | Catálogo y filtro por categoría Hammer | Media | — (sin sesión) | Página principal cargada | 1. Abrir `/`  2. Comprobar que la primera página lista tarjetas de producto  3. Marcar el filtro de categoría «Hammer» (`category-3`)  4. Leer los nombres de las tarjetas resultantes | Paso 2: hay 9 tarjetas y cada una tiene `product-name` no vacío, `product-price` con formato `$n.nn` y una imagen cargada (ancho natural > 0). Paso 4: hay al menos 1 tarjeta y todos los `product-name` contienen «hammer» (sin distinguir mayúsculas) |
| CP-06 | Carrito: cantidad 2, cambio a 3 y quitar producto | Alta | — (sin sesión) | Carrito vacío (contexto nuevo del navegador) | 1. Abrir `/#/product/8` (Claw Hammer) y anotar `unit-price` (11.48)  2. Escribir `2` en la cantidad (`quantity`)  3. Pulsar «Add to cart»  4. Comprobar el contador del carrito (`cart-quantity`)  5. Abrir el carrito (`nav-cart`)  6. Comprobar cantidad y total  7. Cambiar la cantidad del producto (`product-quantity`) a `3` y salir del campo  8. Pulsar el botón de quitar de la fila del producto | Paso 4: `cart-quantity` = 2. Paso 6: `product-title` = «Claw Hammer», `product-quantity` = 2, `product-price` = $11.48 y `cart-total` = $22.96. Paso 7: `cart-total` = $34.44 y `cart-quantity` = 3. Paso 8: el producto ya no aparece en el carrito y `cart-quantity` ya no muestra unidades |
| CP-07 | Compra completa con Cash on Delivery hasta la factura | Alta | customer@practicesoftwaretesting.com | Sesión iniciada como Jane Doe; carrito vacío | 1. Abrir `/#/product/8` y pulsar «Add to cart» con cantidad 1  2. Abrir el carrito (`nav-cart`) y pulsar «Proceed to checkout» (`proceed-1`)  3. En el paso Sign in pulsar `proceed-2`  4. En Address, si State o Postcode vienen vacíos o con «missing value», escribir «Wien» y «1010»; pulsar `proceed-3`  5. En Payment elegir «Cash on Delivery» en `payment-method`; si aparecen «Account name» y «Account number», llenarlos con «Jane Doe» y «12345678»  6. Pulsar «Confirm» (`finish`) una vez  7. Anotar el número de factura  8. Abrir «My account → Invoices» (`#/account/invoices`) | Paso 6: aparece `#order-confirmation` con «Thanks for your order!» y `#invoice-number` con un valor de la forma `INV-` seguido de dígitos. Paso 8: la tabla de facturas tiene una fila con ese número y total $11.48 |
| CP-08 | Favoritos sin sesión y con sesión | Media | customer2@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/#/product/23` (Cordless Drill 20V) sin sesión  2. Pulsar «Add to favourites» (`add-to-favorites`)  3. Iniciar sesión como customer2  4. Abrir `#/account/favorites` y, si Cordless Drill 20V ya está, quitarlo con `delete`  5. Volver a `/#/product/23` y pulsar «Add to favourites»  6. Abrir «My account → Favorites» | Paso 2: aparece un mensaje (`alert`) que indica que hay que iniciar sesión (el observado es «Unauthorized, can not add product to your favorite list.»). Paso 6: `page-title` = «Favorites» y hay una tarjeta de favorito cuyo `product-name` es «Cordless Drill 20V» |
| CP-09 | Contacto: campo obligatorio vacío y luego envío válido | Media | — (sin sesión) | Página de contacto cargada (`#/contact`) | 1. Llenar nombre, correo, asunto «Customer service» y mensaje con los datos de prueba, dejando vacío el apellido (`last-name`)  2. Pulsar «Send» (`contact-submit`)  3. Escribir «Pérez» en el apellido  4. Pulsar «Send» | Paso 2: `last-name-error` muestra «Last name is required»; no aparece ningún otro `*-error` (los demás campos están llenos) y el formulario sigue visible. Paso 4: no hay ningún `*-error` visible, el formulario deja de mostrarse y aparece un mensaje de confirmación de envío |
| CP-10 | El administrador entra al panel | Baja | admin@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Iniciar sesión con el administrador  3. Comprobar la pantalla  4. Cerrar sesión con `nav-admin-menu` → `nav-sign-out` sin tocar nada más | Paso 3: la URL contiene `#/admin/dashboard` y se ve el título «Sales over the years». Paso 4: la URL contiene `#/auth/login` |

## 4. Riesgos y supuestos

- **Ambiente compartido.** Otras personas usan las mismas cuentas: el carrito, los favoritos y las facturas pueden traer datos ajenos. Por eso cada prueba usa un contexto de navegador nuevo, CP-08 limpia el favorito antes de agregarlo y CP-07 busca su propia factura por número, no la primera fila.
- **Datos que se crean.** CP-07 genera un pedido real en la cuenta de Jane Doe y CP-08 deja Cordless Drill 20V en los favoritos de Jack Howe. Es el uso previsto del sitio de práctica.
- **Defectos ya observados que probablemente harán fallar casos** (de `qa/exploracion.md`, sección 5; las expectativas no se ajustan): O1 orden invertido (CP-04), O3 login vacío sin mensajes por campo (CP-03), O7/O6 comportamiento del carrito (CP-06 puede verse afectado), O8/O9 dirección incompleta y doble clic en «Confirm» (CP-07), O10 asunto que nunca se acepta (CP-09), O13 imagen rota (CP-05).
- **CP-07 · dirección y datos de cuenta.** R4 dice que la dirección viene del perfil y que los obligatorios no pueden ir vacíos; el plan completa State y Postcode solo si vienen vacíos, para poder llegar al pago. R4 no dice si «Cash on Delivery» debe pedir datos de cuenta: si los pide, se llenan (supuesto) y la observación O9 queda como posible defecto para el paso 4. «Confirm» se pulsa una sola vez, como haría un cliente.
- **CP-04 · completitud de la búsqueda.** R2 exige que *solo* queden productos con «hammer» en el nombre; el caso no exige que aparezca «Sledgehammer» (O2). Si quieres comprobar también que no falte ningún martillo, añade esa aserción antes de aprobar.
- **CP-06 · subtotal de línea.** R3 habla del «total»; el caso verifica `cart-total`. El subtotal de línea `line-price` (siempre «$00.00» en la exploración, O7) no se afirma porque R3 no lo menciona explícitamente. El botón de quitar no tiene `data-test`: se localizará por rol dentro de la fila del producto.
- **CP-08 · mensaje con sesión.** R5 no exige un mensaje de confirmación al agregar con sesión, solo que el producto aparezca en Favorites; la falta de toast (O11) no se evalúa.
- **CP-09 · texto de confirmación.** La exploración nunca logró enviar el formulario, así que no se conoce el texto exacto de confirmación; la aserción será que no hay errores, que el formulario desaparece y que se muestra un mensaje de confirmación.
- **Filtros por marca (R2).** No se incluyen: las tarjetas no muestran la marca, así que no hay una aserción concreta posible sin abrir cada producto. Queda como cobertura pendiente.
- **Menú de usuario «User Data not found» (O4).** R1 no exige mostrar el nombre del cliente; no se verifica.
- **Cantidad con `increase-quantity` (O5).** No se usa; CP-06 escribe la cantidad directamente en el campo.

Estado: PENDIENTE DE APROBACIÓN
