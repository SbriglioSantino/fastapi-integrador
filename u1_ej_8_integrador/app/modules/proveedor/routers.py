from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List, Optional
from . import schemas, services

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/", response_model=schemas.ProveedorRead, status_code=status.HTTP_201_CREATED
)
def alta_proveedor(proveedor: schemas.ProveedorCreate):
    return services.crear(proveedor)


@router.get(
    "/", response_model=List[schemas.ProveedorRead], status_code=status.HTTP_200_OK
)
def listar_proveedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
    nombre: Optional[str] = Query(None)
):
    return services.obtener_todos(skip, limit, nombre)


@router.get(
    "/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK
)
def detalle_proveedor(id: int = Path(..., gt=0)):
    proveedor = services.obtener_por_id(id)
    if not proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
        )
    return proveedor


@router.put(
    "/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK
)
def actualizar_proveedor(proveedor: schemas.ProveedorCreate, id: int = Path(..., gt=0)):
    actualizado = services.actualizar_total(id, proveedor)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
        )
    return actualizado


@router.put(
    "/{id}/desactivar",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK,
)
def borrado_logico(id: int = Path(..., gt=0)):
    desactivado = services.desactivar(id)
    if not desactivado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
        )
    return desactivado