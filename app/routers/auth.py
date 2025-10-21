from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import UserBase, UserCreate, Token
from app.db.memory import create_user_record
from app.core.security import verify_credentials, create_access_token, grant_scopes

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserBase)
def register(user_in: UserCreate):
    try:
        user = create_user_record(user_in.name, user_in.email, user_in.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserBase(**{k: user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

@router.post("/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = verify_credentials(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    granted_scopes = grant_scopes(user, getattr(form_data, "scopes", []))
    access_token = create_access_token(subject=user["id"], scopes=granted_scopes)
    return {"access_token": access_token, "token_type": "bearer"}
