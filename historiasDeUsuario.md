# Historias de Usuario — API Integradora Unidad 1

Historias de usuario extraídas del análisis del código implementado en `u1_ej_8_integrador/`.

---

## Módulo: Categorías

### HU-01 — Crear una categoría

> Como administrador del sistema, quiero crear una nueva categoría de productos proporcionando un código, descripción y estado, para poder organizar los productos del inventario.

**Criterios de aceptación:**

- El código debe seguir el formato `^[A-Z]{3}-\d{2}$` (3 letras mayúsculas, guión, 2 dígitos). Ej: `"MUE-01"`
- La descripción debe tener al menos 3 caracteres
- El campo `activo` es opcional y por defecto es `true`
- El sistema asigna un ID autoincremental
- Responde con status `201 Created` y la categoría creada (incluyendo el ID)
- Si el código no cumple el formato → `422 Unprocessable Entity`
- Si la descripción tiene menos de 3 caracteres → `422 Unprocessable Entity`

---

### HU-02 — Listar categorías con paginación

> Como usuario del sistema, quiero obtener un listado paginado de categorías para poder navegar los resultados de forma eficiente.

**Criterios de aceptación:**

- Acepta parámetros de query `skip` (default: 0, mínimo: 0) y `limit` (default: 10, máximo: 50)
- Retorna una lista de categorías con todos sus campos (id, codigo, descripcion, activo)
- Si `skip` supera la cantidad total de registros, retorna lista vacía
- Si `skip` es negativo → `422`
- Si `limit` supera 50 → `422`
- Responde con status `200 OK`

---

### HU-03 — Consultar una categoría por ID

> Como usuario del sistema, quiero consultar el detalle de una categoría específica por su ID para ver toda su información.

**Criterios de aceptación:**

- El ID debe ser un entero mayor a 0
- Si la categoría existe, retorna sus datos completos con status `200 OK`
- Si la categoría no existe → `404 Not Found` con mensaje `"Categoría no encontrada"`
- Si el ID es ≤ 0 → `422 Unprocessable Entity`

---

### HU-04 — Actualizar una categoría (reemplazo completo)

> Como administrador del sistema, quiero actualizar todos los datos de una categoría existente para corregir o modificar su información.

**Criterios de aceptación:**

- Se envían TODOS los campos (codigo, descripcion, activo) — es un reemplazo total (PUT)
- Se conserva el ID original
- Se aplican las mismas validaciones que en la creación (formato de código, longitud de descripción)
- Si la categoría existe, retorna los datos actualizados con status `200 OK`
- Si la categoría no existe → `404 Not Found`
- Si los datos no son válidos → `422 Unprocessable Entity`

---

### HU-05 — Desactivar una categoría (borrado lógico)

> Como administrador del sistema, quiero desactivar una categoría sin eliminarla físicamente para mantener el historial y la integridad de datos.

**Criterios de aceptación:**

- No requiere cuerpo en la request
- Cambia el campo `activo` a `false`
- Conserva todos los demás campos intactos
- La categoría desactivada sigue siendo consultable y listable
- Si la categoría existe, retorna sus datos actualizados con status `200 OK`
- Si la categoría no existe → `404 Not Found`

---

## Módulo: Productos

### HU-06 — Crear un producto

> Como administrador del sistema, quiero crear un nuevo producto con su nombre, categoría, precio, stock y stock mínimo para incorporarlo al inventario.

**Criterios de aceptación:**

- `nombre` es obligatorio (string, sin restricción de longitud)
- `categoria` debe seguir el formato `^[A-Z]{3}-\d{2}$` (referencia al código de categoría)
- `precio` debe ser mayor a 0 (float)
- `stock` debe ser mayor o igual a 0 (entero)
- `stock_minimo` debe ser mayor o igual a 0 (entero)
- `activo` es opcional, por defecto `true`
- El sistema asigna un ID autoincremental
- **No se valida** que la categoría referenciada exista en el módulo de categorías
- Responde con status `201 Created` y el producto creado
- Campos inválidos → `422 Unprocessable Entity`

---

### HU-07 — Listar productos con paginación

> Como usuario del sistema, quiero obtener un listado paginado de productos para navegar el inventario.

**Criterios de aceptación:**

- Acepta parámetros de query `skip` (default: 0, mínimo: 0) y `limit` (default: 10, máximo: 50)
- Retorna lista de productos con todos sus campos (id, nombre, categoria, precio, stock, stock_minimo, activo)
- Mismas reglas de paginación que categorías
- Responde con status `200 OK`

---

### HU-08 — Consultar un producto por ID

> Como usuario del sistema, quiero consultar el detalle de un producto específico por su ID para ver toda su información.

**Criterios de aceptación:**

- El ID debe ser un entero mayor a 0
- Si el producto existe, retorna todos sus campos con status `200 OK`
- Si el producto no existe → `404 Not Found` con mensaje `"Producto no encontrado"`
- Si el ID es ≤ 0 → `422 Unprocessable Entity`

---

### HU-09 — Actualizar un producto (reemplazo completo)

> Como administrador del sistema, quiero actualizar todos los datos de un producto existente para corregir precios, stock u otra información.

**Criterios de aceptación:**

- Se envían TODOS los campos — es un reemplazo total (PUT)
- Se conserva el ID original
- Se aplican las mismas validaciones que en la creación
- Si el producto existe, retorna los datos actualizados con status `200 OK`
- Si el producto no existe → `404 Not Found`
- Si los datos no son válidos → `422 Unprocessable Entity`

---

### HU-10 — Desactivar un producto (borrado lógico)

> Como administrador del sistema, quiero desactivar un producto sin eliminarlo físicamente para mantener el registro histórico.

**Criterios de aceptación:**

- No requiere cuerpo en la request
- Cambia el campo `activo` a `false`
- Conserva todos los demás campos intactos
- El producto desactivado sigue siendo consultable y listable
- Si el producto existe, retorna sus datos actualizados con status `200 OK`
- Si el producto no existe → `404 Not Found`

---

### HU-11 — Consultar estado de stock de un producto

> Como usuario del sistema, quiero consultar el estado de stock de un producto para saber si está por debajo del mínimo y tomar decisiones de reposición.

**Criterios de aceptación:**

- Retorna únicamente: `stock`, `bajo_stock_minimo` y `activo`
- La alerta `bajo_stock_minimo` es `true` cuando `stock < stock_minimo`
- Si `stock == stock_minimo`, la alerta es `false` (igual NO dispara alerta)
- Si `stock > stock_minimo`, la alerta es `false`
- Si el producto existe, responde con status `200 OK`
- Si el producto no existe → `404 Not Found`

---

## Transversales

### HU-12 — Documentación automática de la API

> Como desarrollador, quiero que la API exponga documentación interactiva automática (Swagger/OpenAPI) para poder explorar y probar los endpoints.

**Criterios de aceptación:**

- La API tiene título `"API Integradora - Unidad 1"`, versión `1.0.0`
- Los endpoints están agrupados por tags: `"Categorías"` y `"Productos"`
- Swagger UI disponible en `/docs`
- ReDoc disponible en `/redoc`
- Los schemas de request/response se generan automáticamente desde los modelos Pydantic
