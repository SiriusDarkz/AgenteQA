# Plan de pruebas · Toolshop (with bugs)

- Aplicación: Toolshop · https://with-bugs.practicesoftwaretesting.com
- Fuentes: `qa/requisitos.md` y `qa/exploracion.md` (2026-10-22). No hay `qa/historia-de-usuario.md`, así que el alcance sale de los requisitos R1 a R6 y de los 5 escenarios obligatorios.
- Navegador: Chromium (`@playwright/test`, paso 3).

## 1. Objetivo y alcance

Comprobar de punta a punta que la tienda cumple los requisitos funcionales:

- **R1** Inicio de sesión (válido, contraseña incorrecta, campos vacíos) → CP-01, CP-02, CP-03
- **R2** Catálogo, búsqueda, orden y filtro por categoría → CP-04, CP-05
- **R3** Detalle de producto y carrito (cantidad, contador, totales, quitar) → CP-06, CP-07
- **R4** Checkout con «Cash on Delivery» hasta la factura y su aparición en «Invoices» → CP-08
- **R5** Favoritos sin sesión y con sesión → CP-09
- **R6** Formulario de contacto (campo obligatorio vacío y envío válido) → CP-10

Escenarios obligatorios: 1 → CP-08 · 2 → CP-04 · 3 → CP-06 · 4 → CP-02 y CP-03 · 5 → CP-10.

**Fuera de alcance** (según los requisitos): panel de administración (salvo el acceso del admin, ver Riesgos), registro de usuarios, pagos distintos de «Cash on Delivery», la API, rendimiento, accesibilidad, móviles y navegadores distintos de Chromium. Tampoco se prueban el filtro por marca, el rango de precio ni el filtro eco, ni las erratas de textos (O-11), que no tienen requisito explícito.

## 2. Datos de prueba

| Dato | Valor |
|---|---|
| Cliente principal | `customer@practicesoftwaretesting.com` / `welcome01` (Jane Doe) |
| Cliente de respaldo | `customer2@practicesoftwaretesting.com` / `welcome01` (Jack Howe), solo si el principal queda con datos de otra prueba |
| Contraseña incorrecta | `contrasena-incorrecta` |
| Búsqueda | `hammer` |
| Producto para carrito y checkout | Combination Pliers (`/#/product/1`), precio unitario $14.15 → 2 u. = $28.30, 3 u. = $42.45 |
| Producto para favoritos | El de `/#/product/3` (su nombre se anota al abrir la página) |
| Categoría | Hammer (`category-3`) |
| Dirección de facturación | Address «Test street 98», City «Vienna», State «Vienna», Country «Austria», Postcode «1010» |
| Contacto | First name «Ana», Last name «Pérez», Email «ana.perez@example.com», Subject «Customer service», Message «Consulta de prueba del agente de QA sobre un pedido.» (más de 50 caracteres) |

## 3. Casos de prueba

| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |
|----|--------|-----------|---------|--------------|-------|--------------------|
| CP-01 | Inicio de sesión válido (R1) | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/`  2. Pulsar «Sign in» en la barra superior  3. Escribir el correo en «Your E-mail *» y `welcome01` en «Your password *»  4. Pulsar «Login» | La URL contiene `/#/account`, el título de página dice «My account» y en la barra se ve el menú de usuario en lugar de «Sign in» |
| CP-02 | Inicio de sesión con contraseña incorrecta (R1 · Esc. 4) | Alta | customer@practicesoftwaretesting.com | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Escribir el correo del cliente y la contraseña `contrasena-incorrecta`  3. Pulsar «Login» | Se ve el mensaje de error «Invalid email or password», la URL sigue conteniendo `/#/auth/login` y no aparece el menú de usuario |
| CP-03 | Inicio de sesión con campos vacíos (R1 · Esc. 4) | Alta | — (sin usuario) | Sesión cerrada | 1. Abrir `/#/auth/login`  2. Dejar vacíos correo y contraseña  3. Pulsar «Login» | Junto al campo de correo y junto al de contraseña aparece un mensaje que los indica como obligatorios (texto con «required»), la URL sigue conteniendo `/#/auth/login` y no aparece el menú de usuario |
| CP-04 | Búsqueda «hammer» ordenada por precio ascendente (R2 · Esc. 2) | Alta | — (sin sesión) | Sesión cerrada; catálogo cargado en `/` | 1. Abrir `/` y esperar a que se vean productos  2. Escribir `hammer` en el cuadro de búsqueda  3. Pulsar el botón de búsqueda  4. En el selector de orden elegir «Price (Low - High)»  5. Anotar nombres y precios de todos los resultados en el orden mostrado | Se ve la leyenda «Searched for: hammer»; hay al menos un resultado; todos los nombres contienen «hammer» (sin distinguir mayúsculas), y se incluye «Sledgehammer»; cada precio es menor o igual que el siguiente |
| CP-05 | Orden por nombre A-Z y filtro por categoría Hammer (R2) | Media | — (sin sesión) | Sesión cerrada; sin búsqueda activa | 1. Abrir `/` y esperar a que se vean productos  2. En el selector de orden elegir «Name (A - Z)»  3. Anotar los nombres en el orden mostrado  4. Marcar la casilla de categoría «Hammer»  5. Anotar los nombres resultantes | Tras el paso 2 los nombres están en orden alfabético ascendente (cada nombre ≤ el siguiente). Tras el paso 4 hay al menos un producto y todos los nombres contienen «Hammer» |
| CP-06 | Carrito: cantidad 2, luego 3, con totales recalculados (R3 · Esc. 3) | Alta | customer@practicesoftwaretesting.com | Sesión iniciada; carrito vacío | 1. Abrir `/#/product/1` (Combination Pliers)  2. Comprobar nombre, precio 14.15 y descripción  3. Escribir `2` en el campo de cantidad  4. Pulsar «Add to cart»  5. Pulsar el icono del carrito en la barra  6. Cambiar la cantidad de la fila a `3` y pulsar Enter | Tras 4: el contador del carrito muestra 2. Tras 5: la fila muestra «Combination Pliers», cantidad 2, precio $14.15, total de línea $28.30 y total del carrito $28.30. Tras 6: total de línea $42.45, total del carrito $42.45 y contador 3 |
| CP-07 | Quitar un producto del carrito (R3) | Media | customer@practicesoftwaretesting.com | Sesión iniciada; carrito vacío | 1. Abrir `/#/product/1`  2. Dejar cantidad 1 y pulsar «Add to cart»  3. Pulsar el icono del carrito  4. Pulsar el botón rojo de quitar (icono ✕) en la fila de Combination Pliers | Tras 2 el contador muestra 1. Tras 4 ya no hay ninguna fila con «Combination Pliers» y el contador del carrito deja de verse en la barra superior |
| CP-08 | Compra completa con «Cash on Delivery» hasta la factura (R4 · Esc. 1) | Alta | customer@practicesoftwaretesting.com | Sesión iniciada; carrito vacío | 1. Abrir `/#/product/1`, escribir `2` en cantidad y pulsar «Add to cart»  2. Ir al carrito y pulsar «Proceed to checkout»  3. En el paso Sign in, comprobar el saludo y pulsar «Proceed to checkout»  4. En Address, completar los campos vacíos o inválidos con los datos de la sección 2 (State «Vienna», Postcode «1010») y pulsar el botón de continuar  5. En Payment elegir «Cash on Delivery»  6. Pulsar «Confirm» (si aparece «Payment was successful», pulsarlo otra vez)  7. Anotar el número de factura  8. Abrir «My account → Invoices» | Tras 3 se ve «Hello Jane Doe, you are already logged in». Tras 5 el botón «Confirm» está habilitado sin pedir datos de otro método de pago. Tras 6 se ve «Thanks for your order! Your invoice number is INV-…» y el contador del carrito desaparece. Tras 8 hay una fila con ese número de factura y total $28.30 |
| CP-09 | Favoritos: aviso sin sesión y alta con sesión (R5) | Media | customer@practicesoftwaretesting.com | Sesión cerrada. El producto 3 no está en los favoritos del cliente (si está, quitarlo antes desde «My account → Favorites» con su botón de borrar) | 1. Sin sesión, abrir `/#/product/3`, anotar el nombre y pulsar «Add to favourites»  2. Iniciar sesión con el cliente  3. Abrir `/#/product/3` y pulsar «Add to favourites»  4. Abrir «My account → Favorites» | Tras 1 aparece un aviso que indica que hay que iniciar sesión (texto con «Unauthorized» o «log in»). Tras 3 no aparece ningún aviso de error. Tras 4 la lista contiene una tarjeta con el nombre anotado del producto 3 |
| CP-10 | Contacto: campo obligatorio vacío y luego envío válido (R6 · Esc. 5) | Media | — (sin sesión) | Sesión cerrada | 1. Abrir `/#/contact`  2. Llenar First name, Last name, Subject y Message con los datos de la sección 2, dejando Email vacío  3. Pulsar «Send»  4. Escribir el Email de la sección 2  5. Pulsar «Send» | Tras 3: junto al campo Email se ve «Email is required», no aparece ningún mensaje de error en los demás campos llenos y no se muestra la confirmación. Tras 5: se ve «Thanks for your message! We will contact you shortly.» |

