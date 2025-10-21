from typing import List
from pydantic import BaseModel, EmailStr

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
