from typing import Dict, List, Optional
from pwdlib import PasswordHash

# ======= "BANCO" SIMULADO =======
DB_USERS: Dict[str, Dict] = {}         # user_id -> user dict
DB_EMAIL_INDEX: Dict[str, str] = {}    # email -> user_id
DB_ASSESSMENTS: Dict[str, List[Dict]] = {}  # user_id -> [assessment dicts]

pwd_hasher = PasswordHash.recommended()  # Argon2

def get_user_by_email(email: str) -> Optional[dict]:
    uid = DB_EMAIL_INDEX.get(email)
    if uid is None:
        return None
    return DB_USERS.get(uid)

def get_user_by_id(user_id: str) -> Optional[dict]:
    return DB_USERS.get(user_id)

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
        "scopes": ["read"],  # padrão
    }
    return DB_USERS[user_id]

def seed_admin():
    user_id = "1"
    email = "admin@example.com"
    if email in DB_EMAIL_INDEX:
        return
    hashed = pwd_hasher.hash("admin123")
    DB_USERS[user_id] = {
        "id": user_id,
        "email": email,
        "name": "Admin",
        "hashed_password": hashed,
        "disabled": False,
        "scopes": ["admin", "read", "write"],
    }
    DB_EMAIL_INDEX[email] = user_id
