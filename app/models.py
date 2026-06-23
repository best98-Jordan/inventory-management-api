from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class TipoMovimiento(str, enum.Enum):
    entrada = "entrada"
    salida = "salida"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    productos = relationship("Producto", back_populates="creado_por")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, index=True)
    descripcion = Column(String(500), nullable=True)
    codigo = Column(String(50), unique=True, index=True, nullable=True)
    precio_compra = Column(Float, nullable=False, default=0.0)
    precio_venta = Column(Float, nullable=False, default=0.0)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    unidad = Column(String(30), nullable=False, default="unidad")
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    categoria = relationship("Categoria", back_populates="productos")
    creado_por = relationship("Usuario", back_populates="productos")
    movimientos = relationship("Movimiento", back_populates="producto")


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_posterior = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    referencia = Column(String(100), nullable=True)  # ej: # de factura
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    producto = relationship("Producto", back_populates="movimientos")
    registrado_por = relationship("Usuario")
