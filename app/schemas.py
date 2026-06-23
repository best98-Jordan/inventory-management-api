from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from .models import TipoMovimiento


# ─── Auth ────────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_minima(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginData(BaseModel):
    email: EmailStr
    password: str


# ─── Categorías ──────────────────────────────────────────────────────────────

class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]

    model_config = {"from_attributes": True}


# ─── Productos ───────────────────────────────────────────────────────────────

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo: Optional[str] = None
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    stock_actual: int = 0
    stock_minimo: int = 5
    unidad: str = "unidad"
    categoria_id: Optional[int] = None

    @field_validator("precio_compra", "precio_venta")
    @classmethod
    def precio_positivo(cls, v):
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock_minimo: Optional[int] = None
    unidad: Optional[str] = None
    categoria_id: Optional[int] = None


class ProductoOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    codigo: Optional[str]
    precio_compra: float
    precio_venta: float
    stock_actual: int
    stock_minimo: int
    unidad: str
    categoria: Optional[CategoriaOut]
    creado_en: datetime
    stock_bajo: bool = False  # calculado en el endpoint

    model_config = {"from_attributes": True}


# ─── Movimientos ─────────────────────────────────────────────────────────────

class MovimientoCreate(BaseModel):
    producto_id: int
    tipo: TipoMovimiento
    cantidad: int
    motivo: Optional[str] = None
    referencia: Optional[str] = None

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v):
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class MovimientoOut(BaseModel):
    id: int
    producto_id: int
    tipo: TipoMovimiento
    cantidad: int
    stock_anterior: int
    stock_posterior: int
    motivo: Optional[str]
    referencia: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}
