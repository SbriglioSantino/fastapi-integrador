from typing import List, Optional
from .schemas import ProveedorCreate, ProveedorRead

db_proveedores: List[ProveedorRead] = [
    ProveedorRead(id=1, nombre="Distribuidora Norte", email="contacto@norte.com", telefono="2614556789", activo=True),
    ProveedorRead(id=2, nombre="Suministros Sur", email="info@sur.com", telefono="2614112233", activo=True),
]
id_counter = 3


def crear(data: ProveedorCreate) -> ProveedorRead:
    global id_counter
    nuevo = ProveedorRead(id=id_counter, **data.model_dump())
    db_proveedores.append(nuevo)
    id_counter += 1
    return nuevo


def obtener_todos(skip: int = 0, limit: int = 10, nombre: Optional[str] = None) -> List[ProveedorRead]:
    resultado = db_proveedores
    if nombre:
        resultado = [p for p in resultado if nombre.lower() in p.nombre.lower()]
    return resultado[skip: skip + limit]


def obtener_por_id(id: int) -> Optional[ProveedorRead]:
    for p in db_proveedores:
        if p.id == id:
            return p
    return None


def actualizar_total(id: int, data: ProveedorCreate) -> Optional[ProveedorRead]:
    for index, p in enumerate(db_proveedores):
        if p.id == id:
            actualizado = ProveedorRead(id=id, **data.model_dump())
            db_proveedores[index] = actualizado
            return actualizado
    return None


def desactivar(id: int) -> Optional[ProveedorRead]:
    for index, p in enumerate(db_proveedores):
        if p.id == id:
            p_dict = p.model_dump()
            p_dict["activo"] = False
            actualizado = ProveedorRead(**p_dict)
            db_proveedores[index] = actualizado
            return actualizado
    return None