from datetime import datetime, timedelta
from typing import Dict, Optional, Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, Security, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash

# =========================
# CONFIG JWT / SENHA
# =========================
# ATENÇÃO: troque essa chave em produção (use variável de ambiente)
SECRET_KEY = "troque-esta-chave-por-uma-bem-grande-e-secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_hasher = PasswordHash.recommended()  # Argon2 por padrão

# =========================
# "BANCO" SIMULADO (dicionário)
# =========================
DB_USERS: Dict[str, Dict] = {}       # user_id -> user
DB_EMAIL_INDEX: Dict[str, str] = {}  # email -> user_id

def seed_admin():
    user_id = "1"
    email = "admin@example.com"
    if email in DB_EMAIL_INDEX:
        return
    hashed = pwd_hasher.hash("admin123")  # senha: admin123
    DB_USERS[user_id] = {
        "id": user_id,
        "email": email,
        "name": "Admin",
        "hashed_password": hashed,
        "disabled": False,
        "scopes": ["admin", "read", "write"],
    }
    DB_EMAIL_INDEX[email] = user_id

seed_admin()

# =========================
# MODELOS (Schemas)
# =========================
class UserBase(BaseModel):
    id: str
    name: str
    email: EmailStr
    disabled: bool = False
    scopes: List[str] = []

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# =========================
# AUXILIARES DE "BD"
# =========================
def get_user_by_email(email: str) -> Optional[dict]:
    uid = DB_EMAIL_INDEX.get(email)
    if uid is None:
        return None
    return DB_USERS.get(uid)

def get_user_by_id(user_id: str) -> Optional[dict]:
    return DB_USERS.get(user_id)

def create_user(u: UserCreate) -> dict:
    if get_user_by_email(u.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user_id = str(len(DB_USERS) + 1)
    DB_EMAIL_INDEX[u.email] = user_id
    DB_USERS[user_id] = {
        "id": user_id,
        "name": u.name,
        "email": u.email,
        "hashed_password": pwd_hasher.hash(u.password),
        "disabled": False,
        "scopes": ["read"],  # escopo padrão
    }
    return DB_USERS[user_id]

# =========================
# JWT helpers
# =========================
def create_access_token(subject: str, scopes: Optional[List[str]] = None, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": subject, "scopes": scopes or []}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# OAUTH2 + ESCOPOS
# =========================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={
        "read": "Permite leituras",
        "write": "Permite escritas",
        "admin": "Permissões administrativas",
    },
)

async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")

    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_scopes: List[str] = payload.get("scopes", [])
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido", headers={"WWW-Authenticate": authenticate_value})
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido/expirado", headers={"WWW-Authenticate": authenticate_value})

    user = get_user_by_id(user_id)
    if not user or user.get("disabled"):
        raise HTTPException(status_code=401, detail="Usuário inativo/inexistente", headers={"WWW-Authenticate": authenticate_value})

    # Checa escopos exigidos
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=403, detail="Permissão insuficiente", headers={"WWW-Authenticate": authenticate_value})
    return user

async def get_current_active_user(current_user: Annotated[dict, Security(get_current_user, scopes=[])]):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Usuário desativado")
    return current_user

# =========================
# APP + CORS
# =========================
app = FastAPI(title="Auth FastAPI + OAuth2 + Argon2 + JWT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROTAS
# =========================
@app.get("/public/ping")
def public_ping():
    return {"pong": True}

@app.post("/auth/register", response_model=UserBase)
def register(user_in: UserCreate):
    user = create_user(user_in)
    return UserBase(**{k: user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

@app.post("/auth/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # username = email (padrão do OAuth2PasswordRequestForm)
    user = get_user_by_email(form_data.username)
    if not user or not pwd_hasher.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Escopos solicitados pelo cliente via "scope"
    requested_scopes = list(set(form_data.scopes)) if hasattr(form_data, "scopes") else []
    # Conceda apenas escopos que o usuário possui
    granted_scopes = [s for s in requested_scopes if s in user["scopes"]]
    if not granted_scopes:
        granted_scopes = ["read"]

    access_token = create_access_token(subject=user["id"], scopes=granted_scopes)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserBase)
def read_me(current_user: Annotated[dict, Depends(get_current_active_user)]):
    return UserBase(**{k: current_user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

@app.post("/posts")
def create_post(current_user: Annotated[dict, Security(get_current_user, scopes=["write"])]):
    return {"ok": True, "by": current_user["email"]}

@app.get("/admin/metrics")
def admin_metrics(current_user: Annotated[dict, Security(get_current_user, scopes=["admin"])]):
    return {"stats": "segredo-da-admin"}
