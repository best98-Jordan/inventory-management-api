# 📦 Inventory Management API

A production-ready REST API built with **FastAPI** and **SQLite** that helps small businesses track stock levels, record inventory movements, and receive low-stock alerts — replacing manual spreadsheets with a clean, documented API.

> **Live Demo:** [https://inventory-management-api-qf0r.onrender.com/]

---

## ✨ Features

- 🔐 **JWT Authentication** — secure register/login with bcrypt password hashing
- 📦 **Product Management** — full CRUD with categories, pricing, and minimum stock thresholds
- 🔄 **Stock Movements** — log every entry and exit with automatic stock updates
- 🚨 **Low Stock Alerts** — instantly query which products are below their minimum
- 📊 **Inventory Reports** — total value, movement history, and summary dashboard
- 📄 **Auto-generated Docs** — interactive Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Database | SQLite (via SQLAlchemy ORM) |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Deploy | Render.com |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/best98-Jordan/inventory-management-api
cd inventario-api

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# 5. Run the server
uvicorn app.main:app --reload


## 📡 API Endpoints

### Auth
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/auth/register` | Create new account | No |
| POST | `/auth/login` | Login and receive JWT token | No |
| GET | `/auth/me` | Get current user profile | ✅ Yes |

### Products
| Method | Endpoint | Description |
|---|---|---|
| GET | `/productos` | List all products (filter by category, name, low stock) |
| GET | `/productos/{id}` | Get a single product |
| POST | `/productos` | Create a new product |
| PUT | `/productos/{id}` | Update product data |
| DELETE | `/productos/{id}` | Delete a product |

### Stock Movements
| Method | Endpoint | Description |
|---|---|---|
| POST | `/movimientos` | Register a stock entry or exit |
| GET | `/movimientos` | List movements (filter by product, type, date range) |

### Reports
| Method | Endpoint | Description |
|---|---|---|
| GET | `/reportes/stock-bajo` | Products below minimum stock level |
| GET | `/reportes/resumen` | Inventory summary (total value, product count) |

---

## 🔐 Authentication Flow

```
1. POST /auth/register  →  create account
2. POST /auth/login     →  receive { access_token, token_type }
3. Add header to all requests:
   Authorization: Bearer <access_token>
```

---

## 📋 Example Usage

### Register and login
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nombre": "John", "email": "john@example.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'
```

### Create a product
```bash
curl -X POST http://localhost:8000/productos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell XPS",
    "precio_compra": 800.00,
    "precio_venta": 1100.00,
    "stock_actual": 5,
    "stock_minimo": 2
  }'
```

### Register a stock exit
```bash
curl -X POST http://localhost:8000/movimientos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "tipo": "salida",
    "cantidad": 2,
    "motivo": "Sale to customer",
    "referencia": "INV-0042"
  }'
```

### Check low stock
```bash
curl http://localhost:8000/reportes/stock-bajo \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📁 Project Structure

```
inventario-api/
├── app/
│   ├── main.py          # FastAPI app, CORS, auth endpoints
│   ├── database.py      # SQLite connection and session management
│   ├── models.py        # SQLAlchemy ORM models (4 tables)
│   ├── schemas.py       # Pydantic request/response validation
│   ├── auth.py          # JWT creation and verification
│   └── routers/
│       ├── productos.py     # Product CRUD endpoints
│       ├── movimientos.py   # Stock movement endpoints
│       └── reportes.py      # Reporting endpoints
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key (use a strong random string) | insecure default |
| `DATABASE_URL` | Database connection URL | `sqlite:///./inventario.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | `1440` (24 hours) |

Generate a secure key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```


## 🤝 Use Cases

This API is designed for small businesses that need to:
- Replace Excel spreadsheets with a real inventory system
- Track stock across multiple product categories
- Get alerts before running out of stock
- Audit every stock movement with a full history log

---

## 👨‍💻 Author

**Jordan** — Python & FastAPI Developer  
📧 jordanquibest98@email.com  
🔗 [github.com/best98-Jordan](https://github.com/best98-Jordan)  
💼 Available for freelance projects on Workana and Freelancer

---

## 📄 License

MIT License — free to use and modify.
