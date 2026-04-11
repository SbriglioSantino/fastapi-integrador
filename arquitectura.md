# Arquitectura — API Integradora Unidad 1

## Visión General

API REST construida con **FastAPI** que gestiona productos y categorías de un inventario. Arquitectura modular de tres capas con almacenamiento en memoria. Proyecto educativo que integra los conceptos de las unidades 1 a 7.

**Stack:** FastAPI + Pydantic + Uvicorn (todo incluido en `fastapi[standard]`)

---

## Estructura del Proyecto

```
u1_ej_8_integrador/
├── app/
│   ├── main.py                         ← Factory de la app + registro de routers
│   └── modules/
│       ├── categoria/
│       │   ├── routers.py              ← Endpoints HTTP (/categorias)
│       │   ├── schemas.py              ← Modelos Pydantic (Base, Create, Update, Read)
│       │   └── services.py             ← Lógica de negocio + almacenamiento en memoria
│       └── producto/
│           ├── routers.py              ← Endpoints HTTP (/productos)
│           ├── schemas.py              ← Modelos Pydantic + ProductoStockResponse
│           └── services.py             ← Lógica de negocio + alerta de stock
├── tests/
│   └── test_api.http                   ← 13 casos de prueba (VS Code REST Client)
│
u_01/                                   ← Ejercicios progresivos (ej1 a ej7)
```

---

## Patrón Arquitectónico: Tres Capas por Módulo

Cada módulo de dominio (categoria, producto) replica la misma estructura de tres capas:

```
┌─────────────────────────────────────────────────┐
│  ROUTERS  (Capa HTTP)                           │
│  - Define endpoints y status codes              │
│  - Valida Path/Query params                     │
│  - Delega lógica al service                     │
│  - Maneja errores HTTP (404)                    │
├─────────────────────────────────────────────────┤
│  SCHEMAS  (Capa de Validación / Contratos)      │
│  - Define modelos Pydantic                      │
│  - Valida datos de entrada (regex, rangos, etc) │
│  - Filtra datos de salida (response_model)      │
├─────────────────────────────────────────────────┤
│  SERVICES (Capa de Negocio + Datos)             │
│  - Operaciones CRUD                             │
│  - Reglas de negocio (alerta de stock)          │
│  - Persistencia en listas en memoria            │
└─────────────────────────────────────────────────┘
```

Las capas se comunican **siempre hacia abajo**: Router → Service. Los schemas son compartidos entre ambas capas como contratos de datos.

---

## Cadena de Imports (Grafo de Dependencias)

```
main.py
 ├── producto.routers.router ──→ producto.schemas
 │                             ──→ producto.services ──→ producto.schemas
 │
 └── categoria.routers.router ──→ categoria.schemas
                                ──→ categoria.services ──→ categoria.schemas
```

- `main.py` solo conoce los **routers** (no importa schemas ni services directamente)
- Cada **router** importa sus propios schemas y services via imports relativos (`. schemas`, `. services`)
- Cada **service** importa solo los schemas que necesita (`CategoriaCreate`, `CategoriaRead`)
- **No hay dependencias cruzadas** entre módulos (categoria no importa nada de producto y viceversa)

---

## Factory Pattern (Punto de Entrada)

```python
# app/main.py
def create_app() -> FastAPI:
    app = FastAPI(
        title="API Integradora - Unidad 1",
        description="Conceptos: Path, Query, Body, Pydantic, Errores.",
        version="1.0.0"
    )
    app.include_router(producto_router)
    app.include_router(categoria_router)
    return app

app = create_app()
```

La función `create_app()` permite crear múltiples instancias de la app (útil para testing). Se ejecuta inmediatamente para exponer `app` al servidor ASGI (Uvicorn).

---

## Patrón de Schemas (Herencia Pydantic)

Ambos módulos usan el mismo patrón de herencia para separar responsabilidades:

