from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, EmailStr
from app.models.user import UserBase
from app.core.security import get_current_active_user
from app.db.memory import DB_USERS, DB_EMAIL_INDEX, get_user_by_email, pwd_hasher

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserBase)
def read_me(current_user: Annotated[dict, Depends(get_current_active_user)]):
    return UserBase(**{k: current_user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

class EmailUpdate(BaseModel):
    email: EmailStr
    current_password: str

@router.put("/me/email", response_model=UserBase)
def update_email(payload: EmailUpdate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    if not pwd_hasher.verify(payload.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    existing = get_user_by_email(payload.email)
    if existing and existing["id"] != current_user["id"]:
        raise HTTPException(status_code=400, detail="E-mail já em uso")
    old_email = current_user["email"]
    if old_email != payload.email:
        if old_email in DB_EMAIL_INDEX:
            del DB_EMAIL_INDEX[old_email]
        DB_EMAIL_INDEX[payload.email] = current_user["id"]
        current_user["email"] = payload.email
        DB_USERS[current_user["id"]] = current_user
    return UserBase(**{k: current_user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@router.put("/me/password")
def update_password(payload: PasswordUpdate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    if not pwd_hasher.verify(payload.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    current_user["hashed_password"] = pwd_hasher.hash(payload.new_password)
    DB_USERS[current_user["id"]] = current_user
    return {"ok": True}
