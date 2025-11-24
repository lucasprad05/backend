from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS

# NOVO: inicialização do banco SQLModel
from app.db.init_db import init_db, seed_admin

# Routers
from app.routers import auth, users, assessments


app = FastAPI(title="Auth FastAPI + OAuth2 + Argon2 + JWT")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rotas públicas
@app.get("/public/ping")
def ping():
    return {"pong": True}


# Rotas admin (só escopo admin)
@app.get("/admin/metrics")
def admin_metrics():
    return {"stats": "segredo-da-admin"}


# INCLUSÃO DOS ROUTERS
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assessments.router)


# INICIALIZAÇÃO DO BANCO (SQL)
@app.on_event("startup")
def on_startup():
    # cria tabelas
    init_db()

    # cria admin default, se não existir
    seed_admin()
