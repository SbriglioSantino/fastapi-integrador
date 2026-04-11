# Reglas de Negocio — API Integradora Unidad 1

Reglas extraídas del análisis exhaustivo del código implementado en `u1_ej_8_integrador/`.

---

## 1. Reglas de Identificación

### RN-01 — Generación de IDs

Los IDs se generan de forma autoincremental mediante un contador global en cada módulo.

| Módulo    | Contador inicial | Primer ID disponible |
|-----------|-----------------|----------------------|
| Categoría | `id_counter = 3` | 3 (hay 2 registros seed) |
| Producto  | `id_counter = 1` | 1 (arranca vacío) |

- El ID se asigna al momento de la creación y **nunca se modifica**
- El contador **nunca retrocede** (si se desactiva un registro, su ID no se reutiliza)
- No existe mecanismo para resetear el contador

### RN-02 — Datos iniciales (Seed Data)

Al iniciar el servidor se precargan dos categorías:

| ID | Código   | Descripción          | Activo |
|----|----------|----------------------|--------|
| 1  | `MUE-01` | Muebles de Oficina   | `true` |
| 2  | `ELE-02` | Electrónica          | `true` |

La lista de productos arranca **vacía**. Todos los datos son volátiles — se pierden al reiniciar el servidor.

---

## 2. Reglas de Validación

### RN-03 — Formato de código de categoría

El campo `codigo` (en categorías) y `categoria` (en productos) debe cumplir el patrón:

```
^[A-Z]{3}-\d{2}$
```

- Exactamente 3 letras **mayúsculas** (A-Z)
- Un guión (`-`)
- Exactamente 2 dígitos (0-9)
- Ejemplos válidos: `"MUE-01"`, `"ELE-02"`, `"HER-03"`
- Ejemplos inválidos: `"MUEBLES"`, `"mu-01"`, `"MUE-1"`, `"MUE-001"`

Si no cumple el formato → **422 Unprocessable Entity** (automático vía Pydantic).

### RN-04 — Longitud mínima de descripción

El campo `descripcion` de categoría debe tener al menos **3 caracteres**.

- `"AB"` → rechazado (422)
- `"ABC"` → aceptado

### RN-05 — Precio positivo

El campo `precio` de producto debe ser **estrictamente mayor a 0** (`gt=0`).

- `0` → rechazado
- `-50.00` → rechazado
- `0.01` → aceptado

### RN-06 — Stock no negativo

Los campos `stock` y `stock_minimo` de producto deben ser **mayores o iguales a 0** (`ge=0`).

- `-1` → rechazado
- `0` → aceptado
- `20` → aceptado

### RN-07 — Estado activo por defecto

El campo `activo` es **opcional** en la creación. Si no se envía, su valor por defecto es `true`.

Aplica tanto a categorías como a productos.

### RN-08 — ID en path debe ser positivo

Todos los endpoints que reciben `{id}` en la URL lo validan como entero **mayor a 0** (`gt=0`).

- `/productos/0` → 422
- `/productos/-1` → 422
- `/productos/1` → aceptado

### RN-09 — Límites de paginación

| Parámetro | Tipo | Default | Restricción |
|-----------|------|---------|-------------|
| `skip`    | int  | 0       | `ge=0` (no negativo) |
| `limit`   | int  | 10      | `le=50` (máximo 50) |

- `skip=-1` → 422
- `limit=51` → 422
- Sin parámetros → `skip=0, limit=10`

---

## 3. Reglas de Operaciones CRUD

### RN-10 — Creación de registros

- Todos los campos del schema `Create` son **obligatorios** (excepto `activo` que tiene default)
- El sistema asigna el ID automáticamente — no se acepta en el body
- El registro se agrega al final de la lista en memoria
- Responde con **201 Created** y el registro completo incluyendo el ID

### RN-11 — Listado con paginación

- Retorna un slice de la lista: `db[skip : skip + limit]`
- Si `skip` supera la cantidad total de registros → **lista vacía** (no es error)
- **No filtra** por estado `activo` — los registros desactivados aparecen en el listado
- Responde con **200 OK**

### RN-12 — Consulta por ID

- Búsqueda lineal en la lista en memoria
- Si el registro existe → **200 OK** con todos sus campos
- Si no existe → **404 Not Found**
- **No distingue** entre registros activos e inactivos — ambos se retornan

### RN-13 — Actualización total (PUT)

- Es un **reemplazo completo** — todos los campos son obligatorios (usa schema `Create`)
- Se **preserva el ID** original, se reemplazan todos los demás campos
- Si el registro existe → **200 OK** con los datos actualizados
- Si no existe → **404 Not Found**
- **No hay restricción** sobre actualizar registros inactivos
- Se aplican las mismas validaciones que en la creación

### RN-14 — Borrado lógico (Soft Delete)

- Endpoint dedicado: `PUT /{id}/desactivar`
- **No requiere body** en la request
- Cambia el campo `activo` a `false`
- **Preserva** todos los demás campos intactos (nombre, código, precio, stock, etc.)
- El registro **no se elimina** de la lista — sigue existiendo
- Si el registro existe → **200 OK** con el registro actualizado
- Si no existe → **404 Not Found**
- **Es idempotente**: desactivar un registro ya inactivo no produce error, simplemente lo deja en `false`

