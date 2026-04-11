# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Educational FastAPI backend project (Spanish). Two main areas:
- **`u1_ej_8_integrador/`** — Main integrated project: modular REST API for products and categories
- **`u_01/`** — Progressive exercises (u1_ej1 through u1_ej7) teaching FastAPI concepts incrementally

Single dependency: `fastapi[standard]` (includes uvicorn, pydantic, starlette).

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Run integrated project (dev mode with auto-reload)
cd u1_ej_8_integrador
python -m fastapi dev app/main.py

# Run individual exercises
cd u_01/u1_ej4
python -m fastapi dev ej_4_1.py
```

No pytest, linter, or formatter is configured. Testing is done via `.http` files (VS Code REST Client) in `u1_ej_8_integrador/tests/test_api.http` (13 test cases).

## Architecture (Integrated Project)

**App factory pattern** in `u1_ej_8_integrador/app/main.py` — `create_app()` registers routers.

### Module Structure (`app/modules/{module}/`)

Each module (categoria, producto) follows a three-layer pattern:

| Layer | File | Responsibility |
|-------|------|----------------|
| **Routers** | `routers.py` | HTTP endpoints, status codes, path/query/body params, delegates to services |
| **Schemas** | `schemas.py` | Pydantic models: `Base` → `Create`, `Read`, `Update` inheritance pattern |
| **Services** | `services.py` | Business logic, in-memory list storage (no real DB) |

Layers communicate top-down only: Router → Service. Schemas are shared between both as data contracts. No cross-module dependencies (categoria and producto are fully independent).

### Schema Pattern

- `Base` — shared fields with validation (regex, min/max, numeric ranges)
- `Create` — all fields required (used for POST and PUT — full replacement)
- `Read` — extends Base with auto-generated `id`
- `Update` — all fields optional (defined but **not used** in any endpoint yet, intended for future PATCH)
- `ProductoStockResponse` — specialized 3-field response (stock, bajo_stock_minimo, activo)

### Validation Rules

- **codigo / categoria**: regex `^[A-Z]{3}-\d{2}$` (e.g., `"MUE-01"`)
- **descripcion**: `min_length=3`
- **precio**: `gt=0`
- **stock / stock_minimo**: `ge=0`
- **Path id**: `gt=0`
- **Query skip**: `ge=0` (default 0) — **Query limit**: `le=50` (default 10)

No FK validation — producto.categoria is validated by format only, not checked against existing categorías.

### API Endpoints

Both modules follow the same REST pattern:
- `POST /` (201) — Create
- `GET /` (200) — List with `skip`/`limit` pagination
- `GET /{id}` (200) — Detail
- `PUT /{id}` (200) — Full update (requires all fields, uses Create schema)
- `PUT /{id}/desactivar` (200) — Soft delete (sets `activo=false`, no request body)

Producto adds: `GET /{id}/stock` — returns stock alert (`bajo_stock_minimo = stock < stock_minimo`).

### Seed Data

Categorías starts with 2 records (id_counter=3): `MUE-01` "Muebles de Oficina", `ELE-02` "Electrónica". Productos starts empty (id_counter=1). All data is volatile — lost on server restart.

## Language

All code, variable names, comments, and documentation are in **Spanish**.

## Related Documentation

- `arquitectura.md` — Detailed architecture description with diagrams and request flows
- `historiasDeUsuario.md` — 12 user stories with acceptance criteria derived from implemented code
- `reglas.md` — 28 business rules: validation, CRUD, stock logic, errors, and implicit non-enforced rules
- `Readme.md` — Full setup guide, API reference, examples, and data models