## 4. Riesgos y supuestos

- **Ambiente compartido.** Otras personas usan las mismas cuentas: el carrito, los favoritos y las facturas pueden traer datos ajenos. Antes de CP-06, CP-07 y CP-08 se vacía el carrito; CP-09 quita el producto 3 de favoritos si ya estaba (O-13). Si el cliente principal queda inutilizable se usa `customer2@…`.
- **CP-08 crea una factura real** en el ambiente de demostración cada vez que se ejecuta. Es aceptable según los requisitos (no hay pagos reales).
- **Perfil incompleto de Jane Doe (O-6).** State vacío y Postcode «missing value»: el paso 4 de CP-08 los completa; se supone que eso no es parte de lo que se evalúa.
- **CP-08 y O-7.** La exploración vio que con «Cash on Delivery» «Confirm» queda deshabilitado hasta llenar Account name y Account number. El requisito R4 no pide esos datos, así que el caso espera «Confirm» habilitado y fallará en ese punto si el defecto sigue. Si la persona prefiere que la prueba llegue hasta la factura llenando esos campos, debe cambiar el paso 5 antes de aprobar.
- **CP-04 y Sledgehammer (O-3).** Se supone que «filtrar por nombre» incluye todo producto cuyo nombre contiene «hammer», también «Sledgehammer». Se elige el orden por su texto visible, no por el valor interno (O-1, O-2).
- **CP-03.** Los requisitos no fijan el texto exacto del aviso de obligatorio; se acepta cualquier mensaje junto al campo que contenga «required».
- **CP-06.** La cantidad se elige escribiendo en el campo, porque el botón «+» no incrementa (O-4); ese botón no se evalúa en este plan.
- **CP-10 y O-9.** El selector Subject no registra el valor si se fija por programa; en el paso 3 habrá que elegirlo como lo haría una persona (teclado o clic). Si aun así marca «Subject is required», es un defecto.
- **CP-09.** El texto exacto del aviso con sesión no se conoce; se comprueba la ausencia de error y la presencia en Favorites.
- **No incluidos** para quedarse en 10 casos: acceso del administrador (fuera de alcance casi por completo; ya se vio funcionar en la exploración, F8), filtro por marca, orden Z-A y precio descendente, «Home» que apunta a Contact (O-11), 404 de imagen (O-12) y «User Data not found» en el menú (O-10). Se pueden añadir editando el plan.
- **Usuarios de comportamiento anómalo:** los requisitos no marcan ninguno, así que no hay casos adicionales por esa causa.
- Las pantallas cargan de forma asíncrona: cada paso espera a que el elemento sea visible antes de comprobarlo.

Estado: PENDIENTE DE APROBACIÓN