---

## 4. Reglas de Lógica de Negocio

### RN-15 — Alerta de stock bajo

El endpoint `GET /productos/{id}/stock` calcula si un producto está por debajo de su stock mínimo.

**Fórmula:**

```
bajo_stock_minimo = stock < stock_minimo
```

| stock | stock_minimo | bajo_stock_minimo | Explicación |
|-------|-------------|-------------------|-------------|
| 3     | 5           | `true`            | 3 < 5, hay alerta |
| 5     | 5           | `false`           | 5 no es menor que 5, **no hay alerta** |
| 10    | 5           | `false`           | 10 > 5, no hay alerta |
| 0     | 0           | `false`           | 0 no es menor que 0 |

El operador es **estrictamente menor** (`<`), no menor o igual (`<=`). Si el stock es **igual** al mínimo, **no se dispara la alerta**.

### RN-16 — Respuesta filtrada de stock

El endpoint de stock retorna **únicamente 3 campos** a través del schema `ProductoStockResponse`:

```json
{
  "stock": 10,
  "bajo_stock_minimo": false,
  "activo": true
}
```

No expone nombre, precio, categoría ni otros datos del producto.

---

## 5. Reglas de Manejo de Errores

### RN-17 — Error 404 (Recurso no encontrado)

Se dispara cuando se busca un ID que no existe en la lista. Mensajes exactos:

| Módulo    | Mensaje                        |
|-----------|--------------------------------|
| Categoría | `"Categoría no encontrada"`    |
| Producto  | `"Producto no encontrado"`     |

Formato de respuesta:

```json
{
  "detail": "Producto no encontrado"
}
```

### RN-18 — Error 422 (Validación automática)

FastAPI/Pydantic genera automáticamente el error **422 Unprocessable Entity** cuando:

- Un campo obligatorio falta en el body
- Un campo no cumple su constraint (regex, rango, tipo, longitud)
- Un path parameter (`id`) o query parameter (`skip`, `limit`) viola su restricción
- El body no es JSON válido

La respuesta incluye el detalle de **cada campo** que falló la validación.

### RN-19 — Status codes por operación

| Operación            | Éxito | Error ID no existe | Error validación |
|----------------------|-------|--------------------|------------------|
| Crear (POST)         | 201   | —                  | 422              |
| Listar (GET)         | 200   | —                  | 422 (query params) |
| Detalle (GET)        | 200   | 404                | 422 (path param) |
| Actualizar (PUT)     | 200   | 404                | 422              |
| Desactivar (PUT)     | 200   | 404                | 422 (path param) |
| Stock (GET)          | 200   | 404                | 422 (path param) |

---

## 6. Reglas Implícitas (No Enforceadas)

Estas reglas **no están implementadas** en el código actual. Son restricciones que el sistema **no valida**, lo que permite comportamientos que podrían ser problemáticos en producción.

### RN-20 — Sin validación de unicidad

- Se pueden crear **múltiples categorías** con el mismo `codigo`
- Se pueden crear **múltiples productos** con el mismo `nombre`
- No hay constraint de unicidad en ningún campo

### RN-21 — Sin validación de clave foránea

- El campo `categoria` en producto valida **solo el formato** (regex), **no la existencia**
- Se puede crear un producto con `categoria="ZZZ-99"` aunque no exista esa categoría
- No hay relación real entre los módulos de categoría y producto

### RN-22 — Sin filtrado de registros inactivos

- Los endpoints de listado (`GET /categorias/`, `GET /productos/`) retornan **todos** los registros
- No existe parámetro para filtrar por `activo=true`
- Los registros desactivados son indistinguibles de los activos en los listados

### RN-23 — Sin restricción sobre operaciones en registros inactivos

- Se puede **actualizar** un registro inactivo (cambiar su nombre, precio, etc.)
- Se puede **desactivar** un registro que ya está inactivo (operación idempotente)
- No existe endpoint para **reactivar** un registro (volver `activo` a `true`)
  - Workaround: usar PUT con `activo: true` en el body de actualización total

### RN-24 — Sin eliminación en cascada

- Desactivar una categoría **no afecta** a los productos que la referencian
- No hay propagación de cambios entre módulos

### RN-25 — Sin autenticación ni autorización

- Todos los endpoints son **públicos** — sin JWT, API keys, ni roles
- No hay distinción entre usuario y administrador
- No hay auditoría de quién realizó cada operación

### RN-26 — Sin timestamps

- No se registra `fecha_creacion` ni `fecha_actualizacion`
- No hay forma de saber cuándo se creó o modificó un registro

### RN-27 — Sin persistencia de datos

- Los datos se almacenan en **listas en memoria** (variables globales de Python)
- **Todo se pierde** al reiniciar el servidor
- No hay base de datos, archivo, ni ningún mecanismo de persistencia

### RN-28 — Sin seguridad ante concurrencia

- Las listas y contadores son variables globales **no protegidas**
- Requests simultáneos pueden causar condiciones de carrera en:
  - Generación de IDs (posible duplicación)
  - Modificación de la lista durante iteración
  - Lecturas inconsistentes durante escrituras
