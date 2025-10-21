from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.db.memory import seed_admin
from app.routers import auth, users, assessments

app = FastAPI(title="Auth FastAPI + OAuth2 + Argon2 + JWT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/public/ping")
def public_ping():
    return {"pong": True}

# Routers (mantém caminhos originais /auth, /users, etc.)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assessments.router)

# Endpoint admin original segue intocado (exemplo)
@app.get("/admin/metrics")
def admin_metrics():
    return {"stats": "segredo-da-admin"}

# Seed
seed_admin()
