from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/stock-bajo", summary="Productos bajo el stock mínimo")
def stock_bajo(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    productos = db.query(models.Producto).filter(
        models.Producto.usuario_id == current_user.id,
        models.Producto.stock_actual <= models.Producto.stock_minimo
    ).all()

    return {
        "total": len(productos),
        "productos": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "codigo": p.codigo,
                "stock_actual": p.stock_actual,
                "stock_minimo": p.stock_minimo,
                "faltante": max(0, p.stock_minimo - p.stock_actual),
                "categoria": p.categoria.nombre if p.categoria else None
            }
            for p in productos
        ]
    }


@router.get("/resumen", summary="Resumen general del inventario")
def resumen(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    total_productos = db.query(func.count(models.Producto.id)).filter(
        models.Producto.usuario_id == current_user.id
    ).scalar()

    productos_bajo_min = db.query(func.count(models.Producto.id)).filter(
        models.Producto.usuario_id == current_user.id,
        models.Producto.stock_actual <= models.Producto.stock_minimo
    ).scalar()

    valor_inventario = db.query(
        func.sum(models.Producto.stock_actual * models.Producto.precio_compra)
    ).filter(models.Producto.usuario_id == current_user.id).scalar() or 0

    total_movimientos = db.query(func.count(models.Movimiento.id)).filter(
        models.Movimiento.usuario_id == current_user.id
    ).scalar()

    return {
        "total_productos": total_productos,
        "productos_bajo_minimo": productos_bajo_min,
        "valor_inventario_usd": round(valor_inventario, 2),
        "total_movimientos": total_movimientos,
    }
