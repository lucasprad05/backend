from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, EmailStr
from app.models.user import UserBase
from app.core.security import get_current_active_user
from app.db.memory import DB_USERS, DB_EMAIL_INDEX, delete_user_record, get_user_by_email, pwd_hasher

# Router com operações relacionadas ao usuário autenticado (/users).
router = APIRouter(prefix="/users", tags=["users"])

# Retorna os dados públicos do usuário logado.
# Usa a dependência get_current_active_user para garantir autenticação e status ativo.
@router.get("/me", response_model=UserBase)
def read_me(current_user: Annotated[dict, Depends(get_current_active_user)]):
    return UserBase(**{k: current_user[k] for k in ["id", "name", "email", "disabled", "scopes"]})

# Modelo para atualização de e-mail, exigindo confirmação da senha atual.
class EmailUpdate(BaseModel):
    email: EmailStr
    current_password: str

# Atualiza o e-mail do usuário autenticado.
# - Verifica a senha atual
# - Verifica conflito de e-mail já cadastrado
# - Atualiza o índice de e-mails e o registro em DB_USERS
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

# Modelo para atualização de senha, exigindo a senha atual e a nova senha.
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# Atualiza a senha do usuário autenticado.
# - Verifica a senha atual
# - Gera novo hash e persiste no "banco" em memória
@router.put("/me/password")
def update_password(payload: PasswordUpdate, current_user: Annotated[dict, Depends(get_current_active_user)]):
    if not pwd_hasher.verify(payload.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    current_user["hashed_password"] = pwd_hasher.hash(payload.new_password)
    DB_USERS[current_user["id"]] = current_user

    return {"ok": True}

# Deleta a conta do usuário autenticado.
# - Remove do DB_USERS e DB_EMAIL_INDEX
@router.delete("/me")
def delete_account(current_user: Annotated[dict, Depends(get_current_active_user)]):
    user_id = current_user["id"]
    if not delete_user_record(user_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {"ok": True}
