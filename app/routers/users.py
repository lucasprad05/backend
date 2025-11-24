from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.models.user import UserBase
from app.core.security import get_current_active_user
from app.db.session import get_session
from app.db.models import UserModel
from passlib.hash import argon2

router = APIRouter(prefix="/users", tags=["users"])


# ME
@router.get("/me", response_model=UserBase)
def read_me(current_user: UserModel = Depends(get_current_active_user)):
    return UserBase.from_sql(current_user)


# UPDATE EMAIL
class EmailUpdate(BaseModel):
    email: EmailStr
    current_password: str


@router.put("/me/email", response_model=UserBase)
def update_email(payload: EmailUpdate,
                 current_user: UserModel = Depends(get_current_active_user),
                 session: Session = Depends(get_session)):

    if not argon2.verify(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    # verifica duplicidade
    exists = session.exec(
        select(UserModel).where(UserModel.email == payload.email)
    ).first()
    if exists and exists.id != current_user.id:
        raise HTTPException(status_code=400, detail="Email já está em uso")

    current_user.email = payload.email
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserBase.from_sql(current_user)


# UPDATE PASSWORD
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


@router.put("/me/password")
def update_password(payload: PasswordUpdate,
                    current_user: UserModel = Depends(get_current_active_user),
                    session: Session = Depends(get_session)):
    if not argon2.verify(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    current_user.hashed_password = argon2.hash(payload.new_password)
    session.add(current_user)
    session.commit()

    return {"ok": True}


# DELETE ACCOUNT
@router.delete("/me")
def delete_account(current_user: UserModel = Depends(get_current_active_user),
                   session: Session = Depends(get_session)):

    session.delete(current_user)
    session.commit()

    return {"ok": True}
