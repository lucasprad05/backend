from pydantic import BaseModel, EmailStr
from typing import Optional, List


# BASE PARA LEITURA
class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    disabled: bool = False
    scopes: List[str] = []

    # transforma a lista vinda do SQLModel (CSV ou JSON) em list[str]
    @classmethod
    def from_sql(cls, user):
        raw = user.scopes
        if isinstance(raw, list):
            scopes = raw
        elif "," in raw:
            scopes = raw.split(",")
        else:
            scopes = [raw] if raw else []
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            disabled=user.disabled,
            scopes=scopes
        )


# CRIAÇÃO DE USUÁRIO (POST /register)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# TOKEN JWT
class Token(BaseModel):
    access_token: str
    token_type: str
