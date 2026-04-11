from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


# ---------------------------------------------------------
# CASO 0: Sin tipo ni response_model (A ciegas)
# ---------------------------------------------------------
@app.get("/caso-0/sin-reglas")
async def read_sin_tipo():
    """
    Aquí NO declaramos qué vamos a devolver.
    FastAPI no sabe qué esperar.
    """
    return {
        "name": "Objeto Peligroso",
        "price": 99.99,
        # CUIDADO: Estamos devolviendo datos que no existen en el modelo Item
        "password_admin": "admin123",
        "info_interna": "IP: 192.168.1.55",
    }


# ---------------------------------------------------------
# CASO 1: El camino feliz (Type Hint estándar)
# ---------------------------------------------------------
@app.get("/caso-1/exito")
async def read_item_success() -> Item:
    """
    Devuelve un objeto Item válido.
    FastAPI genera la documentación y valida que todo esté bien.
    """
    return Item(name="Portal Gun", price=42.0)


# ---------------------------------------------------------
# CASO 2: La red de seguridad (Type Hint detectando error)
# ---------------------------------------------------------
@app.get("/caso-2/error-servidor")
async def read_item_fail() -> Item:
    """
    Simulamos un BUG en tu código.
    El tipo de retorno dice que devolveremos un 'Item',
    pero estamos devolviendo un diccionario al que le falta el 'price'.

    FastAPI detendrá esto y lanzará un Error 500 Interno
    para no enviar datos rotos al cliente.
    """
    # Falta el campo 'price' que es obligatorio en Item
    return {"name": "Plumbus defectuoso"}  # type: ignore


# ---------------------------------------------------------
# CASO 3: El filtro mágico (response_model)
# ---------------------------------------------------------
@app.get("/caso-3/filtrado", response_model=Item)
async def read_item_filter() -> Any:
    """
    Aquí devolvemos un diccionario sucio o con datos sensibles
    (como una contraseña o campos internos de la BD).

    Gracias a 'response_model=Item', FastAPI:
    1. Convertirá el dict a un objeto Item.
    2. LIMPIARÁ (filtrará) los campos extra ('password_db').
    """
    datos_de_base_de_datos = {
        "name": "Caja Misteriosa",
        "price": 100.0,
        "description": "Contiene secretos",
        "password_db": "SECRET_123",  # ¡Esto NO debe llegar al cliente!
        "created_at": "2023-01-01",  # Esto tampoco está en el modelo
    }

    return datos_de_base_de_datos
