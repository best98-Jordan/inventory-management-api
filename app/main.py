from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from . import models
from sqlalchemy.orm import Session

from .database import engine, get_db, Base
from . import schemas
from .auth import hash_password, verify_password, create_access_token, get_current_user

# Crear todas las tablas al iniciar (en producción usa Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Inventario",
    description="""
## Sistema de gestión de inventario para pequeños negocios

Controla tu stock, registra entradas y salidas, y recibe alertas
cuando un producto esté bajo el mínimo establecido.

### Funcionalidades
- **Autenticación** con JWT (registro e inicio de sesión)
- **Productos** — CRUD completo con categorías
- **Movimientos** — historial de entradas y salidas de stock
- **Reportes** — stock bajo, movimientos por fecha/producto
    """,
    version="1.0.0",
    contact={
        "name": "Tu Nombre",
        "email": "tu@email.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Importar routers ─────────────────────────────────────────────────────────
from .routers import productos, movimientos, reportes

app.include_router(productos.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)


# ─── Auth endpoints ───────────────────────────────────────────────────────────

@app.post(
    "/auth/register",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
    summary="Registrar nuevo usuario"
)
def register(data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese email"
        )
    user = models.Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post(
    "/auth/login",
    response_model=schemas.Token,
    tags=["Auth"],
    summary="Iniciar sesión y obtener token JWT"
)
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get(
    "/auth/me",
    response_model=schemas.UsuarioOut,
    tags=["Auth"],
    summary="Ver perfil del usuario autenticado"
)
def me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user


# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["General"], summary="Health check")
def root():
    return {
        "status": "ok",
        "app": "API de Inventario",
        "version": "1.0.0",
        "docs": "/docs"
    }
