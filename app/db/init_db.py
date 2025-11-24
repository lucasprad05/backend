from sqlmodel import SQLModel, Session, select
from app.db.session import engine
from app.db.models import UserModel
from app.db.session import get_session
from app.db.session import engine
from passlib.hash import argon2


def init_db():
    """Cria as tabelas no SQLite se não existirem."""
    SQLModel.metadata.create_all(engine)


def seed_admin():
    """Cria um admin inicial se não existir."""
    with Session(engine) as session:
        stmt = select(UserModel).where(UserModel.email == "admin@example.com")
        existing = session.exec(stmt).first()

        if existing:
            return

        admin = UserModel(
            name="Admin",
            email="admin@example.com",
            hashed_password=argon2.hash("admin123"),
            disabled=False,
            scopes="admin"
        )

        session.add(admin)
        session.commit()
