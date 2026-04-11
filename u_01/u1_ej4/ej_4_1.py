from fastapi import FastAPI

app = FastAPI()

fake_items_db = [
    {"item_name": "Monitor"},
    {"item_name": "Teclado"},
    {"item_name": "Mouse"},
]


# http://127.0.0.1:8000/items/?skip=0&limit=10
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


## Parámetros opcionales
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# Múltiples parámetros de path y de query
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,  # viene del path y FastAPI lo convierte a int
    item_id: str,  # viene del path como texto
    q: str | None = None,  # query param opcional: ?q=...
    short: bool = False,  # query param bool opcional: ?short=true
):
    # 1) Armo la respuesta base
    item = {"item_id": item_id, "owner_id": user_id}
    # 2) Si enviaron q, lo agrego
    if q:
        item["q"] = q
    # 3) Si short es False, agrego una descripción larga
    if not short:
        item["description"] = "Descripción larga del ítem"
    # 4) Devuelvo el JSON final
    return item


# Parámetro de consulta requerido
@app.get("/items1/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item
