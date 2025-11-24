from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from passlib.hash import argon2

from app.core.config import SECRET_KEY, ALGORITHM
from app.db.session import get_session
from app.db.models import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# JWT - CREATE
def create_access_token(subject: str, scopes: list[str]):
    expires = datetime.utcnow() + timedelta(hours=8)
    payload = {
        "sub": subject,
        "scopes": scopes,
        "exp": expires,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# CONSULTA NO BANCO
def get_user_by_email(session: Session, email: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.email == email)
    return session.exec(stmt).first()


def get_user_by_id(session: Session, user_id: int) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.id == user_id)
    return session.exec(stmt).first()


# VERIFICAR SENHA
def verify_credentials(session: Session, email: str, password: str):
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not argon2.verify(password, user.hashed_password):
        return None
    return user


# GRANT SCOPES
def grant_scopes(user: UserModel, requested_scopes: list[str]):
    # requested_scopes pode ser vazio
    raw = user.scopes
    if "," in raw:
        user_scopes = raw.split(",")
    else:
        user_scopes = [raw]

    # retorna apenas os que o user tem
    return [s for s in requested_scopes if s in user_scopes] or user_scopes


# PEGAR USER DO TOKEN
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise Exception()
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = get_user_by_id(session, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


def get_current_active_user(user: UserModel = Depends(get_current_user)):
    if user.disabled:
        raise HTTPException(status_code=400, detail="Usuário desativado")
    return user
