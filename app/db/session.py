from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path

# Caminho do banco SQLite (arquivo local)
DB_PATH = Path(__file__).parent.parent / "database.sqlite3"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,  # coloque True se quiser ver logs SQL
    connect_args={"check_same_thread": False}  # necessário para SQLite + FastAPI
)

# Cria uma sessão por requisição
def get_session():
    with Session(engine) as session:
        yield session