```
                    CategoriaBase
                   ┌──────────────────────┐
                   │ codigo    (regex)     │
                   │ descripcion (min: 3)  │
                   │ activo    (default T) │
                   └──────┬───────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   CategoriaCreate  CategoriaRead  CategoriaUpdate
   (hereda todo,    (agrega id)    (todo opcional,
    campos req.)                    BaseModel aparte)
```

| Schema   | Uso                          | Campos requeridos       |
|----------|------------------------------|-------------------------|
| Base     | Campos comunes + validaciones| Todos                   |
| Create   | Request body en POST/PUT     | Todos (hereda de Base)  |
| Read     | Response model               | Todos + `id`            |
| Update   | Pensado para PATCH (no usado)| Ninguno (todos opcionales)|

**Producto** agrega además `ProductoStockResponse` — un schema especializado que expone solo 3 campos (`stock`, `bajo_stock_minimo`, `activo`), demostrando filtrado de respuesta.

---

## Persistencia (In-Memory)

No hay base de datos. Cada service mantiene su estado en variables globales:

```python
# categoria/services.py
db_categorias: List[CategoriaRead] = [
    CategoriaRead(id=1, codigo="MUE-01", descripcion="Muebles de Oficina", activo=True),
    CategoriaRead(id=2, codigo="ELE-02", descripcion="Electrónica", activo=True),
]
id_counter = 3   # Siguiente ID disponible

# producto/services.py
db_productos: List[ProductoRead] = []   # Arranca vacío
id_counter = 1
```

**Características:**
- IDs autoincrementales via contador global
- Búsqueda lineal por ID (`for p in db: if p.id == id`)
- Paginación via slicing de lista (`db[skip : skip + limit]`)
- Los datos se pierden al reiniciar el servidor

---

## Flujo de un Request (Ejemplo: POST /productos/)

```
Cliente HTTP
    │
    │  POST /productos/  { nombre, categoria, precio, stock, stock_minimo }
    ▼
FastAPI Routing ──→ match /productos/ ──→ producto/routers.py:alta_producto()
    │
    ▼
Pydantic (ProductoCreate)
    ├─ categoria matches ^[A-Z]{3}-\d{2}$ ?
    ├─ precio > 0 ?
    ├─ stock >= 0 ?  stock_minimo >= 0 ?
    │
    ├─ FALLA → 422 Unprocessable Entity (automático, con detalle del error)
    │
    └─ OK → ProductoCreate instance
              │
              ▼
         services.crear(data)
              │
              ├─ id_counter++ → asigna ID
              ├─ ProductoRead(id=N, **data.model_dump())
              ├─ db_productos.append(nuevo)
              └─ return ProductoRead
                    │
                    ▼
         Router recibe ProductoRead
              │
              ▼
         response_model=ProductoRead filtra campos
              │
              ▼
         HTTP 201 Created + JSON { id, nombre, categoria, precio, stock, stock_minimo, activo }
```

---

## Flujo de Negocio: Alerta de Stock

El único endpoint con lógica de negocio real es `GET /productos/{id}/stock`:

```python
# producto/services.py
def obtener_estado_stock(id):
    producto = obtener_por_id(id)
    alerta_stock = producto.stock < producto.stock_minimo
    return {
        "stock": producto.stock,
        "bajo_stock_minimo": alerta_stock,    # True si stock < stock_minimo
        "activo": producto.activo,
    }
```

**Regla:** `bajo_stock_minimo = True` solamente cuando `stock` es **estrictamente menor** que `stock_minimo`. Si son iguales, la alerta es `False`.

El response se filtra a través de `ProductoStockResponse` — el cliente solo recibe estos 3 campos, no el producto completo.

---

## Borrado Lógico (Soft Delete)

Ambos módulos implementan desactivación en lugar de eliminación:

```
PUT /categorias/{id}/desactivar    →  activo = False
PUT /productos/{id}/desactivar     →  activo = False
```

- No requiere body en la request
- No elimina el registro de la lista
- El registro desactivado **sigue apareciendo** en listados y consultas (no hay filtro por `activo`)
- No existe endpoint para reactivar

---

## Validaciones

### Automáticas (Pydantic → 422)

