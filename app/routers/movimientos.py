from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post("", response_model=schemas.MovimientoOut, status_code=201, summary="Registrar movimiento de stock")
def registrar_movimiento(
    data: schemas.MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id == data.producto_id,
        models.Producto.usuario_id == current_user.id
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    stock_anterior = producto.stock_actual

    if data.tipo == models.TipoMovimiento.salida:
        if producto.stock_actual < data.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {producto.stock_actual}, solicitado: {data.cantidad}"
            )
        stock_nuevo = producto.stock_actual - data.cantidad
    else:
        stock_nuevo = producto.stock_actual + data.cantidad

    producto.stock_actual = stock_nuevo

    movimiento = models.Movimiento(
        producto_id=data.producto_id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=stock_nuevo,
        motivo=data.motivo,
        referencia=data.referencia,
        usuario_id=current_user.id
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.get("", response_model=List[schemas.MovimientoOut], summary="Listar movimientos")
def listar_movimientos(
    producto_id: Optional[int] = Query(None),
    tipo: Optional[models.TipoMovimiento] = Query(None),
    desde: Optional[datetime] = Query(None, description="Fecha inicio (ISO 8601)"),
    hasta: Optional[datetime] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Movimiento).filter(
        models.Movimiento.usuario_id == current_user.id
    )
    if producto_id:
        query = query.filter(models.Movimiento.producto_id == producto_id)
    if tipo:
        query = query.filter(models.Movimiento.tipo == tipo)
    if desde:
        query = query.filter(models.Movimiento.creado_en >= desde)
    if hasta:
        query = query.filter(models.Movimiento.creado_en <= hasta)

    return query.order_by(models.Movimiento.creado_en.desc()).limit(limite).all()
