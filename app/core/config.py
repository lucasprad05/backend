# Chave secreta usada para assinar e validar os tokens JWT
# É essencial substituí-la por uma chave longa, aleatória e segura em produção
SECRET_KEY = "troque-esta-chave-por-uma-bem-grande-e-secreta"

# Algoritmo criptográfico usado na geração e validação dos tokens JWT
# O HS256 (HMAC-SHA256) é um algoritmo simétrico amplamente utilizado
ALGORITHM = "HS256"

# Tempo de expiração do token de acesso (em minutos)
# Após esse período, o usuário precisará fazer login novamente
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Lista de origens permitidas para requisições CORS
# Aqui está configurada para permitir o frontend local em Vite (porta padrão 5173)
CORS_ORIGINS = ["http://localhost:5173"]
