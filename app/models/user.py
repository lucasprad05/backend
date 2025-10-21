from typing import List
from pydantic import BaseModel, EmailStr

# Modelo base de usuário usado em respostas e consultas internas.
# Contém as informações essenciais de identificação e permissão.
class UserBase(BaseModel):
    id: str
    name: str
    email: EmailStr
    disabled: bool = False
    scopes: List[str] = []

# Modelo usado na criação de novos usuários.
# Inclui senha em texto simples, que será posteriormente hasheada.
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Modelo usado para representar o token JWT retornado após login.
# Indica o tipo do token (geralmente "bearer") e o valor codificado.
class Token(BaseModel):
    access_token: str
    token_type: str
