from datetime import datetime, timedelta
from typing import List, Optional, Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.memory import get_user_by_email, get_user_by_id, pwd_hasher

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={
        "read": "Permite leituras",
        "write": "Permite escritas",
        "admin": "Permissões administrativas",
    },
)

def create_access_token(subject: str, scopes: Optional[List[str]] = None, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": subject, "scopes": scopes or []}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=403, detail="Permissão insuficiente", headers={"WWW-Authenticate": authenticate_value})
    return user

async def get_current_active_user(current_user: Annotated[dict, Security(get_current_user, scopes=[])]):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Usuário desativado")
    return current_user

def verify_credentials(email: str, password: str):
    user = get_user_by_email(email)
    if not user or not pwd_hasher.verify(password, user["hashed_password"]):
        return None
    return user

def grant_scopes(user: dict, requested_scopes: Optional[List[str]]):
    req = list(set(requested_scopes or []))
    granted = [s for s in req if s in user["scopes"]]
    return granted or ["read"]
