# API Integradora - Unidad 1

API REST de gestión de inventario (productos y categorías) construida con **FastAPI**. Proyecto educativo que integra progresivamente los conceptos de Path Parameters, Query Parameters, Body, Pydantic, Response Models y manejo de errores.

## Requisitos Previos

- Python 3.10+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd fastapi_backend-main

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Linux / macOS:
source .venv/bin/activate
# Windows (CMD):
.venv\Scripts\activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

### Proyecto Integrador (ejercicio principal)

```bash
cd u1_ej_8_integrador
python -m fastapi dev app/main.py
```

El servidor se levanta en `http://127.0.0.1:8000` con hot-reload habilitado.

### Ejercicios individuales

```bash
cd u_01/u1_ej4
python -m fastapi dev ej_4_1.py
```

## Documentación interactiva

Con el servidor corriendo, acceder a:

| Herramienta | URL |
|-------------|-----|
| Swagger UI  | http://127.0.0.1:8000/docs |
| ReDoc       | http://127.0.0.1:8000/redoc |
| OpenAPI JSON| http://127.0.0.1:8000/openapi.json |

## Estructura del Proyecto

```
fastapi_backend-main/
│
├── u1_ej_8_integrador/              # Proyecto integrador
│   ├── app/
│   │   ├── main.py                  # Factory de la app + registro de routers
│   │   └── modules/
│   │       ├── categoria/
│   │       │   ├── routers.py       # Endpoints /categorias
│   │       │   ├── schemas.py       # Modelos Pydantic
│   │       │   └── services.py      # Lógica de negocio + datos en memoria
│   │       └── producto/
│   │           ├── routers.py       # Endpoints /productos
│   │           ├── schemas.py       # Modelos Pydantic + ProductoStockResponse
│   │           └── services.py      # Lógica de negocio + alerta de stock
│   └── tests/
│       └── test_api.http            # 13 casos de prueba (VS Code REST Client)
│
├── u_01/                            # Ejercicios progresivos
│   ├── u1_ej1/                      # GET básico, respuestas JSON
│   ├── u1_ej2/                      # Path parameters
│   ├── u1_ej3/                      # Enum types en paths
│   ├── u1_ej4/                      # Query parameters (skip, limit)
│   ├── u1_ej5/                      # Request body con Pydantic
│   ├── u1_ej6/                      # Validación con Query() y Annotated
│   └── u1_ej7/                      # response_model, status codes, HTTPException
│
├── requirements.txt
├── Readme.md
├── arquitectura.md                  # Arquitectura detallada con diagramas y flujos
├── historiasDeUsuario.md            # 12 historias de usuario con criterios de aceptación
└── reglas.md                        # 28 reglas de negocio (explícitas e implícitas)
```

## Arquitectura

El proyecto integrador sigue una **arquitectura modular de tres capas**:

```
HTTP Request
    │
    ▼
┌──────────────────────────────────────────┐
│  ROUTERS  (routers.py)                   │
│  Endpoints, status codes, validación     │
│  de Path/Query params, manejo de 404     │
├─���────────────────────────────────────────┤
│  SCHEMAS  (schemas.py)                   │
│  Modelos Pydantic: Base → Create, Read,  │
│  Update. Validación automática (422)     │
├────────────────────────────────────���─────┤
│  SERVICES (services.py)                  │
│  Lógica de negocio, CRUD,               │
│  almacenamiento en listas en memoria     │
└─────��───────────────────────────���────────┘
```

- **Factory pattern**: `main.py` → `create_app()` registra los routers
- **Módulos independientes**: categoria y producto no tienen dependencias cruzadas
- **Flujo unidireccional**: Router → Service (nunca al revés)
- **Schemas compartidos** entre capas como contratos de datos

Para un análisis completo con diagramas de flujo de requests, grafo de dependencias y decisiones de diseño, ver [`arquitectura.md`](arquitectura.md).

## API Reference

### Categorías

| Método | Endpoint                         | Status | Descripción            |
|--------|----------------------------------|--------|------------------------|
| POST   | `/categorias/`                   | 201    | Crear categoría        |
| GET    | `/categorias/`                   | 200    | Listar con paginación  |
| GET    | `/categorias/{id}`               | 200    | Detalle por ID         |
| PUT    | `/categorias/{id}`               | 200    | Reemplazo total        |
| PUT    | `/categorias/{id}/desactivar`    | 200    | Borrado lógico         |

### Productos

| Método | Endpoint                         | Status | Descripción            |
|--------|----------------------------------|--------|------------------------|
| POST   | `/productos/`                    | 201    | Crear producto         |
| GET    | `/productos/`                    | 200    | Listar con paginación  |
| GET    | `/productos/{id}`                | 200    | Detalle por ID         |
| PUT    | `/productos/{id}`                | 200    | Reemplazo total        |
| PUT    | `/productos/{id}/desactivar`     | 200    | Borrado lógico         |
| GET    | `/productos/{id}/stock`          | 200    | Estado de stock        |

### Paginación

Los endpoints de listado aceptan query parameters:

| Parámetro | Tipo | Default | Restricción |
|-----------|------|---------|-------------|
| `skip`    | int  | 0       | >= 0        |
| `limit`   | int  | 10      | <= 50       |

```
GET /productos/?skip=0&limit=5
```

## Modelos de Datos

### Categoría

```json
{
  "id": 1,
  "codigo": "MUE-01",
  "descripcion": "Muebles de Oficina",
  "activo": true
}
```

| Campo       | Tipo   | Validación                         |
|-------------|--------|------------------------------------|
| codigo      | string | Regex: `^[A-Z]{3}-\d{2}$`         |
| descripcion | string | Mínimo 3 caracteres                |
| activo      | bool   | Opcional, default: `true`          |

