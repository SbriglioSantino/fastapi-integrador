from pydantic import BaseModel, Field
from typing import Optional


class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=3, example="Distribuidora Norte")
    email: str = Field(..., example="contacto@norte.com")
    telefono: str = Field(..., min_length=8, example="2614556789")
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3)
    email: Optional[str] = None
    telefono: Optional[str] = Field(None, min_length=8)
    activo: Optional[bool] = None


class ProveedorRead(ProveedorBase):
    id: int