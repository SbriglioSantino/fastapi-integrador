from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


# Datos de entrada
item = Item(name="Cafetera", price=120.0)
item_id = 505

# Acceder a todos los atributos del objeto modelo directamente
# item_dict = item.model_dump()
# print(item_dict)

# Fusión de datos mediante desempaquetado (unpacking)
resultado = {"item_id": item_id, **item.model_dump()}

# Impresión en consola
print(resultado)