| Campo       | Módulo    | Regla                          | Ejemplo válido |
|-------------|-----------|--------------------------------|----------------|
| codigo      | Categoría | `^[A-Z]{3}-\d{2}$`            | `"MUE-01"`    |
| descripcion | Categoría | `min_length=3`                 | `"Muebles"`   |
| categoria   | Producto  | `^[A-Z]{3}-\d{2}$`            | `"ELE-02"`    |
| precio      | Producto  | `gt=0`                         | `150.50`      |
| stock       | Producto  | `ge=0`                         | `20`          |
| stock_minimo| Producto  | `ge=0`                         | `5`           |
| id (path)   | Ambos     | `gt=0`                         | `1`           |
| skip (query)| Ambos     | `ge=0`, default `0`            | `0`           |
| limit (query)| Ambos    | `le=50`, default `10`          | `10`          |

### Manuales (Router → 404)

Cada endpoint que recibe un `{id}` verifica si el service retornó `None` y lanza `HTTPException(404)` con mensajes:
- `"Categoría no encontrada"`
- `"Producto no encontrado"`

---

## Endpoints

### Categorías (`/categorias`)

| Método | Ruta                        | Status | Descripción             |
|--------|-----------------------------|--------|-------------------------|
| POST   | `/categorias/`              | 201    | Crear categoría         |
| GET    | `/categorias/`              | 200    | Listar con paginación   |
| GET    | `/categorias/{id}`          | 200/404| Detalle por ID          |
| PUT    | `/categorias/{id}`          | 200/404| Reemplazo total         |
| PUT    | `/categorias/{id}/desactivar`| 200/404| Borrado lógico         |

### Productos (`/productos`)

| Método | Ruta                        | Status | Descripción             |
|--------|-----------------------------|--------|-------------------------|
| POST   | `/productos/`               | 201    | Crear producto          |
| GET    | `/productos/`               | 200    | Listar con paginación   |
| GET    | `/productos/{id}`           | 200/404| Detalle por ID          |
| PUT    | `/productos/{id}`           | 200/404| Reemplazo total         |
| PUT    | `/productos/{id}/desactivar`| 200/404| Borrado lógico         |
| GET    | `/productos/{id}/stock`     | 200/404| Estado de stock + alerta|

---

## Decisiones de Diseño y Trade-offs

| Decisión | Por qué | Trade-off |
|----------|---------|-----------|
| **In-memory storage** | Proyecto educativo, sin complejidad de DB | Datos volátiles, no apto para producción |
| **Módulo por recurso** | Separación clara, escalable a más módulos | Más archivos que un monolito simple |
| **PUT para updates** (no PATCH) | Simplicidad — reemplazo total | No permite actualización parcial de campos |
| **Soft delete sin filtro** | Enseña el concepto de borrado lógico | Los inactivos siguen apareciendo en listados |
| **Sin validación de FK** | Categoría en producto es solo formato regex | Permite productos con categorías inexistentes |
| **Sin unicidad de código** | Simplicidad | Se pueden crear categorías con código duplicado |
| **Funciones, no clases** | Services como funciones puras (más simple) | Estado global (listas, counters) dificulta testing |
| **Factory pattern** | Permite crear múltiples instancias para tests | Mínimo overhead adicional |

---

## Ejercicios Progresivos (u_01/)

Los ejercicios del 1 al 7 construyen los conceptos que se integran en el proyecto final:

| Ejercicio | Concepto |
|-----------|----------|
| ej1       | Endpoints GET básicos, respuestas JSON |
| ej2       | Path parameters (`/items/{id}`) |
| ej3       | Enum types en path params |
| ej4       | Query parameters (`skip`, `limit`), opcionales, booleanos |
| ej5       | Request body con Pydantic `BaseModel` |
| ej6       | Validación avanzada con `Query()` y `Annotated` |
| ej7       | `response_model`, herencia de schemas, status codes, `HTTPException` |
| **ej8**   | **Integración de todos los conceptos en arquitectura modular** |