### Producto

```json
{
  "id": 1,
  "nombre": "Silla Ergonómica",
  "categoria": "MUE-01",
  "precio": 250.00,
  "stock": 10,
  "stock_minimo": 5,
  "activo": true
}
```

| Campo        | Tipo   | Validación                         |
|--------------|--------|------------------------------------|
| nombre       | string | Requerido                          |
| categoria    | string | Regex: `^[A-Z]{3}-\d{2}$`         |
| precio       | float  | Mayor a 0                          |
| stock        | int    | Mayor o igual a 0                  |
| stock_minimo | int    | Mayor o igual a 0                  |
| activo       | bool   | Opcional, default: `true`          |

### Respuesta de Stock

```json
{
  "stock": 3,
  "bajo_stock_minimo": true,
  "activo": true
}
```

`bajo_stock_minimo` es `true` cuando `stock < stock_minimo`.

## Ejemplos de Uso

### Crear una categoría

```bash
curl -X POST http://127.0.0.1:8000/categorias/ \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "HER-03",
    "descripcion": "Herramientas Manuales",
    "activo": true
  }'
```

**Respuesta (201):**

```json
{
  "id": 3,
  "codigo": "HER-03",
  "descripcion": "Herramientas Manuales",
  "activo": true
}
```

### Crear un producto

```bash
curl -X POST http://127.0.0.1:8000/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Silla Ergonómica",
    "categoria": "MUE-01",
    "precio": 250.00,
    "stock": 10,
    "stock_minimo": 5,
    "activo": true
  }'
```

**Respuesta (201):**

```json
{
  "id": 1,
  "nombre": "Silla Ergonómica",
  "categoria": "MUE-01",
  "precio": 250.0,
  "stock": 10,
  "stock_minimo": 5,
  "activo": true
}
```

### Consultar alerta de stock

```bash
curl http://127.0.0.1:8000/productos/1/stock
```

**Respuesta (200):**

```json
{
  "stock": 10,
  "bajo_stock_minimo": false,
  "activo": true
}
```

### Desactivar un producto

```bash
curl -X PUT http://127.0.0.1:8000/productos/1/desactivar
```

**Respuesta (200):**

```json
{
  "id": 1,
  "nombre": "Silla Ergonómica",
  "categoria": "MUE-01",
  "precio": 250.0,
  "stock": 10,
  "stock_minimo": 5,
  "activo": false
}
```

## Manejo de Errores

### 404 — Recurso no encontrado

```json
{
  "detail": "Producto no encontrado"
}
```

### 422 — Error de validación

Ejemplo: crear un producto con categoría inválida y precio negativo.

```bash
curl -X POST http://127.0.0.1:8000/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Escritorio Roto",
    "categoria": "MUEBLES",
    "precio": -50.00,
    "stock": 5,
    "stock_minimo": 5,
    "activo": true
  }'
```

FastAPI responde automáticamente con los detalles de cada campo que falló la validación.

## Testing

Los tests están en formato `.http` (compatible con la extensión [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) de VS Code).

```
u1_ej_8_integrador/tests/test_api.http
```

Incluye 13 casos de prueba que cubren:

1. Listar categorías
2. Crear categoría
3. Detalle de categoría
4. Actualizar categoría (reemplazo total)
5. Desactivar categoría
6. Crear producto
7. Listar productos con paginación
8. Detalle de producto
9. Actualizar producto
10. Consultar alerta de stock
11. Desactivar producto
12. Producto inexistente (404)
13. Producto inválido (422)

Para ejecutarlos: abrir el archivo en VS Code con REST Client instalado y hacer click en "Send Request" sobre cada bloque.

## Datos Iniciales

Al iniciar el servidor, la API tiene precargadas dos categorías:

| ID | Código  | Descripción          | Activo |
|----|---------|----------------------|--------|
| 1  | MUE-01  | Muebles de Oficina   | true   |
| 2  | ELE-02  | Electrónica          | true   |

La lista de productos arranca vacía.

> **Nota:** Los datos se almacenan en memoria. Se pierden al reiniciar el servidor.

## Conceptos Cubiertos

Este proyecto integra los conceptos trabajados en los ejercicios progresivos (u_01):

| Ejercicio | Concepto                                              |
|-----------|-------------------------------------------------------|
| ej1       | Endpoints GET, respuestas JSON                        |
| ej2       | Path parameters                                       |
| ej3       | Enum types en path parameters                         |
| ej4       | Query parameters con defaults y validación            |
| ej5       | Request body con Pydantic BaseModel                   |
| ej6       | Validación avanzada con `Query()` y `Annotated`       |
| ej7       | `response_model`, herencia de schemas, status codes, `HTTPException` |
| **ej8**   | **Integración modular de todos los conceptos**        |

## Documentación del Proyecto

| Documento | Contenido |
|-----------|-----------|
| [`arquitectura.md`](arquitectura.md) | Arquitectura detallada: diagramas de capas, grafo de dependencias, flujo de requests, patrón de schemas, decisiones de diseño con trade-offs |
| [`historiasDeUsuario.md`](historiasDeUsuario.md) | 12 historias de usuario con criterios de aceptación, derivadas del código implementado |
| [`reglas.md`](reglas.md) | 28 reglas de negocio: validación, CRUD, lógica de stock, errores y reglas implícitas no enforceadas |

## Tecnologías

- **[FastAPI](https://fastapi.tiangolo.com/)** — Framework web async
- **[Pydantic](https://docs.pydantic.dev/)** — Validación de datos
- **[Uvicorn](https://www.uvicorn.org/)** — Servidor ASGI
- **[Starlette](https://www.starlette.io/)** — Framework base de FastAPI
