from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=List[schemas.ProductoOut], summary="Listar todos los productos")
def listar_productos(
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    stock_bajo: Optional[bool] = Query(None, description="Solo productos bajo el mínimo"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Producto).filter(models.Producto.usuario_id == current_user.id)

    if categoria_id:
        query = query.filter(models.Producto.categoria_id == categoria_id)
    if buscar:
        query = query.filter(
            models.Producto.nombre.ilike(f"%{buscar}%") |
            models.Producto.codigo.ilike(f"%{buscar}%")
        )

    productos = query.all()

    result = []
    for p in productos:
        p_dict = schemas.ProductoOut.model_validate(p)
        p_dict.stock_bajo = p.stock_actual <= p.stock_minimo
        if stock_bajo is not None:
            if stock_bajo and not p_dict.stock_bajo:
                continue
            if not stock_bajo and p_dict.stock_bajo:
                continue
        result.append(p_dict)

    return result


@router.get("/{producto_id}", response_model=schemas.ProductoOut, summary="Ver un producto")
def ver_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id,
        models.Producto.usuario_id == current_user.id
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    result = schemas.ProductoOut.model_validate(producto)
    result.stock_bajo = producto.stock_actual <= producto.stock_minimo
    return result


@router.post("", response_model=schemas.ProductoOut, status_code=201, summary="Crear producto")
def crear_producto(
    data: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    if data.codigo:
        existing = db.query(models.Producto).filter(models.Producto.codigo == data.codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")

    producto = models.Producto(**data.model_dump(), usuario_id=current_user.id)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    result = schemas.ProductoOut.model_validate(producto)
    result.stock_bajo = producto.stock_actual <= producto.stock_minimo
    return result


@router.put("/{producto_id}", response_model=schemas.ProductoOut, summary="Actualizar producto")
def actualizar_producto(
    producto_id: int,
    data: schemas.ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id,
        models.Producto.usuario_id == current_user.id
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(producto, field, value)

    db.commit()
    db.refresh(producto)
    result = schemas.ProductoOut.model_validate(producto)
    result.stock_bajo = producto.stock_actual <= producto.stock_minimo
    return result


@router.delete("/{producto_id}", status_code=204, summary="Eliminar producto")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id,
        models.Producto.usuario_id == current_user.id
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
