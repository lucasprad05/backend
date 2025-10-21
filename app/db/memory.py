from typing import Dict, List, Optional
from pwdlib import PasswordHash

# "BANCO DE DADOS" EM MEMÓRIA

# Dicionário principal de usuários, indexado pelo ID do usuário
DB_USERS: Dict[str, Dict] = {}          # Exemplo: { "1": { "id": "1", "name": "Admin", ... } }

# Índice auxiliar para buscar usuários rapidamente pelo e-mail
DB_EMAIL_INDEX: Dict[str, str] = {}     # Exemplo: { "admin@example.com": "1" }

# Dicionário que armazena avaliações (assessments) por usuário
DB_ASSESSMENTS: Dict[str, List[Dict]] = {}  # Exemplo: { "1": [ { "id": "...", "percent": 85, ... } ] }

# Instância do gerador de hashes de senha (usa Argon2 por padrão)
pwd_hasher = PasswordHash.recommended()


# FUNÇÕES DE CONSULTA E CRIAÇÃO
# Busca um usuário a partir do e-mail
# Retorna o dicionário do usuário ou None se não existir
def get_user_by_email(email: str) -> Optional[dict]:
    uid = DB_EMAIL_INDEX.get(email)
    if uid is None:
        return None
    return DB_USERS.get(uid)


# Busca um usuário a partir do ID
def get_user_by_id(user_id: str) -> Optional[dict]:
    return DB_USERS.get(user_id)


# Cria um novo registro de usuário em memória
# - Gera um novo ID incremental
# - Armazena o hash da senha (Argon2)
# - Define escopo padrão como "read"
def create_user_record(name: str, email: str, password: str) -> dict:
    if get_user_by_email(email):
        raise ValueError("E-mail já cadastrado")

    user_id = str(len(DB_USERS) + 1)
    DB_EMAIL_INDEX[email] = user_id
    DB_USERS[user_id] = {
        "id": user_id,
        "name": name,
        "email": email,
        "hashed_password": pwd_hasher.hash(password),
        "disabled": False,
        "scopes": ["read"],  # Permissão padrão mínima
    }
    return DB_USERS[user_id]


# Cria (ou mantém) um usuário administrador padrão
# Função chamada no startup da aplicação para garantir acesso administrativo inicial
def seed_admin():
    user_id = "1"
    email = "admin@example.com"

    # Evita recriar o admin se já existir
    if email in DB_EMAIL_INDEX:
        return

    hashed = pwd_hasher.hash("admin123")
    DB_USERS[user_id] = {
        "id": user_id,
        "email": email,
        "name": "Admin",
        "hashed_password": hashed,
        "disabled": False,
        "scopes": ["admin", "read", "write"],  # Permissões completas
    }
    DB_EMAIL_INDEX[email] = user_id
