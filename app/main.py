# Importações principais do FastAPI e middleware CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurações e módulos internos da aplicação
from app.core.config import CORS_ORIGINS
from app.db.memory import seed_admin
from app.routers import auth, users, assessments

# Criação da instância principal da aplicação FastAPI
app = FastAPI(title="Auth FastAPI + OAuth2 + Argon2 + JWT")

# Configuração do middleware CORS
# Permite que o frontend (origens especificadas em CORS_ORIGINS)
# acesse a API com credenciais, métodos e cabeçalhos liberados
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota pública simples usada para teste de disponibilidade da API
@app.get("/public/ping")
def public_ping():
    return {"pong": True}

# Inclusão dos módulos (routers) que organizam as rotas da aplicação
# Cada módulo possui suas próprias rotas:
# - auth: autenticação e tokens
# - users: gerenciamento de usuários
# - assessments: avaliações/testes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assessments.router)

# Exemplo de rota administrativa, isolada das demais
# Poderia conter informações sensíveis ou métricas internas
@app.get("/admin/metrics")
def admin_metrics():
    return {"stats": "segredo-da-admin"}

# Execução da função de seed que cria o usuário administrador padrão em memória
seed_admin()
