from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

# MODELO DE USUÁRIO
class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    disabled: bool = Field(default=False)
    scopes: str

    assessments: List["AssessmentModel"] = Relationship(back_populates="user")

# MODELO DE AVALIAÇÃO
class AssessmentModel(SQLModel, table=True):
    __tablename__ = "assessments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    percent: float
    level: str
    recommendations: str

    # guardamos dims (dimensões calculadas) como JSON string
    dims: str

    user: Optional[UserModel] = Relationship(back_populates="assessments")
