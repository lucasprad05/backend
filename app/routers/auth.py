from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from passlib.hash import argon2

from app.models.user import UserBase, UserCreate, Token
from app.db.session import get_session
from app.db.models import UserModel
from app.core.security import verify_credentials, create_access_token, grant_scopes

router = APIRouter(prefix="/auth", tags=["auth"])


# REGISTRO
@router.post("/register", response_model=UserBase)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    # verifica duplicidade
    stmt = select(UserModel).where(UserModel.email == user_in.email)
    existing = session.exec(stmt).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = UserModel(
        name=user_in.name,
        email=user_in.email,
        hashed_password=argon2.hash(user_in.password),
        disabled=False,
        scopes="user",
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserBase.from_sql(user)


# LOGIN
@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = verify_credentials(session, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    granted = grant_scopes(user, form.scopes)
    token = create_access_token(subject=str(user.id), scopes=granted)

    return {"access_token": token, "token_type": "bearer"}
